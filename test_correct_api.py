#!/usr/bin/env python3
"""
Test CORRECT API approach based on discovery files:
1. Use ClubHub API to get member agreement IDs
2. Use ClubOS API to get detailed package data
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from clubos_training_api_fixed import ClubOSTrainingPackageAPI
import requests

def test_correct_api_approach():
    print("=== Testing CORRECT API Approach from Discovery Files ===")
    
    # Test member from your working example
    member_id = '191215290'  # Alexander
    clubos_member_id = 125814462  # Mark's clubos_member_id
    
    print(f"Testing with member_id: {member_id}")
    print(f"Testing with clubos_member_id: {clubos_member_id}")
    
    # Initialize API
    api = ClubOSTrainingPackageAPI()
    api.username = 'j.mayo'
    api.password = 'j@SD4fjhANK5WNA'
    
    # Step 1: Authenticate
    if not api.authenticate():
        print("❌ Authentication failed")
        return False
    
    print("✅ Authentication successful")
    
    # Step 2: Test different approaches to get agreement IDs
    print("\n--- Testing ClubHub API approach (from discovery files) ---")
    
    # The discovery files show ClubHub API endpoints work differently
    # Let's try the ClubOS delegation approach that worked yesterday
    
    if api.delegate_to_member(clubos_member_id):
        print(f"✅ Delegated to member {clubos_member_id}")
        
        # Test the broken endpoint (should fail)
        print("\n--- Testing BROKEN endpoint (should fail) ---")
        try:
            url = f"{api.base_url}/api/agreements/package_agreements/list"
            params = {'memberId': clubos_member_id}
            response = api.session.get(url, params=params, timeout=10)
            print(f"Broken endpoint status: {response.status_code}")
            if response.status_code != 200:
                print(f"Broken endpoint response: {response.text[:200]}")
        except Exception as e:
            print(f"Broken endpoint error: {e}")
            
        # Now test using the approach that actually worked
        print("\n--- Testing what SHOULD work based on yesterday's data ---")
        
        # From your yesterday message, you got: Found agreement IDs: ['1672118']
        # This suggests there IS a way to get agreement IDs
        # Let me try the payment details approach that returned agreement_ids
        
        try:
            payment_details = api.get_member_training_payment_details(clubos_member_id)
            print(f"Payment details result: {payment_details}")
            
            if payment_details and payment_details.get('agreement_ids'):
                agreement_ids = payment_details['agreement_ids']
                print(f"✅ Found agreement IDs: {agreement_ids}")
                
                # Now test the V2 endpoint that should work
                for agreement_id in agreement_ids:
                    print(f"\n--- Testing V2 endpoint with agreement {agreement_id} ---")
                    try:
                        url = f"{api.base_url}/api/agreements/package_agreements/V2/{agreement_id}"
                        params = {
                            'include': 'invoices',
                            '_': '1756322485002'  # timestamp like in your working example
                        }
                        response = api.session.get(url, params=params, timeout=10)
                        print(f"V2 endpoint status: {response.status_code}")
                        
                        if response.status_code == 200:
                            data = response.json()
                            print(f"✅ SUCCESS! V2 endpoint returned data")
                            print(f"Agreement name: {data.get('name', 'Unknown')}")
                            print(f"Member ID in agreement: {data.get('memberId', 'Unknown')}")
                            
                            # Check for invoices
                            include_data = data.get('include', {})
                            invoices = include_data.get('invoices', [])
                            print(f"Number of invoices: {len(invoices)}")
                            
                            if invoices:
                                print(f"First invoice amount: ${invoices[0].get('total', 0)}")
                                return True
                        else:
                            print(f"❌ V2 endpoint failed: {response.text[:200]}")
                            
                    except Exception as e:
                        print(f"❌ V2 endpoint error: {e}")
                        
            else:
                print("❌ No agreement IDs found in payment details")
                
        except Exception as e:
            print(f"❌ Payment details error: {e}")
    else:
        print("❌ Delegation failed")
    
    return False

if __name__ == "__main__":
    success = test_correct_api_approach()
    print(f"\n=== Final Result: {'SUCCESS' if success else 'FAILED'} ===")
