"""
Pydantic schemas for File Upload API.
"""
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field
from typing import Optional


class FileUploadResponse(BaseModel):
    """Schema for file upload response."""
    id: UUID
    project_id: UUID
    filename: str
    file_type: str
    file_size: int
    status: str
    analysis_result: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class FileListResponse(BaseModel):
    """Schema for file list response."""
    files: list[FileUploadResponse]
    total: int


class FileAnalysisResponse(BaseModel):
    """Schema for file analysis result."""
    file_id: UUID
    status: str
    analysis: Optional[dict]
    message: str

