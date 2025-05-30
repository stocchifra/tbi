#!/bin/bash
# Test runner script

set -e

echo "🧪 Running AI Document Analysis Application Tests"

# Activate virtual environment
source tbi/bin/activate

# Run backend tests
echo "🔧 Running backend tests..."
cd src
python -m pytest tests/ -v --tb=short --cov=app --cov-report=term-missing

# Run performance tests
echo "⚡ Running performance tests..."
python -m pytest tests/test_performance.py -v -m "not slow"

# Run frontend tests
echo "🎨 Running frontend tests..."
cd frontend
npm test -- --coverage --watchAll=false
cd ../..

echo ""
echo "✅ All tests completed!"
echo ""
