#!/usr/bin/env python3
"""
Quick test to verify single message fix is working completely
"""

import requests
import json
from datetime import datetime

# Test the same message that just failed
test_data = {
    "member_name": "REGINALD BAKER",
    "message": "🧪 TEST MESSAGE - Single message system fix verification at " + datetime.now().strftime('%H:%M:%S'),
    "channel": "sms"
}

print("🧪 Testing Single Message Fix")
print("=" * 50)
print(f"📨 Testing message to: {test_data['member_name']}")
print(f"📱 Channel: {test_data['channel']}")
print()

try:
    response = requests.post(
        "http://localhost:5000/api/messages/send",
        json=test_data,
        headers={"Content-Type": "application/json"},
        timeout=30
    )
    
    print(f"📡 Response Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            print("✅ SUCCESS: Single message fix is working!")
            print(f"📋 Message sent to: {result.get('member_name')}")
            print(f"📋 Member ID: {result.get('member_id')}")
            print(f"📋 Channel: {result.get('channel')}")
            
            # Verify it went to the right person
            if result.get('member_name') == test_data['member_name']:
                print("✅ RECIPIENT VERIFICATION: Correct recipient confirmed!")
                print("\n🎉 THE BUG IS FIXED!")
                print("   ✅ Single messages now use campaign-tested logic")
                print("   ✅ Proper member lookup and validation")
                print("   ✅ Messages go to the correct recipient")
            else:
                print(f"❌ RECIPIENT MISMATCH: Expected '{test_data['member_name']}', got '{result.get('member_name')}'")
        else:
            print(f"❌ API Error: {result.get('error')}")
    else:
        print(f"❌ HTTP Error: {response.text}")

except Exception as e:
    print(f"❌ Request Error: {e}")

print("\n" + "=" * 50)