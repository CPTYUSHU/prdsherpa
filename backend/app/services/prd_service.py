"""
PRD Service - Real-time PRD generation and management.
"""
import logging
from typing import Dict, Any, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm.attributes import flag_modified
from backend.app.models.conversation import Conversation, Message
from backend.app.services.gemini_service import GeminiService
from datetime import datetime

logger = logging.getLogger(__name__)


class PRDService:
    """Service for PRD draft management and generation."""

    # PRD 章节定义
    PRD_SECTIONS = {
        "background": "项目背景",
        "objectives": "产品目标",
        "user_stories": "用户故事",
        "functional_requirements": "功能需求",
        "non_functional": "非功能需求",
        "tech_solution": "技术方案",
        "risks": "风险与对策"
    }

    def __init__(self, gemini_service: GeminiService):
        self.gemini_service = gemini_service

    async def generate_prd_outline(
        self,
        db: AsyncSession,
        conversation_id: UUID,
        project_id: UUID
    ) -> Dict[str, Any]:
        """
        Generate PRD outline based on current conversation.

        Returns:
            PRD draft with section outlines
        """
        # Get conversation messages
        result = await db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at)
        )
        messages = result.scalars().all()

        if not messages:
            return self._create_empty_draft()

        # Build conversation context
        conversation_text = "\n".join([
            f"{'用户' if msg.role == 'user' else 'AI'}: {msg.content}"
            for msg in messages
        ])

        # Get knowledge base context
        from backend.app.models.knowledge_base import KnowledgeBase
        kb_result = await db.execute(
            select(KnowledgeBase).where(KnowledgeBase.project_id == project_id)
        )
        kb = kb_result.scalar_one_or_none()
        kb_context = ""
        if kb and kb.structured_data:
            kb_context = f"""
项目知识库信息：
- 产品类型：{kb.structured_data.get('system_overview', {}).get('product_type', '未知')}
- 项目描述：{kb.structured_data.get('system_overview', {}).get('description', '无')}
- 技术栈：{kb.structured_data.get('tech_conventions', {}).get('api_style', '未知')}
"""

        # Generate outline using AI
        prompt = f"""基于以下对话内容，生成 PRD 各章节的大纲要点。

{kb_context}

对话内容：
{conversation_text}

请为以下每个章节生成简要大纲（3-5个要点）：
1. 项目背景
2. 产品目标
3. 用户故事
4. 功能需求
5. 非功能需求
6. 技术方案
7. 风险与对策

以 JSON 格式返回，格式如下：
{{
  "background": ["要点1", "要点2", "要点3"],
  "objectives": ["要点1", "要点2"],
  "user_stories": ["作为...，我希望...，以便..."],
  "functional_requirements": ["需求1", "需求2"],
  "non_functional": ["性能要求", "安全要求"],
  "tech_solution": ["技术选型", "架构设计"],
  "risks": ["风险1及对策", "风险2及对策"]
}}

只返回 JSON，不要其他内容。"""

        try:
            response = await self.gemini_service.generate_text(prompt)

            # Parse JSON
            import json
            import re
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
            if json_match:
                response = json_match.group(1)

            outlines = json.loads(response.strip())

            # Build draft structure
            draft = {
                "version": 1,
                "last_updated": datetime.utcnow().isoformat(),
                "sections": {}
            }

            for section_key, section_name in self.PRD_SECTIONS.items():
                outline_points = outlines.get(section_key, [])
                content = f"## {section_name}\n\n"
                content += "\n".join([f"- {point}" for point in outline_points])

                draft["sections"][section_key] = {
                    "title": section_name,
                    "content": content,
                    "status": "outline",  # outline, draft, completed
                    "updated_at": datetime.utcnow().isoformat()
                }

            logger.info(f"Generated PRD outline for conversation {conversation_id}")
            return draft

        except Exception as e:
            logger.error(f"Failed to generate PRD outline: {e}")
            return self._create_empty_draft()

    async def update_section(
        self,
        db: AsyncSession,
        conversation_id: UUID,
        section_key: str,
        content: str
    ) -> Dict[str, Any]:
        """
        Update a specific PRD section.

        Args:
            db: Database session
            conversation_id: Conversation ID
            section_key: Section key (e.g., "background")
            content: New content for the section

        Returns:
            Updated PRD draft
        """
        result = await db.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        conversation = result.scalar_one_or_none()

        if not conversation:
            raise ValueError(f"Conversation {conversation_id} not found")

        draft = conversation.prd_draft or self._create_empty_draft()

        if section_key not in self.PRD_SECTIONS:
            raise ValueError(f"Invalid section key: {section_key}")

        # Update section
        if section_key not in draft["sections"]:
            draft["sections"][section_key] = {
                "title": self.PRD_SECTIONS[section_key],
                "content": "",
                "status": "draft",
                "updated_at": datetime.utcnow().isoformat()
            }

        draft["sections"][section_key]["content"] = content
        draft["sections"][section_key]["updated_at"] = datetime.utcnow().isoformat()
        draft["sections"][section_key]["status"] = "draft" if content.strip() else "outline"
        draft["last_updated"] = datetime.utcnow().isoformat()
        draft["version"] = draft.get("version", 1) + 1

        # Save to database
        conversation.prd_draft = draft
        flag_modified(conversation, "prd_draft")
        await db.commit()

        logger.info(f"Updated PRD section '{section_key}' for conversation {conversation_id}")
        return draft

    async def regenerate_section(
        self,
        db: AsyncSession,
        conversation_id: UUID,
        project_id: UUID,
        section_key: str
    ) -> Dict[str, Any]:
        """
        Regenerate a specific section using AI.

        Args:
            db: Database session
            conversation_id: Conversation ID
            project_id: Project ID
            section_key: Section to regenerate

        Returns:
            Updated PRD draft
        """
        if section_key not in self.PRD_SECTIONS:
            raise ValueError(f"Invalid section key: {section_key}")

        # Get conversation messages
        result = await db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at)
        )
        messages = result.scalars().all()

        conversation_text = "\n".join([
            f"{'用户' if msg.role == 'user' else 'AI'}: {msg.content}"
            for msg in messages[-10:]  # Last 10 messages
        ])

        # Get knowledge base
        from backend.app.models.knowledge_base import KnowledgeBase
        kb_result = await db.execute(
            select(KnowledgeBase).where(KnowledgeBase.project_id == project_id)
        )
        kb = kb_result.scalar_one_or_none()
        kb_context = self._build_kb_context(kb)

        # Generate section content
        section_name = self.PRD_SECTIONS[section_key]
        prompt = self._build_section_prompt(section_key, section_name, conversation_text, kb_context)

        try:
            content = await self.gemini_service.generate_text(prompt)

            # Update section
            return await self.update_section(db, conversation_id, section_key, content)

        except Exception as e:
            logger.error(f"Failed to regenerate section '{section_key}': {e}")
            raise

    def _create_empty_draft(self) -> Dict[str, Any]:
        """Create an empty PRD draft structure."""
        return {
            "version": 1,
            "last_updated": datetime.utcnow().isoformat(),
            "sections": {
                section_key: {
                    "title": section_name,
                    "content": "",
                    "status": "empty",
                    "updated_at": datetime.utcnow().isoformat()
                }
                for section_key, section_name in self.PRD_SECTIONS.items()
            }
        }

    def _build_kb_context(self, kb) -> str:
        """Build knowledge base context string."""
        if not kb or not kb.structured_data:
            return ""

        data = kb.structured_data
        context = "项目背景知识：\n"

        if "system_overview" in data:
            so = data["system_overview"]
            context += f"- 产品类型：{so.get('product_type', '未知')}\n"
            context += f"- 产品描述：{so.get('description', '无')}\n"

        if "tech_conventions" in data:
            tc = data["tech_conventions"]
            context += f"- API 风格：{tc.get('api_style', '未知')}\n"
            context += f"- 命名风格：{tc.get('naming_style', '未知')}\n"

        return context

    def _build_section_prompt(self, section_key: str, section_name: str, conversation: str, kb_context: str) -> str:
        """Build prompt for section generation."""
        prompts = {
            "background": f"""基于以下对话和项目信息，编写 PRD 的"项目背景"章节。

{kb_context}

对话内容：
{conversation}

请编写详细的项目背景，包括：
1. 业务背景和痛点
2. 为什么要做这个需求
3. 目标用户群体

使用 Markdown 格式，以 "## 项目背景" 开头。""",

            "objectives": f"""基于对话内容，编写 PRD 的"产品目标"章节。

{kb_context}

对话内容：
{conversation}

请列出：
1. 核心目标（2-3个）
2. 预期效果和指标
3. 成功标准

使用 Markdown 格式。""",

            "user_stories": f"""基于对话内容，编写"用户故事"章节。

{kb_context}

对话内容：
{conversation}

请按照 "作为...，我希望...，以便..." 的格式编写 3-5 个用户故事。
使用 Markdown 格式。""",

            "functional_requirements": f"""基于对话内容，编写"功能需求"章节。

{kb_context}

对话内容：
{conversation}

请详细列出所有功能需求，按模块组织，包括：
- 功能描述
- 交互流程
- 边界条件

使用 Markdown 格式。""",

            "non_functional": f"""编写"非功能需求"章节。

{kb_context}

对话内容：
{conversation}

包括：
- 性能要求
- 安全要求
- 可用性要求
- 兼容性要求

使用 Markdown 格式。""",

            "tech_solution": f"""编写"技术方案"章节。

{kb_context}

对话内容：
{conversation}

包括：
- 技术架构
- 关键技术选型
- 数据库设计要点
- 接口设计

使用 Markdown 格式。""",

            "risks": f"""编写"风险与对策"章节。

{kb_context}

对话内容：
{conversation}

列出可能的风险及应对措施。
使用 Markdown 格式。"""
        }

        return prompts.get(section_key, f"编写 PRD 的 '{section_name}' 章节。\n\n{conversation}")
