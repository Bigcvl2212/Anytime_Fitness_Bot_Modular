#!/usr/bin/env python3
"""
Test Member Lookup and ClubOS Messaging
"""

import requests
import json

def test_member_lookup():
    """Test member lookup for Jeremy Mayo"""
    
    print("🔍 Testing Member Lookup for Jeremy Mayo")
    print("-" * 50)
    
    # Test data
    test_data = {
        "member_name": "Jeremy Mayo",
        "message": "Test message from gym bot API - testing notes functionality",
        "message_type": "sms",
        "notes": "Test message sent via API - Manager notes for tracking"
    }
    
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
            
            # Check if there are any additional details in the response
            if 'member_id' in data:
                print(f"👤 Member ID: {data.get('member_id')}")
            if 'clubos_response' in data:
                print(f"🔗 ClubOS Response: {data.get('clubos_response')}")
                
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
    test_member_lookup()
