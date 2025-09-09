#!/usr/bin/env python3
"""
Send SMS and Email to Jeremy Mayo via ClubOS API using confirmed member ID
"""

from src.services.api.clubos_api_client import ClubOSAPIClient, ClubOSAPIAuthentication
from config.secrets_local import get_secret
import time

TARGET_NAME = "Jeremy Mayo"
TARGET_MEMBER_ID = "187032782"  # Jeremy Mayo's confirmed member ID (from working Selenium script)
SMS_MESSAGE = "🎉 This is a test SMS sent via the ClubOS API! The new implementation is working!"
EMAIL_MESSAGE = "🎉 This is a test EMAIL sent via the ClubOS API! The coding agents fixed the messaging system!"

def send_message_to_jeremy_final():
    """Send both SMS and Email to Jeremy Mayo using the confirmed member ID"""
    
    print("🚀 SENDING MESSAGES TO JEREMY MAYO")
    print("=" * 50)
    print(f"Target: {TARGET_NAME}")
    print(f"Member ID: {TARGET_MEMBER_ID}")
    print()
    
    # Get credentials
    username = get_secret("clubos-username")
    password = get_secret("clubos-password")
    
    if not username or not password:
        print("❌ Missing ClubOS credentials")
        return False
    
    # Create authentication service and authenticate
    print("🔐 Authenticating with ClubOS...")
    auth_service = ClubOSAPIAuthentication()
    
    if not auth_service.login(username, password):
        print("❌ Authentication failed")
        return False
    
    print("✅ Authentication successful")
    print()
    
    # Create API client with authenticated auth service
    client = ClubOSAPIClient(auth_service)
    
    # Send SMS
    print("📱 SENDING SMS MESSAGE")
    print("-" * 30)
    sms_result = client.send_message(TARGET_MEMBER_ID, SMS_MESSAGE, "text")
    
    if sms_result:
        print("✅ SMS sent successfully!")
    else:
        print("❌ SMS failed")
    
    print()
    
    # Wait a moment between messages
    time.sleep(2)
    
    # Send Email
    print("📧 SENDING EMAIL MESSAGE")
    print("-" * 30)
    email_result = client.send_message(TARGET_MEMBER_ID, EMAIL_MESSAGE, "email")
    
    if email_result:
        print("✅ Email sent successfully!")
    else:
        print("❌ Email failed")
    
    print()
    
    # Summary
    print("📊 MESSAGE SENDING SUMMARY")
    print("=" * 30)
    print(f"SMS:   {'✅ SUCCESS' if sms_result else '❌ FAILED'}")
    print(f"Email: {'✅ SUCCESS' if email_result else '❌ FAILED'}")
    
    if sms_result or email_result:
        print("\n🎉 At least one message was sent successfully!")
        print("✅ ClubOS API messaging is working!")
        return True
    else:
        print("\n❌ No messages were sent successfully")
        return False

if __name__ == "__main__":
    success = send_message_to_jeremy_final()
    exit(0 if success else 1) 