#!/usr/bin/env python3
import requests

# Test the category counts API
try:
    print("Testing category counts API...")
    response = requests.get('http://localhost:5000/api/members/category-counts')
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Success: {data.get('success')}")
        print(f"Counts: {data.get('counts')}")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Connection error: {e}")

# Test individual category endpoints
categories = ['green', 'comp', 'ppv', 'staff', 'past_due', 'inactive']

for category in categories:
    try:
        print(f"\nTesting {category} members API...")
        response = requests.get(f'http://localhost:5000/api/members/by-category/{category}')
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Success: {data.get('success')}")
            print(f"Count: {data.get('count')}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Connection error: {e}")
