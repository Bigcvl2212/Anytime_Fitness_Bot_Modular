#!/usr/bin/env python3
"""
Direct test of Mark Benzinger's GUID with ClubOS API
Testing: discover_member_agreement_ids(66082049) to see if it returns agreement IDs
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from clubos_training_api_fixed import ClubOSTrainingPackageAPI

def test_mark_api():
    print("=== Testing Mark Benzinger's GUID with ClubOS API ===")
    print(f"Mark's GUID: 66082049")
    print(f"Mark's clubos_member_id: 125814462")
    
    # Initialize API and set credentials manually (like in working code)
    api = ClubOSTrainingPackageAPI()
    api.username = 'j.mayo'
    api.password = 'j@SD4fjhANK5WNA'
    
    try:
        print("\n--- Testing authentication ---")
        auth_success = api.authenticate()
        print(f"Authentication successful: {auth_success}")
        
        if auth_success:
            print("\n--- Testing GUID delegation ---")
            delegation_success = api.delegate_to_member(66082049)  # Mark's GUID
            print(f"Delegation to GUID 66082049 successful: {delegation_success}")
            
            if delegation_success:
                print("\n--- Testing discover_member_agreement_ids with clubos_member_id (125814462) ---")
                agreement_ids_clubos = api.discover_member_agreement_ids(125814462)  # Mark's clubos_member_id
                print(f"Agreement IDs found with clubos_member_id: {agreement_ids_clubos}")
                print(f"Number of agreement IDs with clubos_member_id: {len(agreement_ids_clubos) if agreement_ids_clubos else 0}")
                
                print("\n--- Testing discover_member_agreement_ids with GUID (66082049) ---")
                agreement_ids_guid = api.discover_member_agreement_ids(66082049)  # Mark's GUID
                print(f"Agreement IDs found with GUID: {agreement_ids_guid}")
                print(f"Number of agreement IDs with GUID: {len(agreement_ids_guid) if agreement_ids_guid else 0}")
                
                if agreement_ids_clubos or agreement_ids_guid:
                    print("\n✅ SUCCESS: Found agreement IDs!")
                    return True
                else:
                    print("\n❌ No agreement IDs returned from either ID type - both API calls successful but empty results")
            else:
                print("❌ Delegation failed")
        else:
            print("❌ Authentication failed")
            
    except Exception as e:
        print(f"❌ Error during API test: {str(e)}")
        import traceback
        traceback.print_exc()
    
    return False

if __name__ == "__main__":
    result = test_mark_api()
    print(f"\n=== Final Result: {'SUCCESS' if result else 'FAILED'} ===")
