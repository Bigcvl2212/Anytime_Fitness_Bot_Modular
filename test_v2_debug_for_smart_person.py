#!/usr/bin/env python3
"""
Standalone V2 endpoint test script for ClubOS training package API
This shows exactly what we're doing to try to get invoice data from V2 endpoint
"""

import sys
import os
import time
import json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.services.api.clubos_training_api import ClubOSTrainingPackageAPI

def test_v2_endpoint():
    """Test V2 endpoint with all the different approaches we've tried"""
    
    print("=" * 80)
    print("ClubOS V2 Endpoint Test Script")
    print("=" * 80)
    
    # Initialize API
    api = ClubOSTrainingPackageAPI()
    
    if not api.authenticate():
        print("❌ Authentication failed")
        return
    
    print("✅ Authentication successful")
    print(f"🔑 Base URL: {api.base_url}")
    
    # Test with Miguel Belmontes who should have past due amounts
    member_id = "177673765"  # Miguel Belmontes
    print(f"\n🔍 Testing with member ID: {member_id} (Miguel Belmontes)")
    
    # Step 1: Get agreement IDs using the working bare list method
    print("\n--- Step 1: Get Agreement IDs ---")
    agreements_list = api.get_package_agreements_list(member_id)
    
    if not agreements_list:
        print("❌ No agreements found in bare list")
        return
    
    print(f"✅ Found {len(agreements_list)} agreements in bare list:")
    agreement_ids = []
    for agreement in agreements_list:
        agreement_id = agreement.get('packageAgreement', {}).get('id')
        agreement_name = agreement.get('packageAgreement', {}).get('name', 'Unknown')
        print(f"  - Agreement {agreement_id}: {agreement_name}")
        if agreement_id:
            agreement_ids.append(agreement_id)
    
    if not agreement_ids:
        print("❌ No valid agreement IDs found")
        return
    
    # Step 2: Test V2 endpoint with different approaches
    print(f"\n--- Step 2: Test V2 Endpoint on Agreement {agreement_ids[0]} ---")
    
    agreement_id = agreement_ids[0]  # Test with first agreement
    timestamp = int(time.time() * 1000)
    
    # Get current bearer token
    bearer_token = api._get_bearer_token()
    print(f"🔑 Bearer Token: {bearer_token[:30] + '...' if bearer_token else 'None'}")
    
    # Test different V2 URL formats and parameters
    test_cases = [
        {
            "name": "Current Method (include=invoices as string)",
            "url": f"{api.base_url}/api/agreements/package_agreements/V2/{agreement_id}",
            "params": {"include": "invoices", "_": timestamp},
            "headers": {
                "User-Agent": api.session.headers.get('User-Agent', 'Mozilla/5.0'),
                "Accept": "*/*",
                "X-Requested-With": "XMLHttpRequest",
                "Referer": f"{api.base_url}/action/PackageAgreementUpdated/spa/",
            }
        },
        {
            "name": "HAR File Method (multiple includes in query string)",
            "url": f"{api.base_url}/api/agreements/package_agreements/V2/{agreement_id}",
            "params": None,  # Build query string manually
            "query_string": f"include=invoices&include=scheduledPayments&include=prohibitChangeTypes&_={timestamp}",
            "headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36 Edg/140.0.0.0",
                "Accept": "*/*",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "Referer": f"{api.base_url}/action/PackageAgreementUpdated/spa/",
                "X-Requested-With": "XMLHttpRequest",
                "Sec-Ch-Ua": '"Chromium";v="140", "Not=A?Brand";v="24", "Microsoft Edge";v="140"',
                "Sec-Ch-Ua-Mobile": "?0",
                "Sec-Ch-Ua-Platform": '"Windows"',
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
            }
        },
        {
            "name": "List Method (include as array)",
            "url": f"{api.base_url}/api/agreements/package_agreements/V2/{agreement_id}",
            "params": {"include": ["invoices", "scheduledPayments"], "_": timestamp},
            "headers": {
                "User-Agent": api.session.headers.get('User-Agent', 'Mozilla/5.0'),
                "Accept": "application/json, text/plain, */*",
                "X-Requested-With": "XMLHttpRequest",
                "Referer": f"{api.base_url}/action/Agreements",
            }
        },
        {
            "name": "Simple Method (no includes)",
            "url": f"{api.base_url}/api/agreements/package_agreements/V2/{agreement_id}",
            "params": {"_": timestamp},
            "headers": {
                "User-Agent": api.session.headers.get('User-Agent', 'Mozilla/5.0'),
                "Accept": "*/*",
                "X-Requested-With": "XMLHttpRequest",
                "Referer": f"{api.base_url}/action/PackageAgreementUpdated/spa/",
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i}: {test_case['name']} ---")
        
        try:
            headers = test_case['headers'].copy()
            if bearer_token:
                headers['Authorization'] = f'Bearer {bearer_token}'
            
            # Build URL
            if 'query_string' in test_case:
                url = f"{test_case['url']}?{test_case['query_string']}"
                print(f"🔗 URL: {url}")
                response = api.session.get(url, headers=headers, timeout=20)
            else:
                url = test_case['url']
                params = test_case['params']
                print(f"🔗 URL: {url}")
                print(f"📋 Params: {params}")
                response = api.session.get(url, headers=headers, params=params, timeout=20)
            
            print(f"📊 Status Code: {response.status_code}")
            print(f"📊 Content-Type: {response.headers.get('Content-Type', 'N/A')}")
            print(f"📊 Content Length: {len(response.text or '')}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print("✅ SUCCESS! JSON response received")
                    
                    # Look for invoice data
                    if 'invoices' in data:
                        invoices = data['invoices']
                        print(f"💰 Found {len(invoices)} invoices:")
                        total_past_due = 0
                        
                        for invoice in invoices:
                            invoice_id = invoice.get('id', 'N/A')
                            amount = float(invoice.get('amount', 0))
                            status = invoice.get('status', 'N/A')
                            due_date = invoice.get('dueDate', 'N/A')
                            
                            print(f"  📄 Invoice {invoice_id}: ${amount:.2f} - Status: {status} - Due: {due_date}")
                            
                            # Status 5 = Past Due according to ClubOS
                            if status == 5:
                                total_past_due += amount
                        
                        print(f"💰 TOTAL PAST DUE: ${total_past_due:.2f}")
                        
                        if total_past_due > 0:
                            print("🎉 FOUND PAST DUE AMOUNTS! This method works!")
                            break
                        else:
                            print("ℹ️ No past due amounts found in this response")
                    else:
                        print("ℹ️ No 'invoices' key in response")
                        print(f"📋 Available keys: {list(data.keys())}")
                        
                except json.JSONDecodeError as e:
                    print(f"❌ JSON decode error: {e}")
                    print(f"Raw response (first 200 chars): {response.text[:200]}")
            else:
                print(f"❌ HTTP Error {response.status_code}")
                print(f"Error response: {response.text[:300]}")
                
        except Exception as e:
            print(f"❌ Request failed: {e}")
    
    print(f"\n--- Step 3: Debug Session Info ---")
    print(f"🍪 Session Cookies:")
    for name, value in api.session.cookies.items():
        if name in ['JSESSIONID', 'apiV3AccessToken', 'delegatedUserId']:
            print(f"  {name}: {value[:20]}...")
    
    print(f"\n--- Step 4: What Works vs What Doesn't ---")
    print("✅ WORKING:")
    print("  - Authentication")
    print("  - Delegation to member")
    print("  - Bare list endpoint (/api/agreements/package_agreements/list)")
    print("  - Agreement ID extraction")
    
    print("❌ NOT WORKING:")
    print("  - V2 endpoint (/api/agreements/package_agreements/V2/{id}) returns HTTP 500")
    print("  - All parameter combinations tried")
    print("  - All header combinations tried")
    print("  - Cannot get invoice data with past due amounts")
    
    print(f"\n--- Step 5: Raw Request Details ---")
    print("If someone smarter wants to debug, here are the exact details:")
    print(f"Base URL: {api.base_url}")
    print(f"Member ID: {member_id}")
    print(f"Agreement ID: {agreement_ids[0]}")
    print(f"Session ID: {api.session.cookies.get('JSESSIONID', 'N/A')}")
    print(f"Bearer Token: {bearer_token}")
    print(f"Delegated User ID: {api.session.cookies.get('delegatedUserId', 'N/A')}")

if __name__ == "__main__":
    test_v2_endpoint()