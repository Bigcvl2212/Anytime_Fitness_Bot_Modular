#!/usr/bin/env python3
"""
Test specific clients that user mentioned should be past due:
Dale Roen, Javae Dixon, Ziann Crump, Mindy Feilbach, Miguel Belmontes, Joe Benson, Diego Pascal
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.services.api.clubos_training_api import ClubOSTrainingPackageAPI
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_specific_past_due_clients():
    """Test the specific clients user mentioned should be past due"""
    api = ClubOSTrainingPackageAPI()
    
    if not api.authenticate():
        print("❌ Authentication failed")
        return
    
    # Test clients by searching for their names
    past_due_names = [
        "Dale Roen", 
        "Javae Dixon", 
        "Ziann Crump", 
        "Mindy Feilbach", 
        "Miguel Belmontes", 
        "Joe Benson", 
        "Diego Pascal"
    ]
    
    found_clients = []
    
    print("🔍 STEP 1: Finding member IDs for the specific past due clients...")
    
    for name in past_due_names:
        try:
            print(f"\n--- Searching for {name} ---")
            member_id = api.search_member_id(name)
            
            if member_id:
                print(f"✅ Found {name} with ID: {member_id}")
                found_clients.append({'name': name, 'id': member_id})
            else:
                print(f"❌ Could not find member ID for {name}")
                
        except Exception as e:
            print(f"❌ Error searching for {name}: {e}")
    
    print(f"\n🔍 STEP 2: Testing breakthrough method on {len(found_clients)} found clients...")
    
    total_past_due_found = 0
    clients_with_past_due = 0
    
    for client in found_clients:
        try:
            print(f"\n=== Testing {client['name']} (ID: {client['id']}) ===")
            
            result = api.get_member_training_packages_breakthrough(client['id'])
            
            if result.get('success') and result.get('packages'):
                packages = result['packages']
                print(f"📋 Found {len(packages)} packages:")
                
                client_total_past_due = 0
                for pkg in packages:
                    package_name = pkg.get('package_name', 'Unknown Package')
                    payment_status = pkg.get('payment_status', 'Unknown')
                    amount_owed = pkg.get('amount_owed', 0)
                    biweekly_amount = pkg.get('biweekly_amount', 0)
                    billing_state = pkg.get('billing_state', 1)
                    
                    print(f"  📦 {package_name}")
                    print(f"     Status: {payment_status} | Amount Owed: ${amount_owed:.2f} | Biweekly: ${biweekly_amount:.2f} | Billing State: {billing_state}")
                    
                    client_total_past_due += float(amount_owed or 0)
                
                if client_total_past_due > 0:
                    print(f"💰 {client['name']} TOTAL PAST DUE: ${client_total_past_due:.2f}")
                    total_past_due_found += client_total_past_due
                    clients_with_past_due += 1
                else:
                    print(f"✅ {client['name']} shows as CURRENT (no past due amounts)")
                    
            else:
                error = result.get('error', 'No packages found')
                print(f"❌ {client['name']}: {error}")
                
        except Exception as e:
            print(f"❌ Error testing {client['name']}: {e}")
    
    print(f"\n=== SUMMARY ===")
    print(f"👥 Clients searched: {len(past_due_names)}")
    print(f"🔍 Clients found: {len(found_clients)}")
    print(f"💰 Clients with past due amounts: {clients_with_past_due}")
    print(f"💵 Total past due found: ${total_past_due_found:.2f}")
    
    if clients_with_past_due == 0:
        print("\n⚠️  ISSUE: None of the specified clients show past due amounts!")
        print("   This suggests either:")
        print("   1. The billing status extraction logic is incorrect")
        print("   2. The clients have actually paid since yesterday")
        print("   3. The past due calculation method is wrong")
        print("   4. The data source doesn't contain the expected billing information")
    else:
        print(f"\n✅ Found {clients_with_past_due} clients with past due amounts - this matches user's expectation!")

if __name__ == "__main__":
    test_specific_past_due_clients()