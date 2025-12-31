"""
API endpoints for knowledge base search.
"""
import logging
from uuid import UUID
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from backend.app.core.database import get_db
from backend.app.models.knowledge_base import KnowledgeBase
from backend.app.models.conversation import Conversation

logger = logging.getLogger(__name__)

router = APIRouter()


# Pydantic schemas
class SearchResult(BaseModel):
    type: str  # requirement, module, tech_pattern, ui_component
    title: str
    description: str
    content: str
    conversation_id: Optional[str] = None
    module_name: Optional[str] = None
    tags: List[str] = []
    created_at: Optional[str] = None
    relevance_score: float = 1.0


class SearchResponse(BaseModel):
    results: List[SearchResult]
    total: int
    query: str


@router.get("/knowledge/{project_id}", response_model=SearchResponse)
async def search_knowledge_base(
    project_id: UUID,
    q: str = Query(..., description="搜索关键词"),
    module: Optional[str] = Query(None, description="按模块筛选"),
    type: Optional[str] = Query(None, description="类型筛选: requirement, module, tech, ui"),
    db: AsyncSession = Depends(get_db)
):
    """
    Search knowledge base content.

    Args:
        project_id: Project ID
        q: Search query
        module: Filter by module name
        type: Filter by result type
        db: Database session

    Returns:
        Search results
    """
    # Get knowledge base
    result = await db.execute(
        select(KnowledgeBase).where(KnowledgeBase.project_id == project_id)
    )
    kb = result.scalar_one_or_none()

    if not kb or not kb.structured_data:
        return SearchResponse(results=[], total=0, query=q)

    data = kb.structured_data
    results = []
    query_lower = q.lower()

    # Search in completed requirements
    if not type or type == "requirement":
        completed_reqs = data.get("completed_requirements", [])
        for req in completed_reqs:
            title = req.get("title", "")
            description = req.get("description", "")
            key_points = " ".join(req.get("key_points", []))

            # Calculate relevance score
            score = 0.0
            search_text = f"{title} {description} {key_points}".lower()

            if query_lower in title.lower():
                score += 3.0
            if query_lower in description.lower():
                score += 2.0
            if query_lower in key_points.lower():
                score += 1.0

            # Simple word matching
            query_words = query_lower.split()
            for word in query_words:
                if word in search_text:
                    score += 0.5

            if score > 0:
                results.append(SearchResult(
                    type="requirement",
                    title=title,
                    description=description,
                    content=key_points,
                    conversation_id=req.get("conversation_id"),
                    tags=["已完成", "需求"],
                    created_at=req.get("archived_at"),
                    relevance_score=score
                ))

    # Search in feature modules
    if not type or type == "module":
        feature_modules = data.get("feature_modules", [])
        for module in feature_modules:
            module_name = module.get("module_name", "")
            module_desc = module.get("description", "")

            # Apply module filter
            if module and module_name != module:
                continue

            search_text = f"{module_name} {module_desc}".lower()
            score = 0.0

            if query_lower in module_name.lower():
                score += 3.0
            if query_lower in module_desc.lower():
                score += 2.0

            if score > 0:
                feature_count = len(module.get("features", []))
                results.append(SearchResult(
                    type="module",
                    title=module_name,
                    description=module_desc,
                    content=f"包含 {feature_count} 个功能",
                    module_name=module_name,
                    tags=["模块"],
                    relevance_score=score
                ))

            # Search in features within module
            if not type or type == "requirement":
                for feature in module.get("features", []):
                    feature_name = feature.get("name", "")
                    feature_desc = feature.get("description", "")
                    key_points = " ".join(feature.get("key_points", []))

                    # Apply module filter
                    if module and module_name != module:
                        continue

                    search_text = f"{feature_name} {feature_desc} {key_points}".lower()
                    score = 0.0

                    if query_lower in feature_name.lower():
                        score += 3.0
                    if query_lower in feature_desc.lower():
                        score += 2.0
                    if query_lower in key_points.lower():
                        score += 1.0

                    if score > 0:
                        results.append(SearchResult(
                            type="requirement",
                            title=feature_name,
                            description=feature_desc,
                            content=key_points,
                            conversation_id=feature.get("conversation_id"),
                            module_name=module_name,
                            tags=["功能", module_name],
                            created_at=feature.get("completed_at"),
                            relevance_score=score
                        ))

    # Search in tech architecture
    if not type or type == "tech":
        tech_arch = data.get("tech_architecture", {})
        patterns = tech_arch.get("patterns", [])

        for pattern in patterns:
            if query_lower in pattern.lower():
                results.append(SearchResult(
                    type="tech_pattern",
                    title=pattern,
                    description="技术模式",
                    content=pattern,
                    tags=["技术架构"],
                    relevance_score=2.0
                ))

    # Search in UI/UX standards
    if not type or type == "ui":
        ui_standards = data.get("ui_ux_standards", {})

        # Search in components
        components = ui_standards.get("common_components", [])
        for component in components:
            if query_lower in component.lower():
                results.append(SearchResult(
                    type="ui_component",
                    title=component,
                    description="UI 组件",
                    content=component,
                    tags=["UI/UX"],
                    relevance_score=2.0
                ))

        # Search in interaction patterns
        patterns = ui_standards.get("interaction_patterns", [])
        for pattern in patterns:
            if query_lower in pattern.lower():
                results.append(SearchResult(
                    type="ui_pattern",
                    title=pattern,
                    description="交互模式",
                    content=pattern,
                    tags=["UI/UX"],
                    relevance_score=2.0
                ))

    # Sort by relevance score
    results.sort(key=lambda x: x.relevance_score, reverse=True)

    logger.info(f"Search '{q}' in project {project_id}: {len(results)} results")

    return SearchResponse(
        results=results,
        total=len(results),
        query=q
    )
