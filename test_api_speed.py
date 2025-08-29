#!/usr/bin/env python3
import requests
import time

print('Testing fast loading training clients API...')

start_time = time.time()
response = requests.get('http://localhost:5000/api/training-clients/all')
end_time = time.time()

print(f'Response time: {(end_time - start_time):.2f} seconds')
print(f'Status code: {response.status_code}')

if response.status_code == 200:
    data = response.json()
    if data.get('success'):
        print(f'Found {len(data.get("training_clients", []))} training clients')
        if data.get('training_clients'):
            first_client = data['training_clients'][0]
            print(f'First client: {first_client.get("member_name")}')
            print(f'Active packages: {first_client.get("active_packages")}')
            print(f'Payment status: {first_client.get("payment_status")}')
    else:
        print(f'API error: {data.get("error")}')
else:
    print(f'HTTP error: {response.status_code}')
    print(response.text[:200])
