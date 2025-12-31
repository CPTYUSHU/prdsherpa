"""
Project model - represents a PRD project.
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from backend.app.core.database import Base


class Project(Base):
    """
    Project model.
    Each project contains:
    - Basic info (name, description)
    - Knowledge base (related via relationship)
    - Conversations (related via relationship)
    - Uploaded files (related via relationship)
    """
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    last_conversation_at = Column(DateTime, nullable=True)  # For sorting in sidebar
    
    # Relationships (will be defined after creating other models)
    # knowledge_base = relationship("KnowledgeBase", back_populates="project", uselist=False)
    # conversations = relationship("Conversation", back_populates="project")
    # files = relationship("UploadedFile", back_populates="project")
    
    def __repr__(self):
        return f"<Project(id={self.id}, name={self.name})>"

