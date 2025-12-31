# PRD助手 - 项目结构

```
prdsherpa/
│
├── .env                          # 环境变量配置（需要用户填写）
├── .env.example                  # 环境变量模板
├── ProductSpec                   # 产品规格文档
├── SETUP.md                      # 项目搭建说明
├── PROJECT_STRUCTURE.md          # 本文件
│
├── backend/                      # FastAPI 后端
│   ├── README.md                 # 后端文档
│   ├── requirements.txt          # Python 依赖
│   ├── init_db.py               # 数据库初始化脚本
│   ├── test_api.py              # API 测试脚本
│   │
│   └── app/                     # 应用主目录
│       ├── main.py              # FastAPI 入口
│       │
│       ├── core/                # 核心配置
│       │   ├── config.py        # 环境变量管理（从 .env 加载）
│       │   └── database.py      # 数据库连接（异步 SQLAlchemy）
│       │
│       ├── models/              # 数据库模型（SQLAlchemy ORM）
│       │   ├── project.py       # 项目表
│       │   ├── knowledge_base.py # 知识库表 + 文档向量表
│       │   ├── conversation.py  # 对话表 + 消息表
│       │   └── file.py          # 上传文件表
│       │
│       ├── schemas/             # API 数据模型（Pydantic）
│       │   └── project.py       # 项目相关的请求/响应模型
│       │
│       ├── api/                 # API 路由
│       │   └── projects.py      # 项目管理 API（CRUD）
│       │
│       ├── services/            # 业务逻辑服务
│       │   └── gemini_service.py # Gemini API 封装
│       │
│       └── tasks/               # Celery 后台任务（待实现）
│
├── tools/                       # 工具脚本
│   ├── llm_api.py
│   ├── screenshot_utils.py
│   ├── search_engine.py
│   └── web_scraper.py
│
└── venv/                        # Python 虚拟环境
```

## 文件说明

### 配置文件

| 文件 | 说明 |
|------|------|
| `.env` | 环境变量配置（需要用户创建并填写） |
| `.env.example` | 环境变量模板 |
| `backend/requirements.txt` | Python 依赖列表 |

### 核心模块

| 模块 | 文件 | 说明 |
|------|------|------|
| **应用入口** | `backend/app/main.py` | FastAPI 应用、路由注册、CORS 配置 |
| **配置管理** | `backend/app/core/config.py` | 从 .env 加载配置（pydantic-settings） |
| **数据库** | `backend/app/core/database.py` | 异步数据库连接、Session 管理 |

### 数据模型

#### SQLAlchemy 模型（数据库表）

| 文件 | 模型 | 说明 |
|------|------|------|
| `models/project.py` | `Project` | 项目基本信息 |
| `models/knowledge_base.py` | `KnowledgeBase` | 项目知识库（JSONB） |
| `models/knowledge_base.py` | `DocumentEmbedding` | 文档向量（语义检索） |
| `models/conversation.py` | `Conversation` | 对话会话 |
| `models/conversation.py` | `Message` | 对话消息 |
| `models/file.py` | `UploadedFile` | 上传的文件 |

#### Pydantic 模型（API 数据验证）

| 文件 | 模型 | 说明 |
|------|------|------|
| `schemas/project.py` | `ProjectCreate` | 创建项目请求 |
| `schemas/project.py` | `ProjectUpdate` | 更新项目请求 |
| `schemas/project.py` | `ProjectResponse` | 项目响应 |
| `schemas/project.py` | `ProjectListResponse` | 项目列表响应 |

### API 路由

| 文件 | 路由前缀 | 说明 |
|------|---------|------|
| `api/projects.py` | `/api/projects` | 项目管理（CRUD） |

**已实现的端点：**
- `POST /api/projects/` - 创建项目
- `GET /api/projects/` - 获取项目列表
- `GET /api/projects/{id}` - 获取单个项目
- `PATCH /api/projects/{id}` - 更新项目
- `DELETE /api/projects/{id}` - 删除项目

### 服务层

| 文件 | 类 | 说明 |
|------|-----|------|
| `services/gemini_service.py` | `GeminiService` | Gemini API 封装 |

**主要方法：**
- `generate_text()` - 文本生成
- `analyze_document()` - 文档分析
- `analyze_image()` - 图片分析
- `chat()` - 对话功能

### 工具脚本

| 文件 | 说明 |
|------|------|
| `backend/init_db.py` | 数据库初始化（创建所有表） |
| `backend/test_api.py` | API 测试脚本 |

## 数据库表结构

### projects（项目表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| name | String(255) | 项目名称 |
| description | Text | 项目描述 |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |
| last_conversation_at | DateTime | 最后对话时间 |

### knowledge_bases（知识库表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| project_id | UUID | 外键 → projects.id |
| structured_data | JSONB | 结构化知识（系统概览、UI规范等） |
| version | Integer | 版本号 |
| status | String(50) | 状态（pending/analyzing/confirmed） |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

### document_embeddings（文档向量表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| knowledge_base_id | UUID | 外键 → knowledge_bases.id |
| source_file | String(255) | 源文件名 |
| chunk_text | Text | 文本块 |
| chunk_index | Integer | 块序号 |
| metadata | JSONB | 元数据 |
| created_at | DateTime | 创建时间 |

### conversations（对话表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| project_id | UUID | 外键 → projects.id |
| title | String(255) | 对话标题 |
| status | String(50) | 状态（active/completed/archived） |
| summary | Text | 对话摘要 |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

### messages（消息表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| conversation_id | UUID | 外键 → conversations.id |
| role | String(20) | 角色（user/assistant） |
| content | Text | 消息内容 |
| metadata | JSONB | 元数据（知识库引用、token数等） |
| sequence | Integer | 消息序号 |
| created_at | DateTime | 创建时间 |

### uploaded_files（上传文件表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| project_id | UUID | 外键 → projects.id |
| filename | String(255) | 文件名 |
| file_path | String(500) | 存储路径 |
| file_type | String(50) | 文件类型 |
| file_size | Integer | 文件大小（字节） |
| status | String(50) | 状态（pending/analyzing/completed/failed） |
| analysis_result | String(1000) | 分析结果简述 |
| created_at | DateTime | 创建时间 |

## 技术栈

| 层级 | 技术 | 版本 |
|------|------|------|
| 后端框架 | FastAPI | 0.115.5 |
| ASGI 服务器 | Uvicorn | 0.32.1 |
| 数据库 | PostgreSQL | 14+ |
| ORM | SQLAlchemy | 2.0.36 |
| 数据库驱动 | asyncpg | 0.30.0 |
| 向量扩展 | pgvector | 0.3.6 |
| AI 模型 | Gemini 2.0 Flash | - |
| AI SDK | google-generativeai | 0.8.3 |
| 任务队列 | Celery | 5.4.0 |
| 消息队列 | Redis | 5.2.1 |
| 配置管理 | pydantic-settings | 2.6.1 |
| 文档解析 | pypdf, python-docx | - |
| 图片处理 | Pillow | 11.0.0 |

## 开发流程

### 1. 添加新的 API 端点

```
1. 在 schemas/ 创建 Pydantic 模型（请求/响应）
2. 在 api/ 创建路由文件
3. 在 main.py 注册路由
4. 在 /docs 测试
```

### 2. 添加新的数据库表

```
1. 在 models/ 创建 SQLAlchemy 模型
2. 在 models/__init__.py 导入
3. 运行 python -m backend.init_db 创建表
```

### 3. 集成新的 AI 功能

```
1. 在 services/gemini_service.py 添加方法
2. 在 API 路由中调用
3. 测试
```

## 下一步开发

- [ ] 文件上传 API
- [ ] 文件分析（Celery 后台任务）
- [ ] 知识库构建 API
- [ ] 对话 API（流式输出）
- [ ] PRD 导出 API
- [ ] 前端开发（Next.js）

