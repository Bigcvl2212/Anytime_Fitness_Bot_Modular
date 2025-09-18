#!/usr/bin/env python3
"""Add debug logging to see which route is being hit"""

import requests

def test_with_debug():
    """Test with more verbose output to see what's happening"""
    
    url = "http://localhost:5000/api/campaigns/status/prospects"
    print(f"🔍 Testing URL: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response keys: {list(data.keys())}")
            print(f"Full response: {data}")
            
            # Check the exact structure
            if 'success' in data:
                print("✅ Has 'success' field")
            else:
                print("❌ Missing 'success' field")
                
            if 'campaign' in data:
                print("✅ Has 'campaign' field")  
            else:
                print("❌ Missing 'campaign' field")
                
            if 'status' in data:
                status_val = data['status']
                print(f"Status value: {status_val} (type: {type(status_val)})")
        else:
            print(f"Error response: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_with_debug()