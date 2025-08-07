#!/usr/bin/env python3
"""
Test prospect ID + 1 theory for finding delegate user IDs
"""

import sys
sys.path.append('.')

from clubos_training_api import ClubOSTrainingPackageAPI
import sqlite3
import json

def test_prospect_id_theory():
    """Test if adding '1' to the beginning of prospect IDs gives us delegate user IDs"""
    
    # Get all prospect IDs from the database
    db_path = 'gym_bot.db'
    prospect_ids = []
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all prospect IDs
        cursor.execute("SELECT id, full_name FROM members LIMIT 20")  # Test first 20
        members = cursor.fetchall()
        
        print(f"🔍 Testing prospect ID + 1 theory with {len(members)} members...")
        
        for member_id, full_name in members:
            # Try adding '1' to the beginning
            potential_delegate_id = f"1{member_id}"
            prospect_ids.append((member_id, full_name, potential_delegate_id))
            
        conn.close()
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return
    
    # Test each potential delegate ID
    api = ClubOSTrainingPackageAPI()
    if not api.authenticate():
        print("❌ Failed to authenticate")
        return
    
    print(f"\n🧪 Testing {len(prospect_ids)} potential delegate IDs...")
    
    training_clients_found = []
    
    for original_id, member_name, delegate_id in prospect_ids:
        print(f"\n🔄 Testing: {member_name} (ID: {original_id} → Delegate: {delegate_id})")
        
        try:
            # Use exact delegation endpoint
            delegation_response = api.session.get(f"{api.base_url}/action/Delegate/{delegate_id}/url=false")
            print(f"   Delegation status: {delegation_response.status_code}")
            
            if delegation_response.status_code == 200:
                # Get package agreements
                response = api.session.get(f"{api.base_url}/api/agreements/package_agreements/list")
                print(f"   Agreements status: {response.status_code}")
                
                if response.status_code == 200:
                    agreements = response.json()
                    print(f"   Found {len(agreements)} agreements")
                    
                    if agreements:
                        print(f"   🎯 TRAINING CLIENT FOUND: {member_name}")
                        training_clients_found.append({
                            'original_id': original_id,
                            'delegate_id': delegate_id,
                            'member_name': member_name,
                            'agreements_count': len(agreements),
                            'agreements': agreements
                        })
                        
                        # Show basic info about agreements
                        for i, agreement in enumerate(agreements):
                            package_info = agreement.get('packageAgreement', {})
                            package_name = package_info.get('name', 'Unknown Package')
                            agreement_id = package_info.get('id', 'No ID')
                            print(f"     Agreement {i+1}: {package_name} (ID: {agreement_id})")
                    else:
                        print(f"   No agreements for {member_name}")
            else:
                print(f"   Delegation failed: {delegation_response.status_code}")
                
        except Exception as e:
            print(f"   Error testing {member_name}: {e}")
    
    # Summary
    print(f"\n" + "="*60)
    print(f"🏁 RESULTS SUMMARY:")
    print(f"   Total members tested: {len(prospect_ids)}")
    print(f"   Training clients found: {len(training_clients_found)}")
    
    if training_clients_found:
        print(f"\n📋 TRAINING CLIENTS DISCOVERED:")
        for client in training_clients_found:
            print(f"   • {client['member_name']}")
            print(f"     Original ID: {client['original_id']}")
            print(f"     Delegate ID: {client['delegate_id']}")
            print(f"     Agreements: {client['agreements_count']}")
            
        # Test Dennis specifically
        dennis_found = False
        for client in training_clients_found:
            if 'dennis' in client['member_name'].lower() or 'rost' in client['member_name'].lower():
                dennis_found = True
                print(f"\n🎯 DENNIS FOUND!")
                print(f"   Name: {client['member_name']}")
                print(f"   Delegate ID: {client['delegate_id']}")
                break
                
        if not dennis_found:
            print(f"\n❌ Dennis not found in this batch")
            
            # Try Dennis specifically if we know his ID
            print(f"\n🔍 Testing Dennis specifically...")
            
            # Get Dennis's ID from members table
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, full_name FROM members 
                    WHERE LOWER(full_name) LIKE '%dennis%' 
                       OR LOWER(full_name) LIKE '%rost%'
                """)
                dennis_members = cursor.fetchall()
                conn.close()
                
                for dennis_id, dennis_name in dennis_members:
                    dennis_delegate_id = f"1{dennis_id}"
                    print(f"   Testing Dennis: {dennis_name} (ID: {dennis_id} → Delegate: {dennis_delegate_id})")
                    
                    delegation_response = api.session.get(f"{api.base_url}/action/Delegate/{dennis_delegate_id}/url=false")
                    if delegation_response.status_code == 200:
                        response = api.session.get(f"{api.base_url}/api/agreements/package_agreements/list")
                        if response.status_code == 200:
                            agreements = response.json()
                            print(f"   Dennis agreements: {len(agreements)}")
                            if agreements:
                                print(f"   🎯 DENNIS FOUND with delegate ID: {dennis_delegate_id}")
                            
            except Exception as e:
                print(f"   Error testing Dennis: {e}")
    else:
        print(f"   ❌ No training clients found with this method")

if __name__ == "__main__":
    print("🧪 Testing Prospect ID + 1 Theory for Delegate User IDs")
    print("=" * 60)
    
    test_prospect_id_theory()
    
    print("\n" + "=" * 60)
    print("🏁 Test complete!")
