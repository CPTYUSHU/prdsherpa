#!/usr/bin/env python3
"""
CLAUDE.md 自动更新工具
用于记录重要代码变更到项目文档中
"""

import sys
import subprocess
from datetime import datetime
from pathlib import Path

CLAUDE_MD_PATH = Path(__file__).parent.parent / "CLAUDE.md"

# 重要文件列表
IMPORTANT_FILES = {
    "backend/app/services/gemini_service.py": "Gemini AI 服务",
    "backend/app/services/conversation_service.py": "对话服务",
    "backend/app/services/knowledge_builder.py": "知识库构建",
    "backend/app/services/file_processor.py": "文件处理",
    "backend/app/api/conversations.py": "对话 API",
    "backend/app/api/files.py": "文件 API",
    "frontend/src/pages/Chat.tsx": "聊天页面",
    "frontend/src/pages/KnowledgeBase.tsx": "知识库页面",
    ".env": "环境配置",
    "requirements.txt": "Python 依赖",
}

def get_git_changed_files():
    """获取 Git 中已修改但未提交的文件"""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip().split('\n') if result.stdout.strip() else []
    except subprocess.CalledProcessError:
        return []

def get_git_diff_summary(file_path):
    """获取指定文件的修改摘要"""
    try:
        result = subprocess.run(
            ["git", "diff", "--stat", "HEAD", "--", file_path],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return ""

def analyze_changes():
    """分析当前的代码变更"""
    changed_files = get_git_changed_files()

    important_changes = []
    for file in changed_files:
        if file in IMPORTANT_FILES:
            description = IMPORTANT_FILES[file]
            diff_summary = get_git_diff_summary(file)
            important_changes.append({
                'file': file,
                'description': description,
                'diff': diff_summary
            })

    return important_changes

def generate_update_entry(title, description, changes):
    """生成文档更新条目"""
    timestamp = datetime.now().strftime("%Y-%m-%d")

    entry = f"\n### {title} ({timestamp})\n"
    entry += f"- **变更说明**: {description}\n"

    if changes:
        entry += "- **修改文件**:\n"
        for change in changes:
            entry += f"  - `{change['file']}` ({change['description']})\n"
            if change['diff']:
                lines = change['diff'].split('\n')
                if len(lines) > 0:
                    entry += f"    - {lines[0].strip()}\n"

    return entry

def insert_update_to_claude_md(entry):
    """将更新条目插入到 CLAUDE.md"""
    if not CLAUDE_MD_PATH.exists():
        print(f"❌ 未找到 CLAUDE.md 文件: {CLAUDE_MD_PATH}")
        return False

    content = CLAUDE_MD_PATH.read_text(encoding='utf-8')

    # 查找插入位置（在 "## 最近功能更新" 章节后）
    marker = "## 最近功能更新"

    if marker in content:
        # 找到标记位置
        parts = content.split(marker, 1)

        # 在标记后的第一个换行符之后插入
        after_marker = parts[1]
        first_newline = after_marker.find('\n')

        if first_newline != -1:
            new_content = (
                parts[0] +
                marker +
                after_marker[:first_newline] +
                entry +
                after_marker[first_newline:]
            )

            CLAUDE_MD_PATH.write_text(new_content, encoding='utf-8')
            return True

    print(f"❌ 未在 CLAUDE.md 中找到 '{marker}' 章节")
    print(f"📝 请手动将以下内容添加到文档中:\n{entry}")
    return False

def main():
    """主函数"""
    print("🔍 正在分析代码变更...")

    # 分析变更
    changes = analyze_changes()

    if not changes:
        print("✅ 未检测到重要文件的修改")
        return

    print(f"\n📋 检测到 {len(changes)} 个重要文件的修改:")
    for change in changes:
        print(f"  - {change['file']} ({change['description']})")

    print("\n" + "="*50)
    print("请提供变更信息:")
    print("="*50)

    # 交互式获取信息
    if len(sys.argv) > 1:
        title = sys.argv[1]
    else:
        title = input("📝 变更标题 (例: 新增流式AI响应): ").strip()

    if len(sys.argv) > 2:
        description = sys.argv[2]
    else:
        description = input("📄 变更描述 (简要说明): ").strip()

    if not title or not description:
        print("❌ 标题和描述不能为空")
        return

    # 生成更新条目
    entry = generate_update_entry(title, description, changes)

    print("\n" + "="*50)
    print("将要添加的内容:")
    print("="*50)
    print(entry)
    print("="*50)

    # 确认
    confirm = input("\n❓ 确认添加到 CLAUDE.md? (y/n): ").strip().lower()

    if confirm == 'y':
        if insert_update_to_claude_md(entry):
            print("✅ 已成功更新 CLAUDE.md")
        else:
            print("❌ 更新失败")
    else:
        print("❌ 已取消")
        print(f"💡 你可以手动运行: python tools/claude_doc_updater.py '{title}' '{description}'")

if __name__ == "__main__":
    main()
