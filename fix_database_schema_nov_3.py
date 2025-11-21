"""
Database Schema Fix - November 3, 2025
Adds missing columns to members and training_clients tables after feature restoration
"""

import sqlite3
import sys

DB_PATH = 'gym_bot.db'

def fix_database_schema():
    """Add all missing columns to database tables"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("=" * 60)
    print("DATABASE SCHEMA FIX - November 3, 2025")
    print("=" * 60)

    # Fix 1: Add prospect_id to members table (if it doesn't exist)
    print("\n1. Checking members table for prospect_id column...")
    cursor.execute("PRAGMA table_info(members)")
    members_columns = [column[1] for column in cursor.fetchall()]

    if 'prospect_id' not in members_columns:
        print("   Adding prospect_id to members table...")
        cursor.execute("ALTER TABLE members ADD COLUMN prospect_id TEXT")
        conn.commit()
        print("   [OK] Added prospect_id column to members table")
    else:
        print("   [OK] prospect_id column already exists in members table")

    # Fix 2: Check training_clients table
    print("\n2. Checking training_clients table columns...")
    cursor.execute("PRAGMA table_info(training_clients)")
    training_columns = [column[1] for column in cursor.fetchall()]

    print(f"   Training clients columns: {', '.join(training_columns)}")

    # Fix 3: Update member prospect_ids from id if they're null
    print("\n3. Updating null prospect_ids in members table...")
    cursor.execute("""
        UPDATE members
        SET prospect_id = CAST(id AS TEXT)
        WHERE prospect_id IS NULL OR prospect_id = ''
    """)
    rows_updated = cursor.rowcount
    conn.commit()
    print(f"   [OK] Updated {rows_updated} members with prospect_id from id")

    # Fix 4: Verify members table has all needed columns
    print("\n4. Verifying members table schema...")
    needed_columns = ['id', 'prospect_id', 'first_name', 'last_name', 'full_name',
                     'email', 'mobile_phone', 'status', 'status_message', 'amount_past_due']
    missing_columns = [col for col in needed_columns if col not in members_columns]

    if missing_columns:
        print(f"   WARNING: Members table missing columns: {', '.join(missing_columns)}")
    else:
        print("   [OK] All required columns exist in members table")

    # Fix 5: Verify training_clients table
    print("\n5. Verifying training_clients table schema...")
    needed_training_cols = ['id', 'clubos_member_id', 'member_name', 'mobile_phone', 'total_past_due']
    missing_training = [col for col in needed_training_cols if col not in training_columns]

    if missing_training:
        print(f"   WARNING: Training_clients missing columns: {', '.join(missing_training)}")
    else:
        print("   [OK] All required columns exist in training_clients table")

    # Show statistics
    print("\n" + "=" * 60)
    print("DATABASE STATISTICS")
    print("=" * 60)

    cursor.execute("SELECT COUNT(*) FROM members")
    member_count = cursor.fetchone()[0]
    print(f"Total members: {member_count}")

    cursor.execute("SELECT COUNT(*) FROM members WHERE prospect_id IS NOT NULL AND prospect_id != ''")
    members_with_prospect_id = cursor.fetchone()[0]
    print(f"Members with prospect_id: {members_with_prospect_id}")

    cursor.execute("SELECT COUNT(*) FROM prospects")
    prospect_count = cursor.fetchone()[0]
    print(f"Total prospects: {prospect_count}")

    cursor.execute("SELECT COUNT(*) FROM training_clients")
    training_count = cursor.fetchone()[0]
    print(f"Total training clients: {training_count}")

    conn.close()

    print("\n" + "=" * 60)
    print("[SUCCESS] DATABASE SCHEMA FIX COMPLETE")
    print("=" * 60)
    print("\nYou can now restart the Flask application.")

if __name__ == "__main__":
    try:
        fix_database_schema()
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
