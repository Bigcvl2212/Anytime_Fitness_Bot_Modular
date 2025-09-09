#!/usr/bin/env python3
"""
Working API solution using the existing enhanced ClubOS API service
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.services.api.enhanced_clubos_service import ClubOSAPIService
from config.secrets_local import get_secret

TARGET_NAME = "Jeremy Mayo"
SMS_MESSAGE = "API working solution SMS - this should definitely work!"
EMAIL_MESSAGE = "API working solution email - this should definitely work!"

def send_message_api_working():
    username = get_secret('clubos-username')
    password = get_secret('clubos-password')
    
    if not username or not password:
        print("❌ ClubOS credentials not set in secrets_local.py.")
        return

    try:
        print("🔐 Initializing ClubOS API service...")
        
        # Create the enhanced API service
        api_service = ClubOSAPIService(username, password)
        print("✅ API service initialized successfully!")
        
        # Send SMS using the API
        print(f"\n📤 Sending SMS to {TARGET_NAME} via API...")
        sms_result = api_service.send_clubos_message(
            member_name=TARGET_NAME,
            subject="API Working SMS Test",
            body=SMS_MESSAGE
        )
        
        if sms_result == True:
            print("✅ SMS sent successfully via API!")
        elif sms_result == "OPTED_OUT":
            print("⚠️ Member has opted out of SMS")
        else:
            print(f"❌ SMS failed: {sms_result}")
        
        # Send Email using the API
        print(f"\n📤 Sending Email to {TARGET_NAME} via API...")
        email_result = api_service.send_clubos_message(
            member_name=TARGET_NAME,
            subject="API Working Email Test",
            body=EMAIL_MESSAGE
        )
        
        if email_result == True:
            print("✅ Email sent successfully via API!")
        elif email_result == "OPTED_OUT":
            print("⚠️ Member has opted out of Email")
        else:
            print(f"❌ Email failed: {email_result}")
        
        # Summary
        print(f"\n📊 API Results Summary:")
        print(f"   SMS: {'✅ Success' if sms_result == True else '❌ Failed' if sms_result == False else f'⚠️ {sms_result}'}")
        print(f"   Email: {'✅ Success' if email_result == True else '❌ Failed' if email_result == False else f'⚠️ {email_result}'}")
        
        if sms_result == True or email_result == True:
            print("\n🎉 At least one message was sent successfully via API!")
        else:
            print("\n⚠️ No messages were delivered via API. Check the output above for details.")
            
    except Exception as e:
        print(f"❌ Error during API messaging: {e}")

if __name__ == "__main__":
    send_message_api_working() 