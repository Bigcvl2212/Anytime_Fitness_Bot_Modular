#!/usr/bin/env python3

import sqlite3

def check_past_due_status():
    """Check the actual past due status in the database"""
    
    print("🔍 Checking Past Due Status in Database")
    print("=" * 50)
    
    conn = sqlite3.connect('gym_bot.db')
    cursor = conn.cursor()
    
    # Check members with different past due criteria
    print("1. Members with amount_past_due > 0:")
    cursor.execute("SELECT full_name, amount_past_due, status_message FROM members WHERE amount_past_due > 0 LIMIT 5")
    members_amount = cursor.fetchall()
    for member in members_amount:
        print(f"   {member[0]}: ${member[1]} - {member[2]}")
    
    print(f"\n   Total: {len(members_amount)} members")
    
    print("\n2. Members with Past Due status message:")
    cursor.execute("""
        SELECT full_name, amount_past_due, status_message 
        FROM members 
        WHERE status_message LIKE '%Past Due 6-30 days%' 
           OR status_message LIKE '%Past Due more than 30 days%'
        LIMIT 5
    """)
    members_status = cursor.fetchall()
    for member in members_status:
        print(f"   {member[0]}: ${member[1]} - {member[2]}")
    
    print(f"\n   Total: {len(members_status)} members")
    
    print("\n3. All unique status messages:")
    cursor.execute("SELECT DISTINCT status_message FROM members WHERE status_message IS NOT NULL AND status_message != ''")
    status_messages = cursor.fetchall()
    for status in status_messages:
        print(f"   - {status[0]}")
    
    print("\n4. Training clients with total_past_due > 0:")
    cursor.execute("SELECT member_name, total_past_due, payment_status FROM training_clients WHERE total_past_due > 0 LIMIT 5")
    training_amount = cursor.fetchall()
    for client in training_amount:
        print(f"   {client[0]}: ${client[1]} - {client[2]}")
    
    print(f"\n   Total: {len(training_amount)} training clients")
    
    print("\n5. Training clients with past_due_amount > 0:")
    cursor.execute("SELECT member_name, past_due_amount, payment_status FROM training_clients WHERE past_due_amount > 0 LIMIT 5")
    training_past_due = cursor.fetchall()
    for client in training_past_due:
        print(f"   {client[0]}: ${client[1]} - {client[2]}")
    
    print(f"\n   Total: {len(training_past_due)} training clients")
    
    conn.close()

if __name__ == "__main__":
    check_past_due_status()
