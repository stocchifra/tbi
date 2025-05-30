#!/bin/bash
# Production startup script using Docker (Single Container)

set -e

echo "🚀 Starting AI Document Analysis Application (Production Mode)"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

echo "🏗️  Building Docker image..."
docker build -t tbi-app .

echo "🛑 Stopping any existing container..."
docker stop tbi-app-prod 2>/dev/null || true
docker rm tbi-app-prod 2>/dev/null || true

echo "🚀 Starting application container..."
docker run -d -p 8080:8080 --name tbi-app-prod tbi-app

echo "⏳ Waiting for service to be ready..."
sleep 15

# Health checks
echo "🧪 Running health checks..."

# Check application health
if curl -f http://localhost:8080/health > /dev/null 2>&1; then
    echo "✅ Application is healthy"
else
    echo "❌ Application health check failed"
    docker logs tbi-app-prod
    exit 1
fi

# Check frontend
if curl -f http://localhost:8080 > /dev/null 2>&1; then
    echo "✅ Frontend is accessible"
else
    echo "❌ Frontend accessibility check failed"
    docker logs tbi-app-prod
    exit 1
fi

echo ""
echo "🎉 Application is running!"
echo ""
echo "📱 Application: http://localhost:8080"
echo "🔧 API Health: http://localhost:8080/health"
echo "📋 API Docs: http://localhost:8080/api/docs"
echo ""
echo "To view logs: docker logs -f tbi-app-prod"
echo "To stop: docker stop tbi-app-prod"
echo ""
