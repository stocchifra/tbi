"""
OpenAI service for document analysis and chat
"""
import asyncio
import hashlib
import logging
from typing import AsyncGenerator, Optional, Dict, Any
from datetime import datetime
import json
import os

import openai
from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from ..utils.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class OpenAIService:
    """Service for interacting with OpenAI API"""
    
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = settings.openai_model
        
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((openai.RateLimitError, openai.APITimeoutError))
    )
    async def analyze_document(
        self, 
        document_content: str, 
        query: str,
        chat_history: Optional[list] = None,
        max_tokens: Optional[int] = None
    ) -> AsyncGenerator[str, None]:
        """
        Analyze document with streaming response
        """
        # Check if we're in simulation mode
        if os.getenv("SIMULATE_OPENAI_KEY") == "1":
            # Simulate streaming response for testing
            async for chunk in self._simulate_response(document_content, query):
                yield chunk
            return
            
        max_tokens = max_tokens or settings.openai_max_tokens
        
        # Create system prompt for document analysis
        system_prompt = self._create_analysis_prompt()
        
        # Build messages array with conversation history
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add document context if available
        if document_content:
            document_prompt = f"Document content:\n```\n{document_content[:8000]}\n```\n\nPlease use this document to answer questions."
            messages.append({"role": "system", "content": document_prompt})
        
        # Add recent chat history for context
        if chat_history:
            for msg in chat_history[-10:]:  # Include last 10 messages for context
                role = "user" if msg["message_type"] == "user" else "assistant"
                messages.append({"role": role, "content": msg["content"]})
        
        # Add current user query
        messages.append({"role": "user", "content": query})
        
        try:
            # Create streaming chat completion
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=settings.openai_temperature,
                stream=True
            )
            
            # Yield streaming response
            async for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
                    
        except openai.RateLimitError as e:
            logger.error(f"Rate limit exceeded: {e}")
            raise
        except openai.APITimeoutError as e:
            logger.error(f"API timeout: {e}")
            raise
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise

    async def _simulate_response(self, document_content: str, query: str) -> AsyncGenerator[str, None]:
        """Simulate OpenAI response for testing without real API key"""
        # Create a simulated response based on the query and document
        if document_content:
            response = f"Based on the document you provided, I can see that it contains information about: {document_content[:100]}... "
        else:
            response = "I'd be happy to help you with your query. "
        
        response += f"Regarding your question '{query}', this is a simulated response for testing purposes. "
        response += "In production with a real OpenAI API key, I would provide detailed analysis based on your document content."
        
        # Simulate streaming by yielding chunks
        words = response.split()
        for i in range(0, len(words), 3):  # Yield 3 words at a time
            chunk = " ".join(words[i:i+3]) + " "
            yield chunk
            await asyncio.sleep(0.1)  # Small delay to simulate streaming
    
    async def get_response_tokens(self, content: str) -> int:
        """Estimate token count for response"""
        # Rough estimation: 1 token ≈ 4 characters for English text
        return len(content) // 4
    
    def _create_analysis_prompt(self) -> str:
        """Create system prompt for document analysis"""
        return """You are an AI assistant specialized in document analysis and conversational Q&A. 
        
        Your capabilities:
        - Analyze documents and extract key insights
        - Answer questions about document content
        - Maintain conversation context and remember previous exchanges
        - Provide clear, well-structured responses
        
        Guidelines:
        - Use the provided document as your primary source of information
        - Reference previous conversation when relevant
        - If information is not available in the document, clearly state this
        - Be conversational and helpful while staying accurate
        - Use proper formatting with bullet points or numbered lists when appropriate
        
        Always base your responses primarily on the provided document content, while maintaining conversation flow."""
    
    def _create_user_prompt(self, document_content: str, query: str) -> str:
        """Create user prompt combining document and query"""
        # Truncate document if too long (simple chunking strategy)
        max_doc_length = 8000  # Leave room for query and system prompt
        if len(document_content) > max_doc_length:
            document_content = document_content[:max_doc_length] + "\n...[Document truncated]"
        
        return f"""Document content:
```
{document_content}
```

User question: {query}

Please analyze the document and answer the question based on the content provided."""

    async def validate_api_key(self) -> bool:
        """Validate the OpenAI API key"""
        if os.getenv("SIMULATE_OPENAI_KEY") == "1":
            # Simulate always valid in test mode
            return True
        try:
            # Make a simple API call to validate the key
            await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Test"}],
                max_tokens=1
            )
            return True
        except openai.AuthenticationError:
            return False
        except Exception as e:
            logger.error(f"API key validation error: {e}")
            return False


class DocumentProcessor:
    """Service for processing documents"""
    
    @staticmethod
    def process_text_document(content: str) -> Dict[str, Any]:
        """Process and validate text document"""
        # Validate UTF-8 encoding
        try:
            content.encode('utf-8')
        except UnicodeEncodeError:
            raise ValueError("Document must be UTF-8 encoded")
        
        # Check size limits
        if len(content.encode('utf-8')) > settings.max_document_size:
            raise ValueError(f"Document too large. Maximum size: {settings.max_document_size} bytes")
        
        # Generate content hash for deduplication
        content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
        
        # Basic document stats
        word_count = len(content.split())
        char_count = len(content)
        
        return {
            "content": content,
            "content_hash": content_hash,
            "word_count": word_count,
            "char_count": char_count,
            "size": len(content.encode('utf-8'))
        }
    
    @staticmethod
    def chunk_document(content: str, chunk_size: int = None) -> list:
        """Split document into chunks for processing"""
        chunk_size = chunk_size or settings.max_chunk_size
        
        # Simple sentence-based chunking
        sentences = content.split('. ')
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) < chunk_size:
                current_chunk += sentence + ". "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + ". "
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
