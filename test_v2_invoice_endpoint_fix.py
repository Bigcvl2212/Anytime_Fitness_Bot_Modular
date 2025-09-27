#!/usr/bin/env python3
"""
Test the V2 training invoice endpoint with PROPER COOKIE INJECTION:
1. Get package agreements list for member (with delegation) 
2. Extract agreement IDs from the list
3. Call V2 endpoint for each agreement with EXPLICIT COOKIE INJECTION to get REAL invoice data
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.services.api.clubos_training_api import ClubOSTrainingPackageAPI
import json

def test_v2_invoice_endpoint_with_cookies():
    """Test the V2 endpoint with the proper cookie injection fix to get REAL invoice data"""
    
    print("=" * 80)
    print("Testing V2 Training Invoice Flow with COOKIE FIX")
    print("Step 1: Get agreement list with delegation")
    print("Step 2: Extract agreement IDs from list")
    print("Step 3: Call V2 for each agreement with EXPLICIT COOKIE INJECTION")
    print("=" * 80)
    
    # Initialize API
    api = ClubOSTrainingPackageAPI()
    
    if not api.authenticate():
        print("❌ Authentication failed")
        return False
    
    print("✅ Authentication successful")
    
    # Test with Miguel Belmontes who should have training packages
    member_id = "177673765"  # Miguel Belmontes
    print(f"\n🔍 Testing with member ID: {member_id} (Miguel Belmontes)")
    
    # === STEP 1: Get Package Agreements List ===
    print(f"\n{'='*60}")
    print("STEP 1: Get Package Agreements List")
    print(f"{'='*60}")
    
    agreements_list = api.get_package_agreements_list(member_id)
    
    if not agreements_list:
        print("❌ No agreements found in list")
        return False
    
    print(f"✅ Found {len(agreements_list)} agreements in list")
    
    # === STEP 2: Extract Agreement IDs ===
    print(f"\n{'='*60}")
    print("STEP 2: Extract Agreement IDs")
    print(f"{'='*60}")
    
    agreement_ids = []
    for i, agreement in enumerate(agreements_list):
        print(f"\nAgreement {i+1} structure:")
        
        # Handle the correct structure from delegated member call
        agreement_id = None
        agreement_name = "Unknown"
        
        if isinstance(agreement, dict):
            # New structure from delegate + bare list
            if 'packageAgreement' in agreement and isinstance(agreement['packageAgreement'], dict):
                agreement_id = agreement['packageAgreement'].get('id')
                agreement_name = agreement['packageAgreement'].get('name', 'Unknown')
                print(f"  ✅ Found ID in packageAgreement: {agreement_id}")
                print(f"  📄 Agreement Name: {agreement_name}")
            # Fallback to old structure
            elif 'id' in agreement:
                agreement_id = agreement.get('id')
                agreement_name = agreement.get('name', 'Unknown')
                print(f"  ✅ Found ID directly: {agreement_id}")
                print(f"  📄 Agreement Name: {agreement_name}")
            else:
                print(f"  ❌ Could not find ID in structure:")
                print(f"      Keys: {list(agreement.keys())}")
        
        if agreement_id:
            agreement_ids.append(str(agreement_id))
            print(f"  ✅ Added agreement ID {agreement_id} to list")
        else:
            print(f"  ❌ Could not extract agreement ID")
    
    if not agreement_ids:
        print("❌ No valid agreement IDs found")
        return False
    
    print(f"\n✅ Extracted {len(agreement_ids)} agreement IDs: {agreement_ids}")
    
    # === STEP 3: Call V2 with PROPER COOKIE INJECTION ===
    print(f"\n{'='*60}")
    print("STEP 3: Call V2 Endpoint with EXPLICIT COOKIE INJECTION")
    print(f"{'='*60}")
    
    all_invoice_data = []
    total_past_due = 0.0
    
    for i, agreement_id in enumerate(agreement_ids):
        print(f"\n--- Processing Agreement {i+1}/{len(agreement_ids)}: {agreement_id} ---")
        
        # Call the V2 endpoint with the cookie fix
        print(f"🔥 Calling V2 endpoint with EXPLICIT COOKIE INJECTION for agreement {agreement_id}")
        v2_result = api.get_package_agreement_details(agreement_id)
        
        if v2_result.get('success'):
            print(f"🎉 V2 SUCCESS! Got REAL invoice data for agreement {agreement_id}")
            
            # Extract REAL invoice data
            invoices = v2_result.get('invoices', [])
            past_due_amount = v2_result.get('past_due_amount', 0.0)
            scheduled_payments = v2_result.get('scheduledPayments', [])
            
            print(f"  📊 Found {len(invoices)} REAL invoices")
            print(f"  💰 REAL Past Due Amount: ${past_due_amount:.2f}")
            print(f"  💳 Scheduled Payments: {len(scheduled_payments)}")
            
            if invoices:
                print(f"  📋 REAL Invoice Details:")
                for invoice in invoices[:5]:  # Show first 5 invoices
                    invoice_id = invoice.get('id', 'N/A')
                    status = invoice.get('status', 'N/A') 
                    amount = float(invoice.get('amount', 0))
                    due_date = invoice.get('dueDate', 'N/A')
                    
                    status_text = "Past Due" if status == 5 else f"Status {status}"
                    print(f"    💰 Invoice {invoice_id}: ${amount:.2f} - {status_text} - Due: {due_date}")
            
            # Add to totals
            total_past_due += past_due_amount
            all_invoice_data.append({
                'agreement_id': agreement_id,
                'invoices': invoices,
                'past_due_amount': past_due_amount,
                'scheduled_payments': scheduled_payments
            })
            
        else:
            print(f"❌ V2 STILL FAILED for agreement {agreement_id}")
            error = v2_result.get('error', 'Unknown error')
            print(f"  Error: {error}")
            
            # If V2 still fails, show what cookies we're trying to send
            print(f"  🍪 Let's debug the cookie injection...")
            current_cookies = api.session.cookies.get_dict()
            print(f"  🍪 Current session cookies:")
            for key, value in current_cookies.items():
                if key in ['JSESSIONID', 'delegatedUserId', 'loggedInUserId', 'apiV3AccessToken']:
                    print(f"    {key}: {'Set' if value else 'NOT SET'}")
    
    # === FINAL RESULTS ===
    print(f"\n{'='*60}")
    print("FINAL RESULTS - REAL INVOICE DATA FROM V2")
    print(f"{'='*60}")
    
    if all_invoice_data:
        print(f"🎉 SUCCESS! Retrieved REAL invoice data for {len(all_invoice_data)} agreements")
        print(f"💰 TOTAL REAL PAST DUE AMOUNT: ${total_past_due:.2f}")
        
        total_invoices = sum(len(data['invoices']) for data in all_invoice_data)
        total_payments = sum(len(data['scheduled_payments']) for data in all_invoice_data)
        print(f"📄 Total REAL Invoices Found: {total_invoices}")
        print(f"💳 Total Scheduled Payments: {total_payments}")
        
        # Show agreements with REAL past due amounts
        past_due_agreements = [data for data in all_invoice_data if data['past_due_amount'] > 0]
        if past_due_agreements:
            print(f"\n⚠️ Agreements with REAL Past Due Amounts:")
            for data in past_due_agreements:
                print(f"  - Agreement {data['agreement_id']}: ${data['past_due_amount']:.2f}")
        
        print(f"\n🎉 V2 ENDPOINT IS WORKING WITH COOKIE INJECTION!")
        print(f"✅ We have REAL invoice data with actual past due amounts!")
        return True
    else:
        print(f"❌ V2 endpoint still failing - cookie injection didn't work")
        print(f"❌ Need to debug the cookie setup further")
        return False

if __name__ == "__main__":
    print("🧪 Starting V2 Training Invoice Flow Test with Cookie Fix")
    
    # Test the V2 endpoint with proper cookie injection
    success = test_v2_invoice_endpoint_with_cookies()
    
    if success:
        print(f"\n🎉 V2 ENDPOINT COOKIE FIX WORKED!")
        print(f"✅ We have REAL invoice data from V2!")
        print(f"✅ Ready to integrate into dashboard with ACCURATE past due amounts!")
    else:
        print(f"\n❌ V2 ENDPOINT STILL FAILING - Need to fix cookie injection!"))