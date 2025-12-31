# 📊 日志系统使用指南

## 🎉 日志系统已完成！

现在每个 API 请求都会记录详细日志，便于调试和问题定位。

---

## 📁 日志文件位置

### 应用日志
```
logs/app.log
```

包含所有应用日志：
- HTTP 请求/响应
- 数据库操作
- AI 分析过程
- 错误信息

### 服务器日志
```
logs/server.log
```

包含服务器启动和运行时日志。

---

## 🔍 日志格式

### 标准日志格式
```
时间戳 | 级别 | 模块:函数:行号 | 消息
```

示例：
```
2025-12-25 22:22:05 | INFO | api.request:dispatch:44 | ✅ POST /api/projects/ → 201 (15.32ms)
```

### 请求日志格式
```
✅ METHOD /path → STATUS_CODE (DURATION_ms)
```

图标说明：
- ✅ 成功 (2xx, 3xx)
- ⚠️ 客户端错误 (4xx)
- ❌ 服务器错误 (5xx)

---

## 📖 查看日志的方法

### 方法 1: 使用日志查看脚本（推荐）

```bash
./view_logs.sh
```

提供 7 种查看模式：
1. 实时查看日志
2. 查看最近 50 条
3. 查看最近 100 条
4. 只看请求日志
5. 只看错误日志
6. 只看 AI 相关日志
7. 搜索日志

### 方法 2: 直接查看文件

```bash
# 查看最新日志
tail -f logs/app.log

# 查看最近 50 条
tail -50 logs/app.log

# 搜索特定内容
grep "ERROR" logs/app.log
```

### 方法 3: 使用命令行工具

```bash
# 只看请求日志
grep "→" logs/app.log

# 只看成功的请求
grep "✅" logs/app.log

# 只看失败的请求
grep "❌" logs/app.log

# 只看 AI 分析日志
grep "analyze" logs/app.log

# 只看数据库日志
grep "sqlalchemy" logs/app.log
```

---

## 🎯 常见调试场景

### 场景 1: API 请求失败

**问题**：调用 API 返回 500 错误

**调试步骤**：
```bash
# 1. 查看最近的错误日志
grep "❌" logs/app.log | tail -10

# 2. 查看完整的错误堆栈
grep -A 20 "ERROR" logs/app.log | tail -50
```

### 场景 2: AI 分析很慢

**问题**：文件分析需要很长时间

**调试步骤**：
```bash
# 查看 AI 分析的耗时
grep "analyze" logs/app.log | grep "ms"

# 示例输出：
# ✅ POST /api/files/{id}/analyze → 200 (2833.38ms)
```

### 场景 3: 数据库查询问题

**问题**：数据没有正确保存

**调试步骤**：
```bash
# 查看 SQL 查询
grep "sqlalchemy.engine" logs/app.log | tail -20

# 查看特定表的操作
grep "projects" logs/app.log | grep "INSERT\|UPDATE\|DELETE"
```

### 场景 4: 文件上传失败

**问题**：文件上传返回错误

**调试步骤**：
```bash
# 查看文件上传相关日志
grep "upload" logs/app.log | tail -20

# 查看文件处理日志
grep "file_processor" logs/app.log | tail -20
```

---

## 📊 日志级别

### DEBUG
详细的调试信息（仅在 DEBUG 模式下）

### INFO
正常的业务流程信息
- HTTP 请求
- 数据库操作
- 业务逻辑执行

### WARNING
警告信息（不影响功能）
- 参数验证失败
- 非关键错误

### ERROR
错误信息（影响功能）
- API 调用失败
- 数据库错误
- AI 分析失败

---

## 🔧 配置日志

### 修改日志级别

编辑 `.env` 文件：

```bash
# 开发模式（详细日志）
DEBUG=True

# 生产模式（简洁日志）
DEBUG=False
```

### 修改日志配置

编辑 `backend/app/core/logging_config.py`：

```python
# 修改日志格式
log_format = "%(asctime)s | %(levelname)s | %(message)s"

# 修改日志级别
log_level = "DEBUG"  # 或 "INFO", "WARNING", "ERROR"
```

---

## 📝 日志示例

### 成功的 API 请求

```
2025-12-25 22:22:02 | INFO | api.request:dispatch:22 | → POST /api/projects/ (client: 127.0.0.1)
2025-12-25 22:22:02 | INFO | backend.app.api.projects:create_project:45 | ✅ Created project: 测试项目 (ID: abc-123)
2025-12-25 22:22:02 | INFO | api.request:dispatch:44 | ✅ POST /api/projects/ → 201 (15.32ms)
```

### 文件上传和分析

```
2025-12-25 22:22:02 | INFO | api.request:dispatch:22 | → POST /api/files/upload (client: 127.0.0.1)
2025-12-25 22:22:02 | INFO | backend.app.api.files:upload_file:95 | Saved file: uploads/proj-123/file.pdf (12345 bytes)
2025-12-25 22:22:02 | INFO | api.request:dispatch:44 | ✅ POST /api/files/upload → 201 (8.27ms)

2025-12-25 22:22:03 | INFO | api.request:dispatch:22 | → POST /api/files/file-456/analyze (client: 127.0.0.1)
2025-12-25 22:22:03 | INFO | backend.app.services.file_processor:process_file:78 | Extracted 1234 characters from PDF
2025-12-25 22:22:05 | INFO | backend.app.services.gemini_service:analyze_document:120 | Generated text with 699 characters
2025-12-25 22:22:05 | INFO | backend.app.api.files:analyze_file:190 | File analysis completed: file.pdf
2025-12-25 22:22:05 | INFO | api.request:dispatch:44 | ✅ POST /api/files/file-456/analyze → 200 (2833.38ms)
```

### 错误日志

```
2025-12-25 22:22:10 | ERROR | api.request:dispatch:52 | ❌ POST /api/files/upload → ERROR (5.23ms): ValueError: File too large
2025-12-25 22:22:10 | ERROR | backend.app.api.files:upload_file:85 | File size exceeds limit: 15MB > 10MB
```

---

## 🚀 实时监控

### 实时查看所有日志
```bash
tail -f logs/app.log
```

### 实时查看请求日志
```bash
tail -f logs/app.log | grep "→"
```

### 实时查看错误
```bash
tail -f logs/app.log | grep "ERROR\|❌"
```

---

## 📦 日志文件管理

### 清理旧日志
```bash
# 清空日志文件
> logs/app.log

# 或删除日志文件
rm logs/app.log
```

### 日志轮转（TODO）
未来可以配置日志轮转，自动归档旧日志：
- 按日期分割（app-2025-12-25.log）
- 按大小分割（app.log.1, app.log.2）
- 自动压缩旧日志

---

## 🎯 最佳实践

### 1. 开发时
- 设置 `DEBUG=True`
- 实时查看日志：`tail -f logs/app.log`
- 关注错误和警告

### 2. 测试时
- 运行测试后查看日志
- 验证所有 API 调用都有日志
- 检查响应时间

### 3. 生产环境
- 设置 `DEBUG=False`
- 定期检查错误日志
- 监控响应时间
- 配置日志轮转

---

## 🔍 快速命令参考

```bash
# 查看最新日志
tail -50 logs/app.log

# 实时查看
tail -f logs/app.log

# 查看请求日志
grep "→" logs/app.log

# 查看错误
grep "ERROR\|❌" logs/app.log

# 搜索关键词
grep -i "keyword" logs/app.log

# 统计请求数
grep "✅" logs/app.log | wc -l

# 统计错误数
grep "❌" logs/app.log | wc -l

# 查看最慢的请求
grep "ms)" logs/app.log | sort -t'(' -k2 -rn | head -10
```

---

## 📚 相关文档

- [QUICKSTART.md](./QUICKSTART.md) - 快速启动指南
- [FILE_UPLOAD_GUIDE.md](./FILE_UPLOAD_GUIDE.md) - 文件上传指南
- http://localhost:8000/docs - API 文档

---

祝你调试顺利！🎊

