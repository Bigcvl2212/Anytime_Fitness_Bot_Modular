#!/usr/bin/env python3
"""
Check which database has the staff_designations table
"""

import sqlite3
import os

def check_database(db_path, description):
    print(f"\n🔍 Checking {description}: {db_path}")
    
    if not os.path.exists(db_path):
        print(f"   ❌ Database file does not exist")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if staff_designations table exists
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='staff_designations'
    """)
    
    result = cursor.fetchone()
    
    if result:
        print(f"   ✅ staff_designations table EXISTS")
        
        # Check contents
        cursor.execute("SELECT COUNT(*) FROM staff_designations")
        count = cursor.fetchone()[0]
        print(f"   📊 Contains {count} records")
        
        # Show active records
        cursor.execute("""
            SELECT prospect_id, full_name, role 
            FROM staff_designations 
            WHERE is_active = TRUE
            ORDER BY full_name
        """)
        records = cursor.fetchall()
        
        for record in records:
            print(f"     • {record[1]} (ID: {record[0]})")
    else:
        print(f"   ❌ staff_designations table DOES NOT EXIST")
    
    # Check staff count in members table
    cursor.execute("""
        SELECT COUNT(*) FROM members 
        WHERE status_message LIKE '%Staff%'
    """)
    staff_count = cursor.fetchone()[0]
    print(f"   📊 Staff members in members table: {staff_count}")
    
    conn.close()

# Check both databases
root_db = r"c:\Users\mayoj\OneDrive\Documents\Gym-Bot\gym-bot\gym-bot-modular\gym_bot.db"
src_db = r"c:\Users\mayoj\OneDrive\Documents\Gym-Bot\gym-bot\gym-bot-modular\src\gym_bot.db"

check_database(root_db, "ROOT database")
check_database(src_db, "SRC database")