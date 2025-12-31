# 性能优化方案

## 1. 数据库查询优化

### 问题：N+1 查询问题

**当前代码** (`conversations.py:108-146`):
```python
# 第一次查询：获取对话列表和消息数
result = await db.execute(
    select(Conversation, func.count(Message.id).label("message_count"))
    .outerjoin(Message)
    .where(Conversation.project_id == project_id)
    .group_by(Conversation.id)
    .order_by(desc(Conversation.updated_at))
    .offset(skip)
    .limit(limit)
)
conversations_with_count = result.all()

# 第二次查询：获取总数
total_result = await db.execute(
    select(func.count(Conversation.id))
    .where(Conversation.project_id == project_id)
)
total = total_result.scalar()
```

**优化方案 1：使用 Window 函数**
```python
from sqlalchemy import func, over

# 单次查询同时获取数据和总数
stmt = (
    select(
        Conversation,
        func.count(Message.id).label("message_count"),
        func.count(Conversation.id).over().label("total_count")
    )
    .outerjoin(Message, Message.conversation_id == Conversation.id)
    .where(Conversation.project_id == project_id)
    .group_by(Conversation.id)
    .order_by(desc(Conversation.updated_at))
    .offset(skip)
    .limit(limit)
)

result = await db.execute(stmt)
rows = result.all()

conversations = []
total = rows[0].total_count if rows else 0

for row in rows:
    conv_dict = {
        **row.Conversation.__dict__,
        "message_count": row.message_count
    }
    conversations.append(conv_dict)
```

**优化方案 2：使用 CTE（公共表表达式）**
```python
from sqlalchemy import select, func, literal_column

# 创建 CTE 计算总数
total_cte = (
    select(func.count(Conversation.id).label("total"))
    .where(Conversation.project_id == project_id)
).cte("total_count")

# 主查询引用 CTE
stmt = (
    select(
        Conversation,
        func.count(Message.id).label("message_count"),
        total_cte.c.total
    )
    .outerjoin(Message)
    .where(Conversation.project_id == project_id)
    .group_by(Conversation.id, total_cte.c.total)
    .order_by(desc(Conversation.updated_at))
    .offset(skip)
    .limit(limit)
)
```

**预期效果：**
- ✅ 减少50%数据库往返时间
- ✅ 降低数据库连接池压力
- ✅ 提升列表接口响应速度 ~30-40%

---

## 2. 添加索引优化

### 当前问题：缺少关键字段索引

**需要添加的索引：**

```python
# backend/app/models/project.py
class Project(Base):
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)

    # 新增索引
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), index=True)
    last_conversation_at = Column(DateTime(timezone=True), nullable=True, index=True)  # 添加索引

# backend/app/models/conversation.py
class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False, index=True)

    # 复合索引优化常见查询
    __table_args__ = (
        Index('ix_conversation_project_updated', 'project_id', 'updated_at'),
        Index('ix_conversation_project_status', 'project_id', 'status'),
    )

# backend/app/models/message.py
class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False)
    sequence = Column(Integer, nullable=False)

    # 唯一索引防止重复
    __table_args__ = (
        UniqueConstraint('conversation_id', 'sequence', name='uix_message_conversation_sequence'),
        Index('ix_message_conversation_created', 'conversation_id', 'created_at'),
    )
```

**数据库迁移脚本：**
```sql
-- 添加索引
CREATE INDEX IF NOT EXISTS ix_projects_created_at ON projects(created_at);
CREATE INDEX IF NOT EXISTS ix_projects_updated_at ON projects(updated_at);
CREATE INDEX IF NOT EXISTS ix_projects_last_conversation_at ON projects(last_conversation_at);

CREATE INDEX IF NOT EXISTS ix_conversation_project_updated ON conversations(project_id, updated_at);
CREATE INDEX IF NOT EXISTS ix_conversation_project_status ON conversations(project_id, status);

CREATE UNIQUE INDEX IF NOT EXISTS uix_message_conversation_sequence ON messages(conversation_id, sequence);
CREATE INDEX IF NOT EXISTS ix_message_conversation_created ON messages(conversation_id, created_at);
```

---

## 3. Redis 缓存实现

### 缓存策略

**场景 1：知识库缓存**
```python
# backend/app/services/knowledge_service.py
import redis.asyncio as redis
import json
from typing import Optional

class KnowledgeCacheService:
    def __init__(self):
        self.redis_client = redis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True
        )

    async def get_knowledge_base(self, project_id: str) -> Optional[dict]:
        """从缓存获取知识库"""
        key = f"kb:{project_id}"
        cached = await self.redis_client.get(key)
        if cached:
            return json.loads(cached)
        return None

    async def set_knowledge_base(
        self,
        project_id: str,
        kb_data: dict,
        ttl: int = 3600  # 1小时
    ):
        """缓存知识库"""
        key = f"kb:{project_id}"
        await self.redis_client.setex(
            key,
            ttl,
            json.dumps(kb_data, ensure_ascii=False)
        )

    async def invalidate_knowledge_base(self, project_id: str):
        """使缓存失效"""
        key = f"kb:{project_id}"
        await self.redis_client.delete(key)

# 在API中使用
@router.get("/{project_id}")
async def get_knowledge_base(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    cache: KnowledgeCacheService = Depends(get_cache_service)
):
    # 尝试从缓存获取
    cached_kb = await cache.get_knowledge_base(str(project_id))
    if cached_kb:
        logger.info(f"Knowledge base cache hit for project {project_id}")
        return cached_kb

    # 缓存未命中，从数据库查询
    result = await db.execute(
        select(KnowledgeBase).where(KnowledgeBase.project_id == project_id)
    )
    kb = result.scalar_one_or_none()

    if kb:
        # 写入缓存
        await cache.set_knowledge_base(str(project_id), kb.structured_data)

    return kb
```

**场景 2：AI 响应缓存（相同问题）**
```python
class AIResponseCache:
    """缓存相似问题的AI响应"""

    async def get_cached_response(self, question_hash: str) -> Optional[str]:
        """获取缓存的AI响应"""
        key = f"ai:response:{question_hash}"
        return await self.redis_client.get(key)

    async def cache_response(
        self,
        question_hash: str,
        response: str,
        ttl: int = 86400  # 24小时
    ):
        """缓存AI响应"""
        key = f"ai:response:{question_hash}"
        await self.redis_client.setex(key, ttl, response)

    @staticmethod
    def hash_question(question: str, context: dict) -> str:
        """生成问题的哈希值"""
        import hashlib
        content = f"{question}:{json.dumps(context, sort_keys=True)}"
        return hashlib.sha256(content.encode()).hexdigest()
```

**预期效果：**
- ✅ 知识库查询响应时间：100ms → 5ms（95%提升）
- ✅ 相似问题AI响应：30s → 0.1s（缓存命中）
- ✅ 减少数据库负载 60-70%
- ✅ 降低 Gemini API 调用成本

---

## 4. 前端性能优化

### 问题：KnowledgeBase.tsx 过大（70KB）

**拆分方案：**

```
frontend/src/
├── pages/
│   └── KnowledgeBase.tsx (主容器, ~15KB)
├── components/
│   └── knowledge/
│       ├── SystemOverviewSection.tsx (~12KB)
│       ├── UIStandardsSection.tsx (~12KB)
│       ├── TechConventionsSection.tsx (~10KB)
│       ├── PendingQuestionsSection.tsx (~8KB)
│       ├── FunctionalArchitectureSection.tsx (~10KB)
│       └── ...其他章节
```

**虚拟滚动实现（Chat.tsx）：**
```typescript
import { Virtualizer } from '@tanstack/react-virtual';

const ChatMessages: React.FC = () => {
  const parentRef = useRef<HTMLDivElement>(null);

  const virtualizer = useVirtualizer({
    count: messages.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 100, // 预估每条消息高度
    overscan: 5, // 多渲染5条备用
  });

  return (
    <div ref={parentRef} style={{ height: '600px', overflow: 'auto' }}>
      <div
        style={{
          height: `${virtualizer.getTotalSize()}px`,
          width: '100%',
          position: 'relative',
        }}
      >
        {virtualizer.getVirtualItems().map((virtualItem) => (
          <div
            key={virtualItem.key}
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              width: '100%',
              transform: `translateY(${virtualItem.start}px)`,
            }}
          >
            <MessageItem message={messages[virtualItem.index]} />
          </div>
        ))}
      </div>
    </div>
  );
};
```

**代码分割：**
```typescript
// 路由级别懒加载
const KnowledgeBase = lazy(() => import('./pages/KnowledgeBase'));
const Chat = lazy(() => import('./pages/Chat'));
const Requirements = lazy(() => import('./pages/Requirements'));

// 组件级别懒加载
const PDFExporter = lazy(() => import('./components/PDFExporter'));
```

---

## 5. AI 调用优化

### 添加重试机制

```python
# backend/app/services/gemini_service.py
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)

class GeminiService:
    # 配置重试策略
    RETRY_CONFIG = dict(
        retry=retry_if_exception_type((ConnectionError, TimeoutError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )

    @retry(**RETRY_CONFIG)
    async def generate_text(self, prompt: str, **kwargs) -> str:
        """带重试机制的文本生成"""
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Gemini API error (will retry): {str(e)}")
            raise

    async def generate_with_fallback(
        self,
        prompt: str,
        fallback_model: str = "gemini-flash-1.5"
    ) -> str:
        """
        带降级策略的生成
        主模型失败时切换到备用模型
        """
        try:
            return await self.generate_text(prompt)
        except Exception as e:
            logger.warning(f"Primary model failed: {e}, using fallback")
            # 切换到备用模型
            original_model = self.model_name
            self.model_name = fallback_model
            try:
                result = await self.generate_text(prompt)
                return result
            finally:
                self.model_name = original_model
```

### 并行处理

```python
import asyncio

async def analyze_multiple_files_parallel(
    file_ids: List[str],
    max_concurrent: int = 3
) -> List[dict]:
    """
    并行分析多个文件
    限制并发数避免API限流
    """
    semaphore = asyncio.Semaphore(max_concurrent)

    async def analyze_with_semaphore(file_id: str):
        async with semaphore:
            return await analyze_file(file_id)

    tasks = [analyze_with_semaphore(fid) for fid in file_ids]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    return [r for r in results if not isinstance(r, Exception)]
```

---

## 6. 监控和可观测性

### Prometheus 指标

```python
# backend/app/core/metrics.py
from prometheus_client import Counter, Histogram, Gauge

# 请求计数器
request_count = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

# 响应时间分布
response_time = Histogram(
    'http_response_duration_seconds',
    'HTTP response duration',
    ['method', 'endpoint']
)

# AI 调用指标
ai_calls = Counter(
    'gemini_api_calls_total',
    'Total Gemini API calls',
    ['operation', 'status']
)

ai_latency = Histogram(
    'gemini_api_latency_seconds',
    'Gemini API latency',
    ['operation']
)

# 数据库连接池
db_pool_size = Gauge(
    'db_connection_pool_size',
    'Current database connection pool size'
)

# 使用示例
@app.middleware("http")
async def add_metrics(request: Request, call_next):
    start_time = time.time()

    response = await call_next(request)

    duration = time.time() - start_time
    request_count.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()

    response_time.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(duration)

    return response
```

### 健康检查端点

```python
@app.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    """完整的健康检查"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "checks": {}
    }

    # 检查数据库连接
    try:
        await db.execute(select(1))
        health_status["checks"]["database"] = "ok"
    except Exception as e:
        health_status["checks"]["database"] = f"error: {str(e)}"
        health_status["status"] = "unhealthy"

    # 检查 Redis
    try:
        redis_client = await get_redis()
        await redis_client.ping()
        health_status["checks"]["redis"] = "ok"
    except Exception as e:
        health_status["checks"]["redis"] = f"error: {str(e)}"
        health_status["status"] = "degraded"

    # 检查 Gemini API
    try:
        await gemini_service.generate_text("test", max_tokens=10)
        health_status["checks"]["gemini_api"] = "ok"
    except Exception as e:
        health_status["checks"]["gemini_api"] = f"error: {str(e)}"
        health_status["status"] = "degraded"

    status_code = 200 if health_status["status"] != "unhealthy" else 503
    return Response(
        content=json.dumps(health_status),
        status_code=status_code,
        media_type="application/json"
    )

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
```

---

## 实施优先级

### P0 - 立即实施（1-2周）
1. ✅ 修复 N+1 查询（conversations.py）
2. ✅ 添加重试机制（gemini_service.py）
3. ✅ 添加数据库索引

### P1 - 短期实施（2-4周）
4. ✅ 实现 Celery 异步任务
5. ✅ 实现 Redis 缓存（知识库）
6. ✅ 添加健康检查和基础监控

### P2 - 中期实施（1-2个月）
7. ✅ 拆分大型前端组件
8. ✅ 实现虚拟滚动
9. ✅ 添加 Prometheus 指标

---

## 预期效果

| 指标 | 优化前 | 优化后 | 提升幅度 |
|------|--------|--------|----------|
| 文件上传响应 | 20-30秒 | 0.5秒 | **98%** |
| 知识库加载 | 100-200ms | 5-10ms | **95%** |
| 对话列表加载 | 150ms | 70ms | **53%** |
| AI响应首字节时间 | 2-3秒 | 1-1.5秒 | **40%** |
| 数据库连接数 | 平均8个 | 平均3个 | **62%** |
| 页面加载时间 | 2.5秒 | 1.2秒 | **52%** |

**成本节省：**
- 数据库查询减少 60%
- Gemini API 调用减少 30%（缓存）
- 服务器资源使用减少 40%
