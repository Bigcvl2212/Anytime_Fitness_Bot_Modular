# Changelog

All notable changes to Gym Bot will be documented in this file.

## [2.1.6] - 2025-10-08

### 🔥 Critical Build System Fixes
- **Fixed launcher frozen mode execution** - Launcher now properly starts Flask server when running as compiled exe
- **Fixed missing dependencies** - Added flask-socketio, eventlet, python-socketio, and dotenv to PyInstaller bundle
- **Fixed import path issues** - Proper frozen vs script mode detection in run_dashboard.py
- **Enabled console for debugging** - Console output visible in exe for troubleshooting

### ✨ New Features
- **Pre-flight build validation** - Added test_build.py to catch issues before building
- **Build verification** - GitHub Actions now verifies exe/app was created successfully
- **Build logs on failure** - Automatically uploads build logs if GitHub Actions build fails
- **Version tracking** - Added VERSION file and version display in launcher

### 📚 Documentation
- **BUILD_GUIDE.md** - Complete build and deployment guide
- **BUILD_TROUBLESHOOTING.md** - Comprehensive error solutions
- **CRITICAL_FIXES_SUMMARY.md** - Detailed explanation of all fixes
- **BUILD_READY_CHECKLIST.md** - Step-by-step action plan
- **GITHUB_ACTIONS_GUIDE.md** - GitHub build automation guide
- **GITHUB_BUILD_READY.md** - Quick start guide

### 🔧 Improvements
- **Enhanced GitHub Actions workflow** - Added pre-flight checks and verification steps
- **Better error handling** - Improved error messages throughout build process
- **Build script improvements** - build_windows.bat now includes validation steps
- **Unicode compatibility** - Fixed encoding issues for GitHub Actions runners

### 🐛 Bug Fixes
- Fixed launcher not starting Flask in frozen mode (subprocess → threading)
- Fixed missing hiddenimports causing ModuleNotFoundError
- Fixed database/log paths not using AppData when frozen
- Fixed Unicode encoding errors in test_build.py for GitHub runners
- Fixed templates/static folder bundling issues

### 📦 Build System
- Updated PyInstaller configuration with all required dependencies
- Improved GitHub Actions workflow with build verification
- Added automated installer creation for Windows and macOS
- Added artifact upload with 30-day retention

---

## [1.0.0] - Initial Release

Initial release of Gym Bot Dashboard with:
- Member management
- Prospect tracking
- Training client management
- Calendar integration
- Messaging system
- Payment tracking
- Multi-club support
- AI-powered agents
- Real-time updates
