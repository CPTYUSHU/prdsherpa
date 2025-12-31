"""
API endpoints for PRD export.
"""
import logging
from uuid import UUID
from urllib.parse import quote
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.database import get_db
from backend.app.schemas.export import ExportRequest, ExportResponse
from backend.app.services.export_service import ExportService
from backend.app.services.gemini_service import GeminiService

logger = logging.getLogger(__name__)

router = APIRouter()


def get_export_service() -> ExportService:
    """Dependency to get export service."""
    gemini_service = GeminiService()
    return ExportService(gemini_service)


@router.post("/conversation/{conversation_id}", response_model=ExportResponse)
async def export_conversation(
    conversation_id: UUID,
    include_knowledge_base: bool = True,
    db: AsyncSession = Depends(get_db),
    export_service: ExportService = Depends(get_export_service)
):
    """
    Export a conversation as a PRD document.
    
    Args:
        conversation_id: Conversation ID
        include_knowledge_base: Whether to include knowledge base
        db: Database session
        export_service: Export service
        
    Returns:
        Exported PRD content
    """
    try:
        content, filename = await export_service.export_conversation_to_markdown(
            db=db,
            conversation_id=conversation_id,
            include_knowledge_base=include_knowledge_base
        )
        
        logger.info(f"Exported conversation {conversation_id} as {filename}")
        
        return ExportResponse(
            content=content,
            format="markdown",
            filename=filename
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error exporting conversation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export conversation: {str(e)}"
        )


@router.get("/conversation/{conversation_id}/download")
async def download_conversation(
    conversation_id: UUID,
    format: str = 'markdown',
    include_knowledge_base: bool = True,
    db: AsyncSession = Depends(get_db),
    export_service: ExportService = Depends(get_export_service)
):
    """
    Download a conversation in various formats.

    Args:
        conversation_id: Conversation ID
        format: Export format (markdown, word, html, pdf)
        include_knowledge_base: Whether to include knowledge base
        db: Database session
        export_service: Export service

    Returns:
        File download in requested format
    """
    try:
        # 验证格式
        valid_formats = ['markdown', 'word', 'html', 'pdf']
        if format not in valid_formats:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid format. Must be one of: {', '.join(valid_formats)}"
            )

        # 导出为请求的格式
        content, filename, content_type = await export_service.export_conversation(
            db=db,
            conversation_id=conversation_id,
            format=format,
            include_knowledge_base=include_knowledge_base
        )

        logger.info(f"Downloaded conversation {conversation_id} as {filename} ({format})")

        # URL encode filename for proper handling of non-ASCII characters
        encoded_filename = quote(filename)

        # 处理字符串和字节内容
        if isinstance(content, str):
            response_content = content.encode('utf-8')
        else:
            response_content = content

        return Response(
            content=response_content,
            media_type=content_type,
            headers={
                "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}",
                "Content-Type": content_type
            }
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error downloading conversation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to download conversation: {str(e)}"
        )

