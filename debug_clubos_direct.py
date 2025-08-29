#!/usr/bin/env python3
"""
Debug test to see exactly what ClubOS is returning
"""
import sys
import os
sys.path.append('.')
sys.path.append('./src')

# Import the ClubOS API directly
try:
    from clubos_training_api_fixed import ClubOSTrainingPackageAPI
    print("✅ ClubOS API imported successfully")
except ImportError as e:
    print(f"❌ Failed to import ClubOS API: {e}")
    exit(1)

def test_clubos_direct(member_id):
    """Test ClubOS API directly to see what we get"""
    print(f"\n🔍 Testing ClubOS API for member {member_id}")
    
    try:
        api = ClubOSTrainingPackageAPI()
        print("✅ ClubOS API initialized")
        
        # Step 1: Get payment details (this should return agreement IDs)
        print(f"📋 Getting payment details for member {member_id}...")
        payment_details = api.get_member_training_payment_details(str(member_id))
        
        print(f"📊 Payment details response: {payment_details}")
        
        if payment_details and payment_details.get('success'):
            agreement_ids = payment_details.get('agreement_ids', [])
            print(f"✅ Found {len(agreement_ids)} agreement IDs: {agreement_ids}")
            
            if agreement_ids:
                # Step 2: Test first agreement ID
                first_agreement = agreement_ids[0]
                print(f"\n🔍 Testing agreement {first_agreement}...")
                
                # Delegate to member
                print(f"👤 Delegating to member {member_id}...")
                api.delegate_to_member(str(member_id))
                
                # Make V2 API call
                url = f'https://anytime.club-os.com/api/agreements/package_agreements/V2/{first_agreement}'
                params = {'include': ['invoices', 'scheduledPayments', 'prohibitChangeTypes']}
                
                print(f"🌐 Making API call: {url}")
                print(f"📋 With params: {params}")
                
                response = api.session.get(url, params=params)
                print(f"📊 Response status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ Got response data!")
                    
                    # Print key parts of the response
                    agreement_data = data.get('data', {})
                    print(f"📋 Agreement status: {agreement_data.get('agreementStatus')}")
                    print(f"📋 Agreement name: {agreement_data.get('name')}")
                    
                    include_data = data.get('include', {})
                    invoices = include_data.get('invoices', [])
                    print(f"🧾 Found {len(invoices)} invoices")
                    
                    if invoices:
                        for i, invoice in enumerate(invoices):
                            status = invoice.get('invoiceStatus')
                            total = invoice.get('total', 0)
                            print(f"   Invoice {i+1}: Status {status}, Total ${total}")
                    
                else:
                    print(f"❌ API call failed: {response.status_code}")
                    print(f"❌ Error: {response.text[:500]}")
        else:
            print(f"❌ No payment details found or failed: {payment_details}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Test with known working member IDs from our chat history
    test_members = [
        "185777276",  # Grace Sphatt - proven working
        "185182950",  # Javae Dixon - proven working  
        "191215290",  # Alejandra Espinoza - current first client
    ]
    
    for member_id in test_members:
        test_clubos_direct(member_id)
        print("\n" + "="*50)
