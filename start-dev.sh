#!/bin/bash
# Development startup script

set -e

echo "🚀 Starting AI Document Analysis Application (Development Mode)"

# Check if virtual environment exists
if [ ! -d "tbi" ]; then
    echo "❌ Virtual environment not found. Please run setup.sh first."
    exit 1
fi

# Activate virtual environment
source tbi/bin/activate

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file and add your OpenAI API key"
fi

# Create data directory
mkdir -p data

echo "🔧 Installing/updating Python dependencies..."
pip install -r requirements.txt

echo "🔧 Installing/updating Node.js dependencies..."
cd src/frontend
npm install
cd ../..

echo "🧪 Running quick health checks..."

# Start backend in background
echo "🚀 Starting backend server..."
uvicorn src.app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Check backend health
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend is running on http://localhost:8000"
else
    echo "❌ Backend failed to start"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

# Start frontend
echo "🚀 Starting frontend server..."
cd src/frontend
npm start &
FRONTEND_PID=$!
cd ../..

echo ""
echo "🎉 Application is starting up!"
echo ""
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📋 API Docs: http://localhost:8000/docs"
echo ""
echo "To stop the application, press Ctrl+C"
echo ""

# Wait for user interrupt
trap 'echo "🛑 Stopping servers..."; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0' INT
wait
