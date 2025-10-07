# GitHub Actions Build Guide

## 🎯 Automatic Mac & Windows Installer Builds

This guide explains how to use GitHub Actions to automatically build Mac and Windows installers for Tyler and other managers.

---

## 🚀 Quick Start

### Step 1: Push to GitHub

```bash
cd gym-bot-modular

# Add all files
git add .

# Commit
git commit -m "Add GitHub Actions build workflow"

# Push to GitHub
git push origin main
```

### Step 2: Watch the Build

1. Go to your GitHub repository
2. Click the **"Actions"** tab at the top
3. You'll see the workflow running: **"Build Gym Bot Installers"**
4. Click on it to watch progress

### Step 3: Download Installers

Once the build completes (takes ~10-15 minutes):

1. Scroll down to **"Artifacts"** section
2. Download:
   - **GymBot-Windows-Installer** (for you)
   - **GymBot-macOS-Installer** (for Tyler)

---

## 📦 What Gets Built

### Windows Installer
- **File**: `GymBotInstaller.exe`
- **Size**: ~50-100 MB
- **For**: Your Windows machine
- **Contains**: Python runtime + all dependencies + app

### macOS Installer
- **File**: `GymBotInstaller.dmg`
- **Size**: ~50-100 MB
- **For**: Tyler's MacBook
- **Contains**: Python runtime + all dependencies + app bundle

---

## 🔄 When Builds Happen Automatically

The workflow runs automatically when you:

1. **Push to main/master branch**
   ```bash
   git push origin main
   ```

2. **Create a pull request**
   - Builds run to test the changes

3. **Push a version tag** (for releases)
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

4. **Manual trigger**
   - Go to Actions tab
   - Click "Build Gym Bot Installers"
   - Click "Run workflow"

---

## 🏷️ Creating Releases (Recommended)

### Why Use Releases?

Releases are better than just builds because:
- Installers are permanently stored
- Easy to share download links
- Version tracking
- Release notes

### How to Create a Release

```bash
# Step 1: Tag your version
git tag -a v1.0.0 -m "Release version 1.0.0 - Initial stable release"

# Step 2: Push the tag
git push origin v1.0.0

# Step 3: Wait for build to complete

# Step 4: Go to GitHub → Releases
# You'll see v1.0.0 with both installers attached
```

### Version Numbering

Use semantic versioning: `vMAJOR.MINOR.PATCH`

- **v1.0.0** - First stable release
- **v1.0.1** - Bug fix
- **v1.1.0** - New features
- **v2.0.0** - Major changes

---

## 📥 Sending to Tyler

### Option 1: Share GitHub Release Link (Best)

1. Create a release (see above)
2. Go to GitHub → Releases
3. Copy the download link for `GymBotInstaller.dmg`
4. Send Tyler the link

Example:
```
Hey Tyler, download the Mac installer here:
https://github.com/your-username/gym-bot/releases/download/v1.0.0/GymBotInstaller.dmg
```

### Option 2: Download & Upload to Cloud

1. Download `GymBot-macOS-Installer.dmg` from Actions
2. Upload to Google Drive / Dropbox
3. Share link with Tyler

### Option 3: Email Directly

1. Download `GymBot-macOS-Installer.dmg` from Actions
2. Email to Tyler (if under 25 MB)
3. Or use WeTransfer for larger files

---

## 🛠️ Troubleshooting

### Build Fails on Windows

**Check:**
- `requirements.txt` has all dependencies
- `gym_bot.spec` is correctly configured
- `installer_windows.iss` paths are correct

**Fix:**
- Review the error in Actions logs
- Update files and push again

### Build Fails on macOS

**Check:**
- Python dependencies are Mac-compatible
- `gym_bot.spec` works on macOS
- No Windows-specific code

**Fix:**
- Test locally on Mac if possible
- Or fix based on GitHub Actions logs

### Artifacts Not Appearing

**Reasons:**
- Build failed (check logs)
- Workflow didn't complete
- Artifact expired (30-day retention)

**Fix:**
- Re-run workflow
- Check for errors in logs

---

## 📊 Build Status Badge

Add this to your README.md to show build status:

```markdown
![Build Status](https://github.com/your-username/gym-bot/actions/workflows/build-installers.yml/badge.svg)
```

---

## ⚙️ Advanced Configuration

### Customize Build Workflow

Edit `.github/workflows/build-installers.yml`:

**Change Python version:**
```yaml
python-version: '3.12'  # Use Python 3.12 instead
```

**Add code signing (Windows):**
```yaml
- name: Sign Windows executable
  run: |
    signtool sign /f ${{ secrets.CERT_FILE }} /p ${{ secrets.CERT_PASSWORD }} Output/GymBotInstaller.exe
```

**Add code signing (macOS):**
```yaml
- name: Sign macOS app
  run: |
    codesign --deep --force --verify --verbose \
      --sign "Developer ID Application: ${{ secrets.APPLE_DEVELOPER_ID }}" \
      dist/GymBot.app
```

### Store Secrets

For code signing or API keys:

1. Go to GitHub → Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Add secrets like:
   - `CERT_FILE`
   - `CERT_PASSWORD`
   - `APPLE_DEVELOPER_ID`

---

## 📝 Workflow Features

### ✅ What It Does

- ✅ Builds Windows EXE installer
- ✅ Builds macOS DMG installer
- ✅ Tests on both platforms
- ✅ Uploads artifacts automatically
- ✅ Creates releases for tags
- ✅ Runs in parallel (fast!)
- ✅ 30-day artifact retention

### ⏱️ Build Times

- **Windows**: ~8-12 minutes
- **macOS**: ~8-12 minutes
- **Total** (parallel): ~10-15 minutes

### 💾 Storage

- Each build uses ~200 MB storage
- Artifacts expire after 30 days
- Releases are permanent

---

## 🎓 Usage Examples

### Example 1: Weekly Updates for Tyler

```bash
# Every Friday, push updates
git add .
git commit -m "Weekly update - bug fixes and improvements"
git push origin main

# Wait 15 minutes for build

# Share new installer link with Tyler
```

### Example 2: Major Release

```bash
# Prepare release
git add .
git commit -m "Version 2.0.0 - Major feature update"

# Create release tag
git tag -a v2.0.0 -m "Release 2.0.0 - Added AI features"
git push origin v2.0.0

# Go to GitHub releases
# Download both installers
# Test on your machine
# Send to Tyler
```

### Example 3: Emergency Fix

```bash
# Quick fix for bug
git add src/fix_file.py
git commit -m "Hotfix - Fixed login issue"
git push origin main

# Trigger manual build if needed:
# Go to Actions → Build Gym Bot Installers → Run workflow

# Download fixed installer immediately
```

---

## 🔐 Security Notes

### What's Safe

- ✅ Building on GitHub's servers
- ✅ No secrets in code
- ✅ Encrypted during build
- ✅ Clean build environment

### What to Avoid

- ❌ Don't commit passwords or API keys
- ❌ Don't commit `.env` files
- ❌ Don't include sensitive data

### Best Practices

1. Use GitHub Secrets for credentials
2. Use `.gitignore` to exclude sensitive files
3. Review code before pushing
4. Test builds before sending to Tyler

---

## 📞 Support

### If Build Fails

1. Check the Actions log
2. Look for red X markers
3. Read error messages
4. Fix the issue
5. Push again

### Common Issues

**"Module not found"**
- Add to `requirements.txt`

**"File not found"**
- Check paths in `gym_bot.spec`

**"Permission denied"**
- Check file permissions
- Ensure executable scripts

---

## 🎉 Success!

Once set up, you can:

1. ✅ Build Mac installer without owning a Mac
2. ✅ Build Windows installer automatically
3. ✅ Send Tyler new versions instantly
4. ✅ Track versions with releases
5. ✅ Never manually build again!

---

## Quick Commands Reference

```bash
# Push and trigger build
git push origin main

# Create release
git tag v1.0.0 && git push origin v1.0.0

# Check build status
# Go to: https://github.com/your-username/gym-bot/actions

# Download installers
# Actions → Build Gym Bot Installers → Artifacts

# Share with Tyler
# Releases → Latest → Download GymBotInstaller.dmg
```

---

**That's it! Your automated build system is ready! 🚀**
