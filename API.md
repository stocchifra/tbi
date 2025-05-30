# API Documentation

## Overview

The AI Document Analysis API provides endpoints for document upload, analysis, and AI-powered querying. All responses follow RESTful conventions with JSON payloads.

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://your-domain.com`

## Authentication

This prototype uses session-based API key management. OpenAI API keys are stored encrypted per session.

## Error Handling

All endpoints return consistent error responses:

```json
{
  "detail": "Error description",
  "error_code": "ERROR_TYPE",
  "timestamp": "2025-05-30T10:30:00Z"
}
```

### Common HTTP Status Codes

- `200` - Success
- `400` - Bad Request (validation error)
- `404` - Not Found (session/document not found)
- `422` - Unprocessable Entity (invalid data)
- `500` - Internal Server Error

## Endpoints

### Health Check

Check API health and status.

```http
GET /health
```

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2025-05-30T10:30:00Z",
  "version": "1.0.0"
}
```

### Session Management

#### Create Session

Create a new chat session.

```http
POST /sessions/
```

**Response**:
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2025-05-30T10:30:00Z"
}
```

#### Get Session History

Retrieve chat history for a session.

```http
GET /sessions/{session_id}/history
```

**Parameters**:
- `session_id` (path): Session UUID
- `limit` (query, optional): Maximum messages to return (default: 50)
- `offset` (query, optional): Number of messages to skip (default: 0)

**Response**:
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "messages": [
    {
      "id": 1,
      "role": "user",
      "content": "What is in the document?",
      "timestamp": "2025-05-30T10:30:00Z"
    },
    {
      "id": 2,
      "role": "assistant",
      "content": "The document contains...",
      "timestamp": "2025-05-30T10:30:01Z",
      "token_usage": {
        "prompt_tokens": 150,
        "completion_tokens": 200,
        "total_tokens": 350
      }
    }
  ],
  "total_count": 2
}
```

### Document Management

#### Upload File

Upload a document file for analysis.

```http
POST /sessions/{session_id}/documents/upload
Content-Type: multipart/form-data
```

**Parameters**:
- `session_id` (path): Session UUID
- `file` (form): Document file (max 1MB)

**Response**:
```json
{
  "message": "Document uploaded successfully",
  "document_id": "doc_123456",
  "filename": "document.txt",
  "size_bytes": 1024,
  "content_hash": "sha256_hash"
}
```

#### Upload Text

Upload text content directly.

```http
POST /sessions/{session_id}/documents/upload-text
Content-Type: application/json
```

**Request Body**:
```json
{
  "content": "Document text content...",
  "filename": "document.txt"
}
```

**Response**:
```json
{
  "message": "Document uploaded successfully",
  "document_id": "doc_123456",
  "filename": "document.txt",
  "size_bytes": 1024,
  "content_hash": "sha256_hash"
}
```

#### List Documents

Get all documents in a session.

```http
GET /sessions/{session_id}/documents
```

**Response**:
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "documents": [
    {
      "id": "doc_123456",
      "filename": "document.txt",
      "size_bytes": 1024,
      "uploaded_at": "2025-05-30T10:30:00Z",
      "content_hash": "sha256_hash"
    }
  ],
  "total_count": 1
}
```

### Chat and Querying

#### Send Chat Query

Send a query about uploaded documents with streaming response.

```http
POST /sessions/{session_id}/chat
Content-Type: application/json
```

**Request Body**:
```json
{
  "query": "What are the key points in the document?",
  "api_key": "sk-...",
  "model": "gpt-4o-mini",
  "temperature": 0.7,
  "max_tokens": 1000
}
```

**Response**: Server-Sent Events (SSE)
```
Content-Type: text/event-stream

data: {"type": "start", "message_id": "msg_123"}

data: {"type": "content", "content": "The document contains"}

data: {"type": "content", "content": " several key points:"}

data: {"type": "content", "content": "\n1. Important topic A"}

data: {"type": "end", "token_usage": {"prompt_tokens": 150, "completion_tokens": 200, "total_tokens": 350}}

data: [DONE]
```

### Configuration

#### Set API Key

Store OpenAI API key for the session (encrypted).

```http
POST /sessions/{session_id}/config/api-key
Content-Type: application/json
```

**Request Body**:
```json
{
  "api_key": "sk-..."
}
```

**Response**:
```json
{
  "message": "API key set successfully"
}
```

#### Get Configuration

Get current session configuration.

```http
GET /sessions/{session_id}/config
```

**Response**:
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "has_api_key": true,
  "model": "gpt-4o-mini",
  "temperature": 0.7,
  "max_tokens": 1000,
  "document_count": 2
}
```

## Rate Limiting

- **Rate**: 10 requests per minute per session
- **Headers**: 
  - `X-RateLimit-Limit`: Request limit
  - `X-RateLimit-Remaining`: Remaining requests
  - `X-RateLimit-Reset`: Reset timestamp

When rate limit is exceeded:
```json
{
  "detail": "Rate limit exceeded",
  "error_code": "RATE_LIMIT_EXCEEDED",
  "retry_after": 60
}
```

## Request/Response Examples

### Complete Workflow Example

1. **Create Session**:
```bash
curl -X POST http://localhost:8000/sessions/
```

2. **Upload Document**:
```bash
curl -X POST \
  -F "file=@document.txt" \
  http://localhost:8000/sessions/{session_id}/documents/upload
```

3. **Set API Key**:
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"api_key": "sk-..."}' \
  http://localhost:8000/sessions/{session_id}/config/api-key
```

4. **Query Document**:
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"query": "Summarize the document", "api_key": "sk-..."}' \
  http://localhost:8000/sessions/{session_id}/chat
```

### JavaScript/TypeScript Examples

#### Using Fetch API

```typescript
// Create session
const sessionResponse = await fetch('/sessions/', {
  method: 'POST'
});
const { session_id } = await sessionResponse.json();

// Upload document
const formData = new FormData();
formData.append('file', file);

await fetch(`/sessions/${session_id}/documents/upload`, {
  method: 'POST',
  body: formData
});

// Query with streaming
const response = await fetch(`/sessions/${session_id}/chat`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    query: 'What is in the document?',
    api_key: 'sk-...'
  })
});

// Handle streaming response
const reader = response.body?.getReader();
while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  
  const chunk = new TextDecoder().decode(value);
  const lines = chunk.split('\n');
  
  for (const line of lines) {
    if (line.startsWith('data: ') && line !== 'data: [DONE]') {
      const data = JSON.parse(line.slice(6));
      console.log(data.content);
    }
  }
}
```

#### Using EventSource for Streaming

```typescript
const eventSource = new EventSource(
  `/sessions/${session_id}/chat?query=${encodeURIComponent(query)}&api_key=${apiKey}`
);

eventSource.onmessage = (event) => {
  if (event.data === '[DONE]') {
    eventSource.close();
    return;
  }
  
  const data = JSON.parse(event.data);
  if (data.type === 'content') {
    console.log(data.content);
  }
};
```

## Performance Considerations

### Response Times
- **Health check**: <100ms
- **Session creation**: <200ms
- **Document upload**: <2s (depends on size)
- **Chat queries**: <3s (p95 latency)

### Optimization Tips
1. **Batch operations** when possible
2. **Reuse sessions** for multiple queries
3. **Monitor token usage** to control costs
4. **Use appropriate model** for your use case
5. **Implement client-side caching**

## Error Handling Best Practices

### Retry Logic
```typescript
async function retryRequest(fn: () => Promise<Response>, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      const response = await fn();
      if (response.ok) return response;
      if (response.status >= 400 && response.status < 500) {
        throw new Error('Client error - do not retry');
      }
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      await new Promise(resolve => setTimeout(resolve, 1000 * Math.pow(2, i)));
    }
  }
}
```

### Graceful Degradation
```typescript
try {
  const response = await queryDocument(query);
  return response;
} catch (error) {
  if (error.code === 'RATE_LIMIT_EXCEEDED') {
    // Show rate limit message
    return { error: 'Please wait before sending another query' };
  } else if (error.code === 'API_KEY_INVALID') {
    // Prompt for new API key
    return { error: 'Please check your OpenAI API key' };
  } else {
    // Generic error handling
    return { error: 'Something went wrong. Please try again.' };
  }
}
```

## WebSocket Alternative

For applications requiring full duplex communication, consider implementing WebSocket endpoints:

```typescript
// Future enhancement - not currently implemented
const ws = new WebSocket(`ws://localhost:8000/sessions/${session_id}/ws`);

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  handleStreamingResponse(data);
};

ws.send(JSON.stringify({
  type: 'query',
  content: 'What is in the document?'
}));
```
