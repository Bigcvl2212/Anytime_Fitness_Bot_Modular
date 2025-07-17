# Git Repository Setup Guide

Follow these steps to initialize and update your git repository:

## 1. Initialize Git Repository (if not already done)
```bash
git init
```

## 2. Add all files to staging
```bash
git add .
```

## 3. Create initial commit
```bash
git commit -m "Initial commit: Organized gym bot codebase

- Modularized code structure with proper package organization
- Added working overdue payments workflow (optimized version)
- Implemented ClubHub API integration for real member balances  
- Added Square invoice creation with current API
- Created proper test structure and legacy file organization
- Added comprehensive README and gitignore"
```

## 4. Add remote repository (replace with your actual repo URL)
```bash
git remote add origin https://github.com/yourusername/gym-bot.git
```

## 5. Push to repository
```bash
git push -u origin main
```

## Daily Workflow for Updates

### When you make changes:
```bash
# Check what files changed
git status

# Add specific files or all changes
git add .

# Commit with descriptive message
git commit -m "Description of your changes"

# Push to repository
git push
```

### Good commit message examples:
- `Fix: Resolved ClubOS login timeout issue`
- `Feature: Added batch invoice processing`
- `Update: Improved error handling in member data fetch`
- `Cleanup: Removed deprecated Square API calls`

## Current Project Status
✅ File structure organized and clean
✅ Legacy files moved to scripts/legacy/
✅ Tests moved to tests/ directory  
✅ Working optimized overdue payments workflow
✅ Proper gitignore and README created
✅ Ready for git repository
