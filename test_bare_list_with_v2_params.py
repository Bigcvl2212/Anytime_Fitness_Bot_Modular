#!/usr/bin/env python3
"""
Test the bare list endpoint with V2 parameters to get invoice data directly
"""

import sys
import os
import json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.services.api.clubos_training_api import ClubOSTrainingPackageAPI

def test_bare_list_with_v2_params():
    """Test if adding V2 parameters to bare list gives us invoice data"""
    
    print("=" * 80)
    print("Testing Bare List Endpoint with V2 Parameters")
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
    
    # Step 1: Test the modified bare list method with V2 parameters
    print("\n--- Step 1: Test Bare List with V2 Parameters ---")
    agreements_list = api.get_package_agreements_list(member_id)
    
    if not agreements_list:
        print("❌ No agreements found")
        return
    
    print(f"✅ Found {len(agreements_list)} agreements with V2 parameters:")
    
    # Step 2: Examine the response structure to see if we got invoice data
    print(f"\n--- Step 2: Examine Response Structure ---")
    
    for i, agreement in enumerate(agreements_list):
        agreement_id = agreement.get('packageAgreement', {}).get('id')
        agreement_name = agreement.get('packageAgreement', {}).get('name', 'Unknown')
        
        print(f"\n📋 Agreement {i+1}: {agreement_id} - {agreement_name}")
        print(f"📊 Top-level keys: {list(agreement.keys())}")
        
        # Check if we have invoice data
        if 'invoices' in agreement:
            invoices = agreement['invoices']
            print(f"🎉 FOUND INVOICES! Count: {len(invoices)}")
            
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
            
            print(f"💰 Total Past Due for Agreement {agreement_id}: ${total_past_due:.2f}")
            
            if total_past_due > 0:
                print("🎉 FOUND REAL PAST DUE AMOUNTS IN BARE LIST!")
        else:
            print("ℹ️ No 'invoices' key found in agreement")
        
        # Check if we have scheduled payments
        if 'scheduledPayments' in agreement:
            scheduled_payments = agreement['scheduledPayments']
            print(f"📅 Found {len(scheduled_payments)} scheduled payments")
        else:
            print("ℹ️ No 'scheduledPayments' key found in agreement")
        
        # Look inside packageAgreement for nested data
        package_agreement = agreement.get('packageAgreement', {})
        if package_agreement:
            print(f"📦 packageAgreement keys: {list(package_agreement.keys())}")
            
            # Check if invoices are nested inside packageAgreement
            if 'invoices' in package_agreement:
                nested_invoices = package_agreement['invoices']
                print(f"🎉 FOUND NESTED INVOICES! Count: {len(nested_invoices)}")
            
            # Check for other nested billing data
            billing_keys = [k for k in package_agreement.keys() if 'bill' in k.lower() or 'invoice' in k.lower() or 'payment' in k.lower()]
            if billing_keys:
                print(f"💰 Found billing-related keys: {billing_keys}")
    
    # Step 3: Save the raw response for analysis
    print(f"\n--- Step 3: Save Raw Response for Analysis ---")
    
    # Let's also make a direct call to see the raw response
    if api.delegate_to_member(member_id):
        import time
        url = f"{api.base_url}/api/agreements/package_agreements/list?include=invoices&include=scheduledPayments&include=prohibitChangeTypes"
        response = api.session.get(url, timeout=20)
        
        if response.status_code == 200:
            raw_data = response.json()
            
            # Save to file for analysis
            filename = f"bare_list_with_v2_params_{member_id}.json"
            with open(filename, 'w') as f:
                json.dump(raw_data, f, indent=2)
            
            print(f"💾 Saved raw response to {filename}")
            print(f"📊 Response contains {len(raw_data)} agreements")
            
            # Quick analysis of what we got
            for agreement in raw_data:
                agreement_id = agreement.get('packageAgreement', {}).get('id')
                has_invoices = 'invoices' in agreement or 'invoices' in agreement.get('packageAgreement', {})
                has_scheduled = 'scheduledPayments' in agreement or 'scheduledPayments' in agreement.get('packageAgreement', {})
                
                print(f"  📋 Agreement {agreement_id}: Invoices={has_invoices}, Scheduled={has_scheduled}")
        else:
            print(f"❌ Direct call failed: {response.status_code}")
    
    return True

if __name__ == "__main__":
    success = test_bare_list_with_v2_params()
    
    if success:
        print("\n✅ Test completed! Check the output above to see if we got invoice data.")
        print("🔍 If we found invoices in the bare list response, we can avoid V2 calls entirely!")
    else:
        print("\n❌ Test failed.")