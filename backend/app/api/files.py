"""
File upload and analysis API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
from uuid import UUID
import os
import aiofiles
from pathlib import Path
import logging

from backend.app.core.database import get_db
from backend.app.core.config import settings
from backend.app.models.file import UploadedFile
from backend.app.models.project import Project
from backend.app.schemas.file import (
    FileUploadResponse,
    FileListResponse,
    FileAnalysisResponse,
)
from backend.app.services.file_processor import file_processor
from backend.app.services.gemini_service import gemini_service

logger = logging.getLogger(__name__)
router = APIRouter()


# Ensure upload directory exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)


@router.post("/upload", response_model=FileUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(
    project_id: UUID = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload a file to a project.
    
    Supported file types:
    - Documents: .pdf, .docx, .doc, .txt, .md
    - Images: .png, .jpg, .jpeg, .gif, .webp
    
    File size limit: 10MB (configurable)
    """
    # Verify project exists
    query = select(Project).where(Project.id == project_id)
    result = await db.execute(query)
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found",
        )
    
    # Check file count limit
    count_query = select(func.count(UploadedFile.id)).where(UploadedFile.project_id == project_id)
    count_result = await db.execute(count_query)
    file_count = count_result.scalar()
    
    if file_count >= settings.MAX_FILES_PER_PROJECT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Project has reached maximum file limit ({settings.MAX_FILES_PER_PROJECT})",
        )
    
    # Check file size
    file_content = await file.read()
    file_size = len(file_content)
    
    if file_size > settings.max_file_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds limit ({settings.MAX_FILE_SIZE_MB}MB)",
        )
    
    # Determine file type
    file_type = file_processor.get_file_type(file.filename)
    
    if file_type == 'unknown':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type. Supported: .pdf, .docx, .pptx, .txt, .md, .png, .jpg, .jpeg",
        )
    
    # Save file to disk
    project_upload_dir = os.path.join(settings.UPLOAD_DIR, str(project_id))
    os.makedirs(project_upload_dir, exist_ok=True)
    
    # Generate unique filename
    import uuid
    file_id = uuid.uuid4()
    file_ext = Path(file.filename).suffix
    saved_filename = f"{file_id}{file_ext}"
    file_path = os.path.join(project_upload_dir, saved_filename)
    
    # Write file
    async with aiofiles.open(file_path, 'wb') as f:
        await f.write(file_content)
    
    logger.info(f"Saved file: {file_path} ({file_size} bytes)")
    
    # Create database record
    uploaded_file = UploadedFile(
        id=file_id,
        project_id=project_id,
        filename=file.filename,
        file_path=file_path,
        file_type=file_type,
        file_size=file_size,
        status="pending",
    )
    
    db.add(uploaded_file)
    await db.commit()
    await db.refresh(uploaded_file)
    
    # TODO: Trigger async analysis task (Celery)
    # For now, we'll analyze synchronously
    logger.info(f"File uploaded successfully: {file.filename}")
    
    return uploaded_file


@router.post("/{file_id}/analyze", response_model=FileAnalysisResponse)
async def analyze_file(
    file_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Analyze an uploaded file using Gemini AI.
    
    This will:
    1. Extract text from the file (for documents)
    2. Send to Gemini for analysis
    3. Store the analysis result
    """
    # Get file record
    query = select(UploadedFile).where(UploadedFile.id == file_id)
    result = await db.execute(query)
    uploaded_file = result.scalar_one_or_none()
    
    if not uploaded_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File with id {file_id} not found",
        )
    
    # Update status to analyzing
    uploaded_file.status = "analyzing"
    await db.commit()
    
    try:
        analysis_result = None

        # Process based on file type
        if uploaded_file.file_type == 'image':
            # Analyze image directly with Gemini
            analysis_result = await gemini_service.analyze_image(uploaded_file.file_path)

        elif uploaded_file.file_type == 'pptx':
            # Extract text from PPTX
            text_content = await file_processor.process_file(
                uploaded_file.file_path,
                uploaded_file.file_type
            )

            # Extract images from PPTX
            image_paths = await file_processor.extract_images_from_pptx(uploaded_file.file_path)
            logger.info(f"Extracted {len(image_paths)} images from PPTX: {uploaded_file.filename}")

            if text_content or image_paths:
                # Analyze with Gemini (text + images)
                analysis_result = await gemini_service.analyze_document_with_images(
                    document_content=text_content or "无文本内容",
                    document_type=uploaded_file.file_type,
                    filename=uploaded_file.filename,
                    image_paths=image_paths if image_paths else None,
                )

        else:
            # Extract text first
            text_content = await file_processor.process_file(
                uploaded_file.file_path,
                uploaded_file.file_type
            )

            if text_content:
                # Analyze with Gemini
                analysis_result = await gemini_service.analyze_document(
                    document_content=text_content,
                    document_type=uploaded_file.file_type,
                    filename=uploaded_file.filename,
                )
        
        # Update file record
        uploaded_file.status = "completed"
        if analysis_result:
            # Store summary as analysis_result
            summary = analysis_result.get('summary', 'Analysis completed')
            uploaded_file.analysis_result = summary[:1000]  # Limit to 1000 chars
        
        await db.commit()
        await db.refresh(uploaded_file)
        
        logger.info(f"File analysis completed: {uploaded_file.filename}")
        
        return FileAnalysisResponse(
            file_id=file_id,
            status="completed",
            analysis=analysis_result,
            message="File analyzed successfully",
        )
    
    except Exception as e:
        # Update status to failed
        uploaded_file.status = "failed"
        uploaded_file.analysis_result = f"Error: {str(e)}"
        await db.commit()
        
        logger.error(f"Error analyzing file {file_id}: {str(e)}")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing file: {str(e)}",
        )


@router.get("/project/{project_id}", response_model=FileListResponse)
async def list_project_files(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    List all files uploaded to a project.
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
    
    # Get files
    query = select(UploadedFile).where(UploadedFile.project_id == project_id).order_by(UploadedFile.created_at.desc())
    result = await db.execute(query)
    files = result.scalars().all()
    
    return FileListResponse(files=files, total=len(files))


@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_file(
    file_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Delete an uploaded file.
    """
    # Get file record
    query = select(UploadedFile).where(UploadedFile.id == file_id)
    result = await db.execute(query)
    uploaded_file = result.scalar_one_or_none()
    
    if not uploaded_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File with id {file_id} not found",
        )
    
    # Delete physical file
    try:
        if os.path.exists(uploaded_file.file_path):
            os.remove(uploaded_file.file_path)
            logger.info(f"Deleted file: {uploaded_file.file_path}")
    except Exception as e:
        logger.error(f"Error deleting physical file: {str(e)}")
    
    # Delete database record
    await db.delete(uploaded_file)
    await db.commit()
    
    return None

