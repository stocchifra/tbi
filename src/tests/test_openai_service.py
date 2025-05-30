"""
Tests for OpenAI service
"""
import pytest
import sys
import os
from unittest.mock import AsyncMock, patch, MagicMock
import json

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.openai_service import OpenAIService

pytestmark = pytest.mark.asyncio


class TestOpenAIService:
    """Test OpenAI service functionality"""
    
    @pytest.fixture
    def openai_service(self):
        """Create OpenAI service instance"""
        return OpenAIService()
    
    @patch('openai.AsyncOpenAI')
    async def test_chat_with_documents_success(self, mock_openai_client, openai_service):
        """Test successful chat with documents"""
        # Setup mock client
        mock_client_instance = AsyncMock()
        mock_openai_client.return_value = mock_client_instance
        
        # Mock streaming response
        mock_chunk = MagicMock()
        mock_chunk.choices = [MagicMock()]
        mock_chunk.choices[0].delta = MagicMock()
        mock_chunk.choices[0].delta.content = "Test response"
        
        mock_stream = AsyncMock()
        mock_stream.__aiter__.return_value = [mock_chunk]
        
        mock_client_instance.chat.completions.create.return_value = mock_stream
        
        # Test documents
        documents = [
            {"content": "Document 1 content", "filename": "doc1.txt"},
            {"content": "Document 2 content", "filename": "doc2.txt"}
        ]
        
        # Execute
        result_stream = openai_service.chat_with_documents(
            query="What is in the documents?",
            documents=documents,
            api_key="test_api_key"
        )
        
        # Collect results
        results = []
        async for chunk in result_stream:
            results.append(chunk)
        
        # Verify
        assert len(results) > 0
        assert any("Test response" in result for result in results)
    
    @patch('openai.AsyncOpenAI')
    async def test_chat_with_documents_api_error(self, mock_openai_client, openai_service):
        """Test handling of OpenAI API errors"""
        # Setup mock to raise exception
        mock_client_instance = AsyncMock()
        mock_openai_client.return_value = mock_client_instance
        mock_client_instance.chat.completions.create.side_effect = Exception("API Error")
        
        documents = [{"content": "Test document", "filename": "test.txt"}]
        
        # Execute and expect error handling
        result_stream = openai_service.chat_with_documents(
            query="Test query",
            documents=documents,
            api_key="test_api_key"
        )
        
        results = []
        async for chunk in result_stream:
            results.append(chunk)
        
        # Should have error message
        assert len(results) > 0
        assert any("error" in result.lower() for result in results)
    
    def test_prepare_context(self, openai_service):
        """Test context preparation from documents"""
        documents = [
            {"content": "Document 1 with important info", "filename": "doc1.txt"},
            {"content": "Document 2 with more data", "filename": "doc2.txt"}
        ]
        
        context = openai_service._prepare_context(documents)
        
        assert "doc1.txt" in context
        assert "doc2.txt" in context
        assert "Document 1 with important info" in context
        assert "Document 2 with more data" in context
    
    def test_estimate_tokens(self, openai_service):
        """Test token estimation"""
        text = "This is a test string with multiple words"
        estimated_tokens = openai_service._estimate_tokens(text)
        
        # Should be roughly 1 token per 4 characters
        expected_range = (len(text) // 6, len(text) // 2)
        assert expected_range[0] <= estimated_tokens <= expected_range[1]
    
    def test_chunk_documents_small(self, openai_service):
        """Test document chunking with small documents"""
        documents = [
            {"content": "Small document", "filename": "small.txt"}
        ]
        
        chunks = openai_service._chunk_documents(documents, max_tokens=1000)
        
        # Should fit in one chunk
        assert len(chunks) == 1
        assert "small.txt" in chunks[0]
    
    def test_chunk_documents_large(self, openai_service):
        """Test document chunking with large documents"""
        large_content = "This is a very long document. " * 200  # Make it large
        documents = [
            {"content": large_content, "filename": "large.txt"}
        ]
        
        chunks = openai_service._chunk_documents(documents, max_tokens=100)
        
        # Should be split into multiple chunks
        assert len(chunks) >= 1
        for chunk in chunks:
            assert len(chunk) > 0
