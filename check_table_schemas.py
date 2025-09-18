#!/usr/bin/env python3
"""
Check column names in both training_clients and members tables
"""

import sqlite3

def check_table_schemas():
    """Check the actual column names in both tables"""
    print("🔍 CHECKING: Table schemas for name matching")
    print("=" * 60)
    
    try:
        # Connect to database
        conn = sqlite3.connect('gym_bot.db')
        cursor = conn.cursor()
        
        # Get training_clients schema
        print("📋 TRAINING_CLIENTS table columns:")
        cursor.execute("PRAGMA table_info(training_clients)")
        training_columns = cursor.fetchall()
        
        for col in training_columns:
            print(f"   {col[1]} ({col[2]})")
        
        print(f"\n📋 MEMBERS table columns:")
        cursor.execute("PRAGMA table_info(members)")
        member_columns = cursor.fetchall()
        
        for col in member_columns:
            print(f"   {col[1]} ({col[2]})")
        
        # Sample data from both tables to see name formats
        print(f"\n📄 Sample training_clients names:")
        cursor.execute("SELECT member_name, first_name, last_name FROM training_clients WHERE member_name IS NOT NULL LIMIT 5")
        training_samples = cursor.fetchall()
        
        for sample in training_samples:
            print(f"   member_name: '{sample[0]}', first_name: '{sample[1]}', last_name: '{sample[2]}'")
        
        print(f"\n📄 Sample members names:")
        cursor.execute("SELECT full_name, first_name, last_name FROM members WHERE full_name IS NOT NULL LIMIT 5")
        member_samples = cursor.fetchall()
        
        for sample in member_samples:
            print(f"   full_name: '{sample[0]}', first_name: '{sample[1]}', last_name: '{sample[2]}'")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error checking schemas: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_table_schemas()