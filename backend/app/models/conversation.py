"""
Conversation model - stores chat messages for PRD writing.
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Integer, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from backend.app.core.database import Base


class Conversation(Base):
    """
    Conversation model.
    Represents a single PRD writing session within a project.
    """
    __tablename__ = "conversations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    
    title = Column(String(255), nullable=True)  # Auto-generated or user-defined
    status = Column(String(50), default="active", nullable=False)  # active, completed, archived
    
    # Summary of the conversation (generated periodically)
    summary = Column(Text, nullable=True)

    # Requirement summary for completed conversations (stored when marked as completed)
    requirement_summary = Column(JSON, nullable=True)
    # Example structure:
    # {
    #   "title": "用户登录功能",
    #   "description": "实现用户通过邮箱和密码登录",
    #   "key_points": ["需要支持记住密码", "登录失败3次锁定账号"],
    #   "prd_generated": true
    # }

    # PRD draft for real-time preview and editing
    prd_draft = Column(JSON, nullable=True)
    # Example structure:
    # {
    #   "version": 1,
    #   "last_updated": "2025-12-27T10:00:00Z",
    #   "sections": {
    #     "background": {"content": "...", "status": "draft", "updated_at": "..."},
    #     "objectives": {"content": "...", "status": "draft", "updated_at": "..."},
    #     "user_stories": {"content": "...", "status": "draft", "updated_at": "..."},
    #     "functional_requirements": {"content": "...", "status": "draft", "updated_at": "..."},
    #     "non_functional": {"content": "...", "status": "draft", "updated_at": "..."},
    #     "tech_solution": {"content": "...", "status": "draft", "updated_at": "..."},
    #     "risks": {"content": "...", "status": "draft", "updated_at": "..."}
    #   }
    # }

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Relationships
    # project = relationship("Project", back_populates="conversations")
    # messages = relationship("Message", back_populates="conversation", order_by="Message.created_at")
    
    def __repr__(self):
        return f"<Conversation(id={self.id}, title={self.title})>"


class Message(Base):
    """
    Message model.
    Individual messages within a conversation.
    """
    __tablename__ = "messages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    
    role = Column(String(20), nullable=False)  # "user" or "assistant"
    content = Column(Text, nullable=False)
    
    # Metadata (e.g., knowledge base references, tokens used)
    meta_data = Column(JSON, nullable=True, default=dict)
    # Example:
    # {
    #   "knowledge_references": ["ui_standards.primary_color"],
    #   "tokens_used": 150
    # }
    
    sequence = Column(Integer, nullable=False)  # Message order in conversation
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Relationships
    # conversation = relationship("Conversation", back_populates="messages")
    
    def __repr__(self):
        return f"<Message(id={self.id}, role={self.role}, sequence={self.sequence})>"

