"""
API endpoints for PRD management.
"""
import logging
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from backend.app.core.database import get_db
from backend.app.models.conversation import Conversation
from backend.app.services.prd_service import PRDService
from backend.app.services.gemini_service import GeminiService

logger = logging.getLogger(__name__)

router = APIRouter()


# Pydantic schemas
class PRDSectionUpdate(BaseModel):
    section_key: str
    content: str


class PRDDraftResponse(BaseModel):
    version: int
    last_updated: str
    sections: dict


def get_prd_service() -> PRDService:
    """Dependency to get PRD service."""
    gemini_service = GeminiService()
    return PRDService(gemini_service)


@router.post("/{conversation_id}/outline", response_model=PRDDraftResponse)
async def generate_prd_outline(
    conversation_id: UUID,
    db: AsyncSession = Depends(get_db),
    prd_service: PRDService = Depends(get_prd_service)
):
    """
    Generate PRD outline based on current conversation.

    Args:
        conversation_id: Conversation ID
        db: Database session
        prd_service: PRD service

    Returns:
        PRD draft with section outlines
    """
    # Get conversation to get project_id
    result = await db.execute(
        select(Conversation).where(Conversation.id == conversation_id)
    )
    conversation = result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation with id {conversation_id} not found"
        )

    # Generate outline
    draft = await prd_service.generate_prd_outline(
        db=db,
        conversation_id=conversation_id,
        project_id=conversation.project_id
    )

    # Save draft to conversation
    from sqlalchemy.orm.attributes import flag_modified
    conversation.prd_draft = draft
    flag_modified(conversation, "prd_draft")
    await db.commit()

    logger.info(f"Generated PRD outline for conversation {conversation_id}")

    return PRDDraftResponse(**draft)


@router.get("/{conversation_id}/draft", response_model=PRDDraftResponse)
async def get_prd_draft(
    conversation_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get current PRD draft for a conversation.

    Args:
        conversation_id: Conversation ID
        db: Database session

    Returns:
        Current PRD draft or empty draft if none exists
    """
    result = await db.execute(
        select(Conversation).where(Conversation.id == conversation_id)
    )
    conversation = result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation with id {conversation_id} not found"
        )

    draft = conversation.prd_draft
    if not draft:
        # Return empty draft
        prd_service = PRDService(GeminiService())
        draft = prd_service._create_empty_draft()

    return PRDDraftResponse(**draft)


@router.patch("/{conversation_id}/section", response_model=PRDDraftResponse)
async def update_prd_section(
    conversation_id: UUID,
    section_update: PRDSectionUpdate,
    db: AsyncSession = Depends(get_db),
    prd_service: PRDService = Depends(get_prd_service)
):
    """
    Update a specific PRD section.

    Args:
        conversation_id: Conversation ID
        section_update: Section key and new content
        db: Database session
        prd_service: PRD service

    Returns:
        Updated PRD draft
    """
    try:
        draft = await prd_service.update_section(
            db=db,
            conversation_id=conversation_id,
            section_key=section_update.section_key,
            content=section_update.content
        )

        logger.info(f"Updated section '{section_update.section_key}' for conversation {conversation_id}")

        return PRDDraftResponse(**draft)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{conversation_id}/section/{section_key}/regenerate", response_model=PRDDraftResponse)
async def regenerate_prd_section(
    conversation_id: UUID,
    section_key: str,
    db: AsyncSession = Depends(get_db),
    prd_service: PRDService = Depends(get_prd_service)
):
    """
    Regenerate a specific PRD section using AI.

    Args:
        conversation_id: Conversation ID
        section_key: Section to regenerate
        db: Database session
        prd_service: PRD service

    Returns:
        Updated PRD draft
    """
    # Get conversation to get project_id
    result = await db.execute(
        select(Conversation).where(Conversation.id == conversation_id)
    )
    conversation = result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation with id {conversation_id} not found"
        )

    try:
        draft = await prd_service.regenerate_section(
            db=db,
            conversation_id=conversation_id,
            project_id=conversation.project_id,
            section_key=section_key
        )

        logger.info(f"Regenerated section '{section_key}' for conversation {conversation_id}")

        return PRDDraftResponse(**draft)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
