"""
Conversation service for handling AI-powered PRD writing dialogue.
"""
import logging
from typing import List, Dict, Any, Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from backend.app.models.conversation import Conversation, Message
from backend.app.models.knowledge_base import KnowledgeBase
from backend.app.services.gemini_service import GeminiService

logger = logging.getLogger(__name__)


class ConversationService:
    """Service for managing conversations and AI dialogue."""
    
    def __init__(self, gemini_service: GeminiService):
        self.gemini_service = gemini_service
    
    async def get_conversation_context(
        self,
        db: AsyncSession,
        conversation_id: UUID,
        max_messages: int = 50
    ) -> List[Dict[str, str]]:
        """
        Get recent conversation history for context.

        Enhanced from 10 to 50 messages for better context retention.
        The AI model can now reference much longer conversation histories,
        leading to more coherent and context-aware responses.

        Args:
            db: Database session
            conversation_id: Conversation ID
            max_messages: Maximum number of recent messages to include (default: 50)

        Returns:
            List of message dictionaries with role and content
        """
        result = await db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(max_messages)
        )
        messages = result.scalars().all()
        
        # Reverse to get chronological order
        return [
            {"role": msg.role, "content": msg.content}
            for msg in reversed(messages)
        ]
    
    async def get_knowledge_base_context(
        self,
        db: AsyncSession,
        project_id: UUID
    ) -> Optional[str]:
        """
        Get project knowledge base as context for AI.
        
        Args:
            db: Database session
            project_id: Project ID
            
        Returns:
            Formatted knowledge base context string
        """
        result = await db.execute(
            select(KnowledgeBase)
            .where(KnowledgeBase.project_id == project_id)
            .where(KnowledgeBase.status == "confirmed")
        )
        kb = result.scalar_one_or_none()
        
        if not kb:
            return None
        
        # Format knowledge base into context
        data = kb.structured_data
        context_parts = ["# 项目知识库\n"]
        
        # System overview
        if data.get("system_overview"):
            overview = data["system_overview"]
            context_parts.append("## 系统概览")
            if overview.get("product_type"):
                context_parts.append(f"产品类型：{overview['product_type']}")
            if overview.get("core_modules"):
                context_parts.append(f"核心模块：{', '.join(overview['core_modules'])}")
            if overview.get("description"):
                context_parts.append(f"描述：{overview['description']}")
            context_parts.append("")
        
        # UI standards
        if data.get("ui_standards"):
            ui = data["ui_standards"]
            context_parts.append("## UI规范")
            if ui.get("primary_colors"):
                context_parts.append(f"主色调：{', '.join(ui['primary_colors'])}")
            if ui.get("component_library"):
                context_parts.append(f"组件库：{ui['component_library']}")
            if ui.get("layout_features"):
                context_parts.append(f"布局特征：{', '.join(ui['layout_features'])}")
            context_parts.append("")
        
        # Tech conventions
        if data.get("tech_conventions"):
            tech = data["tech_conventions"]
            context_parts.append("## 技术约定")
            if tech.get("naming_style"):
                context_parts.append(f"命名风格：{tech['naming_style']}")
            if tech.get("api_style"):
                context_parts.append(f"API风格：{tech['api_style']}")
            if tech.get("known_fields"):
                context_parts.append("已知字段：")
                for field in tech["known_fields"][:5]:  # Limit to 5 fields
                    context_parts.append(f"  - {field.get('name')}: {field.get('type')} - {field.get('usage')}")
            context_parts.append("")

        # Completed requirements (history)
        if data.get("completed_requirements"):
            requirements = data["completed_requirements"]
            context_parts.append("## 已完成需求")
            context_parts.append("以下是项目中已经确认和完成的需求，请在设计新需求时参考这些内容，避免冲突或重复：")
            context_parts.append("")
            for idx, req in enumerate(requirements[-5:], 1):  # Show last 5 requirements
                context_parts.append(f"### {idx}. {req.get('title', '未命名需求')}")
                context_parts.append(f"**描述**: {req.get('description', '暂无描述')}")
                if req.get('key_points'):
                    context_parts.append("**关键要点**:")
                    for point in req['key_points']:
                        context_parts.append(f"  - {point}")
                context_parts.append("")

        return "\n".join(context_parts)
    
    async def generate_ai_response(
        self,
        db: AsyncSession,
        project_id: UUID,
        conversation_id: UUID,
        user_message: str,
        image_paths: Optional[List[str]] = None
    ) -> str:
        """
        Generate AI response based on user message and context.
        
        Args:
            db: Database session
            project_id: Project ID
            conversation_id: Conversation ID
            user_message: User's message
            
        Returns:
            AI-generated response
        """
        # Get knowledge base context
        kb_context = await self.get_knowledge_base_context(db, project_id)
        
        # Get conversation history
        history = await self.get_conversation_context(db, conversation_id)
        
        # Build system prompt
        system_prompt = """你是一个专业的产品需求文档（PRD）写作助手。你的任务是：
1. 理解用户的需求描述
2. 基于项目知识库提出必要的澄清问题
3. 帮助用户完善需求细节
4. 最终生成结构化的PRD文档

请遵循以下原则：
- 提问要具体、有针对性
- 参考项目知识库中的UI规范和技术约定
- 使用Markdown格式输出
- 保持专业但友好的语气
"""
        
        if kb_context:
            system_prompt += f"\n\n{kb_context}"
        
        # Prepare messages for Gemini
        messages = [{"role": "user", "content": system_prompt}]
        
        # Add conversation history
        for msg in history:
            messages.append(msg)
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        # Generate response using Gemini with optional images
        try:
            response = await self.gemini_service.chat(
                messages=messages,
                image_paths=image_paths
            )
            logger.info(f"Generated AI response for conversation {conversation_id}")
            return response
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            return "抱歉，我遇到了一些问题。请稍后再试。"

    async def generate_ai_response_stream(
        self,
        db: AsyncSession,
        project_id: UUID,
        conversation_id: UUID,
        user_message: str,
        image_paths: Optional[List[str]] = None
    ):
        """
        Generate AI response with streaming based on user message and context.

        Args:
            db: Database session
            project_id: Project ID
            conversation_id: Conversation ID
            user_message: User's message
            image_paths: Optional image file paths

        Yields:
            Text chunks as they are generated
        """
        # Get knowledge base context
        kb_context = await self.get_knowledge_base_context(db, project_id)

        # Get conversation history
        history = await self.get_conversation_context(db, conversation_id)

        # Build system prompt
        system_prompt = """你是一个专业的产品需求文档（PRD）写作助手。你的任务是：
1. 理解用户的需求描述
2. 基于项目知识库提出必要的澄清问题
3. 帮助用户完善需求细节
4. 最终生成结构化的PRD文档

请遵循以下原则：
- 提问要具体、有针对性
- 参考项目知识库中的UI规范和技术约定
- 使用Markdown格式输出
- 保持专业但友好的语气
"""

        if kb_context:
            system_prompt += f"\n\n{kb_context}"

        # Prepare messages for Gemini
        messages = [{"role": "user", "content": system_prompt}]

        # Add conversation history
        for msg in history:
            messages.append(msg)

        # Add current user message
        messages.append({"role": "user", "content": user_message})

        # Generate response using Gemini with streaming
        try:
            async for chunk in self.gemini_service.chat_stream(
                messages=messages,
                image_paths=image_paths
            ):
                yield chunk
            logger.info(f"Generated AI response stream for conversation {conversation_id}")
        except Exception as e:
            logger.error(f"Error generating AI response stream: {e}")
            yield "抱歉，我遇到了一些问题。请稍后再试。"

    async def generate_conversation_title(
        self,
        first_user_message: str
    ) -> str:
        """
        Generate a conversation title based on the first user message.

        Args:
            first_user_message: First message from user

        Returns:
            Generated title
        """
        # Use first 50 characters or generate with AI
        if len(first_user_message) <= 50:
            return first_user_message

        # Try to generate a concise title with AI
        try:
            prompt = f"""请为以下需求描述生成一个简短的标题（不超过20个字）：

{first_user_message}

只返回标题，不要其他内容。"""

            title = await self.gemini_service.generate_text(prompt)
            # Clean up the title
            title = title.strip().strip('"').strip("'")
            if len(title) > 50:
                title = title[:50] + "..."
            return title
        except Exception as e:
            logger.error(f"Error generating title: {e}")
            # Fallback to truncated message
            return first_user_message[:47] + "..."

    async def generate_requirement_summary(
        self,
        db: AsyncSession,
        conversation_id: UUID
    ) -> Dict[str, Any]:
        """
        Generate a requirement summary from conversation history.

        Args:
            db: Database session
            conversation_id: Conversation ID

        Returns:
            Requirement summary dictionary
        """
        # Get all messages in the conversation
        result = await db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at)
        )
        messages = result.scalars().all()

        if not messages:
            return {
                "title": "未命名需求",
                "description": "暂无描述",
                "key_points": [],
                "prd_generated": False
            }

        # Build conversation text
        conversation_text = "\n\n".join([
            f"{'用户' if msg.role == 'user' else 'AI助手'}: {msg.content}"
            for msg in messages
        ])

        # Generate summary with AI
        try:
            prompt = f"""请分析以下产品需求对话，生成一个结构化的需求摘要。

对话内容：
{conversation_text}

请以JSON格式返回，包含以下字段：
{{
  "title": "需求标题（简短描述，10-20字）",
  "description": "需求描述（1-2句话概括核心需求）",
  "key_points": ["关键要点1", "关键要点2", "关键要点3"],
  "prd_generated": false
}}

只返回JSON，不要其他内容。"""

            summary_text = await self.gemini_service.generate_text(prompt)

            # Parse JSON from response (handle markdown code blocks)
            import json
            import re

            # Try to extract JSON from markdown code block
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', summary_text, re.DOTALL)
            if json_match:
                summary_text = json_match.group(1)

            summary = json.loads(summary_text.strip())
            logger.info(f"Generated requirement summary for conversation {conversation_id}")
            return summary

        except Exception as e:
            logger.error(f"Error generating requirement summary: {e}")
            # Fallback to basic summary
            return {
                "title": messages[0].content[:30] if messages else "未命名需求",
                "description": messages[0].content[:100] if messages else "暂无描述",
                "key_points": [],
                "prd_generated": False
            }

    async def archive_requirement_to_knowledge_base(
        self,
        db: AsyncSession,
        project_id: UUID,
        conversation_id: UUID,
        requirement_summary: Dict[str, Any]
    ) -> None:
        """
        Archive completed requirement to project knowledge base.

        Args:
            db: Database session
            project_id: Project ID
            conversation_id: Conversation ID
            requirement_summary: Requirement summary to archive
        """
        # Get knowledge base
        result = await db.execute(
            select(KnowledgeBase)
            .where(KnowledgeBase.project_id == project_id)
        )
        kb = result.scalar_one_or_none()

        if not kb:
            logger.warning(f"No knowledge base found for project {project_id}, skipping requirement archive")
            return

        # Get or initialize completed_requirements section
        data = kb.structured_data or {}
        if "completed_requirements" not in data:
            data["completed_requirements"] = []

        # Add requirement with conversation reference
        archived_requirement = {
            "conversation_id": str(conversation_id),
            "title": requirement_summary.get("title", "未命名需求"),
            "description": requirement_summary.get("description", ""),
            "key_points": requirement_summary.get("key_points", []),
            "prd_generated": requirement_summary.get("prd_generated", False),
            "archived_at": datetime.utcnow().isoformat()
        }

        data["completed_requirements"].append(archived_requirement)

        # Update knowledge base (don't commit here, let the caller handle it)
        kb.structured_data = data
        # Mark as modified to ensure SQLAlchemy tracks the change
        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(kb, "structured_data")

        logger.info(f"Archived requirement from conversation {conversation_id} to knowledge base")

