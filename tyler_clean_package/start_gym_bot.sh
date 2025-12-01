#!/bin/bash

# Gym Bot Startup Script for Mac/Linux
echo "🏋️‍♂️  Setting up Gym Bot for Tyler..."
echo "============================================"

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.11+ from https://python.org/downloads/"
    exit 1
fi

# Check Python version
python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
required_version="3.11"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "⚠️  Python $python_version found, but Python 3.11+ is recommended"
    echo "   Continuing anyway..."
fi

echo "✅ Python $python_version detected"

# Run setup
echo "📦 Installing dependencies..."
python3 setup_for_tyler.py

if [ $? -ne 0 ]; then
    echo "❌ Setup failed. Please check the error messages above."
    exit 1
fi

echo ""
echo "🚀 Setup complete! Starting the app..."
echo "🌍 NOTE: Internet connection required for ClubOS/ClubHub"
echo "📱 The app will open at: http://localhost:5000"
echo "🔐 You'll need to set up YOUR ClubOS credentials on first login"
echo ""
echo "💡 Press Ctrl+C to stop the server"
echo "============================================"

# Start the app
python3 start_gym_bot.py
