#!/usr/bin/env python3
"""Debug database connection and schema"""

import sqlite3
import os

def main():
    print("=== Database Debug ===")
    
    # Check if database file exists
    db_path = 'gym_bot.db'
    print(f"Database file exists: {os.path.exists(db_path)}")
    if os.path.exists(db_path):
        print(f"Database file size: {os.path.getsize(db_path)} bytes")
    
    try:
        # Try to connect
        print("\nTrying to connect to database...")
        conn = sqlite3.connect(db_path)
        print("✅ Database connection successful")
        
        cursor = conn.cursor()
        
        # Check tables
        print("\nChecking tables...")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"Tables found: {len(tables)}")
        for table in tables:
            print(f"  - {table[0]}")
        
        # Check members table specifically
        if any('members' in table[0].lower() for table in tables):
            print("\nChecking members table...")
            cursor.execute("PRAGMA table_info(members)")
            columns = cursor.fetchall()
            print(f"Members table columns: {len(columns)}")
            for col in columns:
                print(f"  - {col[1]} ({col[2]})")
            
            # Check sample data
            cursor.execute("SELECT COUNT(*) FROM members")
            count = cursor.fetchone()[0]
            print(f"Members table row count: {count}")
            
            if count > 0:
                cursor.execute("SELECT * FROM members LIMIT 1")
                sample = cursor.fetchone()
                print(f"Sample row: {sample}")
        else:
            print("\n❌ No members table found")
        
        conn.close()
        print("\n✅ Database check completed")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
