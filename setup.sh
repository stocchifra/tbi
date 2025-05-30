#!/bin/bash
# Initial setup script

set -e

echo "🔧 Setting up AI Document Analysis Application"

# Check Python version
if ! python3 --version | grep -q "3.11"; then
    echo "⚠️  Python 3.11 is recommended. Current version:"
    python3 --version
fi

# Check Node.js version
if ! node --version | grep -q "v18"; then
    echo "⚠️  Node.js 18 is recommended. Current version:"
    node --version
fi

# Create virtual environment if it doesn't exist
if [ ! -d "tbi" ]; then
    echo "🐍 Creating Python virtual environment..."
    python3 -m venv tbi
fi

# Activate virtual environment
source tbi/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Install Node.js dependencies
echo "📦 Installing Node.js dependencies..."
cd src/frontend
npm install
cd ../..

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p data
mkdir -p src/app/static

# Copy environment template
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
fi

# Make scripts executable
chmod +x start-dev.sh
chmod +x start-prod.sh
chmod +x run-tests.sh

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file and add your OpenAI API key"
echo "2. Run './start-dev.sh' for development mode"
echo "3. Run './start-prod.sh' for production mode"
echo "4. Run './run-tests.sh' to run tests"
echo ""
