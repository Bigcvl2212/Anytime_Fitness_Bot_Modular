"""
ClubOS Messaging Service - PROVEN WORKING CODE FROM ORIGINAL SCRIPT
Contains the EXACT proven messaging functions from Anytime_Bot.py
"""

import time
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

try:
    from ...config.constants import (
        CLUBOS_DASHBOARD_URL,
        CLUBOS_MESSAGES_URL,
        CLUBOS_TEXT_TAB_ID,
        CLUBOS_EMAIL_TAB_ID,
        TEXT_MESSAGE_CHARACTER_LIMIT,
        NOTE_AUTHOR_NAME,
        STAFF_NAMES
    )
except ImportError:
    # Fallback for direct imports
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from config.constants import (
        CLUBOS_DASHBOARD_URL,
        CLUBOS_MESSAGES_URL,
        CLUBOS_TEXT_TAB_ID,
        CLUBOS_EMAIL_TAB_ID,
        TEXT_MESSAGE_CHARACTER_LIMIT,
        NOTE_AUTHOR_NAME,
        STAFF_NAMES
    )


def send_clubos_message(driver, member_name, subject, body):
    """
    A single, robust function to send a message (Text or Email) to a member.
    This version includes automatic email fallback if SMS fails.
    
    PROVEN FUNCTION FROM ORIGINAL ANYTIME_BOT.PY
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


def get_last_message_sender(driver):
    """
    Gets the name of the member from the most recent thread on the messages page.
    
    PROVEN FUNCTION FROM ORIGINAL ANYTIME_BOT.PY
    """
    print(f"INFO: Getting the most recent member to process...")
    try:
        driver.get(CLUBOS_MESSAGES_URL)
        first_message_item = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//li[div[@class='message'] and div[@class='message-options']]"))
        )
        member_name = first_message_item.find_element(By.CSS_SELECTOR, "a.username-content").text.strip()
        print(f"   SUCCESS: Identified top member: {member_name}")
        return member_name
    except Exception as e:
        print(f"ERROR: Could not get last message sender. Error: {e}")
        return None


# Aliases for backward compatibility
get_member_conversation = get_last_message_sender
get_messaging_service = lambda driver: None  # Placeholder
