#!/usr/bin/env python3
"""
Test script to verify the single message fix works correctly.
This tests that messages go to the right person using the campaign-tested logic.
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
DASHBOARD_URL = "http://localhost:5000"
TEST_MESSAGE = f"🧪 TEST MESSAGE - Single message fix verification at {datetime.now().strftime('%H:%M:%S')}"

def test_single_message_fix():
    """Test that single messages now use the reliable campaign logic"""
    
    print("🧪 Testing Single Message Fix")
    print("=" * 50)
    
    # Test 1: Send message by member name (most common use case)
    test_member_name = "Kymberley Marr"  # The member from your original bug report
    
    print(f"\n📨 Test 1: Sending message to '{test_member_name}' by name...")
    
    payload = {
        "member_name": test_member_name,
        "message": TEST_MESSAGE,
        "channel": "sms"
    }
    
    try:
        response = requests.post(
            f"{DASHBOARD_URL}/api/messages/send",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📡 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"✅ SUCCESS: {result.get('message')}")
                print(f"📋 Member ID: {result.get('member_id')}")
                print(f"📋 Member Name: {result.get('member_name')}")
                print(f"📋 Channel: {result.get('channel')}")
                print(f"\n🎯 CRITICAL CHECK: Message was sent to '{result.get('member_name')}'")
                
                if result.get('member_name') == test_member_name:
                    print("✅ RECIPIENT VERIFICATION: Correct recipient!")
                else:
                    print(f"❌ RECIPIENT MISMATCH: Expected '{test_member_name}', got '{result.get('member_name')}'")
            else:
                print(f"❌ FAILED: {result.get('error')}")
        else:
            print(f"❌ HTTP ERROR: {response.text}")
            
    except Exception as e:
        print(f"❌ REQUEST FAILED: {e}")
    
    print("\n" + "=" * 50)
    print("🧪 Single Message Fix Test Complete")
    print("\nℹ️  If successful, the message should:")
    print("   1. Go to the correct recipient (Kymberley Marr)")
    print("   2. Use the same reliable logic as campaigns")
    print("   3. Show proper member validation in logs")
    print("\n📱 Check your phone/ClubOS to verify message delivery!")

if __name__ == "__main__":
    test_single_message_fix()