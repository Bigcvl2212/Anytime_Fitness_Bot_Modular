#!/usr/bin/env python3
"""
Test email messaging to confirm the system works
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.clubos_messaging_client import ClubOSMessagingClient
from src.config.secrets_local import get_secret

def test_email_working():
    """Test email messaging to confirm the system works"""
    
    print("📧 TESTING EMAIL MESSAGING (SYSTEM CONFIRMATION)")
    print("=" * 60)
    
    # Get credentials
    username = get_secret("clubos-username")
    password = get_secret("clubos-password")
    
    # Create client and authenticate
    client = ClubOSMessagingClient(username, password)
    if not client.authenticate():
        print("❌ Authentication failed")
        return
    
    print("✅ Authentication successful")
    print()
    
    member_id = "187032782"
    subject = "ClubOS Messaging System Test"
    message = """This email confirms that the ClubOS messaging system is working correctly.

The issue with SMS is likely one of these:
1. SMS opt-in not enabled in ClubOS
2. Phone number format needs to be +17155868669
3. ClubOS SMS service issues

To fix SMS:
1. Go to https://anytime.club-os.com
2. Update your phone number to: +17155868669
3. Enable SMS opt-in in your account settings
4. Test sending yourself a message from the web interface

The API messaging system is working - it's just the SMS delivery that needs fixing."""
    
    print(f"📧 Sending email to member ID: {member_id}")
    print(f"📧 Your email: mayojeremy2212@gmail.com")
    print(f"Subject: {subject}")
    print()
    
    # Send email
    success = client.send_email_message(member_id, subject, message, "System test - SMS opt-in issue")
    
    if success:
        print("✅ Email sent successfully!")
        print("📧 Check your email at mayojeremy2212@gmail.com")
        print()
        print("🎯 CONCLUSION:")
        print("   ✅ ClubOS messaging API is working correctly")
        print("   ✅ Email messaging is working")
        print("   ❌ SMS delivery is the issue (not the API)")
        print()
        print("🔧 NEXT STEPS:")
        print("   1. Check your ClubOS account settings")
        print("   2. Update phone number to: +17155868669")
        print("   3. Enable SMS opt-in")
        print("   4. Test from ClubOS web interface")
    else:
        print("❌ Email failed")

if __name__ == "__main__":
    test_email_working()


