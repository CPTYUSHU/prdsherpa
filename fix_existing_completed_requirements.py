#!/usr/bin/env python3
"""
修复已完成但未归档的需求
"""
import asyncio
from sqlalchemy import select
from sqlalchemy.orm.attributes import flag_modified
from backend.app.core.database import get_db
from backend.app.models.knowledge_base import KnowledgeBase
from backend.app.models.conversation import Conversation
from datetime import datetime


async def main():
    print("=" * 60)
    print("修复已完成但未归档的需求")
    print("=" * 60)
    print()

    async for db in get_db():
        # 找到所有已完成的对话
        result = await db.execute(
            select(Conversation)
            .where(Conversation.status == "completed")
        )
        completed_convs = result.scalars().all()

        print(f"找到 {len(completed_convs)} 个已完成的对话")
        print()

        for conv in completed_convs:
            print(f"处理对话: {conv.title} (ID: {conv.id})")

            if not conv.requirement_summary:
                print(f"  ⚠️  没有需求摘要，跳过")
                continue

            # 获取项目的知识库
            kb_result = await db.execute(
                select(KnowledgeBase)
                .where(KnowledgeBase.project_id == conv.project_id)
            )
            kb = kb_result.scalar_one_or_none()

            if not kb:
                print(f"  ⚠️  没有找到知识库，跳过")
                continue

            # 检查是否已经归档
            data = kb.structured_data or {}
            completed_reqs = data.get("completed_requirements", [])

            already_archived = any(
                req.get("conversation_id") == str(conv.id)
                for req in completed_reqs
            )

            if already_archived:
                print(f"  ✓ 已归档")
                continue

            # 归档需求
            if "completed_requirements" not in data:
                data["completed_requirements"] = []

            archived_requirement = {
                "conversation_id": str(conv.id),
                "title": conv.requirement_summary.get("title", "未命名需求"),
                "description": conv.requirement_summary.get("description", ""),
                "key_points": conv.requirement_summary.get("key_points", []),
                "prd_generated": conv.requirement_summary.get("prd_generated", False),
                "archived_at": datetime.utcnow().isoformat()
            }

            data["completed_requirements"].append(archived_requirement)
            kb.structured_data = data
            flag_modified(kb, "structured_data")

            print(f"  ✅ 已归档: {archived_requirement['title']}")

        await db.commit()
        print()
        print("修复完成！")
        break


if __name__ == "__main__":
    asyncio.run(main())
