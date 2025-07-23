#!/usr/bin/env python3
"""
Use the proven working messaging function from services/clubos/messaging.py
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from services.clubos.messaging import send_clubos_message
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config.secrets_local import get_secret
import time

TARGET_NAME = "Jeremy Mayo"
SMS_MESSAGE = "Proven function SMS test - this should definitely work!"
EMAIL_MESSAGE = "Proven function email test - this should definitely work!"

def send_message_using_proven_function():
    username = get_secret('clubos-username')
    password = get_secret('clubos-password')
    
    if not username or not password:
        print("❌ ClubOS credentials not set in secrets_local.py.")
        return

    # Set up Chrome with proven working options
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--allow-running-insecure-content")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    try:
        print("🔐 Logging into ClubOS...")
        
        # Login using the proven approach
        driver.get("https://anytime.club-os.com/action/Login")
        time.sleep(2)
        
        username_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "username")))
        password_field = driver.find_element(By.NAME, "password")
        
        username_field.clear()
        username_field.send_keys(username)
        password_field.clear()
        password_field.send_keys(password)
        
        # Find and click login button
        login_button = driver.find_element(By.CSS_SELECTOR, "input[type='submit']")
        login_button.click()
        
        # Wait for login to complete
        WebDriverWait(driver, 15).until(EC.url_contains("Dashboard"))
        print("✅ Login successful!")
        
        # Use the proven messaging function for SMS
        print(f"\n📤 Sending SMS to {TARGET_NAME} using proven function...")
        sms_result = send_clubos_message(driver, TARGET_NAME, "Proven Function SMS Test", SMS_MESSAGE)
        
        if sms_result == True:
            print("✅ SMS sent successfully!")
        elif sms_result == "OPTED_OUT":
            print("⚠️ Member has opted out of SMS")
        else:
            print(f"❌ SMS failed: {sms_result}")
        
        # Use the proven messaging function for Email
        print(f"\n📤 Sending Email to {TARGET_NAME} using proven function...")
        email_result = send_clubos_message(driver, TARGET_NAME, "Proven Function Email Test", EMAIL_MESSAGE)
        
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
        driver.save_screenshot("proven_function_error.png")
        print("📸 Screenshot saved as proven_function_error.png")
    
    finally:
        driver.quit()

if __name__ == "__main__":
    send_message_using_proven_function() 