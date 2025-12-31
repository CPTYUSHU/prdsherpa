# PRD Sherpa 快速参考

> 📖 项目文档和常用命令的快速索引

## 📚 文档快速访问

### 🚀 新手入门
- **[项目主文档](README.md)** - 项目概述、特性、快速开始
- **[安装指南](docs/guides/SETUP.md)** - 详细的环境搭建步骤
- **[快速开始](docs/guides/QUICKSTART.md)** - 5分钟快速上手

### 📖 功能文档
- **[文件上传指南](docs/guides/FILE_UPLOAD_GUIDE.md)** - 文件上传和AI分析
- **[对话功能](docs/guides/CONVERSATION_FEATURE.md)** - 对话式需求撰写
- **[导出功能](docs/guides/EXPORT_FEATURE.md)** - PRD文档导出
- **[日志系统](docs/guides/LOGGING_GUIDE.md)** - 日志配置和使用

### 🏗️ 技术文档
- **[项目结构](docs/architecture/PROJECT_STRUCTURE.md)** - 代码组织说明
- **[项目组织](PROJECT_ORGANIZATION.md)** - 文件组织规范

### 📊 开发报告
- **[后端总结](docs/reports/BACKEND_COMPLETE.md)** - 后端开发完成情况
- **[前端总结](docs/reports/FRONTEND_COMPLETE.md)** - 前端开发完成情况
- **[测试报告](docs/reports/TERMINAL_TEST_REPORT.md)** - 完整测试结果
- **[整理报告](docs/reports/ORGANIZATION_COMPLETE.md)** - 文档整理完成情况

### 📋 完整导航
- **[文档中心](docs/README.md)** - 所有文档的导航中心

---

## 🚀 常用命令

### 后端开发

```bash
# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 初始化数据库
python backend/init_db.py

# 启动后端服务
python -m backend.app.main
# 访问：http://localhost:8000
# API文档：http://localhost:8000/docs
```

### 前端开发

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
# 访问：http://localhost:5173

# 构建生产版本
npm run build
```

### 测试

```bash
# 运行所有API测试
./scripts/test_all_apis.sh

# 运行单个测试
venv/bin/python tests/integration/test_upload.py
venv/bin/python tests/integration/test_knowledge.py
venv/bin/python tests/integration/test_conversation.py
venv/bin/python tests/integration/test_export.py

# 后端单元测试
venv/bin/python backend/test_api.py
```

### 日志查看

```bash
# 使用交互式日志查看器
./scripts/view_logs.sh

# 直接查看日志
tail -f logs/app.log
tail -f logs/server.log
tail -f logs/server_conversation.log
```

---

## 📁 项目结构速览

```
prdsherpa/
├── README.md                   # 项目主文档
├── PROJECT_ORGANIZATION.md     # 文件组织规范
├── QUICK_REFERENCE.md          # 本文件
│
├── docs/                       # 📚 文档中心
│   ├── README.md               # 文档导航
│   ├── guides/                 # 使用指南
│   ├── architecture/           # 架构文档
│   └── reports/                # 开发报告
│
├── backend/                    # 后端代码
│   ├── app/                    # FastAPI应用
│   ├── init_db.py              # 数据库初始化
│   └── test_api.py             # API测试
│
├── frontend/                   # 前端代码
│   ├── src/                    # 源代码
│   └── package.json            # 依赖配置
│
├── tests/                      # 测试代码
│   └── integration/            # 集成测试
│
├── scripts/                    # 工具脚本
│   ├── test_all_apis.sh        # 运行所有测试
│   └── view_logs.sh            # 日志查看器
│
├── tools/                      # 开发工具
│   ├── llm_api.py              # LLM API
│   ├── web_scraper.py          # 网页爬虫
│   └── search_engine.py        # 搜索引擎
│
├── uploads/                    # 上传文件存储
├── logs/                       # 日志文件
└── venv/                       # Python虚拟环境
```

---

## 🎯 快速定位

### 我想...

#### 开始使用项目
→ [快速开始](docs/guides/QUICKSTART.md)

#### 搭建开发环境
→ [安装指南](docs/guides/SETUP.md)

#### 了解项目功能
→ [项目主文档](README.md)

#### 查看API文档
→ 启动后端后访问 http://localhost:8000/docs

#### 运行测试
→ `./scripts/test_all_apis.sh`

#### 查看日志
→ `./scripts/view_logs.sh`

#### 添加新功能
→ [项目结构](docs/architecture/PROJECT_STRUCTURE.md)

#### 查找文档
→ [文档中心](docs/README.md)

#### 了解测试情况
→ [测试报告](docs/reports/TERMINAL_TEST_REPORT.md)

#### 了解项目组织规范
→ [项目组织](PROJECT_ORGANIZATION.md)

---

## 🔧 配置文件

### 环境变量 (.env)

```env
# 数据库
DATABASE_URL=postgresql+asyncpg://user@localhost:5432/prdsherpa

# Gemini API
GEMINI_API_KEY=your_api_key_here

# 应用配置
DEBUG=True
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# 文件上传
UPLOAD_DIR=uploads
MAX_FILE_SIZE=10485760
MAX_FILES_PER_PROJECT=50
```

详细配置说明：[SETUP.md](docs/guides/SETUP.md)

---

## 📊 项目状态

### ✅ 已完成功能

**后端 (20 API)**
- ✅ 项目管理 (5 API)
- ✅ 文件上传与AI分析 (4 API)
- ✅ 知识库构建 (4 API)
- ✅ 对话式需求撰写 (5 API)
- ✅ PRD导出 (2 API)

**前端**
- ✅ React 18 + TypeScript + Vite
- ✅ 项目管理界面
- ✅ 文件上传界面
- ✅ 知识库展示
- ✅ 对话界面
- ✅ PRD导出功能

**文档**
- ✅ 完整的功能文档
- ✅ 开发报告
- ✅ 测试报告
- ✅ 项目组织规范

---

## 🆘 常见问题

### 后端无法启动
1. 检查数据库是否运行
2. 检查 `.env` 配置是否正确
3. 查看日志：`tail -f logs/app.log`

### 前端无法连接后端
1. 确认后端已启动（http://localhost:8000）
2. 检查 CORS 配置
3. 查看浏览器控制台错误

### 测试失败
1. 确认数据库已初始化
2. 确认环境变量配置正确
3. 查看测试日志输出

### 找不到文档
→ 访问 [文档中心](docs/README.md) 查看所有文档

---

## 📞 获取帮助

1. **查看文档** - [docs/README.md](docs/README.md)
2. **查看日志** - `./scripts/view_logs.sh`
3. **查看测试** - [测试报告](docs/reports/TERMINAL_TEST_REPORT.md)
4. **查看组织规范** - [PROJECT_ORGANIZATION.md](PROJECT_ORGANIZATION.md)

---

<div align="center">

**快速、简洁、高效** ⚡

最后更新：2025-12-26

</div>

