#!/usr/bin/env python3
"""
Debug V2 endpoint issues - figure out why V2 calls are failing with HTTP 500
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.services.api.clubos_training_api import ClubOSTrainingPackageAPI
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def debug_v2_endpoint():
    """Debug why V2 endpoint calls are failing"""
    api = ClubOSTrainingPackageAPI()
    
    if not api.authenticate():
        print("❌ Authentication failed")
        return
    
    # Test with Miguel Belmontes who we know has past due amounts
    member_id = "177673765"  # Miguel Belmontes
    print(f"🔍 Debugging V2 endpoint for Miguel Belmontes (ID: {member_id})")
    
    # Step 1: Get agreements list to get agreement IDs
    print("\n=== Step 1: Get agreement IDs ===")
    agreements_list = api.get_package_agreements_list(member_id)
    
    if not agreements_list:
        print("❌ No agreements found!")
        return
    
    print(f"✅ Found {len(agreements_list)} agreements")
    for agreement in agreements_list:
        agreement_id = agreement.get('packageAgreement', {}).get('id')
        agreement_name = agreement.get('packageAgreement', {}).get('name', 'Unknown')
        print(f"  - Agreement {agreement_id}: {agreement_name}")
    
    # Step 2: Test V2 endpoint on each agreement
    print("\n=== Step 2: Test V2 endpoint on each agreement ===")
    
    for agreement in agreements_list:
        agreement_id = agreement.get('packageAgreement', {}).get('id')
        if not agreement_id:
            continue
            
        print(f"\n--- Testing V2 for agreement {agreement_id} ---")
        
        # Try the current V2 method
        v2_result = api.get_package_agreement_details(agreement_id)
        
        if 'error' in v2_result:
            print(f"❌ V2 failed: {v2_result['error']}")
            
            # Let's try a more direct approach - replicate the exact dev tools request
            print("🔧 Trying direct V2 request with exact dev tools headers...")
            
            try:
                import time
                timestamp = int(time.time() * 1000)
                
                # Use the EXACT URL format from successful dev tools request
                v2_url = f"{api.base_url}/api/agreements/package_agreements/V2/{agreement_id}"
                
                # Build query parameters exactly like dev tools
                params = {
                    'include': ['invoices', 'scheduledPayments', 'prohibitChangeTypes'],
                    '_': timestamp
                }
                
                # Use exact headers from successful request
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36 Edg/140.0.0.0',
                    'Accept': '*/*',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br, zstd',
                    'Referer': f'{api.base_url}/action/PackageAgreementUpdated/spa/',
                    'X-Requested-With': 'XMLHttpRequest',
                    'Sec-Ch-Ua': '"Chromium";v="140", "Not=A?Brand";v="24", "Microsoft Edge";v="140"',
                    'Sec-Ch-Ua-Mobile': '?0',
                    'Sec-Ch-Ua-Platform': '"Windows"',
                    'Sec-Fetch-Dest': 'empty',
                    'Sec-Fetch-Mode': 'cors',
                    'Sec-Fetch-Site': 'same-origin',
                }
                
                # Add Bearer token
                bearer = api._get_bearer_token()
                if bearer:
                    headers['Authorization'] = f'Bearer {bearer}'
                    print(f"🔑 Using Bearer token: {bearer[:20]}...")
                else:
                    print("⚠️ No Bearer token available")
                
                print(f"🔍 Direct V2 URL: {v2_url}")
                print(f"📋 Parameters: {params}")
                
                response = api.session.get(v2_url, headers=headers, params=params, timeout=20)
                
                print(f"📊 Response Status: {response.status_code}")
                print(f"📊 Response Headers: {dict(response.headers)}")
                print(f"📊 Response Length: {len(response.text or '')}")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        print("✅ V2 SUCCESS with direct approach!")
                        
                        # Look for invoice data
                        invoices = data.get('invoices', [])
                        print(f"💰 Found {len(invoices)} invoices:")
                        
                        total_past_due = 0
                        for invoice in invoices:
                            invoice_id = invoice.get('id')
                            amount = float(invoice.get('amount', 0))
                            status = invoice.get('status')  # 1=Paid, 2=Pending, 5=Past Due
                            due_date = invoice.get('dueDate')
                            
                            print(f"  Invoice {invoice_id}: ${amount:.2f} - Status: {status} - Due: {due_date}")
                            
                            if status == 5:  # Past due
                                total_past_due += amount
                        
                        print(f"💰 TOTAL PAST DUE: ${total_past_due:.2f}")
                        
                        if total_past_due > 0:
                            print("🎉 SUCCESS! Found actual past due amounts in V2 data!")
                        else:
                            print("⚠️ V2 data shows no past due amounts")
                        
                    except Exception as json_error:
                        print(f"❌ JSON parse error: {json_error}")
                        print(f"Raw response: {response.text[:500]}...")
                else:
                    print(f"❌ Direct V2 request failed: {response.status_code}")
                    print(f"Response: {response.text[:500]}...")
                    
            except Exception as e:
                print(f"❌ Direct V2 attempt failed: {e}")
        else:
            print(f"✅ V2 succeeded: {v2_result}")

if __name__ == "__main__":
    debug_v2_endpoint()