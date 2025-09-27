#!/usr/bin/env python3
"""
TEST THE EXACT V2 ENDPOINT CALL THAT WORKED LAST TIME
Using the exact cURL format that broke through the 500 errors
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.services.api.clubos_training_api import ClubOSTrainingPackageAPI
import requests
import json

def test_exact_v2_curl_format():
    """Test using the EXACT cURL format that worked last time"""
    
    print("=" * 80)
    print("🔓 TESTING EXACT V2 CURL FORMAT THAT WORKED LAST TIME")
    print("=" * 80)
    
    # Initialize API to get authenticated session
    api = ClubOSTrainingPackageAPI()
    
    if not api.authenticate():
        print("❌ Authentication failed")
        return False
    
    print("✅ Authentication successful")
    
    # Get member agreements first
    member_id = "177673765"  # Miguel Belmontes
    print(f"\n🔍 Getting agreements for member {member_id}")
    
    agreements_list = api.get_package_agreements_list(member_id)
    if not agreements_list:
        print("❌ No agreements found")
        return False
    
    print(f"✅ Found {len(agreements_list)} agreements")
    
    # Extract agreement IDs
    agreement_ids = []
    for agreement in agreements_list:
        if 'packageAgreement' in agreement:
            agreement_id = agreement['packageAgreement'].get('id')
            if agreement_id:
                agreement_ids.append(str(agreement_id))
                print(f"  📋 Agreement ID: {agreement_id}")
    
    # Dump current session cookies for debugging
    print("\n📦 Session cookies after delegation:")
    all_cookies = api.session.cookies.get_dict()
    for key, value in all_cookies.items():
        display_value = f"{value[:60]}..." if isinstance(value, str) and len(value) > 60 else value
        print(f"  {key}: {display_value}")

    # Now test the EXACT V2 cURL format that worked
    for agreement_id in agreement_ids:
        print(f"\n{'='*60}")
        print(f"🔥 TESTING V2 WITH EXACT CURL FORMAT: Agreement {agreement_id}")
        print(f"{'='*60}")
        
        # Get the current session state
        bearer_token = api._get_bearer_token()
        session_cookies = api.session.cookies.get_dict()
        
        # Build the EXACT URL format that worked
        # Include timestamp query like browser to avoid cached responses
        import time
        timestamp = int(time.time() * 1000)
        url = (
            "https://anytime.club-os.com/api/agreements/package_agreements/V2/"
            f"{agreement_id}?include=invoices&include=scheduledPayments&include=prohibitChangeTypes&_={timestamp}"
        )
        
        # EXACT headers from the working cURL
        headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "en-US,en;q=0.9",
            "Authorization": f"Bearer {bearer_token}",
            "Referer": "https://anytime.club-os.com/action/PackageAgreementUpdated/spa/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36 Edg/140.0.0.0",
            "X-Requested-With": "XMLHttpRequest",
            "Origin": "https://anytime.club-os.com",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty"
        }
        
        # CRITICAL COOKIES that made it work last time
        cookies = {
            "JSESSIONID": session_cookies.get('JSESSIONID'),
            "delegatedUserId": session_cookies.get('delegatedUserId'),
            "loggedInUserId": session_cookies.get('loggedInUserId'),
            "apiV3AccessToken": session_cookies.get('apiV3AccessToken'),
            "apiV3RefreshToken": session_cookies.get('apiV3RefreshToken')
        }
        
        print(f"🔑 Bearer Token: {bearer_token[:50]}...")
        print(f"🍪 Critical Cookies:")
        for key, value in cookies.items():
            if value:
                display_value = f"{value[:20]}..." if len(str(value)) > 20 else value
                print(f"    {key}: {display_value}")
        
        # Make the EXACT request format that worked
        print(f"\n🚀 Making GET request to: {url}")
        debug_headers = {k: headers[k] for k in headers}
        print(f"🧾 Request headers: {json.dumps(debug_headers, indent=2)}")
        print(f"🧾 Request cookies: {json.dumps({k: v for k, v in cookies.items() if v}, indent=2)}")

        # Use the authenticated session (preserves TLS + cookie jar)
        response = api.session.get(url, headers=headers, cookies=cookies, timeout=20)
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📄 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("🎉 SUCCESS! V2 endpoint is working!")
            
            try:
                data = response.json()
                invoices = data.get("invoices", [])
                scheduled_payments = data.get("scheduledPayments", [])
                
                print(f"📄 Total invoices: {len(invoices)}")
                print(f"💳 Scheduled payments: {len(scheduled_payments)}")
                
                # Calculate real past due amount from actual invoices
                past_due_total = 0.0
                current_invoices = []
                past_due_invoices = []
                
                for invoice in invoices:
                    invoice_id = invoice.get('id', 'N/A')
                    status = invoice.get('status')
                    amount = float(invoice.get('amount', 0))
                    due_date = invoice.get('dueDate', 'N/A')
                    
                    if status == 5:  # Status 5 = Past Due
                        past_due_total += amount
                        past_due_invoices.append(invoice)
                        print(f"  ⚠️ PAST DUE: Invoice {invoice_id}: ${amount:.2f} - Due: {due_date}")
                    else:
                        current_invoices.append(invoice)
                        print(f"  ✅ Current: Invoice {invoice_id}: ${amount:.2f} - Status: {status} - Due: {due_date}")
                
                print(f"\n💰 REAL PAST DUE AMOUNT FROM V2: ${past_due_total:.2f}")
                print(f"📋 Past Due Invoices: {len(past_due_invoices)}")
                print(f"📋 Current Invoices: {len(current_invoices)}")
                
                # Show scheduled payments too
                if scheduled_payments:
                    print(f"\n💳 Upcoming Scheduled Payments:")
                    for payment in scheduled_payments[:3]:
                        payment_date = payment.get('scheduledDate', 'N/A')
                        payment_amount = payment.get('amount', 0)
                        print(f"  📅 ${payment_amount:.2f} scheduled for {payment_date}")
                
                return True
                
            except Exception as json_error:
                print(f"❌ JSON parsing failed: {json_error}")
                print(f"Raw response: {response.text[:500]}")
                
        else:
            print(f"❌ V2 request failed: {response.status_code}")
            print(f"Error response: {response.text[:500]}")
            # Save debug payload for deeper inspection
            debug_filename = f"debug_v2_response_{agreement_id}.txt"
            try:
                with open(debug_filename, 'w', encoding='utf-8') as f:
                    f.write(response.text)
                print(f"📝 Saved error body to {debug_filename}")
            except Exception as e:
                print(f"⚠️ Failed to save debug response: {e}")
    
    return False

if __name__ == "__main__":
    print("🚀 Testing the EXACT V2 cURL format that worked last time")
    
    success = test_exact_v2_curl_format()
    
    if success:
        print("\n🎉 V2 ENDPOINT IS WORKING WITH EXACT CURL FORMAT!")
        print("✅ We have the real invoice data with actual past due amounts!")
        print("✅ This is the breakthrough we needed!")
    else:
        print("\n❌ V2 endpoint still not working - need to debug further")