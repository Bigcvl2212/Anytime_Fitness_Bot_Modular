#!/usr/bin/env python3
"""
Test script to check the messaging endpoints and dashboard functionality
"""
import requests
import json
from datetime import datetime

def test_dashboard_messaging():
    """Test the dashboard and messaging endpoints"""
    
    base_url = "http://localhost:5000"  # Assuming Flask is running on default port
    
    print("🧪 Testing Dashboard and Messaging System")
    print("=" * 50)
    
    # Test 1: Check if dashboard loads
    try:
        print("1. Testing dashboard endpoint...")
        response = requests.get(f"{base_url}/", timeout=5)
        print(f"   Dashboard status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Dashboard loads successfully")
        else:
            print(f"   ❌ Dashboard failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Dashboard error: {e}")
    
    # Test 2: Test recent messages API
    try:
        print("\n2. Testing recent messages endpoint...")
        response = requests.get(f"{base_url}/api/messaging/recent", timeout=10)
        print(f"   Recent messages status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Recent messages: {data.get('count', 0)} messages")
            if 'messages' in data and len(data['messages']) > 0:
                sample_message = data['messages'][0]
                print(f"   Sample message: {sample_message.get('from_user', 'Unknown')} - {sample_message.get('content', 'No content')[:50]}...")
        else:
            print(f"   ❌ Recent messages failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Recent messages error: {e}")
    
    # Test 3: Test member message history with a sample member ID
    test_member_ids = ["149169", "1234", "test_member"]  # Use known member IDs
    
    for member_id in test_member_ids:
        try:
            print(f"\n3. Testing member message history for ID: {member_id}...")
            response = requests.get(f"{base_url}/api/messaging/member-history/{member_id}", timeout=15)
            print(f"   Member history status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Member messages: {data.get('count', 0)} messages")
                print(f"   Source: {data.get('source', 'unknown')}")
                
                if 'note' in data:
                    print(f"   Note: {data['note']}")
                
                if 'message_history' in data and len(data['message_history']) > 0:
                    sample_message = data['message_history'][0]
                    print(f"   First message: {sample_message.get('from_user', 'Unknown')} - {sample_message.get('content', 'No content')[:60]}...")
                    
                    # Check for system messages
                    system_messages = [msg for msg in data['message_history'] if msg.get('message_type') == 'system']
                    if system_messages:
                        print(f"   System messages: {len(system_messages)}")
                        for sys_msg in system_messages[:2]:  # Show first 2 system messages
                            print(f"     • {sys_msg.get('content', 'No content')[:80]}...")
                            
            else:
                print(f"   ❌ Member history failed: {response.status_code}")
                
            # Only test the first member ID to avoid too many requests
            break
            
        except Exception as e:
            print(f"   ❌ Member history error: {e}")
    
    # Test 4: Check messaging dashboard endpoint
    try:
        print(f"\n4. Testing messaging dashboard endpoint...")
        response = requests.get(f"{base_url}/messaging", timeout=10)
        print(f"   Messaging dashboard status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Messaging dashboard loads successfully")
        else:
            print(f"   ❌ Messaging dashboard failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Messaging dashboard error: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Dashboard and messaging tests completed")
    print(f"⏰ Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    test_dashboard_messaging()
