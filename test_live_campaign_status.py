#!/usr/bin/env python3
"""Test campaign status directly to check if running campaigns show up properly"""

import requests
import json

def test_live_campaign_status():
    """Test campaign status for categories that might have active campaigns"""
    base_url = "http://localhost:5000"
    categories = ['prospects', 'members', 'training_clients', 'green', 'past_due']
    
    print("🔍 Testing Live Campaign Status...")
    print("=" * 50)
    
    for category in categories:
        url = f"{base_url}/api/campaigns/status/{category}"
        try:
            response = requests.get(url, timeout=10)
            print(f"\n📊 Testing {category}:")
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Response: {json.dumps(data, indent=2)}")
                
                # Check if this matches the expected frontend format
                if 'success' in data and 'campaign' in data:
                    print("✅ Correct frontend format!")
                else:
                    print("❌ Incorrect format - need to fix API endpoint")
                
            else:
                print(f"Error: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print(f"❌ Could not connect to {url}")
            print("Make sure Flask app is running!")
            return False
        except Exception as e:
            print(f"❌ Error testing {category}: {e}")
    
    print("\n" + "=" * 50)
    return True

if __name__ == "__main__":
    test_live_campaign_status()