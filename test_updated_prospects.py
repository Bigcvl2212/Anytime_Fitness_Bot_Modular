#!/usr/bin/env python3
"""
Test the updated prospects API that uses the ClubHubAPIClient working approach
"""

import requests

def test_updated_prospects_api():
    """Test the updated prospects API"""
    print("🔄 Testing updated prospects API with ClubHubAPIClient approach...")
    
    try:
        response = requests.get('http://localhost:5000/api/prospects/all')
        print(f"Status: {response.status_code}")
        
        if response.ok:
            data = response.json()
            total_prospects = data.get('total_prospects', 'N/A')
            print(f"✅ Success! Total prospects: {total_prospects}")
            
            if total_prospects > 3000:
                print(f"🎉 EXCELLENT! Got {total_prospects} prospects - approaching the 9,000+ target!")
            elif total_prospects > 1000:
                print(f"👍 Good progress! Got {total_prospects} prospects")
            else:
                print(f"📊 Got {total_prospects} prospects")
        else:
            print(f"❌ Error: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_updated_prospects_api()
