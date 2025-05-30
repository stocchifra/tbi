"""
Database models and schemas
"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel

from ..utils.config import get_settings

settings = get_settings()

# SQLAlchemy Base
Base = declarative_base()

# Database engine
engine = create_engine(
    settings.database_url,
    echo=settings.debug
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class ChatMessage(Base):
    """Chat message model"""
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(50), index=True, nullable=False)
    message_type = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    tokens_used = Column(Integer, default=0)
    processing_time = Column(Integer, default=0)  # milliseconds


class Document(Base):
    """Document model"""
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(50), index=True, nullable=False)
    filename = Column(String(255), nullable=True)
    content = Column(Text, nullable=False)
    content_hash = Column(String(64), index=True)
    upload_timestamp = Column(DateTime, default=datetime.utcnow)
    size = Column(Integer, nullable=False)


class APIKeyStorage(Base):
    """API key storage (encrypted)"""
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(50), index=True, nullable=False)
    service = Column(String(50), nullable=False)  # 'openai'
    encrypted_key = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)


# Pydantic schemas
class ChatMessageCreate(BaseModel):
    session_id: str
    message_type: str
    content: str


class ChatMessageResponse(BaseModel):
    id: int
    session_id: str
    message_type: str
    content: str
    timestamp: datetime
    tokens_used: int
    processing_time: int
    
    class Config:
        from_attributes = True


class DocumentUpload(BaseModel):
    filename: Optional[str] = None
    content: str
    session_id: str


class DocumentResponse(BaseModel):
    id: int
    session_id: str
    filename: Optional[str]
    size: int
    upload_timestamp: datetime
    
    class Config:
        from_attributes = True


class QueryRequest(BaseModel):
    query: str
    session_id: str
    document_id: Optional[int] = None


class QueryResponse(BaseModel):
    response: str
    session_id: str
    tokens_used: int
    processing_time: int


class APIKeyRequest(BaseModel):
    api_key: str
    session_id: str


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)


def get_db_session():
    """Get database session"""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
