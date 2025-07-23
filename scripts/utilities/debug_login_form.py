#!/usr/bin/env python3
"""
Debug the actual login form structure and make it work
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

def debug_login_form():
    username = get_secret('clubos-username')
    password = get_secret('clubos-password')
    
    if not username or not password:
        print("❌ ClubOS credentials not set in secrets_local.py.")
        return

    # Set up Chrome with debugging options
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        print("🔍 Debugging ClubOS login form...")
        
        # Go to login page
        driver.get("https://anytime.club-os.com/action/Login")
        time.sleep(3)
        
        print(f"   Current URL: {driver.current_url}")
        print(f"   Page title: {driver.title}")
        
        # Save the login page HTML for analysis
        with open('login_page_debug.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print("   💾 Saved login page HTML to login_page_debug.html")
        
        # Find all form elements
        print("\n🔍 Analyzing form elements...")
        
        forms = driver.find_elements(By.TAG_NAME, "form")
        print(f"   Found {len(forms)} forms")
        
        for i, form in enumerate(forms):
            print(f"   Form {i+1}:")
            print(f"      Action: {form.get_attribute('action')}")
            print(f"      Method: {form.get_attribute('method')}")
            print(f"      ID: {form.get_attribute('id')}")
            print(f"      Class: {form.get_attribute('class')}")
        
        # Find all input elements
        inputs = driver.find_elements(By.TAG_NAME, "input")
        print(f"\n   Found {len(inputs)} input elements")
        
        for i, input_elem in enumerate(inputs):
            input_type = input_elem.get_attribute('type')
            input_name = input_elem.get_attribute('name')
            input_id = input_elem.get_attribute('id')
            input_class = input_elem.get_attribute('class')
            
            print(f"   Input {i+1}: type={input_type}, name={input_name}, id={input_id}, class={input_class}")
        
        # Find all button elements
        buttons = driver.find_elements(By.TAG_NAME, "button")
        print(f"\n   Found {len(buttons)} button elements")
        
        for i, button in enumerate(buttons):
            button_type = button.get_attribute('type')
            button_text = button.text
            button_id = button.get_attribute('id')
            button_class = button.get_attribute('class')
            
            print(f"   Button {i+1}: type={button_type}, text='{button_text}', id={button_id}, class={button_class}")
        
        # Try to find username and password fields
        print("\n🔍 Looking for username/password fields...")
        
        username_field = None
        password_field = None
        
        # Try different selectors for username
        username_selectors = [
            (By.NAME, "username"),
            (By.ID, "username"),
            (By.NAME, "user"),
            (By.NAME, "email"),
            (By.CSS_SELECTOR, "input[type='text']"),
            (By.CSS_SELECTOR, "input[placeholder*='username']"),
            (By.CSS_SELECTOR, "input[placeholder*='email']")
        ]
        
        for selector_type, selector_value in username_selectors:
            try:
                username_field = driver.find_element(selector_type, selector_value)
                print(f"   ✅ Found username field with {selector_type}: {selector_value}")
                break
            except:
                continue
        
        # Try different selectors for password
        password_selectors = [
            (By.NAME, "password"),
            (By.ID, "password"),
            (By.NAME, "pass"),
            (By.CSS_SELECTOR, "input[type='password']")
        ]
        
        for selector_type, selector_value in password_selectors:
            try:
                password_field = driver.find_element(selector_type, selector_value)
                print(f"   ✅ Found password field with {selector_type}: {selector_value}")
                break
            except:
                continue
        
        if not username_field:
            print("   ❌ Could not find username field")
            return
        
        if not password_field:
            print("   ❌ Could not find password field")
            return
        
        # Try to find submit button
        print("\n🔍 Looking for submit button...")
        
        submit_button = None
        submit_selectors = [
            (By.CSS_SELECTOR, "input[type='submit']"),
            (By.CSS_SELECTOR, "button[type='submit']"),
            (By.CSS_SELECTOR, "button:contains('Login')"),
            (By.CSS_SELECTOR, "button:contains('Sign In')"),
            (By.CSS_SELECTOR, ".login-button"),
            (By.CSS_SELECTOR, ".submit-button"),
            (By.CSS_SELECTOR, "button"),
            (By.CSS_SELECTOR, "input[type='button']")
        ]
        
        for selector_type, selector_value in submit_selectors:
            try:
                submit_button = driver.find_element(selector_type, selector_value)
                print(f"   ✅ Found submit button with {selector_type}: {selector_value}")
                print(f"      Text: '{submit_button.text}'")
                print(f"      Value: '{submit_button.get_attribute('value')}'")
                break
            except:
                continue
        
        if not submit_button:
            print("   ❌ Could not find submit button")
            return
        
        # Try to login
        print("\n🔐 Attempting login...")
        
        username_field.clear()
        username_field.send_keys(username)
        print("   ✅ Entered username")
        
        password_field.clear()
        password_field.send_keys(password)
        print("   ✅ Entered password")
        
        # Try clicking the submit button
        try:
            submit_button.click()
            print("   ✅ Clicked submit button")
        except Exception as e:
            print(f"   ❌ Failed to click submit button: {e}")
            # Try JavaScript click
            try:
                driver.execute_script("arguments[0].click();", submit_button)
                print("   ✅ Clicked submit button via JavaScript")
            except Exception as e2:
                print(f"   ❌ Failed JavaScript click: {e2}")
                return
        
        # Wait and check if login was successful
        time.sleep(5)
        
        print(f"\n📊 Login attempt results:")
        print(f"   Current URL: {driver.current_url}")
        print(f"   Page title: {driver.title}")
        
        if "Dashboard" in driver.current_url or "dashboard" in driver.current_url.lower():
            print("   ✅ Login successful!")
            
            # Save the dashboard page
            with open('dashboard_page_debug.html', 'w', encoding='utf-8') as f:
                f.write(driver.page_source)
            print("   💾 Saved dashboard page HTML to dashboard_page_debug.html")
            
        elif "login" in driver.current_url.lower():
            print("   ❌ Login failed - still on login page")
            
            # Check for error messages
            error_elements = driver.find_elements(By.CSS_SELECTOR, ".error, .alert, .message")
            for error in error_elements:
                if error.text.strip():
                    print(f"   ❌ Error message: {error.text}")
            
        else:
            print("   ⚠️ Login status unclear")
            
            # Save the current page
            with open('login_result_debug.html', 'w', encoding='utf-8') as f:
                f.write(driver.page_source)
            print("   💾 Saved login result HTML to login_result_debug.html")
        
        print(f"\n🎯 LOGIN DEBUG SUMMARY:")
        print(f"   Analyzed login form structure")
        print(f"   Found form elements and tried login")
        print(f"   Check the saved HTML files for detailed analysis")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    debug_login_form() 