#!/usr/bin/env python3
import requests
import time

try:
    print('Testing API endpoint...')
    start = time.time()
    response = requests.get('http://localhost:5000/api/training-clients/all', timeout=30)
    end = time.time()
    
    print(f'Response time: {end-start:.2f} seconds')
    print(f'Status: {response.status_code}')
    
    if response.status_code == 200:
        data = response.json()
        print(f'Success: {data.get("success")}')
        
        if data.get('success'):
            clients = data.get('training_clients', [])
            print(f'Found {len(clients)} training clients')
            if clients:
                first = clients[0]
                print(f'First client: {first.get("member_name")}')
                print(f'Packages: {first.get("active_packages")}')
                print(f'Payment status: {first.get("payment_status")}')
        else:
            print(f'API Error: {data.get("error")}')
    else:
        print(f'HTTP Error: {response.text[:500]}')
        
except Exception as e:
    print(f'Exception: {e}')
    
print('Test complete.')
