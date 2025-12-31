# PRD助手 Backend

FastAPI 后端服务，提供 AI 驱动的 PRD 写作功能。

## 技术栈

- **框架**: FastAPI 0.115.5
- **数据库**: PostgreSQL + pgvector
- **ORM**: SQLAlchemy 2.0 (异步)
- **AI**: Google Gemini 2.0 Flash
- **任务队列**: Celery + Redis

## 快速开始

### 1. 环境准备

确保已安装：
- Python 3.13+
- PostgreSQL 14+
- Redis (用于 Celery)

### 2. 配置环境变量

复制 `.env.example` 为 `.env`，并填入真实值：

```bash
cp ../.env.example ../.env
```

必须配置的变量：
- `DATABASE_URL`: PostgreSQL 连接字符串
- `GEMINI_API_KEY`: Gemini API 密钥
- `SECRET_KEY`: 应用密钥（生产环境请使用强密钥）

### 3. 安装依赖

```bash
# 激活虚拟环境（如果使用 venv）
source ../venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 4. 初始化数据库

```bash
# 创建数据库表
python -m backend.init_db
```

### 5. 启动服务

```bash
# 开发模式（自动重载）
python -m backend.app.main

# 或使用 uvicorn 命令
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

### 6. 访问 API 文档

服务启动后，访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API 端点

### 项目管理

- `POST /api/projects` - 创建项目
- `GET /api/projects` - 获取项目列表
- `GET /api/projects/{project_id}` - 获取单个项目
- `PATCH /api/projects/{project_id}` - 更新项目
- `DELETE /api/projects/{project_id}` - 删除项目

### 知识库管理 (TODO)

- `POST /api/knowledge/analyze` - 分析上传的文件
- `GET /api/knowledge/{project_id}` - 获取项目知识库
- `PATCH /api/knowledge/{project_id}` - 更新知识库

### 对话管理 (TODO)

- `POST /api/conversations` - 创建对话
- `GET /api/conversations/{conversation_id}` - 获取对话历史
- `POST /api/conversations/{conversation_id}/messages` - 发送消息

### 导出 (TODO)

- `GET /api/export/{conversation_id}` - 导出 PRD (Markdown)

## 项目结构

```
backend/
├── app/
│   ├── api/              # API 路由
│   │   └── projects.py   # 项目管理 API
│   ├── core/             # 核心配置
│   │   ├── config.py     # 环境变量配置
│   │   └── database.py   # 数据库连接
│   ├── models/           # SQLAlchemy 模型
│   │   ├── project.py
│   │   ├── knowledge_base.py
│   │   ├── conversation.py
│   │   └── file.py
│   ├── schemas/          # Pydantic 模型
│   │   └── project.py
│   ├── services/         # 业务逻辑
│   │   └── gemini_service.py
│   ├── tasks/            # Celery 任务
│   └── main.py           # FastAPI 应用入口
├── alembic/              # 数据库迁移
├── tests/                # 测试
├── init_db.py            # 数据库初始化脚本
├── requirements.txt      # Python 依赖
└── README.md
```

## 开发指南

### 添加新的 API 端点

1. 在 `app/schemas/` 创建 Pydantic 模型
2. 在 `app/api/` 创建路由文件
3. 在 `app/main.py` 注册路由

### 数据库迁移 (使用 Alembic)

```bash
# 生成迁移文件
alembic revision --autogenerate -m "描述"

# 执行迁移
alembic upgrade head

# 回滚
alembic downgrade -1
```

### 调试技巧

1. **查看 SQL 日志**: 设置 `.env` 中的 `DEBUG=True`
2. **使用 Swagger UI**: 访问 `/docs` 直接测试 API
3. **查看日志**: 日志会输出到控制台

## 常见问题

### Q: 数据库连接失败

A: 检查 `DATABASE_URL` 是否正确，确保 PostgreSQL 服务已启动。

### Q: Gemini API 报错

A: 检查 `GEMINI_API_KEY` 是否有效，确认 API 配额是否充足。

### Q: 如何重置数据库？

A: 
```bash
# 删除所有表
python -c "from backend.app.core.database import Base, engine; import asyncio; asyncio.run(Base.metadata.drop_all(engine))"

# 重新创建
python -m backend.init_db
```

## 完整文档

查看项目根目录的文档中心获取完整文档：

- [文档中心](../docs/README.md) - 所有文档导航
- [后端开发总结](../docs/reports/BACKEND_COMPLETE.md) - 后端功能完成情况
- [API 测试报告](../docs/reports/TERMINAL_TEST_REPORT.md) - 完整测试结果

## 已完成功能

- [x] 项目管理 (5 API)
- [x] 文件上传与分析 (4 API)
- [x] 知识库构建 (4 API)
- [x] 对话功能 (5 API)
- [x] PRD 导出 (2 API)

**总计：20 个 API 端点全部完成并测试通过！**

