#!/usr/bin/env python3
import requests
import time

# Test with Mark Benzinger who we know has training data
try:
    print('Testing with Mark Benzinger...')
    
    # Get all training clients and find Mark
    response = requests.get('http://localhost:5000/api/training-clients/all', timeout=10)
    if response.status_code == 200:
        data = response.json()
        if data.get('success') and data.get('training_clients'):
            clients = data['training_clients']
            
            # Find Mark Benzinger
            mark = None
            for client in clients:
                if 'Mark' in client.get('member_name', '') and 'Benzinger' in client.get('member_name', ''):
                    mark = client
                    break
            
            if mark:
                member_id = mark.get('member_id') or mark.get('clubos_member_id')
                print(f'Found Mark Benzinger - Member ID: {member_id}, Name: {mark.get("member_name")}')
                
                # Test his package endpoint
                print(f'Calling /api/training-clients/{member_id}/packages...')
                start = time.time()
                pkg_response = requests.get(f'http://localhost:5000/api/training-clients/{member_id}/packages', timeout=30)
                end = time.time()
                
                print(f'Package API response time: {end-start:.2f} seconds')
                print(f'Package API status: {pkg_response.status_code}')
                
                if pkg_response.status_code == 200:
                    pkg_data = pkg_response.json()
                    print(f'Package API success: {pkg_data.get("success")}')
                    if pkg_data.get('success'):
                        print(f'Active packages: {pkg_data.get("active_packages")}')
                        print(f'Past due amount: ${pkg_data.get("past_due_amount", 0):.2f}')
                        print(f'Payment status: {pkg_data.get("payment_status")}')
                    else:
                        print(f'Package API error: {pkg_data.get("error")}')
                else:
                    print(f'Package API HTTP error: {pkg_response.text[:300]}')
            else:
                print('Mark Benzinger not found in training clients')
                
                # Show first few clients
                print('\nFirst few training clients:')
                for i, client in enumerate(clients[:5]):
                    print(f'{i+1}. {client.get("member_name")} (ID: {client.get("member_id") or client.get("clubos_member_id")})')

except Exception as e:
    print(f'Exception: {e}')

print('Test complete.')
