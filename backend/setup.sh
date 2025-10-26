#!/bin/bash

# Synergy Backend Setup Script
# Run this once to set up your development environment

echo "🔧 Setting up Synergy Backend..."
echo ""

# Create virtual environment
echo "1️⃣  Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "2️⃣  Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "3️⃣  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "4️⃣  Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "5️⃣  Creating .env file..."
    echo ""
    echo "⚠️  Please enter your Groq API key:"
    echo "   (Get it from: https://console.groq.com/keys)"
    read -p "API Key: " api_key
    echo "GROQ_API_KEY=$api_key" > .env
    echo "✅ .env file created with API key"
else
    echo "5️⃣  .env file already exists, skipping..."
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "📝 Next steps:"
echo "   1. Seed the database: python seed_db.py"
echo "   2. Start the server: ./start.sh"
echo ""
