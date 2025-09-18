#!/usr/bin/env python3
"""
Check which database has member data
"""

import os
import sqlite3

def check_database(db_path):
    """Check a database for member data"""
    try:
        if not os.path.exists(db_path):
            return f"❌ {db_path} does not exist"
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if members table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='members'")
        if not cursor.fetchone():
            conn.close()
            return f"❌ {db_path} has no 'members' table"
        
        # Count members
        cursor.execute("SELECT COUNT(*) FROM members")
        total_count = cursor.fetchone()[0]
        
        if total_count == 0:
            conn.close()
            return f"❌ {db_path} has 0 members"
        
        # Count active members
        cursor.execute("SELECT COUNT(*) FROM members WHERE status > 0")
        active_count = cursor.fetchone()[0]
        
        # Get sample member names
        cursor.execute("SELECT full_name, prospect_id, status_message FROM members LIMIT 3")
        sample_members = cursor.fetchall()
        
        conn.close()
        
        result = f"✅ {db_path}: {total_count} total members, {active_count} active"
        result += f"\n   Sample: {', '.join([f'{name} (ID:{pid})' for name, pid, _ in sample_members])}"
        return result
        
    except Exception as e:
        return f"❌ {db_path} error: {e}"

def main():
    databases = [
        'gym_bot.db',
        'gym_bot_local.db',
        'fitness_bot.db',
        'test.db',
        'gym_bot_test.db'
    ]
    
    print("🔍 Checking all database files for member data:\n")
    
    for db in databases:
        if os.path.exists(db):
            print(check_database(db))
        else:
            print(f"❌ {db} does not exist")
    
    print("\n🎯 Based on the Flask app configuration (src/main_app.py line 119):")
    print("   The app should be using: gym_bot.db")

if __name__ == "__main__":
    main()