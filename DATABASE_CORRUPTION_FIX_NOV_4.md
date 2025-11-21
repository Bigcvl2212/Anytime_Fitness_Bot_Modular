# Database Corruption Fix - November 4, 2025

## Problem

The `gym_bot.db` database file got corrupted during the git restore operation. This happened because git tried to overwrite the file while it was open.

**Error:**
```
sqlite3.DatabaseError: malformed database schema (20)
```

---

## The Issue

The database file is **LOCKED** by another process and cannot be renamed/replaced while it's open.

**Likely causes:**
1. Python process still running in background
2. DB Browser or another SQLite tool has it open
3. Windows file explorer previewing it
4. Previous Flask app process still alive

---

## Solution: Manual Database Recovery

### Step 1: Close ALL Programs
1. **Close ALL Python/Terminal windows**
2. **Close DB Browser for SQLite** (if open)
3. **Close any file explorers** viewing the gym-bot folder
4. **Check Task Manager** for any `python.exe` processes and END them

### Step 2: Manually Rename the Corrupted Database

Open PowerShell in your project folder and run:

```powershell
cd "C:\Users\mayoj\OneDrive\Documents\Gym-Bot\gym-bot\gym-bot-modular"

# Rename the corrupted database
Rename-Item "gym_bot.db" "gym_bot_CORRUPTED.db"

# Copy the backup
Copy-Item "gym_bot_backup_20250914_142515.db" "gym_bot.db"
```

### Step 3: Verify the Database

```powershell
python -c "import sqlite3; conn = sqlite3.connect('gym_bot.db'); cursor = conn.cursor(); cursor.execute('SELECT COUNT(*) FROM members'); print(f'Members: {cursor.fetchone()[0]}'); cursor.execute('SELECT COUNT(*) FROM prospects'); print(f'Prospects: {cursor.fetchone()[0]}'); conn.close()"
```

---

## Alternative: Fresh Database (If Backup Doesn't Work)

If the backup database is also corrupted, create a fresh one:

```powershell
# Remove old database (after closing all programs!)
Remove-Item "gym_bot.db" -Force

# Create fresh database
python -c "import sqlite3; conn = sqlite3.connect('gym_bot.db'); cursor = conn.cursor(); cursor.execute('CREATE TABLE members (id INTEGER PRIMARY KEY, prospect_id TEXT, first_name TEXT, last_name TEXT, full_name TEXT, email TEXT, mobile_phone TEXT, status TEXT, amount_past_due REAL, member_type TEXT, club_name TEXT)'); cursor.execute('CREATE TABLE prospects (id INTEGER PRIMARY KEY, prospect_id TEXT, first_name TEXT, last_name TEXT, full_name TEXT, email TEXT, mobile_phone TEXT, status TEXT, club_name TEXT)'); cursor.execute('CREATE TABLE training_clients (id INTEGER PRIMARY KEY, client_id TEXT, member_name TEXT, email TEXT, phone TEXT, past_due_amount REAL)'); conn.commit(); conn.close(); print('Fresh database created')"
```

**Note:** A fresh database will be empty. Data will sync on next login when you select your clubs.

---

## Quick PowerShell Commands (Copy/Paste All at Once)

```powershell
cd "C:\Users\mayoj\OneDrive\Documents\Gym-Bot\gym-bot\gym-bot-modular"

# Stop any Python processes
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force

# Wait a moment
Start-Sleep -Seconds 2

# Rename corrupted database
Rename-Item "gym_bot.db" "gym_bot_CORRUPTED_backup.db" -Force

# Copy backup to main database
Copy-Item "gym_bot_backup_20250914_142515.db" "gym_bot.db" -Force

Write-Host "Database restored! Run: python run_dashboard.py"
```

---

## After Database is Fixed

Once you can rename/replace the database:

1. **Start the app:**
   ```bash
   python run_dashboard.py
   ```

2. **Login** at http://localhost:5000

3. **Select your clubs** - This will trigger a fresh data sync

4. **All your data will be re-synced** from ClubOS/ClubHub

---

## Prevention

To prevent this in the future:
1. **Always close the app** before doing git operations
2. **Never git checkout** while Python is running
3. **Use backups** - The app has automatic backup functionality

---

## Current Status

✅ **Backup exists:** `gym_bot_backup_20250914_142515.db` (2.0 MB from Sept 14)
✅ **Corruption identified:** malformed schema
✅ **Fix ready:** Just need to close programs and rename file

**Next step:** Close all programs, then copy/paste the PowerShell commands above
