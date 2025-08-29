#!/usr/bin/env python3
import requests
import time

print('Testing Grace Sphatt (known working member ID: 185777276)...')

try:
    start = time.time()
    response = requests.get('http://localhost:5000/api/training-clients/185777276/packages', timeout=30)
    end = time.time()
    
    print(f'Response time: {end-start:.2f} seconds')
    print(f'Status: {response.status_code}')
    
    if response.status_code == 200:
        data = response.json()
        print(f'Success: {data.get("success")}')
        print(f'Packages: {data.get("active_packages")}')
        print(f'Past due: ${data.get("past_due_amount", 0):.2f}')
        print(f'Payment status: {data.get("payment_status")}')
    else:
        print(f'Error: {response.text[:200]}')
        
except Exception as e:
    print(f'Exception: {e}')

print('Done.')
