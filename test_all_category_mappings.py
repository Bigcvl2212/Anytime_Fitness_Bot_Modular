#!/usr/bin/env python3

import requests
import json

def test_all_category_mappings():
    """Test all category mappings to ensure they work properly"""
    
    base_url = "http://localhost:5000"
    
    # Test categories that should now work with the expanded mappings
    test_categories = [
        "past-due-30",                    # Fixed - should work
        "past-due-6-30",                  # Should work
        "good-standing",                  # Should work  
        "green",                          # Fixed - should work
        "staff-member",                   # Fixed - should work (lowercase variant)
        "member-will-expire-within-30-days",  # Fixed - should work
        "expiring-soon",                  # Fixed - should work (alternative name)
        "invalid-bad-address-information", # Fixed - should work
        "address-issues"                   # Fixed - should work (alternative name)
    ]
    
    # Standard message for testing
    test_message = "This is a test message to verify that all category mappings are working correctly. This message meets the minimum length requirements for campaign validation."
    
    success_count = 0
    total_members_found = 0
    
    print("🧪 Testing All Category Mappings")
    print("=" * 50)
    
    for category in test_categories:
        print(f"\n🔍 Testing category: '{category}'")
        
        campaign_data = {
            "name": f"Test {category}",
            "message": test_message,
            "message_type": "sms",
            "subject": "",
            "categories": [category],
            "notes": f"Testing {category} mapping"
        }
        
        headers = {"Content-Type": "application/json"}
        
        try:
            response = requests.post(f"{base_url}/api/campaigns/send", json=campaign_data, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if 'campaign_results' in data:
                    results = data['campaign_results']
                    total_found = results.get('total', 0)
                    successful = results.get('successful', 0)
                    total_members_found += total_found
                    
                    print(f"  ✅ WORKS! Found {total_found} members, sent to {successful}")
                    success_count += 1
                else:
                    print(f"  ⚠️ Success but no campaign_results: {data}")
                    success_count += 1
            else:
                try:
                    error_data = response.json()
                    print(f"  ❌ FAILED: {error_data.get('error', 'Unknown error')}")
                except:
                    print(f"  ❌ FAILED: HTTP {response.status_code} - {response.text}")
                    
        except requests.exceptions.Timeout:
            print(f"  ⏰ TIMEOUT (but mapping likely works - messages may be sending)")
        except Exception as e:
            print(f"  ❌ ERROR: {e}")
    
    print("\n" + "=" * 50)
    print("📊 SUMMARY:")
    print(f"  ✅ Categories working: {success_count}/{len(test_categories)}")
    print(f"  👥 Total members found: {total_members_found}")
    print(f"  🎯 Success rate: {(success_count/len(test_categories)*100):.1f}%")
    
    if success_count == len(test_categories):
        print("🎉 ALL CATEGORY MAPPINGS ARE WORKING!")
    else:
        print(f"⚠️ {len(test_categories) - success_count} categories still need fixes")

if __name__ == "__main__":
    test_all_category_mappings()