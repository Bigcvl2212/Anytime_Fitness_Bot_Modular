#!/usr/bin/env python3

import requests
import json

def test_campaign_categories():
    """Test both past due categories to ensure the mapping fix works"""
    
    base_url = "http://localhost:5000"
    
    # Test categories that were failing before
    test_categories = [
        "past-due-30",        # This was failing - should map to 'Past Due more than 30 days.'
        "past-due-6-30",      # This should work - maps to 'Past Due 6-30 days'
        "good-standing",      # This should work - maps to 'Member is in good standing'
        "green",              # This should work now - maps to 'Member is in good standing'
    ]
    
    for category in test_categories:
        print(f"\n🧪 Testing category: '{category}'")
        
        # Test campaign data
        campaign_data = {
            "name": f"Test {category} Category",
            "message_text": f"Test message for {category} category to verify category mapping fix.",
            "message_type": "sms", 
            "subject": "",
            "member_categories": [category],
            "notes": f"Testing {category} category mapping fix"
        }
        
        headers = {"Content-Type": "application/json"}
        
        try:
            response = requests.post(f"{base_url}/api/campaigns/send", json=campaign_data, headers=headers)
            
            print(f"📊 Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Category '{category}' works!")
                if 'results' in data:
                    results = data['results']
                    print(f"   📋 Found {results.get('total', 0)} members")
                    print(f"   📧 Sent to {results.get('successful', 0)} members")
                    if results.get('failed', 0) > 0:
                        print(f"   ❌ Failed: {results.get('failed', 0)}")
            else:
                try:
                    error_data = response.json()
                    print(f"❌ Category '{category}' failed: {error_data.get('error', 'Unknown error')}")
                except:
                    print(f"❌ Category '{category}' failed with raw response: {response.text}")
                    
        except Exception as e:
            print(f"❌ Network error testing '{category}': {e}")

if __name__ == "__main__":
    test_campaign_categories()