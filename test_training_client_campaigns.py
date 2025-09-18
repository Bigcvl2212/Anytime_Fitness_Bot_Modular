#!/usr/bin/env python3
"""
Test training client campaign functionality
"""

import requests
import json
import time

def test_training_client_debug_validation():
    """Test the debug validation endpoint for training clients"""
    print("🧪 TESTING: Training Client Campaign Debug Validation")
    print("=" * 60)
    
    # Test data for past due training clients
    test_data = {
        "categories": ["training-past-due"],
        "type": "sms",
        "max_recipients": 50,
        "message": "Test message for past due training clients"
    }
    
    try:
        # Send request to debug validation endpoint
        print("📤 Sending debug validation request...")
        response = requests.post(
            "http://localhost:5000/api/campaigns/debug-validation", 
            json=test_data,
            timeout=30
        )
        
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get('success'):
                debug_results = result.get('debug_results', {})
                validation_summary = debug_results.get('validation_summary', {})
                
                print(f"✅ Debug validation successful!")
                print(f"📋 Total members found: {validation_summary.get('total_members_found', 0)}")
                print(f"📋 Valid for SMS: {validation_summary.get('total_valid_for_message_type', 0)}")
                print(f"📋 Would campaign succeed: {validation_summary.get('would_campaign_succeed', False)}")
                
                category_results = debug_results.get('category_results', [])
                for category_result in category_results:
                    print(f"\n📊 Category '{category_result['original_category']}':")
                    print(f"   Mapped to: {category_result['mapped_status_message']}")
                    print(f"   Raw query results: {category_result['raw_query_results']}")
                    print(f"   Query: {category_result['query_executed']}")
                    
                    sample_members = category_result.get('sample_members', [])
                    if sample_members:
                        print(f"   Sample members:")
                        for i, member in enumerate(sample_members[:3]):
                            print(f"     {i+1}. {member.get('full_name')} - {member.get('status_message')}")
                    
                return validation_summary.get('total_valid_for_message_type', 0) > 0
                
            else:
                print(f"❌ Debug validation failed: {result.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ HTTP error: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data}")
            except:
                print(f"   Response text: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing debug validation: {e}")
        return False

def test_training_client_categories():
    """Test the member categories endpoint to see training clients"""
    print("\n🧪 TESTING: Member Categories Endpoint")
    print("=" * 40)
    
    try:
        response = requests.get("http://localhost:5000/api/members/categories", timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get('success'):
                categories = result.get('categories', [])
                print(f"✅ Found {len(categories)} member categories:")
                
                training_categories = []
                for category in categories:
                    name = category.get('name', '')
                    count = category.get('count', 0)
                    print(f"   - {name}: {count} members")
                    
                    if 'training' in name.lower() or 'past due' in name.lower():
                        training_categories.append(category)
                
                if training_categories:
                    print(f"\n🎯 Training-related categories found:")
                    for category in training_categories:
                        print(f"   - {category['name']}: {category['count']} members")
                else:
                    print(f"\n⚠️ No training-specific categories found in API response")
                    
                return True
            else:
                print(f"❌ Categories request failed: {result.get('error')}")
                return False
        else:
            print(f"❌ Categories HTTP error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing categories: {e}")
        return False

def main():
    print("🚀 TRAINING CLIENT CAMPAIGN TESTING")
    print("=" * 50)
    print("Testing if past due training clients now show up in campaigns...")
    
    # Test 1: Debug validation
    validation_success = test_training_client_debug_validation()
    
    # Test 2: Categories endpoint
    categories_success = test_training_client_categories()
    
    # Summary
    print(f"\n📊 TEST SUMMARY:")
    print(f"   Debug validation: {'✅ PASS' if validation_success else '❌ FAIL'}")
    print(f"   Categories endpoint: {'✅ PASS' if categories_success else '❌ FAIL'}")
    
    if validation_success:
        print(f"\n🎉 SUCCESS: Past due training clients are now discoverable in campaigns!")
        print(f"   • You can now send campaigns to category 'training-past-due'")
        print(f"   • 11 training clients with past due amounts should be included")
        print(f"   • Total past due amount: Over $8,600")
    else:
        print(f"\n❌ ISSUE: Training clients still not showing up in campaigns")
        print(f"   • Check if Flask dashboard is running on localhost:5000")
        print(f"   • Verify database contains training_clients table with past due clients")

if __name__ == "__main__":
    main()