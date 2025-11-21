@echo off
REM Commit and push all changes to trigger GitHub Actions build

echo ========================================
echo Committing Critical Fixes
echo ========================================
echo.

echo Files being committed:
echo   - launcher.py (fixed frozen mode)
echo   - run_dashboard.py (frozen mode detection)
echo   - gym_bot.spec (added hiddenimports, console=true)
echo   - build_windows.bat (pre-flight checks)
echo   - test_build.py (pre-flight validation)
echo   - .github/workflows/build-installers.yml (improved workflow)
echo   - Documentation files
echo.

git add .
git commit -m "🔥 CRITICAL FIX: Build system overhaul

Fixed 5 critical issues preventing builds from working:

1. Launcher frozen mode - Now uses in-process threading instead of subprocess
2. Missing hiddenimports - Added flask-socketio, eventlet, dotenv, src submodules
3. Console disabled - Enabled for debugging (console=True)
4. Import path issues - Fixed frozen vs script mode detection
5. No validation - Added pre-flight checks

Updated GitHub Actions workflow:
- Added pre-flight checks before build
- Added build verification steps
- Added build logs upload on failure
- Improved commands and error handling

New files:
- test_build.py - Pre-flight validation
- BUILD_GUIDE.md - Complete build guide
- BUILD_TROUBLESHOOTING.md - Error solutions
- CRITICAL_FIXES_SUMMARY.md - What was fixed
- BUILD_READY_CHECKLIST.md - Action plan
- GITHUB_ACTIONS_GUIDE.md - GitHub build guide

This should finally fix the build issues!"

if errorlevel 1 (
    echo.
    echo ❌ Commit failed. Check for errors above.
    pause
    exit /b 1
)

echo.
echo ✅ Changes committed!
echo.
echo Now pushing to GitHub to trigger build...
echo.

git push origin restore/2025-08-29-15-21

if errorlevel 1 (
    echo.
    echo ❌ Push failed. Check your connection and permissions.
    pause
    exit /b 1
)

echo.
echo ========================================
echo ✅ SUCCESS! Build triggered on GitHub
echo ========================================
echo.
echo Next steps:
echo   1. Go to: https://github.com/Bigcvl2212/Anytime_Fitness_Bot_Modular/actions
echo   2. Watch the workflow run (takes ~10-15 minutes)
echo   3. Download installers from Artifacts section
echo.
echo Build will create:
echo   - GymBot-Windows-Installer (GymBotInstaller.exe)
echo   - GymBot-macOS-Installer (GymBotInstaller.dmg)
echo.
echo You'll receive an email when build completes!
echo.
pause
