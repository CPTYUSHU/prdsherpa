"""
API endpoints for wireframe generation.
"""
import logging
from datetime import datetime, timezone
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from backend.app.core.database import get_db
from backend.app.services.wireframe_service import WireframeService
from backend.app.services.gemini_service import GeminiService
from backend.app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize services
gemini_service = GeminiService()
wireframe_service = WireframeService(gemini_service)


class WireframeGenerateRequest(BaseModel):
    """Request model for wireframe generation."""
    device_type: str = Field(
        default="mobile",
        description="Device type: mobile, tablet, or desktop"
    )
    reference_file_ids: list[str] = Field(
        default_factory=list,
        description="List of uploaded file IDs to use as UI reference (screenshots, existing designs)"
    )


class WireframeResponse(BaseModel):
    """Response model for wireframe generation."""
    html_content: str = Field(description="Complete HTML document with inline CSS")
    device_type: str = Field(description="Device type used for generation")
    created_at: str = Field(description="ISO 8601 timestamp")


@router.post(
    "/conversations/{conversation_id}/wireframe",
    response_model=WireframeResponse,
    summary="Generate wireframe from PRD conversation",
    description="Generate a low-fidelity HTML/CSS wireframe prototype from a PRD conversation"
)
async def generate_wireframe(
    conversation_id: UUID,
    request: WireframeGenerateRequest = WireframeGenerateRequest(),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate HTML/CSS wireframe from PRD conversation.

    Args:
        conversation_id: UUID of the conversation
        request: Wireframe generation request parameters
        db: Database session

    Returns:
        WireframeResponse with HTML content

    Raises:
        HTTPException: If conversation not found or generation fails
    """
    try:
        logger.info(
            f"Generating wireframe for conversation {conversation_id}, "
            f"device_type={request.device_type}"
        )

        # Validate device_type
        valid_device_types = ["mobile", "tablet", "desktop"]
        if request.device_type not in valid_device_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid device_type. Must be one of: {', '.join(valid_device_types)}"
            )

        # Generate wireframe
        html_content = await wireframe_service.generate_wireframe_html(
            db=db,
            conversation_id=conversation_id,
            device_type=request.device_type,
            reference_file_ids=request.reference_file_ids
        )

        # Return response
        return WireframeResponse(
            html_content=html_content,
            device_type=request.device_type,
            created_at=datetime.now(timezone.utc).isoformat()
        )

    except ValueError as e:
        logger.error(f"Validation error generating wireframe: {e}")
        raise HTTPException(status_code=404, detail=str(e))

    except Exception as e:
        logger.error(f"Error generating wireframe: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate wireframe: {str(e)}"
        )
