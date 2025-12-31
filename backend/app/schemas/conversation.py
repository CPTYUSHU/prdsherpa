"""
Pydantic schemas for Conversation API.
"""
from datetime import datetime, timezone
from uuid import UUID
from pydantic import BaseModel, Field, field_serializer
from typing import Optional, List, Dict, Any


class MessageCreate(BaseModel):
    """Schema for creating a message."""
    content: str = Field(..., min_length=1, description="Message content")
    role: str = Field(..., pattern="^(user|assistant)$", description="Message role: user or assistant")


class MessageResponse(BaseModel):
    """Schema for message response."""
    id: UUID
    conversation_id: UUID
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True

    @field_serializer('created_at')
    def serialize_datetime(self, dt: datetime, _info) -> str:
        """Serialize datetime to ISO 8601 format with UTC timezone."""
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.isoformat()


class ConversationCreate(BaseModel):
    """Schema for creating a conversation."""
    project_id: UUID
    title: Optional[str] = Field(None, description="Conversation title (optional)")


class RequirementSummary(BaseModel):
    """Schema for requirement summary."""
    title: str = Field(..., description="Requirement title")
    description: str = Field(..., description="Brief requirement description")
    key_points: List[str] = Field(default_factory=list, description="Key requirement points")
    prd_generated: bool = Field(default=False, description="Whether PRD was generated")


class ConversationResponse(BaseModel):
    """Schema for conversation response."""
    id: UUID
    project_id: UUID
    title: Optional[str]
    status: str = Field(default="active", description="Conversation status: active, completed, archived")
    requirement_summary: Optional[Dict[str, Any]] = Field(None, description="Requirement summary for completed conversations")
    message_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

    @field_serializer('created_at', 'updated_at')
    def serialize_datetime(self, dt: datetime, _info) -> str:
        """Serialize datetime to ISO 8601 format with UTC timezone."""
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.isoformat()


class ConversationDetailResponse(BaseModel):
    """Schema for detailed conversation response with messages."""
    id: UUID
    project_id: UUID
    title: Optional[str]
    status: str
    requirement_summary: Optional[Dict[str, Any]] = None
    messages: List[MessageResponse]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

    @field_serializer('created_at', 'updated_at')
    def serialize_datetime(self, dt: datetime, _info) -> str:
        """Serialize datetime to ISO 8601 format with UTC timezone."""
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.isoformat()


class ConversationListResponse(BaseModel):
    """Schema for conversation list response."""
    conversations: List[ConversationResponse]
    total: int


class ChatRequest(BaseModel):
    """Schema for chat request (send message and get AI response)."""
    message: str = Field(..., min_length=1, description="User message")
    stream: bool = Field(default=False, description="Enable streaming response")
    image_file_ids: Optional[List[UUID]] = Field(default=None, description="Optional list of uploaded file IDs to include as images")


class ChatResponse(BaseModel):
    """Schema for chat response."""
    user_message: MessageResponse
    assistant_message: MessageResponse
    conversation_id: UUID


class ConversationStatusUpdate(BaseModel):
    """Schema for updating conversation status."""
    status: str = Field(..., pattern="^(active|completed|archived)$", description="New status: active, completed, or archived")
    generate_summary: bool = Field(default=True, description="Whether to auto-generate requirement summary when marking as completed")


class ConversationTitleUpdate(BaseModel):
    """Schema for updating conversation title."""
    title: str = Field(..., min_length=1, max_length=100, description="New title for the conversation")

