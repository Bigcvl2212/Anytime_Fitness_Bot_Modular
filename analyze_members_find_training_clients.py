#!/usr/bin/env python3
"""
Check member status values and find training clients properly
"""

import sys
sys.path.append('.')

import sqlite3
from clubos_training_api import ClubOSTrainingPackageAPI
import json
import time

def analyze_members_and_find_training_clients():
    """Analyze member data and properly find training clients"""
    
    # Connect to database
    conn = sqlite3.connect('gym_bot.db')
    cursor = conn.cursor()
    
    print("📊 Analyzing members table...")
    
    # Check different status values
    cursor.execute("SELECT status, COUNT(*) FROM members GROUP BY status")
    status_counts = cursor.fetchall()
    
    print(f"   Status distribution:")
    for status, count in status_counts:
        print(f"     Status '{status}': {count} members")
    
    # Check status messages
    cursor.execute("SELECT status_message, COUNT(*) FROM members GROUP BY status_message LIMIT 10")
    status_message_counts = cursor.fetchall()
    
    print(f"\n   Top status messages:")
    for status_msg, count in status_message_counts:
        print(f"     '{status_msg}': {count} members")
    
    # Look for all Dennis entries again
    cursor.execute("""
        SELECT id, full_name, status, status_message, membership_start, last_visit 
        FROM members 
        WHERE LOWER(full_name) LIKE '%dennis%' AND LOWER(full_name) LIKE '%rost%'
    """)
    
    dennis_members = cursor.fetchall()
    print(f"\n🔍 Dennis Rost entries:")
    for member in dennis_members:
        member_id, name, status, status_msg, start, last_visit = member
        print(f"   ID: {member_id}, Name: {name}")
        print(f"   Status: '{status}', Message: '{status_msg}'")
        print(f"   Start: {start}, Last Visit: {last_visit}")
        print()
    
    # Get recent active members (non-PPV)
    cursor.execute("""
        SELECT id, full_name, status, status_message 
        FROM members 
        WHERE status_message NOT LIKE '%Pay per visit%'
        AND status_message NOT LIKE '%Cancelled%'
        AND last_visit > date('now', '-6 months')
        ORDER BY last_visit DESC
        LIMIT 20
    """)
    
    recent_members = cursor.fetchall()
    print(f"📋 Testing {len(recent_members)} recent active members for training status...")
    
    api = ClubOSTrainingPackageAPI()
    if not api.authenticate():
        print("❌ Failed to authenticate with ClubOS")
        return
    
    training_clients_found = []
    
    for i, (member_id, full_name, status, status_msg) in enumerate(recent_members):
        print(f"   Testing {i+1}/{len(recent_members)}: {full_name} (ID: {member_id})")
        print(f"     Status: '{status}', Message: '{status_msg}'")
        
        try:
            # Test payment status
            payment_status = api.get_member_payment_status(str(member_id))
            
            if payment_status and payment_status != "Unknown":
                print(f"     ✅ TRAINING CLIENT: {payment_status}")
                
                training_clients_found.append({
                    'member_id': member_id,
                    'member_name': full_name,
                    'clubos_member_id': member_id,
                    'payment_status': payment_status,
                    'member_status': status,
                    'status_message': status_msg
                })
                
                # Check if this is Dennis
                if 'dennis' in full_name.lower() and 'rost' in full_name.lower():
                    print(f"     🎯 FOUND DENNIS AS TRAINING CLIENT!")
                    print(f"        Member ID: {member_id}")
                    print(f"        Payment Status: {payment_status}")
                    print(f"        Member Status: {status}")
                    print(f"        Status Message: {status_msg}")
            else:
                print(f"     ⚪ No training status")
                
        except Exception as e:
            print(f"     ❌ Error: {e}")
        
        # Rate limiting
        time.sleep(0.2)
    
    print(f"\n🎯 Found {len(training_clients_found)} training clients:")
    for client in training_clients_found:
        print(f"   {client['member_name']}: {client['payment_status']}")
    
    if training_clients_found:
        print(f"\n💾 Updating training_clients table...")
        
        # Create training_clients table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS training_clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                member_id INTEGER,
                member_name TEXT,
                clubos_member_id TEXT,
                package_name TEXT,
                sessions_remaining INTEGER,
                sessions_purchased INTEGER,
                package_amount REAL,
                amount_paid REAL,
                amount_due REAL,
                payment_status TEXT,
                last_session_date TEXT,
                next_billing_date TEXT,
                email TEXT,
                phone TEXT,
                emergency_contact TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Clear existing data
        cursor.execute("DELETE FROM training_clients")
        
        # Insert training clients
        for client in training_clients_found:
            cursor.execute('''
                INSERT INTO training_clients 
                (member_id, member_name, clubos_member_id, payment_status, package_name)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                client['member_id'],
                client['member_name'], 
                client['clubos_member_id'],
                client['payment_status'],
                'Training Package'
            ))
        
        conn.commit()
        print(f"   ✅ Inserted {len(training_clients_found)} training clients")
        
        # Verify Dennis is now in training_clients
        cursor.execute("""
            SELECT * FROM training_clients 
            WHERE LOWER(member_name) LIKE '%dennis%' AND LOWER(member_name) LIKE '%rost%'
        """)
        
        dennis_result = cursor.fetchone()
        if dennis_result:
            print(f"\n🎯 Dennis Rost now in training_clients table:")
            print(f"   ID: {dennis_result[0]}")
            print(f"   Member ID: {dennis_result[1]}")
            print(f"   Name: {dennis_result[2]}")
            print(f"   ClubOS ID: {dennis_result[3]}")
            print(f"   Payment Status: {dennis_result[10]}")
        else:
            print(f"\n❌ Dennis Rost still not found in training_clients")
    
    conn.close()

if __name__ == "__main__":
    print("📊 Analyzing members and finding training clients...")
    print("=" * 60)
    
    analyze_members_and_find_training_clients()
    
    print("\n" + "=" * 60)
    print("🏁 Analysis complete!")
