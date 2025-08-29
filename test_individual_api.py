#!/usr/bin/env python3
import requests
import time

# Test the individual package endpoint
try:
    print('Testing individual package endpoint...')
    
    # First get all training clients to see what member IDs we have
    response = requests.get('http://localhost:5000/api/training-clients/all', timeout=10)
    if response.status_code == 200:
        data = response.json()
        if data.get('success') and data.get('training_clients'):
            clients = data['training_clients']
            print(f'Found {len(clients)} training clients')
            
            # Test the first client's package endpoint
            if clients:
                first_client = clients[0]
                member_id = first_client.get('member_id') or first_client.get('clubos_member_id')
                print(f'Testing member ID: {member_id} ({first_client.get("member_name")})')
                
                if member_id:
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
                    print('No member ID found for first client')
        else:
            print(f'Main API failed: {data.get("error")}')
    else:
        print(f'Main API HTTP error: {response.status_code} - {response.text[:300]}')

except Exception as e:
    print(f'Exception: {e}')

print('Test complete.')
