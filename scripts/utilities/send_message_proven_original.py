#!/usr/bin/env python3
"""
Use the exact proven messaging function from the original Anytime_Bot.py
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from config.secrets_local import get_secret

# Constants from the original script
CLUBOS_DASHBOARD_URL = "https://anytime.club-os.com/action/Dashboard/view"
CLUBOS_TEXT_TAB_ID = "text-tab"
CLUBOS_EMAIL_TAB_ID = "email-tab"
TEXT_MESSAGE_CHARACTER_LIMIT = 300
NOTE_AUTHOR_NAME = "Gym Bot"

TARGET_NAME = "Jeremy Mayo"
SMS_MESSAGE = "Proven original SMS test - this should definitely work!"
EMAIL_MESSAGE = "Proven original email test - this should definitely work!"

def setup_driver_and_login():
    """Setup Chrome driver and login to Club OS - EXACT FROM ORIGINAL"""
    driver = None
    try:
        username = get_secret('clubos-username')
        password = get_secret('clubos-password')
        
        if not username or not password:
            print("ERROR: Missing ClubOS credentials")
            return None
        
        print("INFO: Initializing WebDriver...")
        options = Options()
        options.add_argument("--start-maximized")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        driver = webdriver.Chrome(options=options)
        
        # Hide webdriver properties
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        print("INFO: Attempting Club OS login...")
        driver.get("https://anytime.club-os.com/action/Login")
        time.sleep(3)
        
        print("   INFO: Filling login credentials...")
        username_field = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.NAME, "username"))
        )
        username_field.send_keys(username)
        
        password_field = driver.find_element(By.NAME, "password")
        password_field.send_keys(password)
        
        login_button = driver.find_element(By.CLASS_NAME, "js-login")
        login_button.click()
        
        print("   INFO: Waiting for login to complete...")
        WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.ID, "quick-search-text")))
        print("SUCCESS: Club OS login complete.")
        return driver
    except Exception as e:
        print(f"CRITICAL: Login failed. Error: {e}")
        if driver: 
            driver.quit()
        return None

def send_clubos_message(driver, member_name, subject, body):
    """
    A single, robust function to send a message (Text or Email) to a member.
    This version includes automatic email fallback if SMS fails.
    EXACT COPY FROM ORIGINAL ANYTIME_BOT.PY
    """
    print(f"INFO: Preparing to send message to '{member_name}'...")
    try:
        driver.get(CLUBOS_DASHBOARD_URL)
        search_box = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "quick-search-text")))
        search_box.clear()
        search_box.send_keys(member_name)
        time.sleep(3.5)
        
        contact_result_xpath = f"//h4[normalize-space(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'))='{member_name.lower()}']"
        WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, contact_result_xpath))).click()
        
        print("   INFO: Applying zoom to profile page...")
        driver.execute_script("document.body.style.zoom='75%'")
        time.sleep(1)

        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[data-original-title='Send Message']"))).click()
        print("   SUCCESS: Opened message popup.")
        
        # --- CRITICAL FIX: Add a patient wait for the popup contents to stabilize ---
        print("   INFO: Waiting for popup contents to load...")
        time.sleep(3) # A 3-second patient wait

        # --- Check for available communication channels ---
        text_tab_present_and_clickable = False
        email_tab_present_and_clickable = False
        text_tab = None
        email_tab = None
        
        try:
            text_tab = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.ID, CLUBOS_TEXT_TAB_ID)))
            if text_tab.is_displayed(): 
                text_tab_present_and_clickable = True
                print("   INFO: Text tab available")
        except TimeoutException:
            print(f"   INFO: Text tab (ID '{CLUBOS_TEXT_TAB_ID}') not found or not clickable.")

        try:
            email_tab = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.ID, CLUBOS_EMAIL_TAB_ID)))
            if email_tab.is_displayed(): 
                email_tab_present_and_clickable = True
                print("   INFO: Email tab available")
        except TimeoutException:
            print(f"   INFO: Email tab (ID '{CLUBOS_EMAIL_TAB_ID}') not found or not clickable.")

        if not text_tab_present_and_clickable and not email_tab_present_and_clickable:
            print(f"   WARN: No communication channels (Text/Email tabs) available for {member_name}. Member has opted out.")
            try:
                WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.header-close-button.close-button"))).click()
            except: pass
            return "OPTED_OUT"

        # Determine sending method - try SMS first if message is short and SMS is available
        use_email = False
        fallback_reason = ""
        
        if len(body) >= TEXT_MESSAGE_CHARACTER_LIMIT:
            use_email = True
            fallback_reason = f"Message too long for SMS ({len(body)} chars)"
        elif not text_tab_present_and_clickable:
            use_email = True
            fallback_reason = "SMS not available (likely opted out)"
        
        # First attempt: Try SMS if conditions allow
        if not use_email and text_tab_present_and_clickable:
            try:
                print("   INFO: Attempting to send as TEXT message...")
                text_tab.click()
                
                text_area = WebDriverWait(driver, 8).until(EC.element_to_be_clickable((By.NAME, "textMessage")))
                text_area.clear()
                text_area.send_keys(body)
                
                notes_field = driver.find_element(By.NAME, "followUpOutcomeNotes")
                notes_field.clear()
                notes_field.send_keys(f"Auto-SMS sent by {NOTE_AUTHOR_NAME}")
                
                print(f"   ACTION: Sending SMS to {member_name}...")
                send_button_element = driver.find_element(By.CSS_SELECTOR, "a.save-follow-up")
                driver.execute_script("arguments[0].click();", send_button_element)
                
                # Wait for popup to close with shorter timeout for SMS
                print("   INFO: Waiting for SMS popup to close (up to 10 seconds)...")
                WebDriverWait(driver, 10).until(
                    EC.invisibility_of_element_located((By.ID, "followup-popup-content"))
                )
                print(f"   SUCCESS: SMS sent and popup closed for {member_name}.")
                return True
                
            except TimeoutException:
                print(f"   WARN: SMS send timed out for {member_name}. Attempting email fallback...")
                use_email = True
                fallback_reason = "SMS timed out"
                # Don't return here, continue to email fallback
                
            except Exception as sms_error:
                print(f"   WARN: SMS send failed for {member_name}: {sms_error}. Attempting email fallback...")
                use_email = True
                fallback_reason = f"SMS error: {sms_error}"
                # Don't return here, continue to email fallback

        # Email fallback attempt
        if use_email and email_tab_present_and_clickable:
            try:
                print(f"   INFO: Sending as EMAIL ({fallback_reason})...")
                
                # Re-open popup if it closed during SMS attempt
                try:
                    popup = driver.find_element(By.ID, "followup-popup-content")
                    if not popup.is_displayed():
                        print("   INFO: Re-opening message popup for email fallback...")
                        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[data-original-title='Send Message']"))).click()
                        time.sleep(2)
                except:
                    # Popup might already be open, continue
                    pass
                
                email_tab = WebDriverWait(driver, 8).until(EC.element_to_be_clickable((By.ID, CLUBOS_EMAIL_TAB_ID)))
                email_tab.click()
                
                subject_field = driver.find_element(By.NAME, "emailSubject")
                subject_field.clear()
                subject_field.send_keys(subject)
                
                email_body_editor = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.redactor_editor")))
                driver.execute_script("arguments[0].innerHTML = arguments[1];", email_body_editor, body)
                
                notes_field = driver.find_element(By.NAME, "followUpOutcomeNotes")
                notes_field.clear()
                notes_field.send_keys(f"Auto-email sent by {NOTE_AUTHOR_NAME} ({fallback_reason})")
                
                print(f"   ACTION: Sending EMAIL to {member_name}...")
                send_button_element = driver.find_element(By.CSS_SELECTOR, "a.save-follow-up")
                driver.execute_script("arguments[0].click();", send_button_element)
                
                print("   INFO: Waiting for email popup to close (up to 20 seconds)...")
                WebDriverWait(driver, 20).until(
                    EC.invisibility_of_element_located((By.ID, "followup-popup-content"))
                )
                print(f"   SUCCESS: Email sent and popup closed for {member_name}.")
                return True
                
            except Exception as email_error:
                print(f"   ERROR: Email fallback also failed for {member_name}: {email_error}")
                # Continue to cleanup and return failure
        
        # If we get here, both SMS and email failed or weren't available
        if not email_tab_present_and_clickable:
            print(f"   ERROR: No email option available for {member_name} after SMS failure.")
            return "OPTED_OUT"
        else:
            print(f"   ERROR: Both SMS and email attempts failed for {member_name}.")
            return False
    except TimeoutException as te:
        print(f"   WARN: Overall timeout occurred during message sending for {member_name}. Error: {te}")
        # Attempt to close popup if still open
        try:
            if driver.find_element(By.ID, "followup-popup-content").is_displayed():
                WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.header-close-button.close-button"))).click()
        except: pass
        return False
    except Exception as e:
        print(f"   ERROR: Failed to send Club OS message to {member_name}. Error: {type(e).__name__} - {e}")
        try:
            if driver.find_elements(By.TAG_NAME, "iframe"): 
                driver.switch_to.default_content()
            # Attempt to close popup if still open
            if driver.find_element(By.ID, "followup-popup-content").is_displayed():
                WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.header-close-button.close-button"))).click()
        except: pass
        return False

def send_message_proven_original():
    """Send messages using the exact proven function from original Anytime_Bot.py"""
    try:
        print("🔐 Setting up driver and logging into ClubOS...")
        
        # Use the exact proven driver setup function
        driver = setup_driver_and_login()
        
        if not driver:
            print("❌ Failed to setup driver and login")
            return
        
        print("✅ Driver setup and login successful!")
        
        # Send SMS using the exact proven messaging function
        print(f"\n📤 Sending SMS to {TARGET_NAME} using proven original function...")
        sms_result = send_clubos_message(driver, TARGET_NAME, "Proven Original SMS Test", SMS_MESSAGE)
        
        if sms_result == True:
            print("✅ SMS sent successfully using proven original function!")
        elif sms_result == "OPTED_OUT":
            print("⚠️ Member has opted out of SMS")
        else:
            print(f"❌ SMS failed: {sms_result}")
        
        # Send Email using the exact proven messaging function
        print(f"\n📤 Sending Email to {TARGET_NAME} using proven original function...")
        email_result = send_clubos_message(driver, TARGET_NAME, "Proven Original Email Test", EMAIL_MESSAGE)
        
        if email_result == True:
            print("✅ Email sent successfully using proven original function!")
        elif email_result == "OPTED_OUT":
            print("⚠️ Member has opted out of Email")
        else:
            print(f"❌ Email failed: {email_result}")
        
        # Summary
        print(f"\n📊 Proven Original Results Summary:")
        print(f"   SMS: {'✅ Success' if sms_result == True else '❌ Failed' if sms_result == False else f'⚠️ {sms_result}'}")
        print(f"   Email: {'✅ Success' if email_result == True else '❌ Failed' if email_result == False else f'⚠️ {email_result}'}")
        
        if sms_result == True or email_result == True:
            print("\n🎉 At least one message was sent successfully using the proven original function!")
        else:
            print("\n⚠️ No messages were delivered using the proven original function.")
            
    except Exception as e:
        print(f"❌ Error during proven original messaging: {e}")
    
    finally:
        try:
            if driver:
                driver.quit()
        except:
            pass

if __name__ == "__main__":
    send_message_proven_original() 