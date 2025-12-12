#!/bin/bash
# Development startup script for Hotel Booking System

echo "🏨 Starting Hotel Booking System..."
echo ""

# Check if dependencies are installed
if ! python -c "import flask" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
    echo ""
fi

# Set default port if not provided
export PORT=${PORT:-8000}

echo "✅ Starting Flask application on port $PORT..."
echo "🌐 Access the app at: http://localhost:$PORT"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the Flask app
python main.py
