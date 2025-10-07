@echo off
echo ============================================
echo   GitHub Actions Build Setup
echo ============================================
echo.

echo This script will help you set up automated builds for Mac and Windows
echo.

REM Check if git is installed
git --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Git is not installed or not in PATH
    echo Please install Git from https://git-scm.com/
    pause
    exit /b 1
)

echo ✓ Git is installed
echo.

REM Check if we're in a git repository
git rev-parse --git-dir >nul 2>&1
if errorlevel 1 (
    echo This folder is not a Git repository yet.
    echo.
    set /p INIT_GIT="Do you want to initialize Git here? (y/n): "
    if /i "%INIT_GIT%"=="y" (
        git init
        echo ✓ Git repository initialized
    ) else (
        echo Please navigate to your Git repository first
        pause
        exit /b 1
    )
)

echo ✓ Git repository detected
echo.

REM Check if .github/workflows exists
if not exist ".github\workflows" (
    echo Creating .github/workflows directory...
    mkdir .github\workflows
    echo ✓ Created .github/workflows directory
) else (
    echo ✓ .github/workflows directory exists
)

echo.
echo ============================================
echo   Next Steps:
echo ============================================
echo.
echo 1. Make sure you have a GitHub repository created
echo.
echo 2. Add your repository as remote (if not already done):
echo    git remote add origin https://github.com/YOUR_USERNAME/gym-bot.git
echo.
echo 3. Add and commit the workflow:
echo    git add .github/workflows/build-installers.yml
echo    git add GITHUB_BUILD_GUIDE.md
echo    git commit -m "Add GitHub Actions build workflow"
echo.
echo 4. Push to GitHub:
echo    git push origin main
echo    (or: git push origin master)
echo.
echo 5. Go to GitHub → Actions tab to see the build running!
echo.
echo 6. Download installers from Actions → Artifacts
echo.
echo ============================================
echo.

REM Check for remote
git remote -v >nul 2>&1
if errorlevel 1 (
    echo WARNING: No git remote configured
    echo.
    set /p SETUP_REMOTE="Do you want to add a GitHub remote now? (y/n): "
    if /i "%SETUP_REMOTE%"=="y" (
        set /p REMOTE_URL="Enter your GitHub repository URL: "
        git remote add origin "%REMOTE_URL%"
        echo ✓ Remote added
    )
)

echo.
set /p PUSH_NOW="Do you want to commit and push these files now? (y/n): "
if /i "%PUSH_NOW%"=="y" (
    echo.
    echo Adding files...
    git add .github/workflows/build-installers.yml
    git add GITHUB_BUILD_GUIDE.md
    git add setup_github_builds.bat

    echo Committing...
    git commit -m "Add GitHub Actions automated build workflow for Mac and Windows"

    echo Pushing to GitHub...
    git push origin main
    if errorlevel 1 (
        echo.
        echo Push failed. Try: git push origin master
        git push origin master
    )

    echo.
    echo ============================================
    echo ✅ Success!
    echo ============================================
    echo.
    echo The build workflow is now active!
    echo.
    echo Go to GitHub → Actions to watch the build
    echo.
    echo In ~15 minutes, download:
    echo   - GymBot-Windows-Installer.exe (for you)
    echo   - GymBot-macOS-Installer.dmg (for Tyler)
    echo.
) else (
    echo.
    echo Manual push: Run these commands when ready:
    echo   git add .github/workflows/build-installers.yml
    echo   git add GITHUB_BUILD_GUIDE.md
    echo   git commit -m "Add GitHub Actions build workflow"
    echo   git push origin main
)

echo.
echo See GITHUB_BUILD_GUIDE.md for detailed instructions
echo.
pause
