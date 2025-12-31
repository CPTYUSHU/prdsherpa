"""
Pydantic schemas for Project API.
"""
from datetime import datetime, timezone
from uuid import UUID
from pydantic import BaseModel, Field, field_serializer
from typing import Optional


class ProjectCreate(BaseModel):
    """Schema for creating a new project."""
    name: str = Field(..., min_length=1, max_length=255, description="Project name")
    description: Optional[str] = Field(None, description="Project description")


class ProjectUpdate(BaseModel):
    """Schema for updating a project."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None


class ProjectResponse(BaseModel):
    """Schema for project response."""
    id: UUID
    name: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
    last_conversation_at: Optional[datetime]

    class Config:
        from_attributes = True  # Allows ORM model to Pydantic model conversion

    @field_serializer('created_at', 'updated_at', 'last_conversation_at')
    def serialize_datetime(self, dt: Optional[datetime], _info) -> Optional[str]:
        """Serialize datetime to ISO 8601 format with UTC timezone."""
        if dt is None:
            return None
        # Ensure datetime is timezone-aware (UTC)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.isoformat()


class ProjectListResponse(BaseModel):
    """Schema for project list response."""
    projects: list[ProjectResponse]
    total: int

