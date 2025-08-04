#!/usr/bin/env python3
"""
Send messages to Jeremy Mayo via ClubOS using Selenium
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from config.secrets_local import get_secret
import time

TARGET_NAME = "Jeremy Mayo"
MEMBER_ID = "187032782"  # Known Jeremy Mayo member ID
SMS_MESSAGE = "This is a test SMS sent via ClubOS Selenium."
EMAIL_MESSAGE = "This is a test EMAIL sent via ClubOS Selenium."

def send_messages_via_selenium():
    """Send messages using Selenium automation"""
    
    username = get_secret('clubos-username')
    password = get_secret('clubos-password')
    
    if not username or not password:
        print("❌ ClubOS credentials not set in secrets_local.py.")
        return
    
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.implicitly_wait(10)
        
        print("🌐 Starting ClubOS automation...")
        
        # Step 1: Login to ClubOS
        print("📝 Logging into ClubOS...")
        driver.get("https://anytime.club-os.com/action/Login")
        
        # Wait for login form and fill credentials
        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        password_field = driver.find_element(By.NAME, "password")
        
        username_field.send_keys(username)
        password_field.send_keys(password)
        
        # Submit login form
        submit_button = driver.find_element(By.NAME, "submit")
        submit_button.click()
        
        # Wait for login to complete
        WebDriverWait(driver, 10).until(
            EC.url_contains("Dashboard") or EC.url_contains("dashboard")
        )
        print("✅ Login successful!")
        
        # Step 2: Navigate to Messages page
        print("📄 Navigating to Messages page...")
        driver.get("https://anytime.club-os.com/action/Dashboard/messages")
        time.sleep(3)
        
        # Step 3: Find and fill message form
        print("📝 Filling message form...")
        
        # Look for member search field
        try:
            member_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder*='member'], input[name*='member'], input[id*='member']"))
            )
            member_field.clear()
            member_field.send_keys("Jeremy Mayo")
            time.sleep(2)
            
            # Look for dropdown and select Jeremy Mayo
            dropdown_item = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Jeremy Mayo')]"))
            )
            dropdown_item.click()
            print("✅ Selected Jeremy Mayo")
            
        except Exception as e:
            print(f"⚠️ Could not find member search field: {e}")
            # Try alternative approach - look for member ID field
            try:
                member_id_field = driver.find_element(By.NAME, "memberId")
                member_id_field.clear()
                member_id_field.send_keys(MEMBER_ID)
                print("✅ Entered member ID directly")
            except:
                print("⚠️ Could not find member ID field either")
        
        # Step 4: Fill message content
        try:
            message_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "textarea, input[name*='message'], input[id*='message']"))
            )
            message_field.clear()
            message_field.send_keys(SMS_MESSAGE)
            print("✅ Filled message content")
        except Exception as e:
            print(f"⚠️ Could not find message field: {e}")
        
        # Step 5: Select message type (SMS)
        try:
            sms_radio = driver.find_element(By.CSS_SELECTOR, "input[type='radio'][value='sms'], input[type='radio'][name*='sms']")
            sms_radio.click()
            print("✅ Selected SMS option")
        except:
            print("⚠️ Could not find SMS radio button")
        
        # Step 6: Send SMS
        try:
            send_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit'], input[type='submit'], .send-button, .submit-button"))
            )
            send_button.click()
            print("📤 SMS sent!")
            time.sleep(3)
        except Exception as e:
            print(f"⚠️ Could not send SMS: {e}")
        
        # Step 7: Send Email
        print("📧 Sending email...")
        try:
            # Clear message field and enter email message
            message_field = driver.find_element(By.CSS_SELECTOR, "textarea, input[name*='message'], input[id*='message']")
            message_field.clear()
            message_field.send_keys(EMAIL_MESSAGE)
            
            # Select email option
            email_radio = driver.find_element(By.CSS_SELECTOR, "input[type='radio'][value='email'], input[type='radio'][name*='email']")
            email_radio.click()
            
            # Send email
            send_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit'], input[type='submit'], .send-button, .submit-button")
            send_button.click()
            print("📤 Email sent!")
            
        except Exception as e:
            print(f"⚠️ Could not send email: {e}")
        
        print("\n✅ Message sending completed!")
        time.sleep(5)
        
    except Exception as e:
        print(f"❌ Error during automation: {e}")
    
    finally:
        try:
            driver.quit()
        except:
            pass

if __name__ == "__main__":
    send_messages_via_selenium() 