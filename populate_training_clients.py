#!/usr/bin/env python3
"""
Populate training_clients table with real ClubOS training clients
"""

import sys
sys.path.append('.')

import sqlite3
from clubos_training_api import ClubOSTrainingPackageAPI
import json
import time

def populate_training_clients():
    """Find and populate the training_clients table with real ClubOS data"""
    
    api = ClubOSTrainingPackageAPI()
    if not api.authenticate():
        print("❌ Failed to authenticate with ClubOS")
        return
    
    print("🔍 Finding training clients from ClubOS...")
    
    # Connect to database
    conn = sqlite3.connect('gym_bot.db')
    cursor = conn.cursor()
    
    # Get all members from our local database
    cursor.execute("SELECT id, full_name, email FROM members WHERE status = '0' LIMIT 50")
    members = cursor.fetchall()
    
    print(f"📋 Testing payment status for {len(members)} active members...")
    
    training_clients_found = []
    
    for i, (member_id, full_name, email) in enumerate(members):
        print(f"   Testing {i+1}/{len(members)}: {full_name} (ID: {member_id})")
        
        try:
            # Test payment status
            payment_status = api.get_member_payment_status(str(member_id))
            
            if payment_status and payment_status != "Unknown":
                print(f"   ✅ {full_name}: {payment_status}")
                
                training_clients_found.append({
                    'member_id': member_id,
                    'member_name': full_name,
                    'clubos_member_id': member_id,
                    'payment_status': payment_status,
                    'email': email
                })
                
                # Check if this is Dennis
                if 'dennis' in full_name.lower() and 'rost' in full_name.lower():
                    print(f"   🎯 FOUND DENNIS AS TRAINING CLIENT!")
                    print(f"      Member ID: {member_id}")
                    print(f"      Payment Status: {payment_status}")
            else:
                print(f"   ⚪ {full_name}: No training status")
                
        except Exception as e:
            print(f"   ❌ Error testing {full_name}: {e}")
        
        # Rate limiting
        time.sleep(0.1)
    
    print(f"\n📊 Found {len(training_clients_found)} training clients")
    
    if training_clients_found:
        print(f"\n💾 Inserting training clients into database...")
        
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
                (member_id, member_name, clubos_member_id, payment_status, email, package_name)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                client['member_id'],
                client['member_name'], 
                client['clubos_member_id'],
                client['payment_status'],
                client['email'],
                'Training Package'  # Generic for now
            ))
        
        conn.commit()
        print(f"   ✅ Inserted {len(training_clients_found)} training clients")
        
        # Show Dennis specifically
        cursor.execute("""
            SELECT * FROM training_clients 
            WHERE LOWER(member_name) LIKE '%dennis%' AND LOWER(member_name) LIKE '%rost%'
        """)
        
        dennis_result = cursor.fetchone()
        if dennis_result:
            print(f"\n🎯 Dennis Rost in training_clients table:")
            print(f"   {dennis_result}")
        else:
            print(f"\n❌ Dennis Rost still not found in training_clients")
    
    conn.close()
    
    print(f"\n🧪 Testing funding lookup for Dennis after database update...")
    
    # Now test the funding lookup system
    try:
        from clean_dashboard import training_package_cache
        
        funding_data = training_package_cache.lookup_participant_funding("Dennis Rost")
        if funding_data:
            print(f"✅ Dennis funding lookup now works: {funding_data}")
        else:
            print(f"❌ Dennis funding lookup still failing")
            
    except Exception as e:
        print(f"❌ Error testing funding lookup: {e}")

if __name__ == "__main__":
    print("🔍 Populating training_clients table from ClubOS data...")
    print("=" * 60)
    
    populate_training_clients()
    
    print("\n" + "=" * 60)
    print("🏁 Training clients population complete!")
