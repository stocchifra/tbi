# AI-Powered Document Analysis Application

A prototype application that automates document analysis, extracts key insights, and generates summaries using AI. Built with FastAPI backend, React TypeScript frontend, and OpenAI API integration.

## 🚀 Features

- **Document Upload**: Support for file upload and text paste
- **AI-Powered Analysis**: Natural language queries about your documents
- **Real-time Chat**: Streaming responses for fast interaction
- **Session Management**: Persistent chat history and document storage
- **Secure API Key Management**: Encrypted storage of OpenAI API keys
- **Performance Optimized**: Sub-3-second response times (p95 latency)
- **Cost Efficient**: Optimized for <$0.01 per query
- **Production Ready**: Docker containerization and health monitoring

## 🏗️ Architecture

### Backend (FastAPI)
- **FastAPI** with async/await for high performance
- **SQLAlchemy** with SQLite for data persistence
- **OpenAI API** integration with streaming responses
- **Encryption** for secure API key storage
- **Session management** with UUID-based sessions
- **Document chunking** for large file handling

### Frontend (React TypeScript)
- **React 18** with TypeScript for type safety
- **Material-UI** for professional, responsive design
- **Real-time streaming** with Server-Sent Events
- **Context-based state management**
- **Error handling** and connection monitoring

## 📋 Requirements

- **Python 3.11+**
- **Node.js 18+**
- **Docker** (for production deployment)
- **OpenAI API Key**

## 🚀 Quick Start

### 1. Initial Setup
```bash
# Clone the repository
git clone <repository-url>
cd tbi

# Run setup script
./setup.sh
```

### 2. Configure Environment
```bash
# Edit .env file with your OpenAI API key
cp .env.example .env
# Edit .env and add: OPENAI_API_KEY=your_api_key_here
```

### 3. Development Mode
```bash
# Start development servers
./start-dev.sh
```

### 4. Production Mode
```bash
# Start with Docker (single container)
./start-prod.sh

# Or manually:
docker build -t tbi-app .
docker run -p 8080:8080 tbi-app
```

## 🛠️ Manual Setup

### Backend Setup
```bash
# Create virtual environment
python3 -m venv tbi
source tbi/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start backend
uvicorn src.app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup
```bash
# Install dependencies
cd src/frontend
npm install

# Start frontend
npm start
```

## 🧪 Testing

### Run All Tests
```bash
./run-tests.sh
```

### Run Specific Tests
```bash
# Backend tests only
source tbi/bin/activate
cd src
python -m pytest tests/ -v

# Performance tests
python -m pytest tests/test_performance.py -v

# Frontend tests
cd frontend
npm test
```

## 📊 Performance Specifications

- **P95 Latency**: <3 seconds for document queries
- **Cost Efficiency**: <$0.01 per query
- **Stability**: 100+ consecutive queries without failure
- **Concurrent Users**: Supports multiple simultaneous sessions
- **Document Size**: Up to 1MB per document
- **Session Management**: Persistent across browser sessions

## 🔧 Configuration

### Environment Variables

#### Backend (.env)
```bash
# Required
OPENAI_API_KEY=your_openai_api_key_here
SECRET_KEY=your_secret_key_for_encryption

# Optional
DATABASE_URL=sqlite:///data/app.db
ENVIRONMENT=development
REDIS_URL=redis://localhost:6379/0
```

#### Frontend (src/frontend/.env)
```bash
REACT_APP_API_URL=http://localhost:8000
REACT_APP_VERSION=1.0.0
REACT_APP_ENVIRONMENT=development
```

### Application Settings
- **OpenAI Model**: Configurable (default: gpt-4o-mini)
- **Max Document Size**: 1MB (configurable)
- **Query Timeout**: 30 seconds
- **Rate Limiting**: 10 requests per minute per session

## 📁 Project Structure

```
tbi/
├── Dockerfile                  # Single-container deployment
├── nginx-single.conf           # Nginx configuration
├── supervisord.conf           # Process management
├── requirements.txt            # Python dependencies
├── setup.sh                    # Initial setup script
├── start-dev.sh               # Development startup
├── start-prod.sh              # Production startup
├── run-tests.sh               # Test runner
├── src/
│   ├── app/                   # Backend application
│   │   ├── main.py           # FastAPI application
│   │   ├── api/              # API routes
│   │   ├── models/           # Database models
│   │   ├── services/         # Business logic
│   │   └── utils/            # Utilities
│   ├── frontend/             # React application
│   │   ├── src/
│   │   │   ├── components/   # React components
│   │   │   ├── contexts/     # State management
│   │   │   └── App.tsx       # Main component
│   │   └── package.json
│   └── tests/                # Test suite
└── tbi/                      # Python virtual environment
```

## 🌐 API Endpoints

### Core Endpoints
- `GET /health` - Health check
- `POST /sessions/` - Create new session
- `GET /sessions/{session_id}/history` - Get chat history
- `POST /sessions/{session_id}/chat` - Send query (streaming)
- `POST /sessions/{session_id}/documents/upload` - Upload file
- `POST /sessions/{session_id}/documents/upload-text` - Upload text
- `GET /sessions/{session_id}/documents` - List documents
- `POST /sessions/{session_id}/config/api-key` - Set API key
- `GET /sessions/{session_id}/config` - Get configuration

### Authentication
API keys are stored encrypted per session. No global authentication required for the prototype.

## 🐳 Docker Deployment

### Single Container (Recommended)
```bash
# Build and start
docker build -t tbi-app .
docker run -p 8080:8080 tbi-app

# Or use production script
./start-prod.sh

# View logs
docker logs -f tbi-app-prod

# Stop service
docker stop tbi-app-prod
```

### Access the Application
- **Frontend**: http://localhost:8080
- **API Health**: http://localhost:8080/health  
- **API Docs**: http://localhost:8080/api/docs

## 🔍 Monitoring and Debugging

### Health Checks
- Application: `http://localhost:8080/health`
- Frontend: `http://localhost:8080`

### Logs
```bash
# Development logs
tail -f backend.log

# Docker logs
docker logs -f tbi-app-prod
```

### Performance Monitoring
- Built-in latency tracking
- Token usage monitoring
- Error rate tracking
- Memory usage monitoring

## 🛡️ Security Considerations

- **API Key Encryption**: OpenAI keys encrypted at rest
- **CORS Protection**: Configured for development/production
- **Input Validation**: Comprehensive request validation
- **Rate Limiting**: Per-session request limiting
- **File Size Limits**: Prevent abuse with size restrictions

## 🚧 Known Limitations

- **Prototype Status**: Not production-hardened
- **Single Server**: No load balancing or clustering
- **Local Storage**: SQLite for simplicity (use PostgreSQL for production)
- **Basic Auth**: No user authentication system
- **File Types**: Text-based documents only

## 🔄 Development Workflow

### Making Changes
1. **Backend changes**: Automatic reload in development mode
2. **Frontend changes**: Hot reload with React dev server
3. **Database changes**: Migrations handled automatically
4. **Testing**: Run tests before committing

### Adding Features
1. **Backend**: Add routes in `src/app/api/routes.py`
2. **Frontend**: Add components in `src/frontend/src/components/`
3. **Database**: Update models in `src/app/models/database.py`
4. **Tests**: Add tests in `src/tests/`

## 📈 Performance Optimization

### Cost Optimization
- **Smart chunking**: Minimize token usage
- **Context optimization**: Relevant document selection
- **Caching**: Session-based response caching
- **Model selection**: Cost-effective model choices

### Latency Optimization
- **Streaming responses**: Real-time user feedback
- **Async processing**: Non-blocking operations
- **Connection pooling**: Efficient resource usage
- **CDN ready**: Static asset optimization

## 🆘 Troubleshooting

### Common Issues

#### Backend won't start
```bash
# Check Python version
python3 --version

# Check virtual environment
source tbi/bin/activate
pip list

# Check database
ls -la data/
```

#### Frontend build issues
```bash
# Clear cache
rm -rf src/frontend/node_modules
rm src/frontend/package-lock.json
cd src/frontend && npm install
```

#### OpenAI API errors
- Verify API key in .env file
- Check API key permissions
- Monitor usage limits
- Check network connectivity

#### Docker issues
```bash
# Reset Docker environment
docker stop tbi-app-prod
docker rm tbi-app-prod
docker system prune -f
docker build -t tbi-app .
```

## 📞 Support

For issues and questions:
1. Check this documentation
2. Review error logs
3. Check GitHub issues
4. Run diagnostic tests: `./run-tests.sh`

## 🔮 Future Enhancements

- **Multi-user support** with authentication
- **Advanced file types** (PDF, Word, etc.)
- **Vector embeddings** for better document search
- **Batch processing** for multiple documents
- **API rate limiting** improvements
- **Advanced analytics** and reporting
- **Cloud deployment** guides
- **Plugin system** for extensibility

---

**License**: MIT License - see LICENSE file for details