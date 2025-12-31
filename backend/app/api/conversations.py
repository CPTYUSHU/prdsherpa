"""
API endpoints for conversation management.
"""
import logging
import json
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from backend.app.core.database import get_db
from backend.app.models.conversation import Conversation, Message
from backend.app.models.project import Project
from backend.app.schemas.conversation import (
    ConversationCreate,
    ConversationResponse,
    ConversationDetailResponse,
    ConversationListResponse,
    MessageResponse,
    ChatRequest,
    ChatResponse,
    ConversationStatusUpdate,
    ConversationTitleUpdate,
)
from backend.app.services.conversation_service import ConversationService
from backend.app.services.gemini_service import GeminiService

logger = logging.getLogger(__name__)

router = APIRouter()


def get_conversation_service() -> ConversationService:
    """Dependency to get conversation service."""
    gemini_service = GeminiService()
    return ConversationService(gemini_service)


@router.post("/", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    conversation: ConversationCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new conversation for a project.
    
    Args:
        conversation: Conversation creation data
        db: Database session
        
    Returns:
        Created conversation
    """
    # Verify project exists
    result = await db.execute(
        select(Project).where(Project.id == conversation.project_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {conversation.project_id} not found"
        )
    
    # Create conversation
    db_conversation = Conversation(
        project_id=conversation.project_id,
        title=conversation.title
    )
    db.add(db_conversation)
    await db.commit()
    await db.refresh(db_conversation)
    
    logger.info(f"Created conversation {db_conversation.id} for project {conversation.project_id}")
    
    return ConversationResponse(
        id=db_conversation.id,
        project_id=db_conversation.project_id,
        title=db_conversation.title,
        status=db_conversation.status,
        requirement_summary=db_conversation.requirement_summary,
        message_count=0,
        created_at=db_conversation.created_at,
        updated_at=db_conversation.updated_at
    )


@router.get("/project/{project_id}", response_model=ConversationListResponse)
async def list_project_conversations(
    project_id: UUID,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """
    List all conversations for a project.
    
    Args:
        project_id: Project ID
        skip: Number of conversations to skip
        limit: Maximum number of conversations to return
        db: Database session
        
    Returns:
        List of conversations
    """
    # Get conversations with message count
    result = await db.execute(
        select(
            Conversation,
            func.count(Message.id).label("message_count")
        )
        .outerjoin(Message)
        .where(Conversation.project_id == project_id)
        .group_by(Conversation.id)
        .order_by(desc(Conversation.updated_at))
        .offset(skip)
        .limit(limit)
    )
    conversations_with_count = result.all()
    
    # Get total count
    total_result = await db.execute(
        select(func.count(Conversation.id))
        .where(Conversation.project_id == project_id)
    )
    total = total_result.scalar()
    
    conversation_list = [
        ConversationResponse(
            id=conv.id,
            project_id=conv.project_id,
            title=conv.title,
            status=conv.status,
            requirement_summary=conv.requirement_summary,
            message_count=msg_count,
            created_at=conv.created_at,
            updated_at=conv.updated_at
        )
        for conv, msg_count in conversations_with_count
    ]
    
    return ConversationListResponse(
        conversations=conversation_list,
        total=total
    )


@router.get("/{conversation_id}", response_model=ConversationDetailResponse)
async def get_conversation(
    conversation_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a conversation with all its messages.
    
    Args:
        conversation_id: Conversation ID
        db: Database session
        
    Returns:
        Conversation with messages
    """
    # Get conversation
    result = await db.execute(
        select(Conversation).where(Conversation.id == conversation_id)
    )
    conversation = result.scalar_one_or_none()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation with id {conversation_id} not found"
        )
    
    # Get messages
    messages_result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
    )
    messages = messages_result.scalars().all()
    
    return ConversationDetailResponse(
        id=conversation.id,
        project_id=conversation.project_id,
        title=conversation.title,
        status=conversation.status,
        requirement_summary=conversation.requirement_summary,
        messages=[MessageResponse.model_validate(msg) for msg in messages],
        created_at=conversation.created_at,
        updated_at=conversation.updated_at
    )


@router.post("/{conversation_id}/chat", response_model=ChatResponse)
async def chat(
    conversation_id: UUID,
    chat_request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    conv_service: ConversationService = Depends(get_conversation_service)
):
    """
    Send a message and get AI response.
    
    Args:
        conversation_id: Conversation ID
        chat_request: Chat request with user message
        db: Database session
        conv_service: Conversation service
        
    Returns:
        User message and AI response
    """
    # Get conversation
    result = await db.execute(
        select(Conversation).where(Conversation.id == conversation_id)
    )
    conversation = result.scalar_one_or_none()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation with id {conversation_id} not found"
        )
    
    # Get next sequence number
    seq_result = await db.execute(
        select(func.coalesce(func.max(Message.sequence), 0) + 1)
        .where(Message.conversation_id == conversation_id)
    )
    next_sequence = seq_result.scalar()
    
    # Save user message
    user_message = Message(
        conversation_id=conversation_id,
        role="user",
        content=chat_request.message,
        sequence=next_sequence
    )
    db.add(user_message)
    await db.flush()
    
    # Generate title if this is the first message
    if not conversation.title:
        title = await conv_service.generate_conversation_title(chat_request.message)
        conversation.title = title
    
    # Get image file paths if provided
    image_paths = None
    if chat_request.image_file_ids:
        from backend.app.models.file import UploadedFile
        image_paths = []
        for file_id in chat_request.image_file_ids:
            file_result = await db.execute(
                select(UploadedFile).where(UploadedFile.id == file_id)
            )
            uploaded_file = file_result.scalar_one_or_none()
            if uploaded_file and uploaded_file.file_path:
                image_paths.append(uploaded_file.file_path)
                logger.info(f"Including image in chat: {uploaded_file.filename}")
    
    # Generate AI response with optional images
    ai_response_text = await conv_service.generate_ai_response(
        db=db,
        project_id=conversation.project_id,
        conversation_id=conversation_id,
        user_message=chat_request.message,
        image_paths=image_paths
    )
    
    # Save AI message
    ai_message = Message(
        conversation_id=conversation_id,
        role="assistant",
        content=ai_response_text,
        sequence=next_sequence + 1
    )
    db.add(ai_message)
    
    # Update conversation timestamp
    await db.execute(
        select(Conversation).where(Conversation.id == conversation_id)
    )
    
    await db.commit()
    await db.refresh(user_message)
    await db.refresh(ai_message)
    
    logger.info(f"Chat exchange completed for conversation {conversation_id}")
    
    return ChatResponse(
        user_message=MessageResponse.model_validate(user_message),
        assistant_message=MessageResponse.model_validate(ai_message),
        conversation_id=conversation_id
    )


@router.post("/{conversation_id}/chat-stream")
async def chat_stream(
    conversation_id: UUID,
    chat_request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    conv_service: ConversationService = Depends(get_conversation_service)
):
    """
    Send a message and get AI response with streaming.
    Returns Server-Sent Events (SSE) stream.

    Args:
        conversation_id: Conversation ID
        chat_request: Chat request with user message
        db: Database session
        conv_service: Conversation service

    Returns:
        StreamingResponse with SSE events
    """
    # Get conversation
    result = await db.execute(
        select(Conversation).where(Conversation.id == conversation_id)
    )
    conversation = result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation with id {conversation_id} not found"
        )

    # Get next sequence number
    seq_result = await db.execute(
        select(func.coalesce(func.max(Message.sequence), 0) + 1)
        .where(Message.conversation_id == conversation_id)
    )
    next_sequence = seq_result.scalar()

    # Save user message
    user_message = Message(
        conversation_id=conversation_id,
        role="user",
        content=chat_request.message,
        sequence=next_sequence
    )
    db.add(user_message)
    await db.flush()
    await db.refresh(user_message)

    # Generate title if this is the first message
    if not conversation.title:
        title = await conv_service.generate_conversation_title(chat_request.message)
        conversation.title = title

    # Get image file paths if provided
    image_paths = None
    if chat_request.image_file_ids:
        from backend.app.models.file import UploadedFile
        image_paths = []
        for file_id in chat_request.image_file_ids:
            file_result = await db.execute(
                select(UploadedFile).where(UploadedFile.id == file_id)
            )
            uploaded_file = file_result.scalar_one_or_none()
            if uploaded_file and uploaded_file.file_path:
                image_paths.append(uploaded_file.file_path)
                logger.info(f"Including image in chat stream: {uploaded_file.filename}")

    # Commit user message
    await db.commit()

    # Stream AI response
    async def generate_stream():
        """Generate SSE stream."""
        try:
            # Send user message event
            user_msg_data = {
                "id": str(user_message.id),
                "conversation_id": str(user_message.conversation_id),
                "role": user_message.role,
                "content": user_message.content,
                "sequence": user_message.sequence,
                "created_at": user_message.created_at.isoformat()
            }
            yield f"event: user_message\ndata: {json.dumps(user_msg_data)}\n\n"

            # Accumulate AI response
            ai_response_text = ""

            # Stream AI response chunks
            async for chunk in conv_service.generate_ai_response_stream(
                db=db,
                project_id=conversation.project_id,
                conversation_id=conversation_id,
                user_message=chat_request.message,
                image_paths=image_paths
            ):
                ai_response_text += chunk
                # Send chunk event
                yield f"event: chunk\ndata: {json.dumps({'text': chunk})}\n\n"

            # Save complete AI message to database
            ai_message = Message(
                conversation_id=conversation_id,
                role="assistant",
                content=ai_response_text,
                sequence=next_sequence + 1
            )
            db.add(ai_message)
            await db.commit()
            await db.refresh(ai_message)

            # Send complete message event
            ai_msg_data = {
                "id": str(ai_message.id),
                "conversation_id": str(ai_message.conversation_id),
                "role": ai_message.role,
                "content": ai_message.content,
                "sequence": ai_message.sequence,
                "created_at": ai_message.created_at.isoformat()
            }
            yield f"event: assistant_message\ndata: {json.dumps(ai_msg_data)}\n\n"

            # Send done event
            yield f"event: done\ndata: {json.dumps({'conversation_id': str(conversation_id)})}\n\n"

            logger.info(f"Streaming chat completed for conversation {conversation_id}")

        except Exception as e:
            logger.error(f"Error in chat stream: {e}")
            error_data = {"error": str(e)}
            yield f"event: error\ndata: {json.dumps(error_data)}\n\n"

    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        }
    )


@router.patch("/{conversation_id}/title", response_model=ConversationResponse)
async def update_conversation_title(
    conversation_id: UUID,
    title_update: ConversationTitleUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update conversation title.

    Args:
        conversation_id: Conversation ID
        title: New title
        db: Database session

    Returns:
        Updated conversation
    """
    # Get conversation
    result = await db.execute(
        select(Conversation).where(Conversation.id == conversation_id)
    )
    conversation = result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation with id {conversation_id} not found"
        )

    # Update title
    conversation.title = title_update.title
    await db.commit()
    await db.refresh(conversation)

    # Get message count
    count_result = await db.execute(
        select(func.count(Message.id)).where(Message.conversation_id == conversation_id)
    )
    message_count = count_result.scalar()

    logger.info(f"Updated conversation {conversation_id} title to: {title_update.title}")

    return ConversationResponse(
        id=conversation.id,
        project_id=conversation.project_id,
        title=conversation.title,
        status=conversation.status,
        requirement_summary=conversation.requirement_summary,
        message_count=message_count,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at
    )


@router.patch("/{conversation_id}/status", response_model=ConversationResponse)
async def update_conversation_status(
    conversation_id: UUID,
    status_update: ConversationStatusUpdate,
    db: AsyncSession = Depends(get_db),
    conv_service: ConversationService = Depends(get_conversation_service)
):
    """
    Update conversation status (active, completed, archived).
    When marking as completed, optionally generates a requirement summary.

    Args:
        conversation_id: Conversation ID
        status_update: Status update data
        db: Database session
        conv_service: Conversation service

    Returns:
        Updated conversation
    """
    # Get conversation
    result = await db.execute(
        select(Conversation).where(Conversation.id == conversation_id)
    )
    conversation = result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation with id {conversation_id} not found"
        )

    # Update status
    conversation.status = status_update.status

    # Generate requirement summary if marking as completed
    if status_update.status == "completed" and status_update.generate_summary:
        requirement_summary = await conv_service.generate_requirement_summary(
            db=db,
            conversation_id=conversation_id
        )
        conversation.requirement_summary = requirement_summary

        # Archive to knowledge base
        await conv_service.archive_requirement_to_knowledge_base(
            db=db,
            project_id=conversation.project_id,
            conversation_id=conversation_id,
            requirement_summary=requirement_summary
        )

        # Evolve knowledge base structure
        from backend.app.services.knowledge_evolution_service import KnowledgeEvolutionService
        gemini_service = GeminiService()
        evolution_service = KnowledgeEvolutionService(gemini_service)
        await evolution_service.evolve_knowledge_base(
            db=db,
            project_id=conversation.project_id,
            completed_conversation_id=conversation_id,
            requirement_summary=requirement_summary
        )

    await db.commit()
    await db.refresh(conversation)

    # Get message count
    count_result = await db.execute(
        select(func.count(Message.id)).where(Message.conversation_id == conversation_id)
    )
    message_count = count_result.scalar()

    logger.info(f"Updated conversation {conversation_id} status to {status_update.status}")

    return ConversationResponse(
        id=conversation.id,
        project_id=conversation.project_id,
        title=conversation.title,
        status=conversation.status,
        requirement_summary=conversation.requirement_summary,
        message_count=message_count,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at
    )


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a conversation and all its messages.

    Args:
        conversation_id: Conversation ID
        db: Database session
    """
    # Get conversation
    result = await db.execute(
        select(Conversation).where(Conversation.id == conversation_id)
    )
    conversation = result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation with id {conversation_id} not found"
        )

    # Delete messages (cascade should handle this, but being explicit)
    await db.execute(
        select(Message).where(Message.conversation_id == conversation_id)
    )

    # Delete conversation
    await db.delete(conversation)
    await db.commit()

    logger.info(f"Deleted conversation {conversation_id}")

