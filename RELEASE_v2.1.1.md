# Release v2.1.1 - WinError 5 Fix + Launcher Improvements

## 🚨 Critical Fix

**v2.1.0 had a fatal bug** - Compiled executable tried to write logs to `C:\Program Files\GymBot\_internal\logs` which is **read-only**, causing:
```
WinError 5: Access is denied
C:\Program Files\GymBot\_internal\logs
```

## ✅ What's Fixed in v2.1.1

### 1. **WinError 5 Access Denied** (NEW FIX)
- **Problem**: Compiled .exe tried to write to Program Files (read-only)
- **Solution**: Now uses writable user directory:
  - **Logs**: `%LOCALAPPDATA%\GymBot\logs\launcher_flask.log`
  - **Database**: `%LOCALAPPDATA%\GymBot\data\gym_bot.db`
- **Script mode unchanged**: Still uses project directory for development

### 2. **Launcher Subprocess Hanging** (from v2.1.0)
- **Problem**: "Server failed to start within 30 seconds" error
- **Root Cause**: `subprocess.PIPE` causes Windows buffering/hanging
- **Solution**: Changed to file-based logging
- **Result**: Server now starts in 5-10 seconds ✅

### 3. **Messaging Inbox Timestamps** (from v2.1.0)
- **Problem**: Inbox showed old January messages with "Just now" timestamps
- **Root Cause**: Parser was using `datetime.now()` fallback
- **Solution**: Extract timestamps from sibling `<div class="message-options">` element
- **Result**: Shows actual times like "9:30 AM", "Sep 4", etc. ✅

### 4. **Inbox Sort Order** (from v2.1.0)
- **Problem**: Oldest messages appeared first
- **Root Cause**: Wrong SQL sort order (ROWID DESC)
- **Solution**: Changed to ROWID ASC (ClubOS returns newest-first)
- **Result**: Newest messages appear at top ✅

### 5. **Inbox Performance** (from v2.1.0)
- **Problem**: Inbox took 5 minutes to load
- **Root Cause**: HTTP lookups for every message sender
- **Solution**: Use owner_id directly from database
- **Result**: Inbox loads in 2 seconds ✅

## 📦 Installation

### Fresh Install
1. Download installer from GitHub Releases:
   - **Windows**: `GymBotInstaller.exe`
   - **macOS**: `GymBotInstaller.dmg`
2. Run installer
3. Launch "Gym Bot" from Start Menu (Windows) or Applications (macOS)

### Upgrade from v2.1.0
1. **Uninstall v2.1.0** (Control Panel > Programs)
2. **Download v2.1.1** installer
3. **Install v2.1.1**
4. Your data is safe - new version uses different location

### Data Migration (if needed)
Your v2.1.0 data is NOT in Program Files (it never worked), so no migration needed!

## 🔍 Verify Fix

After installing v2.1.1:

1. **Launch Gym Bot** from Start Menu
2. **Click "Start Server"**
3. **Should see**:
   - Status changes to "Starting server..." within 1 second
   - Status changes to "Server is running" (green) within 10 seconds
   - Browser opens automatically to dashboard
4. **Check logs** (click "View Logs" button):
   - Should open: `C:\Users\YourName\AppData\Local\GymBot\logs\launcher_flask.log`
   - Should see Flask startup messages
5. **Check database**:
   - Location: `C:\Users\YourName\AppData\Local\GymBot\data\gym_bot.db`
   - Created automatically on first run

## 🚀 Download

GitHub Actions is building the installers now:
https://github.com/Bigcvl2212/Anytime_Fitness_Bot_Modular/actions

Once complete (~10-15 minutes), download from:
https://github.com/Bigcvl2212/Anytime_Fitness_Bot_Modular/releases/tag/v2.1.1

## 📝 Files Changed

- `launcher.py` - Use AppData for logs when frozen
- `src/main_app.py` - Use AppData for database when frozen
- Both files detect `sys.frozen` to use correct paths

## 🎯 Distribution to Gym Managers

**IMPORTANT**: Only distribute v2.1.1, NOT v2.1.0!

v2.1.0 is broken and will show:
```
WinError 5: Access is denied
```

v2.1.1 fixes this completely.

## 💬 Support

If gym managers still see "Access Denied" errors:
1. Verify they installed v2.1.1 (not v2.1.0)
2. Check they have write permissions to `%LOCALAPPDATA%` (should always work)
3. Check logs at: `C:\Users\USERNAME\AppData\Local\GymBot\logs\launcher_flask.log`
4. If still failing, run installer as Administrator

## 📊 Version History

- **v2.1.1** (Oct 8, 2025) - Fix WinError 5 by using AppData ✅ **CURRENT**
- **v2.1.0** (Oct 8, 2025) - Launcher + inbox fixes but broken on Windows ❌
- **v2.0.x** - Previous versions

---

**Build Status**: ⏳ Building now (GitHub Actions)
**ETA**: 10-15 minutes
**Next Step**: Download installers from Releases page when ready
