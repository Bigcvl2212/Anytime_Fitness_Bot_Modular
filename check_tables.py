#!/usr/bin/env python3
"""
Check database tables
"""

import sqlite3

def check_tables():
    """Check what tables exist in gym_bot.db"""
    try:
        conn = sqlite3.connect('gym_bot.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print("📊 Database Tables:")
        for table in tables:
            print(f"  - {table[0]}")
            
        # Check if bulk_checkin_runs table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='bulk_checkin_runs'")
        bulk_table = cursor.fetchone()
        
        if bulk_table:
            print("\n✅ bulk_checkin_runs table exists")
            cursor.execute("SELECT * FROM bulk_checkin_runs LIMIT 5")
            runs = cursor.fetchall()
            print(f"   Found {len(runs)} runs")
        else:
            print("\n❌ bulk_checkin_runs table does NOT exist")
            
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_tables()