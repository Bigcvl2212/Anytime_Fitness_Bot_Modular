#!/usr/bin/env python3
"""
Direct test with Mark Benzinger's GUID (66082049) to see what ClubOS returns
"""
import sys
sys.path.append('.')

from clubos_training_api_fixed import ClubOSTrainingPackageAPI

def test_mark_direct():
    print("🧪 Testing Mark Benzinger with GUID 66082049")
    
    try:
        api = ClubOSTrainingPackageAPI()
        
        # Step 1: Get payment details using his GUID
        print("📋 Step 1: Getting payment details...")
        payment_details = api.get_member_training_payment_details("66082049")
        
        print(f"📊 Payment details result: {payment_details}")
        
        if payment_details and payment_details.get('success'):
            agreement_ids = payment_details.get('agreement_ids', [])
            print(f"✅ Found {len(agreement_ids)} agreement IDs: {agreement_ids}")
            
            if agreement_ids:
                # Step 2: Test with first agreement
                first_agreement = agreement_ids[0]
                print(f"\n📋 Step 2: Testing agreement {first_agreement}")
                
                # Delegate to member using GUID
                print("👤 Delegating to member...")
                api.delegate_to_member("66082049")
                
                # Make V2 API call
                url = f'https://anytime.club-os.com/api/agreements/package_agreements/V2/{first_agreement}'
                params = {'include': ['invoices', 'scheduledPayments', 'prohibitChangeTypes']}
                
                print(f"🌐 API URL: {url}")
                response = api.session.get(url, params=params)
                
                print(f"📊 Response status: {response.status_code}")
                print(f"📊 Response time: {response.elapsed.total_seconds():.2f}s")
                
                if response.status_code == 200:
                    data = response.json()
                    agreement_data = data.get('data', {})
                    
                    print(f"📋 Agreement Name: {agreement_data.get('name')}")
                    print(f"📋 Agreement Status: {agreement_data.get('agreementStatus')}")
                    
                    # Check invoice data
                    include_data = data.get('include', {})
                    invoices = include_data.get('invoices', [])
                    print(f"🧾 Found {len(invoices)} invoices")
                    
                    for i, invoice in enumerate(invoices):
                        status = invoice.get('invoiceStatus')
                        total = invoice.get('total', 0)
                        print(f"   Invoice {i+1}: Status {status}, Total ${total}")
                        
                else:
                    print(f"❌ API Error: {response.status_code}")
                    print(f"❌ Response: {response.text[:500]}")
            else:
                print("❌ No agreement IDs found")
        else:
            print("❌ Payment details failed or empty")
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_mark_direct()
