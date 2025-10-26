#!/bin/bash

# Synergy Backend Startup Script
# This script activates the virtual environment, loads the API key, and starts the server

echo "🚀 Starting Synergy Backend..."

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Run: python3 -m venv venv"
    exit 1
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    echo "Create it with: echo 'GROQ_API_KEY=your_key_here' > .env"
    exit 1
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Load .env file and export GROQ_API_KEY
echo "🔑 Loading API key from .env..."
export $(cat .env | grep -v '^#' | xargs)

# Check if API key is loaded
if [ -z "$GROQ_API_KEY" ]; then
    echo "❌ GROQ_API_KEY not found in .env file!"
    exit 1
fi

echo "✅ Environment ready!"
echo ""

# Start Flask server
python app.py
