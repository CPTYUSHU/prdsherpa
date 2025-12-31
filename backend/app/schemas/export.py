"""
Pydantic schemas for PRD export.
"""
from pydantic import BaseModel, Field
from typing import Optional


class ExportRequest(BaseModel):
    """Schema for PRD export request."""
    conversation_id: str = Field(..., description="Conversation ID to export")
    format: str = Field(default="markdown", pattern="^(markdown|md)$", description="Export format")
    include_knowledge_base: bool = Field(default=True, description="Include knowledge base in export")
    template: Optional[str] = Field(None, description="Custom template (optional)")


class ExportResponse(BaseModel):
    """Schema for PRD export response."""
    content: str = Field(..., description="Exported PRD content")
    format: str = Field(..., description="Export format")
    filename: str = Field(..., description="Suggested filename")

