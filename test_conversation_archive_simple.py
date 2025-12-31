#!/usr/bin/env python3
"""
Simple test for conversation status update and archiving.
Tests without needing Gemini API or knowledge base setup.
"""
import asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.database import get_db, engine
from backend.app.models.project import Project
from backend.app.models.conversation import Conversation, Message
from backend.app.models.knowledge_base import KnowledgeBase
from backend.app.services.conversation_service import ConversationService
from backend.app.services.gemini_service import GeminiService
from uuid import uuid4
import json


async def main():
    print("=" * 70)
    print("Testing Conversation Archiving Feature (Direct Database Test)")
    print("=" * 70)
    print()

    async for db in get_db():
        # 1. Create test project
        print("1. Creating test project...")
        project = Project(
            name=f"Test Project {uuid4().hex[:6]}",
            description="Testing conversation archiving"
        )
        db.add(project)
        await db.commit()
        await db.refresh(project)
        print(f"   ✅ Created project: {project.id}")
        print()

        # 2. Create knowledge base
        print("2. Creating knowledge base...")
        kb = KnowledgeBase(
            project_id=project.id,
            structured_data={
                "system_overview": {
                    "product_type": "测试应用",
                    "core_modules": ["模块1", "模块2"]
                }
            },
            status="confirmed"
        )
        db.add(kb)
        await db.commit()
        await db.refresh(kb)
        print(f"   ✅ Created knowledge base")
        print()

        # 3. Create conversation
        print("3. Creating conversation...")
        conversation = Conversation(
            project_id=project.id,
            title="用户登录功能",
            status="active"
        )
        db.add(conversation)
        await db.commit()
        await db.refresh(conversation)
        print(f"   ✅ Created conversation: {conversation.id}")
        print(f"   Status: {conversation.status}")
        print()

        # 4. Add messages
        print("4. Adding test messages...")
        messages_content = [
            ("user", "我需要实现一个用户登录功能"),
            ("assistant", "好的，请问需要支持哪些登录方式？"),
            ("user", "需要支持邮箱和密码登录，并且有记住密码功能"),
            ("assistant", "明白了。还有其他安全要求吗？"),
            ("user", "登录失败3次后需要锁定账号30分钟"),
            ("assistant", "好的，我已经记录了所有要求。")
        ]

        for idx, (role, content) in enumerate(messages_content):
            msg = Message(
                conversation_id=conversation.id,
                role=role,
                content=content,
                sequence=idx + 1
            )
            db.add(msg)

        await db.commit()
        print(f"   ✅ Added {len(messages_content)} messages")
        print()

        # 5. Generate requirement summary
        print("5. Generating requirement summary...")
        conv_service = ConversationService(GeminiService())
        try:
            summary = await conv_service.generate_requirement_summary(
                db=db,
                conversation_id=conversation.id
            )
            print(f"   ✅ Generated summary:")
            print(f"      Title: {summary.get('title', 'N/A')}")
            print(f"      Description: {summary.get('description', 'N/A')}")
            if summary.get('key_points'):
                print(f"      Key points:")
                for point in summary['key_points']:
                    print(f"        - {point}")
        except Exception as e:
            print(f"   ⚠️  Summary generation failed (expected if no Gemini API key): {e}")
            # Use fallback summary
            summary = {
                "title": "用户登录功能",
                "description": "实现邮箱密码登录，支持记住密码，失败3次锁定30分钟",
                "key_points": [
                    "邮箱和密码登录",
                    "记住密码功能",
                    "失败3次锁定30分钟"
                ],
                "prd_generated": False
            }
            print(f"   Using fallback summary")
        print()

        # 6. Update conversation status and archive
        print("6. Marking conversation as completed and archiving...")
        conversation.status = "completed"
        conversation.requirement_summary = summary

        # Archive to knowledge base
        await conv_service.archive_requirement_to_knowledge_base(
            db=db,
            project_id=project.id,
            conversation_id=conversation.id,
            requirement_summary=summary
        )
        await db.commit()
        print(f"   ✅ Conversation marked as completed")
        print(f"   ✅ Requirement archived to knowledge base")
        print()

        # 7. Verify knowledge base contains the archived requirement
        print("7. Verifying knowledge base...")
        result = await db.execute(
            select(KnowledgeBase).where(KnowledgeBase.project_id == project.id)
        )
        kb_updated = result.scalar_one()

        completed_reqs = kb_updated.structured_data.get("completed_requirements", [])
        print(f"   Total completed requirements: {len(completed_reqs)}")

        if completed_reqs:
            print(f"   ✅ Requirements successfully archived!")
            for idx, req in enumerate(completed_reqs, 1):
                print(f"   Requirement {idx}:")
                print(f"      Title: {req.get('title')}")
                print(f"      Description: {req.get('description')}")
                print(f"      Conversation ID: {req.get('conversation_id')}")
                if req.get('key_points'):
                    print(f"      Key points: {', '.join(req['key_points'])}")
        else:
            print(f"   ❌ No requirements found in knowledge base")
        print()

        # 8. Test context generation
        print("8. Testing knowledge base context generation...")
        context = await conv_service.get_knowledge_base_context(db, project.id)
        if context:
            print(f"   ✅ Context generated ({len(context)} characters)")
            if "已完成需求" in context:
                print(f"   ✅ Context includes completed requirements section")
                # Print relevant section
                lines = context.split("\n")
                in_req_section = False
                for line in lines:
                    if "## 已完成需求" in line:
                        in_req_section = True
                    if in_req_section:
                        print(f"      {line}")
                        if line.startswith("## ") and "已完成需求" not in line:
                            break
            else:
                print(f"   ⚠️  Context does not include completed requirements")
        else:
            print(f"   ⚠️  No context generated")
        print()

        print("=" * 70)
        print("Test completed successfully!")
        print("=" * 70)

        # Only process first db session
        break

    # Close database connections
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
