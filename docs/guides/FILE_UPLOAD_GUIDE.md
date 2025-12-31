# 📁 文件上传与 AI 分析功能指南

## 🎉 新功能已实现！

现在你可以上传文档和截图，让 AI 自动分析内容！

---

## 📋 支持的文件类型

### 文档类型
- ✅ PDF (`.pdf`)
- ✅ Word 文档 (`.docx`, `.doc`)
- ✅ 文本文件 (`.txt`)
- ✅ Markdown (`.md`)

### 图片类型
- ✅ PNG (`.png`)
- ✅ JPEG (`.jpg`, `.jpeg`)
- ✅ GIF (`.gif`)
- ✅ WebP (`.webp`)

### 限制
- 单文件最大：**10MB**
- 每个项目最多：**50个文件**

---

## 🚀 使用方法

### 方法 1: 使用 Swagger UI（推荐）

1. **打开 API 文档**
   ```
   http://localhost:8000/docs
   ```

2. **找到文件上传接口**
   ```
   POST /api/files/upload
   ```

3. **点击 "Try it out"**

4. **填写参数**
   - `project_id`: 项目 ID（从项目列表获取）
   - `file`: 选择要上传的文件

5. **点击 "Execute"**

6. **分析文件（获取 file_id 后）**
   ```
   POST /api/files/{file_id}/analyze
   ```

### 方法 2: 使用测试脚本

运行自动化测试脚本：

```bash
cd /Users/aiden/prdsherpa
venv/bin/python test_upload.py
```

这个脚本会：
1. ✅ 创建测试项目
2. ✅ 生成测试文档
3. ✅ 上传文件
4. ✅ 调用 AI 分析
5. ✅ 显示分析结果

### 方法 3: 使用 curl 命令

```bash
# 1. 创建项目
PROJECT_ID=$(curl -X POST http://localhost:8000/api/projects/ \
  -H "Content-Type: application/json" \
  -d '{"name": "测试项目"}' | jq -r '.id')

# 2. 上传文件
FILE_ID=$(curl -X POST http://localhost:8000/api/files/upload \
  -F "project_id=$PROJECT_ID" \
  -F "file=@/path/to/your/file.pdf" | jq -r '.id')

# 3. 分析文件
curl -X POST http://localhost:8000/api/files/$FILE_ID/analyze
```

---

## 🤖 AI 分析功能

AI 会从文件中提取以下信息：

### 1. 文档概述
简要描述文档的主要内容

### 2. 关键实体
- 模块名称
- 功能名称
- 字段名称
- API 接口名称

### 3. UI 信息（如果有）
- 布局方式
- 颜色方案
- 组件库

### 4. 技术约定
- 字段命名规范（如 camelCase）
- API 风格（如 RESTful）
- 数据类型

### 5. 重要引用
值得记录的具体内容片段

---

## 📖 API 端点说明

### 上传文件
```
POST /api/files/upload
```

**请求参数：**
- `project_id` (form): 项目 ID
- `file` (file): 文件

**响应：**
```json
{
  "id": "uuid",
  "project_id": "uuid",
  "filename": "test.pdf",
  "file_type": "pdf",
  "file_size": 12345,
  "status": "pending",
  "created_at": "2025-12-25T10:00:00"
}
```

### 分析文件
```
POST /api/files/{file_id}/analyze
```

**响应：**
```json
{
  "file_id": "uuid",
  "status": "completed",
  "analysis": {
    "summary": "这是一个用户管理模块的PRD文档...",
    "entities": ["用户管理", "userID", "登录接口"],
    "ui_info": {
      "layout": "左侧导航",
      "colors": ["#4299E1"]
    },
    "tech_info": {
      "naming": "camelCase",
      "api_style": "RESTful"
    },
    "references": ["用户ID使用userID字段"]
  },
  "message": "File analyzed successfully"
}
```

### 获取项目文件列表
```
GET /api/files/project/{project_id}
```

**响应：**
```json
{
  "files": [
    {
      "id": "uuid",
      "filename": "test.pdf",
      "status": "completed",
      "analysis_result": "文档概述..."
    }
  ],
  "total": 1
}
```

### 删除文件
```
DELETE /api/files/{file_id}
```

---

## ⚙️ 配置 Gemini API Key

**重要：** 要使用 AI 分析功能，必须配置 Gemini API Key。

### 1. 获取 API Key

访问：https://makersuite.google.com/app/apikey

### 2. 配置 .env 文件

编辑 `.env` 文件，填入你的 API Key：

```bash
GEMINI_API_KEY=你的_API_Key_这里
GEMINI_MODEL=gemini-2.0-flash-exp
```

### 3. 重启服务器

```bash
# 停止服务器（Ctrl+C）
# 重新启动
cd /Users/aiden/prdsherpa
venv/bin/python -m backend.app.main
```

---

## 🧪 测试示例

### 测试文档上传

创建一个测试文件 `test.md`：

```markdown
# 用户管理模块

## 字段定义
- userID: string
- userName: string
- userEmail: string

## API 接口
- POST /api/users/register
- POST /api/users/login
```

上传并分析：

```bash
# 上传
curl -X POST http://localhost:8000/api/files/upload \
  -F "project_id=YOUR_PROJECT_ID" \
  -F "file=@test.md"

# 分析（替换 FILE_ID）
curl -X POST http://localhost:8000/api/files/FILE_ID/analyze
```

---

## 🔍 工作流程

```
1. 用户上传文件
   ↓
2. 系统保存文件到 uploads/ 目录
   ↓
3. 创建数据库记录（status: pending）
   ↓
4. 用户触发分析
   ↓
5. 提取文本内容（PDF/DOCX）或直接处理图片
   ↓
6. 调用 Gemini API 分析
   ↓
7. 保存分析结果（status: completed）
   ↓
8. 返回结构化分析结果
```

---

## ❓ 常见问题

### Q: 上传文件后如何分析？

A: 上传成功后会返回 `file_id`，使用这个 ID 调用分析接口：
```
POST /api/files/{file_id}/analyze
```

### Q: 支持哪些图片格式？

A: PNG, JPEG, GIF, WebP。图片会直接由 Gemini Vision API 分析。

### Q: 文件存储在哪里？

A: 存储在 `uploads/{project_id}/` 目录下。

### Q: 如何查看已上传的文件？

A: 使用项目文件列表接口：
```
GET /api/files/project/{project_id}
```

### Q: Gemini API 报错怎么办？

A: 检查：
1. API Key 是否正确配置
2. API Key 是否有效
3. 网络是否能访问 Google API

---

## 📊 下一步功能

- [ ] 知识库构建（整合所有文件分析结果）
- [ ] 对话式 PRD 写作
- [ ] PRD 导出

---

## 🎯 快速开始

```bash
# 1. 确保服务器运行
cd /Users/aiden/prdsherpa
venv/bin/python -m backend.app.main

# 2. 打开 Swagger UI
open http://localhost:8000/docs

# 3. 或运行测试脚本
venv/bin/python test_upload.py
```

祝你使用愉快！🚀

