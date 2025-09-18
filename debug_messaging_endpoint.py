#!/usr/bin/env python3
"""
Debug the messaging endpoint to see what data is being received
"""

import requests
import json

def test_messaging_endpoint():
    """Test what the messaging endpoint is receiving"""
    
    url = "http://localhost:5000/api/messages/send"
    
    # Test with the same data format the frontend sends
    test_data = {
        "member_id": "69006142",  # The member ID from your log
        "message": "Test message from debug script",
        "channel": "sms"
    }
    
    print(f"🧪 Testing messaging endpoint: {url}")
    print(f"📡 Sending data: {json.dumps(test_data, indent=2)}")
    
    try:
        response = requests.post(
            url,
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"📡 Response status: {response.status_code}")
        print(f"📡 Response headers: {dict(response.headers)}")
        
        try:
            response_data = response.json()
            print(f"📡 Response data: {json.dumps(response_data, indent=2)}")
        except:
            print(f"📡 Response text: {response.text}")
            
        return response.status_code == 200
            
    except Exception as e:
        print(f"❌ Error testing endpoint: {e}")
        return False

def test_with_empty_data():
    """Test with empty/null data to reproduce the error"""
    
    url = "http://localhost:5000/api/messages/send"
    
    test_cases = [
        {"member_id": None, "message": "test", "channel": "sms"},
        {"member_id": "", "message": "test", "channel": "sms"}, 
        {"member_id": "69006142", "message": None, "channel": "sms"},
        {"member_id": "69006142", "message": "", "channel": "sms"},
        {"channel": "sms"},  # Missing both
        {}  # Empty data
    ]
    
    for i, test_data in enumerate(test_cases):
        print(f"\n🧪 Test case {i+1}: {json.dumps(test_data)}")
        
        try:
            response = requests.post(
                url,
                json=test_data,
                headers={'Content-Type': 'application/json'},
                timeout=5
            )
            
            print(f"📡 Status: {response.status_code}")
            try:
                response_data = response.json()
                print(f"📡 Response: {response_data}")
            except:
                print(f"📡 Response text: {response.text}")
                
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🧪 Debugging Messaging Endpoint")
    print("=" * 50)
    
    # Test with valid data
    success = test_messaging_endpoint()
    
    # Test with invalid data to reproduce error
    print("\n" + "=" * 50)
    print("🧪 Testing with invalid data:")
    test_with_empty_data()
    
    if success:
        print("\n✅ Valid data test passed - issue might be with frontend data")
    else:
        print("\n❌ Valid data test failed - backend issue")