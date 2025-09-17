#!/usr/bin/env python3
"""
Test the proven working ClubOS messaging approach
Uses our working authentication with the exact form submission from documentation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.clubos_messaging_client import ClubOSMessagingClient
from src.config.secrets_local import get_secret

def test_proven_approach():
    """Test using our working authentication with proven form submission"""
    
    print("🚀 TESTING PROVEN CLUBOS MESSAGING APPROACH")
    print("=" * 60)
    print("Using working authentication + proven form submission")
    print()
    
    # Get credentials
    username = get_secret("clubos-username")
    password = get_secret("clubos-password")
    
    # Create client and authenticate (this works)
    client = ClubOSMessagingClient(username, password)
    if not client.authenticate():
        print("❌ Authentication failed")
        return False
    
    print("✅ Authentication successful")
    print()
    
    member_id = "187032782"
    
    # Test 1: SMS using proven form submission
    print("📱 TEST 1: SMS using proven form submission")
    print("-" * 40)
    
    sms_message = "🎉 PROVEN APPROACH TEST: This SMS uses the exact form submission from your documentation!"
    sms_success = client.send_sms_message(member_id, sms_message, "Proven approach test")
    
    if sms_success:
        print("✅ SMS sent successfully using proven approach!")
    else:
        print("❌ SMS failed")
    
    print()
    
    # Test 2: Email using proven form submission
    print("📧 TEST 2: Email using proven form submission")
    print("-" * 40)
    
    email_subject = "Proven Approach Test"
    email_message = "🎉 PROVEN APPROACH TEST: This email uses the exact form submission from your documentation! The API endpoints were failing but form submission to /action/FollowUp/save works!"
    email_success = client.send_email_message(member_id, email_subject, email_message, "Proven approach test")
    
    if email_success:
        print("✅ Email sent successfully using proven approach!")
    else:
        print("❌ Email failed")
    
    print()
    
    # Results
    print("📊 FINAL RESULTS:")
    print("=" * 30)
    print(f"SMS:   {'✅ SUCCESS' if sms_success else '❌ FAILED'}")
    print(f"Email: {'✅ SUCCESS' if email_success else '❌ FAILED'}")
    
    if sms_success and email_success:
        print("\n🎉 BOTH MESSAGES SENT SUCCESSFULLY!")
        print("✅ The proven approach is working!")
        print("✅ ClubOS messaging via form submission is functional")
    elif sms_success or email_success:
        print("\n⚠️ PARTIAL SUCCESS - One message type worked")
        print("✅ The proven approach is partially working")
    else:
        print("\n❌ BOTH MESSAGES FAILED")
        print("❌ Need to investigate further")
    
    return sms_success and email_success

if __name__ == "__main__":
    success = test_proven_approach()
    exit(0 if success else 1)






