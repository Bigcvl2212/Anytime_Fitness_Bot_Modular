#!/usr/bin/env python3
"""
Quick check if staff_designations table exists
"""

import sqlite3
import os

# Database path
db_path = 'gym_bot.db'

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if staff_designations table exists
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='staff_designations'
    """)
    
    result = cursor.fetchone()
    
    if result:
        print("✅ staff_designations table EXISTS")
        
        # Check contents
        cursor.execute("SELECT COUNT(*) FROM staff_designations")
        count = cursor.fetchone()[0]
        print(f"📊 Contains {count} records")
        
        # Show all records
        cursor.execute("SELECT * FROM staff_designations")
        records = cursor.fetchall()
        
        for record in records:
            print(f"   Record: {record}")
    else:
        print("❌ staff_designations table DOES NOT EXIST")
        
        # Show what tables do exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"\nExisting tables:")
        for table in tables:
            print(f"   - {table[0]}")
    
    conn.close()
else:
    print(f"❌ Database file not found: {db_path}")