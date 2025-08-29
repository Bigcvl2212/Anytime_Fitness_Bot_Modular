#!/usr/bin/env python3
"""
Direct test of get_member_training_payment_details with Mark's ClubOS ID (125814462)
"""
import sys
sys.path.append('.')

from clubos_training_api_fixed import ClubOSTrainingPackageAPI

def test_mark_direct_payment_details():
    print("🧪 Testing Mark Benzinger payment details with ClubOS ID 125814462")
    
    try:
        api = ClubOSTrainingPackageAPI()
        
        # Direct call to get_member_training_payment_details
        print("📋 Calling get_member_training_payment_details('125814462')...")
        payment_details = api.get_member_training_payment_details("125814462")
        
        print(f"📊 Raw payment details response: {payment_details}")
        
        if payment_details and payment_details.get('success'):
            agreement_ids = payment_details.get('agreement_ids', [])
            print(f"✅ SUCCESS! Found {len(agreement_ids)} agreement IDs: {agreement_ids}")
            
            # Let's test each agreement ID
            for i, agreement_id in enumerate(agreement_ids):
                print(f"\n🔍 Testing agreement {i+1}/{len(agreement_ids)}: {agreement_id}")
                
                # Delegate first
                api.delegate_to_member("125814462")
                
                # Try the V2 API call
                url = f'https://anytime.club-os.com/api/agreements/package_agreements/V2/{agreement_id}'
                params = {'include': ['invoices', 'scheduledPayments', 'prohibitChangeTypes']}
                
                response = api.session.get(url, params=params)
                print(f"📊 Response status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    agreement_data = data.get('data', {})
                    
                    print(f"📋 Agreement Name: {agreement_data.get('name')}")
                    print(f"📋 Agreement Status: {agreement_data.get('agreementStatus')}")
                    
                    include_data = data.get('include', {})
                    invoices = include_data.get('invoices', [])
                    print(f"🧾 Found {len(invoices)} invoices")
                    
                    if invoices:
                        for j, invoice in enumerate(invoices):
                            status = invoice.get('invoiceStatus')
                            total = invoice.get('total', 0)
                            print(f"   Invoice {j+1}: Status {status}, Total ${total}")
                    
                    if agreement_data.get('agreementStatus') == 2:  # Active
                        print("🎉 FOUND ACTIVE AGREEMENT!")
                        
                else:
                    print(f"❌ API call failed: {response.status_code} - {response.text[:200]}")
        else:
            print(f"❌ Payment details failed: {payment_details}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_mark_direct_payment_details()
