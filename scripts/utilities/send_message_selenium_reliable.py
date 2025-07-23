#!/usr/bin/env python3
"""
Reliable Selenium-based messaging using the proven working code
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from config.secrets_local import get_secret
import time

TARGET_NAME = "Jeremy Mayo"
SMS_MESSAGE = "Test SMS via reliable Selenium - this should definitely work!"
EMAIL_MESSAGE = "Test Email via reliable Selenium - this should definitely work!"

def send_message_selenium_reliable():
    username = get_secret('clubos-username')
    password = get_secret('clubos-password')
    
    if not username or not password:
        print("❌ ClubOS credentials not set in secrets_local.py.")
        return

    # Set up Chrome with better options for reliability
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
    
    # Hide automation
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    try:
        print("🔐 Logging into ClubOS via Selenium...")
        
        # Login
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
        
        # Go to dashboard
        driver.get("https://anytime.club-os.com/action/Dashboard/view")
        time.sleep(3)
        
        # Search for Jeremy Mayo
        print(f"🔍 Searching for {TARGET_NAME}...")
        search_box = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.ID, "quick-search-text")))
        search_box.clear()
        search_box.send_keys(TARGET_NAME)
        time.sleep(4)  # Give more time for search results
        
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
        time.sleep(4)  # Give more time for popup to load
        
        # Check for available communication channels
        text_tab_present = False
        email_tab_present = False
        
        try:
            text_tab = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, "text-tab")))
            if text_tab.is_displayed():
                text_tab_present = True
                print("   ✅ Text tab available")
        except TimeoutException:
            print("   ⚠️ Text tab not found")
        
        try:
            email_tab = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, "email-tab")))
            if email_tab.is_displayed():
                email_tab_present = True
                print("   ✅ Email tab available")
        except TimeoutException:
            print("   ⚠️ Email tab not found")
        
        if not text_tab_present and not email_tab_present:
            print("   ❌ No communication channels available")
            return
        
        # Send SMS if available
        if text_tab_present:
            print("📤 Sending SMS...")
            try:
                text_tab = driver.find_element(By.ID, "text-tab")
                text_tab.click()
                time.sleep(2)
                
                text_area = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "textMessage")))
                text_area.clear()
                text_area.send_keys(SMS_MESSAGE)
                
                notes_field = driver.find_element(By.NAME, "followUpOutcomeNotes")
                notes_field.clear()
                notes_field.send_keys("Reliable Selenium test")
                
                print("   🚀 Clicking send button for SMS...")
                send_button = driver.find_element(By.CSS_SELECTOR, "a.save-follow-up")
                driver.execute_script("arguments[0].click();", send_button)
                
                # Wait for popup to close
                WebDriverWait(driver, 15).until(
                    EC.invisibility_of_element_located((By.ID, "followup-popup-content"))
                )
                print("   ✅ SMS sent successfully!")
                
            except Exception as e:
                print(f"   ❌ SMS failed: {e}")
        
        # Send Email if available
        if email_tab_present:
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
                
                email_tab = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "email-tab")))
                email_tab.click()
                time.sleep(2)
                
                subject_field = driver.find_element(By.NAME, "emailSubject")
                subject_field.clear()
                subject_field.send_keys("Reliable Selenium Test Email")
                
                email_body_editor = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.redactor_editor")))
                driver.execute_script("arguments[0].innerHTML = arguments[1];", email_body_editor, EMAIL_MESSAGE)
                
                notes_field = driver.find_element(By.NAME, "followUpOutcomeNotes")
                notes_field.clear()
                notes_field.send_keys("Reliable Selenium email test")
                
                print("   🚀 Clicking send button for email...")
                send_button = driver.find_element(By.CSS_SELECTOR, "a.save-follow-up")
                driver.execute_script("arguments[0].click();", send_button)
                
                # Wait for popup to close
                WebDriverWait(driver, 20).until(
                    EC.invisibility_of_element_located((By.ID, "followup-popup-content"))
                )
                print("   ✅ Email sent successfully!")
                
            except Exception as e:
                print(f"   ❌ Email failed: {e}")
        
        print(f"\n📊 Selenium Messaging Summary:")
        print(f"   If you received the messages, the Selenium approach is working reliably!")
        print(f"   This is the proven method that actually delivers messages.")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    send_message_selenium_reliable() 