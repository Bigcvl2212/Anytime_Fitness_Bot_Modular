"""
ClubOS Proven Messaging Functions
These are the EXACT proven functions from the original Anytime_Bot.py script.
"""

import time
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from ...config.constants import (
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


def scrape_conversation_for_contact(driver, member_name):
    """
    Scrapes the full message history from the popup using the proven flexible iframe logic.
    
    PROVEN FUNCTION FROM ORIGINAL ANYTIME_BOT.PY
    """
    print(f"INFO: Scraping conversation for '{member_name}'...")
    current_step = "Initializing"
    in_iframe = False # Define in_iframe at a broader scope
    try:
        current_step = "Navigating to dashboard"
        driver.get(CLUBOS_DASHBOARD_URL)

        current_step = "Waiting for search box and searching"
        search_box = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "quick-search-text")))
        search_box.clear(); search_box.send_keys(member_name)
        time.sleep(3.5)

        contact_result_xpath = f"//h4[normalize-space(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'))='{member_name.lower()}']"
        current_step = f"Clicking contact result for '{member_name}'"
        print(f"   DEBUG: Attempting to click contact result using XPath: {contact_result_xpath}")
        contact_element = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, contact_result_xpath)))
        contact_element.click()
        print(f"   DEBUG: Clicked contact result. Current URL: {driver.current_url}. Waiting for profile page to settle...")
        time.sleep(2) # Small delay for page to settle after navigation

        send_message_button_selector = "a[data-original-title='Send Message']"
        current_step = f"Waiting for 'Send Message' button to be present and clickable"
        print(f"   DEBUG: Waiting for '{send_message_button_selector}' to be present and clickable...")
        send_message_element = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, send_message_button_selector)))
        send_message_element.click()
        print(f"   DEBUG: Clicked 'Send Message' button. Current URL: {driver.current_url}. Waiting for popup to initialize...")
        time.sleep(1) # Small delay for popup to start appearing

        current_step = "Waiting for followup-popup-content"
        print(f"   DEBUG: Waiting for followup-popup-content to be visible.")
        popup_content = WebDriverWait(driver, 15).until(EC.visibility_of_element_located((By.ID, "followup-popup-content")))
        print(f"   DEBUG: followup-popup-content is visible.")

        current_step = "Checking for iframe"
        try:
            iframe = WebDriverWait(popup_content, 5).until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))
            driver.switch_to.frame(iframe)
            in_iframe = True
            print("   DEBUG: Switched to iframe.")
        except TimeoutException:
            print("   DEBUG: No iframe found in popup, proceeding.")
            pass # No iframe, continue in main content

        current_step = "Locating scroll container"
        scroll_container = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "follow-up-log")))
        
        current_step = "Scrolling messages"
        last_height = -1
        scroll_attempts = 0
        max_scroll_attempts = 15 # Prevent infinite loop, increased slightly
        while scroll_attempts < max_scroll_attempts:
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scroll_container)
            time.sleep(2) # Wait for content to load
            new_height = driver.execute_script("return arguments[0].scrollHeight", scroll_container)
            if new_height == last_height: break
            last_height = new_height
            scroll_attempts += 1
        if scroll_attempts == max_scroll_attempts:
            print("   WARN: Reached max scroll attempts for messages.")

        current_step = "Parsing entries"
        entries = scroll_container.find_elements(By.CSS_SELECTOR, ".followup-entry")
        conversation_history = []
        for entry_index, entry in enumerate(entries):
            current_step = f"Parsing entry {entry_index + 1}/{len(entries)}"
            try:
                entry.find_element(By.CSS_SELECTOR, "img[src*='icon_text.png']")
                author_text = entry.find_element(By.CSS_SELECTOR, ".followup-entry-date").text
                note_element = entry.find_element(By.CSS_SELECTOR, ".followup-entry-note")
                note_text = driver.execute_script("var element = arguments[0].cloneNode(true); var img = element.querySelector('img'); if (img) img.remove(); return element.textContent.trim();", note_element)
                author_name = author_text.split('by ')[-1].strip()
                sender = "Member" if author_name not in STAFF_NAMES else "Gym-Bot"
                if note_text: conversation_history.append({"sender": sender, "text": note_text})
            except NoSuchElementException: continue
        
        print(f"   SUCCESS: Parsed {len(conversation_history)} text messages.")
        if in_iframe: driver.switch_to.default_content()
        return list(reversed(conversation_history))

    except TimeoutException as te:
        print(f"   ERROR: TimeoutException during conversation scraping at step '{current_step}'. Error: {te}")
        if in_iframe: driver.switch_to.default_content()
        return []
    except Exception as e:
        print(f"   ERROR: An unexpected error ({type(e).__name__}) occurred during conversation scraping at step '{current_step}'. Error: {e}")
        if in_iframe: driver.switch_to.default_content()
        return []
