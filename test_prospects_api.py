#!/usr/bin/env python3
"""
Test script to check the prospects API
"""

import requests
import json

def test_prospects_api():
    """Test the prospects API endpoint"""
    try:
        print("🔍 Testing prospects API...")
        response = requests.get("http://localhost:5000/api/prospects/all", timeout=30)
        
        print(f"📥 Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success: {data.get('success')}")
            print(f"📊 Total prospects: {data.get('total_prospects')}")
            print(f"📈 Source: {data.get('source')}")
            
            if data.get('total_prospects', 0) > 100:
                print(f"🎉 Great! We have {data.get('total_prospects')} prospects - this looks like the full dataset!")
            elif data.get('total_prospects', 0) < 100:
                print(f"⚠️ Only {data.get('total_prospects')} prospects - this might be cached data, not the full 9000+")
                
            # Check if we have error details
            if 'error' in data:
                print(f"❌ Error in response: {data['error']}")
                
        else:
            print(f"❌ Request failed: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            
    except Exception as e:
        print(f"❌ Error testing API: {e}")

if __name__ == "__main__":
    test_prospects_api()
