# 🚀 快速启动指南

## 前置条件检查

在开始之前，确保已安装：

- ✅ Python 3.13+ （已安装在 `venv/`）
- ⬜ PostgreSQL 14+
- ⬜ Redis（用于 Celery，可选）
- ⬜ Gemini API Key

---

## 5 分钟快速启动

### 1️⃣ 安装 PostgreSQL

**macOS (Homebrew):**
```bash
brew install postgresql@14
brew services start postgresql@14
createdb prdsherpa
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo -u postgres createdb prdsherpa
```

**验证安装:**
```bash
psql prdsherpa -c "SELECT version();"
```

### 2️⃣ 获取 Gemini API Key

1. 访问 https://makersuite.google.com/app/apikey
2. 点击 "Create API Key"
3. 复制生成的 API Key

### 3️⃣ 配置环境变量

编辑 `.env` 文件（已存在），修改以下两项：

```bash
# 修改数据库连接（替换用户名和密码）
DATABASE_URL=postgresql+asyncpg://你的用户名:你的密码@localhost:5432/prdsherpa

# 填入 Gemini API Key
GEMINI_API_KEY=你的_API_Key_这里
```

**macOS 默认 PostgreSQL 配置:**
```bash
DATABASE_URL=postgresql+asyncpg://$(whoami)@localhost:5432/prdsherpa
```

### 4️⃣ 初始化数据库

```bash
cd /Users/aiden/prdsherpa
venv/bin/python -m backend.init_db
```

**预期输出:**
```
Creating database tables...
✅ Database tables created successfully!
```

### 5️⃣ 启动服务器

```bash
venv/bin/python -m backend.app.main
```

**预期输出:**
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 6️⃣ 测试 API

**方式 1: 浏览器访问 Swagger UI**
```
http://localhost:8000/docs
```

**方式 2: 运行测试脚本**
```bash
# 新开一个终端
venv/bin/python backend/test_api.py
```

**方式 3: 使用 curl**
```bash
# 健康检查
curl http://localhost:8000/

# 创建项目
curl -X POST http://localhost:8000/api/projects/ \
  -H "Content-Type: application/json" \
  -d '{"name": "测试项目", "description": "我的第一个项目"}'

# 获取项目列表
curl http://localhost:8000/api/projects/
```

---

## 🎉 成功！

如果看到以下内容，说明一切正常：

```json
{
  "status": "ok",
  "message": "PRD助手 API is running",
  "version": "0.1.0"
}
```

---

## 📖 下一步

### 探索 API 文档
访问 http://localhost:8000/docs，查看所有可用的 API 端点。

### 创建第一个项目
在 Swagger UI 中：
1. 找到 `POST /api/projects/`
2. 点击 "Try it out"
3. 输入项目名称和描述
4. 点击 "Execute"

### 查看数据库
```bash
psql prdsherpa
\dt  # 查看所有表
SELECT * FROM projects;  # 查看项目数据
```

---

## ❓ 遇到问题？

### 问题 1: 数据库连接失败

**错误信息:**
```
asyncpg.exceptions.InvalidCatalogNameError: database "prdsherpa" does not exist
```

**解决方法:**
```bash
createdb prdsherpa
```

---

### 问题 2: PostgreSQL 用户名/密码错误

**错误信息:**
```
asyncpg.exceptions.InvalidPasswordError
```

**解决方法:**

查看当前用户：
```bash
whoami
```

查看 PostgreSQL 用户：
```bash
psql -l
```

修改 `.env` 中的 `DATABASE_URL`：
```bash
# 如果不需要密码（本地开发）
DATABASE_URL=postgresql+asyncpg://你的用户名@localhost:5432/prdsherpa

# 如果需要密码
DATABASE_URL=postgresql+asyncpg://你的用户名:你的密码@localhost:5432/prdsherpa
```

---

### 问题 3: Gemini API Key 无效

**错误信息:**
```
google.api_core.exceptions.PermissionDenied: 403 API key not valid
```

**解决方法:**
1. 检查 API Key 是否正确复制（没有多余空格）
2. 确认 API Key 已启用
3. 访问 https://makersuite.google.com/app/apikey 重新生成

---

### 问题 4: 端口 8000 已被占用

**错误信息:**
```
OSError: [Errno 48] Address already in use
```

**解决方法:**

查找占用端口的进程：
```bash
lsof -i :8000
```

杀死进程：
```bash
kill -9 <PID>
```

或使用其他端口：
```bash
venv/bin/python -m uvicorn backend.app.main:app --port 8001
```

---

## 🔧 高级配置

### 启用调试模式

在 `.env` 中设置：
```bash
DEBUG=True
```

这将：
- 输出所有 SQL 查询
- 启用自动重载（代码修改后自动重启）
- 显示详细错误信息

### 配置 CORS（跨域）

如果前端运行在不同端口，修改 `.env`：
```bash
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### 修改文件上传限制

在 `.env` 中：
```bash
MAX_FILE_SIZE_MB=20          # 单文件最大 20MB
MAX_FILES_PER_PROJECT=100    # 每个项目最多 100 个文件
```

---

## 📚 相关文档

- [SETUP.md](./SETUP.md) - 详细的项目搭建说明
- [PROJECT_STRUCTURE.md](./PROJECT_STRUCTURE.md) - 项目结构说明
- [backend/README.md](./backend/README.md) - 后端开发文档
- [ProductSpec](./ProductSpec) - 产品规格文档

---

## 💡 小贴士

1. **使用 Swagger UI 调试**: `/docs` 是最方便的 API 测试工具
2. **查看日志**: 所有日志输出到控制台，包括 SQL 查询
3. **数据库管理**: 使用 `psql` 或 pgAdmin 查看数据
4. **代码修改自动重载**: 在 DEBUG 模式下，修改代码会自动重启服务器

---

祝你使用愉快！🎊

