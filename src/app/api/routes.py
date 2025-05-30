"""
API routes     get_db_session, 
    ChatMessage, 
    Document, 
    APIKeyStorage,
    ChatMessageCreate,
    ChatMessageResponse,
    DocumentUpload,
    DocumentResponse,
    QueryRequest,
    QueryResponse,
    APIKeyRequest
)
from ..services.openai_service import OpenAIService
from ..services.session_service import SessionService
from ..utils.encryption import encrypt_data, decrypt_datat analysis application
"""
import asyncio
import logging
import time
from typing import Optional, List
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import select, desc

from ..models.database import (
    get_db_session, 
    ChatMessage, 
    Document, 
    APIKeyStorage,
    ChatMessageCreate,
    ChatMessageResponse,
    DocumentUpload,
    DocumentResponse,
    QueryRequest,
    QueryResponse,
    APIKeyRequest
)
from ..services.openai_service import OpenAIService, DocumentProcessor
from ..services.session_service import SessionService
from ..utils.encryption import encrypt_api_key, decrypt_api_key

logger = logging.getLogger(__name__)

router = APIRouter()

# Global session service
session_service = SessionService()


@router.post("/config/openai-key")
async def set_openai_key(
    request: APIKeyRequest,
    db: Session = Depends(get_db_session)
):
    """Set OpenAI API key for a session"""
    try:
        # Validate the API key
        openai_service = OpenAIService(request.api_key)
        is_valid = await openai_service.validate_api_key()
        
        if not is_valid:
            raise HTTPException(status_code=400, detail="Invalid OpenAI API key")
        
        # Store encrypted API key
        encrypted_key = encrypt_api_key(request.api_key)
        
        # Remove existing keys for this session
        db.execute(
            select(APIKeyStorage).where(
                APIKeyStorage.session_id == request.session_id,
                APIKeyStorage.service == "openai"
            )
        )
        
        # Store new key
        api_key_record = APIKeyStorage(
            session_id=request.session_id,
            service="openai",
            encrypted_key=encrypted_key,
            is_active=True
        )
        db.add(api_key_record)
        db.commit()
        
        return {"status": "success", "message": "OpenAI API key set successfully"}
        
    except Exception as e:
        logger.error(f"Error setting API key: {e}")
        raise HTTPException(status_code=500, detail="Failed to set API key")


@router.post("/documents/upload", response_model=DocumentResponse)
async def upload_document(
    document: DocumentUpload,
    db: Session = Depends(get_db_session)
):
    """Upload a text document"""
    try:
        # Process document
        processed_doc = DocumentProcessor.process_text_document(document.content)
        
        # Check if document already exists (by hash)
        existing_doc = db.execute(
            select(Document).where(Document.content_hash == processed_doc["content_hash"])
        )
        existing_doc = existing_doc.scalar_one_or_none()
        
        if existing_doc:
            return DocumentResponse.from_orm(existing_doc)
        
        # Create new document record
        doc_record = Document(
            session_id=document.session_id,
            filename=document.filename,
            content=processed_doc["content"],
            content_hash=processed_doc["content_hash"],
            size=processed_doc["size"]
        )
        
        db.add(doc_record)
        db.commit()
        db.refresh(doc_record)
        
        return DocumentResponse.from_orm(doc_record)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload document")


@router.post("/sessions/{session_id}/documents/upload", response_model=DocumentResponse)
async def upload_file_document(
    session_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db_session)
):
    """Upload a file document for a specific session"""
    try:
        # Validate file type
        if not file.filename.endswith('.txt'):
            raise HTTPException(status_code=400, detail="Only .txt files are supported")
        
        # Read file content
        content = await file.read()
        content_text = content.decode('utf-8')
        
        # Process document
        processed_doc = DocumentProcessor.process_text_document(content_text)
        
        # Check if document already exists for this session (by hash and session)
        existing_doc = db.execute(
            select(Document).where(
                Document.content_hash == processed_doc["content_hash"],
                Document.session_id == session_id
            )
        )
        existing_doc = existing_doc.scalar_one_or_none()
        
        if existing_doc:
            return DocumentResponse.from_orm(existing_doc)
        
        # Create new document record
        doc_record = Document(
            session_id=session_id,
            filename=file.filename,
            content=processed_doc["content"],
            content_hash=processed_doc["content_hash"],
            size=processed_doc["size"]
        )
        
        db.add(doc_record)
        db.commit()
        db.refresh(doc_record)
        
        return DocumentResponse.from_orm(doc_record)
        
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File must be valid UTF-8 text")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error uploading file document: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload file document")


@router.post("/chat/query")
async def process_query(
    request: QueryRequest,
    db: Session = Depends(get_db_session)
):
    """Process a user query with streaming response"""
    start_time = time.time()
    
    try:
        # Get API key for session
        api_key_record = db.execute(
            select(APIKeyStorage).where(
                APIKeyStorage.session_id == request.session_id,
                APIKeyStorage.service == "openai",
                APIKeyStorage.is_active == True
            ).order_by(desc(APIKeyStorage.created_at))
        )
        api_key_record = api_key_record.scalar_one_or_none()
        
        if not api_key_record:
            raise HTTPException(status_code=400, detail="OpenAI API key not set")
        
        # Decrypt API key
        api_key = decrypt_api_key(api_key_record.encrypted_key)
        openai_service = OpenAIService(api_key)
        
        # Get document content if document_id is provided
        document_content = ""
        if request.document_id:
            doc_record = db.execute(
                select(Document).where(Document.id == request.document_id)
            )
            doc_record = doc_record.scalar_one_or_none()
            if doc_record:
                document_content = doc_record.content
        
        # Get recent chat history for context (excluding the current message)
        chat_history = []
        history_result = db.execute(
            select(ChatMessage)
            .where(ChatMessage.session_id == request.session_id)
            .order_by(desc(ChatMessage.timestamp))
            .limit(20)  # Get last 20 messages for context
        )
        history_messages = history_result.scalars().all()
        
        # Convert to list format needed by OpenAI service (in chronological order)
        chat_history = [
            {
                "message_type": msg.message_type,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat()
            }
            for msg in reversed(history_messages)
        ]
        
        # Store user message
        user_message = ChatMessage(
            session_id=request.session_id,
            message_type="user",
            content=request.query,
            timestamp=datetime.utcnow()
        )
        db.add(user_message)
        db.commit()
        
        # Create streaming response
        async def generate_response():
            response_content = ""
            tokens_used = 0
            
            try:
                async for chunk in openai_service.analyze_document(
                    document_content, 
                    request.query,
                    chat_history
                ):
                    response_content += chunk
                    # Send chunk as-is - OpenAI handles proper spacing between tokens
                    yield f"data: {chunk}\n\n"
                
                # Calculate tokens and processing time
                tokens_used = await openai_service.get_response_tokens(response_content)
                processing_time = int((time.time() - start_time) * 1000)
                
                # Store assistant message
                assistant_message = ChatMessage(
                    session_id=request.session_id,
                    message_type="assistant",
                    content=response_content,
                    timestamp=datetime.utcnow(),
                    tokens_used=tokens_used,
                    processing_time=processing_time
                )
                db.add(assistant_message)
                db.commit()
                
                # Send completion signal
                yield f"data: [DONE]\n\n"
                
            except Exception as e:
                logger.error(f"Error in streaming response: {e}")
                yield f"data: ERROR: {str(e)}\n\n"
        
        return StreamingResponse(
            generate_response(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail="Failed to process query")


@router.get("/chat/history/{session_id}", response_model=List[ChatMessageResponse])
async def get_chat_history(
    session_id: str,
    limit: int = 50,
    db: Session = Depends(get_db_session)
):
    """Get chat history for a session"""
    try:
        result = db.execute(
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(desc(ChatMessage.timestamp))
            .limit(limit)
        )
        messages = result.scalars().all()
        
        # Reverse to get chronological order
        return [ChatMessageResponse.from_orm(msg) for msg in reversed(messages)]
        
    except Exception as e:
        logger.error(f"Error getting chat history: {e}")
        raise HTTPException(status_code=500, detail="Failed to get chat history")


@router.get("/documents/{session_id}", response_model=List[DocumentResponse])
async def get_documents(
    session_id: str,
    db: Session = Depends(get_db_session)
):
    """Get documents for a session"""
    try:
        result = db.execute(
            select(Document)
            .where(Document.session_id == session_id)
            .order_by(desc(Document.upload_timestamp))
        )
        documents = result.scalars().all()
        
        return [DocumentResponse.from_orm(doc) for doc in documents]
        
    except Exception as e:
        logger.error(f"Error getting documents: {e}")
        raise HTTPException(status_code=500, detail="Failed to get documents")


@router.post("/sessions/")
async def create_session():
    """Create a new session"""
    session_id = session_service.create_session()
    return {"session_id": session_id}


@router.get("/session/new")
async def create_new_session():
    """Create a new session ID"""
    session_id = session_service.create_session()
    return {"session_id": session_id}


@router.get("/health")
async def health_check():
    """API health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "AI Document Analysis API"
    }
