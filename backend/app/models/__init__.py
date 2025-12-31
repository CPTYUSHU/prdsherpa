"""
Database models.
Import all models here to ensure they are registered with SQLAlchemy.
"""
from backend.app.models.project import Project
from backend.app.models.knowledge_base import KnowledgeBase, DocumentEmbedding
from backend.app.models.conversation import Conversation, Message
from backend.app.models.file import UploadedFile

__all__ = [
    "Project",
    "KnowledgeBase",
    "DocumentEmbedding",
    "Conversation",
    "Message",
    "UploadedFile",
]

