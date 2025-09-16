#!/usr/bin/env python3
"""
Populate training_clients table with real ClubOS training clients
"""

import sys
import os

# Ensure project root is on sys.path so 'src' is imported as a package
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import sqlite3
from src.clubos_training_api import ClubOSTrainingPackageAPI
import json
import time

def populate_training_clients():
    """Find and populate the training_clients table with real ClubOS data"""
    
    # Import and set up credentials
    try:
        from src.services.authentication.secure_secrets_manager import SecureSecretsManager
        secrets_manager = SecureSecretsManager()
        username = secrets_manager.get_secret('clubos-username')
        password = secrets_manager.get_secret('clubos-password')
        
        if not username or not password:
            print("❌ ClubOS credentials not found in secrets")
            return
            
        print(f"🔐 Using ClubOS credentials for: {username}")
        
    except Exception as e:
        print(f"❌ Error loading credentials: {e}")
        return
    
    api = ClubOSTrainingPackageAPI()
    api.username = username
    api.password = password
    
    if not api.authenticate():
        print("❌ Failed to authenticate with ClubOS")
        return
    
    print("🔍 Finding training clients from ClubOS...")
    
    # Use the fetch_assignees method to get training clients directly from ClubOS
    print("📋 Fetching training clients from ClubOS assignees...")
    assignees = api.fetch_assignees(force_refresh=True)
    
    if not assignees:
        print("❌ No training clients found from ClubOS assignees")
        return
    
    print(f"✅ Found {len(assignees)} training clients from ClubOS")
    
    # Connect to database
    conn = sqlite3.connect('gym_bot.db')
    cursor = conn.cursor()
    
    training_clients_found = []
    
    for i, assignee in enumerate(assignees):
        member_id = assignee.get('id')
        member_name = assignee.get('name', 'Unknown')
        email = assignee.get('email', 'N/A')
        phone = assignee.get('phone', 'N/A')
        
        print(f"   Processing {i+1}/{len(assignees)}: {member_name} (ID: {member_id})")
        
        # Get payment status for this training client
        try:
            payment_status = api.get_member_payment_status(str(member_id))
            if not payment_status or payment_status == "Unknown":
                payment_status = "Current"  # Default for training clients
            
            print(f"   ✅ {member_name}: {payment_status}")
            
            training_clients_found.append({
                'member_id': member_id,
                'member_name': member_name,
                'clubos_member_id': member_id,
                'payment_status': payment_status,
                'email': email,
                'phone': phone
            })
            
        except Exception as e:
            print(f"   ❌ Error processing {member_name}: {e}")
            # Still add them as training clients even if payment status fails
            training_clients_found.append({
                'member_id': member_id,
                'member_name': member_name,
                'clubos_member_id': member_id,
                'payment_status': 'Error',
                'email': email,
                'phone': phone
            })
    
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
        from src.services.training_package_cache import TrainingPackageCache
        training_package_cache = TrainingPackageCache()
        
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
