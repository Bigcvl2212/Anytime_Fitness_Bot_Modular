#!/usr/bin/env python3
"""
Check the actual database schema to see what columns exist
"""

import sqlite3
import os

def check_schema():
    db_path = 'data/gym_bot.db'
    
    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔍 Checking database schema...")
        print("-" * 60)
        
        # Get table schema
        cursor.execute("PRAGMA table_info(members)")
        columns = cursor.fetchall()
        
        print("📋 Members table columns:")
        for col in columns:
            print(f"  {col[1]} ({col[2]})")
        
        # Check if our new columns exist
        print("\n🎯 Looking for our new columns:")
        target_fields = [
            'base_amount_past_due',
            'late_fees', 
            'missed_payments',
            'amount_past_due'
        ]
        
        existing_fields = [col[1] for col in columns]
        for field in target_fields:
            if field in existing_fields:
                print(f"✅ {field} - EXISTS")
            else:
                print(f"❌ {field} - MISSING")
        
        # Check what name field exists
        name_fields = [col[1] for col in columns if 'name' in col[1].lower()]
        print(f"\n📝 Name fields found: {name_fields}")
        
        # Check what status fields exist
        status_fields = [col[1] for col in columns if 'status' in col[1].lower()]
        print(f"📊 Status fields found: {status_fields}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error checking schema: {e}")

if __name__ == "__main__":
    check_schema()
