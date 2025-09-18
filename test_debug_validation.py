#!/usr/bin/env python3
"""
Test Debug Campaign Validation Endpoint
Test the new debug endpoint to trace exactly what's happening
"""

import requests
import json

def test_debug_endpoint():
    """Test the new debug campaign validation endpoint"""
    
    print("🔍 TESTING DEBUG CAMPAIGN VALIDATION ENDPOINT")
    print("=" * 60)
    
    # Test payload - same as the failing campaign but for debug
    test_payload = {
        'category': 'past-due-6-30',
        'type': 'sms',
        'max_recipients': 100
    }
    
    print(f"Debug payload: {json.dumps(test_payload, indent=2)}")
    
    try:
        response = requests.post(
            'http://localhost:5000/api/campaigns/debug-validation',
            json=test_payload,
            timeout=30
        )
        
        print(f"\nResponse Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            debug_results = result.get('debug_results', {})
            
            print("\n📊 DEBUG RESULTS:")
            print("=" * 40)
            
            print(f"Input Categories: {debug_results.get('input_categories')}")
            print(f"Message Type: {debug_results.get('message_type')}")
            print(f"Max Recipients: {debug_results.get('max_recipients')}")
            
            print(f"\n📋 CATEGORY PROCESSING:")
            for category_result in debug_results.get('category_results', []):
                print(f"\nCategory: '{category_result.get('original_category')}'")
                print(f"  Mapped to: '{category_result.get('mapped_status_message')}'")
                print(f"  Query Results: {category_result.get('raw_query_results')} members")
                
                if category_result.get('query_error'):
                    print(f"  ❌ Query Error: {category_result.get('query_error')}")
                
                validation = category_result.get('validation_results', {})
                print(f"  Valid Emails: {validation.get('valid_email_count', 0)}")
                print(f"  Valid Phones: {validation.get('valid_phone_count', 0)}")
                print(f"  Valid Both: {validation.get('valid_both_count', 0)}")
                print(f"  Would Pass: {category_result.get('would_pass_validation', False)}")
                
                if validation.get('validation_errors'):
                    print(f"  Validation Errors: {validation.get('validation_errors')}")
                
                print(f"  Sample Members:")
                for sample in category_result.get('sample_members', []):
                    print(f"    - {sample.get('full_name')} | {sample.get('email')} | {sample.get('mobile_phone')}")
            
            print(f"\n🎯 FINAL SUMMARY:")
            summary = debug_results.get('validation_summary', {})
            print(f"  Total Members Found: {summary.get('total_members_found')}")
            print(f"  Valid for Message Type: {summary.get('total_valid_for_message_type')}")
            print(f"  Campaign Would Succeed: {summary.get('would_campaign_succeed')}")
            
            if summary.get('failure_reason'):
                print(f"  ❌ Failure Reason: {summary.get('failure_reason')}")
            else:
                print(f"  ✅ Validation would succeed!")
        
        else:
            print(f"❌ Error Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    test_debug_endpoint()