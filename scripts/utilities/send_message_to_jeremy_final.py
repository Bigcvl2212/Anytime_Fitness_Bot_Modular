#!/usr/bin/env python3
"""
Send messages to Jeremy Mayo via ClubOS using the working approach
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from services.api.migration_service import get_migration_service
from config.secrets_local import get_secret
from datetime import datetime

TARGET_NAME = "Jeremy Mayo"
SMS_MESSAGE = "This is a test SMS sent via ClubOS API - it should work this time!"
EMAIL_MESSAGE = "This is a test EMAIL sent via ClubOS API - it should work this time!"

def main():
    username = get_secret('clubos-username')
    password = get_secret('clubos-password')
    
    if not username or not password:
        print("❌ ClubOS credentials not set in secrets_local.py.")
        return
    
    try:
        print("🔐 Initializing migration service...")
        migration_service = get_migration_service("hybrid")
        print("✅ Migration service initialized successfully!")
        
        # Send SMS
        print(f"\n📤 Sending SMS to {TARGET_NAME}...")
        sms_result = migration_service.send_message(TARGET_NAME, "Test SMS", SMS_MESSAGE)
        print(f"SMS Result: {sms_result}")
        
        # Send Email
        print(f"\n📤 Sending EMAIL to {TARGET_NAME}...")
        email_result = migration_service.send_message(TARGET_NAME, "Test Email", EMAIL_MESSAGE)
        print(f"Email Result: {email_result}")
        
        # Summary
        print(f"\n📊 Results Summary:")
        print(f"   SMS: {'✅ Success' if sms_result == True else '❌ Failed' if sms_result == False else f'⚠️ {sms_result}'}")
        print(f"   Email: {'✅ Success' if email_result == True else '❌ Failed' if email_result == False else f'⚠️ {email_result}'}")
        
        if sms_result == True or email_result == True:
            print("\n🎉 At least one message was sent successfully!")
        else:
            print("\n⚠️ No messages were delivered. Check the output above for details.")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 