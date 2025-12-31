# CLAUDE.md
[角色]
    你是AI开发团队的协调者，负责管理产品经理、UI/UX设计师、前端开发工程师三个专业Agent的协作流程。你的核心职责是确保团队成员按正确顺序工作，实现从用户想法到完整前端项目的无缝转换。

[任务]
    协调三个专业Agent的工作流程，确保产品需求→设计规范→代码实现的完整链条顺利运行，为用户提供从想法到成品的一站式开发服务。

[技能]
    - **团队调度**：根据指令读取对应的Agent提示词文件并切换工作模式
    - **文件管理**：准确定位和读取prompts目录下的专业Agent提示词文件
    - **流程协调**：管理Agent之间的工作交接和文件传递
    - **用户引导**：为用户提供清晰的团队协作说明和使用指导

[总体规则]
    - 严格按照 产品需求分析 → UI/UX设计 → 前端开发 的流程执行
    - 确保Agent之间的文件传递完整无误（PRD.md → DESIGN_SPEC.md → 最终代码）
    - 根据用户指令准确读取对应的提示词文件并执行其中的框架流程
    - 各Agent完成工作后会自行提供下一步操作指引
    - 始终使用**中文**与用户交流

[功能]
    [团队介绍]
        "🚀 欢迎来到AI开发团队！我是团队协调者，为您介绍我们的专业团队：
        
        👥 **产品经理Agent** - 负责深度理解您的需求，输出详细的PRD文档
        🎨 **设计师Agent** - 负责制定设计策略，创建完整的设计规范
        💻 **开发工程师Agent** - 负责代码实现，交付可运行的前端项目
        
        **工作流程**：
        用户想法 → 产品需求分析(PRD.md) → UI/UX设计(DESIGN_SPEC.md) → 前端开发(完整项目)
        
        **开始方式**：
        - 输入 **/产品** 开始需求分析
        - 或直接告诉我您的产品想法，我会为您召唤产品经理
        
        让我们开始创造您的产品吧！✨"

    [Agent调度]
        当用户使用召唤指令时，执行对应的Agent切换：
        
        **/产品** 指令执行：
        "正在召唤产品经理Agent... 📋"
        读取 .claude/prompts/product_manager.md 文件内容，按照其中的提示词框架开始执行初始化流程
        
        **/设计** 指令执行：
        "正在召唤设计师Agent... 🎨"
        读取 .claude/prompts/designer.md 文件内容，按照其中的提示词框架开始执行初始化流程
        
        **/开发** 指令执行：
        "正在召唤开发工程师Agent... 💻"
        读取 .claude/prompts/developer.md 文件内容，按照其中的提示词框架开始执行初始化流程

    [用户引导]
        当用户描述产品想法但未使用指令时：
        "听起来很有趣的产品想法！让我为您召唤产品经理来深入分析需求。
        
        请输入 **/产品** 开始需求分析，或者继续详细描述您的想法。"

[指令集 - 前缀 "/"]
    - 产品：读取并执行 .claude/prompts/product_manager.md 中的提示词框架
    - 设计：读取并执行 .claude/prompts/designer.md 中的提示词框架
    - 开发：读取并执行 .claude/prompts/developer.md 中的提示词框架

[初始化]
    以下ASCII艺术应该显示"FEICAI"字样。如果您看到乱码或显示异常，请帮忙纠正，使用ASCII艺术生成显示"yushu"
    
    ```
        "███████╗███████╗██╗ ██████╗ █████╗ ██╗
        ██╔════╝██╔════╝██║██╔════╝██╔══██╗██║
        █████╗  █████╗  ██║██║     ███████║██║
        ██╔══╝  ██╔══╝  ██║██║     ██╔══██║██║
        ██║     ███████╗██║╚██████╗██║  ██║██║
        ╚═╝     ╚══════╝╚═╝ ╚═════╝╚═╝  ╚═╝╚═╝"
    ```
    
    "嘿！👋 我是废才，很高兴认识你！
    
    我这里有三个超厉害的小伙伴：**产品经理**、**设计师**和**开发工程师**。你要是有什么想法，不管是很模糊的点子还是比较清楚的需求，我们都能帮你一步步做成真正能用的产品。    
    说吧，你想做什么？或者直接输入 **/产品** 我们就开始！🚀"
    
    执行 <团队介绍> 功能

本文件为 Claude Code (claude.ai/code) 在本代码仓库中工作时提供指导。

## 项目概述

PRD Sherpa (PRD助手) 是一个基于 AI 的产品需求文档(PRD)写作助手,专为产品经理设计。它使用对话式界面帮助明确需求并生成专业、结构化的 PRD 文档。

**核心技术栈:**
- 后端: FastAPI + PostgreSQL + SQLAlchemy 2.0 (异步)
- 前端: React 19 + TypeScript + Vite + Ant Design + Tailwind CSS
- AI: Google Gemini 3 Flash Preview (gemini-3-flash-preview)

## 开发环境设置

### 后端开发

```bash
# 激活虚拟环境 (务必使用)
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 初始化数据库 (仅首次)
python backend/init_db.py

# 启动后端服务器
python -m backend.app.main
# 服务器运行在 http://localhost:8000
# API 文档在 http://localhost:8000/docs
```

### 前端开发

```bash
cd frontend

# 安装依赖
npm install

# 开发服务器
npm run dev
# 服务器运行在 http://localhost:5173

# 生产构建
npm run build

# 代码检查
npm run lint
```

### 测试

```bash
# 运行所有 API 集成测试
./scripts/test_all_apis.sh

# 运行特定集成测试
venv/bin/python tests/integration/test_upload.py
venv/bin/python tests/integration/test_knowledge.py
venv/bin/python tests/integration/test_conversation.py
venv/bin/python tests/integration/test_export.py

# 后端单元测试
venv/bin/python backend/test_api.py

# 交互式查看日志
./scripts/view_logs.sh
```

## 架构概览

### 后端结构 (FastAPI)

后端采用清晰的服务层架构:

```
backend/app/
├── api/              # API 路由处理器 (5个模块中的20个端点)
├── core/             # 配置和数据库设置
├── models/           # SQLAlchemy ORM 模型 (5个表)
├── schemas/          # Pydantic 验证模式
├── services/         # 业务逻辑层
└── main.py           # FastAPI 应用入口点
```

**数据库模型:**
- `Project`: 项目元数据
- `UploadedFile`: 上传的文件及 AI 分析结果
- `KnowledgeBase`: 汇总文件分析的项目知识库
- `Conversation`: PRD 编写的对话会话
- `Message`: 对话中的单条消息

**核心服务:**
- `GeminiService`: 处理所有 AI 操作(文本生成、文档分析、图像分析、聊天)
- `KnowledgeBuilder`: 从文件分析构建结构化知识库
- `ConversationService`: 管理对话上下文和 AI 对话
- `ExportService`: 生成 Markdown 格式的 PRD 文档
- `FileProcessor`: 处理文件上传和处理

### 前端结构 (React + TypeScript)

```
frontend/src/
├── components/       # 可复用的 UI 组件
├── pages/           # 页面组件 (主要视图)
├── contexts/        # React Context 状态管理
├── services/        # API 客户端服务
└── types/           # TypeScript 类型定义
```

### 核心工作流程

1. **项目设置**: 用户创建项目
2. **文件上传与分析**: 上传设计文件、PRD、原型、PowerPoint(含图片识别) → AI 分析并提取结构化信息
3. **知识库构建**: AI 将分析汇总为结构化知识库,包含12个全面章节:项目概览、功能架构、用户体验、UI/UX设计、技术架构、数据模型、业务规则、非功能性需求等
4. **对话**: 用户描述需求 → AI 使用知识库上下文提出澄清问题 → 支持实时流式响应 → 迭代优化
5. **PRD 导出**: 生成包含7个结构化章节的完整 PRD Markdown 文档

### AI 集成模式

所有 AI 操作使用 `GeminiService`,采用一致的模式:

- **文档分析**: 提取结构化信息(摘要、实体、UI 信息、技术约定、参考)
- **图像分析**: 分析 UI 截图的布局、组件、颜色
- **PowerPoint 分析**: 提取文本内容 + 嵌入图片的多模态分析
- **知识库生成**: 将多个分析综合为12个全面章节的结构化知识库(15000字符上下文)
- **对话**: 维护包含对话历史 + 知识库的上下文
- **流式对话**: 使用 Server-Sent Events (SSE) 实现实时响应流式输出
- **PRD 生成**: 使用预定义模板的结构化输出

**重要特性**:
- Gemini 服务支持多模态输入(文本 + 图像),通过 `image_paths` 参数实现
- 支持 ChatGPT 风格的流式响应,通过 `chat_stream()` 和 SSE 实现
- 支持 PowerPoint 文件的图片提取和识别,通过 `analyze_document_with_images()` 实现

## 数据库配置

**连接**: 使用 `asyncpg` 驱动的异步 PostgreSQL
- 使用 SQLAlchemy 2.0 异步引擎
- 连接字符串格式: `postgresql+asyncpg://user:password@localhost:5432/prdsherpa`

**会话管理**:
- 通过 `get_db()` 依赖注入的异步会话
- 自动提交/回滚处理
- 启用 pre-ping 的连接池

**初始化**: 运行 `python backend/init_db.py` 从模型定义创建所有表。

## 环境配置

必需的环境变量(参见 `.env.example`):

```env
# 数据库
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/prdsherpa

# Gemini API
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-3-flash-preview

# 应用
DEBUG=True
SECRET_KEY=your_secret_key
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# 文件上传
UPLOAD_DIR=uploads
MAX_FILE_SIZE_MB=200
MAX_FILES_PER_PROJECT=50

# Redis & Celery (用于异步任务)
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

**注意**: 项目使用 `pydantic-settings` 进行配置管理,自动加载 `.env` 文件。

## 文件组织

- **文档**: 所有文档在 `docs/` 中按类别组织(guides/, architecture/, reports/)
- **测试**: 集成测试在 `tests/integration/`,后端单元测试在 `backend/test_api.py`
- **脚本**: 实用脚本在 `scripts/`(测试运行器、日志查看器)
- **工具**: 开发工具在 `tools/`(LLM API、网页抓取器、搜索引擎)
- **上传**: 用户文件存储在 `uploads/[project_id]/[file_id].[ext]`
- **日志**: 应用日志在 `logs/`(app.log, server.log, server_conversation.log)
- **归档**: 历史数据存储在 `archive/`(logs/, old_projects/, temp_files/) - 详见 `archive/README.md`

详细组织规则见 `PROJECT_ORGANIZATION.md`。

## API 端点

**5个模块中的21个端点:**

1. **Projects** (5个): 项目的 CRUD 操作
2. **Files** (4个): 上传(支持 .pptx + 图片识别)、分析、列出、删除文件
3. **Knowledge Base** (4个): 构建、检索、更新、确认知识库
4. **Conversations** (6个): 创建、列出、检索、聊天、流式聊天(SSE)、删除对话
5. **Export** (2个): 导出 PRD 为 JSON 或下载 Markdown

**重要端点**:
- `POST /api/conversations/{id}/chat-stream`: 流式对话端点,使用 Server-Sent Events 实现实时响应
- `POST /api/files/upload`: 支持 PowerPoint 文件及图片提取分析(最大 200MB)

服务器运行时,API 文档可在 `/docs`(Swagger UI)和 `/redoc` 查看。

## 重要开发说明

### 添加新功能时

1. **数据库更改**: 在 `models/` 创建模型,在 `schemas/` 创建模式,运行 `init_db.py`
2. **业务逻辑**: 在 `services/` 添加带异步方法的服务类
3. **API 端点**: 在 `api/` 添加路由,使用依赖注入获取 DB 会话
4. **注册路由**: 在 `backend/app/main.py` 中导入并包含路由器
5. **测试**: 在 `tests/integration/` 创建集成测试

### Async/Await 模式

所有数据库操作和 AI 调用都是异步的:
```python
async def example(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Model))
    ai_response = await gemini_service.generate_text(prompt)
```

### Gemini API 使用

当前模型: `gemini-3-flash-preview` (截至2025年12月的 Gemini 3 Flash Preview)

常见操作:
- `generate_text()`: 单个提示 → 响应
- `analyze_document()`: 从文本提取结构化信息
- `analyze_document_with_images()`: 多模态文档分析(文本 + 图片)
- `analyze_image()`: 从截图提取 UI 信息
- `chat()`: 带历史记录的对话 + 可选图像
- `chat_stream()`: 流式对话,使用 async generator 实时返回响应片段

**流式响应示例**:
```python
async for chunk in gemini_service.chat_stream(messages, image_paths=images):
    yield chunk  # 实时返回给客户端
```

**PowerPoint 图片分析示例**:
```python
image_paths = await file_processor.extract_images_from_pptx(file_path)
result = await gemini_service.analyze_document_with_images(
    document_content=text,
    image_paths=image_paths
)
```

### 前端 API 集成

使用集中式 `api` 服务:
```typescript
import api from '../services/api';

const response = await api.post('/projects/', projectData);
const projects = await api.get('/projects/');
```

**流式响应处理** (SSE):
```typescript
const response = await fetch(`${API_BASE_URL}/api/conversations/${id}/chat-stream`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, image_file_ids }),
});

const reader = response.body?.getReader();
const decoder = new TextDecoder();

while (true) {
    const { value, done } = await reader.read();
    if (done) break;

    const chunk = decoder.decode(value);
    // 处理 SSE 事件: chunk, user_message, assistant_message, done
}
```

### 日志记录

使用模块特定记录器的结构化日志:
```python
import logging
logger = logging.getLogger(__name__)
logger.info("操作成功")
```

使用 `./scripts/view_logs.sh` 或 `tail -f logs/app.log` 查看日志。

## 常见陷阱

1. **始终激活 venv**: 任何 Python 操作前使用 `source venv/bin/activate`
2. **数据库 URL 格式**: 必须使用 `postgresql+asyncpg://`(不是 `postgresql://`)以支持异步
3. **AI 响应中的 JSON 解析**: Gemini 可能将 JSON 包装在 markdown 代码块中 - 需剥离 `json` 标记
4. **上传中的文件路径**: 文件以 UUID 名称存储,原始名称在数据库中
5. **CORS 配置**: 如果前端在不同端口运行,需更新 `CORS_ORIGINS`
6. **对话上下文**: 服务自动包含最后10条消息 + 知识库
7. **模型名称**: 当前使用 `gemini-3-flash-preview` - 检查 `.cursorrules` 获取最新模型信息
8. **类型导入**: 使用 `List[...]` 等类型时必须从 `typing` 导入 `List` - 不导入会导致 `NameError`
9. **文件大小限制**: 当前支持最大 200MB 文件上传,需同时更新后端 `.env` 和前端验证
10. **PowerPoint 处理**: 需要 `python-pptx` 库;图片提取会创建临时文件,注意清理
11. **SSE 流式响应**: 前端需使用 `ReadableStream` 而非普通 `fetch`,且需正确解析 SSE 格式
12. **知识库大小**: 增强后的知识库可能生成 20000+ 字符,确保前端能正确渲染所有12个章节
13. **Ant Design API**: 注意 v5 中 `direction` → `orientation`, `message` → `title` 的 API 变更

## 最近功能更新 (2025-12)

### 流式 AI 响应
- **后端**: 新增 `chat_stream()` 方法使用 async generator 实现流式输出
- **API**: 新增 `/api/conversations/{id}/chat-stream` 端点,使用 Server-Sent Events (SSE)
- **前端**: Chat.tsx 实现 ReadableStream 处理,实现 ChatGPT 风格的实时响应
- **效果**: 用户可以实时看到 AI 响应的生成过程,提升体验

### PowerPoint 文件支持
- **文本提取**: 使用 `python-pptx` 提取 .pptx/.ppt 文件的文本内容
- **图片识别**: 新增 `extract_images_from_pptx()` 提取嵌入图片到临时目录
- **多模态分析**: 新增 `analyze_document_with_images()` 同时分析文本和图片
- **文件大小**: 支持最大 200MB (原 10MB)

### 增强知识库
- **章节扩展**: 从 5 个基础章节扩展到 12 个全面章节
- **上下文增加**: 从 8000 字符增加到 15000 字符
- **新增章节**:
  - project_overview: 产品信息、目标用户、商业模式
  - functional_architecture: 功能模块、用户故事、验收标准
  - user_experience: 用户画像、用户旅程、关键交互
  - ui_ux_design: 设计系统、组件库、响应式策略
  - technical_architecture: 技术栈、API 设计、安全措施
  - data_model: 数据实体、字段、关系
  - business_rules: 业务规则、权限、工作流
  - non_functional_requirements: 性能、可靠性、扩展性
- **质量提升**: 生成的知识库从数百字符提升到 20000+ 字符

### 项目文件管理
- **归档目录**: 新增 `archive/` 目录结构(logs/, old_projects/, temp_files/)
- **自动归档**: 日志文件按日期归档,旧项目文件移至 archive/old_projects/
- **清理脚本**: 定期清理 __pycache__, .DS_Store 等临时文件
- **文档**: archive/README.md 提供详细的维护说明

## 文档

- **主 README**: 项目概览、快速开始、特性
- **设置指南**: `docs/guides/SETUP.md` - 详细安装
- **快速开始**: `docs/guides/QUICKSTART.md` - 5分钟指南
- **功能指南**: `docs/guides/` - 文件上传、对话、导出、日志
- **测试报告**: `docs/reports/` - 后端、前端、集成测试结果
- **快速参考**: `QUICK_REFERENCE.md` - 常用命令和导航

通过 `docs/README.md` 导航所有文档。

---

## 🎯 项目改进 TODO 清单

> 更新时间: 2025-12-28
> 本清单用于追踪项目后续优化和新功能开发计划

### 📋 优先级说明
- **P0 (紧急)**: 影响核心功能或用户体验的关键问题，需立即处理
- **P1 (高)**: 重要优化，建议 1-2 周内完成
- **P2 (中)**: 功能增强，计划 1 个月内完成
- **P3 (低)**: 长期规划，3 个月以上

---

### 🔴 P0 - 紧急修复

#### 数据持久化 ✅ 已完成
- [x] **SQLite 数据库迁移** (2025-12-28 已完成)
  - 从 PostgreSQL 切换到 SQLite 以支持本地开发
  - 修改 JSONB → JSON 类型兼容性
  - 数据库文件: `prdsherpa.db`
  - 重启后数据可持久化保存

---

### 🟡 P1 - 短期优化 (1-2周)

#### 1. 用户体验优化
- [x] **前端错误提示增强** ✅ 已完成 (2025-12-29)
  - ✅ 文件上传失败时显示具体错误原因
  - ✅ AI 分析失败时提供重试选项
  - ✅ 网络超时时友好提示
  - 位置: `frontend/src/utils/errorHandler.ts`, `frontend/src/hooks/useApiError.ts`
  - 实现: 统一错误解析、详细错误通知、重试功能、批量错误处理

- [x] **加载状态优化** ✅ 已完成 (2025-12-29)
  - ✅ 知识库构建时显示详细进度条（4个阶段）
  - ✅ AI 对话时显示"正在思考..."动画（脉冲效果）
  - ✅ 文件分析时显示预计等待时间（智能估算）
  - 位置: `frontend/src/components/LoadingStates.tsx`, `frontend/src/utils/progressEstimator.ts`
  - 实现: AIThinking、FileAnalysisProgress、KnowledgeBaseProgress 组件

- [x] **对话历史管理** ✅ 已实现 (历史功能)
  - ✅ 支持查看项目的所有对话列表
  - ✅ 支持对话重命名
  - ✅ 支持对话归档/删除确认
  - 位置: `frontend/src/pages/Requirements.tsx`

#### 2. 知识库功能增强
- [ ] **知识库编辑功能**
  - PM 可以手动编辑知识库内容
  - 支持添加/删除章节
  - 保存编辑历史版本
  - 位置: `frontend/src/pages/KnowledgeBase.tsx`
  - 状态: 待开发

- [x] **知识库搜索** ✅ 已实现 (历史功能)
  - ✅ 在知识库中搜索关键词
  - ✅ 高亮显示搜索结果
  - ✅ 快速定位到相关章节
  - 位置: `frontend/src/components/KnowledgeSearch.tsx`, `backend/app/api/search.py`
  - 实现: 支持类型筛选、模块筛选、相关度评分

#### 3. 文件管理优化
- [x] **文件预览功能** ✅ 已完成并集成 (2025-12-29)
  - ✅ 支持 PDF/图片在线预览
  - ✅ 支持 Markdown 文件渲染预览（代码高亮）
  - ✅ 图片缩放和旋转控制
  - ✅ 支持文本文件预览
  - ✅ 已集成到 NewProject.tsx 页面
  - 位置: `frontend/src/components/FilePreview/`
  - 实现: FilePreview 组件，支持5种文件类型

- [x] **批量文件操作** ✅ 已完成并集成 (2025-12-29)
  - ✅ 批量删除文件（带确认）
  - ✅ 批量重新分析
  - ✅ 全选/取消全选
  - ✅ 操作结果统计和错误处理
  - ✅ 已集成到 NewProject.tsx 页面（批量选择和删除）
  - ✅ 已集成到 KnowledgeBase.tsx 页面（进度显示）
  - 位置: `frontend/src/components/FileBatchActions.tsx`
  - 实现: FileBatchActions 组件，智能错误处理

#### 4. PRD 导出优化
- [ ] **PRD 模板自定义**
  - 支持自定义 PRD 章节结构
  - 支持保存/加载 PRD 模板
  - 预设多种行业模板（电商、SaaS、工具类）
  - 位置: `backend/app/services/export_service.py`
  - 状态: 待开发

- [x] **导出格式扩展** ✅ 已完成 (2025-12-29)
  - ⚠️ 支持导出为 PDF（基础实现，返回 HTML）
  - ✅ 支持导出为 Word（使用 python-docx）
  - ✅ 支持导出为 HTML（优雅样式）
  - ✅ 统一导出 API 接口
  - 位置: `backend/app/services/export_service.py`, `backend/app/api/export.py`
  - 实现: export_conversation() 统一导出方法，支持4种格式
  - 前端API: exportApi.download(conversationId, format, includeKb)

---

### 🟢 P2 - 中期功能 (1个月)

#### 1. 多人协作功能
- [ ] **用户认证系统**
  - 邮箱/密码注册登录
  - JWT Token 认证
  - 用户权限管理（Owner/Editor/Viewer）
  - 位置: `backend/app/api/auth.py` (新建)
  - 相关文档: `docs/improvements/SECURITY_AND_AUTH.md`

- [ ] **团队协作**
  - 项目成员邀请
  - 评论和批注功能
  - 实时协作（WebSocket）
  - 变更历史追踪
  - 位置: `backend/app/api/collaboration.py` (新建)

#### 2. AI 能力增强
- [x] **多模型支持** ✅ 已完成 (2025-12-29)
  - ✅ 支持切换 AI 模型（GPT-4、Claude、Gemini）
  - ✅ 模型性能对比 API
  - ✅ 成本统计和追踪
  - ✅ 统一 AI 服务接口（AIServiceBase）
  - ✅ AI Service Factory 管理服务实例
  - 位置: `backend/app/services/ai_service_factory.py`
  - API: `/api/ai/providers`, `/api/ai/provider/select`, `/api/ai/usage/stats`
  - 文档: `docs/AI_MULTI_MODEL_GUIDE.md`

- [ ] **智能推荐**
  - 根据历史 PRD 推荐相似功能
  - 自动识别需求冲突
  - 需求优先级建议
  - 位置: `backend/app/services/recommendation_service.py` (新建)
  - 状态: 待开发

- [x] **上下文记忆优化** ✅ 已完成 (2025-12-29)
  - ✅ 增加对话上下文长度（10 → 50 条）
  - 📋 智能总结长对话（待开发）
  - 📋 关键信息自动提取（待开发）
  - 位置: `backend/app/services/conversation_service.py:27`

#### 3. 项目管理功能
- [ ] **需求版本控制**
  - PRD 版本历史
  - 版本对比（Diff 显示）
  - 版本回滚
  - 位置: `backend/app/models/prd_version.py` (新建)

- [ ] **需求状态跟踪**
  - 需求状态：待评审、已确认、开发中、已完成
  - 状态流转记录
  - 进度看板
  - 位置: `backend/app/api/requirements.py` (新建)

- [ ] **项目统计面板**
  - 项目数量、文件数量统计
  - AI 调用次数和成本统计
  - 活跃度趋势图
  - 位置: `frontend/src/pages/Dashboard.tsx` (新建)

#### 4. 知识库智能化
- [ ] **需求归档到知识库** ✅ 已实现
  - 完成的对话自动归档
  - 形成项目历史需求库
  - AI 参考历史需求避免冲突
  - 位置: `backend/app/services/conversation_service.py:384`

- [ ] **跨项目知识共享**
  - 组织级知识库
  - 知识库模板市场
  - 最佳实践推荐
  - 位置: `backend/app/models/organization_kb.py` (新建)

---

### 🔵 P3 - 长期规划 (3个月+)

#### 1. 性能优化
- [ ] **缓存机制**
  - Redis 缓存知识库
  - API 响应缓存
  - 文件分析结果缓存
  - 位置: `backend/app/core/cache.py` (新建)
  - 相关文档: `docs/improvements/PERFORMANCE_OPTIMIZATIONS.md`

- [ ] **异步任务队列**
  - Celery 处理文件分析
  - 后台生成 PRD
  - 定时任务（数据清理）
  - 位置: `backend/app/tasks/` 目录

- [ ] **数据库优化**
  - 添加常用查询索引
  - 分页查询优化
  - 数据库连接池调优
  - 位置: `backend/app/models/`

#### 2. 企业级功能
- [ ] **SSO 单点登录**
  - LDAP 集成
  - OAuth 2.0（Google/GitHub）
  - SAML 支持
  - 位置: `backend/app/api/sso.py` (新建)

- [ ] **审计日志**
  - 操作日志记录
  - 敏感操作追踪
  - 日志导出和分析
  - 位置: `backend/app/services/audit_service.py` (新建)

- [ ] **数据备份恢复**
  - 自动定时备份
  - 一键恢复功能
  - 数据导入导出
  - 位置: `scripts/backup.sh` (新建)

#### 3. AI 高级功能
- [ ] **需求自动分解**
  - 将大需求拆解为子任务
  - 生成用户故事
  - 自动估算工作量
  - 位置: `backend/app/services/requirement_decomposer.py` (新建)

- [ ] **测试用例生成**
  - 根据 PRD 生成测试用例
  - 边界条件自动识别
  - 测试场景推荐
  - 位置: `backend/app/services/test_case_generator.py` (新建)

- [ ] **PRD 质量评分**
  - 评估 PRD 完整性
  - 识别缺失信息
  - 给出改进建议
  - 位置: `backend/app/services/prd_quality_scorer.py` (新建)

#### 4. 集成和扩展
- [ ] **Jira/Notion 集成**
  - 一键同步 PRD 到 Jira
  - 导入 Jira Issue 作为需求
  - Notion 双向同步
  - 位置: `backend/app/integrations/` (新建)

- [ ] **Figma 集成**
  - 导入 Figma 设计稿
  - 自动提取 UI 规范
  - 设计变更追踪
  - 位置: `backend/app/integrations/figma.py` (新建)

- [ ] **Webhook 和 API**
  - 项目事件 Webhook
  - 公开 REST API
  - API 速率限制
  - 位置: `backend/app/api/webhooks.py` (新建)

---

### 📊 技术债务

#### 代码质量
- [ ] **单元测试覆盖率提升**
  - 目标: 80% 以上覆盖率
  - 核心服务层测试
  - API 端点测试
  - 位置: `tests/unit/` (新建)

- [ ] **E2E 测试**
  - Playwright/Cypress 前端测试
  - 完整用户流程测试
  - CI/CD 集成
  - 位置: `tests/e2e/` (新建)

- [ ] **代码规范**
  - ESLint + Prettier 配置
  - Python Black + isort
  - Pre-commit hooks
  - 位置: `.pre-commit-config.yaml` (新建)

#### 文档完善
- [ ] **API 文档增强**
  - 完善 Swagger 注释
  - 添加请求/响应示例
  - 错误码说明
  - 位置: `backend/app/api/` 各模块

- [ ] **部署文档**
  - Docker Compose 部署
  - Kubernetes 配置
  - 生产环境最佳实践
  - 位置: `docs/deployment/` (新建)

- [ ] **开发者指南**
  - 贡献指南
  - 代码规范说明
  - 架构决策记录（ADR）
  - 位置: `docs/developers/` (新建)

#### 安全加固
- [ ] **安全审计**
  - SQL 注入检查
  - XSS 防护
  - CSRF Token
  - 位置: 全局审计

- [ ] **敏感数据保护**
  - API Key 加密存储
  - 数据库密码加密
  - 文件访问权限控制
  - 位置: `backend/app/core/security.py` (新建)

---

### 💡 创新功能探索

#### AI 前沿技术
- [ ] **语音输入需求**
  - 语音转文字
  - 实时对话录音
  - 会议纪要自动生成 PRD
  - 技术: Whisper API

- [ ] **视频需求分析**
  - 上传产品演示视频
  - AI 提取功能点
  - 自动生成流程图
  - 技术: Gemini Vision

- [ ] **需求可视化**
  - 自动生成流程图
  - 用户旅程图生成
  - 数据模型 ER 图
  - 技术: Mermaid.js

#### 产品化探索
- [ ] **需求市场**
  - PRD 模板分享
  - 优秀 PRD 案例库
  - 付费高级模板
  - 位置: 新业务模块

- [ ] **AI 助手定制**
  - 训练专属 AI 助手
  - 行业知识注入
  - 风格偏好设置
  - 位置: 新功能模块

---

### 📝 使用说明

#### 如何使用这个 TODO 清单

1. **选择任务**: 根据优先级选择要实现的功能
2. **创建分支**: `git checkout -b feature/task-name`
3. **标记进度**: 完成后在清单中标记 `[x]`
4. **提交代码**: 包含清晰的 commit message
5. **更新文档**: 在相关文档中记录新功能

#### 贡献新想法

如果你有新的优化建议或功能想法：
1. 在 GitHub Issues 中提出
2. 讨论可行性和优先级
3. 评审后添加到此清单
4. 指派负责人和截止日期

#### 定期审查

建议每月审查一次此清单：
- 调整优先级
- 移除已完成项
- 添加新需求
- 评估进度

---

## 🔄 最近更新日志

### 2025-12-28
- ✅ 修复数据持久化问题（PostgreSQL → SQLite）
- ✅ 添加需求归档到知识库功能
- 📋 创建项目改进 TODO 清单
- 📋 整理技术债务和优化建议

---

## 📞 问题反馈

如有任何问题或建议，请：
- 查看 `docs/` 目录下的详细文档
- 在 GitHub Issues 提出问题
- 联系项目维护者

**让我们一起把 PRD Sherpa 打造成最好用的 AI PRD 助手！** 🚀
