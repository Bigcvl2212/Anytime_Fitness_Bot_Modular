#!/bin/bash
# macOS Build Script for Gym Bot
# This script builds the .app bundle and creates a DMG installer

echo "========================================"
echo "Gym Bot - macOS Build Script"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8 or higher from python.org"
    exit 1
fi

echo "Step 1: Installing dependencies..."
pip3 install -r requirements.txt
pip3 install pyinstaller
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi

echo ""
echo "Step 2: Cleaning previous builds..."
rm -rf build dist GymBot.spec

echo ""
echo "Step 3: Building .app bundle with PyInstaller..."
pyinstaller gym_bot.spec
if [ $? -ne 0 ]; then
    echo "ERROR: PyInstaller build failed"
    exit 1
fi

echo ""
echo "Step 4: Code signing (optional)..."
echo "Skipping code signing (requires Apple Developer account)"
echo "To enable code signing, uncomment and configure the following line:"
echo "# codesign --deep --force --verify --verbose --sign \"Developer ID Application: YOUR NAME\" dist/GymBot.app"

echo ""
echo "Step 5: Creating DMG installer..."

# Check if create-dmg is installed
if ! command -v create-dmg &> /dev/null; then
    echo "Installing create-dmg..."
    brew install create-dmg
    if [ $? -ne 0 ]; then
        echo "WARNING: create-dmg installation failed"
        echo "Install it manually with: brew install create-dmg"
        echo ""
        echo "Build completed successfully!"
        echo "Application available at: dist/GymBot.app"
        exit 0
    fi
fi

# Create DMG
create-dmg \
  --volname "Gym Bot Installer" \
  --volicon "static/favicon.icns" \
  --window-pos 200 120 \
  --window-size 800 400 \
  --icon-size 100 \
  --icon "GymBot.app" 200 190 \
  --hide-extension "GymBot.app" \
  --app-drop-link 600 185 \
  --no-internet-enable \
  "dist/GymBotInstaller.dmg" \
  "dist/GymBot.app"

if [ $? -ne 0 ]; then
    echo "WARNING: DMG creation failed"
    echo ""
    echo "Build completed successfully!"
    echo "Application available at: dist/GymBot.app"
    exit 0
fi

echo ""
echo "========================================"
echo "Build completed successfully!"
echo "========================================"
echo ""
echo "Application: dist/GymBot.app"
echo "DMG Installer: dist/GymBotInstaller.dmg"
echo ""
echo "Testing the app:"
echo "  open dist/GymBot.app"
echo ""
echo "Distribution:"
echo "  Distribute dist/GymBotInstaller.dmg to users"
echo ""
