#!/usr/bin/env python3
"""
Capture the current page structure to understand what elements are available
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

def capture_page_structure():
    username = get_secret('clubos-username')
    password = get_secret('clubos-password')
    
    if not username or not password:
        print("❌ ClubOS credentials not set in secrets_local.py.")
        return

    # Set up Chrome
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    try:
        print("🔍 Starting page structure capture...")
        
        # Navigate to ClubOS login
        print("📱 Navigating to ClubOS login...")
        driver.get("https://clubos.com/login")
        time.sleep(5)
        
        # Handle login form
        print("🔐 Attempting login...")
        wait = WebDriverWait(driver, 15)
        
        try:
            username_field = wait.until(EC.presence_of_element_located((By.NAME, "username")))
            username_field.clear()
            username_field.send_keys(username)
            
            password_field = driver.find_element(By.NAME, "password")
            password_field.clear()
            password_field.send_keys(password)
            
            login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_button.click()
            
            print("✅ Login submitted")
            time.sleep(5)
            
        except Exception as e:
            print(f"❌ Login failed: {e}")
            return
        
        # Navigate to search
        print("🔍 Navigating to member search...")
        driver.get("https://clubos.com/action/Dashboard/search")
        time.sleep(5)
        
        # Search for Jeremy Mayo
        print("🔍 Searching for Jeremy Mayo...")
        try:
            search_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder*='search'], input[type='text']")))
            search_input.clear()
            search_input.send_keys("Jeremy Mayo")
            search_input.submit()
            time.sleep(5)
        except Exception as e:
            print(f"❌ Search failed: {e}")
            return
        
        # Click on Jeremy Mayo's profile
        print("👤 Looking for Jeremy Mayo's profile...")
        try:
            jeremy_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Jeremy Mayo')]")))
            jeremy_link.click()
            time.sleep(5)
        except Exception as e:
            print(f"❌ Jeremy Mayo link not found: {e}")
            # Try alternative approach
            links = driver.find_elements(By.XPATH, "//a[contains(text(), 'Jeremy') or contains(text(), 'Mayo')]")
            if links:
                links[0].click()
                time.sleep(5)
        
        # Look for follow-up button
        print("💬 Looking for follow-up button...")
        try:
            follow_up_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.follow-up")))
            follow_up_button.click()
            time.sleep(5)
        except Exception as e:
            print(f"❌ Follow-up button not found: {e}")
            # Try alternative selectors
            selectors = ["a.follow-up", "button.follow-up", ".follow-up", "a[href*='follow']"]
            for selector in selectors:
                try:
                    button = driver.find_element(By.CSS_SELECTOR, selector)
                    button.click()
                    time.sleep(5)
                    print(f"✅ Found and clicked button with selector: {selector}")
                    break
                except Exception:
                    continue
        
        # Capture current page structure
        print("📋 Capturing page structure...")
        page_source = driver.page_source
        
        # Save the page source
        with open("current_page_structure.html", "w", encoding="utf-8") as f:
            f.write(page_source)
        print("💾 Saved page structure to current_page_structure.html")
        
        # Analyze the page structure
        print("🔍 Analyzing page structure...")
        
        # Look for all form elements
        forms = driver.find_elements(By.TAG_NAME, "form")
        print(f"📝 Found {len(forms)} form(s)")
        
        # Look for all input elements
        inputs = driver.find_elements(By.TAG_NAME, "input")
        print(f"📝 Found {len(inputs)} input(s)")
        for i, inp in enumerate(inputs):
            try:
                name = inp.get_attribute("name") or "no-name"
                type_attr = inp.get_attribute("type") or "no-type"
                value = inp.get_attribute("value") or "no-value"
                print(f"  Input {i+1}: name='{name}', type='{type_attr}', value='{value[:50]}...'")
            except Exception as e:
                print(f"  Input {i+1}: Error getting attributes - {e}")
        
        # Look for all textarea elements
        textareas = driver.find_elements(By.TAG_NAME, "textarea")
        print(f"📝 Found {len(textareas)} textarea(s)")
        for i, ta in enumerate(textareas):
            try:
                name = ta.get_attribute("name") or "no-name"
                value = ta.get_attribute("value") or "no-value"
                print(f"  Textarea {i+1}: name='{name}', value='{value[:50]}...'")
            except Exception as e:
                print(f"  Textarea {i+1}: Error getting attributes - {e}")
        
        # Look for all button elements
        buttons = driver.find_elements(By.TAG_NAME, "button")
        print(f"📝 Found {len(buttons)} button(s)")
        for i, btn in enumerate(buttons):
            try:
                text = btn.text or "no-text"
                type_attr = btn.get_attribute("type") or "no-type"
                print(f"  Button {i+1}: text='{text[:50]}...', type='{type_attr}'")
            except Exception as e:
                print(f"  Button {i+1}: Error getting attributes - {e}")
        
        # Look for all anchor elements
        anchors = driver.find_elements(By.TAG_NAME, "a")
        print(f"📝 Found {len(anchors)} anchor(s)")
        for i, a in enumerate(anchors):
            try:
                text = a.text or "no-text"
                href = a.get_attribute("href") or "no-href"
                print(f"  Anchor {i+1}: text='{text[:50]}...', href='{href[:50]}...'")
            except Exception as e:
                print(f"  Anchor {i+1}: Error getting attributes - {e}")
        
        print("🔍 Page structure analysis completed.")
        
    except Exception as e:
        print(f"❌ Error during capture: {e}")
        driver.save_screenshot("capture_error.png")
        print("📸 Screenshot saved as capture_error.png")
    
    finally:
        driver.quit()

if __name__ == "__main__":
    capture_page_structure() 