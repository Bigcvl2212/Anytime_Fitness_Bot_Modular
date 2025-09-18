#!/usr/bin/env python3

import requests
import json

def test_single_category():
    """Test the 'past-due-30' category specifically to ensure the mapping fix works"""
    
    base_url = "http://localhost:5000"
    
    # Test with proper message text that meets validation requirements
    campaign_data = {
        "name": "Test past-due-30 Category Fix",
        "message": "This is your final warning. Your account has an unpaid balance. To prevent your account from being flagged as uncontactable and sent to collections, please pay the outstanding amount by this Friday. For assistance, contact Anytime Fitness in Fond du Lac at 920-921-4800.",
        "message_type": "sms", 
        "subject": "",
        "categories": ["past-due-30"],  # This was failing before the fix
        "notes": "Testing past-due-30 category mapping fix"
    }
    
    headers = {"Content-Type": "application/json"}
    
    try:
        print("🧪 Testing 'past-due-30' category with full message...")
        response = requests.post(f"{base_url}/api/campaigns/send", json=campaign_data, headers=headers)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 'past-due-30' category mapping fix works!")
            if 'results' in data:
                results = data['results']
                print(f"📋 Found {results.get('total', 0)} members")
                print(f"📧 Sent to {results.get('successful', 0)} members")
                if results.get('failed', 0) > 0:
                    print(f"❌ Failed: {results.get('failed', 0)}")
            print(f"📋 Full Response: {json.dumps(data, indent=2)}")
        else:
            try:
                error_data = response.json()
                print(f"❌ Category 'past-due-30' failed: {error_data.get('error', 'Unknown error')}")
                print(f"📋 Error Response: {json.dumps(error_data, indent=2)}")
            except:
                print(f"❌ Raw response: {response.text}")
                
    except Exception as e:
        print(f"❌ Network error: {e}")

if __name__ == "__main__":
    test_single_category()