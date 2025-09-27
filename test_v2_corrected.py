#!/usr/bin/env python3
"""
Test script to verify the corrected V2 endpoint implementation using the exact agreement ID from dev tools.
"""

import sys
import os

# Add the src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from services.api.clubos_training_api import ClubOSTrainingPackageAPI

def test_v2_corrected():
    """Test the corrected V2 endpoint with the exact agreement ID from the successful dev tools request."""
    
    print("🧪 Testing V2 endpoint with corrected URL format")
    print("="*60)
    
    # Initialize API
    api = ClubOSTrainingPackageAPI()
    
    # Step 1: Authenticate
    print("\n1️⃣ Authenticating...")
    if not api.authenticate():
        print("❌ Authentication failed!")
        return False
        
    print("✅ Authentication successful")
    
    # Step 2: Test with the exact agreement ID that worked in dev tools
    agreement_id = "1672118"  # From the successful dev tools request
    member_id = "191215290"   # Member ID from the dev tools request
    
    print(f"\n2️⃣ Testing V2 endpoint with agreement ID: {agreement_id}")
    
    # First delegate to the member context (this was working in dev tools)
    print(f"🔑 Delegating to member: {member_id}")
    delegation_success = api.delegate_to_member(member_id)
    print(f"Delegation result: {'✅ Success' if delegation_success else '❌ Failed'}")
    
    # Now test the V2 endpoint with corrected format
    print(f"\n3️⃣ Fetching V2 data for agreement {agreement_id}...")
    result = api.get_package_agreement_details(agreement_id)
    
    if isinstance(result, dict) and result.get('success'):
        print("✅ SUCCESS! V2 endpoint working!")
        
        # Extract invoice data like the dev tools response
        data = result.get('data', {})
        include_data = data.get('include', {})
        invoices = include_data.get('invoices', [])
        scheduled_payments = include_data.get('scheduledPayments', [])
        
        print(f"\n📊 V2 Response Summary:")
        print(f"   - Agreement ID: {data.get('id')}")
        print(f"   - Agreement Name: {data.get('name')}")
        print(f"   - Member ID: {data.get('memberId')}")
        print(f"   - Agreement Status: {data.get('agreementStatus')}")
        print(f"   - Total Invoices: {len(invoices)}")
        print(f"   - Scheduled Payments: {len(scheduled_payments)}")
        
        if invoices:
            print(f"\n💰 Invoice Details:")
            for i, invoice in enumerate(invoices[:3]):  # Show first 3 invoices
                status_name = "Paid" if invoice.get('invoiceStatus') == 1 else f"Status {invoice.get('invoiceStatus')}"
                print(f"   Invoice {i+1}: ID={invoice.get('id')}, Status={status_name}, Total=${invoice.get('total')}, Remaining=${invoice.get('remainingTotal')}, Date={invoice.get('billingDate')}")
        
        return True
        
    else:
        print("❌ V2 endpoint failed!")
        print(f"Error: {result}")
        return False

if __name__ == "__main__":
    success = test_v2_corrected()
    print("\n" + "="*60)
    if success:
        print("🎉 BREAKTHROUGH V2 TEST: SUCCESS!")
        print("The V2 endpoint is now working with the corrected URL format!")
    else:
        print("❌ V2 test failed - check the error details above")