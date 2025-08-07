#!/usr/bin/env python3
"""
Test Dennis Rost's payment token for training API access
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.clubos_training_package_api import ClubOSTrainingPackageAPI
import requests

def test_dennis_payment_token():
    """Test Dennis's payment token from CSV for API access"""
    
    api = ClubOSTrainingPackageAPI()
    
    # Dennis's data from CSV
    dennis_payment_token = "8d4b4880-39dd-4a6a-b3d4-0b3a7c9fc02f"
    dennis_csv_member_id = 65828815
    dennis_delegate_id = 189425730  # We found this works for training packages
    
    print("=== TESTING DENNIS PAYMENT TOKEN ===")
    print(f"Payment Token: {dennis_payment_token}")
    print(f"CSV Member ID: {dennis_csv_member_id}")
    print(f"Delegate ID: {dennis_delegate_id}")
    
    # Test 1: Use payment token as query parameter
    print("\n1. Testing payment token as query parameter...")
    test_urls = [
        f"/api/agreements/package_agreements/list?paymentToken={dennis_payment_token}",
        f"/api/members/training?paymentToken={dennis_payment_token}",
        f"/api/training/clients?paymentToken={dennis_payment_token}",
        f"/action/Dashboard?paymentToken={dennis_payment_token}",
        f"/action/Training?paymentToken={dennis_payment_token}",
    ]
    
    for url in test_urls:
        try:
            response = api.session.get(f"{api.base_url}{url}")
            print(f"  {url}")
            print(f"    Status: {response.status_code}")
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                if 'application/json' in content_type:
                    print(f"    JSON Response: {len(response.text)} chars")
                    if response.text.strip():
                        print(f"    Data: {response.text[:200]}...")
                elif 'text/html' in content_type:
                    print(f"    HTML Response: {len(response.text)} chars")
                    if "training" in response.text.lower():
                        print("    ✓ Contains training-related content")
            else:
                print(f"    Error: {response.text[:200]}")
        except Exception as e:
            print(f"    Exception: {e}")
    
    # Test 2: Set delegation first, then use payment token
    print("\n2. Testing delegation + payment token...")
    try:
        # Set delegation to Dennis
        delegation_url = f"/action/Delegate/{dennis_delegate_id}/url=false"
        delegation_response = api.session.get(f"{api.base_url}{delegation_url}")
        print(f"Delegation Status: {delegation_response.status_code}")
        
        if delegation_response.status_code == 200:
            # Now try with payment token
            test_url = f"/api/agreements/package_agreements/list?paymentToken={dennis_payment_token}"
            response = api.session.get(f"{api.base_url}{test_url}")
            print(f"With delegation + token: {response.status_code}")
            if response.status_code == 200:
                print(f"Success! Response: {response.text[:500]}...")
    except Exception as e:
        print(f"Delegation test error: {e}")
    
    # Test 3: Use payment token in headers
    print("\n3. Testing payment token in headers...")
    headers = {
        'Authorization': f'Bearer {dennis_payment_token}',
        'X-Payment-Token': dennis_payment_token,
        'X-Agreement-Token': dennis_payment_token
    }
    
    try:
        response = api.session.get(
            f"{api.base_url}/api/agreements/package_agreements/list",
            headers=headers
        )
        print(f"Header token test: {response.status_code}")
        if response.status_code == 200:
            print(f"Success! Response: {response.text[:200]}...")
    except Exception as e:
        print(f"Header test error: {e}")

if __name__ == "__main__":
    test_dennis_payment_token()
