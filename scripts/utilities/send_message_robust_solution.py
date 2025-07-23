#!/usr/bin/env python3
"""
Robust solution that handles login issues and focuses on getting messaging to work
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from config.secrets_local import get_secret
import time

TARGET_NAME = "Jeremy Mayo"
SMS_MESSAGE = "Robust solution SMS test - this should work!"
EMAIL_MESSAGE = "Robust solution email test - this should work!"

def send_message_robust_solution():
    username = get_secret('clubos-username')
    password = get_secret('clubos-password')
    
    if not username or not password:
        print("❌ ClubOS credentials not set in secrets_local.py.")
        return

    # Set up Chrome with better options
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--allow-running-insecure-content")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    try:
        print("🔍 Starting robust messaging session...")
        
        # Navigate to ClubOS login with retry
        print("📱 Navigating to ClubOS login...")
        driver.get("https://clubos.com/login")
        time.sleep(5)  # Give more time for page to load
        
        # Handle login form with better error handling
        print("🔐 Attempting login...")
        wait = WebDriverWait(driver, 15)
        
        try:
            # Find and fill username
            username_field = wait.until(EC.presence_of_element_located((By.NAME, "username")))
            username_field.clear()
            time.sleep(1)
            username_field.send_keys(username)
            print("✅ Username entered")
            
            # Find and fill password
            password_field = driver.find_element(By.NAME, "password")
            password_field.clear()
            time.sleep(1)
            password_field.send_keys(password)
            print("✅ Password entered")
            
            # Submit login form
            login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_button.click()
            print("✅ Login button clicked")
            
            # Wait for dashboard with longer timeout
            print("⏳ Waiting for dashboard...")
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".dashboard, .main-content")))
            print("✅ Successfully logged in!")
            
        except TimeoutException:
            print("❌ Login timeout - trying alternative approach...")
            # Try to find any dashboard-like element
            dashboard_elements = driver.find_elements(By.CSS_SELECTOR, ".dashboard, .main-content, .container")
            if dashboard_elements:
                print("✅ Found dashboard-like element, proceeding...")
            else:
                print("❌ Still can't find dashboard, but proceeding anyway...")
        
        # Navigate to search
        print("🔍 Navigating to member search...")
        driver.get("https://clubos.com/action/Dashboard/search")
        time.sleep(5)
        
        # Search for Jeremy Mayo
        print(f"🔍 Searching for {TARGET_NAME}...")
        try:
            search_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder*='search'], input[type='text']")))
            search_input.clear()
            time.sleep(1)
            search_input.send_keys(TARGET_NAME)
            search_input.submit()
            time.sleep(5)
        except TimeoutException:
            print("❌ Search input not found, trying alternative...")
            # Try to find any input field
            inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='text']")
            if inputs:
                inputs[0].clear()
                inputs[0].send_keys(TARGET_NAME)
                inputs[0].submit()
                time.sleep(5)
        
        # Click on Jeremy Mayo's profile
        print("👤 Looking for Jeremy Mayo's profile...")
        try:
            jeremy_link = wait.until(EC.element_to_be_clickable((By.XPATH, f"//a[contains(text(), '{TARGET_NAME}')]")))
            jeremy_link.click()
            time.sleep(5)
        except TimeoutException:
            print("❌ Jeremy Mayo link not found, trying alternative...")
            # Try to find any link with Jeremy or Mayo
            links = driver.find_elements(By.XPATH, "//a[contains(text(), 'Jeremy') or contains(text(), 'Mayo')]")
            if links:
                links[0].click()
                time.sleep(5)
        
        # Click follow-up button
        print("💬 Looking for follow-up button...")
        try:
            follow_up_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.follow-up")))
            follow_up_button.click()
            time.sleep(5)
        except TimeoutException:
            print("❌ Follow-up button not found, trying alternatives...")
            # Try different selectors
            selectors = ["a.follow-up", "button.follow-up", ".follow-up", "a[href*='follow']"]
            for selector in selectors:
                try:
                    button = driver.find_element(By.CSS_SELECTOR, selector)
                    button.click()
                    time.sleep(5)
                    print(f"✅ Found and clicked button with selector: {selector}")
                    break
                except NoSuchElementException:
                    continue
        
        # Wait for popup
        print("📋 Waiting for popup...")
        try:
            popup = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".modal-content, .popup, .dialog")))
            print("✅ Popup found!")
        except TimeoutException:
            print("❌ Popup not found, but continuing...")
        
        # Try to send SMS
        print("📱 Attempting to send SMS...")
        try:
            # Find SMS textarea with multiple selectors
            sms_selectors = [
                "textarea[name='textMessage']",
                "textarea[name='smsMessage']", 
                "textarea[name='message']",
                "input[name='textMessage']",
                "input[name='smsMessage']"
            ]
            
            sms_textarea = None
            for selector in sms_selectors:
                try:
                    sms_textarea = driver.find_element(By.CSS_SELECTOR, selector)
                    print(f"✅ Found SMS field with selector: {selector}")
                    break
                except NoSuchElementException:
                    continue
            
            if sms_textarea:
                # Use JavaScript to set value and trigger events
                driver.execute_script("""
                    arguments[0].value = arguments[1];
                    arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                    arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
                """, sms_textarea, SMS_MESSAGE)
                
                print("✅ SMS text set successfully")
                
                # Find and click save button
                save_selectors = ["a.save-follow-up", "button.save", ".save", "input[type='submit']"]
                save_button = None
                for selector in save_selectors:
                    try:
                        save_button = driver.find_element(By.CSS_SELECTOR, selector)
                        print(f"✅ Found save button with selector: {selector}")
                        break
                    except NoSuchElementException:
                        continue
                
                if save_button:
                    save_button.click()
                    print("💾 Save button clicked")
                    time.sleep(3)
                    
                    # Check for success/error messages
                    page_source = driver.page_source.lower()
                    if "success" in page_source:
                        print("✅ Success indicator found!")
                    if "error" in page_source:
                        print("❌ Error indicator found!")
                    if "sent" in page_source:
                        print("✅ Sent indicator found!")
                    
                    print("📱 SMS submission completed")
                else:
                    print("❌ Save button not found")
            else:
                print("❌ SMS textarea not found")
                
        except Exception as e:
            print(f"❌ SMS failed: {e}")
        
        # Try to send Email
        print("📧 Attempting to send Email...")
        try:
            # Find email textarea with multiple selectors
            email_selectors = [
                "textarea[name='emailMessage']",
                "textarea[name='email']", 
                "textarea[name='message']",
                "input[name='emailMessage']",
                "input[name='email']"
            ]
            
            email_textarea = None
            for selector in email_selectors:
                try:
                    email_textarea = driver.find_element(By.CSS_SELECTOR, selector)
                    print(f"✅ Found email field with selector: {selector}")
                    break
                except NoSuchElementException:
                    continue
            
            if email_textarea:
                # Use JavaScript to set value and trigger events
                driver.execute_script("""
                    arguments[0].value = arguments[1];
                    arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                    arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
                """, email_textarea, EMAIL_MESSAGE)
                
                print("✅ Email text set successfully")
                
                # Find and click save button again
                save_selectors = ["a.save-follow-up", "button.save", ".save", "input[type='submit']"]
                save_button = None
                for selector in save_selectors:
                    try:
                        save_button = driver.find_element(By.CSS_SELECTOR, selector)
                        break
                    except NoSuchElementException:
                        continue
                
                if save_button:
                    save_button.click()
                    print("💾 Email save button clicked")
                    time.sleep(3)
                    
                    # Check for success/error messages
                    page_source = driver.page_source.lower()
                    if "success" in page_source:
                        print("✅ Success indicator found!")
                    if "error" in page_source:
                        print("❌ Error indicator found!")
                    if "sent" in page_source:
                        print("✅ Sent indicator found!")
                    
                    print("📧 Email submission completed")
                else:
                    print("❌ Email save button not found")
            else:
                print("❌ Email textarea not found")
                
        except Exception as e:
            print(f"❌ Email failed: {e}")
        
        print("🔍 Robust messaging session completed.")
        
    except Exception as e:
        print(f"❌ Error during robust session: {e}")
        driver.save_screenshot("robust_error.png")
        print("📸 Screenshot saved as robust_error.png")
    
    finally:
        driver.quit()

if __name__ == "__main__":
    send_message_robust_solution() 