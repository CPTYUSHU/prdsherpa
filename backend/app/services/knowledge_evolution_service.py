"""
Knowledge Evolution Service - Intelligently update knowledge base as requirements are completed.
"""
import logging
from typing import Dict, Any, List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm.attributes import flag_modified
from backend.app.models.knowledge_base import KnowledgeBase
from backend.app.models.conversation import Conversation, Message
from backend.app.services.gemini_service import GeminiService
from datetime import datetime
import json
import re

logger = logging.getLogger(__name__)


class KnowledgeEvolutionService:
    """Service for evolving knowledge base as project grows."""

    def __init__(self, gemini_service: GeminiService):
        self.gemini_service = gemini_service

    async def evolve_knowledge_base(
        self,
        db: AsyncSession,
        project_id: UUID,
        completed_conversation_id: UUID,
        requirement_summary: Dict[str, Any]
    ) -> None:
        """
        Intelligently update knowledge base when a requirement is completed.

        This method:
        1. Analyzes the completed requirement
        2. Determines which module it belongs to
        3. Updates feature modules
        4. Updates tech architecture if needed
        5. Updates UI standards if needed
        6. Updates project overview statistics

        Args:
            db: Database session
            project_id: Project ID
            completed_conversation_id: ID of completed conversation
            requirement_summary: Summary of the requirement
        """
        # Get knowledge base
        result = await db.execute(
            select(KnowledgeBase).where(KnowledgeBase.project_id == project_id)
        )
        kb = result.scalar_one_or_none()

        if not kb:
            logger.warning(f"No knowledge base found for project {project_id}")
            return

        # Get conversation messages for detailed analysis
        msg_result = await db.execute(
            select(Message)
            .where(Message.conversation_id == completed_conversation_id)
            .order_by(Message.created_at)
        )
        messages = msg_result.scalars().all()

        # Build conversation context
        conversation_text = "\n".join([
            f"{'用户' if msg.role == 'user' else 'AI'}: {msg.content}"
            for msg in messages
        ])

        # Get current knowledge base data
        data = kb.structured_data or {}

        # Initialize structure if needed
        self._initialize_kb_structure(data, requirement_summary)

        # Use AI to analyze and update knowledge base
        await self._analyze_and_update(data, requirement_summary, conversation_text)

        # Update knowledge base
        kb.structured_data = data
        flag_modified(kb, "structured_data")
        await db.commit()

        logger.info(f"Evolved knowledge base for project {project_id}")

    def _initialize_kb_structure(self, data: Dict[str, Any], req_summary: Dict[str, Any]) -> None:
        """Initialize knowledge base structure if not exists."""

        # Project overview
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

        # Feature modules
        if "feature_modules" not in data:
            data["feature_modules"] = []

        # Tech architecture
        if "tech_architecture" not in data:
            data["tech_architecture"] = {
                "conventions": data.get("tech_conventions", {}),
                "patterns": []
            }

        # UI/UX standards
        if "ui_ux_standards" not in data:
            data["ui_ux_standards"] = data.get("ui_standards", {})

        # Completed requirements
        if "completed_requirements" not in data:
            data["completed_requirements"] = []

    async def _analyze_and_update(
        self,
        data: Dict[str, Any],
        req_summary: Dict[str, Any],
        conversation_text: str
    ) -> None:
        """Use AI to analyze requirement and update knowledge base."""

        try:
            # Build analysis prompt
            current_modules = [m.get("module_name", "") for m in data.get("feature_modules", [])]

            prompt = f"""分析以下已完成的需求，判断它如何影响项目知识库。

需求标题：{req_summary.get('title', '')}
需求描述：{req_summary.get('description', '')}
关键要点：{', '.join(req_summary.get('key_points', []))}

当前项目的功能模块：{', '.join(current_modules) if current_modules else '暂无'}

请以 JSON 格式返回分析结果：
{{
  "module_assignment": {{
    "is_new_module": true/false,
    "module_name": "功能模块名称",
    "module_description": "模块简介（如果是新模块）"
  }},
  "tech_insights": {{
    "has_tech_update": true/false,
    "patterns": ["技术模式1", "技术模式2"],
    "conventions": ["约定1", "约定2"]
  }},
  "ui_insights": {{
    "has_ui_update": true/false,
    "components": ["组件1", "组件2"],
    "patterns": ["UI模式1"]
  }}
}}

只返回 JSON，不要其他内容。"""

            response = await self.gemini_service.generate_text(prompt)

            # Parse JSON response
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
            if json_match:
                response = json_match.group(1)

            analysis = json.loads(response.strip())

            # Update based on analysis
            self._update_feature_modules(data, req_summary, analysis.get("module_assignment", {}))
            self._update_tech_architecture(data, analysis.get("tech_insights", {}))
            self._update_ui_standards(data, analysis.get("ui_insights", {}))
            self._update_project_overview(data)

        except Exception as e:
            logger.error(f"Failed to analyze requirement: {e}")
            # Fallback: add to "其他功能" module
            self._update_feature_modules(data, req_summary, {
                "is_new_module": False,
                "module_name": "其他功能"
            })
            self._update_project_overview(data)

    def _update_feature_modules(
        self,
        data: Dict[str, Any],
        req_summary: Dict[str, Any],
        module_assignment: Dict[str, Any]
    ) -> None:
        """Update feature modules section."""

        modules = data.get("feature_modules", [])
        module_name = module_assignment.get("module_name", "其他功能")
        is_new_module = module_assignment.get("is_new_module", False)

        # Find or create module
        module = None
        for m in modules:
            if m.get("module_name") == module_name:
                module = m
                break

        if not module:
            module = {
                "module_name": module_name,
                "description": module_assignment.get("module_description", ""),
                "features": []
            }
            modules.append(module)

        # Add feature to module
        module["features"].append({
            "name": req_summary.get("title", ""),
            "description": req_summary.get("description", ""),
            "status": "completed",
            "conversation_id": req_summary.get("conversation_id", ""),
            "key_points": req_summary.get("key_points", []),
            "completed_at": datetime.utcnow().isoformat()
        })

        data["feature_modules"] = modules

    def _update_tech_architecture(
        self,
        data: Dict[str, Any],
        tech_insights: Dict[str, Any]
    ) -> None:
        """Update tech architecture section."""

        if not tech_insights.get("has_tech_update"):
            return

        tech_arch = data.get("tech_architecture", {})

        # Add new patterns
        if "patterns" not in tech_arch:
            tech_arch["patterns"] = []

        for pattern in tech_insights.get("patterns", []):
            if pattern not in tech_arch["patterns"]:
                tech_arch["patterns"].append(pattern)

        # Add new conventions
        if "conventions" not in tech_arch:
            tech_arch["conventions"] = {}

        for convention in tech_insights.get("conventions", []):
            # Simple string-based convention storage
            if convention not in tech_arch.get("notes", []):
                if "notes" not in tech_arch["conventions"]:
                    tech_arch["conventions"]["notes"] = []
                tech_arch["conventions"]["notes"].append(convention)

        data["tech_architecture"] = tech_arch

    def _update_ui_standards(
        self,
        data: Dict[str, Any],
        ui_insights: Dict[str, Any]
    ) -> None:
        """Update UI/UX standards section."""

        if not ui_insights.get("has_ui_update"):
            return

        ui_standards = data.get("ui_ux_standards", {})

        # Add new components
        if "common_components" not in ui_standards:
            ui_standards["common_components"] = []

        for component in ui_insights.get("components", []):
            if component not in ui_standards["common_components"]:
                ui_standards["common_components"].append(component)

        # Add new patterns
        if "interaction_patterns" not in ui_standards:
            ui_standards["interaction_patterns"] = []

        for pattern in ui_insights.get("patterns", []):
            if pattern not in ui_standards["interaction_patterns"]:
                ui_standards["interaction_patterns"].append(pattern)

        data["ui_ux_standards"] = ui_standards

    def _update_project_overview(self, data: Dict[str, Any]) -> None:
        """Update project overview statistics."""

        overview = data.get("project_overview", {})
        status = overview.get("current_status", {})

        # Count completed requirements
        completed_reqs = data.get("completed_requirements", [])
        status["total_requirements"] = len(completed_reqs)

        # Extract completed features
        completed_features = [req.get("title", "") for req in completed_reqs]
        status["completed_features"] = completed_features[-10:]  # Last 10

        # Count by module
        modules = data.get("feature_modules", [])
        feature_count = {}
        for module in modules:
            module_name = module.get("module_name", "")
            feature_count[module_name] = len(module.get("features", []))

        status["feature_count_by_module"] = feature_count

        overview["current_status"] = status
        data["project_overview"] = overview
