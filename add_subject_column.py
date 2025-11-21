#!/usr/bin/env python3
"""
Add subject column to messages table
"""

import sqlite3
import sys
import os

# Add workspace root to path
workspace_root = os.path.abspath(os.path.dirname(__file__))
if workspace_root not in sys.path:
    sys.path.insert(0, workspace_root)

def add_subject_column():
    """Add subject column to messages table"""
    db_path = os.path.join(workspace_root, 'gym_bot.db')

    print(f"Adding subject column to messages table in {db_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check if column already exists
        cursor.execute("PRAGMA table_info(messages)")
        columns = [col[1] for col in cursor.fetchall()]

        if 'subject' in columns:
            print("OK: subject column already exists")
        else:
            # Add subject column
            cursor.execute("""
                ALTER TABLE messages
                ADD COLUMN subject TEXT
            """)
            conn.commit()
            print("OK: Added subject column to messages table")

        conn.close()
        return True

    except Exception as e:
        print(f"ERROR: {e}")
        conn.close()
        return False

if __name__ == '__main__':
    success = add_subject_column()
    sys.exit(0 if success else 1)
