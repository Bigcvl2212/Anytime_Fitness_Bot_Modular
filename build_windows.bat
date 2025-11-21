@echo off
REM Windows Build Script for Gym Bot
REM This script builds the executable and creates an installer

echo ========================================
echo Gym Bot - Windows Build Script
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

echo Step 0: Running pre-flight checks...
python test_build.py
if errorlevel 1 (
    echo ERROR: Pre-flight checks failed
    echo Fix the errors above before building
    pause
    exit /b 1
)

echo.
echo Step 1: Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

pip install pyinstaller
if errorlevel 1 (
    echo ERROR: Failed to install PyInstaller
    pause
    exit /b 1
)

echo.
echo Step 2: Cleaning previous builds...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist

echo.
echo Step 3: Building executable with PyInstaller...
echo This may take 5-10 minutes...
echo.
python -m PyInstaller gym_bot.spec --clean --noconfirm
if errorlevel 1 (
    echo ERROR: PyInstaller build failed
    echo Check the error messages above
    pause
    exit /b 1
)

echo.
echo Step 4: Verifying build output...
if not exist "dist\GymBot\GymBot.exe" (
    echo ERROR: GymBot.exe was not created
    echo Check build logs above
    pause
    exit /b 1
)

echo ✅ Build verification passed!
echo.

echo Step 5: Creating installer with Inno Setup...
echo Looking for Inno Setup...

REM Check common Inno Setup installation paths
set INNO_PATH=
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    set INNO_PATH=C:\Program Files (x86)\Inno Setup 6\ISCC.exe
) else if exist "C:\Program Files\Inno Setup 6\ISCC.exe" (
    set INNO_PATH=C:\Program Files\Inno Setup 6\ISCC.exe
) else if exist "C:\Program Files (x86)\Inno Setup 5\ISCC.exe" (
    set INNO_PATH=C:\Program Files (x86)\Inno Setup 5\ISCC.exe
)

if "%INNO_PATH%"=="" (
    echo WARNING: Inno Setup not found
    echo Please install Inno Setup from: https://jrsoftware.org/isdl.php
    echo.
    echo Build completed successfully!
    echo Executable available at: dist\GymBot\GymBot.exe
    echo.
    echo To test the build:
    echo   cd dist\GymBot
    echo   GymBot.exe
    echo.
    pause
    exit /b 0
)

"%INNO_PATH%" installer_windows.iss
if errorlevel 1 (
    echo ERROR: Inno Setup compilation failed
    pause
    exit /b 1
)

echo.
echo ========================================
echo Build completed successfully!
echo ========================================
echo.
echo Executable: dist\GymBot\GymBot.exe
echo Installer: Output\GymBotInstaller.exe
echo.
echo To test the build:
echo   1. Run: dist\GymBot\GymBot.exe
echo   2. Check logs in: %%LOCALAPPDATA%%\GymBot\logs
echo.
echo To distribute:
echo   Share: Output\GymBotInstaller.exe
echo.
pause
