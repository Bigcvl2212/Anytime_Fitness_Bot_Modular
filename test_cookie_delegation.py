#!/usr/bin/env python3
"""
Find Dennis using cookie-based delegation approach
"""

import sys
sys.path.append('.')

from clubos_training_api import ClubOSTrainingPackageAPI
import re
import json
import time

def test_cookie_delegation():
    """Test delegation using cookies instead of POST endpoints"""
    
    api = ClubOSTrainingPackageAPI()
    if not api.authenticate():
        print("❌ Failed to authenticate")
        return
    
    # From the HAR files, we see these delegated user IDs work:
    known_working_delegate_ids = [
        184027841,  # Most common in HAR files
        185777276,  # Alternative ID seen in HAR files
    ]
    
    # Our known Dennis IDs to try
    dennis_candidate_ids = [
        65828815,    # ClubHub ID
        96530079,    # CSV agreement_agreementID  
        31489560,    # CSV userId
        1840278041,  # JWT delegateUserId from HAR (might be Dennis?)
        1857772761,  # Modified version of the other working ID
    ]
    
    all_ids_to_test = known_working_delegate_ids + dennis_candidate_ids
    
    print("🍪 Testing cookie-based delegation...")
    print(f"Current cookies: {dict(api.session.cookies)}")
    
    for delegate_id in all_ids_to_test:
        print(f"\n🔄 Testing delegatedUserId={delegate_id}")
        
        # Set the delegation cookie
        api.session.cookies.set('delegatedUserId', str(delegate_id))
        
        try:
            # Try to get package agreements with this delegation
            response = api.session.get(f"{api.base_url}/api/agreements/package_agreements/list")
            print(f"   Package agreements status: {response.status_code}")
            
            if response.status_code == 200:
                agreements = response.json()
                print(f"   ✅ Found {len(agreements)} agreements for delegate ID {delegate_id}")
                
                if agreements:
                    print(f"   Sample agreement keys: {list(agreements[0].keys())}")
                    
                    # Look for Dennis in the agreements
                    dennis_found = False
                    for i, agreement in enumerate(agreements):
                        agreement_text = str(agreement).lower()
                        if 'dennis' in agreement_text or 'rost' in agreement_text:
                            print(f"   🎯 FOUND DENNIS in agreement {i}: {json.dumps(agreement, indent=2)}")
                            dennis_found = True
                        
                        # Show a few sample member names to see the pattern
                        if i < 3:
                            member_info = agreement.get('member', {})
                            member_name = member_info.get('name', 'No name')
                            member_id = member_info.get('id', 'No ID')
                            print(f"   Sample member {i}: {member_name} (ID: {member_id})")
                    
                    if not dennis_found and len(agreements) > 0:
                        print(f"   Dennis not found in {len(agreements)} agreements for delegate ID {delegate_id}")
                        
                        # If this is a known working ID, let's see all the member names
                        if delegate_id in known_working_delegate_ids:
                            print(f"   📋 All member names for delegate ID {delegate_id}:")
                            for i, agreement in enumerate(agreements):
                                member_info = agreement.get('member', {})
                                member_name = member_info.get('name', 'No name')
                                print(f"      {i+1}: {member_name}")
                
                else:
                    print(f"   No agreements found for delegate ID {delegate_id}")
                    
            else:
                print(f"   ❌ Request failed: {response.status_code} - {response.text[:200]}")
                
        except Exception as e:
            print(f"   Error testing delegate ID {delegate_id}: {e}")
            
        time.sleep(0.5)
    
    # Reset to original delegation
    api.session.cookies.set('delegatedUserId', str(187032782))  # Your original user ID
    print(f"\n🔄 Reset delegation to your user ID: 187032782")

def search_member_names_in_agreements():
    """Search for Dennis by looking at all member names across all working delegate IDs"""
    
    api = ClubOSTrainingPackageAPI()
    if not api.authenticate():
        return
    
    # Test the known working delegate IDs
    working_delegate_ids = [184027841, 185777276]
    
    all_members = {}
    
    for delegate_id in working_delegate_ids:
        print(f"\n📋 Getting all members for delegate ID {delegate_id}...")
        
        api.session.cookies.set('delegatedUserId', str(delegate_id))
        
        try:
            response = api.session.get(f"{api.base_url}/api/agreements/package_agreements/list")
            if response.status_code == 200:
                agreements = response.json()
                print(f"   Found {len(agreements)} agreements")
                
                for agreement in agreements:
                    member_info = agreement.get('member', {})
                    member_name = member_info.get('name', '').strip()
                    member_id = member_info.get('id', '')
                    
                    if member_name:
                        all_members[member_name.lower()] = {
                            'name': member_name,
                            'id': member_id,
                            'delegate_id': delegate_id,
                            'agreement': agreement
                        }
                        
        except Exception as e:
            print(f"   Error: {e}")
    
    print(f"\n🔍 Searching through {len(all_members)} unique members...")
    
    # Search for Dennis variations
    dennis_variations = ['dennis', 'rost', 'dennis rost', 'den ', 'ros']
    
    found_matches = []
    for name_lower, member_data in all_members.items():
        for variation in dennis_variations:
            if variation in name_lower:
                found_matches.append(member_data)
                break
    
    if found_matches:
        print(f"\n🎯 Found {len(found_matches)} potential Dennis matches:")
        for match in found_matches:
            print(f"   Name: {match['name']}")
            print(f"   ID: {match['id']}")
            print(f"   Delegate ID: {match['delegate_id']}")
            print(f"   Agreement: {json.dumps(match['agreement'], indent=2)[:300]}...")
            print()
    else:
        print("   ❌ No Dennis matches found")
        
        # Show some sample names to see what we're working with
        print(f"\n📋 Sample member names:")
        for i, (name_lower, member_data) in enumerate(list(all_members.items())[:10]):
            print(f"   {i+1}: {member_data['name']} (ID: {member_data['id']})")

if __name__ == "__main__":
    print("🍪 Testing cookie-based delegation to find Dennis...")
    print("=" * 60)
    
    # First test cookie delegation with known IDs
    test_cookie_delegation()
    
    # Then search through all member names
    search_member_names_in_agreements()
    
    print("\n" + "=" * 60)
    print("🏁 Cookie delegation test complete!")
