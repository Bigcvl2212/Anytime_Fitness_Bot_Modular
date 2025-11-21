#!/usr/bin/env python3
"""
Force Fix Database - Remove locks and restore
"""
import os
import shutil
import time

print("=" * 60)
print("FORCE DATABASE FIX")
print("=" * 60)

# Step 1: Remove WAL and SHM files (these hold the locks)
lock_files = ['gym_bot.db-wal', 'gym_bot.db-shm']
for lock_file in lock_files:
    if os.path.exists(lock_file):
        try:
            os.remove(lock_file)
            print(f"Removed lock file: {lock_file}")
        except Exception as e:
            print(f"Could not remove {lock_file}: {e}")

# Give it a moment
time.sleep(1)

# Step 2: Try to rename the database
try:
    if os.path.exists('gym_bot.db'):
        os.rename('gym_bot.db', 'gym_bot_CORRUPTED.db')
        print("Renamed corrupted database to gym_bot_CORRUPTED.db")
except Exception as e:
    print(f"Could not rename database: {e}")
    print("\nTrying alternative method...")

    # Alternative: Copy over it
    try:
        shutil.copy2('gym_bot_backup_20250914_142515.db', 'gym_bot_TEMP.db')
        print("Created temporary database copy")

        # Try to replace
        if os.path.exists('gym_bot.db'):
            os.replace('gym_bot_TEMP.db', 'gym_bot.db')
            print("Replaced corrupted database!")
        else:
            os.rename('gym_bot_TEMP.db', 'gym_bot.db')
            print("Created new database!")

    except Exception as e2:
        print(f"Alternative method also failed: {e2}")
        exit(1)

# Step 3: Copy backup
if not os.path.exists('gym_bot.db') or os.path.getsize('gym_bot.db') < 100000:
    try:
        shutil.copy2('gym_bot_backup_20250914_142515.db', 'gym_bot.db')
        print("Copied backup to gym_bot.db")
    except Exception as e:
        print(f"Could not copy backup: {e}")

# Step 4: Verify
import sqlite3
try:
    conn = sqlite3.connect('gym_bot.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM members")
    member_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM prospects")
    prospect_count = cursor.fetchone()[0]
    conn.close()

    print(f"\nDatabase FIXED!")
    print(f"Members: {member_count}")
    print(f"Prospects: {prospect_count}")
    print("\nYou can now run: python run_dashboard.py")

except Exception as e:
    print(f"\nDatabase verification failed: {e}")
    print("You may need to create a fresh database")
