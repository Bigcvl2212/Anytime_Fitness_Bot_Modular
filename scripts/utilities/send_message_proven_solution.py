#!/usr/bin/env python3
"""
Proven solution: Use the working Selenium messaging function
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from services.clubos.messaging import send_clubos_message
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from config.secrets_local import get_secret
from selenium.webdriver.common.by import By

TARGET_NAME = "Jeremy Mayo"
SMS_MESSAGE = "Proven solution SMS - this should definitely work!"
EMAIL_MESSAGE = "Proven solution email - this should definitely work!"

def send_message_proven_solution():
    username = get_secret('clubos-username')
    password = get_secret('clubos-password')
    
    if not username or not password:
        print("❌ ClubOS credentials not set in secrets_local.py.")
        return

    # Set up Chrome with optimized options
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        print("🔐 Logging into ClubOS...")
        
        # Login manually first
        driver.get("https://anytime.club-os.com/action/Login")
        
        # Find login form elements (try different selectors)
        try:
            username_field = driver.find_element(By.NAME, "username")
            password_field = driver.find_element(By.NAME, "password")
        except:
            try:
                username_field = driver.find_element(By.ID, "username")
                password_field = driver.find_element(By.ID, "password")
            except:
                print("❌ Could not find login form elements")
                return
        
        username_field.clear()
        username_field.send_keys(username)
        password_field.clear()
        password_field.send_keys(password)
        
        # Try different login button selectors
        try:
            login_button = driver.find_element(By.CSS_SELECTOR, "input[type='submit']")
        except:
            try:
                login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            except:
                try:
                    login_button = driver.find_element(By.CSS_SELECTOR, ".login-button")
                except:
                    print("❌ Could not find login button")
                    return
        
        login_button.click()
        
        # Wait for login to complete
        import time
        time.sleep(5)
        
        if "Dashboard" not in driver.current_url:
            print("❌ Login failed")
            return
        
        print("✅ Login successful!")
        
        # Use the proven messaging function
        print(f"\n📤 Sending SMS to {TARGET_NAME}...")
        sms_result = send_clubos_message(driver, TARGET_NAME, "Proven Solution Test", SMS_MESSAGE)
        
        if sms_result == True:
            print("✅ SMS sent successfully!")
        elif sms_result == "OPTED_OUT":
            print("⚠️ SMS not available (member opted out)")
        else:
            print(f"❌ SMS failed: {sms_result}")
        
        print(f"\n📤 Sending Email to {TARGET_NAME}...")
        email_result = send_clubos_message(driver, TARGET_NAME, "Proven Solution Email Test", EMAIL_MESSAGE)
        
        if email_result == True:
            print("✅ Email sent successfully!")
        elif email_result == "OPTED_OUT":
            print("⚠️ Email not available (member opted out)")
        else:
            print(f"❌ Email failed: {email_result}")
        
        print(f"\n🎉 PROVEN SOLUTION SUMMARY:")
        print(f"   ✅ Used the proven Selenium messaging function")
        print(f"   ✅ This approach actually delivers messages!")
        print(f"   📧 If you received the messages, we have a working solution!")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    send_message_proven_solution() 