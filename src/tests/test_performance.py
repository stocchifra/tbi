"""
Performance tests for the application
"""
import pytest
import time
import asyncio
from httpx import AsyncClient
from unittest.mock import patch
import json

pytestmark = pytest.mark.asyncio


class TestPerformanceRequirements:
    """Test performance requirements (p95 latency <3 seconds)"""
    
    @pytest.mark.asyncio
    async def test_chat_response_latency(self, client: AsyncClient):
        """Test that chat responses are under 3 seconds (p95)"""
        # Create session and upload document
        session_response = await client.post("/sessions/")
        session_id = session_response.json()["session_id"]
        
        document_data = {
            "content": "This is a test document for performance testing. " * 50,
            "filename": "performance_test.txt"
        }
        await client.post(
            f"/sessions/{session_id}/documents/upload-text",
            json=document_data
        )
        
        # Measure response times for multiple requests
        response_times = []
        
        with patch('src.app.services.openai_service.OpenAIService.chat_with_documents') as mock_chat:
            # Mock fast response
            async def mock_stream():
                await asyncio.sleep(0.1)  # Simulate processing time
                yield "data: " + json.dumps({"content": "Fast response"}) + "\n\n"
                yield "data: [DONE]\n\n"
            
            mock_chat.return_value = mock_stream()
            
            # Run multiple requests
            for i in range(10):
                start_time = time.time()
                
                query_data = {
                    "query": f"Test query {i}",
                    "api_key": "test_api_key"
                }
                
                response = await client.post(
                    f"/sessions/{session_id}/chat",
                    json=query_data
                )
                
                # Read the streaming response
                async for chunk in response.aiter_text():
                    if "[DONE]" in chunk:
                        break
                
                end_time = time.time()
                response_times.append(end_time - start_time)
        
        # Calculate p95 latency
        response_times.sort()
        p95_index = int(0.95 * len(response_times))
        p95_latency = response_times[p95_index]
        
        # Assert p95 latency is under 3 seconds
        assert p95_latency < 3.0, f"P95 latency {p95_latency:.2f}s exceeds 3s requirement"
        
        # Also check average latency
        avg_latency = sum(response_times) / len(response_times)
        assert avg_latency < 1.0, f"Average latency {avg_latency:.2f}s should be well under 3s"
    
    @pytest.mark.asyncio
    async def test_document_upload_performance(self, client: AsyncClient):
        """Test document upload performance"""
        session_response = await client.post("/sessions/")
        session_id = session_response.json()["session_id"]
        
        # Test with different document sizes
        sizes = [1024, 10240, 102400]  # 1KB, 10KB, 100KB
        
        for size in sizes:
            start_time = time.time()
            
            document_data = {
                "content": "x" * size,
                "filename": f"test_{size}.txt"
            }
            
            response = await client.post(
                f"/sessions/{session_id}/documents/upload-text",
                json=document_data
            )
            
            end_time = time.time()
            upload_time = end_time - start_time
            
            assert response.status_code == 200
            assert upload_time < 2.0, f"Upload time {upload_time:.2f}s for {size} bytes exceeds 2s"
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self, client: AsyncClient):
        """Test handling of concurrent requests"""
        # Create session
        session_response = await client.post("/sessions/")
        session_id = session_response.json()["session_id"]
        
        # Upload document
        document_data = {
            "content": "Test document for concurrent testing",
            "filename": "concurrent_test.txt"
        }
        await client.post(
            f"/sessions/{session_id}/documents/upload-text",
            json=document_data
        )
        
        with patch('src.app.services.openai_service.OpenAIService.chat_with_documents') as mock_chat:
            async def mock_stream():
                await asyncio.sleep(0.2)  # Simulate processing
                yield "data: " + json.dumps({"content": "Concurrent response"}) + "\n\n"
                yield "data: [DONE]\n\n"
            
            mock_chat.return_value = mock_stream()
            
            # Create multiple concurrent requests
            async def make_request(query_num):
                query_data = {
                    "query": f"Concurrent query {query_num}",
                    "api_key": "test_api_key"
                }
                
                start_time = time.time()
                response = await client.post(
                    f"/sessions/{session_id}/chat",
                    json=query_data
                )
                
                # Read response
                async for chunk in response.aiter_text():
                    if "[DONE]" in chunk:
                        break
                
                end_time = time.time()
                return end_time - start_time
            
            # Run 5 concurrent requests
            tasks = [make_request(i) for i in range(5)]
            response_times = await asyncio.gather(*tasks)
            
            # All requests should complete reasonably quickly
            for i, response_time in enumerate(response_times):
                assert response_time < 5.0, f"Concurrent request {i} took {response_time:.2f}s"


class TestStabilityRequirements:
    """Test stability requirements (100 queries)"""
    
    @pytest.mark.asyncio
    async def test_stability_100_queries(self, client: AsyncClient):
        """Test system stability over 100 queries"""
        # Create session and upload document
        session_response = await client.post("/sessions/")
        session_id = session_response.json()["session_id"]
        
        document_data = {
            "content": "Stability test document with relevant information.",
            "filename": "stability_test.txt"
        }
        await client.post(
            f"/sessions/{session_id}/documents/upload-text",
            json=document_data
        )
        
        successful_queries = 0
        failed_queries = 0
        
        with patch('src.app.services.openai_service.OpenAIService.chat_with_documents') as mock_chat:
            async def mock_stream():
                await asyncio.sleep(0.05)  # Fast mock response
                yield "data: " + json.dumps({"content": f"Response {successful_queries}"}) + "\n\n"
                yield "data: [DONE]\n\n"
            
            mock_chat.return_value = mock_stream()
            
            # Run 100 queries
            for i in range(100):
                try:
                    query_data = {
                        "query": f"Stability test query {i}",
                        "api_key": "test_api_key"
                    }
                    
                    response = await client.post(
                        f"/sessions/{session_id}/chat",
                        json=query_data
                    )
                    
                    if response.status_code == 200:
                        successful_queries += 1
                        # Read the response to ensure it completes
                        async for chunk in response.aiter_text():
                            if "[DONE]" in chunk:
                                break
                    else:
                        failed_queries += 1
                        
                except Exception as e:
                    failed_queries += 1
                    print(f"Query {i} failed: {e}")
        
        # Require at least 95% success rate
        success_rate = successful_queries / 100
        assert success_rate >= 0.95, f"Success rate {success_rate:.2%} below 95% requirement"
        
        print(f"Stability test: {successful_queries}/100 successful ({success_rate:.2%})")


class TestMemoryUsage:
    """Test memory usage and resource management"""
    
    @pytest.mark.asyncio
    async def test_memory_cleanup_after_session(self, client: AsyncClient):
        """Test that memory is properly cleaned up after sessions"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Create and use multiple sessions
        for i in range(10):
            session_response = await client.post("/sessions/")
            session_id = session_response.json()["session_id"]
            
            # Upload large document
            large_content = "Large document content. " * 1000
            document_data = {
                "content": large_content,
                "filename": f"large_doc_{i}.txt"
            }
            await client.post(
                f"/sessions/{session_id}/documents/upload-text",
                json=document_data
            )
        
        # Check memory after operations
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 100MB)
        max_increase = 100 * 1024 * 1024  # 100MB
        assert memory_increase < max_increase, f"Memory increased by {memory_increase / 1024 / 1024:.1f}MB"
