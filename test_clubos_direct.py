#!/usr/bin/env python3
# Test ClubOS API directly with Mark's GUID
try:
    from clubos_training_api_fixed import ClubOSTrainingPackageAPI
    
    print("Testing ClubOS API directly with Mark Benzinger's GUID: 66082049")
    
    api = ClubOSTrainingPackageAPI()
    
    print("1. Getting training payment details...")
    payment_details = api.get_member_training_payment_details('66082049')
    
    if payment_details:
        print(f"Payment details success: {payment_details.get('success')}")
        if payment_details.get('success'):
            agreement_ids = payment_details.get('agreement_ids', [])
            print(f"Found {len(agreement_ids)} agreement IDs: {agreement_ids}")
            
            if agreement_ids:
                print("\n2. Testing first agreement...")
                agreement_id = agreement_ids[0]
                
                print(f"Delegating to member 66082049...")
                api.delegate_to_member('66082049')
                
                print(f"Getting agreement {agreement_id} data...")
                url = f'https://anytime.club-os.com/api/agreements/package_agreements/V2/{agreement_id}'
                params = {'include': ['invoices', 'scheduledPayments', 'prohibitChangeTypes']}
                
                response = api.session.get(url, params=params)
                print(f"Response status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    agreement_data = data.get('data', {})
                    
                    print(f"Agreement status: {agreement_data.get('agreementStatus')}")
                    print(f"Agreement name: {agreement_data.get('name')}")
                    
                    include_data = data.get('include', {})
                    invoices = include_data.get('invoices', [])
                    print(f"Found {len(invoices)} invoices")
                    
                    if invoices:
                        for i, invoice in enumerate(invoices):
                            print(f"  Invoice {i+1}: Status={invoice.get('invoiceStatus')}, Amount=${invoice.get('total', 0)}")
                else:
                    print(f"API Error: {response.text[:300]}")
            else:
                print("No agreement IDs found")
        else:
            print(f"Payment details error: {payment_details.get('error')}")
    else:
        print("Payment details returned None")
        
except Exception as e:
    print(f"Exception: {e}")
    import traceback
    traceback.print_exc()
