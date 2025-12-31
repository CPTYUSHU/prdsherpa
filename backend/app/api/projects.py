"""
Project management API endpoints.
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
from uuid import UUID

from backend.app.core.database import get_db
from backend.app.models.project import Project
from backend.app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectListResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new project.
    
    Request body:
    - name: Project name (required)
    - description: Project description (optional)
    """
    # Create new project
    new_project = Project(
        name=project_data.name,
        description=project_data.description,
    )
    
    db.add(new_project)
    await db.commit()
    await db.refresh(new_project)
    
    logger.info(f"✅ Created project: {new_project.name} (ID: {new_project.id})")
    
    return new_project


@router.get("/", response_model=ProjectListResponse)
async def list_projects(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """
    List all projects.
    
    Query parameters:
    - skip: Number of projects to skip (for pagination)
    - limit: Maximum number of projects to return
    """
    # Get total count
    count_query = select(func.count(Project.id))
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Get projects (ordered by last_conversation_at, then updated_at)
    query = (
        select(Project)
        .order_by(
            Project.last_conversation_at.desc().nullslast(),
            Project.updated_at.desc(),
        )
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(query)
    projects = result.scalars().all()
    
    return ProjectListResponse(projects=projects, total=total)


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Get a specific project by ID.
    """
    query = select(Project).where(Project.id == project_id)
    result = await db.execute(query)
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found",
        )
    
    return project


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: UUID,
    project_data: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
):
    """
    Update a project.
    
    Request body:
    - name: New project name (optional)
    - description: New project description (optional)
    """
    # Get existing project
    query = select(Project).where(Project.id == project_id)
    result = await db.execute(query)
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found",
        )
    
    # Update fields
    if project_data.name is not None:
        project.name = project_data.name
    if project_data.description is not None:
        project.description = project_data.description
    
    await db.commit()
    await db.refresh(project)
    
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a project.
    This will cascade delete all related data (knowledge base, conversations, files).
    """
    # Get existing project
    query = select(Project).where(Project.id == project_id)
    result = await db.execute(query)
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found",
        )
    
    await db.delete(project)
    await db.commit()
    
    return None

