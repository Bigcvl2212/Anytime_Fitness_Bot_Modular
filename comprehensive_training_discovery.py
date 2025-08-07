#!/usr/bin/env python3
"""
Comprehensive Training Client Discovery
Uses multiple approaches to find ClubOS training clients
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'services'))

from api.clubhub_api_client import ClubHubAPIClient
from config.clubhub_credentials import CLUBHUB_EMAIL, CLUBHUB_PASSWORD

# Import ClubOS training API
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from clubos_training_api import ClubOSTrainingPackageAPI

def test_member_training_status(training_api, member_name, clubos_id):
    """Test if a member has training data with given ClubOS ID"""
    try:
        payment_status = training_api.get_member_payment_status(str(clubos_id))
        if payment_status:
            return {
                'clubos_id': str(clubos_id),
                'payment_status': payment_status,
                'status_type': type(payment_status).__name__
            }
    except Exception as e:
        pass  # Ignore errors, just return None
    return None

def main():
    print("=== COMPREHENSIVE TRAINING CLIENT DISCOVERY ===")
    
    # Authenticate ClubHub
    client = ClubHubAPIClient()
    if not client.authenticate(CLUBHUB_EMAIL, CLUBHUB_PASSWORD):
        print("❌ ClubHub authentication failed")
        return
    
    print("✅ ClubHub authenticated")
    
    # Initialize ClubOS training API
    training_api = ClubOSTrainingPackageAPI()
    if not training_api.authenticate():
        print("❌ ClubOS training API authentication failed")
        return
    
    print("✅ ClubOS training API authenticated")
    
    # Get all ClubHub members
    all_members = []
    page = 1
    while page <= 6:
        members = client.get_all_members(page=page, page_size=100)
        if not members:
            break
        all_members.extend(members)
        page += 1
    
    print(f"📋 Retrieved {len(all_members)} ClubHub members")
    
    # Known working mappings from our previous discoveries
    known_mappings = {
        "JORDAN KRUEGER": "160402199",  # From funding_status_cache
        # Add more as we discover them
    }
    
    print(f"\n🔍 Testing multiple ID mapping approaches...")
    
    training_clients_found = []
    checked_count = 0
    
    for member in all_members:
        checked_count += 1
        member_name = f"{member.get('firstName', '')} {member.get('lastName', '')}".strip()
        member_name_upper = member_name.upper()
        clubhub_id = str(member.get('id'))
        
        if checked_count % 50 == 0:
            print(f"   Checked {checked_count}/{len(all_members)} members... Found {len(training_clients_found)} training clients")
        
        # Try multiple approaches to find ClubOS ID
        approaches_to_try = [
            (clubhub_id, "direct_mapping"),  # ClubHub ID = ClubOS ID
        ]
        
        # Add known special mappings
        if member_name_upper in known_mappings:
            approaches_to_try.append((known_mappings[member_name_upper], "known_mapping"))
        
        # Try different ID variations (some systems pad IDs, etc.)
        if len(clubhub_id) >= 6:
            # Try without leading digits
            for i in range(1, min(3, len(clubhub_id))):
                variant_id = clubhub_id[i:]
                if variant_id != clubhub_id:
                    approaches_to_try.append((variant_id, f"variant_trim_{i}"))
        
        # Test each approach
        for clubos_id, method in approaches_to_try:
            result = test_member_training_status(training_api, member_name, clubos_id)
            
            if result:
                training_clients_found.append({
                    'name': member_name,
                    'clubhub_id': clubhub_id,
                    'clubos_id': result['clubos_id'],
                    'payment_status': result['payment_status'],
                    'mapping_method': method,
                    'status_type': result['status_type']
                })
                
                status_emoji = "✅" if 'current' in str(result['payment_status']).lower() else "⚠️"
                print(f"{status_emoji} {member_name} - {result['payment_status']} (ClubOS: {result['clubos_id']}, Method: {method})")
                
                # Found one, don't try other methods for this member
                break
    
    print(f"\n=== FINAL RESULTS ===")
    print(f"📊 Total members checked: {checked_count}")
    print(f"✅ Training clients found: {len(training_clients_found)}")
    
    if training_clients_found:
        print(f"\n🏋️ ALL TRAINING CLIENTS:")
        
        # Group by payment status
        status_groups = {}
        method_counts = {}
        
        for client in training_clients_found:
            status = str(client['payment_status']).lower()
            method = client['mapping_method']
            
            if status not in status_groups:
                status_groups[status] = []
            status_groups[status].append(client)
            
            method_counts[method] = method_counts.get(method, 0) + 1
        
        for status, clients in status_groups.items():
            status_emoji = "✅" if 'current' in status else "⚠️"
            print(f"\n{status_emoji} {status.upper()} ({len(clients)} clients):")
            for client in clients:
                print(f"   {client['name']} (ClubOS: {client['clubos_id']}, Method: {client['mapping_method']})")
        
        print(f"\n📊 MAPPING METHOD BREAKDOWN:")
        for method, count in sorted(method_counts.items()):
            print(f"   {method}: {count} clients")
        
        # Check if Dennis was found
        dennis_found = any('DENNIS' in client['name'].upper() and 'ROST' in client['name'].upper() 
                          for client in training_clients_found)
        if dennis_found:
            print(f"\n🎯 SUCCESS: Dennis Rost found as training client!")
        else:
            print(f"\n❌ Dennis Rost not found - may need additional investigation")
    
    else:
        print(f"\n❌ No training clients found - API may have issues")
    
    print(f"\n✅ Comprehensive discovery complete!")

if __name__ == "__main__":
    main()
