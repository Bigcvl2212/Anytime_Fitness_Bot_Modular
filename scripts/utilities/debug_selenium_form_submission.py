#!/usr/bin/env python3
"""
Use Selenium to capture the exact form submission when clicking "Send Message"
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
import json

TARGET_NAME = "Jeremy Mayo"

def capture_form_submission():
    username = get_secret('clubos-username')
    password = get_secret('clubos-password')
    
    if not username or not password:
        print("❌ ClubOS credentials not set in secrets_local.py.")
        return

    # Set up Chrome with network logging
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # Enable network logging
    chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        print("🔐 Logging into ClubOS via Selenium...")
        
        # Login
        driver.get("https://anytime.club-os.com/action/Login")
        
        username_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "username")))
        password_field = driver.find_element(By.NAME, "password")
        
        username_field.send_keys(username)
        password_field.send_keys(password)
        
        # Find and click login button
        login_button = driver.find_element(By.CSS_SELECTOR, "input[type='submit']")
        login_button.click()
        
        # Wait for login to complete
        WebDriverWait(driver, 10).until(EC.url_contains("Dashboard"))
        print("✅ Login successful!")
        
        # Go to dashboard
        driver.get("https://anytime.club-os.com/action/Dashboard/view")
        time.sleep(2)
        
        # Search for Jeremy Mayo
        print(f"🔍 Searching for {TARGET_NAME}...")
        search_box = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "quick-search-text")))
        search_box.clear()
        search_box.send_keys(TARGET_NAME)
        time.sleep(3.5)
        
        # Click on the search result
        contact_result_xpath = f"//h4[normalize-space(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'))='{TARGET_NAME.lower()}']"
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, contact_result_xpath))).click()
        
        print("✅ Clicked on member profile")
        time.sleep(2)
        
        # Clear previous logs
        driver.get_log('performance')
        
        # Click "Send Message" button
        print("📤 Clicking 'Send Message' button...")
        send_message_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a[data-original-title='Send Message']"))
        )
        send_message_button.click()
        
        print("✅ Opened message popup")
        time.sleep(3)
        
        # Fill in SMS message
        print("📝 Filling SMS message...")
        text_area = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "textMessage")))
        text_area.clear()
        text_area.send_keys("Test SMS via Selenium form capture")
        
        # Fill notes
        notes_field = driver.find_element(By.NAME, "followUpOutcomeNotes")
        notes_field.clear()
        notes_field.send_keys("Selenium form capture test")
        
        # Capture network logs before clicking send
        print("📊 Capturing network logs...")
        logs = driver.get_log('performance')
        
        # Click send button
        print("🚀 Clicking send button...")
        send_button = driver.find_element(By.CSS_SELECTOR, "a.save-follow-up")
        send_button.click()
        
        # Wait a moment for the request to complete
        time.sleep(5)
        
        # Get final logs
        final_logs = driver.get_log('performance')
        
        print(f"📊 Captured {len(final_logs)} network events")
        
        # Analyze the logs to find the form submission
        form_submissions = []
        for log in final_logs:
            try:
                log_entry = json.loads(log['message'])
                if 'message' in log_entry and log_entry['message']['method'] == 'Network.requestWillBeSent':
                    request = log_entry['message']['params']['request']
                    if request['method'] == 'POST':
                        url = request['url']
                        if 'follow' in url.lower() or 'message' in url.lower() or 'send' in url.lower():
                            form_submissions.append({
                                'url': url,
                                'method': request['method'],
                                'headers': request['headers'],
                                'postData': request.get('postData', '')
                            })
                            print(f"🔍 Found form submission to: {url}")
                            print(f"   Method: {request['method']}")
                            print(f"   Headers: {request['headers']}")
                            print(f"   Post Data: {request.get('postData', '')}")
            except Exception as e:
                continue
        
        if form_submissions:
            print(f"\n✅ Captured {len(form_submissions)} form submissions!")
            print("Use this information to replicate the API calls.")
        else:
            print("❌ No form submissions captured. The popup might not have submitted via AJAX.")
        
        # Also try to capture the form HTML
        try:
            popup = driver.find_element(By.ID, "followup-popup-content")
            form_html = popup.get_attribute('innerHTML')
            with open('captured_form.html', 'w', encoding='utf-8') as f:
                f.write(form_html)
            print("💾 Saved form HTML to captured_form.html")
        except Exception as e:
            print(f"⚠️ Could not capture form HTML: {e}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    capture_form_submission() 