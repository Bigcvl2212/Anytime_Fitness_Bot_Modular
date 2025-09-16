#!/usr/bin/env python3
"""
Test the Flask API endpoints directly to debug the cache/database issue
"""

import sys
sys.path.append('.')
import json
import requests
import time

def test_api_endpoints():
    """Test the actual API endpoints to see what they return"""
    
    base_url = "http://localhost:5000"  # Adjust if running on different port
    
    endpoints = [
        "/api/members/all",
        "/api/prospects/all", 
        "/api/training/clients"
    ]
    
    print("🔍 Testing Flask API endpoints...")
    
    for endpoint in endpoints:
        try:
            print(f"\n📡 Testing {endpoint}:")
            url = f"{base_url}{endpoint}"
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success'):
                    # Extract the actual data array
                    if 'members' in data:
                        count = len(data['members'])
                        source = data.get('source', 'unknown')
                        print(f"   ✅ Success: {count} members (source: {source})")
                        
                        if count > 0:
                            print(f"   Sample data: {data['members'][0].get('first_name', 'No name')} {data['members'][0].get('last_name', '')}")
                        
                    elif 'prospects' in data:
                        count = len(data.get('prospects', data.get('data', [])))
                        print(f"   ✅ Success: {count} prospects")
                        
                    elif 'training_clients' in data or 'clients' in data or 'data' in data:
                        clients = data.get('training_clients', data.get('clients', data.get('data', [])))
                        count = len(clients) if clients else 0
                        print(f"   ✅ Success: {count} training clients")
                        
                    else:
                        print(f"   ⚠️ Unexpected response format: {list(data.keys())}")
                else:
                    print(f"   ❌ API returned success=False: {data.get('error', 'Unknown error')}")
            else:
                print(f"   ❌ HTTP {response.status_code}: {response.text[:100]}...")
                
        except requests.exceptions.ConnectionError:
            print(f"   ⚠️ Connection failed - Flask server not running?")
            break
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n✅ API endpoint testing complete")

if __name__ == "__main__":
    test_api_endpoints()