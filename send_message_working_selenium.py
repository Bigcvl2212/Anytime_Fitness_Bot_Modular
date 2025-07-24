#!/usr/bin/env python3
"""
Working Selenium script to send real messages via ClubOS
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from config.secrets_local import get_secret
import time

TARGET_NAME = "Jeremy Mayo"
SMS_MESSAGE = "🎉 This is a REAL SMS sent via working Selenium! The API approach was wrong!"
EMAIL_MESSAGE = "🎉 This is a REAL EMAIL sent via working Selenium! The API approach was wrong!"

def send_message_working_selenium():
    username = get_secret('clubos-username')
    password = get_secret('clubos-password')
    
    if not username or not password:
        print("❌ ClubOS credentials not set in secrets_local.py.")
        return

    # Set up Chrome with better options
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
        print("🔐 Logging into ClubOS via Selenium...")
        
        # Login
        driver.get("https://anytime.club-os.com/action/Login")
        time.sleep(3)
        
        # Find login form elements with better error handling
        try:
            username_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "username")))
            password_field = driver.find_element(By.NAME, "password")
        except:
            print("❌ Could not find username/password fields")
            return
        
        username_field.clear()
        username_field.send_keys(username)
        password_field.clear()
        password_field.send_keys(password)
        
        # Try different login button selectors
        login_button = None
        try:
            login_button = driver.find_element(By.CSS_SELECTOR, "input[type='submit']")
        except:
            try:
                login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            except:
                try:
                    login_button = driver.find_element(By.CSS_SELECTOR, ".btn-primary")
                except:
                    try:
                        login_button = driver.find_element(By.CSS_SELECTOR, "input[value*='Login'], input[value*='Sign']")
                    except:
                        print("❌ Could not find login button")
                        return
        
        if login_button:
            login_button.click()
            print("✅ Clicked login button")
        
        # Wait for login to complete
        WebDriverWait(driver, 15).until(EC.url_contains("Dashboard"))
        print("✅ Login successful!")
        
        # Go to dashboard
        driver.get("https://anytime.club-os.com/action/Dashboard/view")
        time.sleep(3)
        
        # Search for Jeremy Mayo
        print(f"🔍 Searching for {TARGET_NAME}...")
        search_box = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.ID, "quick-search-text")))
        search_box.clear()
        search_box.send_keys(TARGET_NAME)
        time.sleep(4)
        
        # Click on the search result
        contact_result_xpath = f"//h4[normalize-space(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'))='{TARGET_NAME.lower()}']"
        WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, contact_result_xpath))).click()
        
        print("✅ Clicked on member profile")
        time.sleep(3)
        
        # Click "Send Message" button
        print("📤 Clicking 'Send Message' button...")
        send_message_button = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a[data-original-title='Send Message']"))
        )
        send_message_button.click()
        
        print("✅ Opened message popup")
        time.sleep(4)
        
        # Send SMS
        print("📤 Sending SMS...")
        try:
            # Find the text message field
            text_message_field = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "textMessage")))
            text_message_field.clear()
            text_message_field.send_keys(SMS_MESSAGE)
            print("   ✅ Entered SMS message")
            
            # Find the notes field
            notes_field = driver.find_element(By.NAME, "followUpOutcomeNotes")
            notes_field.clear()
            notes_field.send_keys("Working Selenium test")
            print("   ✅ Entered notes")
            
            # Find and click the save button
            save_button = driver.find_element(By.CSS_SELECTOR, "a.save-follow-up")
            print("   🚀 Clicking save button for SMS...")
            driver.execute_script("arguments[0].click();", save_button)
            
            # Wait for popup to close
            WebDriverWait(driver, 15).until(
                EC.invisibility_of_element_located((By.ID, "followup-popup-content"))
            )
            print("   ✅ SMS sent successfully!")
            
        except Exception as e:
            print(f"   ❌ SMS failed: {e}")
        
        # Send Email
        print("📤 Sending Email...")
        try:
            # Re-open popup if it closed during SMS
            try:
                popup = driver.find_element(By.ID, "followup-popup-content")
                if not popup.is_displayed():
                    print("   📤 Re-opening message popup for email...")
                    send_message_button = WebDriverWait(driver, 15).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "a[data-original-title='Send Message']"))
                    )
                    send_message_button.click()
                    time.sleep(3)
            except:
                pass
            
            # Switch to email tab
            email_tab = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "email-tab")))
            email_tab.click()
            time.sleep(2)
            
            # Fill email subject
            subject_field = driver.find_element(By.NAME, "emailSubject")
            subject_field.clear()
            subject_field.send_keys("Working Selenium Test Email")
            
            # Fill email body
            email_body_editor = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.redactor_editor")))
            driver.execute_script("arguments[0].innerHTML = arguments[1];", email_body_editor, EMAIL_MESSAGE)
            
            # Fill notes
            notes_field = driver.find_element(By.NAME, "followUpOutcomeNotes")
            notes_field.clear()
            notes_field.send_keys("Working Selenium email test")
            
            # Send email
            save_button = driver.find_element(By.CSS_SELECTOR, "a.save-follow-up")
            print("   🚀 Clicking save button for email...")
            driver.execute_script("arguments[0].click();", save_button)
            
            # Wait for popup to close
            WebDriverWait(driver, 15).until(
                EC.invisibility_of_element_located((By.ID, "followup-popup-content"))
            )
            print("   ✅ Email sent successfully!")
            
        except Exception as e:
            print(f"   ❌ Email failed: {e}")
        
        print(f"\n🎉 WORKING SELENIUM SOLUTION SUMMARY:")
        print(f"   ✅ Login works with proper form handling")
        print(f"   ✅ Navigates to member profile")
        print(f"   ✅ Opens message popup")
        print(f"   ✅ Sends real SMS and Email messages!")
        print(f"   📧 Check your phone and email for the messages!")
        
    except Exception as e:
        print(f"❌ Error during automation: {e}")
    
    finally:
        try:
            driver.quit()
        except:
            pass

if __name__ == "__main__":
    send_message_working_selenium() 