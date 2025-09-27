#!/usr/bin/env python3
"""
Test the CORRECTED V2 endpoint method with GET instead of POST
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.services.api.clubos_training_api import ClubOSTrainingPackageAPI

def test_corrected_v2_method():
    """Test the corrected V2 method with Miguel Belmontes"""
    
    print("=" * 80)
    print("Testing CORRECTED V2 Endpoint Method (GET instead of POST)")
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
    
    # Step 1: Get agreement IDs using the working bare list method
    print("\n--- Step 1: Get Agreement IDs ---")
    agreements_list = api.get_package_agreements_list(member_id)
    
    if not agreements_list:
        print("❌ No agreements found")
        return
    
    print(f"✅ Found {len(agreements_list)} agreements:")
    for agreement in agreements_list:
        agreement_id = agreement.get('packageAgreement', {}).get('id')
        agreement_name = agreement.get('packageAgreement', {}).get('name', 'Unknown')
        print(f"  - Agreement {agreement_id}: {agreement_name}")
    
    # Step 2: Test the CORRECTED V2 endpoint method
    print(f"\n--- Step 2: Test CORRECTED V2 Endpoint ---")
    
    first_agreement = agreements_list[0]
    agreement_id = first_agreement.get('packageAgreement', {}).get('id')
    
    print(f"🧪 Testing corrected V2 method with agreement {agreement_id}")
    
    # Call the corrected V2 method
    v2_result = api.get_package_agreement_details(agreement_id)
    
    if v2_result.get('success'):
        print("🎉 SUCCESS! V2 endpoint is now working!")
        print(f"📊 Agreement ID: {v2_result.get('agreement_id')}")
        print(f"💰 Past Due Amount: ${v2_result.get('past_due_amount', 0):.2f}")
        print(f"📄 Total Invoices: {v2_result.get('total_invoices', 0)}")
        
        # Show invoice details if available
        data = v2_result.get('data', {})
        invoices = data.get('invoices', [])
        
        if invoices:
            print("\n📋 Invoice Details:")
            for invoice in invoices:
                invoice_id = invoice.get('id', 'N/A')
                status = invoice.get('status', 'N/A')
                amount = invoice.get('amount', 0)
                due_date = invoice.get('dueDate', 'N/A')
                
                status_text = "Past Due" if status == 5 else f"Status {status}"
                print(f"  💰 Invoice {invoice_id}: ${amount:.2f} - {status_text} - Due: {due_date}")
        
        return True
    else:
        print("❌ V2 endpoint still failed")
        print(f"Error: {v2_result.get('error', 'Unknown error')}")
        return False

if __name__ == "__main__":
    success = test_corrected_v2_method()
    
    if success:
        print("\n🎉 V2 ENDPOINT IS NOW WORKING! The fix was successful!")
        print("✅ Now we can get actual invoice data with real past due amounts!")
    else:
        print("\n❌ V2 endpoint is still broken. Need more debugging.")