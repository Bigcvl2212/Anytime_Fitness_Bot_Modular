#!/usr/bin/env python3
"""
Test the FINAL CORRECTED V2 endpoint method with GET + query params + cookies
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.services.api.clubos_training_api import ClubOSTrainingPackageAPI

def test_final_corrected_v2():
    """Test the final corrected V2 method with cookies included"""
    
    print("=" * 80)
    print("Testing FINAL CORRECTED V2 Method (GET + Query Params + Cookies)")
    print("=" * 80)
    
    # Initialize API
    api = ClubOSTrainingPackageAPI()
    
    if not api.authenticate():
        print("❌ Authentication failed")
        return
    
    print("✅ Authentication successful")
    
    # Test with Miguel Belmontes who should have past due amounts
    member_id = "177673765"  # Miguel Belmontes
    print(f"\n🔍 Testing with member ID: {member_id} (Miguel Belmontes)")
    
    # Step 1: Get agreement IDs and delegate to member
    print("\n--- Step 1: Get Agreement IDs and Delegate ---")
    agreements_list = api.get_package_agreements_list(member_id)
    
    if not agreements_list:
        print("❌ No agreements found")
        return
    
    print(f"✅ Found {len(agreements_list)} agreements after delegation:")
    for agreement in agreements_list:
        agreement_id = agreement.get('packageAgreement', {}).get('id')
        agreement_name = agreement.get('packageAgreement', {}).get('name', 'Unknown')
        print(f"  - Agreement {agreement_id}: {agreement_name}")
    
    # Step 2: Show current session state
    print(f"\n--- Step 2: Session State Debug ---")
    cookies = api.session.cookies.get_dict()
    important_cookies = ['JSESSIONID', 'delegatedUserId', 'loggedInUserId', 'userId', 'apiV3AccessToken']
    
    for cookie_name in important_cookies:
        cookie_value = cookies.get(cookie_name, 'Not Set')
        if cookie_value != 'Not Set' and len(cookie_value) > 20:
            cookie_value = cookie_value[:20] + '...'
        print(f"🍪 {cookie_name}: {cookie_value}")
    
    bearer_token = api._get_bearer_token()
    print(f"🔑 Bearer Token: {'Set (' + bearer_token[:20] + '...)' if bearer_token else 'Not Set'}")
    
    # Step 3: Test the FINAL CORRECTED V2 endpoint method
    print(f"\n--- Step 3: Test FINAL CORRECTED V2 Method ---")
    
    # Test with the known working agreement from your HAR analysis
    test_agreement_id = "1651819"  # From your working HAR
    print(f"🧪 Testing V2 method with known working agreement {test_agreement_id}")
    
    # Call the corrected V2 method
    v2_result = api.get_package_agreement_details(test_agreement_id)
    
    if v2_result.get('success'):
        print("🎉 SUCCESS! V2 endpoint is now working with cookies!")
        print(f"📊 Agreement ID: {v2_result.get('agreement_id')}")
        print(f"💰 Past Due Amount: ${v2_result.get('past_due_amount', 0):.2f}")
        print(f"📄 Total Invoices: {v2_result.get('total_invoices', 0)}")
        
        # Show invoice details if available
        data = v2_result.get('data', {})
        invoices = data.get('invoices', [])
        
        if invoices:
            print("\n📋 Invoice Details:")
            total_past_due = 0
            for invoice in invoices:
                invoice_id = invoice.get('id', 'N/A')
                status = invoice.get('status', 'N/A')
                amount = float(invoice.get('amount', 0))
                due_date = invoice.get('dueDate', 'N/A')
                
                status_text = "Past Due" if status == 5 else f"Status {status}"
                print(f"  💰 Invoice {invoice_id}: ${amount:.2f} - {status_text} - Due: {due_date}")
                
                if status == 5:
                    total_past_due += amount
            
            print(f"\n💰 TOTAL PAST DUE FROM V2: ${total_past_due:.2f}")
            
            if total_past_due > 0:
                print("🎉 FOUND REAL PAST DUE AMOUNTS IN V2 DATA!")
        
        # Test with Miguel's actual agreement too
        first_agreement = agreements_list[0]
        miguel_agreement_id = first_agreement.get('packageAgreement', {}).get('id')
        
        print(f"\n🧪 Now testing with Miguel's agreement {miguel_agreement_id}")
        miguel_v2_result = api.get_package_agreement_details(miguel_agreement_id)
        
        if miguel_v2_result.get('success'):
            print(f"✅ Miguel's V2 data retrieved successfully!")
            miguel_past_due = miguel_v2_result.get('past_due_amount', 0)
            print(f"💰 Miguel's Past Due Amount: ${miguel_past_due:.2f}")
        else:
            print(f"❌ Miguel's V2 failed: {miguel_v2_result.get('error')}")
        
        return True
    else:
        print("❌ V2 endpoint still failed even with cookies")
        print(f"Error: {v2_result.get('error', 'Unknown error')}")
        
        # Show what cookies we tried to send
        print("\n🍪 Cookies we attempted to send:")
        for cookie_name in important_cookies:
            cookie_value = cookies.get(cookie_name, 'Not Set')
            print(f"  {cookie_name}: {'Set' if cookie_value != 'Not Set' else 'Not Set'}")
        
        return False

if __name__ == "__main__":
    success = test_final_corrected_v2()
    
    if success:
        print("\n🎉 V2 ENDPOINT IS NOW WORKING! The cookie fix was successful!")
        print("✅ Now we can get actual invoice data with real past due amounts!")
        print("✅ We can finally fix the dashboard to show accurate past due clients!")
    else:
        print("\n❌ V2 endpoint is still broken. Need to investigate cookies/session state.")