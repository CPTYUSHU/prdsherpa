# CLAUDE.md 自动更新指南

本文档说明如何使用自动化工具来记录重要代码变更到 CLAUDE.md 文档中。

## 可用工具

项目提供了三种方式来帮助你维护 CLAUDE.md 文档:

### 1. Git Pre-commit Hook (自动提醒)

**位置**: `.git/hooks/pre-commit`

**功能**: 在 Git 提交时自动检测重要文件的修改，并生成变更记录模板。

**使用方式**:
```bash
# 已自动启用，无需额外操作
git add .
git commit -m "your message"

# 如果检测到重要文件修改，会显示提醒和模板
```

**效果**:
- 自动检测以下重要文件的修改:
  - `backend/app/services/*.py`
  - `backend/app/api/*.py`
  - `frontend/src/pages/*.tsx`
  - `.env`, `requirements.txt`
- 生成变更记录模板到 `/tmp/claude_update_template.md`
- 提醒你更新 CLAUDE.md

### 2. Bash 脚本 (快速更新)

**位置**: `scripts/update_claude_md.sh`

**功能**: 快速将变更信息追加到 CLAUDE.md 的 "最近功能更新" 章节。

**使用方式**:
```bash
./scripts/update_claude_md.sh "变更说明" "影响范围"

# 示例:
./scripts/update_claude_md.sh \
  "新增流式AI响应功能" \
  "Gemini服务, 对话API, Chat页面"
```

**效果**:
- 自动在 CLAUDE.md 中插入格式化的更新条目
- 包含时间戳和最近修改的文件列表
- 需要确认后才会写入

### 3. Python 工具 (智能分析)

**位置**: `tools/claude_doc_updater.py`

**功能**: 智能分析 Git 变更，自动识别重要文件，交互式生成文档更新。

**使用方式**:

**交互式模式** (推荐):
```bash
python tools/claude_doc_updater.py
```

会提示你输入:
1. 变更标题 (例: "新增流式AI响应")
2. 变更描述 (简要说明)

**命令行模式**:
```bash
python tools/claude_doc_updater.py "变更标题" "变更描述"

# 示例:
python tools/claude_doc_updater.py \
  "新增流式AI响应" \
  "实现ChatGPT风格的实时响应流式输出"
```

**效果**:
- 自动分析 Git 中修改的文件
- 识别哪些是重要文件（有预定义列表）
- 生成包含文件修改统计的详细条目
- 自动插入到 CLAUDE.md 的正确位置

## 推荐工作流程

### 日常开发中

1. **正常开发**: 修改代码文件
2. **提交变更**: `git add .` 和 `git commit`
3. **查看提醒**: Pre-commit hook 会自动提醒你更新文档
4. **运行工具**: 如果修改重要，运行 `python tools/claude_doc_updater.py`
5. **确认更新**: 工具会显示将要添加的内容，确认后自动写入

### 完成重要功能后

使用 Python 工具记录详细的功能更新:

```bash
# 1. 分析变更
python tools/claude_doc_updater.py

# 2. 输入信息
📝 变更标题: 新增PowerPoint图片识别
📄 变更描述: 支持从PPTX文件中提取图片并使用Gemini进行多模态分析

# 3. 确认并写入
```

### 快速更新

如果只是小修改，使用 Bash 脚本快速更新:

```bash
./scripts/update_claude_md.sh \
  "修复文件上传bug" \
  "FileProcessor服务"
```

## CLAUDE.md 文档结构

更新会自动插入到以下章节:

```markdown
## 最近功能更新 (2025-12)

### 新功能标题 (2025-12-27)
- **变更说明**: ...
- **影响范围**: ...
- **修改文件**:
  - `file1.py` (描述)
  - `file2.tsx` (描述)

### 另一个功能 (2025-12-26)
...
```

## 重要文件列表

工具会特别关注以下文件的修改:

**后端核心服务**:
- `backend/app/services/gemini_service.py` - Gemini AI 服务
- `backend/app/services/conversation_service.py` - 对话服务
- `backend/app/services/knowledge_builder.py` - 知识库构建
- `backend/app/services/file_processor.py` - 文件处理

**后端 API**:
- `backend/app/api/conversations.py` - 对话 API
- `backend/app/api/files.py` - 文件 API

**前端页面**:
- `frontend/src/pages/Chat.tsx` - 聊天页面
- `frontend/src/pages/KnowledgeBase.tsx` - 知识库页面

**配置文件**:
- `.env` - 环境配置
- `requirements.txt` - Python 依赖

## 自定义配置

### 添加更多重要文件

编辑 `tools/claude_doc_updater.py`:

```python
IMPORTANT_FILES = {
    "your/file/path.py": "文件描述",
    # ... 添加更多
}
```

### 修改检测规则

编辑 `.git/hooks/pre-commit`:

```bash
IMPORTANT_FILES=(
    "your/pattern/*.py"
    # ... 添加更多
)
```

## 故障排除

### Pre-commit hook 未触发

```bash
# 检查权限
ls -la .git/hooks/pre-commit

# 如果没有执行权限，添加权限
chmod +x .git/hooks/pre-commit
```

### Python 工具报错

```bash
# 确保在项目根目录运行
cd /Users/aiden/prdsherpa

# 激活虚拟环境（如果需要）
source venv/bin/activate

# 运行工具
python tools/claude_doc_updater.py
```

### 找不到 "## 最近功能更新" 章节

确保 CLAUDE.md 中有这个章节标题。如果没有，工具会提示你手动添加内容。

## 最佳实践

1. **及时记录**: 完成重要功能后立即更新文档
2. **详细描述**: 提供清晰的变更说明，帮助团队成员理解
3. **标记影响**: 明确指出变更影响的模块和功能
4. **定期审查**: 每周查看 CLAUDE.md，确保文档完整准确
5. **版本标记**: 重大更新时标注日期，方便追溯

## 示例

### 完整的更新示例

```bash
$ python tools/claude_doc_updater.py

🔍 正在分析代码变更...

📋 检测到 3 个重要文件的修改:
  - backend/app/services/gemini_service.py (Gemini AI 服务)
  - backend/app/api/conversations.py (对话 API)
  - frontend/src/pages/Chat.tsx (聊天页面)

==================================================
请提供变更信息:
==================================================
📝 变更标题: 实现流式AI响应
📄 变更描述: 使用SSE实现ChatGPT风格的实时响应流式输出

==================================================
将要添加的内容:
==================================================

### 实现流式AI响应 (2025-12-27)
- **变更说明**: 使用SSE实现ChatGPT风格的实时响应流式输出
- **修改文件**:
  - `backend/app/services/gemini_service.py` (Gemini AI 服务)
    - 1 file changed, 45 insertions(+), 2 deletions(-)
  - `backend/app/api/conversations.py` (对话 API)
    - 1 file changed, 78 insertions(+), 5 deletions(-)
  - `frontend/src/pages/Chat.tsx` (聊天页面)
    - 1 file changed, 56 insertions(+), 12 deletions(-)

==================================================

❓ 确认添加到 CLAUDE.md? (y/n): y
✅ 已成功更新 CLAUDE.md
```

---

通过这些工具，你可以轻松地维护项目文档，确保 CLAUDE.md 始终反映最新的代码变更和功能更新。
