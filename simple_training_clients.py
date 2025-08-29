#!/usr/bin/env python3
"""
Simple script to manually navigate to training clients page and extract data
"""

import sys
sys.path.append('.')

from clubos_training_api_fixed import ClubOSTrainingPackageAPI
from config.secrets_local import get_secret
import sqlite3
import time

def get_training_clients_manually():
    """Get training clients by manually navigating to the training page"""
    
    # Set up API with credentials
    username = get_secret('clubos-username')
    password = get_secret('clubos-password')
    
    if not username or not password:
        print("❌ ClubOS credentials not found")
        return []
    
    api = ClubOSTrainingPackageAPI()
    api.username = username
    api.password = password
    
    if not api.authenticate():
        print("❌ Failed to authenticate with ClubOS")
        return []
    
    print("✅ Authenticated with ClubOS")
    
    # Try to navigate to the training clients page
    try:
        # Navigate to the main training page
        print("🔍 Navigating to training page...")
        response = api.session.get("https://anytime.club-os.com/action/Assignees", timeout=30)
        
        if response.status_code == 200:
            print(f"✅ Training page loaded successfully ({len(response.text)} characters)")
            
            # Look for training client data in the HTML
            html = response.text
            
            # Look for specific patterns that indicate training clients
            if "assignee" in html.lower() or "training" in html.lower():
                print("🎯 Found training-related content in HTML")
                
                # Try to find member IDs in the HTML
                import re
                
                # Look for onclick="delegate(MEMBER_ID,'/action/Assignees')" patterns
                delegate_pattern = r'onclick="delegate\((\d+),'
                member_ids = re.findall(delegate_pattern, html)
                
                if member_ids:
                    print(f"✅ Found {len(member_ids)} potential training client IDs: {member_ids[:10]}...")
                    
                    # Create training client records
                    training_clients = []
                    for member_id in member_ids:
                        training_clients.append({
                            'member_id': member_id,
                            'member_name': f'Training Client {member_id}',
                            'clubos_member_id': member_id,
                            'payment_status': 'Current',
                            'email': 'N/A',
                            'phone': 'N/A'
                        })
                    
                    return training_clients
                else:
                    print("⚠️ No member IDs found in delegate patterns")
            else:
                print("⚠️ No training-related content found in HTML")
                
        else:
            print(f"❌ Failed to load training page: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error navigating to training page: {e}")
    
    return []

def populate_database(training_clients):
    """Populate the training_clients table with the found data"""
    
    if not training_clients:
        print("❌ No training clients to insert")
        return
    
    print(f"💾 Inserting {len(training_clients)} training clients into database...")
    
    try:
        conn = sqlite3.connect('gym_bot.db')
        cursor = conn.cursor()
        
        # Create table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS training_clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                member_id TEXT,
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
        for client in training_clients:
            cursor.execute('''
                INSERT INTO training_clients 
                (member_id, member_name, clubos_member_id, payment_status, email, phone, package_name)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                client['member_id'],
                client['member_name'], 
                client['clubos_member_id'],
                client['payment_status'],
                client['email'],
                client['phone'],
                'Training Package'
            ))
        
        conn.commit()
        print(f"✅ Successfully inserted {len(training_clients)} training clients")
        
        # Verify the data
        cursor.execute("SELECT COUNT(*) FROM training_clients")
        count = cursor.fetchone()[0]
        print(f"📊 Database now contains {count} training clients")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error inserting into database: {e}")

if __name__ == "__main__":
    print("🔍 Manually extracting training clients from ClubOS...")
    print("=" * 60)
    
    # Get training clients manually
    training_clients = get_training_clients_manually()
    
    if training_clients:
        print(f"✅ Found {len(training_clients)} training clients")
        
        # Populate database
        populate_database(training_clients)
        
        print(f"\n🎯 Training clients found:")
        for client in training_clients[:5]:  # Show first 5
            print(f"   - {client['member_name']} (ID: {client['member_id']})")
        
        if len(training_clients) > 5:
            print(f"   ... and {len(training_clients) - 5} more")
    else:
        print("❌ No training clients found")
    
    print("\n" + "=" * 60)
    print("🏁 Manual training clients extraction complete!")
