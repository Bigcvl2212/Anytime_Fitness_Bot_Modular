#!/usr/bin/env python3
"""
Fix Corrupted Database - November 4, 2025
"""

import sqlite3
import os
import shutil
from datetime import datetime

def backup_corrupted_db():
    """Backup the corrupted database"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    corrupted_backup = f'gym_bot_corrupted_{timestamp}.db'

    if os.path.exists('gym_bot.db'):
        print(f"Backing up corrupted database to {corrupted_backup}...")
        shutil.copy2('gym_bot.db', corrupted_backup)
        print(f"Backup created: {corrupted_backup}")
        return True
    return False

def try_recover_database():
    """Try to recover the database using dump/restore"""
    print("\nAttempting to recover database...")

    try:
        # Try to connect and dump
        conn = sqlite3.connect('gym_bot.db')

        # Try to dump the database
        with open('gym_bot_dump.sql', 'w', encoding='utf-8') as f:
            for line in conn.iterdump():
                f.write(f'{line}\n')

        conn.close()
        print("Successfully dumped database to gym_bot_dump.sql")

        # Remove corrupted database
        os.remove('gym_bot.db')
        print("Removed corrupted database")

        # Create new database from dump
        conn = sqlite3.connect('gym_bot.db')
        with open('gym_bot_dump.sql', 'r', encoding='utf-8') as f:
            conn.executescript(f.read())
        conn.close()

        print("Successfully recovered database!")
        return True

    except Exception as e:
        print(f"Recovery failed: {e}")
        return False

def use_backup_database():
    """Use the backup database"""
    print("\nUsing backup database...")

    backup_files = [
        'gym_bot_backup_20250914_142515.db',
        'gym_bot_local.db'
    ]

    for backup_file in backup_files:
        if os.path.exists(backup_file):
            print(f"Found backup: {backup_file}")

            # Try to rename instead of delete (works even if file is locked)
            if os.path.exists('gym_bot.db'):
                try:
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    os.rename('gym_bot.db', f'gym_bot_old_{timestamp}.db')
                    print("Renamed corrupted database")
                except Exception as e:
                    print(f"Could not rename: {e}")
                    print("Please close any programs using gym_bot.db and run this script again")
                    return False

            # Copy backup to main database
            shutil.copy2(backup_file, 'gym_bot.db')
            print(f"Restored database from {backup_file}")

            # Verify it works
            try:
                conn = sqlite3.connect('gym_bot.db')
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM members")
                member_count = cursor.fetchone()[0]
                cursor.execute("SELECT COUNT(*) FROM prospects")
                prospect_count = cursor.fetchone()[0]
                conn.close()

                print(f"Database verified: {member_count} members, {prospect_count} prospects")
                return True
            except Exception as e:
                print(f"Backup database also corrupted: {e}")
                continue

    print("No working backup found")
    return False

def create_fresh_database():
    """Create a fresh database with proper schema"""
    print("\nCreating fresh database...")

    if os.path.exists('gym_bot.db'):
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            os.rename('gym_bot.db', f'gym_bot_old_{timestamp}.db')
            print("Renamed old database")
        except Exception as e:
            print(f"Could not rename old database: {e}")
            print("Please close any programs using gym_bot.db and run this script again")
            return False

    conn = sqlite3.connect('gym_bot.db')
    cursor = conn.cursor()

    # Create basic tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prospect_id TEXT,
            guid TEXT,
            club_id TEXT,
            first_name TEXT,
            last_name TEXT,
            full_name TEXT,
            email TEXT,
            mobile_phone TEXT,
            status TEXT,
            amount_past_due REAL DEFAULT 0,
            member_type TEXT,
            club_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS prospects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prospect_id TEXT,
            guid TEXT,
            club_id TEXT,
            first_name TEXT,
            last_name TEXT,
            full_name TEXT,
            email TEXT,
            mobile_phone TEXT,
            status TEXT,
            club_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS training_clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id TEXT,
            member_name TEXT,
            email TEXT,
            phone TEXT,
            trainer_name TEXT,
            package_name TEXT,
            sessions_remaining INTEGER,
            past_due_amount REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()

    print("Fresh database created with basic schema")
    print("Note: Database is empty - sync will populate it on next login")
    return True

def main():
    print("=" * 60)
    print("DATABASE CORRUPTION FIX")
    print("=" * 60)

    # Step 1: Backup corrupted database
    backup_corrupted_db()

    # Step 2: Try to recover
    if try_recover_database():
        print("\n✅ Database recovered successfully!")
        return

    # Step 3: Try backup database
    if use_backup_database():
        print("\n✅ Database restored from backup!")
        return

    # Step 4: Create fresh database
    if create_fresh_database():
        print("\n✅ Fresh database created!")
        print("\nNote: Database is empty. Data will be synced on next login.")
        return

    print("\n❌ Could not fix database")

if __name__ == '__main__':
    main()
