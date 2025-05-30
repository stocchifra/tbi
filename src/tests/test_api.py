"""
Tests for API routes
"""
import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch
import json

pytestmark = pytest.mark.asyncio


class TestHealthEndpoint:
    """Test health check endpoint"""
    
    @pytest.mark.asyncio
    async def test_health_check(self, client):
        """Test health check returns OK"""
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data


class TestSessionEndpoints:
    """Test session management endpoints"""
    
    @pytest.mark.asyncio
    async def test_create_session(self, client):
        """Test session creation"""
        response = await client.get("/session/new")
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert len(data["session_id"]) > 0
    
    @pytest.mark.asyncio
    async def test_get_session_history_empty(self, client):
        """Test getting history for new session"""
        # Create session first
        session_response = await client.get("/session/new")
        session_id = session_response.json()["session_id"]
        
        # Get history
        response = await client.get(f"/chat/history/{session_id}")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0


class TestDocumentEndpoints:
    """Test document upload and management"""
    
    async def test_upload_text_document(self, client: AsyncClient):
        """Test uploading text document"""
        # Create session
        session_response = await client.post("/sessions/")
        session_id = session_response.json()["session_id"]
        
        # Upload document
        document_data = {
            "content": "This is a test document with important information.",
            "filename": "test.txt"
        }
        
        response = await client.post(
            f"/sessions/{session_id}/documents/upload-text",
            json=document_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Document uploaded successfully"
        assert data["document_id"] is not None
    
    async def test_upload_file_document(self, client: AsyncClient):
        """Test uploading file document"""
        # Create session
        session_response = await client.post("/sessions/")
        session_id = session_response.json()["session_id"]
        
        # Create test file
        test_content = b"This is test file content"
        files = {"file": ("test.txt", test_content, "text/plain")}
        
        response = await client.post(
            f"/sessions/{session_id}/documents/upload",
            files=files
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Document uploaded successfully"
    
    async def test_get_documents(self, client: AsyncClient):
        """Test getting documents for session"""
        # Create session
        session_response = await client.post("/sessions/")
        session_id = session_response.json()["session_id"]
        
        # Upload a document first
        document_data = {
            "content": "Test document",
            "filename": "test.txt"
        }
        await client.post(
            f"/sessions/{session_id}/documents/upload-text",
            json=document_data
        )
        
        # Get documents
        response = await client.get(f"/sessions/{session_id}/documents")
        assert response.status_code == 200
        data = response.json()
        assert len(data["documents"]) == 1
        assert data["documents"][0]["filename"] == "test.txt"


class TestChatEndpoints:
    """Test chat functionality"""
    
    @patch('src.app.services.openai_service.OpenAIService.chat_with_documents')
    async def test_chat_query(self, mock_chat, client: AsyncClient, mock_openai_response):
        """Test chat query with documents"""
        # Setup mock
        async def mock_stream():
            yield "data: " + json.dumps({"content": "Test response"}) + "\n\n"
            yield "data: [DONE]\n\n"
        
        mock_chat.return_value = mock_stream()
        
        # Create session and upload document
        session_response = await client.post("/sessions/")
        session_id = session_response.json()["session_id"]
        
        document_data = {
            "content": "This is a test document",
            "filename": "test.txt"
        }
        await client.post(
            f"/sessions/{session_id}/documents/upload-text",
            json=document_data
        )
        
        # Send chat query
        query_data = {
            "query": "What is in the document?",
            "api_key": "test_api_key"
        }
        
        response = await client.post(
            f"/sessions/{session_id}/chat",
            json=query_data
        )
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/event-stream; charset=utf-8"


class TestConfigEndpoints:
    """Test configuration endpoints"""
    
    async def test_set_api_key(self, client: AsyncClient):
        """Test setting API key"""
        # Create session
        session_response = await client.post("/sessions/")
        session_id = session_response.json()["session_id"]
        
        # Set API key
        config_data = {"api_key": "test_api_key"}
        response = await client.post(
            f"/sessions/{session_id}/config/api-key",
            json=config_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "API key set successfully"
    
    async def test_get_config(self, client: AsyncClient):
        """Test getting configuration"""
        # Create session
        session_response = await client.post("/sessions/")
        session_id = session_response.json()["session_id"]
        
        # Get config
        response = await client.get(f"/sessions/{session_id}/config")
        assert response.status_code == 200
        data = response.json()
        assert "has_api_key" in data
        assert "model" in data
