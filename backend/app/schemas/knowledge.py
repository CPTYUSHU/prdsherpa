"""
Pydantic schemas for Knowledge Base API.
"""
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class SystemOverview(BaseModel):
    """System overview section of knowledge base."""
    product_type: Optional[str] = None
    core_modules: List[str] = []
    description: Optional[str] = None


class UIStandards(BaseModel):
    """UI standards section of knowledge base."""
    primary_colors: List[str] = []
    component_library: Optional[str] = None
    layout_features: List[str] = []
    screenshots: List[str] = []  # File paths to screenshots


class TechConventions(BaseModel):
    """Technical conventions section of knowledge base."""
    naming_style: Optional[str] = None
    api_style: Optional[str] = None
    known_fields: List[Dict[str, Any]] = []
    # Example: [{"name": "userID", "type": "string", "usage": "用户唯一标识"}]


class PendingQuestion(BaseModel):
    """A question that needs PM confirmation."""
    question: str
    context: Optional[str] = None
    suggested_answer: Optional[str] = None


class KnowledgeBaseData(BaseModel):
    """Complete knowledge base structure."""
    system_overview: SystemOverview = SystemOverview()
    ui_standards: UIStandards = UIStandards()
    tech_conventions: TechConventions = TechConventions()
    pending_questions: List[PendingQuestion] = []
    raw_insights: List[str] = []  # Additional insights from AI


class KnowledgeBaseResponse(BaseModel):
    """Schema for knowledge base response."""
    id: UUID
    project_id: UUID
    structured_data: KnowledgeBaseData
    version: int
    status: str  # pending, analyzing, confirmed
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class KnowledgeBaseBuildRequest(BaseModel):
    """Request to build knowledge base."""
    force_rebuild: bool = Field(default=False, description="Force rebuild even if exists")


class KnowledgeBaseUpdateRequest(BaseModel):
    """Request to update knowledge base."""
    structured_data: KnowledgeBaseData
    notes: Optional[str] = None


class KnowledgeBaseConfirmRequest(BaseModel):
    """Request to confirm knowledge base."""
    answers: Optional[Dict[str, str]] = None  # Answers to pending questions
    notes: Optional[str] = None

