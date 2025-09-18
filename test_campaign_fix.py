#!/usr/bin/env python3

import requests
import json

def test_campaign_send():
    """Test sending a campaign to ensure the database column issue is fixed"""
    
    url = "http://localhost:5000/api/campaigns/send"
    
    # Test campaign data
    campaign_data = {
        "name": "Database Fix Test",
        "message_text": "Test message to verify database column fix is working.",
        "message_type": "sms",
        "subject": "",
        "member_categories": ["past-due-6-30"],
        "notes": "Testing database column fix"
    }
    
    headers = {"Content-Type": "application/json"}
    
    try:
        print("🧪 Testing campaign send with fixed database column...")
        response = requests.post(url, json=campaign_data, headers=headers)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Campaign send successful!")
            print(f"📋 Response: {json.dumps(data, indent=2)}")
        else:
            print(f"❌ Campaign send failed")
            try:
                error_data = response.json()
                print(f"📋 Error Response: {json.dumps(error_data, indent=2)}")
            except:
                print(f"📋 Raw Response: {response.text}")
                
    except Exception as e:
        print(f"❌ Test failed with error: {e}")

if __name__ == "__main__":
    test_campaign_send()
