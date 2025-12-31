#!/usr/bin/env python3
"""
检查知识库中的已完成需求数据
"""
import asyncio
from sqlalchemy import select
from backend.app.core.database import get_db
from backend.app.models.knowledge_base import KnowledgeBase
from backend.app.models.conversation import Conversation
import json


async def main():
    print("=" * 60)
    print("检查知识库中的已完成需求")
    print("=" * 60)
    print()

    async for db in get_db():
        # 获取所有知识库
        result = await db.execute(select(KnowledgeBase))
        kbs = result.scalars().all()

        print(f"找到 {len(kbs)} 个知识库\n")

        for kb in kbs:
            print(f"项目 ID: {kb.project_id}")
            print(f"状态: {kb.status}")
            print(f"创建时间: {kb.created_at}")
            print()

            # 检查 structured_data
            data = kb.structured_data or {}
            completed_reqs = data.get("completed_requirements", [])

            print(f"已完成需求数量: {len(completed_reqs)}")
            print()

            if completed_reqs:
                for idx, req in enumerate(completed_reqs, 1):
                    print(f"需求 {idx}:")
                    print(f"  标题: {req.get('title', 'N/A')}")
                    print(f"  描述: {req.get('description', 'N/A')}")
                    print(f"  对话ID: {req.get('conversation_id', 'N/A')}")
                    print(f"  关键要点数: {len(req.get('key_points', []))}")
                    print(f"  归档时间: {req.get('archived_at', 'N/A')}")
                    print()
            else:
                print("  没有已完成需求")
                print()

            # 检查对应的已完成对话
            conv_result = await db.execute(
                select(Conversation)
                .where(Conversation.project_id == kb.project_id)
                .where(Conversation.status == "completed")
            )
            completed_convs = conv_result.scalars().all()

            print(f"已完成对话数量: {len(completed_convs)}")
            for conv in completed_convs:
                print(f"  - {conv.title} (ID: {conv.id})")
                if conv.requirement_summary:
                    print(f"    有需求摘要: {conv.requirement_summary.get('title', 'N/A')}")
                else:
                    print(f"    没有需求摘要")
            print()
            print("-" * 60)
            print()

        break

    print("检查完成！")


if __name__ == "__main__":
    asyncio.run(main())
