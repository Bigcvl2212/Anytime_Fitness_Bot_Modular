#!/usr/bin/env python3

import sqlite3
import json

def check_agreement_data():
    """Check what agreement data is stored in the database"""
    
    print("🔍 Checking Agreement Data in Database")
    print("=" * 50)
    
    conn = sqlite3.connect('gym_bot.db')
    cursor = conn.cursor()
    
    # Check members table structure and agreement data
    print("1. Members table structure:")
    cursor.execute("PRAGMA table_info(members)")
    member_columns = cursor.fetchall()
    for col in member_columns:
        print(f"   {col[1]} ({col[2]})")
    
    print("\n2. Sample member with past due data:")
    cursor.execute("""
        SELECT full_name, amount_past_due, status_message, agreement_recurring_cost
        FROM members 
        WHERE status_message LIKE '%Past Due%'
        LIMIT 3
    """)
    members = cursor.fetchall()
    for member in members:
        print(f"   {member[0]}:")
        print(f"     Past Due: ${member[1]}")
        print(f"     Status: {member[2]}")
        print(f"     Recurring Cost: ${member[3]}")
        print()
    
    print("3. Training clients table structure:")
    cursor.execute("PRAGMA table_info(training_clients)")
    training_columns = cursor.fetchall()
    for col in training_columns:
        print(f"   {col[1]} ({col[2]})")
    
    print("\n4. Sample training client with agreement data:")
    cursor.execute("""
        SELECT member_name, package_details, total_past_due, payment_status
        FROM training_clients 
        WHERE total_past_due > 0
        LIMIT 3
    """)
    training_clients = cursor.fetchall()
    for client in training_clients:
        print(f"   {client[0]}:")
        print(f"     Package Details: {client[1]}")
        print(f"     Past Due: ${client[2]}")
        print(f"     Status: {client[3]}")
        print()
    
    print("5. All columns that might contain agreement data:")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    for table in tables:
        table_name = table[0]
        if table_name in ['members', 'training_clients']:
            print(f"\n{table_name} table columns:")
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            for col in columns:
                if 'agreement' in col[1].lower() or 'package' in col[1].lower() or 'details' in col[1].lower():
                    print(f"   {col[1]} ({col[2]})")
    
    conn.close()

if __name__ == "__main__":
    check_agreement_data()
