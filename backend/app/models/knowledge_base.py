"""
Knowledge Base model - stores structured project context.
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from backend.app.core.database import Base


class KnowledgeBase(Base):
    """
    Knowledge Base model.
    Stores AI-generated structured understanding of the project.
    """
    __tablename__ = "knowledge_bases"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    
    # Structured data (JSON format)
    structured_data = Column(JSON, nullable=False, default=dict)
    # Example structure:
    # {
    #   "system_overview": {
    #     "product_type": "CMS系统",
    #     "core_modules": ["文章管理", "用户管理"]
    #   },
    #   "ui_standards": {
    #     "primary_color": "#4299E1",
    #     "component_library": "Ant Design"
    #   },
    #   "tech_conventions": {
    #     "naming_style": "camelCase",
    #     "known_fields": [...]
    #   },
    #   "pending_questions": [...]
    # }
    
    version = Column(Integer, default=1, nullable=False)
    status = Column(String(50), default="pending", nullable=False)  # pending, analyzing, confirmed

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Relationships
    # project = relationship("Project", back_populates="knowledge_base")
    # embeddings = relationship("DocumentEmbedding", back_populates="knowledge_base")
    
    def __repr__(self):
        return f"<KnowledgeBase(id={self.id}, project_id={self.project_id}, version={self.version})>"


class DocumentEmbedding(Base):
    """
    Document Embedding model.
    Stores vector embeddings of uploaded documents for semantic search.
    """
    __tablename__ = "document_embeddings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    knowledge_base_id = Column(UUID(as_uuid=True), ForeignKey("knowledge_bases.id", ondelete="CASCADE"), nullable=False)
    
    source_file = Column(String(255), nullable=False)  # Original filename
    chunk_text = Column(Text, nullable=False)  # Text chunk
    chunk_index = Column(Integer, nullable=False)  # Order in the document
    
    # Vector embedding (using pgvector extension)
    # Note: Gemini embedding dimension is 768
    # embedding = Column(Vector(768), nullable=False)  # Will be added after pgvector setup
    
    meta_data = Column(JSON, nullable=True, default=dict)  # Additional metadata

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Relationships
    # knowledge_base = relationship("KnowledgeBase", back_populates="embeddings")
    
    def __repr__(self):
        return f"<DocumentEmbedding(id={self.id}, source_file={self.source_file})>"

