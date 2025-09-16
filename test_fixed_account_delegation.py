#!/usr/bin/env python3
"""
Test the FIXED ClubOS messaging with correct account delegation
The issue was using member_id for followUpUser.tfoUserId instead of staff account ID
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.clubos_messaging_client import ClubOSMessagingClient
from src.config.secrets_local import get_secret

def test_fixed_account_delegation():
    """Test messaging with correct account delegation"""
    
    print("🔧 TESTING FIXED ACCOUNT DELEGATION")
    print("=" * 50)
    print("FIXED: followUpUser.tfoUserId now uses staff account ID (187032782)")
    print("instead of member_id for proper message routing")
    print()
    
    # Get credentials
    username = get_secret("clubos-username")
    password = get_secret("clubos-password")
    
    # Create client and authenticate
    client = ClubOSMessagingClient(username, password)
    if not client.authenticate():
        print("❌ Authentication failed")
        return False
    
    print("✅ Authentication successful")
    print()
    
    member_id = "187032782"  # Jeremy Mayo's member ID
    
    # Test SMS with fixed account delegation
    print("📱 Testing SMS with FIXED account delegation...")
    sms_message = "🔧 ACCOUNT DELEGATION FIX TEST: This SMS should now be routed to your account correctly!"
    
    sms_success = client.send_sms_message(member_id, sms_message, "Fixed account delegation test")
    
    if sms_success:
        print("✅ SMS sent successfully with fixed account delegation")
    else:
        print("❌ SMS failed even with fixed account delegation")
    
    print()
    
    # Test Email with fixed account delegation
    print("📧 Testing Email with FIXED account delegation...")
    email_subject = "Fixed Account Delegation Test"
    email_message = "🔧 ACCOUNT DELEGATION FIX TEST: This email should now be routed to your account correctly! The followUpUser.tfoUserId field now uses the correct staff account ID instead of the member ID."
    
    email_success = client.send_email_message(member_id, email_subject, email_message, "Fixed account delegation test")
    
    if email_success:
        print("✅ Email sent successfully with fixed account delegation")
    else:
        print("❌ Email failed even with fixed account delegation")
    
    print()
    print("📊 RESULTS:")
    print("=" * 20)
    print(f"SMS:   {'✅ SUCCESS' if sms_success else '❌ FAILED'}")
    print(f"Email: {'✅ SUCCESS' if email_success else '❌ FAILED'}")
    
    if sms_success and email_success:
        print("\n🎉 ACCOUNT DELEGATION FIXED!")
        print("✅ Messages should now be routed to your account correctly!")
        print("📧 Check your phone and email for the messages!")
    elif sms_success or email_success:
        print("\n⚠️ PARTIAL SUCCESS - One message type worked")
        print("✅ Account delegation fix is partially working")
    else:
        print("\n❌ BOTH MESSAGES FAILED")
        print("❌ Account delegation fix didn't work")
    
    return sms_success and email_success

if __name__ == "__main__":
    success = test_fixed_account_delegation()
    exit(0 if success else 1)




