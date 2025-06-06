# AI Document Analysis Application

A production-ready single-container application for AI-powered document analysis and conversational querying. Built with FastAPI backend, React TypeScript frontend, and OpenAI integration, all packaged in a single Docker container for easy deployment.

## Quick Start

The application provides two main commands for deployment and testing:

### 1. Production Deployment
```bash
docker run -p 8080:8080 <image_tag>
```
**Access the application at: http://localhost:8080**

### 2. Test Execution
```bash
docker run <image_tag> python /home/src/tests/run_tests.py
```
**Runs complete test suite (24 unit, integration, and performance tests)**

## High-Level Architecture

### Single-Container Design
The application uses a sophisticated single-container architecture that combines multiple services:

```
┌─────────────────────────────────────────────────────────┐
│                    Docker Container                     │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │    Nginx    │  │   FastAPI    │  │   React      │   │
│  │ (Port 8080) │  │ (Port 8000)  │  │   Frontend   │   │
│  │             │  │              │  │   (Built)    │   │
│  └─────────────┘  └──────────────┘  └──────────────┘   │
│         │                 │                │           │
│         └─────────────────┼────────────────┘           │
│                          │                             │
│  ┌─────────────┐         │         ┌──────────────┐    │
│  │   SQLite    │         │         │ Supervisor   │    │
│  │  Database   │         │         │ (Process     │    │
│  │             │         │         │  Manager)    │    │
│  └─────────────┘         │         └──────────────┘    │
│                          │                             │
│                          ▼                             │
│                 ┌──────────────┐                       │
│                 │  OpenAI API  │                       │
│                 │ Integration  │                       │
│                 └──────────────┘                       │
└─────────────────────────────────────────────────────────┘
```

### Component Architecture

#### 1. **Nginx Reverse Proxy (Port 8080)**
- Serves React frontend static files
- Proxies API requests to FastAPI backend at `/api/*`
- Handles CORS and security headers
- Provides single entry point for the application

#### 2. **FastAPI Backend (Port 8000)**
- RESTful API with async/await for high performance
- OpenAI integration with streaming responses
- Session management and document storage
- Encrypted API key storage
- Real-time Server-Sent Events for chat streaming

#### 3. **React Frontend**
- TypeScript-based React application
- Material-UI for professional interface
- Real-time chat with streaming responses
- Document upload and management
- Connection status monitoring

#### 4. **SQLite Database**
- Lightweight, embedded database
- Session and document persistence
- Encrypted API key storage
- Chat history management

#### 5. **Supervisor Process Manager**
- Manages nginx and FastAPI processes
- Automatic restart on failure
- Centralized logging and monitoring

## Application Logic

### Core Workflow
1. **Session Creation**: Each user gets a unique session ID
2. **API Key Setup**: Users provide their OpenAI API key (encrypted and stored)
3. **Document Upload**: Support for text input or file upload
4. **AI Analysis**: Natural language queries processed through OpenAI
5. **Streaming Responses**: Real-time chat interface with live responses

### Key Features
- **Real-time Chat**: Streaming responses for immediate feedback
- **Document Context**: AI queries reference uploaded documents
- **Session Persistence**: Chat history and documents persist across sessions
- **Production Ready**: Health checks, error handling, and monitoring
- **Security**: Encrypted API key storage and CORS protection

## Repository Structure

```
tbi/
├── Dockerfile                    # Multi-stage build configuration
├── nginx-single.conf            # Nginx reverse proxy configuration
├── supervisord.conf             # Process management configuration
├── requirements.txt             # Python dependencies
├── README.md                    # This documentation
│
├── src/
│   ├── app/                     # FastAPI Backend Application
│   │   ├── main.py             # FastAPI app with CORS and routing
│   │   ├── api/
│   │   │   └── routes.py       # API endpoints and handlers
│   │   ├── models/
│   │   │   └── database.py     # SQLAlchemy models and schemas
│   │   ├── services/
│   │   │   └── openai_service.py # OpenAI integration and document processing
│   │   └── utils/
│   │       ├── config.py       # Application configuration
│   │       └── encryption.py   # API key encryption utilities
│   │
│   ├── frontend/                # React TypeScript Frontend
│   │   ├── src/
│   │   │   ├── components/     # React UI components
│   │   │   │   ├── ChatInterface.tsx
│   │   │   │   ├── DocumentUploader.tsx
│   │   │   │   ├── SettingsPanel.tsx
│   │   │   │   └── ConnectionStatus.tsx
│   │   │   ├── contexts/       # React context providers
│   │   │   │   ├── APIContext.tsx
│   │   │   │   ├── SessionContext.tsx
│   │   │   │   └── DocumentContext.tsx
│   │   │   ├── App.tsx         # Main React application
│   │   │   └── index.tsx       # React entry point
│   │   ├── package.json        # Frontend dependencies
│   │   └── tsconfig.json       # TypeScript configuration
│   │
│   └── tests/                   # Comprehensive Test Suite
│       ├── run_tests.py        # Test runner with logging
│       ├── test_api.py         # API endpoint tests
│       ├── test_openai_service.py # OpenAI service tests
│       └── test_performance.py  # Performance and stability tests
│
└── data/                        # Application data directory
    └── app.db                   # SQLite database (created at runtime)
```

## Docker Container Setup

### Building the Container
The application uses a sophisticated multi-stage Docker build:

1. **Frontend Build Stage**: Compiles React TypeScript application
2. **Backend Build Stage**: Installs Python dependencies
3. **Final Stage**: Combines everything into production container

```bash
# Build the container
docker build -t tbi-app .

# The build process:
# 1. Builds React frontend with production optimizations
# 2. Installs Python dependencies for FastAPI
# 3. Configures nginx reverse proxy
# 4. Sets up supervisor for process management
# 5. Configures test environment at /home/src/
```

### Container Configuration
The container is configured with:
- **Port 8080**: Main application access point
- **Environment Variables**: Production settings with simulation mode
- **Health Checks**: Automatic monitoring and restart
- **Volume Support**: Persistent data storage capability

## Running the Application

### Production Deployment
```bash
# Start the application
docker run -p 8080:8080 --name my-app tbi-app

# Access the application
open http://localhost:8080

# Monitor the application
docker logs -f my-app

# Stop the application
docker stop my-app
```

### Test Execution
```bash
# Run all tests (unit, integration, performance)
docker run --rm tbi-app python /home/src/tests/run_tests.py

# The test suite includes:
# - 9 API endpoint tests
# - 7 OpenAI service tests  
# - 4 performance tests
# - 4 stability and memory tests
# Total: 24 comprehensive tests
```

### Advanced Usage
```bash
# Run with custom name and environment
docker run -p 8080:8080 \
  --name production-app \
  -e SECRET_KEY=your-secret-key \
  tbi-app

# Run tests with verbose output
docker run --rm tbi-app python /home/src/tests/run_tests.py -v

# Access container for debugging
docker exec -it production-app /bin/bash
```

## Configuration Options

### Environment Variables
- `SIMULATE_OPENAI_KEY`: Set to "1" for testing without real API keys
- `SECRET_KEY`: Encryption key for API key storage
- `DATABASE_URL`: Database connection string
- `ENVIRONMENT`: Application environment (production/development)

### Production Settings
The container comes pre-configured for production with:
- Nginx optimization and security headers
- FastAPI with async/await performance
- Automatic process restart via supervisor
- Health check endpoints
- CORS properly configured

## 🧪 Testing Framework

### Test Categories
1. **API Tests** (`test_api.py`): Endpoint functionality and validation
2. **Service Tests** (`test_openai_service.py`): OpenAI integration and document processing  
3. **Performance Tests** (`test_performance.py`): Latency, concurrency, and stability

### Test Features
- **Simulation Mode**: Tests run without requiring real OpenAI API keys
- **Comprehensive Coverage**: API, business logic, and performance testing
- **Automated Validation**: Response time, memory usage, and error handling
- **Exit Code Support**: Proper exit codes for CI/CD integration

### Running Specific Tests
```bash
# Run only API tests
docker run --rm tbi-app python -m pytest /home/src/tests/test_api.py -v

# Run only performance tests  
docker run --rm tbi-app python -m pytest /home/src/tests/test_performance.py -v

# Run with detailed output
docker run --rm tbi-app python /home/src/tests/run_tests.py --verbose
```

## Performance Specifications

- **Latency**: Sub-3 second response times for document queries
- **Concurrency**: Supports multiple simultaneous users
- **Stability**: 100+ consecutive queries without failure  
- **Memory Efficiency**: Automatic cleanup and garbage collection
- **Cost Optimization**: Smart token usage with OpenAI API

## Security Features

- **API Key Encryption**: OpenAI keys encrypted at rest using Fernet
- **CORS Protection**: Properly configured for production and development
- **Input Validation**: Comprehensive request validation with Pydantic
- **Session Isolation**: Each user session is completely isolated
- **Error Handling**: Secure error messages without information leakage

## API Documentation

Once running, access interactive API documentation at:
- **Swagger UI**: http://localhost:8080/api/docs
- **ReDoc**: http://localhost:8080/api/redoc

### Key Endpoints
- `GET /api/health` - Application health check
- `POST /api/sessions/` - Create new session
- `POST /api/config/openai-key` - Set OpenAI API key
- `POST /api/documents/upload` - Upload document
- `POST /api/chat/query` - Send chat query (streaming)

## Troubleshooting

### Common Issues

#### Container won't start
```bash
# Check if port is available
lsof -i :8080

# Check container logs
docker logs <container-name>

# Rebuild container
docker build -t tbi-app . --no-cache
```

#### Frontend shows connection errors
- Ensure container is fully started (wait 30 seconds)
- Check that port 8080 is properly mapped
- Verify health endpoint: `curl http://localhost:8080/api/health`

#### Tests fail
- Ensure SIMULATE_OPENAI_KEY=1 is set for test environment
- Check container has proper test files at /home/src/tests/
- Verify Python path and dependencies

### Health Checks
```bash
# Application health
curl http://localhost:8080/api/health

# Container status
docker ps --filter name=your-container-name

# Process status inside container
docker exec your-container-name supervisorctl status
```

## Development Notes

### Design Decisions
1. **Single Container**: Simplified deployment and resource management
2. **Nginx Proxy**: Professional routing and static file serving
3. **Supervisor**: Robust process management and auto-restart
4. **SQLite**: Lightweight database suitable for single-instance deployment
5. **React Build**: Optimized static files served by nginx

### Production Considerations
- For production scale, consider PostgreSQL instead of SQLite
- Implement proper user authentication for multi-tenant use
- Add monitoring and logging solutions (Prometheus, ELK stack)
- Consider container orchestration (Kubernetes) for high availability



## 📜 License

MIT License - see LICENSE file for details

---

**Ready to deploy? Just run:** `docker run -p 8080:8080 <your_image_tag>`
