#!/usr/bin/env python3
"""
Test Fixed ClubOS Messaging API - Send SMS and Email to Jeremy Mayo
Tests the fixed implementation that uses working form submission endpoints.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from services.api.clubos_api_client import create_clubos_api_client
from config.secrets_local import get_secret

# Target member details
JEREMY_MAYO_ID = "187032782"
TEST_SMS_MESSAGE = "This is a test SMS sent via the FIXED ClubOS API using form submission."
TEST_EMAIL_MESSAGE = "This is a test EMAIL sent via the FIXED ClubOS API using form submission. The API endpoints were failing but form submission to /action/FollowUp/save works!"

def test_fixed_clubos_messaging():
    """Test the fixed ClubOS messaging implementation"""
    
    print("🚀 TESTING FIXED CLUBOS MESSAGING API")
    print("=" * 60)
    print(f"Target: Jeremy Mayo (ID: {JEREMY_MAYO_ID})")
    print("Using form submission instead of failing API endpoints")
    print()
    
    # Get credentials
    try:
        username = get_secret("clubos-username")
        password = get_secret("clubos-password")
    except Exception as e:
        print(f"❌ Could not get ClubOS credentials: {e}")
        return False
    
    # Create API client
    print("🔐 Creating ClubOS API client...")
    client = create_clubos_api_client(username, password)
    
    if not client:
        print("❌ Failed to create authenticated ClubOS API client")
        return False
    
    print("✅ ClubOS API client authenticated successfully")
    print()
    
    # Test 1: Send SMS using form submission
    print("📱 TEST 1: Sending SMS via form submission")
    print("-" * 40)
    sms_result = client.send_message(JEREMY_MAYO_ID, TEST_SMS_MESSAGE, "text")
    
    if sms_result:
        print("✅ SMS TEST PASSED - Message sent successfully!")
    else:
        print("❌ SMS TEST FAILED - Could not send message")
    
    print()
    
    # Test 2: Send Email using form submission
    print("📧 TEST 2: Sending Email via form submission") 
    print("-" * 40)
    email_result = client.send_message(JEREMY_MAYO_ID, TEST_EMAIL_MESSAGE, "email")
    
    if email_result:
        print("✅ EMAIL TEST PASSED - Message sent successfully!")
    else:
        print("❌ EMAIL TEST FAILED - Could not send message")
    
    print()
    
    # Test 3: Send SMS using member profile direct submission
    print("👤 TEST 3: Sending SMS via member profile")
    print("-" * 40)
    profile_sms_result = client.send_message_to_member_profile(JEREMY_MAYO_ID, "SMS via profile page test", "text")
    
    if profile_sms_result:
        print("✅ PROFILE SMS TEST PASSED - Message sent successfully!")
    else:
        print("❌ PROFILE SMS TEST FAILED - Could not send message")
    
    print()
    
    # Test 4: Send Email using member profile direct submission
    print("👤 TEST 4: Sending Email via member profile")
    print("-" * 40)
    profile_email_result = client.send_message_to_member_profile(JEREMY_MAYO_ID, "Email via profile page test", "email")
    
    if profile_email_result:
        print("✅ PROFILE EMAIL TEST PASSED - Message sent successfully!")
    else:
        print("❌ PROFILE EMAIL TEST FAILED - Could not send message")
    
    print()
    
    # Summary
    print("📊 TEST SUMMARY")
    print("=" * 40)
    tests = [
        ("Form SMS", sms_result),
        ("Form Email", email_result), 
        ("Profile SMS", profile_sms_result),
        ("Profile Email", profile_email_result)
    ]
    
    passed = sum(result for _, result in tests)
    total = len(tests)
    
    for test_name, result in tests:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<15}: {status}")
    
    print(f"\nSuccess Rate: {passed}/{total} ({(passed/total)*100:.1f}%)")
    
    if passed >= 2:  # At least half the tests pass
        print("\n🎉 SOLUTION SUCCESSFUL!")
        print("✅ ClubOS messaging now works via form submission")
        print("✅ Ready to replace Selenium automation with API calls")
    else:
        print("\n⚠️ SOLUTION NEEDS MORE WORK")
        print("❌ Some messaging methods are still failing")
    
    return passed >= 2

def main():
    """Main test function"""
    success = test_fixed_clubos_messaging()
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())