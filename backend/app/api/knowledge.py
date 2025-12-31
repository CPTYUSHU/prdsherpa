"""
Knowledge base management API endpoints.
"""
import logging
import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from backend.app.core.database import get_db
from backend.app.models.project import Project
from backend.app.models.knowledge_base import KnowledgeBase
from backend.app.models.file import UploadedFile
from backend.app.schemas.knowledge import (
    KnowledgeBaseResponse,
    KnowledgeBaseBuildRequest,
    KnowledgeBaseUpdateRequest,
    KnowledgeBaseConfirmRequest,
    KnowledgeBaseData,
)
from backend.app.services.knowledge_builder import knowledge_builder

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/build/{project_id}", response_model=KnowledgeBaseResponse)
async def build_knowledge_base(
    project_id: UUID,
    request: KnowledgeBaseBuildRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Build knowledge base from all analyzed files in the project.
    
    This will:
    1. Gather all file analysis results
    2. Use AI to integrate them into a structured knowledge base
    3. Generate pending questions for PM to confirm
    """
    logger.info(f"Building knowledge base for project: {project_id}")
    
    # Verify project exists
    project_query = select(Project).where(Project.id == project_id)
    project_result = await db.execute(project_query)
    project = project_result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found",
        )
    
    # Check if knowledge base already exists
    kb_query = select(KnowledgeBase).where(KnowledgeBase.project_id == project_id)
    kb_result = await db.execute(kb_query)
    existing_kb = kb_result.scalar_one_or_none()
    
    if existing_kb and not request.force_rebuild:
        logger.info(f"Knowledge base already exists for project {project_id}")
        return existing_kb
    
    # Get all completed file analyses
    files_query = (
        select(UploadedFile)
        .where(UploadedFile.project_id == project_id)
        .where(UploadedFile.status == "completed")
    )
    files_result = await db.execute(files_query)
    files = files_result.scalars().all()
    
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No analyzed files found. Please upload and analyze files first.",
        )
    
    logger.info(f"Found {len(files)} analyzed files")
    
    # Prepare file analyses
    file_analyses = []
    for file in files:
        # Read analysis from file (stored during analysis)
        # For now, we'll use a simplified approach
        # In production, you might want to store full analysis in a separate table
        file_analyses.append({
            "filename": file.filename,
            "file_type": file.file_type,
            "analysis": {
                "summary": file.analysis_result or "No analysis available"
            }
        })
    
    # For better results, we should re-analyze or fetch stored detailed analysis
    # Let's fetch from a hypothetical analysis storage
    # TODO: Implement proper analysis storage and retrieval
    
    # Build knowledge base
    try:
        kb_data = await knowledge_builder.build_knowledge_base(
            project_name=project.name,
            file_analyses=file_analyses,
        )
        
        # Create or update knowledge base
        if existing_kb:
            logger.info(f"Updating existing knowledge base (version {existing_kb.version})")
            existing_kb.structured_data = kb_data
            existing_kb.version += 1
            existing_kb.status = "confirmed" if not kb_data.get("pending_questions") else "pending"
            kb = existing_kb
        else:
            logger.info("Creating new knowledge base")
            kb = KnowledgeBase(
                project_id=project_id,
                structured_data=kb_data,
                version=1,
                status="pending",
            )
            db.add(kb)
        
        await db.commit()
        await db.refresh(kb)
        
        logger.info(f"✅ Knowledge base built successfully for project: {project.name}")
        
        return kb
    
    except Exception as e:
        logger.error(f"Error building knowledge base: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error building knowledge base: {str(e)}",
        )


@router.get("/{project_id}", response_model=KnowledgeBaseResponse)
async def get_knowledge_base(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Get the knowledge base for a project.
    """
    # Verify project exists
    project_query = select(Project).where(Project.id == project_id)
    project_result = await db.execute(project_query)
    project = project_result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found",
        )
    
    # Get knowledge base
    kb_query = select(KnowledgeBase).where(KnowledgeBase.project_id == project_id)
    kb_result = await db.execute(kb_query)
    kb = kb_result.scalar_one_or_none()
    
    if not kb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Knowledge base not found for project {project_id}. Please build it first.",
        )
    
    return kb


@router.patch("/{project_id}", response_model=KnowledgeBaseResponse)
async def update_knowledge_base(
    project_id: UUID,
    request: KnowledgeBaseUpdateRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Update knowledge base content.
    PM can edit any part of the knowledge base.
    """
    # Get knowledge base
    kb_query = select(KnowledgeBase).where(KnowledgeBase.project_id == project_id)
    kb_result = await db.execute(kb_query)
    kb = kb_result.scalar_one_or_none()
    
    if not kb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Knowledge base not found for project {project_id}",
        )
    
    # Update structured data
    kb.structured_data = request.structured_data.dict()
    kb.version += 1
    
    await db.commit()
    await db.refresh(kb)
    
    logger.info(f"✅ Knowledge base updated for project {project_id} (version {kb.version})")
    
    return kb


@router.post("/{project_id}/confirm", response_model=KnowledgeBaseResponse)
async def confirm_knowledge_base(
    project_id: UUID,
    request: KnowledgeBaseConfirmRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Confirm knowledge base.
    PM confirms the knowledge base is correct and ready to use.
    Optionally provide answers to pending questions.
    """
    # Get knowledge base
    kb_query = select(KnowledgeBase).where(KnowledgeBase.project_id == project_id)
    kb_result = await db.execute(kb_query)
    kb = kb_result.scalar_one_or_none()
    
    if not kb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Knowledge base not found for project {project_id}",
        )
    
    # If answers provided, add them to raw_insights
    if request.answers:
        kb_data = kb.structured_data
        if "raw_insights" not in kb_data:
            kb_data["raw_insights"] = []
        
        for question, answer in request.answers.items():
            kb_data["raw_insights"].append(f"Q: {question}\nA: {answer}")
        
        # Clear pending questions
        kb_data["pending_questions"] = []
        kb.structured_data = kb_data
    
    # Update status
    kb.status = "confirmed"
    kb.version += 1
    
    await db.commit()
    await db.refresh(kb)
    
    logger.info(f"✅ Knowledge base confirmed for project {project_id}")
    
    return kb

