#!/usr/bin/env python3
"""
Test the fixed ClubOS Training API with yesterday's exact working code
"""

import sys
sys.path.append('src')

from clubos_training_api_fixed import ClubOSTrainingPackageAPI
import json
import time

def test_fixed_api():
    try:
        # Initialize the API client
        api = ClubOSTrainingPackageAPI()
        print('ClubOS Training API (fixed) initialized')
        
        # Set credentials manually (like in working code)
        api.username = 'j.mayo'
        api.password = 'j@SD4fjhANK5WNA'
        
        # Authenticate
        print('Authenticating...')
        auth_result = api.authenticate()
        print(f'Authentication result: {auth_result}')
        
        if api.authenticated:
            print('✅ Authentication successful')
            
            # Test with a known training client ID from database
            test_member_id = '191215290'  # Alexander Ovanin
            print(f'Testing package agreements for member ID: {test_member_id}')
            
            # FIRST: Test the fixed get_member_training_payment_details method
            print('\n--- Testing fixed get_member_training_payment_details ---')
            payment_details = api.get_member_training_payment_details(test_member_id)
            print(f'Payment details: {json.dumps(payment_details, indent=2)}')
            
            if payment_details.get('success') and payment_details.get('agreement_ids'):
                agreement_ids = payment_details['agreement_ids']
                print(f'✅ Found {len(agreement_ids)} agreement IDs: {agreement_ids}')
                
                # Now test the V2 endpoint that was working yesterday
                print('\n--- Testing V2 endpoint for first agreement ---')
                if agreement_ids:
                    first_agreement = agreement_ids[0]
                    api.delegate_to_member(test_member_id)  # Ensure delegation
                    
                    timestamp = int(time.time() * 1000)
                    detail_url = f'https://anytime.club-os.com/api/agreements/package_agreements/V2/{first_agreement}'
                    detail_params = {
                        'include': 'invoices,scheduledPayments,prohibitChangeTypes',
                        '_': timestamp
                    }
                    
                    response = api.session.get(detail_url, params=detail_params, timeout=15)
                    print(f'V2 Response status: {response.status_code}')
                    
                    if response.status_code == 200:
                        data = response.json()
                        agreement_data = data.get('data', {})
                        agreement_name = agreement_data.get('name', 'Unknown')
                        agreement_status = agreement_data.get('agreementStatus', 0)
                        print(f'✅ V2 SUCCESS: Agreement {first_agreement} "{agreement_name}" (status: {agreement_status})')
                        print(f'Response keys: {list(data.keys())}')
                        
                        # Show invoices if available
                        include_data = data.get('include', {})
                        invoices = include_data.get('invoices', [])
                        print(f'Invoices found: {len(invoices)}')
                        
                        return True
                    else:
                        print(f'❌ V2 FAILED: Status {response.status_code}, Response: {response.text}')
            else:
                print('❌ No agreement IDs found in payment details')
                
        else:
            print('❌ Authentication failed')
            
    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()
        
    return False

if __name__ == "__main__":
    success = test_fixed_api()
    print(f"\n=== Test Result: {'SUCCESS' if success else 'FAILED'} ===")
