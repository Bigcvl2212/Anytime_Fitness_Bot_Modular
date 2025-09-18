#!/usr/bin/env python3
"""
Test Campaign Validation with Enhanced Logging
Test the exact messaging route logic with detailed step-by-step logging
"""

import requests
import json
import time

def test_campaign_with_logging():
    """Test campaign sending with enhanced logging to trace validation failure"""
    
    print("🔍 TESTING CAMPAIGN WITH ENHANCED LOGGING")
    print("=" * 60)
    
    # Test campaign payload
    test_campaign = {
        'category': 'past-due-6-30',
        'name': 'Test Campaign - Debug', 
        'message': 'Test message for debugging validation.',
        'type': 'sms',
        'recipientLimit': 1,  # Just 1 member to test validation
        'notes': 'Debug test campaign'
    }
    
    print("📤 Sending test campaign request...")
    print(f"Payload: {json.dumps(test_campaign, indent=2)}")
    
    try:
        response = requests.post(
            'http://localhost:5000/api/campaigns/send', 
            json=test_campaign, 
            timeout=30
        )
        
        print(f"\n📥 Response received:")
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Content: {response.text}")
        
        if response.headers.get('content-type', '').startswith('application/json'):
            try:
                response_json = response.json()
                print(f"\nParsed JSON Response:")
                print(json.dumps(response_json, indent=2))
            except Exception as e:
                print(f"Failed to parse JSON: {e}")
        
    except requests.exceptions.Timeout:
        print("❌ Request timed out after 30 seconds")
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - is the Flask server running?")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    test_campaign_with_logging()