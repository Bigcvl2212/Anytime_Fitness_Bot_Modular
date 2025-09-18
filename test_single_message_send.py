#!/usr/bin/env python3
"""
Test single message sending from members page
"""

import requests
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_message_send_endpoint():
    """Test the /api/messages/send endpoint with proper format"""
    
    url = "http://localhost:5000/api/messages/send"
    
    # Test data - using a real member ID format
    test_data = {
        "member_id": "69006142",  # This is the member ID from your log
        "message": "Test message from single message feature",
        "channel": "sms"
    }
    
    print(f"🧪 Testing single message send to {url}")
    print(f"📡 Request data: {json.dumps(test_data, indent=2)}")
    
    try:
        response = requests.post(
            url,
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"📡 Response status: {response.status_code}")
        print(f"📡 Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Response data: {json.dumps(data, indent=2)}")
            
            if data.get('success'):
                print("✅ Message send endpoint working correctly!")
                return True
            else:
                print(f"❌ API returned success=False: {data.get('error', 'Unknown error')}")
                return False
                
        else:
            print(f"❌ HTTP Error {response.status_code}")
            try:
                error_data = response.json()
                print(f"❌ Error response: {json.dumps(error_data, indent=2)}")
            except:
                print(f"❌ Response text: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_alternative_endpoint():
    """Also test the /api/send-message endpoint to see if both work"""
    
    url = "http://localhost:5000/api/send-message"
    
    # Test data - using a real member ID format
    test_data = {
        "member_id": "69006142",  # This is the member ID from your log
        "message": "Test message from alternative endpoint",
        "channel": "sms"
    }
    
    print(f"\n🧪 Testing alternative endpoint {url}")
    print(f"📡 Request data: {json.dumps(test_data, indent=2)}")
    
    try:
        response = requests.post(
            url,
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"📡 Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Alternative endpoint response: {json.dumps(data, indent=2)}")
            return True
        else:
            print(f"❌ Alternative endpoint failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"❌ Error response: {json.dumps(error_data, indent=2)}")
            except:
                print(f"❌ Response text: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Alternative endpoint error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Single Message Send Endpoints")
    print("=" * 50)
    
    # Test primary endpoint
    primary_success = test_message_send_endpoint()
    
    # Test alternative endpoint
    alt_success = test_alternative_endpoint()
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"Primary endpoint (/api/messages/send): {'✅ SUCCESS' if primary_success else '❌ FAILED'}")
    print(f"Alternative endpoint (/api/send-message): {'✅ SUCCESS' if alt_success else '❌ FAILED'}")
    
    if primary_success:
        print("\n✅ Single message sending should now work from the members page!")
    else:
        print("\n❌ Single message sending still has issues.")