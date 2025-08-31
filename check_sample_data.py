#!/usr/bin/env python3
"""
Check sample data to see what's actually in the database
"""

import sqlite3
import os

def check_sample_data():
    db_path = 'data/gym_bot.db'
    
    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔍 Checking sample data from database...")
        print("-" * 60)
        
        # Check total member count
        cursor.execute("SELECT COUNT(*) FROM members")
        total_count = cursor.fetchone()[0]
        print(f"📊 Total members in database: {total_count}")
        
        # Check what status_message values exist
        cursor.execute("SELECT DISTINCT status_message FROM members WHERE status_message IS NOT NULL LIMIT 10")
        statuses = cursor.fetchall()
        print(f"\n📋 Sample status_message values:")
        for status in statuses:
            print(f"  {status[0]}")
        
        # Check what past_due_amount values exist
        cursor.execute("SELECT COUNT(*) FROM members WHERE past_due_amount > 0")
        past_due_count = cursor.fetchone()[0]
        print(f"\n💰 Members with past_due_amount > 0: {past_due_count}")
        
        # Check sample members with past due amounts
        cursor.execute("""
            SELECT name, status_message, past_due_amount, base_amount_past_due, late_fees, missed_payments
            FROM members 
            WHERE past_due_amount > 0 
            LIMIT 5
        """)
        
        results = cursor.fetchall()
        if results:
            print(f"\n📊 Sample members with past due amounts:")
            for row in results:
                name, status, past_due, base, late, missed = row
                print(f"👤 {name}")
                print(f"   Status: {status}")
                print(f"   past_due_amount: ${past_due:.2f}")
                print(f"   base_amount_past_due: ${base or 0:.2f}")
                print(f"   late_fees: ${late or 0:.2f}")
                print(f"   missed_payments: {missed or 0}")
                print("-" * 40)
        else:
            print("❌ No members with past due amounts found")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error checking data: {e}")

if __name__ == "__main__":
    check_sample_data()
