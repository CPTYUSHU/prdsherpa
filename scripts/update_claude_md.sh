#!/bin/bash

# 更新 CLAUDE.md 的辅助脚本
# 用法: ./scripts/update_claude_md.sh "变更说明" "影响范围"

TIMESTAMP=$(date '+%Y-%m-%d')
CLAUDE_MD="CLAUDE.md"

# 检查参数
if [ $# -lt 2 ]; then
    echo "用法: $0 '变更说明' '影响范围'"
    echo ""
    echo "示例: $0 '新增流式AI响应功能' 'Gemini服务, 对话API, Chat页面'"
    exit 1
fi

CHANGE_DESC="$1"
IMPACT_SCOPE="$2"

# 获取最近的 Git 变更
RECENT_CHANGES=$(git diff HEAD~1 --name-only 2>/dev/null | head -10 | sed 's/^/  - /')

# 创建更新条目
UPDATE_ENTRY="
### $CHANGE_DESC ($TIMESTAMP)
- **变更说明**: $CHANGE_DESC
- **影响范围**: $IMPACT_SCOPE
- **修改文件**:
$RECENT_CHANGES
"

echo "=========================================="
echo "将要添加到 CLAUDE.md 的内容:"
echo "=========================================="
echo "$UPDATE_ENTRY"
echo "=========================================="
echo ""

read -p "确认添加到 CLAUDE.md? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    # 在 "## 最近功能更新" 章节后插入
    if grep -q "## 最近功能更新" "$CLAUDE_MD"; then
        # 使用 sed 在章节后插入
        sed -i.bak "/## 最近功能更新/a\\
$UPDATE_ENTRY
" "$CLAUDE_MD"
        rm "${CLAUDE_MD}.bak"
        echo "✅ 已成功更新 CLAUDE.md"
    else
        echo "❌ 未找到 '## 最近功能更新' 章节"
        echo "请手动将以下内容添加到 CLAUDE.md:"
        echo "$UPDATE_ENTRY"
    fi
else
    echo "已取消"
fi
