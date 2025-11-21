#!/usr/bin/env python3
"""
Get details about the 11 past due training clients
"""

import sqlite3
import json

def main():
    print("🔍 DETAILED VIEW: Past Due Training Clients")
    print("=" * 50)
    
    try:
        # Connect to database
        conn = sqlite3.connect('gym_bot.db')
        cursor = conn.cursor()
        
        # Get all past due training clients
        cursor.execute("SELECT * FROM training_clients WHERE payment_status = 'Past Due'")
        past_due_clients = cursor.fetchall()
        
        # Get column names
        cursor.execute("PRAGMA table_info(training_clients)")
        schema = cursor.fetchall()
        columns = [col[1] for col in schema]
        
        print(f"📊 Found {len(past_due_clients)} past due training clients")
        print("=" * 50)
        
        for i, client_row in enumerate(past_due_clients):
            client = dict(zip(columns, client_row))
            
            print(f"\n🚨 Past Due Client #{i+1}:")
            print(f"   Name: {client['member_name']}")
            print(f"   Member ID: {client['member_id']}")
            print(f"   ClubOS ID: {client['clubos_member_id']}")
            print(f"   Email: {client['email']}")
            print(f"   Phone: {client['phone']}")
            print(f"   Payment Status: {client['payment_status']}")
            print(f"   Past Due Amount: ${client['past_due_amount']:.2f}")
            print(f"   Total Past Due: ${client['total_past_due']:.2f}")
            print(f"   Trainer: {client['trainer_name']}")
            print(f"   Package Summary: {client['package_summary']}")
            print(f"   Financial Summary: {client['financial_summary']}")
            
            # Parse package_details if available
            if client['package_details']:
                try:
                    package_details = json.loads(client['package_details'])
                    print(f"   Package Details:")
                    for package in package_details:
                        print(f"     - {package.get('package_name')}: ${package.get('amount_owed', 0):.2f}")
                except:
                    print(f"   Package Details: {client['package_details'][:100]}...")
        
        print(f"\n📋 SUMMARY:")
        print(f"   • {len(past_due_clients)} training clients are past due")
        print(f"   • These clients are NOT showing up in campaigns")
        print(f"   • Campaign system only looks at 'members' table")
        print(f"   • Need to modify campaign system to include training_clients table")
        
        # Check if any of these clients also exist in members table
        print(f"\n🔍 Cross-checking with members table:")
        training_client_names = [dict(zip(columns, row))['member_name'] for row in past_due_clients]
        
        for name in training_client_names:
            cursor.execute("SELECT status_message FROM members WHERE TRIM(LOWER(name)) = TRIM(LOWER(?))", (name,))
            member_status = cursor.fetchone()
            if member_status:
                print(f"   ✅ {name}: Also in members table with status '{member_status[0]}'")
            else:
                print(f"   ❌ {name}: NOT in members table (training client only)")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error getting past due training clients: {e}")

if __name__ == "__main__":
    main()