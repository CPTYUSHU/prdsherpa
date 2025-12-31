#!/usr/bin/env python3
"""
初始化知识库演进结构
"""
import asyncio
from sqlalchemy import select
from sqlalchemy.orm.attributes import flag_modified
from backend.app.core.database import get_db
from backend.app.models.knowledge_base import KnowledgeBase
from backend.app.models.conversation import Conversation
from backend.app.services.gemini_service import GeminiService
from backend.app.services.knowledge_evolution_service import KnowledgeEvolutionService


async def main():
    print("=" * 60)
    print("初始化知识库演进结构")
    print("=" * 60)
    print()

    gemini_service = GeminiService()
    evolution_service = KnowledgeEvolutionService(gemini_service)

    async for db in get_db():
        # 获取所有知识库
        result = await db.execute(select(KnowledgeBase))
        kbs = result.scalars().all()

        for kb in kbs:
            print(f"处理知识库: {kb.project_id}")

            data = kb.structured_data or {}

            # 初始化新的结构
            if "project_overview" not in data:
                data["project_overview"] = {
                    "description": data.get("system_overview", {}).get("description", ""),
                    "product_type": data.get("system_overview", {}).get("product_type", ""),
                    "current_status": {
                        "total_requirements": 0,
                        "completed_features": [],
                        "feature_count_by_module": {}
                    }
                }
                print("  ✓ 初始化 project_overview")

            if "feature_modules" not in data:
                data["feature_modules"] = []
                print("  ✓ 初始化 feature_modules")

            if "tech_architecture" not in data:
                data["tech_architecture"] = {
                    "conventions": data.get("tech_conventions", {}),
                    "patterns": []
                }
                print("  ✓ 初始化 tech_architecture")

            # 处理已归档的需求
            completed_reqs = data.get("completed_requirements", [])
            print(f"  发现 {len(completed_reqs)} 个已归档需求")

            for req in completed_reqs:
                print(f"    处理需求: {req.get('title')}")
                conversation_id = req.get("conversation_id")

                if conversation_id:
                    # 运行知识库演进
                    try:
                        await evolution_service.evolve_knowledge_base(
                            db=db,
                            project_id=kb.project_id,
                            completed_conversation_id=conversation_id,
                            requirement_summary=req
                        )
                        print(f"      ✅ 知识库演进完成")
                    except Exception as e:
                        print(f"      ⚠️  演进失败: {e}")
                        import traceback
                        traceback.print_exc()

            # 保存更新
            kb.structured_data = data
            flag_modified(kb, "structured_data")
            await db.commit()
            print("  💾 保存完成")
            print()

        print("所有知识库初始化完成！")
        break


if __name__ == "__main__":
    asyncio.run(main())
