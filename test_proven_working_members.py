#!/usr/bin/env python3
import requests
import time

print('Testing with WORKING member: Grace Sphatt (185777276)')
start = time.time()
response = requests.get('http://localhost:5000/api/training-clients/185777276/packages', timeout=30)
end = time.time()

print(f'Response time: {end-start:.2f} seconds')
print(f'Status: {response.status_code}')

if response.status_code == 200:
    data = response.json()
    print(f'Success: {data.get("success")}')
    if data.get('success'):
        print(f'Active packages: {data.get("active_packages")}')
        print(f'Past due: ${data.get("past_due_amount", 0):.2f}')
        print(f'Status: {data.get("payment_status")}')
    else:
        print(f'Error: {data.get("error")}')
else:
    print(f'HTTP Error: {response.text[:300]}')

print('')
print('Testing with WORKING member: Javae Dixon (185182950)')
start = time.time()
response = requests.get('http://localhost:5000/api/training-clients/185182950/packages', timeout=30)
end = time.time()

print(f'Response time: {end-start:.2f} seconds')
print(f'Status: {response.status_code}')

if response.status_code == 200:
    data = response.json()
    print(f'Success: {data.get("success")}')
    if data.get('success'):
        print(f'Active packages: {data.get("active_packages")}')
        print(f'Past due: ${data.get("past_due_amount", 0):.2f}')
        print(f'Status: {data.get("payment_status")}')
    else:
        print(f'Error: {data.get("error")}')
else:
    print(f'HTTP Error: {response.text[:300]}')
