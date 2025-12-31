# PRD Sherpa 部署使用指南

> 本指南适用于团队成员快速部署和使用 PRD Sherpa 系统

## 📋 目录

- [项目简介](#项目简介)
- [环境要求](#环境要求)
- [快速开始](#快速开始)
- [配置说明](#配置说明)
- [启动服务](#启动服务)
- [功能使用](#功能使用)
- [常见问题](#常见问题)
- [故障排查](#故障排查)

---

## 项目简介

**PRD Sherpa** 是一个基于 AI 的产品需求文档(PRD)写作助手，专为产品经理设计。通过对话式界面帮助明确需求并生成专业、结构化的 PRD 文档。

### 核心功能

- **智能文件分析**: 上传 PRD、设计稿、原型图、PowerPoint（含图片识别）
- **知识库构建**: AI 自动汇总分析，生成 12 个章节的结构化知识库
- **对话式需求澄清**: 流式 AI 对话，实时响应，支持图片上传
- **PRD 自动生成**: 一键导出 Markdown/Word/HTML/PDF 格式 PRD

### 技术栈

- **后端**: FastAPI + PostgreSQL/SQLite + SQLAlchemy 2.0 (异步)
- **前端**: React 19 + TypeScript + Vite + Ant Design + Tailwind CSS
- **AI**: 支持多模型切换（Gemini/GPT-4/Claude）

---

## 环境要求

### 必需软件

- **Python**: 3.9 或更高版本
- **Node.js**: 16.x 或更高版本
- **npm**: 8.x 或更高版本
- **数据库**: SQLite（默认）或 PostgreSQL

### 推荐配置

- 操作系统: macOS / Linux / Windows
- 内存: 4GB 以上
- 磁盘空间: 2GB 以上

---

## 快速开始

### 1. 克隆项目

```bash
git clone <你的仓库地址>
cd prdsherpa
```

### 2. 安装后端依赖

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 3. 安装前端依赖

```bash
cd frontend
npm install
cd ..
```

### 4. 配置环境变量

```bash
# 复制配置模板
cp .env.example .env

# 编辑配置文件（重要！）
# macOS/Linux 使用:
nano .env
# 或
vim .env
```

**必须配置的字段**（见下一节 [配置说明](#配置说明)）

### 5. 初始化数据库

```bash
# 确保虚拟环境已激活
source venv/bin/activate

# 初始化数据库（仅首次运行）
python backend/init_db.py
```

### 6. 启动服务

```bash
# 启动后端（新终端窗口 1）
source venv/bin/activate
python -m backend.app.main

# 启动前端（新终端窗口 2）
cd frontend
npm run dev
```

### 7. 访问应用

- **前端界面**: http://localhost:5173
- **后端 API**: http://localhost:8000
- **API 文档**: http://localhost:8000/docs

---

## 配置说明

### 核心配置项（`.env` 文件）

#### 1. 数据库配置

**SQLite（推荐，开箱即用）**
```bash
DATABASE_URL=sqlite+aiosqlite:///./prdsherpa.db
```

**PostgreSQL（生产环境）**
```bash
DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/prdsherpa
```

#### 2. AI 模型配置

**必须配置至少一个 AI 服务的 API Key**

##### 选项 1: Google Gemini（推荐，免费）

```bash
# 获取密钥: https://aistudio.google.com/app/apikey
GEMINI_API_KEY=你的_gemini_api_key
GEMINI_MODEL=gemini-3-flash-preview
DEFAULT_AI_PROVIDER=gemini
```

##### 选项 2: OpenAI GPT-4（付费）

```bash
# 获取密钥: https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-你的_openai_key
OPENAI_MODEL=gpt-4-turbo-preview
DEFAULT_AI_PROVIDER=openai
```

##### 选项 3: Anthropic Claude（付费）

```bash
# 获取密钥: https://console.anthropic.com/
CLAUDE_API_KEY=sk-ant-你的_claude_key
CLAUDE_MODEL=claude-3-5-sonnet-20241022
DEFAULT_AI_PROVIDER=claude
```

#### 3. 网络代理配置（国内用户必看）

如果你在国内无法直接访问 AI 服务，需要配置代理：

```bash
# Clash/V2ray（常见端口 7890）
HTTP_PROXY=http://127.0.0.1:7890
HTTPS_PROXY=http://127.0.0.1:7890

# Shadowsocks（常见端口 1087）
HTTP_PROXY=http://127.0.0.1:1087
HTTPS_PROXY=http://127.0.0.1:1087
```

**如何查找代理端口**:
- **Clash**: 打开设置 → 查看 HTTP 端口
- **V2ray**: 查看配置中的 HTTP 代理端口
- **Shadowsocks**: 查看本地端口设置

#### 4. Redis 配置（可选）

用于后台任务队列（文件分析、PRD 生成）：

```bash
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

如果未安装 Redis，可以临时注释掉这些配置。

#### 5. 其他配置

```bash
# 调试模式
DEBUG=True

# 密钥（生产环境请更换）
SECRET_KEY=your_secret_key_here_change_in_production

# CORS 跨域配置
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# 文件上传配置
UPLOAD_DIR=./uploads
MAX_FILE_SIZE_MB=200
MAX_FILES_PER_PROJECT=50
```

### 完整配置示例

```bash
# 数据库
DATABASE_URL=sqlite+aiosqlite:///./prdsherpa.db

# AI 配置（Gemini + 代理）
GEMINI_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXX
GEMINI_MODEL=gemini-3-flash-preview
DEFAULT_AI_PROVIDER=gemini

# 网络代理
HTTP_PROXY=http://127.0.0.1:7890
HTTPS_PROXY=http://127.0.0.1:7890

# Redis
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# 应用配置
DEBUG=True
SECRET_KEY=dev_secret_key_change_in_production
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# 文件上传
UPLOAD_DIR=./uploads
MAX_FILE_SIZE_MB=200
MAX_FILES_PER_PROJECT=50
```

---

## 启动服务

### 开发环境

**方式 1: 两个终端窗口**

```bash
# 终端 1 - 后端
source venv/bin/activate
python -m backend.app.main

# 终端 2 - 前端
cd frontend
npm run dev
```

**方式 2: 后台运行**

```bash
# 后端后台运行
source venv/bin/activate
nohup python -m backend.app.main > logs/server.log 2>&1 &

# 前端后台运行
cd frontend
nohup npm run dev > ../logs/frontend.log 2>&1 &
```

### 生产环境

```bash
# 后端（使用 Gunicorn + Uvicorn）
source venv/bin/activate
gunicorn backend.app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000

# 前端（构建静态文件）
cd frontend
npm run build
# 使用 Nginx 提供静态文件服务
```

### 停止服务

```bash
# Ctrl+C 停止前台运行的服务

# 或查找并停止后台进程
ps aux | grep "backend.app.main"
kill <进程ID>

ps aux | grep "npm run dev"
kill <进程ID>
```

---

## 功能使用

### 1. 创建项目

1. 打开浏览器访问 http://localhost:5173
2. 点击"新建项目"按钮
3. 填写项目名称和描述
4. 点击"创建"

### 2. 上传文件分析

支持的文件类型：
- **文档**: PDF, Word (.docx), Markdown (.md), TXT
- **设计**: 图片 (PNG, JPG, JPEG), PowerPoint (.pptx)
- **原型**: Figma 导出文件

操作步骤：
1. 进入项目详情页
2. 点击"上传文件"
3. 选择文件（支持批量上传）
4. 等待 AI 自动分析（显示进度条）
5. 查看分析结果

### 3. 构建知识库

1. 上传文件后，点击"构建知识库"
2. AI 将汇总所有文件分析，生成 12 个章节：
   - 项目概览
   - 功能架构
   - 用户体验
   - UI/UX 设计
   - 技术架构
   - 数据模型
   - 业务规则
   - 非功能性需求
   - 等...
3. 查看和搜索知识库内容

### 4. 对话式需求澄清

1. 进入"对话"页面
2. 创建新对话或选择已有对话
3. 输入需求描述
4. AI 会基于知识库提出澄清问题
5. 支持上传图片辅助说明
6. 实时流式响应（ChatGPT 风格）

### 5. 导出 PRD

1. 对话完成后，点击"导出 PRD"
2. 选择导出格式：
   - **Markdown**: 纯文本，易于版本控制
   - **Word**: 可编辑文档
   - **HTML**: 网页格式，样式优雅
   - **PDF**: 最终交付格式
3. 选择是否包含知识库
4. 点击"下载"

---

## 常见问题

### 1. 启动后端报错：`ModuleNotFoundError`

**原因**: 虚拟环境未激活

**解决**:
```bash
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate  # Windows
```

### 2. AI 响应超时或失败

**原因**: 网络无法访问 AI 服务

**解决**:
1. 检查代理配置是否正确
2. 确认代理软件正在运行
3. 尝试切换其他 AI 服务（如 OpenAI/Claude）

```bash
# 方式 1: 配置代理
HTTP_PROXY=http://127.0.0.1:7890
HTTPS_PROXY=http://127.0.0.1:7890

# 方式 2: 切换 AI 服务
DEFAULT_AI_PROVIDER=openai  # 或 claude
```

### 3. 数据库连接失败

**SQLite 报错**: 检查文件权限
```bash
chmod 644 prdsherpa.db
```

**PostgreSQL 报错**: 检查连接字符串和数据库服务
```bash
# 确认 PostgreSQL 正在运行
pg_isready

# 测试连接
psql -U username -d prdsherpa
```

### 4. 前端无法访问后端 API

**原因**: CORS 配置问题

**解决**:
```bash
# .env 文件中添加前端地址
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

### 5. 文件上传失败

**原因**: 文件过大或格式不支持

**解决**:
1. 检查文件大小限制（默认 200MB）
2. 确认文件格式在支持列表中
3. 查看后端日志：`tail -f logs/app.log`

### 6. Redis 连接失败

**临时解决**（如未安装 Redis）:
```bash
# 注释掉 .env 中的 Redis 配置
# REDIS_URL=redis://localhost:6379/0
# CELERY_BROKER_URL=redis://localhost:6379/0
# CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

**永久解决**（安装 Redis）:
```bash
# macOS
brew install redis
brew services start redis

# Ubuntu/Debian
sudo apt install redis-server
sudo systemctl start redis

# Windows
# 下载并安装: https://github.com/microsoftarchive/redis/releases
```

---

## 故障排查

### 查看日志

```bash
# 应用日志
tail -f logs/app.log

# 服务器日志
tail -f logs/server.log

# 前端日志
tail -f logs/frontend.log
```

### 测试 API

```bash
# 测试后端健康检查
curl http://localhost:8000/health

# 测试项目列表 API
curl http://localhost:8000/api/projects/
```

### 重置数据库

```bash
# 删除旧数据库
rm prdsherpa.db

# 重新初始化
source venv/bin/activate
python backend/init_db.py
```

### 清理缓存

```bash
# 清理 Python 缓存
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete

# 清理前端缓存
cd frontend
rm -rf node_modules/.vite
rm -rf dist

# 重新安装依赖
npm install
```

---

## 项目结构

```
prdsherpa/
├── backend/              # 后端代码
│   ├── app/
│   │   ├── api/         # API 路由（21个端点）
│   │   ├── core/        # 核心配置
│   │   ├── models/      # 数据库模型
│   │   ├── schemas/     # Pydantic 模式
│   │   └── services/    # 业务逻辑
│   └── init_db.py       # 数据库初始化
├── frontend/            # 前端代码
│   ├── src/
│   │   ├── components/  # React 组件
│   │   ├── pages/       # 页面组件
│   │   ├── services/    # API 客户端
│   │   └── types/       # TypeScript 类型
│   └── package.json
├── logs/                # 日志文件
├── uploads/             # 上传文件存储
├── .env                 # 环境配置（不提交）
├── .env.example         # 配置模板
├── requirements.txt     # Python 依赖
└── DEPLOYMENT_GUIDE.md  # 本文档
```

---

## 获取帮助

### 文档

- **快速开始**: `docs/guides/QUICKSTART.md`
- **功能指南**: `docs/guides/`
- **API 文档**: http://localhost:8000/docs
- **架构文档**: `docs/architecture/`

### 联系方式

- **技术支持**: 联系项目维护者
- **Bug 报告**: 提交 Issue 到 Git 仓库
- **功能建议**: 查看 `CLAUDE.md` 中的 TODO 清单

---

## 安全提示

- **生产环境必须更改 `SECRET_KEY`**
- **不要提交 `.env` 文件到 Git**
- **定期更新依赖包**
- **使用 HTTPS（生产环境）**
- **API Key 妥善保管，不要分享**

---

## 版本信息

- **版本**: 1.0.0
- **更新日期**: 2025-12-31
- **Python**: 3.9+
- **Node.js**: 16.x+
- **数据库**: SQLite / PostgreSQL

---

祝使用愉快！如有问题，请查阅文档或联系维护者。
