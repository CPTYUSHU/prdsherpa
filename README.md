# PRD助手 - AI 驱动的产品需求文档写作助手

<div align="center">

**让 AI 帮你写出专业的 PRD 文档**

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green.svg)](https://fastapi.tiangolo.com/)
[![Gemini](https://img.shields.io/badge/Gemini-2.0_Flash-orange.svg)](https://ai.google.dev/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14+-blue.svg)](https://www.postgresql.org/)

</div>

---

## 📖 项目简介

PRD助手 是一个基于 AI 的产品需求文档（PRD）写作助手，专为产品经理设计。通过对话式交互，AI 帮助你澄清需求细节，最终生成结构化、专业的 PRD 文档。

### 核心特性

- 🤖 **AI 驱动**: 使用 Google Gemini 2.0 Flash 提供智能分析
- 💬 **对话式交互**: 自然语言描述需求，AI 主动提问澄清
- 📁 **文件分析**: 上传设计稿、原型图，AI 自动提取信息
- 📚 **知识库**: 自动构建项目知识库，确保需求一致性
- 📄 **一键导出**: 生成完整的 Markdown PRD 文档
- 🎯 **结构化输出**: 包含需求概述、功能需求、UI/UX、技术实现等完整章节

---

## 🚀 快速开始

### 前置要求

- Python 3.13+
- PostgreSQL 14+
- Gemini API Key

### 5 分钟安装

```bash
# 1. 克隆项目
git clone <repository-url>
cd prdsherpa

# 2. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入数据库和 Gemini API Key

# 5. 初始化数据库
python backend/init_db.py

# 6. 启动服务器
python -m backend.app.main
```

服务器启动后，访问：
- API 文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/health

详细安装指南请查看 [SETUP.md](docs/guides/SETUP.md)

---

## 💡 使用示例

### 1. 创建项目

```python
import httpx

async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://localhost:8000/api/projects/",
        json={
            "name": "电商APP",
            "description": "一个现代化的移动电商应用"
        }
    )
    project = response.json()
    print(f"项目创建成功: {project['id']}")
```

### 2. 上传文件并分析

```python
# 上传设计稿
with open("design.png", "rb") as f:
    files = {"file": ("design.png", f, "image/png")}
    data = {"project_id": project_id}
    response = await client.post(
        "http://localhost:8000/api/files/upload",
        files=files,
        data=data
    )
    file_data = response.json()

# AI 分析文件
response = await client.post(
    f"http://localhost:8000/api/files/{file_data['id']}/analyze"
)
analysis = response.json()
print(f"AI 分析结果: {analysis['analysis_result']}")
```

### 3. 构建知识库

```python
# 构建知识库
response = await client.post(
    f"http://localhost:8000/api/knowledge/build/{project_id}",
    json={"file_ids": [file_id]}
)
kb = response.json()

# 确认知识库
response = await client.post(
    f"http://localhost:8000/api/knowledge/{project_id}/confirm",
    json={"confirmed_by": "产品经理"}
)
```

### 4. 对话式需求撰写

```python
# 创建对话
response = await client.post(
    "http://localhost:8000/api/conversations/",
    json={
        "project_id": project_id,
        "title": "用户登录功能"
    }
)
conversation = response.json()

# 发送消息
response = await client.post(
    f"http://localhost:8000/api/conversations/{conversation['id']}/chat",
    json={"message": "我需要实现用户登录功能"}
)
result = response.json()
print(f"AI 回复: {result['assistant_message']['content']}")
```

### 5. 导出 PRD

```python
# 导出为 JSON
response = await client.post(
    f"http://localhost:8000/api/export/conversation/{conversation_id}"
)
prd = response.json()
print(f"PRD 文件名: {prd['filename']}")

# 下载 Markdown 文件
response = await client.get(
    f"http://localhost:8000/api/export/conversation/{conversation_id}/download"
)
with open(prd['filename'], 'w', encoding='utf-8') as f:
    f.write(response.text)
```

---

## 📚 文档

> 📖 **[完整文档导航](docs/README.md)** - 查看所有文档

### 入门指南
- [安装指南](docs/guides/SETUP.md) - 详细的安装和配置说明
- [快速开始](docs/guides/QUICKSTART.md) - 5 分钟快速上手
- [项目结构](docs/architecture/PROJECT_STRUCTURE.md) - 代码组织说明

### 功能说明
- [文件上传](docs/guides/FILE_UPLOAD_GUIDE.md) - 文件上传和 AI 分析
- [对话功能](docs/guides/CONVERSATION_FEATURE.md) - 对话式需求撰写
- [导出功能](docs/guides/EXPORT_FEATURE.md) - PRD 文档导出
- [日志系统](docs/guides/LOGGING_GUIDE.md) - 日志配置和使用

### 开发报告
- [后端总结](docs/reports/BACKEND_COMPLETE.md) - 后端开发完成总结
- [前端总结](docs/reports/FRONTEND_COMPLETE.md) - 前端开发完成总结
- [测试报告](docs/reports/TERMINAL_TEST_REPORT.md) - API 测试结果

---

## 🏗️ 技术架构

### 后端技术栈
- **FastAPI**: 现代、高性能的 Python Web 框架
- **PostgreSQL**: 关系型数据库
- **SQLAlchemy 2.0**: 异步 ORM
- **Gemini 2.0 Flash**: Google 最新 AI 模型
- **Pydantic**: 数据验证和设置管理

### 核心功能模块
```
PRD助手
├── 项目管理 (5 API)
├── 文件管理 (4 API)
├── 知识库 (4 API)
├── 对话 (5 API)
└── 导出 (2 API)

总计: 20 个 API 端点
```

### 数据库设计
```
projects          - 项目信息
uploaded_files    - 上传的文件
knowledge_bases   - 项目知识库
conversations     - 对话记录
messages          - 对话消息
```

---

## 🧪 测试

### 运行测试

```bash
# 测试项目管理
venv/bin/python backend/test_api.py

# 测试文件上传
venv/bin/python tests/integration/test_upload.py

# 测试知识库
venv/bin/python tests/integration/test_knowledge.py

# 测试对话功能
venv/bin/python tests/integration/test_conversation.py

# 测试导出功能
venv/bin/python tests/integration/test_export.py

# 测试所有 API（终端）
./scripts/test_all_apis.sh
```

### 测试覆盖
- ✅ 20 个 API 端点全部测试通过
- ✅ 文件上传和解析
- ✅ AI 分析和知识库构建
- ✅ 对话上下文管理
- ✅ PRD 文档生成

---

## 📊 API 文档

启动服务器后，访问自动生成的 API 文档：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 主要 API 端点

#### 项目管理
```
POST   /api/projects/           - 创建项目
GET    /api/projects/           - 获取项目列表
GET    /api/projects/{id}       - 获取项目详情
PATCH  /api/projects/{id}       - 更新项目
DELETE /api/projects/{id}       - 删除项目
```

#### 文件管理
```
POST   /api/files/upload                - 上传文件
POST   /api/files/{id}/analyze          - AI 分析文件
GET    /api/files/project/{project_id}  - 获取文件列表
DELETE /api/files/{id}                  - 删除文件
```

#### 知识库
```
POST   /api/knowledge/build/{project_id}  - 构建知识库
GET    /api/knowledge/{project_id}        - 获取知识库
PATCH  /api/knowledge/{project_id}        - 更新知识库
POST   /api/knowledge/{project_id}/confirm - 确认知识库
```

#### 对话
```
POST   /api/conversations/                    - 创建对话
GET    /api/conversations/project/{id}        - 获取对话列表
GET    /api/conversations/{id}                - 获取对话详情
POST   /api/conversations/{id}/chat           - 发送消息
DELETE /api/conversations/{id}                - 删除对话
```

#### 导出
```
POST   /api/export/conversation/{id}          - 导出 PRD (JSON)
GET    /api/export/conversation/{id}/download - 下载 PRD 文件
```

---

## 🔧 配置

### 环境变量 (.env)

```env
# 数据库配置
DATABASE_URL=postgresql+asyncpg://user@localhost:5432/prdsherpa

# Gemini API
GEMINI_API_KEY=your_api_key_here

# 应用配置
DEBUG=True
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# 文件上传
UPLOAD_DIR=uploads
MAX_FILE_SIZE=10485760        # 10MB
MAX_FILES_PER_PROJECT=50
```

详细配置说明请查看 [.env.example](.env.example)

---

## 📝 日志

### 查看日志

```bash
# 使用交互式日志查看器
./scripts/view_logs.sh

# 或直接查看日志文件
tail -f logs/app.log
```

### 日志级别
- **DEBUG**: 详细调试信息
- **INFO**: 一般信息（默认）
- **WARNING**: 警告信息
- **ERROR**: 错误信息

---

## 🎯 产品特色

### 1. 智能文件分析
- 支持 PDF、DOCX、TXT、MD、图片等多种格式
- AI 自动提取关键信息
- 识别 UI 元素、功能模块、技术要求

### 2. 项目知识库
- 自动整合多个文件的分析结果
- 生成结构化知识库
- 包含系统概览、UI 规范、技术约定
- AI 主动提出待确认问题

### 3. 对话式需求撰写
- 自然语言描述需求
- AI 主动提问澄清细节
- 记忆对话上下文
- 参考项目知识库

### 4. 专业 PRD 输出
- 完整的 7 大章节
- 结构化、可执行
- Markdown 格式
- 一键导出

---

## 🚀 生产部署

### Docker 部署（推荐）

```dockerfile
FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
docker build -t prdsherpa .
docker run -p 8000:8000 --env-file .env prdsherpa
```

### 传统部署

```bash
# 使用 gunicorn
pip install gunicorn
gunicorn backend.app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

详细部署指南请查看 [BACKEND_COMPLETE.md](docs/reports/BACKEND_COMPLETE.md)

---

## 🛠️ 开发

### 项目结构

```
prdsherpa/
├── backend/                  # 后端代码
│   ├── app/
│   │   ├── api/              # API 路由
│   │   ├── core/             # 核心配置
│   │   ├── models/           # 数据库模型
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── services/         # 业务逻辑
│   │   └── main.py           # 应用入口
│   └── init_db.py            # 数据库初始化
├── frontend/                 # 前端代码
│   ├── src/
│   │   ├── components/       # React 组件
│   │   ├── pages/            # 页面组件
│   │   ├── contexts/         # 状态管理
│   │   └── services/         # API 服务
│   └── package.json
├── docs/                     # 📚 文档中心
│   ├── guides/               # 使用指南
│   ├── architecture/         # 架构文档
│   ├── reports/              # 开发报告
│   └── README.md             # 文档导航
├── tests/                    # 测试脚本
│   └── integration/          # 集成测试
├── scripts/                  # 工具脚本
├── tools/                    # 开发工具
├── uploads/                  # 上传文件
├── logs/                     # 日志文件
├── .env                      # 环境变量
└── requirements.txt          # Python 依赖
```

### 添加新功能

1. 在 `backend/app/models/` 添加数据库模型
2. 在 `backend/app/schemas/` 添加 Pydantic schemas
3. 在 `backend/app/services/` 添加业务逻辑
4. 在 `backend/app/api/` 添加 API 路由
5. 在 `backend/app/main.py` 注册路由
6. 编写测试脚本

---

## 🤝 贡献

欢迎贡献代码、报告问题或提出建议！

### 贡献流程

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

---

## 🙏 致谢

- [FastAPI](https://fastapi.tiangolo.com/) - 现代、高性能的 Web 框架
- [Google Gemini](https://ai.google.dev/) - 强大的 AI 模型
- [PostgreSQL](https://www.postgresql.org/) - 可靠的数据库
- [SQLAlchemy](https://www.sqlalchemy.org/) - 优秀的 ORM

---

## 📞 联系方式

- 项目主页: [GitHub Repository]
- 问题反馈: [GitHub Issues]
- 文档: [docs/](docs/)

---

<div align="center">

**用 AI 让 PRD 写作更简单** ✨

Made with ❤️ by PRD助手 Team

</div>

