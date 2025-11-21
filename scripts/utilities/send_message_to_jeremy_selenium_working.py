#!/usr/bin/env python3
"""
Send messages to Jeremy Mayo via ClubOS using the proven Selenium messaging function
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.services.clubos.messaging import send_clubos_message
from core.driver import setup_driver_and_login
from config.secrets_local import get_secret

TARGET_NAME = "Jeremy Mayo"
SMS_MESSAGE = "This is a test SMS sent via ClubOS Selenium - it should work this time!"
EMAIL_MESSAGE = "This is a test EMAIL sent via ClubOS Selenium - it should work this time!"

def send_messages_via_selenium():
    """Send messages using the proven Selenium messaging function"""
    
    username = get_secret('clubos-username')
    password = get_secret('clubos-password')
    
    if not username or not password:
        print("❌ ClubOS credentials not set in secrets_local.py.")
        return
    
    try:
        print("🌐 Setting up Selenium driver and logging into ClubOS...")
        driver = setup_driver_and_login()
        
        if not driver:
            print("❌ Failed to setup Selenium driver")
            return
        
        print("✅ Selenium driver setup and login successful!")
        
        # Send SMS
        print(f"\n📤 Sending SMS to {TARGET_NAME}...")
        sms_result = send_clubos_message(driver, TARGET_NAME, "Test SMS", SMS_MESSAGE)
        print(f"SMS Result: {sms_result}")
        
        # Send Email
        print(f"\n📤 Sending EMAIL to {TARGET_NAME}...")
        email_result = send_clubos_message(driver, TARGET_NAME, "Test Email", EMAIL_MESSAGE)
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
        print(f"❌ Error during automation: {e}")
    
    finally:
        try:
            driver.quit()
        except:
            pass

if __name__ == "__main__":
    send_messages_via_selenium() 