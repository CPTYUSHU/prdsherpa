# CLAUDE.md 更新快速参考

## 🚀 三种更新方式

### 1️⃣ 自动提醒 (Git Hook)
```bash
git commit -m "your message"
# ✅ 自动检测重要文件修改
# ✅ 生成模板到 /tmp/claude_update_template.md
```

### 2️⃣ 快速更新 (Bash)
```bash
./scripts/update_claude_md.sh "变更说明" "影响范围"

# 示例:
./scripts/update_claude_md.sh \
  "新增流式响应" \
  "Gemini服务, Chat页面"
```

### 3️⃣ 智能更新 (Python) ⭐ 推荐
```bash
python3 tools/claude_doc_updater.py

# 或直接传参:
python3 tools/claude_doc_updater.py \
  "功能标题" \
  "详细描述"
```

## 📋 重要文件列表

工具自动监控以下文件的修改:

**后端**:
- `backend/app/services/gemini_service.py`
- `backend/app/services/conversation_service.py`
- `backend/app/services/knowledge_builder.py`
- `backend/app/services/file_processor.py`
- `backend/app/api/*.py`

**前端**:
- `frontend/src/pages/Chat.tsx`
- `frontend/src/pages/KnowledgeBase.tsx`

**配置**:
- `.env`
- `requirements.txt`

## 🔧 故障排除

```bash
# Hook 未执行?
chmod +x .git/hooks/pre-commit

# 脚本无权限?
chmod +x scripts/update_claude_md.sh
chmod +x tools/claude_doc_updater.py

# Python 找不到?
python3 tools/claude_doc_updater.py
```

## 📖 详细文档

查看完整指南: `docs/guides/CLAUDE_MD_AUTO_UPDATE.md`

---

💡 **推荐工作流**: 完成重要功能后，运行 `python3 tools/claude_doc_updater.py` 交互式记录变更
