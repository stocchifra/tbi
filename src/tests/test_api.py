"""
Tests for API routes
"""
import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch
import json
import os

# Set environment variable for simulated API key validation
os.environ["SIMULATE_OPENAI_KEY"] = "1"

pytestmark = pytest.mark.asyncio


class TestHealthEndpoint:
    """Test health check endpoint"""
    
    @pytest.mark.asyncio
    async def test_health_check(self, client):
        """Test health check returns OK"""
        response = await client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "service" in data


class TestSessionEndpoints:
    """Test session management endpoints"""
    
    @pytest.mark.asyncio
    async def test_create_session(self, client):
        """Test session creation"""
        response = await client.get("/api/session/new")
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert len(data["session_id"]) > 0
    
    @pytest.mark.asyncio
    async def test_create_session_post(self, client):
        """Test session creation via POST"""
        response = await client.post("/api/sessions/")
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert len(data["session_id"]) > 0
    
    @pytest.mark.asyncio
    async def test_get_session_history_empty(self, client):
        """Test getting history for new session"""
        # Create session first
        session_response = await client.get("/api/session/new")
        session_id = session_response.json()["session_id"]
        
        # Get history
        response = await client.get(f"/api/chat/history/{session_id}")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0


class TestDocumentEndpoints:
    """Test document upload and management"""
    
    async def test_upload_text_document(self, client: AsyncClient):
        """Test uploading text document"""
        # Create session
        session_response = await client.post("/api/sessions/")
        session_id = session_response.json()["session_id"]
        
        # Upload document
        document_data = {
            "session_id": session_id,
            "content": "This is a test document with important information.",
            "filename": "test.txt"
        }
        
        response = await client.post(
            "/api/documents/upload",
            json=document_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["filename"] == "test.txt"
        assert data["session_id"] == session_id
    
    async def test_upload_file_document(self, client: AsyncClient):
        """Test uploading file document"""
        # Create session
        session_response = await client.post("/api/sessions/")
        session_id = session_response.json()["session_id"]
        
        # Create test file
        test_content = b"This is test file content"
        files = {"file": ("test.txt", test_content, "text/plain")}
        
        response = await client.post(
            f"/api/sessions/{session_id}/documents/upload",
            files=files
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["filename"] == "test.txt"
        assert data["session_id"] == session_id
    
    async def test_get_documents(self, client: AsyncClient):
        """Test getting documents for session"""
        # Create session
        session_response = await client.post("/api/sessions/")
        session_id = session_response.json()["session_id"]
        
        # Upload a document first
        document_data = {
            "session_id": session_id,
            "content": "Test document",
            "filename": "test.txt"
        }
        await client.post(
            "/api/documents/upload",
            json=document_data
        )
        
        # Get documents
        response = await client.get(f"/api/documents/{session_id}")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]["filename"] == "test.txt"


class TestChatEndpoints:
    """Test chat functionality"""
    
    @patch('app.services.openai_service.OpenAIService.analyze_document')
    async def test_chat_query(self, mock_analyze, client: AsyncClient):
        """Test chat query with documents"""
        # Setup mock
        async def mock_stream():
            yield "Test"
            yield " response"
            yield " from"
            yield " AI"
        
        mock_analyze.return_value = mock_stream()
        
        # Create session
        session_response = await client.post("/api/sessions/")
        session_id = session_response.json()["session_id"]
        
        # Set dummy API key
        api_key_data = {
            "session_id": session_id,
            "api_key": "dummy-test-key-for-testing"
        }
        await client.post("/api/config/openai-key", json=api_key_data)
        
        # Upload document
        document_data = {
            "session_id": session_id,
            "content": "This is a test document",
            "filename": "test.txt"
        }
        doc_response = await client.post("/api/documents/upload", json=document_data)
        document_id = doc_response.json()["id"]
        
        # Send chat query
        query_data = {
            "session_id": session_id,
            "query": "What is in the document?",
            "document_id": document_id
        }
        
        response = await client.post("/api/chat/query", json=query_data)
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/event-stream; charset=utf-8"


class TestConfigEndpoints:
    """Test configuration endpoints"""
    
    async def test_set_api_key(self, client: AsyncClient):
        """Test setting API key"""
        # Create session
        session_response = await client.post("/api/sessions/")
        session_id = session_response.json()["session_id"]
        
        # Set API key
        config_data = {
            "session_id": session_id,
            "api_key": "dummy-test-key-for-testing"
        }
        response = await client.post("/api/config/openai-key", json=config_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "API key set successfully" in data["message"]
