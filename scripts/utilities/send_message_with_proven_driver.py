#!/usr/bin/env python3
"""
Use the proven working driver setup and messaging functions
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from core.driver import setup_driver_and_login
from services.clubos.messaging import send_clubos_message

TARGET_NAME = "Jeremy Mayo"
SMS_MESSAGE = "Proven driver SMS test - this should definitely work!"
EMAIL_MESSAGE = "Proven driver email test - this should definitely work!"

def send_message_with_proven_driver():
    try:
        print("🔐 Setting up proven driver and logging into ClubOS...")
        
        # Use the proven driver setup function
        driver = setup_driver_and_login()
        
        if not driver:
            print("❌ Failed to setup driver and login")
            return
        
        print("✅ Driver setup and login successful!")
        
        # Use the proven messaging function for SMS
        print(f"\n📤 Sending SMS to {TARGET_NAME} using proven function...")
        sms_result = send_clubos_message(driver, TARGET_NAME, "Proven Driver SMS Test", SMS_MESSAGE)
        
        if sms_result == True:
            print("✅ SMS sent successfully!")
        elif sms_result == "OPTED_OUT":
            print("⚠️ Member has opted out of SMS")
        else:
            print(f"❌ SMS failed: {sms_result}")
        
        # Use the proven messaging function for Email
        print(f"\n📤 Sending Email to {TARGET_NAME} using proven function...")
        email_result = send_clubos_message(driver, TARGET_NAME, "Proven Driver Email Test", EMAIL_MESSAGE)
        
        if email_result == True:
            print("✅ Email sent successfully!")
        elif email_result == "OPTED_OUT":
            print("⚠️ Member has opted out of Email")
        else:
            print(f"❌ Email failed: {email_result}")
        
        # Summary
        print(f"\n📊 Results Summary:")
        print(f"   SMS: {'✅ Success' if sms_result == True else '❌ Failed' if sms_result == False else f'⚠️ {sms_result}'}")
        print(f"   Email: {'✅ Success' if email_result == True else '❌ Failed' if email_result == False else f'⚠️ {email_result}'}")
        
        if sms_result == True or email_result == True:
            print("\n🎉 At least one message was sent successfully!")
        else:
            print("\n⚠️ No messages were delivered. Check the output above for details.")
            
    except Exception as e:
        print(f"❌ Error during messaging: {e}")
    
    finally:
        try:
            if driver:
                driver.quit()
        except:
            pass

if __name__ == "__main__":
    send_message_with_proven_driver() 