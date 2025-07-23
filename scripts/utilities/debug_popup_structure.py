#!/usr/bin/env python3
"""
Debug the popup structure to find the correct messaging elements
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

def debug_popup_structure():
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
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--allow-running-insecure-content")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(options=chrome_options)
    
    # Remove automation indicators
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    try:
        print("🔐 Logging into ClubOS...")
        
        # Go to login page
        driver.get("https://anytime.club-os.com/action/Login")
        time.sleep(3)
        
        # Wait for the login form to be present
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "loginForm"))
        )
        
        # Find the username and password fields
        username_field = driver.find_element(By.NAME, "username")
        password_field = driver.find_element(By.NAME, "password")
        
        # Clear and fill the fields
        username_field.clear()
        username_field.send_keys(username)
        password_field.clear()
        password_field.send_keys(password)
        
        # Find the login button
        login_button = driver.find_element(By.CSS_SELECTOR, "button.js-login")
        login_button.click()
        
        # Wait for login to complete
        time.sleep(5)
        
        # Check if login was successful
        if "Dashboard" in driver.current_url or "dashboard" in driver.current_url.lower():
            print("✅ Login successful!")
            
            # Go to dashboard
            driver.get("https://anytime.club-os.com/action/Dashboard/view")
            time.sleep(3)
            
            # Search for Jeremy Mayo
            print("🔍 Searching for Jeremy Mayo...")
            search_box = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.ID, "quick-search-text"))
            )
            search_box.clear()
            search_box.send_keys("Jeremy Mayo")
            time.sleep(4)
            
            # Click on the search result
            contact_result_xpath = "//h4[normalize-space(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'))='jeremy mayo']"
            WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, contact_result_xpath))
            ).click()
            
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
            
            # Save the popup HTML for analysis
            with open('popup_debug.html', 'w', encoding='utf-8') as f:
                f.write(driver.page_source)
            print("💾 Saved popup HTML to popup_debug.html")
            
            # Debug the popup structure
            print("\n🔍 Analyzing popup structure...")
            
            # Find all elements in the popup
            try:
                popup_content = driver.find_element(By.ID, "followup-popup-content")
                print("   ✅ Found popup content")
                
                # Find all tabs
                tabs = popup_content.find_elements(By.CSS_SELECTOR, "[role='tab'], .tab, .nav-tabs li")
                print(f"   Found {len(tabs)} potential tabs")
                
                for i, tab in enumerate(tabs):
                    print(f"   Tab {i+1}: text='{tab.text}', class='{tab.get_attribute('class')}', id='{tab.get_attribute('id')}'")
                
                # Find all buttons
                buttons = popup_content.find_elements(By.CSS_SELECTOR, "button, a.btn, input[type='submit']")
                print(f"\n   Found {len(buttons)} potential buttons")
                
                for i, button in enumerate(buttons):
                    print(f"   Button {i+1}: text='{button.text}', class='{button.get_attribute('class')}', id='{button.get_attribute('id')}'")
                
                # Find all input fields
                inputs = popup_content.find_elements(By.CSS_SELECTOR, "input, textarea")
                print(f"\n   Found {len(inputs)} potential input fields")
                
                for i, input_elem in enumerate(inputs):
                    input_type = input_elem.get_attribute('type')
                    input_name = input_elem.get_attribute('name')
                    input_id = input_elem.get_attribute('id')
                    print(f"   Input {i+1}: type='{input_type}', name='{input_name}', id='{input_id}'")
                
                # Look for specific messaging elements
                print("\n🔍 Looking for messaging-specific elements...")
                
                # Try different selectors for text messaging
                text_selectors = [
                    "#text-tab",
                    ".text-tab",
                    "[data-tab='text']",
                    "a[href*='text']",
                    "button[onclick*='text']"
                ]
                
                for selector in text_selectors:
                    try:
                        element = popup_content.find_element(By.CSS_SELECTOR, selector)
                        print(f"   ✅ Found text element with selector: {selector}")
                        print(f"      Text: '{element.text}'")
                        print(f"      Class: '{element.get_attribute('class')}'")
                    except:
                        continue
                
                # Try different selectors for email messaging
                email_selectors = [
                    "#email-tab",
                    ".email-tab",
                    "[data-tab='email']",
                    "a[href*='email']",
                    "button[onclick*='email']"
                ]
                
                for selector in email_selectors:
                    try:
                        element = popup_content.find_element(By.CSS_SELECTOR, selector)
                        print(f"   ✅ Found email element with selector: {selector}")
                        print(f"      Text: '{element.text}'")
                        print(f"      Class: '{element.get_attribute('class')}'")
                    except:
                        continue
                
                # Look for save/send buttons
                save_selectors = [
                    "a.save-follow-up",
                    "button.save-follow-up",
                    "input[value*='Send']",
                    "button[onclick*='save']",
                    "a[onclick*='save']"
                ]
                
                for selector in save_selectors:
                    try:
                        element = popup_content.find_element(By.CSS_SELECTOR, selector)
                        print(f"   ✅ Found save element with selector: {selector}")
                        print(f"      Text: '{element.text}'")
                        print(f"      Class: '{element.get_attribute('class')}'")
                    except:
                        continue
                
            except Exception as e:
                print(f"   ❌ Error analyzing popup: {e}")
            
            print(f"\n🎯 POPUP DEBUG SUMMARY:")
            print(f"   Analyzed popup structure")
            print(f"   Check popup_debug.html for detailed HTML")
            print(f"   Look for the correct selectors to use")
                
        else:
            print("❌ Login failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    debug_popup_structure() 