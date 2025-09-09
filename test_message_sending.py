#!/usr/bin/env python3
"""
Test Message Sending API
Tests the /api/messages/send endpoint
"""

import requests
import json

def test_send_message():
    """Test sending a message via the API"""
    
    # Test data
    test_data = {
        "member_name": "Jeremy Mayo",
        "message": "Test message from gym bot API - testing notes functionality",
        "message_type": "sms",
        "notes": "Test message sent via API - Manager notes for tracking"
    }
    
    print("🧪 Testing Message Sending API")
    print(f"📤 Sending message to: {test_data['member_name']}")
    print(f"📝 Message: {test_data['message']}")
    print(f"📱 Type: {test_data['message_type']}")
    print(f"📋 Notes: {test_data['notes']}")
    print("-" * 50)
    
    try:
        # Send POST request to the API
        response = requests.post(
            'http://localhost:5000/api/messages/send',
            headers={'Content-Type': 'application/json'},
            data=json.dumps(test_data),
            timeout=30
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success: {data.get('success')}")
            print(f"📨 Response: {data.get('message')}")
            print(f"📋 Type: {data.get('message_type')}")
        else:
            print(f"❌ Error Status: {response.status_code}")
            try:
                error_data = response.json()
                print(f"❌ Error: {error_data.get('error')}")
            except:
                print(f"❌ Error: {response.text}")
                
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the dashboard is running on localhost:5000")
    except requests.exceptions.Timeout:
        print("❌ Timeout: Request took too long")
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")

if __name__ == "__main__":
    test_send_message()
