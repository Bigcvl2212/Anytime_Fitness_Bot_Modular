#!/usr/bin/env python3
"""
Systematic Training Client Discovery
Based on HAR analysis patterns - scan for all training delegate IDs
"""

import time
import sqlite3
from datetime import datetime
import json

def create_training_clients_table():
    """Create or update the training_clients table with proper structure"""
    conn = sqlite3.connect('gym_bot.db')
    cursor = conn.cursor()
    
    # Drop and recreate table to ensure proper structure
    cursor.execute('DROP TABLE IF EXISTS training_clients')
    
    cursor.execute('''
    CREATE TABLE training_clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        delegate_id TEXT NOT NULL UNIQUE,
        member_name TEXT,
        package_name TEXT,
        agreement_id INTEGER,
        start_date TEXT,
        end_date TEXT,
        unit_price REAL,
        units_per_billing REAL,
        billing_duration INTEGER,
        agreement_status INTEGER,
        discovered_date TEXT,
        last_updated TEXT,
        raw_data TEXT
    )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Training clients table created/updated")

def systematic_training_client_scan():
    """Systematically scan for training clients using delegate ID ranges"""
    
    try:
        import sys
        sys.path.append('.')
        from clubos_training_api import ClubOSTrainingPackageAPI
        
        api = ClubOSTrainingPackageAPI()
        if not api.authenticate():
            print("❌ Authentication failed")
            return
        
        print("🔍 Starting systematic training client discovery...")
        
        # Known working delegate IDs from HAR analysis
        known_working_ids = [189425730, 185777276]  # Dennis and the other working ID
        
        # Scan ranges around known working IDs
        scan_ranges = []
        for base_id in known_working_ids:
            # Scan ±2000 around each known working ID
            start_id = base_id - 2000
            end_id = base_id + 2000
            scan_ranges.append((start_id, end_id))
        
        # Also scan common ID ranges found in HAR files
        scan_ranges.extend([
            (180000000, 180010000),  # Common range start
            (184000000, 184010000),  # Around Jeremy's ID
            (185000000, 185010000),  # Extended range
            (188000000, 192000000),  # Dennis's range extended
        ])
        
        training_clients = []
        total_checked = 0
        
        for start_id, end_id in scan_ranges:
            print(f"\n📊 Scanning delegate ID range: {start_id} to {end_id}")
            
            for delegate_id in range(start_id, end_id):
                total_checked += 1
                
                if total_checked % 100 == 0:
                    print(f"   Checked {total_checked} IDs, found {len(training_clients)} training clients...")
                
                try:
                    # Set delegation
                    delegation_response = api.session.get(f"{api.base_url}/action/Delegate/{delegate_id}/url=false")
                    
                    if delegation_response.status_code == 200:
                        # Get training packages
                        packages_response = api.session.get(f"{api.base_url}/api/agreements/package_agreements/list")
                        
                        if packages_response.status_code == 200:
                            packages = packages_response.json()
                            
                            if packages and len(packages) > 0:
                                print(f"\n🎯 FOUND TRAINING CLIENT - Delegate ID: {delegate_id}")
                                
                                for package in packages:
                                    package_info = package.get('packageAgreement', {})
                                    services = package.get('packageAgreementMemberServices', [])
                                    
                                    # Extract key information
                                    client_data = {
                                        'delegate_id': str(delegate_id),
                                        'package_name': package_info.get('name', 'Unknown'),
                                        'agreement_id': package_info.get('id'),
                                        'member_id': package_info.get('memberId'),
                                        'start_date': package_info.get('startDate'),
                                        'end_date': package_info.get('endDate'),
                                        'agreement_status': package_info.get('agreementStatus'),
                                        'services': services,
                                        'raw_data': json.dumps(package)
                                    }
                                    
                                    # Try to get member name from member lookup
                                    member_name = get_member_name_from_csv(delegate_id)
                                    if not member_name:
                                        member_name = f"Unknown Member {delegate_id}"
                                    
                                    client_data['member_name'] = member_name
                                    
                                    # Extract pricing info
                                    if services:
                                        service = services[0]  # Use first service
                                        client_data['unit_price'] = service.get('unitPrice')
                                        client_data['units_per_billing'] = service.get('unitsPerBillingDuration')
                                        client_data['billing_duration'] = service.get('billingDuration')
                                    
                                    training_clients.append(client_data)
                                    
                                    print(f"   📋 Package: {client_data['package_name']}")
                                    print(f"   👤 Member: {client_data['member_name']}")
                                    print(f"   💰 Price: ${client_data.get('unit_price', 'N/A')}")
                                    print(f"   📅 Period: {client_data['start_date']} to {client_data['end_date']}")
                
                except Exception as e:
                    # Skip errors and continue scanning
                    pass
                
                # Rate limiting - don't overwhelm the server
                time.sleep(0.1)
        
        print(f"\n🏁 Scan Complete!")
        print(f"   Total IDs checked: {total_checked}")
        print(f"   Training clients found: {len(training_clients)}")
        
        # Save to database
        if training_clients:
            save_training_clients_to_db(training_clients)
        
        return training_clients
        
    except Exception as e:
        print(f"❌ Error during systematic scan: {e}")
        return []

def get_member_name_from_csv(delegate_id):
    """Try to find member name from CSV data by delegate ID"""
    try:
        conn = sqlite3.connect('gym_bot.db')
        cursor = conn.cursor()
        
        # Try to find member by delegate ID
        # Note: This might not work due to the dual ID system
        cursor.execute('SELECT first_name, last_name FROM members WHERE id = ?', (delegate_id,))
        result = cursor.fetchone()
        
        if result:
            return f"{result[0]} {result[1]}"
        
        # Also try userID field
        cursor.execute('SELECT first_name, last_name FROM members WHERE userID = ?', (delegate_id,))
        result = cursor.fetchone()
        
        if result:
            return f"{result[0]} {result[1]}"
        
        conn.close()
        return None
        
    except Exception as e:
        return None

def save_training_clients_to_db(training_clients):
    """Save discovered training clients to database"""
    conn = sqlite3.connect('gym_bot.db')
    cursor = conn.cursor()
    
    current_time = datetime.now().isoformat()
    
    for client in training_clients:
        try:
            cursor.execute('''
            INSERT OR REPLACE INTO training_clients 
            (delegate_id, member_name, package_name, agreement_id, start_date, end_date,
             unit_price, units_per_billing, billing_duration, agreement_status,
             discovered_date, last_updated, raw_data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                client['delegate_id'],
                client['member_name'],
                client['package_name'],
                client['agreement_id'],
                client['start_date'],
                client['end_date'],
                client.get('unit_price'),
                client.get('units_per_billing'),
                client.get('billing_duration'),
                client['agreement_status'],
                current_time,
                current_time,
                client['raw_data']
            ))
        except Exception as e:
            print(f"   ⚠️ Error saving client {client['delegate_id']}: {e}")
    
    conn.commit()
    conn.close()
    print(f"✅ Saved {len(training_clients)} training clients to database")

def show_discovered_training_clients():
    """Display all discovered training clients"""
    conn = sqlite3.connect('gym_bot.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT delegate_id, member_name, package_name, unit_price, 
           units_per_billing, billing_duration, start_date, end_date
    FROM training_clients 
    ORDER BY member_name
    ''')
    
    results = cursor.fetchall()
    conn.close()
    
    if not results:
        print("❌ No training clients found in database")
        return
    
    print(f"\n📋 Discovered Training Clients ({len(results)} total):")
    print("=" * 80)
    
    for row in results:
        delegate_id, name, package, price, units, duration, start, end = row
        print(f"👤 {name} (ID: {delegate_id})")
        print(f"   📦 Package: {package}")
        print(f"   💰 ${price}/session, {units} sessions every {duration} weeks")
        print(f"   📅 Active: {start} to {end}")
        print()

if __name__ == "__main__":
    print("🚀 Training Client Discovery System")
    print("=" * 60)
    
    # Setup database
    create_training_clients_table()
    
    # Run systematic scan
    print("\n⚠️  This will scan thousands of delegate IDs - may take 10-20 minutes")
    response = input("Continue with systematic scan? (y/n): ")
    
    if response.lower() == 'y':
        discovered_clients = systematic_training_client_scan()
        
        # Show results
        print("\n" + "=" * 60)
        show_discovered_training_clients()
    else:
        print("Scan cancelled. Showing existing training clients...")
        show_discovered_training_clients()
