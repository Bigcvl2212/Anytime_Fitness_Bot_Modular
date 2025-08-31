#!/usr/bin/env python3
"""
Check if the updated member data with calculated fields is in the database
"""

import sqlite3
import os

def check_updated_data():
    db_path = 'data/gym_bot.db'
    
    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔍 Checking for updated member data with calculated fields...")
        print("-" * 60)
        
        # Check for past due members with the new calculated fields
        cursor.execute("""
            SELECT name, status_message, base_amount_past_due, late_fees, 
                   missed_payments, amount_past_due, agreement_recurring_cost
            FROM members 
            WHERE status_message LIKE '%Past Due%' 
            LIMIT 10
        """)
        
        results = cursor.fetchall()
        
        if results:
            print("📊 Past Due Members - Current Data:")
            for row in results:
                name, status, base, late, missed, total, recurring = row
                print(f"👤 {name}")
                print(f"   Status: {status}")
                print(f"   Base Amount: ${base or 0:.2f}")
                print(f"   Late Fees: ${late or 0:.2f}")
                print(f"   Missed Payments: {missed or 0}")
                print(f"   Total Owed: ${total or 0:.2f}")
                print(f"   Recurring Cost: ${recurring or 0:.2f}")
                print("-" * 40)
        else:
            print("❌ No past due members found")
        
        # Check specific members we know about
        print("\n🎯 Checking Specific Members:")
        print("-" * 60)
        
        specific_members = ['DALE ROEN', 'Miguel Belmontes', 'ANGELA GIVENS']
        for member_name in specific_members:
            cursor.execute("""
                SELECT name, status_message, base_amount_past_due, late_fees, 
                       missed_payments, amount_past_due, agreement_recurring_cost
                FROM members 
                WHERE name = ?
            """, (member_name,))
            
            result = cursor.fetchone()
            if result:
                name, status, base, late, missed, total, recurring = result
                print(f"👤 {name}")
                print(f"   Status: {status}")
                print(f"   Base Amount: ${base or 0:.2f}")
                print(f"   Late Fees: ${late or 0:.2f}")
                print(f"   Missed Payments: {missed or 0}")
                print(f"   Total Owed: ${total or 0:.2f}")
                print(f"   Recurring Cost: ${recurring or 0:.2f}")
                print("-" * 40)
            else:
                print(f"❌ Member not found: {member_name}")
        
        # Check field population status
        print("\n🔢 Field Population Status:")
        print("-" * 60)
        
        cursor.execute("SELECT COUNT(*) FROM members WHERE base_amount_past_due IS NOT NULL AND base_amount_past_due > 0")
        base_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM members WHERE late_fees IS NOT NULL AND late_fees > 0")
        late_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM members WHERE missed_payments IS NOT NULL AND missed_payments > 0")
        missed_count = cursor.fetchone()[0]
        
        print(f"Members with base_amount_past_due > 0: {base_count}")
        print(f"Members with late_fees > 0: {late_count}")
        print(f"Members with missed_payments > 0: {missed_count}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error checking data: {e}")

if __name__ == "__main__":
    check_updated_data()
