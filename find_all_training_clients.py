#!/usr/bin/env python3
"""
Find all training client delegate user IDs by systematically searching
"""

import sys
sys.path.append('.')

from clubos_training_api import ClubOSTrainingPackageAPI
import sqlite3
import json
import time

def get_all_member_ids_from_database():
    """Get all member IDs from local database to test as potential delegate IDs"""
    try:
        conn = sqlite3.connect('gym_bot.db')
        cursor = conn.cursor()
        
        # First check if members table exists and has data
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='members'")
        if cursor.fetchone():
            cursor.execute("SELECT COUNT(*) FROM members")
            count = cursor.fetchone()[0]
            print(f"   Members table has {count} rows")
            
            if count > 0:
                # Get all member IDs from members table
                cursor.execute("SELECT id, full_name FROM members ORDER BY id")
                members = cursor.fetchall()
                conn.close()
                return members
        
        # If no members table or empty, try to get from ClubHub fresh data
        print(f"   No members in local database, trying ClubHub...")
        
        # Try to import and use ClubHub API
        try:
            from clubos_fresh_data_api import ClubOSFreshDataAPI
            
            fresh_api = ClubOSFreshDataAPI()
            members_data = fresh_api.get_fresh_member_data()
            
            if members_data and 'members' in members_data:
                members = []
                for member in members_data['members']:
                    member_id = member.get('id')
                    full_name = member.get('full_name', 'Unknown')
                    if member_id:
                        members.append((member_id, full_name))
                
                print(f"   Got {len(members)} members from ClubHub")
                conn.close()
                return members
                
        except Exception as e:
            print(f"   Error getting ClubHub data: {e}")
        
        conn.close()
        return []
    except Exception as e:
        print(f"❌ Database error: {e}")
        return []

def test_delegate_id_range():
    """Test different ranges of delegate IDs to find other training clients"""
    
    # Dennis's delegate ID is 189425730
    dennis_id = 189425730
    
    test_ranges = []
    
    # Range 1: Around Dennis's ID (we know this works)
    test_ranges.extend(range(dennis_id - 50, dennis_id + 50, 5))
    
    # Range 2: Try IDs around your user ID (187032782)
    your_id = 187032782
    test_ranges.extend(range(your_id - 50, your_id + 50, 5))
    
    # Range 3: Try some random high ID ranges that might be training clients
    test_ranges.extend(range(160000000, 160000100, 10))  # Lower range
    test_ranges.extend(range(180000000, 180000100, 10))  # Middle range
    test_ranges.extend(range(190000000, 190000100, 10))  # Higher range
    
    # Range 4: Try the delegate ID from HAR files (184027841)
    har_delegate_id = 184027841
    test_ranges.extend(range(har_delegate_id - 50, har_delegate_id + 50, 5))
    
    # Remove duplicates and sort
    test_ranges = sorted(list(set(test_ranges)))
    
    return test_ranges

def find_all_training_clients():
    """Find all training clients by testing different delegate IDs"""
    
    api = ClubOSTrainingPackageAPI()
    if not api.authenticate():
        print("❌ Failed to authenticate")
        return
    
    print("🔍 Finding all training clients...")
    
    # Strategy 1: Test member IDs from database
    print("\n📋 Strategy 1: Testing member IDs from database as delegate IDs...")
    
    members = get_all_member_ids_from_database()
    print(f"Found {len(members)} members in database to test")
    
    training_clients_found = {}
    
    # Test first 50 members as delegate IDs (to get more comprehensive results)
    test_count = min(50, len(members))
    for i, (member_id, member_name) in enumerate(members[:test_count]):
        print(f"   Testing member {i+1}/{test_count}: {member_name} (ID: {member_id})")
        
        try:
            # Use the delegation endpoint
            delegation_response = api.session.get(f"{api.base_url}/action/Delegate/{member_id}/url=false")
            
            if delegation_response.status_code == 200:
                # Get package agreements
                response = api.session.get(f"{api.base_url}/api/agreements/package_agreements/list")
                
                if response.status_code == 200:
                    agreements = response.json()
                    if agreements:
                        print(f"   ✅ Found {len(agreements)} agreements for delegate ID {member_id}")
                        training_clients_found[member_id] = {
                            'name': member_name,
                            'agreements': agreements
                        }
                        
                        # Show details of first agreement
                        if agreements:
                            first_agreement = agreements[0]
                            package_info = first_agreement.get('packageAgreement', {})
                            print(f"      Sample package: {package_info.get('name', 'No name')}")
                            print(f"      Member ID: {package_info.get('memberId', 'No member ID')}")
            
        except Exception as e:
            print(f"   Error testing ID {member_id}: {e}")
        
        time.sleep(0.5)  # Rate limiting
    
    # Strategy 2: Test broader ID ranges
    print(f"\n🎯 Strategy 2: Testing broader delegate ID ranges...")
    
    test_ids = test_delegate_id_range()
    print(f"Testing {len(test_ids)} strategic IDs across multiple ranges...")
    
    tested_count = 0
    for delegate_id in test_ids:
        tested_count += 1
        print(f"   Testing delegate ID {tested_count}/{len(test_ids)}: {delegate_id}")
        
        try:
            # Use the delegation endpoint
            delegation_response = api.session.get(f"{api.base_url}/action/Delegate/{delegate_id}/url=false")
            
            if delegation_response.status_code == 200:
                # Get package agreements
                response = api.session.get(f"{api.base_url}/api/agreements/package_agreements/list")
                
                if response.status_code == 200:
                    agreements = response.json()
                    if agreements:
                        print(f"   ✅ Found {len(agreements)} agreements for delegate ID {delegate_id}")
                        
                        # Get member info from agreement
                        first_agreement = agreements[0]
                        package_info = first_agreement.get('packageAgreement', {})
                        member_id = package_info.get('memberId', 'Unknown')
                        package_name = package_info.get('name', 'No name')
                        
                        # Only add if it's a new member (not Dennis again)
                        if member_id != 189425730:
                            training_clients_found[delegate_id] = {
                                'name': f"Member_{member_id}",
                                'member_id': member_id,
                                'agreements': agreements
                            }
                            
                            print(f"      🆕 NEW TRAINING CLIENT!")
                            print(f"      Package: {package_name}")
                            print(f"      Member ID: {member_id}")
                        else:
                            print(f"      (Same as Dennis - skipping)")
            
        except Exception as e:
            print(f"   Error testing ID {delegate_id}: {e}")
        
        time.sleep(0.2)  # Faster rate limiting since we're testing more IDs
    
    # Strategy 3: Try to find a members/list endpoint
    print(f"\n📊 Strategy 3: Looking for member list endpoints...")
    
    member_list_endpoints = [
        "/api/members/list",
        "/api/users/list", 
        "/api/clubservices/members",
        "/api/training/members",
        "/api/delegation/members"
    ]
    
    for endpoint in member_list_endpoints:
        try:
            response = api.session.get(f"{api.base_url}{endpoint}")
            print(f"   {endpoint}: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ {endpoint} returned data: {type(data)}")
                
                if isinstance(data, list) and data:
                    print(f"   Found {len(data)} items")
                    
                    # Show sample of first few items
                    for i, item in enumerate(data[:3]):
                        print(f"      Item {i+1}: {json.dumps(item, indent=2)[:200]}...")
                        
        except Exception as e:
            print(f"   Error with {endpoint}: {e}")
    
    # Summary
    print(f"\n🏁 SUMMARY:")
    print(f"Found {len(training_clients_found)} training clients:")
    
    for delegate_id, client_info in training_clients_found.items():
        name = client_info['name']
        agreement_count = len(client_info['agreements'])
        print(f"   Delegate ID {delegate_id}: {name} ({agreement_count} agreements)")
        
        # Show package names
        for agreement in client_info['agreements']:
            package_info = agreement.get('packageAgreement', {})
            package_name = package_info.get('name', 'No name')
            print(f"      - {package_name}")
    
    return training_clients_found

if __name__ == "__main__":
    print("🔍 Finding all training client delegate IDs...")
    print("=" * 60)
    
    training_clients = find_all_training_clients()
    
    print("\n" + "=" * 60)
    print("🏁 Search complete!")
