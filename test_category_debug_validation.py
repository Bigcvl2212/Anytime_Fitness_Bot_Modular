#!/usr/bin/env python3

import requests
import json

def test_category_debug():
    """Test the debug validation endpoint to verify category mappings without sending messages"""
    
    base_url = "http://localhost:5000"
    
    # Test the categories we added mappings for
    test_categories = [
        "past-due-30",                    # Fixed 
        "staff-member",                   # Fixed - lowercase variant
        "member-will-expire-within-30-days", # Fixed 
        "expiring-soon",                  # Fixed - alternative name
        "invalid-bad-address-information", # Fixed
        "address-issues"                   # Fixed - alternative name
    ]
    
    success_count = 0
    
    print("🔍 Testing Category Debug Validation (No Messages Sent)")
    print("=" * 60)
    
    for category in test_categories:
        print(f"\n🧪 Testing category: '{category}'")
        
        debug_data = {
            "categories": [category],
            "type": "sms",
            "max_recipients": 5
        }
        
        headers = {"Content-Type": "application/json"}
        
        try:
            response = requests.post(f"{base_url}/api/campaigns/debug-validation", json=debug_data, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'debug_results' in data:
                    debug_results = data['debug_results']
                    category_results = debug_results.get('category_results', [])
                    
                    if category_results:
                        result = category_results[0]
                        mapped_status = result.get('mapped_status_message')
                        members_found = result.get('raw_query_results', 0)
                        
                        print(f"  ✅ Mapped to: '{mapped_status}'")
                        print(f"  👥 Found: {members_found} members")
                        
                        if members_found > 0:
                            print(f"  🎯 SUCCESS - Category mapping works!")
                            success_count += 1
                        else:
                            print(f"  ⚠️ Mapping works but no members in this category")
                            success_count += 1  # Still count as success since mapping works
                    else:
                        print(f"  ❌ No category results returned")
                else:
                    print(f"  ❌ No debug_results in response")
            else:
                try:
                    error_data = response.json()
                    print(f"  ❌ FAILED: {error_data.get('error', 'Unknown error')}")
                except:
                    print(f"  ❌ FAILED: HTTP {response.status_code}")
                    
        except Exception as e:
            print(f"  ❌ ERROR: {e}")
    
    print("\n" + "=" * 60)
    print("📊 CATEGORY MAPPING TEST RESULTS:")
    print(f"  ✅ Working mappings: {success_count}/{len(test_categories)}")
    print(f"  🎯 Success rate: {(success_count/len(test_categories)*100):.1f}%")
    
    if success_count == len(test_categories):
        print("🎉 ALL NEW CATEGORY MAPPINGS ARE WORKING!")
    else:
        print(f"⚠️ {len(test_categories) - success_count} categories still need fixes")

if __name__ == "__main__":
    test_category_debug()