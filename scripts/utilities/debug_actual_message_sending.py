#!/usr/bin/env python3
"""
Debug the actual message sending process to understand why messages aren't delivered
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config.secrets_local import get_secret
import time

TARGET_NAME = "Jeremy Mayo"
SMS_MESSAGE = "Debug test SMS - checking actual delivery!"
EMAIL_MESSAGE = "Debug test email - checking actual delivery!"

def debug_actual_message_sending():
    username = get_secret('clubos-username')
    password = get_secret('clubos-password')
    
    if not username or not password:
        print("❌ ClubOS credentials not set in secrets_local.py.")
        return

    # Set up Chrome with network logging
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # Enable network logging
    chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    try:
        print("🔍 Starting debug session...")
        
        # Navigate to ClubOS login
        print("📱 Navigating to ClubOS login...")
        driver.get("https://clubos.com/login")
        time.sleep(3)
        
        # Handle login form
        print("🔐 Attempting login...")
        wait = WebDriverWait(driver, 10)
        
        # Find and fill username
        username_field = wait.until(EC.presence_of_element_located((By.NAME, "username")))
        username_field.clear()
        username_field.send_keys(username)
        
        # Find and fill password
        password_field = driver.find_element(By.NAME, "password")
        password_field.clear()
        password_field.send_keys(password)
        
        # Submit login form
        login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        login_button.click()
        
        # Wait for dashboard
        print("⏳ Waiting for dashboard...")
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".dashboard")))
        print("✅ Successfully logged in!")
        
        # Navigate to search
        print("🔍 Navigating to member search...")
        driver.get("https://clubos.com/action/Dashboard/search")
        time.sleep(3)
        
        # Search for Jeremy Mayo
        print(f"🔍 Searching for {TARGET_NAME}...")
        search_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder*='search']")))
        search_input.clear()
        search_input.send_keys(TARGET_NAME)
        search_input.submit()
        time.sleep(3)
        
        # Click on Jeremy Mayo's profile
        print("👤 Clicking on Jeremy Mayo's profile...")
        jeremy_link = wait.until(EC.element_to_be_clickable((By.XPATH, f"//a[contains(text(), '{TARGET_NAME}')]")))
        jeremy_link.click()
        time.sleep(3)
        
        # Click follow-up button
        print("💬 Clicking follow-up button...")
        follow_up_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.follow-up")))
        follow_up_button.click()
        time.sleep(3)
        
        # Wait for popup and capture its HTML
        print("📋 Capturing popup HTML...")
        popup = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".modal-content")))
        
        # Save popup HTML for analysis
        with open("popup_debug_detailed.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("💾 Saved popup HTML to popup_debug_detailed.html")
        
        # Try to send SMS
        print("📱 Attempting to send SMS...")
        try:
            # Find SMS textarea
            sms_textarea = driver.find_element(By.CSS_SELECTOR, "textarea[name='textMessage']")
            
            # Use JavaScript to set value and trigger events
            driver.execute_script("""
                arguments[0].value = arguments[1];
                arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
            """, sms_textarea, SMS_MESSAGE)
            
            print("✅ SMS text set successfully")
            
            # Find and click save button
            save_button = driver.find_element(By.CSS_SELECTOR, "a.save-follow-up")
            
            # Capture network logs before clicking
            print("📊 Capturing network logs...")
            logs = driver.get_log('performance')
            
            # Click save button
            print("💾 Clicking save button...")
            save_button.click()
            
            # Wait a moment and capture more logs
            time.sleep(5)
            logs_after = driver.get_log('performance')
            
            # Save all logs
            with open("network_logs.txt", "w", encoding="utf-8") as f:
                f.write("=== BEFORE SAVE ===\n")
                for log in logs:
                    f.write(str(log) + "\n")
                f.write("\n=== AFTER SAVE ===\n")
                for log in logs_after:
                    f.write(str(log) + "\n")
            
            print("💾 Saved network logs to network_logs.txt")
            
            # Check for any error messages or success indicators
            page_source = driver.page_source
            with open("page_after_save.html", "w", encoding="utf-8") as f:
                f.write(page_source)
            print("💾 Saved page after save to page_after_save.html")
            
            # Look for success/error messages
            if "success" in page_source.lower():
                print("✅ Success indicator found in page")
            if "error" in page_source.lower():
                print("❌ Error indicator found in page")
            if "sent" in page_source.lower():
                print("✅ Sent indicator found in page")
            
            print("📱 SMS submission completed")
            
        except Exception as e:
            print(f"❌ SMS failed: {e}")
        
        # Try to send Email
        print("📧 Attempting to send Email...")
        try:
            # Find email textarea
            email_textarea = driver.find_element(By.CSS_SELECTOR, "textarea[name='emailMessage']")
            
            # Use JavaScript to set value and trigger events
            driver.execute_script("""
                arguments[0].value = arguments[1];
                arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
            """, email_textarea, EMAIL_MESSAGE)
            
            print("✅ Email text set successfully")
            
            # Find and click save button again
            save_button = driver.find_element(By.CSS_SELECTOR, "a.save-follow-up")
            save_button.click()
            
            print("📧 Email submission completed")
            
        except Exception as e:
            print(f"❌ Email failed: {e}")
        
        print("🔍 Debug session completed. Check the saved files for analysis.")
        
    except Exception as e:
        print(f"❌ Error during debug: {e}")
        driver.save_screenshot("debug_error.png")
        print("📸 Screenshot saved as debug_error.png")
    
    finally:
        driver.quit()

if __name__ == "__main__":
    debug_actual_message_sending() 