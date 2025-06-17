#!/bin/bash
# Lab Manager - Start Script
# This script ensures the Flask application starts correctly with proper environment setup

echo "🚀 Lab Manager - Starting Application"
echo "=================================="

# Set Flask environment variables
export FLASK_APP=run.py
export FLASK_DEBUG=1

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ Virtual environment active: $VIRTUAL_ENV"
else
    echo "⚠️  Warning: No virtual environment detected. Consider using 'source venv/bin/activate'"
fi

# Check if required files exist
if [ ! -f "run.py" ]; then
    echo "❌ Error: run.py not found. Make sure you're in the Lab_Manager directory."
    exit 1
fi

if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found. Using default configuration."
fi

echo "📋 Available commands:"
echo "  1. Direct execution:     python run.py"
echo "  2. Flask CLI (basic):    flask run"
echo "  3. Flask CLI (custom):   flask run --host=127.0.0.1 --port=5000 --debug"
echo "  4. Show routes:          flask routes"
echo ""

# Ask user which method to use
read -p "Choose execution method (1-4) or press Enter for default (1): " choice

case $choice in
    1|"")
        echo "🔧 Starting with system health checks..."
        python run.py
        ;;
    2)
        echo "🔧 Starting with Flask CLI (basic)..."
        flask run
        ;;
    3)
        echo "🔧 Starting with Flask CLI (custom)..."
        flask run --host=127.0.0.1 --port=5000 --debug
        ;;
    4)
        echo "📋 Showing available routes..."
        flask routes
        ;;
    *)
        echo "❌ Invalid choice. Using default method..."
        python run.py
        ;;
esac
