@echo off
title Gym Bot Dashboard Setup
echo.
echo 🏋️‍♂️  Setting up Gym Bot for Tyler...
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.11+ from https://python.org/downloads/
    echo    Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo ✅ Python detected
echo 📦 Installing dependencies...
python setup_for_tyler.py

if errorlevel 1 (
    echo ❌ Setup failed. Please check the error messages above.
    pause
    exit /b 1
)

echo.
echo 🚀 Setup complete! Starting the app...
echo 🌍 NOTE: Internet connection required for ClubOS/ClubHub
echo 📱 The app will open at: http://localhost:5000
echo 🔐 You'll need to set up YOUR ClubOS credentials on first login
echo.
echo 💡 Press Ctrl+C to stop the server
echo ============================================
echo.

python start_gym_bot.py
pause
