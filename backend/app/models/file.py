"""
Uploaded File model - tracks files uploaded to projects.
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from backend.app.core.database import Base


class UploadedFile(Base):
    """
    Uploaded File model.
    Tracks files uploaded for project knowledge base.
    """
    __tablename__ = "uploaded_files"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    
    filename = Column(String(255), nullable=False)  # Original filename
    file_path = Column(String(500), nullable=False)  # Storage path
    file_type = Column(String(50), nullable=False)  # e.g., "pdf", "image", "docx"
    file_size = Column(Integer, nullable=False)  # Size in bytes
    
    status = Column(String(50), default="pending", nullable=False)  # pending, analyzing, completed, failed
    analysis_result = Column(String(1000), nullable=True)  # Brief description of analysis

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Relationships
    # project = relationship("Project", back_populates="files")
    
    def __repr__(self):
        return f"<UploadedFile(id={self.id}, filename={self.filename})>"

