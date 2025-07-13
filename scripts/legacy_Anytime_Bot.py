import os
import sys
import time
import re
import json
import random
import argparse
import traceback
import pandas as pd
import requests
import google.generativeai as genai
from datetime import datetime, timedelta, timezone
from dateutil.parser import parse as parse_date
from dateutil.relativedelta import relativedelta

# Selenium & Webdriver Manager
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService

# Google Cloud & AI Libraries
from google.cloud import secretmanager
import google.generativeai as genai
from google.cloud import firestore

# Flask for web server
from flask import Flask, request

# Square Payment Integration
import squareup
from squareup import Client as SquareClient

import inspect
import requests

# --- CONSTANTS AND CONFIGURATION ---
STAFF_NAMES = ["Gym-Bot AI", "Jeremy", "Staff"]  # Names to identify staff messages
CLUBOS_TEXT_TAB_ID = "text-tab"  # ID for text message tab in Club OS
CLUBOS_EMAIL_TAB_ID = "email-tab"  # ID for email tab in Club OS

# Club Hub API Configuration (placeholders)
CLUBHUB_API_URL_MEMBERS = "https://api.placeholder.com/members"
CLUBHUB_API_URL_PROSPECTS = "https://api.placeholder.com/prospects"
CLUBHUB_HEADERS = {"Authorization": "Bearer YOUR_API_KEY"}
PARAMS_FOR_MEMBERS_RECENT = {"recent": True}
PARAMS_FOR_PROSPECTS_RECENT = {"recent": True}

# =============================================================================
# SQUARE PAYMENT INTEGRATION CONFIGURATION
# =============================================================================

# Square API Configuration
SQUARE_ENVIRONMENT = os.getenv('SQUARE_ENVIRONMENT', 'sandbox')  # 'sandbox' or 'production'

# Square API Secret Names (stored in Google Secret Manager)
SQUARE_SANDBOX_ACCESS_TOKEN_SECRET = "square-sandbox-access-token"
SQUARE_SANDBOX_APPLICATION_ID_SECRET = "square-sandbox-application-id" 
SQUARE_SANDBOX_APPLICATION_SECRET_SECRET = "square-sandbox-application-secret"

SQUARE_PRODUCTION_ACCESS_TOKEN_SECRET = "square-production-access-token"
SQUARE_PRODUCTION_APPLICATION_ID_SECRET = "square-production-application-id"
SQUARE_PRODUCTION_APPLICATION_SECRET_SECRET = "square-production-application-secret"

SQUARE_LOCATION_ID_SECRET = "square-location-id"

# --- DEBUG FUNCTIONS ---
def debug_page_state(driver, debug_name):
    """
    Captures comprehensive page state for debugging - HTML, screenshot, and filter analysis.
    Returns paths to created debug files for immediate analysis.
    """
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        base_filename = f"debug_{debug_name}_{timestamp}"
        
        results = {
            'timestamp': timestamp,
            'page_source_file': None,
            'screenshot_file': None,
            'filter_analysis_file': None,
            'filter_candidates': []
        }
        
        # 1. Save page source HTML
        try:
            page_source_file = f"{base_filename}_page_source.html"
            with open(page_source_file, 'w', encoding='utf-8') as f:
                f.write(driver.page_source)
            results['page_source_file'] = page_source_file
            print(f"   [FILE] Page source saved: {page_source_file}")
        except Exception as e:
            print(f"   WARN: Could not save page source: {e}")
        
        # 2. Take screenshot
        try:
            screenshot_file = f"{base_filename}_screenshot.png"
            driver.save_screenshot(screenshot_file)
            results['screenshot_file'] = screenshot_file
            print(f"   [SCREENSHOT] Screenshot saved: {screenshot_file}")
        except Exception as e:
            print(f"   WARN: Could not save screenshot: {e}")
        
        # 3. Analyze filter elements specifically
        try:
            analysis_file = f"{base_filename}_filter_analysis.txt"
            filter_candidates = []
            
            # Find all potential filter elements
            potential_filters = driver.find_elements(By.CSS_SELECTOR, "select, button, input, [role='button'], [role='combobox']")
            
            with open(analysis_file, 'w', encoding='utf-8') as f:
                f.write(f"FILTER ANALYSIS - {debug_name}\n")
                f.write(f"Timestamp: {timestamp}\n")
                f.write(f"Current URL: {driver.current_url}\n")
                f.write(f"Page Title: {driver.title}\n")
                f.write("="*80 + "\n\n")
                
                f.write(f"Found {len(potential_filters)} potential filter elements:\n\n")
                
                for i, element in enumerate(potential_filters, 1):
                    try:
                        tag_name = element.tag_name
                        element_id = element.get_attribute('id') or 'NO_ID'
                        element_class = element.get_attribute('class') or 'NO_CLASS'
                        element_text = element.text[:50] or 'NO_TEXT'
                        is_displayed = element.is_displayed()
                        is_enabled = element.is_enabled()
                        
                        candidate_info = {
                            'index': i,
                            'element': tag_name,
                            'id': element_id,
                            'class': element_class,
                            'text': element_text,
                            'visible': is_displayed,
                            'enabled': is_enabled
                        }
                        filter_candidates.append(candidate_info)
                        
                        f.write(f"{i:3d}. {tag_name.upper()}\n")
                        f.write(f"     ID: {element_id}\n")
                        f.write(f"     Class: {element_class}\n")
                        f.write(f"     Text: {element_text}\n")
                        f.write(f"     Visible: {is_displayed}, Enabled: {is_enabled}\n")
                        f.write(f"     Location: {element.location}\n")
                        f.write("-" * 40 + "\n")
                        
                    except Exception as elem_error:
                        f.write(f"{i:3d}. ERROR analyzing element: {elem_error}\n")
                        f.write("-" * 40 + "\n")
                
                # Look specifically for training filter IDs
                f.write("\n" + "="*80 + "\n")
                f.write("SPECIFIC TRAINING FILTER SEARCH:\n\n")
                
                target_ids = [
                    "personal-training-filters-location-select-select-select",
                    "personal-training-filters-employee-select-select-select", 
                    "button-apply-filter"
                ]
                
                for target_id in target_ids:
                    try:
                        element = driver.find_element(By.ID, target_id)
                        f.write(f"[FOUND] FOUND: {target_id}\n")
                        f.write(f"   Visible: {element.is_displayed()}\n")
                        f.write(f"   Enabled: {element.is_enabled()}\n")
                        f.write(f"   Location: {element.location}\n")
                        f.write(f"   Size: {element.size}\n")
                        f.write(f"   Text: {element.text}\n")
                    except NoSuchElementException:
                        f.write(f"[NOT FOUND] NOT FOUND: {target_id}\n")
                    f.write("\n")
            
            results['filter_analysis_file'] = analysis_file
            results['filter_candidates'] = filter_candidates
            print(f"   [ANALYSIS] Filter analysis saved: {analysis_file}")
            
        except Exception as e:
            print(f"   WARN: Could not complete filter analysis: {e}")
        
        return results
        
    except Exception as e:
        print(f"   ERROR: Debug capture failed: {e}")
        return None

# --- CONFIGURATION ---
GCP_PROJECT_ID = "round-device-460522-g8"
GEMINI_API_KEY_SECRET = "gemini-api-key"
CLUBOS_USERNAME_SECRET = "clubos-username"
CLUBOS_PASSWORD_SECRET = "clubos-password"
CLUBOS_TEXT_TAB_ID = "3"
CLUBOS_EMAIL_TAB_ID = "2"
STAFF_NAMES = ["Jeremy M.", "Linda D.", "Kayla M.", "System I.", "Leticia E.", "Noah T.", "James A."]
CLUBHUB_API_URL_MEMBERS = "https://clubhub-ios-api.anytimefitness.com/api/clubs/1156/members" 
CLUBHUB_API_URL_PROSPECTS = "https://clubhub-ios-api.anytimefitness.com/api/clubs/1156/prospects"
CLUBHUB_HEADERS = {
    "Host": "clubhub-ios-api.anytimefitness.com",
    "Cookie": "dtCookie=v_4_srv_8_sn_263A8A87967FBF7A4710B4E5362A4465_perc_100000_ol_0_mul_1_app-3Aea7c4b59f27d43eb_0_rcs-3Acss_0; incap_ses_132_434694=vxEzaqJV3iLp+QSwUfXUAXjsUmgAAAAATTfXoc+H3lcFABfyHTyBMw==; visid_incap_434694=RnkdTm5oTZGIHQp7qeKPZANjSGgAAAAAQUIPAAAAAADfxJ4/rmakILSU3890u2w3; _ga_E3V4XR2W24=GS2.1.s1748029777$o2$g1$t1748029958$j0$l0$h0; rl_anonymous_id=RS_ENC_v3_IjQ4N2UyYTBkLTQ3NjItNDRhYy04ZDVkLTQ5ZWJjM2M1MWMyYSI%3D; rl_page_init_referrer=RS_ENC_v3_Imh0dHBzOi8vcmVzb3VyY2VjZW50ZXIuc2VicmFuZHMuY29tLyI%3D; rl_page_init_referring_domain=RS_ENC_v3_InJlc291cmNlY2VudGVyLnNlYnJhbmRzLmNvbSI%3D; rl_session=RS_ENC_v3_eyJpZCI6MTc0ODAyOTc3ODU1MiwiZXhwaXJlc0F0IjoxNzQ4MDMxNTc4NTYxLCJ0aW1lb3V0IjoxODAwMDAwLCJhdXRvVHJhY2siOnRydWUsInNlc3Npb25TdGFydCI6dHJ1ZX0%3D; _ga=GA1.1.2023145946.1747779026; visid_incap_498134=n71aHYAISneGZ49qOGxwdM39LGgAAAAAQUIPAAAAAABKTx/MOoTZK3A95JgTilNy", 
    "API-version": "1",
    "Accept": "application/json",
    "User-Agent": "ClubHub Store/2.15.0 (com.anytimefitness.Club-Hub; build:1004; iOS 18.5.0) Alamofire/5.6.4",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMDgyMDQ0OSIsImVtYWlsIjoibWF5by5qZXJlbXkyMjEyQGdtYWlsLmNvbSIsImdpdmVuX25hbWUiOiJKZXJlbXkiLCJhZl9hcGlfdG9rZW4iOiJCV1dLNWZfM053VkphV25CUDN5OEUtQ1ZHNHlfcWRnMG14SE5OVG5OVmptX1pvbFVnajZCWTRXMUhJcHZlZEFDZGpoTkQxMTBkSk05VWJRU05DUko2OWNZMGxOMWs2TXdmWkVWYXp4V3I4bVFOXzJwODVNSzRVUlh4ZWNkTEh3N2s0dGhRejJYcXlvUTlNdklmb0RFTVFKVkV1a2M2THlGbk12akJNc2RXWXF0a2JqOWZHUjJLbnRuVzRjdHpuSXRnQnkxNzBFbzhtbHdUWnJ4bFBmc1J5VlRoZkpHNjI2c1FQeTJNbjNMTzFBRTZLdVU3aU1IUWppRkk4T3lPaURaQ1VPU01rYWt6aGtYQ1dEb0twakZlZEtYVEI1Vlo1YnU4UGJkSThpV2tDaVpfMHlmbjI0WEZyTlY4V3VEbzRySTRXeXBHN3BYRGQ5OG4ycC1WN1oxMXgxMFdsMCIsInBob3RvX3VybCI6IiIsInVzZXJfdHlwZSI6IlRyYWluZXIiLCJjbHViX2lkcyI6WyIxMTU2IiwiMTY1NyJdLCJyb2xlIjoiVHJhaW5lciIsImFwcGxpY2F0aW9uX2lkcyI6WyIxIiwiMyIsIjgiLCIxMiJdLCJuYmYiOjE3NTAyNjQ5NTMsImV4cCI6MTc1MDM1MTM1MywiaWF0IjoxNzUwMjY0OTUzLCJpc3MiOiJodHRwczovL2NsdWJodWItaW9zLWFwaS5hbnl0aW1lZml0bmVzcy5jb20vIiwiYXVkIjoiQ2x1Ykh1Yklvc0FwaSJ9.GKpG1A8OG9mrwUCGqx7cqe8JPjG9D1_d_laWlXvPHmg", 
    "Accept-Language": "en-US",
    "Accept-Encoding": "br;q=1.0, gzip;q=0.9, deflate;q=0.8"
}
PARAMS_FOR_HISTORICAL_PULL = { "days": "4000", "page": "1", "pageSize": "50" } 
PARAMS_FOR_MEMBERS_RECENT = { "days": "30", "page": "1", "pageSize": "50" } 
PARAMS_FOR_PROSPECTS_RECENT = { "days": "14", "page": "1", "pageSize": "50" }  
# --- CAMPAIGN MESSAGE TEMPLATES ---
# Edit these messages to control what the daily campaign sends
MESSAGE_TEMPLATES = {
    "Prospect": "Everything for $99/mo! Group training, gym access, nutrition coaching, unlimited body scans during staff hours, free swimming at Comfort Inn—plus HSA/FSA accepted and refer a friend = 1 free month, no limits! Let’s go, Fond du Lac!.",
    "PPV": "Everything for $99/mo! Group training, gym access, nutrition coaching, unlimited body scans during staff hours, free swimming at Comfort Inn—plus HSA/FSA accepted and refer a friend = 1 free month, no limits! Let’s go, Fond du Lac!.",
    "YellowList": "Hey just letting you know that you missed your gym payment and the gym will be locked for you until you pay your account current or enter into a payment plan with me. You have 7 days to respond to this message or your account will be flagged and sent to collections.",
    "RedList": "Hey just letting you know that you missed your gym payment and the gym will be locked for you until you pay your account current or enter into a payment plan with me. You have 7 days to respond to this message or your account will be flagged and sent to collections."
}

# --- BUSINESS POLICIES FOR AI ---
POLICIES = """
- **Cancellation Policy:**
  - If member is under contract: They must call Abc Financial at 501-515-5000, pay their Early Termination Fee and all debts, then mail a written cancellation notice to Abc Financial. Their account then enters a 45-day pending cancellation status where they make their final payments.
  - If member is past their agreement end date: They must call Abc Financial and mail the written notice. There is no Early Termination Fee, but they must still complete the 45-day notice payment period.

- **Late Payment Policy:**
  - A late fee of $19.50 plus the missed payment is applied for any payment over 1 day late. Multiple missed payments result in multiple late fees.
  - A one-time annual late fee waiver is possible IF the member updates their billing with a new bank account and routing number. If this happens, you must note that the fee was waived and the member needs to be added to the 'Late Payments Waived List' Google Sheet. (NOTE: AI cannot write to the sheet yet, just state the policy).
"""

FIRESTORE_COLLECTION = "member_conversations_v77_MASTER"
CLUBOS_LOGIN_URL = "https://anytime.club-os.com/action/Login/view?__fsk=-1558382445"
CLUBOS_CALENDAR_URL = "https://anytime.club-os.com/action/Calendar"
CLUBOS_MESSAGES_URL = "https://anytime.club-os.com/action/Dashboard/messages"
CLUBOS_DASHBOARD_URL = "https://anytime.club-os.com/action/Dashboard/view"
NOTE_AUTHOR_NAME = "Gym-Bot AI" # Changed to be more generic
TEXT_MESSAGE_CHARACTER_LIMIT = 300
MASTER_CONTACT_LIST_PATH = "master_contact_list.xlsx"
PROSPECT_DAILY_LIMIT = 100
PPV_MEMBER_DAILY_LIMIT = 20

# --- PAYMENT SCRAPING CONFIGURATION ---
CLUBOS_PERSONAL_TRAINING_URL = "https://anytime.club-os.com/action/Dashboard/PersonalTraining"
EXCLUDED_COMP_ACCOUNTS = [
    "Attitude Sports Employee Son", "Comfort Inn Guest 2", "Precision Lock Fdl", 
    "Comfort Inn-New", "Equipment Guy", "Attitude Sports Employee 1", 
    "Attitude Sports Employee 2", "Mason Dorn", "Dave Haase Attitude Sports"
]

# --- OVERDUE PAYMENT CONFIGURATION ---
OVERDUE_PAYMENT_THRESHOLD = 0.01  # Any amount over $0.00
SQUARE_APPLICATION_ID = "YOUR_ACTUAL_APPLICATION_ID_HERE"  # Replace with your real Square app ID
SQUARE_ACCESS_TOKEN_SECRET = "square-access-token"  # Secret Manager key for Square token
SQUARE_LOCATION_ID = "YOUR_LOCATION_ID_HERE"  # Replace with your Square location ID
OVERDUE_MESSAGE_TEMPLATE = """Hi {member_name}! 

Your account shows an overdue balance of ${amount:.2f}. Please click the link below to pay online immediately:

{invoice_link}

Questions? Reply to this message and we'll help right away!

Thanks,
Anytime Fitness Fond du Lac"""

# --- SERVICE CLIENTS (GLOBAL) & SETUP ---
secret_client = secretmanager.SecretManagerServiceClient()
db = firestore.Client()
gemini_model = None
app = Flask(__name__) # Initialize Flask app here

def get_secret(secret_name, version="latest"):
    """Get secret from Google Secret Manager."""
    try:
        # First try environment variables
        env_var_name = secret_name.upper().replace('-', '_')
        env_value = os.environ.get(env_var_name)
        if env_value:
            print(f"INFO: Using environment variable for {secret_name}")
            return env_value
        
        # Fall back to Secret Manager
        print(f"INFO: Fetching secret '{secret_name}' from Secret Manager...")
        name = f"projects/{GCP_PROJECT_ID}/secrets/{secret_name}/versions/{version}"
        response = secret_client.access_secret_version(name=name)
        return response.payload.data.decode("UTF-8")
    except Exception as e:
        print(f"ERROR: Failed to get secret {secret_name}: {e}")
        return None

def initialize_services():
    """Initialize Google services and AI model."""
    global gemini_model
    try:
        # Initialize Gemini AI
        genai.configure(api_key=get_secret("gemini-api-key"))
        gemini_model = genai.GenerativeModel('gemini-pro')
        print("SUCCESS: Services initialized")
    except Exception as e:
        print(f"ERROR: Failed to initialize services: {e}")
        gemini_model = None

def setup_driver_and_login():
    """Setup Chrome driver and login to Club OS."""
    driver = None
    try:
        clubos_user = get_secret(CLUBOS_USERNAME_SECRET)
        clubos_pass = get_secret(CLUBOS_PASSWORD_SECRET)
        print("INFO: Initializing WebDriver...")
        options = Options()
        options.add_argument("--start-maximized")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        # Hide webdriver properties
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        print("INFO: Attempting Club OS login...")
        driver.get(CLUBOS_LOGIN_URL)
        time.sleep(3)
        
        print("   INFO: Filling login credentials...")
        username_field = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.NAME, "username"))
        )
        username_field.send_keys(clubos_user)
        
        password_field = driver.find_element(By.NAME, "password")
        password_field.send_keys(clubos_pass)
        
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

# --- MESSAGING FUNCTION (FROM MASTER_SCRIPT01.PY) ---
def send_clubos_message(driver, member_name, subject, body):
    """
    A single, robust function to send a message (Text or Email) to a member.
    This version includes automatic email fallback if SMS fails.
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
# --- END OF MESSAGING FUNCTION ---

# --- CORE DATA & SCRAPING FUNCTIONS ---

def get_last_message_sender(driver):
    """Gets the name of the member from the most recent thread on the messages page."""
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
    """Scrapes the full message history from the popup using the proven flexible iframe logic."""
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
        # driver.save_screenshot(f"debug_timeout_{current_step.replace(' ', '_')}.png") # Optional
        if in_iframe: driver.switch_to.default_content()
        return []
    except Exception as e:
        print(f"   ERROR: An unexpected error ({type(e).__name__}) occurred during conversation scraping at step '{current_step}'. Error: {e}")
        # driver.save_screenshot(f"debug_exception_{current_step.replace(' ', '_')}.png") # Optional
        # try:
        #     with open(f"debug_pagesource_{current_step.replace(' ', '_')}.html", "w", encoding="utf-8") as f_ps:
        #         f_ps.write(driver.page_source)
        # except: pass
        if in_iframe: driver.switch_to.default_content()
        return []

def get_member_training_type(member_name):
    """Reads the training_clients.csv file to determine the event type."""
    print(f"   INFO: Looking up training type for {member_name}...")
    # Path relative to Anytime_Bot.py if it's in Gym-Bot/ and csv is in Gym-Bot/gym-bot/
    csv_path = "gym-bot/training_clients.csv" 
    try:
        df = pd.read_csv(csv_path)
        member_row = df[df['Name'].str.contains(member_name, case=False, na=False)]
        if not member_row.empty:
            agreement_type = member_row.iloc[0]['AgreementType']
            print(f"   SUCCESS: Found Agreement Type: '{agreement_type}'")
            if "Small Group" in agreement_type: return "SMALL_GROUP_TRAINING"
            if "Personal" in agreement_type or "Coaching" in agreement_type: return "PERSONAL_TRAINING"
            if "Consultation" in agreement_type: return "ORIENTATION" # Retained from Anytime_Bot.py
            return "LEAD" # Default if no specific match
        print(f"   WARN: Member '{member_name}' not found in '{csv_path}'. Defaulting event type to LEAD.")
        return "LEAD"
    except FileNotFoundError:
        print(f"   ERROR: '{csv_path}' not found. Cannot determine training type for {member_name}. Defaulting event type to LEAD.")
        return "LEAD"
    except Exception as e:
        print(f"   ERROR: Could not read client data file ('{csv_path}') for {member_name}. Error: {e}. Defaulting event type to LEAD.")
        return "LEAD"

# --- CALENDAR FUNCTIONS ---

def navigate_calendar_week(driver, direction):
    """Navigates the calendar forward or backward by one week."""
    print(f"   INFO: Navigating calendar {direction} one week...")
    try:
        # Ensure driver is on the calendar page first
        if not driver.current_url.startswith(CLUBOS_CALENDAR_URL):
            print(f"   INFO: Not on calendar page. Navigating to {CLUBOS_CALENDAR_URL}")
            driver.get(CLUBOS_CALENDAR_URL)
            WebDriverWait(driver, 20).until(EC.url_contains("Calendar"))
            time.sleep(2) # Allow page to settle

        if direction == 'next':
            button_xpath = "//a[contains(@class, 'schedule-dayR') and .//i[contains(@class, 'fa-chevron-right')]]" # More specific selector
        else: # 'previous'
            button_xpath = "//a[contains(@class, 'schedule-dayL') and .//i[contains(@class, 'fa-chevron-left')]]" # More specific selector
        
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, button_xpath))).click()
        print(f"   SUCCESS: Clicked '{direction}' week button.")
        print("   INFO: Waiting 5 seconds for new week to load...") # Reduced wait time
        time.sleep(5)
        return True
    except Exception as e:
        print(f"   ERROR: Could not navigate calendar week. Error: {e}")
        return False

def get_calendar_view_details(driver, schedule_name="My schedule"):
    """
    Scans the entire calendar week and identifies the status of each time slot
    (e.g., Available, Group Training, Personal Training, etc.) based on the
    icon's title attribute.
    """
    print(f"   INFO: Performing detailed scan of calendar for '{schedule_name}'...")
    calendar_data = {}
    try:
        # 1. Navigate to the calendar and select the correct view
        driver.get("https://anytime.club-os.com/action/Calendar")
        time.sleep(5) # Patient wait for page to render

        view_dropdown_element = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, "change-view"))
        )
        Select(view_dropdown_element).select_by_visible_text(schedule_name)
        time.sleep(3)
        
        # 2. Apply zoom to see the whole grid
        driver.execute_script("document.body.style.zoom='20%'"); time.sleep(2)
        
        schedule_table = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "schedule")))
        
        # 3. Get the column headers for each day
        header_row = schedule_table.find_element(By.CSS_SELECTOR, "tr.calendar-head")
        day_headers = header_row.find_elements(By.TAG_NAME, "th")[1:-1]
        day_columns = {header.find_element(By.CSS_SELECTOR, "p.primary").text: idx for idx, header in enumerate(day_headers)}

        # 4. Loop through each time row and day cell
        time_rows = schedule_table.find_elements(By.CSS_SELECTOR, "tbody > tr:not(.calendar-head):not(.am-pm)")
        for row in time_rows:
            day_cells = row.find_elements(By.TAG_NAME, "td")[1:-1]
            for day_name, col_idx in day_columns.items():
                if day_name not in calendar_data:
                    calendar_data[day_name] = []
                
                cell = day_cells[col_idx]
                time_text_element = cell.find_element(By.CSS_SELECTOR, "span:not(.avail-location)")
                time_text = time_text_element.text.strip()
                if not time_text:
                    continue

                slot_details = {"time": time_text, "status": "Unknown"}

                # Check if the slot is booked
                try:
                    event_container = cell.find_element(By.CSS_SELECTOR, "div.cal-event-container")
                    # If an event exists, check its type by the icon title
                    try:
                        icon = event_container.find_element(By.TAG_NAME, "img")
                        event_title = icon.get_attribute("title")
                        if "Small Group Training" in event_title or "Group Training" in event_title:
                            slot_details["status"] = "Group Training"
                        elif "Personal Training" in event_title:
                            slot_details["status"] = "Personal Training"
                        elif "Appointment" in event_title:
                            slot_details["status"] = "Appointment"
                        else:
                            slot_details["status"] = "Booked"
                    except NoSuchElementException:
                        slot_details["status"] = "Booked" # Booked, but no specific icon found
                except NoSuchElementException:
                    # If no event container, the slot is available
                    slot_details["status"] = "Available"

                calendar_data[day_name].append(slot_details)
        
        print(f"   SUCCESS: Detailed calendar scan complete.")
        driver.execute_script("document.body.style.zoom='100%'")
        return calendar_data
    except Exception as e:
        print(f"   ERROR: Could not perform detailed calendar scan. Error: {e}")
        try:
            driver.execute_script("document.body.style.zoom='100%'")
        except:
            pass
        return {}
    
def add_to_group_session(driver, details):
    """
    Finds an existing group session on the calendar using direct DOM manipulation and JSON metadata.
    This is a cleaner approach that uses the session containers' hidden JSON data for reliable matching.
    'details' should contain:
      - member_name_to_add
      - session_time_str (e.g., "10:30 AM")
      - session_day_xpath_part (e.g., "2025-06-27") 
      - target_schedule_name
    """
    print(f"INFO: Adding '{details['member_name_to_add']}' to group session using DOM-based approach...")
    
    try:
        # 1. Navigate to calendar and set correct schedule view
        if not driver.current_url.startswith(CLUBOS_CALENDAR_URL):
            print(f"   DEBUG: Navigating to calendar: {CLUBOS_CALENDAR_URL}")
            driver.get(CLUBOS_CALENDAR_URL)
            WebDriverWait(driver, 20).until(EC.url_contains("Calendar"))

        # Change to target schedule view if needed  
        current_view_element = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.ID, "change-view")))
        current_view_select = Select(current_view_element)
        current_schedule = current_view_select.first_selected_option.text.strip()
        target_schedule = details['target_schedule_name']
        
        if current_schedule != target_schedule:
            print(f"   DEBUG: Changing from '{current_schedule}' to '{target_schedule}'")
            current_view_select.select_by_visible_text(target_schedule)
            time.sleep(3)

        # 2. Wait for calendar sessions to load
        print("   DEBUG: Waiting for calendar sessions to load...")
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "cal-event-container"))
        )
        
        # Get all session containers
        all_sessions = driver.find_elements(By.CLASS_NAME, "cal-event-container")
        print(f"   DEBUG: Found {len(all_sessions)} total sessions in calendar")
        
        # 3. Parse each session's JSON metadata to find target
        target_session = None
        target_event_ids = ["2", "8"]  # Personal Training and Small Group Training
        
        # Parse the target date and time
        target_date_str = details['session_day_xpath_part']  # e.g., "2025-06-27"
        target_time_str = details['session_time_str']  # e.g., "10:30 AM"
        
        print(f"   DEBUG: Searching for sessions matching:")
        print(f"     - Event types: {target_event_ids} (Personal/Small Group Training)")
        print(f"     - Target time: {target_time_str}")
        print(f"     - Target date: {target_date_str}")
        
        for i, session in enumerate(all_sessions):
            try:
                # Extract JSON metadata from hidden input
                hidden_input = session.find_element(By.XPATH, ".//input[@type='hidden']")
                json_data = hidden_input.get_attribute("value").replace('&quot;', '"')
                session_data = json.loads(json_data)
                
                # Get session info - try multiple possible field names for time
                event_type_id = session_data.get("eventTypeId", "")
                session_date = session_data.get("day", "")  # e.g., "6/27/2025"
                
                # Extract time from .slot-info text instead of JSON
                session_time = ""
                try:
                    slot_info = session.find_element(By.CLASS_NAME, "slot-info")
                    slot_text = slot_info.text.strip();
                    
                    # Match the time range, e.g., "4:00 - 4:30" or "10:30 - 11:00"
                    match = re.search(r"(\d{1,2}:\d{2})\s*-\s*(\d{1,2}:\d{2})", slot_text)
                    if match:
                        start_time = match.group(1)  # "4:00" or "10:30"
                        
                        # Convert to 12-hour format with AM/PM to match target format
                        try:
                            # Parse as 24-hour time first
                            time_obj = datetime.strptime(start_time, "%H:%M")
                            session_time = time_obj.strftime("%I:%M %p").lstrip('0')  # Remove leading zero
                        except ValueError:
                            # If that fails, try 12-hour format
                            try:
                                time_obj = datetime.strptime(start_time, "%I:%M")
                                session_time = time_obj.strftime("%I:%M %p").lstrip('0')
                            except ValueError:
                                session_time = start_time  # Use as-is if parsing fails
                        
                        print(f"     Session {i+1}: Extracted time '{start_time}' -> '{session_time}' from slot text: {slot_text}")
                    else:
                        print(f"     Session {i+1}: No time pattern found in slot text: {slot_text}")
                        
                except NoSuchElementException:
                    print(f"     Session {i+1}: No .slot-info element found")
                
                # Debug: Print all available keys in session_data for troubleshooting
                if i < 3:  # Only print first 3 sessions to avoid spam
                    print(f"     Session {i+1} JSON keys: {list(session_data.keys())}")
                
                print(f"     Session {i+1}: Type={event_type_id}, Date={session_date}, Time='{session_time}'")
                
                # Convert dates to comparable format
                session_date_normalized = None
                if session_date:
                    try:
                        # Parse "6/27/2025" format
                        session_date_obj = datetime.strptime(session_date, "%m/%d/%Y")
                        session_date_normalized = session_date_obj.strftime("%Y-%m-%d")
                    except:
                        try:
                            # Try other date formats if needed
                            session_date_obj = datetime.strptime(session_date, "%Y-%m-%d")
                            session_date_normalized = session_date
                        except:
                            pass
                
                # Check if this matches our criteria
                if (event_type_id in target_event_ids and 
                    session_time == target_time_str and 
                    session_date_normalized == target_date_str):
                    print(f"     -> MATCH: Found exact target session!")
                    target_session = session
                    break
                    
                # If we found the right date and event type but time doesn't match exactly,
                # let's also try a more flexible time matching
                if (event_type_id in target_event_ids and 
                    session_date_normalized == target_date_str and 
                    not target_session):  # Only if we haven't found an exact match
                    
                    # Try to match time more flexibly (in case of formatting differences)
                    if session_time and target_time_str:
                        # Remove extra spaces and compare
                        session_time_clean = ' '.join(session_time.split())
                        target_time_clean = ' '.join(target_time_str.split())
                        
                        if session_time_clean.lower() == target_time_clean.lower():
                            print(f"     -> FLEXIBLE MATCH: Found target session with flexible time matching!")
                            target_session = session
                            break
                    
            except Exception as e:
                print(f"     Session {i+1}: Error parsing JSON - {e}")
                continue
        
        if not target_session:
            print(f"   WARN: No matching training session found via JSON method for {target_date_str} at {target_time_str}")
            print(f"   INFO: Trying alternative DOM-based matching approach...")
            
            # Alternative approach: Find sessions by inspecting the calendar DOM directly
            try:
                # Navigate to calendar if not already there
                if not driver.current_url.startswith(CLUBOS_CALENDAR_URL):
                    driver.get(CLUBOS_CALENDAR_URL)
                    WebDriverWait(driver, 20).until(EC.url_contains("Calendar"))
                
                # Apply zoom to see calendar better
                driver.execute_script("document.body.style.zoom='50%'")
                time.sleep(2)
                
                # Look for calendar cells that contain the target time
                time_xpath = f"//td[contains(@class, 'cal-slot') and .//span[contains(text(), '{target_time_str}')]]"
                time_slots = driver.find_elements(By.XPATH, time_xpath)
                
                print(f"   DEBUG: Found {len(time_slots)} time slots matching '{target_time_str}'")
                
                # For each matching time slot, check if it has a training session
                for slot in time_slots:
                    try:
                        # Look for training sessions in this slot
                        training_sessions = slot.find_elements(By.CSS_SELECTOR, ".cal-event-container")
                        for session in training_sessions:
                            # Check if this is a training session
                            try:
                                icon = session.find_element(By.TAG_NAME, "img")
                                title = icon.get_attribute("title") or ""
                                if ("Training" in title or "Group" in title):
                                    print(f"   SUCCESS: Found training session via DOM method: {title}")
                                    target_session = session
                                    driver.execute_script("document.body.style.zoom='100%'")
                                    break
                            except NoSuchElementException:
                                continue
                        if target_session:
                            break
                    except Exception as e:
                        continue
                
                driver.execute_script("document.body.style.zoom='100%'")
                
            except Exception as e:
                print(f"   ERROR: DOM-based fallback also failed: {e}")
                driver.execute_script("document.body.style.zoom='100%'")
            
            if not target_session:
                print(f"   ERROR: No matching training session found for {target_date_str} at {target_time_str}")
                return False
            
        print("   SUCCESS: Found target session, opening modal...")
        
        # 4. Click the target session to open modal
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", target_session)
        time.sleep(0.5)
        target_session.click()
        
        # 5. Wait for modal to appear and handle attendee modification
        print("   DEBUG: Waiting for session modal to open...")
        modal_selectors = [
            "#add-event-popup",    # Common modal ID
            "#eventModal",         # Alternative modal ID 
            ".modal",              # Generic modal class
            "[role='dialog']"      # ARIA dialog role
        ]
        
        modal = None
        for selector in modal_selectors:
            try:
                modal = WebDriverWait(driver, 5).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, selector))
                )
                print(f"   SUCCESS: Modal opened with selector: {selector}")
                break
            except TimeoutException:
                continue
                
        if not modal:
            print("   ERROR: Could not find session modal after clicking")
            return False
            
        # 6. Add attendee to the session using proven logic
        member_name = details['member_name_to_add']
        print(f"   DEBUG: Adding attendee '{member_name}' to session...")
        
        # Apply zoom for better element interaction
        driver.execute_script("document.body.style.zoom='60%'"); 
        time.sleep(1.5)
        
        # Use the proven attendee search selector - search in the whole driver, not just modal
        attendee_search_selector = "#add-event-popup input[name='attendeeSearchText']"
        print(f"   DEBUG: Waiting for attendee search box (Selector: {attendee_search_selector}) to be clickable...")
        
        # Search in the entire document, not just within modal
        attendee_search_box = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, attendee_search_selector))
        )
        
        print(f"   DEBUG: Attendee search box found. Clicking, clearing, and sending keys: '{member_name}'")
        attendee_search_box.click(); 
        time.sleep(0.5)
        attendee_search_box.clear()
        attendee_search_box.send_keys(member_name)
        print(f"   DEBUG: Keys sent to attendee search box.")

        # Use proven dropdown logic from working function
        dropdown_container_xpath = "//div[@id='add-event-popup']//div[@class='quick-search small-popup']"
        print(f"   DEBUG: Waiting for quick-search dropdown container to be visible...")
        WebDriverWait(driver, 15).until(EC.visibility_of_element_located((By.XPATH, dropdown_container_xpath)))
        
        dropdown_list_xpath = f"{dropdown_container_xpath}//ul[@class='search-results']"
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, dropdown_list_xpath)))
        
        dropdown_items_xpath_base = f"{dropdown_list_xpath}/li[@class='person']"
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, dropdown_items_xpath_base)))
        print(f"   DEBUG: Dropdown items present. Pausing 3 seconds for full rendering...")
        time.sleep(3)

        # Robust attendee selection using proven XPaths
        contact_result_xpath_v1 = f"{dropdown_items_xpath_base}[.//h4[normalize-space(.)=\"{member_name}\"]]"
        contact_result_xpath_v2_icon = f"{dropdown_items_xpath_base}[.//h4[normalize-space(.)=\"{member_name}\"] and .//img[@title='Member']]"
        contact_result_xpath_v3_fallback = f"{dropdown_items_xpath_base}[contains(normalize-space(.), \"{member_name}\")]"

        member_selected = False
        for i, xpath_attempt in enumerate([contact_result_xpath_v1, contact_result_xpath_v2_icon, contact_result_xpath_v3_fallback]):
            try:
                print(f"   DEBUG: Attempting to find and click contact result (Attempt {i+1})...")
                contact_result_element = WebDriverWait(driver, 7).until(
                    EC.element_to_be_clickable((By.XPATH, xpath_attempt))
                )
                driver.execute_script("arguments[0].click();", contact_result_element)
                print(f"   SUCCESS: Selected '{member_name}' using attempt {i+1}.")
                member_selected = True
                break
            except TimeoutException:
                print(f"   WARN: Attendee selection attempt {i+1} timed out.")
                continue
                
        if not member_selected:
            print(f"   ERROR: Could not find or select '{member_name}' in dropdown after all attempts")
            driver.execute_script("document.body.style.zoom='100%'")
            return False
        
        # Reset zoom before save
        print(f"   DEBUG: Resetting zoom to 100% before save.")
        driver.execute_script("document.body.style.zoom='100%'"); 
        time.sleep(0.5)
        
        # 7. Save changes using proven save button logic
        save_button = driver.find_element(By.ID, "save-event")
        print("   ACTION: Clicking 'Save event' button...")
        driver.execute_script("arguments[0].click();", save_button)
        
        # 8. Wait for modal to close
        WebDriverWait(driver, 20).until(
            EC.invisibility_of_element_located((By.ID, "add-event-popup"))
        )
        print(f"SUCCESS: Appointment for '{details['member_name']}' booked successfully.")
        return True
    except Exception as e:
        print(f"   ERROR: Failed during appointment booking. Current URL: {driver.current_url}. Error: {e}")
        try:
            error_screenshot_path = f"debug_booking_error_recurring_{details['member_name'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
            driver.save_screenshot(error_screenshot_path)
            print(f"   DEBUG: Screenshot of error saved to: {error_screenshot_path}")
        except Exception as ss_error:
            print(f"   WARN: Could not save screenshot during booking error: {ss_error}")
        try:
            driver.execute_script("document.body.style.zoom='100%'")
        except Exception as e_zoom_reset:
            print(f"   WARN: Failed to reset zoom in except block: {e_zoom_reset}")
        return False
# --- END: book_appointment ---

# --- BEGIN: update_contacts_from_source_workflow (restored robust version) ---
def update_contacts_from_source_workflow(overwrite=False):
    """
    Updates the master contact list from the ClubHub API, optionally overwriting with a full API pull.
    """
    print(f"INFO: Starting update_contacts_from_source_workflow (overwrite={overwrite})")
    try:
        # Pull members and prospects from ClubHub API
        print("   INFO: Pulling members from ClubHub API...")
        members_resp = requests.get(CLUBHUB_API_URL_MEMBERS, headers=CLUBHUB_HEADERS, params=PARAMS_FOR_MEMBERS_RECENT)
        members = members_resp.json().get('members', []) if members_resp.ok else []
        print(f"   INFO: Pulled {len(members)} members.")
        print("   INFO: Pulling prospects from ClubHub API...")
        prospects_resp = requests.get(CLUBHUB_API_URL_PROSPECTS, headers=CLUBHUB_HEADERS, params=PARAMS_FOR_PROSPECTS_RECENT)
        prospects = prospects_resp.json().get('prospects', []) if prospects_resp.ok else []
        print(f"   INFO: Pulled {len(prospects)} prospects.")
        # Combine and normalize
        contacts = []
        for m in members:
            contacts.append({
                'Name': m.get('name', ''),
                'Category': 'PPV' if m.get('agreementType', '').upper() == 'PPV' else 'Member',
                'ProspectID': m.get('id', ''),
                'MessagingStatus': ''
            })
        for p in prospects:
            contacts.append({
                'Name': p.get('name', ''),
                'Category': 'Prospect',
                'ProspectID': p.get('id', ''),
                'MessagingStatus': ''
            })
        df_new = pd.DataFrame(contacts)
        if overwrite or not os.path.exists(MASTER_CONTACT_LIST_PATH):
            print(f"   INFO: Overwriting '{MASTER_CONTACT_LIST_PATH}' with {len(df_new)} contacts.")
            df_new.to_excel(MASTER_CONTACT_LIST_PATH, index=False)
        else:
            print(f"   INFO: Merging new contacts with existing '{MASTER_CONTACT_LIST_PATH}'.")
            df_existing = pd.read_excel(MASTER_CONTACT_LIST_PATH, dtype=str).fillna("")
            df_combined = pd.concat([df_existing, df_new]).drop_duplicates(subset=['ProspectID', 'Name'], keep='first')
            df_combined.to_excel(MASTER_CONTACT_LIST_PATH, index=False)
        print(f"SUCCESS: Master contact list updated.")
    except Exception as e:
        print(f"ERROR: Failed to update contacts from source. Error: {e}")
# --- END: update_contacts_from_source_workflow ---

# --- BEGIN: handle_conversation_workflow (restored robust version, filled) ---
def handle_conversation_workflow(driver):
    """
    Handles the conversation workflow for the most recent member message.
    """
    print("INFO: Starting handle_conversation_workflow...")
    try:
        member_name = get_last_message_sender(driver)
        if not member_name:
            print("ERROR: No member found to process.")
            return
        print(f"   INFO: Processing conversation for member: {member_name}")
        conversation_history = scrape_conversation_for_contact(driver, member_name)
        print(f"   INFO: Conversation history: {conversation_history}")
        member_profile = {}  # Optionally pull more profile info here
        triage_label = get_ai_triage(conversation_history, member_profile)
        print(f"   INFO: AI triage label: {triage_label}")
        if triage_label == "SCHEDULING":
            params = get_ai_scheduling_parameters(conversation_history, member_profile)
            print(f"   INFO: Scheduling parameters: {params}")
            details = {
                'member_name': member_name,
                'time': params.get('times', [''])[0],
                'event_type': params.get('type', 'ORIENTATION'),
                'is_recurring': False
            }
            _process_booking_attempt(driver, details)
        elif triage_label == "GENERAL":
            reply = get_ai_general_reply(conversation_history, member_profile)
            print(f"   INFO: AI-generated reply: {reply}")
            send_clubos_message(driver, member_name, "Re: Your Message", reply)
        elif triage_label == "OPT-OUT":
            print(f"   INFO: Member {member_name} has opted out. No further action taken.")
        else:
            print(f"   INFO: Unknown triage label. No action taken.")
    except Exception as e:
        print(f"ERROR: Exception in handle_conversation_workflow. Error: {e}")
# --- END: handle_conversation_workflow ---

@app.route('/test_calendar_actions', methods=['POST'])
def test_calendar_actions():
    data = request.get_json()
    if not data:
        return {'status': 'error', 'message': 'No JSON data received'}, 400
    
    action = data.get('action')
    member_name = data.get('member_name')
    session_time = data.get('session_time')
    session_date = data.get('session_date')
    target_schedule = data.get('target_schedule', 'My schedule')
    
    print(f"INFO: Received calendar action request: {action} for {member_name} at {session_time} on {session_date}")
    
    # Setup driver and login for each request
    driver = None
    try:
        driver = setup_driver_and_login()
        
        if action == 'add_to_group_session':
            # Transform the request data into the format expected by add_to_group_session
            details = {
                'member_name_to_add': member_name,
                'session_time_str': session_time,
                'session_day_xpath_part': session_date,  # Will be used for date matching
                'target_schedule_name': target_schedule
            }
            result = add_to_group_session(driver, details)
            return {'status': 'success' if result else 'failure', 'action': action, 'member_name': member_name}, 200
        else:
            return {'status': 'error', 'message': f'Unknown action: {action}'}, 400
    except Exception as e:
        print(f"ERROR: Exception in calendar action: {e}")
        return {'status': 'error', 'message': str(e)}, 500
    finally:
        if driver:
            driver.quit()

def test_remove_from_session():
    """Test function to demonstrate removing a member from a group session."""
    print("=== Testing Remove from Session Functionality ===")
    
    # Initialize services and driver
    initialize_services()
    driver = setup_driver_and_login()
    
    try:
        # Test removal details - same session we used for adding Grace Sphatt
        session_details = {
            'member_name_to_add': 'Grace Sphatt',     # For adding
            'member_name_to_remove': 'Grace Sphatt',  # For removing
            'session_time_str': '10:30 AM',          # Session time
            'session_day_xpath_part': '2025-06-27',  # Session date (YYYY-MM-DD format)
            'target_schedule_name': 'My schedule'    # Calendar view name
        }
        
        print(f"\n=== Testing ADD then REMOVE for '{session_details['member_name_to_add']}' ===")
        print(f"  - Date: {session_details['session_day_xpath_part']}")
        print(f"  - Time: {session_details['session_time_str']}")
        print(f"  - Calendar: {session_details['target_schedule_name']}")
        
        # First, add the member to the session
        print("\n1. Adding member to session...")
        add_success = add_to_group_session(driver, session_details)
        
        if add_success:
            print("\n[SUCCESS] ADD SUCCESS: Grace Sphatt was added to the session!")
            
            # Wait and refresh the calendar to ensure the changes are reflected
            print("\n   DEBUG: Waiting 5 seconds for calendar to stabilize after add...")
            time.sleep(5)
            
            print("   DEBUG: Refreshing calendar to ensure Grace appears in the attendee list...")
            driver.refresh()
            time.sleep(3)  # Wait for page to reload
            
            # Now test the removal
            print("\n2. Now testing REMOVE from the same session...")
            remove_success = remove_attendee_from_session(driver, session_details)
            
            if remove_success:
                print("\n[SUCCESS] REMOVE SUCCESS: Grace Sphatt was successfully removed!")
                print("\n[SUCCESS] Both ADD and REMOVE functionality are working correctly!")
                return True
            else:
                print("\n[ERROR] REMOVE FAILED: Could not remove Grace from session.")
                return False
        else:
            print("\n[ERROR] ADD FAILED: Could not add Grace to session. Skipping remove test.")
            return False
            
    except Exception as e:
        print(f"\nERROR: Test failed with exception: {e}")
        return False
    finally:
        driver.quit()
        print("[SUCCESS] Test completed - WebDriver closed.")

# --- SQUARE API & OVERDUE PAYMENT FUNCTIONS ---

def get_square_client():
    """Initialize Square API client with credentials from Secret Manager."""
    print("INFO: Initializing Square API client...")
    try:
        import squareup
        from squareup.models import Money
        
        # Get Square access token from Secret Manager
        square_token = get_secret(SQUARE_ACCESS_TOKEN_SECRET)
        
        # Initialize Square client (use production for live business account)
        client = squareup.Client(
            access_token=square_token,
            environment='production'  # Using production since you have a real business account
        )
        
        print("   SUCCESS: Square API client initialized")
        return client
        
    except Exception as e:
        print(f"   ERROR: Failed to initialize Square client: {e}")
        return None

def create_square_invoice(member_name, amount_due, member_email=None):
    """Create a Square invoice for overdue payments and return the payment link."""
    print(f"INFO: Creating Square invoice for {member_name} - ${amount_due:.2f}")
    try:
        client = get_square_client()
        if not client:
            return None
            
        invoices_api = client.invoices
        
        # Create invoice request
        from squareup.models import CreateInvoiceRequest, Invoice, InvoiceRecipient, Money
        
        # Convert amount to cents for Square API
        amount_cents = int(amount_due * 100)
        
        invoice_body = Invoice(
            primary_recipient=InvoiceRecipient(
                given_name=member_name.split()[0] if ' ' in member_name else member_name,
                family_name=member_name.split()[1] if ' ' in member_name else ""
            ),
            payment_requests=[{
                "request_method": "EMAIL",  # Email invoice
                "request_type": "BALANCE",  # Request full balance
                "due_date": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")  # Due in 7 days
            }],
            delivery_method="EMAIL",
            invoice_number=f"OVERDUE-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            title="Overdue Account Balance",
            description=f"Overdue balance for {member_name} at Anytime Fitness Fond du Lac",
            order_request={
                "location_id": "LOCATION_ID_HERE",  # TODO: Replace with actual location ID
                "order": {
                    "location_id": "LOCATION_ID_HERE",  # TODO: Replace with actual location ID
                    "line_items": [{
                        "name": "Overdue Account Balance",
                        "quantity": "1",
                        "base_price_money": Money(
                            amount=amount_cents,
                            currency="USD"
                        )
                    }]
                }
            }
        )
        
        # Add email if provided
        if member_email:
            invoice_body.primary_recipient.email_address = member_email
        
        request = CreateInvoiceRequest(invoice=invoice_body)
        
        # Create the invoice
        result = invoices_api.create_invoice(body=request)
        
        if result.is_success():
            invoice = result.body.get('invoice', {})
            invoice_id = invoice.get('id')
            
            # Publish the invoice to make it payable
            publish_result = invoices_api.publish_invoice(
                invoice_id=invoice_id,
                body={"request_method": "EMAIL"}
            )
            
            if publish_result.is_success():
                # Get the payment URL
                invoice_data = publish_result.body.get('invoice', {})
                payment_url = invoice_data.get('public_url', '')
                
        driver.get(CLUBOS_DASHBOARD_URL)
        
        search_box = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, "quick-search-text"))
        )
        search_box.clear()
        search_box.send_keys(member_name)
        time.sleep(3)
        
        # Click on the member's profile
        contact_result_xpath = f"//h4[normalize-space(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'))='{member_name.lower()}']"
        contact_element = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, contact_result_xpath))
        )
        contact_element.click()
        time.sleep(3)
        
        # Look for balance information on the profile page
        balance_selectors = [
            "//span[contains(text(), 'Balance')]/following-sibling::span",
            "//div[contains(@class, 'balance')]//span[contains(text(), '$')]",
            "//*[contains(text(), 'Outstanding')]/following-sibling::*[contains(text(), '$')]",

            "//*[contains(text(), 'Overdue')]/following-sibling::*[contains(text(), '$')]",
            "//td[contains(text(), 'Balance')]/following-sibling::td",
            "//*[@class='amount' or @class='balance' or contains(@class, 'overdue')]"
        ]
        
        balance_amount = 0.0
        balance_found = False
        
        for selector in balance_selectors:
            try:
                balance_elements = driver.find_elements(By.XPATH, selector)
                for element in balance_elements:
                    balance_text = element.text.strip()
                    print(f"   DEBUG: Found potential balance text: '{balance_text}'")
                    
                    # Extract dollar amount from text
                    import re
                    money_match = re.search(r'\$?([0-9,]+\.?[0-9]*)', balance_text)
                    if money_match:
                        amount_str = money_match.group(1).replace(',', '')
                        try:
                            amount = float(amount_str)
                            if amount > 0:  # Only consider positive balances as overdue
                                balance_amount = amount
                                balance_found = True
                                print(f"   SUCCESS: Found overdue balance: ${balance_amount:.2f}")
                                break
                        except ValueError:
                            continue
            except Exception as e:
                print(f"   DEBUG: Selector failed: {selector} - {e}")
                continue
        
        if not balance_found:
            print(f"   INFO: No overdue balance found for {member_name} (assuming $0.00)")
            balance_amount = 0.0
        
        return balance_amount
        
    except Exception as e:
        print(f"   ERROR: Failed to check balance for {member_name}: {e}")
        return     0.0

def check_member_balance(driver, member_name):
    """
    Check member's balance from their Club OS profile page.
    Returns the balance due amount as a float.
    """
    try:
        # Wait for page to fully load
        time.sleep(3)
        
        balance_due = 0.0
        page_source = driver.page_source.lower()
        
        # Common patterns for balance information on Club OS
        balance_patterns = [
            r'balance[:\s]*\$?([\d,]+\.?\d*)',
            r'amount due[:\s]*\$?([\d,]+\.?\d*)',
            r'outstanding[:\s]*\$?([\d,]+\.?\d*)',
            r'balance due[:\s]*\$?([\d,]+\.?\d*)',
            r'past due[:\s]*\$?([\d,]+\.?\d*)',
            r'overdue[:\s]*\$?([\d,]+\.?\d*)',
            r'\$?([\d,]+\.?\d*)\s*(?:past|over)?due',
            r'owe[sd]?[:\s]*\$?([\d,]+\.?\d*)'
        ]
        
        # Look for balance information using various selectors
        balance_selectors = [
            # Common Club OS balance element selectors
            "span[class*='balance']",
            "div[class*='balance']",
            "span[class*='amount']",
            "div[class*='amount']",
            "span[class*='due']",
            "div[class*='due']",
            ".balance-amount",
            ".amount-due",
            ".outstanding-balance",
            "#balance",
            "[data-balance]",
            "td:contains('Balance')",
            "td:contains('Amount Due')",
            "span:contains('$')"
        ]
        
        # Try to find balance using CSS selectors
        for selector in balance_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    element_text = element.text.strip()
                    if element_text and ('$' in element_text or any(word in element_text.lower() for word in ['balance', 'due', 'owe'])):
                        # Extract numeric value
                        import re
                        numbers = re.findall(r'\$?([\d,]+\.?\d*)', element_text)
                        if numbers:
                            try:
                                amount = float(numbers[0].replace(',', ''))
                                if amount > balance_due:
                                    balance_due = amount
                                    print(f"   Found balance via selector '{selector}': ${balance_due:.2f} in text '{element_text}'")
                            except ValueError:
                                continue
            except Exception as e:
                # Some selectors might not work, continue with others
                continue
        
        # If no balance found via selectors, try regex patterns on page source
        if balance_due == 0.0:
            import re
            for pattern in balance_patterns:
                matches = re.findall(pattern, page_source, re.IGNORECASE)
                for match in matches:
                    try:
                        amount = float(match.replace(',', ''))
                        if amount > 0 and amount > balance_due:
                            balance_due = amount
                            print(f"   Found balance via pattern '{pattern}': ${balance_due:.2f}")
                            break
                    except ValueError:
                        continue
        
        # Look for specific Club OS financial section
        try:
            # Look for financial/billing related sections
            financial_sections = driver.find_elements(By.CSS_SELECTOR, 
                "section[class*='financial'], div[class*='billing'], div[class*='payment'], .account-summary, .financial-info")
            
            for section in financial_sections:
                section_text = section.text
                if any(word in section_text.lower() for word in ['balance', 'due', 'owe', 'payment', '$']):
                    # Try to extract balance from this section
                    import re
                    amounts = re.findall(r'\$?([\d,]+\.?\d*)', section_text)
                    for amount_str in amounts:
                        try:
                            amount = float(amount_str.replace(',', ''))
                            if amount > balance_due:
                                balance_due = amount
                                print(f"   Found balance in financial section: ${balance_due:.2f}")
                        except ValueError:
                            continue
        except Exception as e:
            print(f"   WARN: Error checking financial sections: {e}")
        
        # If still no balance found, check for tables with financial data
        if balance_due == 0.0:
            try:
                tables = driver.find_elements(By.TAG_NAME, "table")
                for table in tables:
                    table_text = table.text.lower()
                    if any(word in table_text for word in ['balance', 'due', 'amount', 'payment']):
                        # This table might contain financial info
                        rows = table.find_elements(By.TAG_NAME, "tr")
                        for row in rows:
                            row_text = row.text
                            if any(word in row_text.lower() for word in ['balance', 'due', 'owe']):
                                # Extract amount from this row
                                import re
                                amounts = re.findall(r'\$?([\d,]+\.?\d*)', row_text)
                                for amount_str in amounts:
                                    try:
                                        amount = float(amount_str.replace(',', ''))
                                        if amount > balance_due:
                                            balance_due = amount
                                            print(f"   Found balance in table row: ${balance_due:.2f} from '{row_text}'")
                                    except ValueError:
                                        continue
            except Exception as e:
                print(f"   WARN: Error checking tables: {e}")
        
        # Final validation
        if balance_due > 0:
            print(f"   INFO: {member_name} balance due: ${balance_due:.2f}")
        else:
            print(f"   INFO: {member_name} appears current (no balance found)")
        
        return balance_due
        
    except Exception as e:
        print(f"   ERROR: Failed to check balance for {member_name}: {e}")
        return 0.0

# --- DATA SAVING AND EXPORT FUNCTIONS ---

def save_training_package_data(training_data, output_directory="package_data"):
    """
    Save the comprehensive training package data in multiple formats for both automation and human use.
    
    Args:
        training_data: List of member data dictionaries containing training packages
        output_directory: Directory to save output files
    
    Returns:
        dict: Summary of saved files and statistics
    """
    try:
        import os
        import json
        import csv
        from datetime import datetime
        import pandas as pd
        
        # Create output directory if it doesn't exist
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)
            print(f"   INFO: Created output directory: {output_directory}")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # SAVE 1: Complete JSON file (for bot automation)
        json_filename = f"training_package_data_complete_{timestamp}.json"
        json_filepath = os.path.join(output_directory, json_filename)
        
        with open(json_filepath, 'w', encoding='utf-8') as f:
            json.dump({
                'extraction_timestamp': datetime.now().isoformat(),
                'total_members': len(training_data),
                'members_with_training': len([m for m in training_data if m.get('has_active_training', False)]),
                'total_packages': sum([m.get('training_package_count', 0) for m in training_data]),
                'data': training_data
            }, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"   SUCCESS: Saved complete JSON data to: {json_filepath}")
        
        # SAVE 2: Package-focused JSON (flattened structure for easy bot access)
        packages_only = []
        for member in training_data:
            if member.get('training_packages'):
                for package in member['training_packages']:
                    # Add member context to each package
                    package_with_context = {
                        **package,
                        'member_payment_status': member.get('payment_status', ''),
                        'member_balance_due': member.get('balance_due', 0.0),
                        'member_overdue_amount': member.get('overdue_amount', 0.0),
                        'member_next_invoice': member.get('next_invoice', ''),
                        'extraction_timestamp': datetime.now().isoformat()
                    }
                    packages_only.append(package_with_context)
        
        packages_json_filename = f"training_packages_only_{timestamp}.json"
        packages_json_filepath = os.path.join(output_directory, packages_json_filename)
        
        with open(packages_json_filepath, 'w', encoding='utf-8') as f:
            json.dump({
                'extraction_timestamp': datetime.now().isoformat(),
                'total_packages': len(packages_only),
                'packages': packages_only
            }, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"   SUCCESS: Saved packages-only JSON to: {packages_json_filepath}")
        
        # SAVE 3: CSV file for human analysis (flattened package data)
        if packages_only:
            csv_filename = f"training_packages_analysis_{timestamp}.csv"
            csv_filepath = os.path.join(output_directory, csv_filename)
            
            # Create flattened rows for CSV
            csv_rows = []
            for package in packages_only:
                row = {
                    'member_name': package.get('member_name', ''),
                    'package_name': package.get('package_name', ''),
                    'package_type': package.get('package_type', ''),
                    'trainer': package.get('trainer', ''),
                    'salesperson': package.get('salesperson', ''),
                    'payment_status': package.get('payment_status', ''),
                    'past_due_amount': package.get('past_due_amount', 0.0),
                    'next_payment_due_date': package.get('next_payment_due_date', ''),
                    'next_payment_amount': package.get('next_payment_amount', 0.0),
                    'monthly_cost': package.get('monthly_cost', 0.0),
                    'unit_price': package.get('unit_price', 0.0),
                    'total_agreement_value': package.get('total_agreement_value', 0.0),
                    'remaining_payments': package.get('remaining_payments', 0),
                    'sessions_remaining': package.get('sessions_remaining', 0),
                    'total_sessions': package.get('total_sessions', 0),
                    'sessions_used': package.get('sessions_used', 0),
                    'start_date': package.get('start_date', ''),
                    'billing_frequency': package.get('billing_frequency', ''),
                    'term_length': package.get('term_length', ''),
                    'renewal_type': package.get('renewal_type', ''),
                    'last_payment_date': package.get('last_payment_date', ''),
                    'last_payment_amount': package.get('last_payment_amount', 0.0),
                    'member_payment_status': package.get('member_payment_status', ''),
                    'member_balance_due': package.get('member_balance_due', 0.0),
                    'member_overdue_amount': package.get('member_overdue_amount', 0.0),
                    'extraction_timestamp': package.get('extraction_timestamp', '')
                }
                csv_rows.append(row)
            
            # Write CSV file
            if csv_rows:
                fieldnames = list(csv_rows[0].keys())
                with open(csv_filepath, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(csv_rows)
                
                print(f"   SUCCESS: Saved CSV analysis file to: {csv_filepath}")
        
        # SAVE 4: Past Due Focus Report (JSON + CSV)
        past_due_packages = [p for p in packages_only if p.get('past_due_amount', 0) > 0]
        
        if past_due_packages:
            # Past Due JSON
            past_due_json_filename = f"past_due_packages_{timestamp}.json"
            past_due_json_filepath = os.path.join(output_directory, past_due_json_filename)
            
            with open(past_due_json_filepath, 'w', encoding='utf-8') as f:
                json.dump({
                    'extraction_timestamp': datetime.now().isoformat(),
                    'total_past_due_packages': len(past_due_packages),
                    'total_past_due_amount': sum([p.get('past_due_amount', 0) for p in past_due_packages]),
                    'past_due_packages': past_due_packages
                }, f, indent=2, ensure_ascii=False, default=str)
            
            # Past Due CSV (simplified for quick review)
            past_due_csv_filename = f"past_due_summary_{timestamp}.csv"
            past_due_csv_filepath = os.path.join(output_directory, past_due_csv_filename)
            
            past_due_rows = []
            for package in past_due_packages:
                row = {
                    'member_name': package.get('member_name', ''),
                    'package_name': package.get('package_name', ''),
                    'trainer': package.get('trainer', ''),
                    'past_due_amount': package.get('past_due_amount', 0.0),
                    'next_payment_due_date': package.get('next_payment_due_date', ''),
                    'next_payment_amount': package.get('next_payment_amount', 0.0),
                    'last_payment_date': package.get('last_payment_date', ''),
                    'phone': '',  # Could be added if available in member data
                    'email': '',  # Could be added if available in member data
                    'notes': f"Past due: ${package.get('past_due_amount', 0.0):.2f}"
                }
                past_due_rows.append(row)
            
            if past_due_rows:
                with open(past_due_csv_filepath, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=list(past_due_rows[0].keys()))
                    writer.writeheader()
                    writer.writerows(past_due_rows)
                
                print(f"   SUCCESS: Saved past due summary to: {past_due_csv_filepath}")
                print(f"   CRITICAL: {len(past_due_packages)} packages with past due amounts totaling ${sum([p.get('past_due_amount', 0) for p in past_due_packages]):.2f}")
        
        # SAVE 5: Payment Schedule Report (upcoming payments)
        upcoming_payments = []
        for package in packages_only:
            if package.get('payment_schedule'):
                for payment in package['payment_schedule']:
                    payment_with_context = {
                        **payment,
                        'member_name': package.get('member_name', ''),
                        'package_name': package.get('package_name', ''),
                        'trainer': package.get('trainer', ''),
                        'package_past_due': package.get('past_due_amount', 0.0)
                    }
                    upcoming_payments.append(payment_with_context)
        
        if upcoming_payments:
            schedule_filename = f"payment_schedule_{timestamp}.json"
            schedule_filepath = os.path.join(output_directory, schedule_filename)
            
            with open(schedule_filepath, 'w', encoding='utf-8') as f:
                json.dump({
                    'extraction_timestamp': datetime.now().isoformat(),
                    'total_upcoming_payments': len(upcoming_payments),
                    'upcoming_payments': upcoming_payments
                }, f, indent=2, ensure_ascii=False, default=str)
            
            print(f"   SUCCESS: Saved payment schedule to: {schedule_filepath}")
        
        # Return summary
        summary = {
            'files_saved': {
                'complete_json': json_filepath,
                'packages_json': packages_json_filepath,
                'analysis_csv': csv_filepath if packages_only else None,
                'past_due_json': past_due_json_filepath if past_due_packages else None,
                'past_due_csv': past_due_csv_filepath if past_due_packages else None,
                'payment_schedule': schedule_filepath if upcoming_payments else None
            },
            'statistics': {
                'total_members': len(training_data),
                'members_with_training': len([m for m in training_data if m.get('has_active_training', False)]),
                'total_packages': len(packages_only),
                'past_due_packages': len(past_due_packages),
                'total_past_due_amount': sum([p.get('past_due_amount', 0) for p in past_due_packages]),
                'upcoming_payments': len(upcoming_payments)
            }
        }
        
        print(f"\n   DATA EXPORT SUMMARY:")
        print(f"   - Complete data: {json_filename}")
        print(f"   - Package analysis: {csv_filename if packages_only else 'No packages found'}")
        print(f"   - Past due alerts: {len(past_due_packages)} packages, ${sum([p.get('past_due_amount', 0) for p in past_due_packages]):.2f} total")
        print(f"   - Payment schedule: {len(upcoming_payments)} upcoming payments")
        
        return summary
        
    except Exception as e:
        print(f"   ERROR: Failed to save training package data: {e}")
        traceback.print_exc()
        return None

def generate_overdue_report(training_data, output_directory="package_data"):
    """
    Generate a focused report on overdue accounts for immediate action.
    
    Args:
        training_data: List of member data dictionaries
        output_directory: Directory to save report
        
    Returns:
        dict: Report summary with critical overdue information
    """
    try:
        import os
        from datetime import datetime
        
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Collect all overdue information
        overdue_members = []
        
        for member in training_data:
            member_overdue_info = {
                'member_name': member.get('member_name', ''),
                'member_payment_status': member.get('payment_status', ''),
                'member_balance_due': member.get('balance_due', 0.0),
                'member_overdue_amount': member.get('overdue_amount', 0.0),
                'training_packages': []
            }
            
            # Add training package overdue info
            if member.get('training_packages'):
                for package in member['training_packages']:
                    if package.get('past_due_amount', 0) > 0:
                        package_overdue = {
                            'package_name': package.get('package_name', ''),
                            'trainer': package.get('trainer', ''),
                            'past_due_amount': package.get('past_due_amount', 0.0),
                            'next_payment_due_date': package.get('next_payment_due_date', ''),
                            'next_payment_amount': package.get('next_payment_amount', 0.0),
                            'last_payment_date': package.get('last_payment_date', ''),
                            'monthly_cost': package.get('monthly_cost', 0.0)
                        }
                        member_overdue_info['training_packages'].append(package_overdue)
            
            # Include member if they have any overdue amounts
            total_overdue = member_overdue_info['member_overdue_amount'] + sum([p['past_due_amount'] for p in member_overdue_info['training_packages']])
            
            if total_overdue > 0:
                member_overdue_info['total_overdue_amount'] = total_overdue
                overdue_members.append(member_overdue_info)
        
        # Sort by total overdue amount (highest first)
        overdue_members.sort(key=lambda x: x['total_overdue_amount'], reverse=True)
        
        # Generate report
        report_filename = f"OVERDUE_PRIORITY_REPORT_{timestamp}.json"
        report_filepath = os.path.join(output_directory, report_filename)
        
        report_data = {
            'report_timestamp': datetime.now().isoformat(),
            'total_overdue_members': len(overdue_members),
            'total_overdue_amount': sum([m['total_overdue_amount'] for m in overdue_members]),
            'priority_contacts': overdue_members[:10],  # Top 10 priority
            'all_overdue_members': overdue_members
        }
        
        with open(report_filepath, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False, default=str)
        
        # Generate human-readable summary
        summary_filename = f"OVERDUE_SUMMARY_{timestamp}.txt"
        summary_filepath = os.path.join(output_directory, summary_filename)
        
        with open(summary_filepath, 'w', encoding='utf-8') as f:
            f.write(f"OVERDUE MEMBERS PRIORITY REPORT\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"=" * 50 + "\n\n")
            f.write(f"SUMMARY:\n")
            f.write(f"Total overdue members: {len(overdue_members)}\n")
            f.write(f"Total overdue amount: ${sum([m['total_overdue_amount'] for m in overdue_members]):.2f}\n\n")
            
            f.write(f"TOP 10 PRIORITY CONTACTS:\n")
            f.write(f"-" * 30 + "\n")
            
            for i, member in enumerate(overdue_members[:10]):
                f.write(f"{i+1}. {member['member_name']}\n")
                f.write(f"   Total Overdue: ${member['total_overdue_amount']:.2f}\n")
                f.write(f"   Member Status: {member['member_payment_status']}\n")
                
                if member['training_packages']:
                    f.write(f"   Training Packages:\n")
                    for pkg in member['training_packages']:
                        f.write(f"     - {pkg['package_name']} (Trainer: {pkg['trainer']})\n")
                        f.write(f"       Past Due: ${pkg['past_due_amount']:.2f}\n")
                        if pkg['next_payment_due_date']:
                            f.write(f"       Next Payment: {pkg['next_payment_due_date']} - ${pkg['next_payment_amount']:.2f}\n")
                f.write(f"\n")
        
        print(f"   SUCCESS: Generated overdue priority report:")
        print(f"   - JSON Report: {report_filename}")
        print(f"   - Summary: {summary_filename}")
        print(f"   - {len(overdue_members)} overdue members, ${sum([m['total_overdue_amount'] for m in overdue_members]):.2f} total")
        
        return {
            'report_file': report_filepath,
            'summary_file': summary_filepath,
            'overdue_count': len(overdue_members),
            'total_overdue': sum([m['total_overdue_amount'] for m in overdue_members])
        }
        
    except Exception as e:
        print(f"   ERROR: Failed to generate overdue report: {e}")
        traceback.print_exc()
        return None

# --- HELPER FUNCTIONS FOR TRAINING PACKAGE SCRAPING ---

def scrape_package_details(driver, member_name):
    """
    Extract detailed training package information from the Club OS package agreement details page.
    Returns a dictionary with comprehensive package details including payment schedules and agreement documents.
    
    This function handles the React-based Club OS package agreement page structure
    and extracts all relevant client, agreement, financial, and payment data.
    """
    try:
        print(f"   INFO: Scraping comprehensive package agreement details for {member_name}...")
        
        # Initialize comprehensive package info structure
        package_info = {
            # Basic Info
            'member_name': member_name,
            'package_name': '',
            'package_id': '',
            'package_type': 'Package Agreement',
            'status': 'Active',
            'scraped_timestamp': datetime.now().isoformat(),
            
            # Agreement Details
            'term_length': '',
            'billing_frequency': '',
            'start_date': '',
            'renewal_type': '',
            'trainer': '',
            'salesperson': '',
            
            # Financial Details
            'unit_price': 0.0,
            'units_per_billing_cycle': 0,
            'billing_cycle_days': 0,
            'monthly_cost': 0.0,
            'remaining_payments': 0,
            'total_agreement_value': 0.0,
            'past_due_amount': 0.0,
            'next_payment_due_date': '',
            'next_payment_amount': 0.0,
            'payment_status': 'Current',
            
            # Session Information
            'sessions_remaining': 0,
            'total_sessions': 0,
            'sessions_used': 0,
            'expiration_date': '',
        }
        
        # Wait for page to load
        time.sleep(3)
        
        # Extract from Club OS package agreement structure
        try:
            # Extract from left panel (package-agreement-details)
            details_panel = driver.find_elements(By.CSS_SELECTOR, ".package-agreement-details")
            
            if details_panel:
                panel = details_panel[0]
                
                # Extract Term Length
                try:
                    term_element = panel.find_element(By.XPATH, ".//label[contains(text(), 'Term Length')]/following-sibling::span//p")
                    package_info['term_length'] = term_element.text.strip()
                    print(f"   INFO: Term Length: {package_info['term_length']}")
                except:
                    pass
                
                # Extract Billing frequency
                try:
                    billing_element = panel.find_element(By.XPATH, ".//label[contains(text(), 'Billing')]/following-sibling::p")
                    billing_text = billing_element.text.strip()
                    package_info['billing_frequency'] = billing_text
                    
                    # Parse billing frequency to determine cycle days
                    if "2 weeks" in billing_text.lower():
                        package_info['billing_cycle_days'] = 14
                    elif "week" in billing_text.lower():
                        package_info['billing_cycle_days'] = 7
                    elif "month" in billing_text.lower():
                        package_info['billing_cycle_days'] = 30
                    
                    print(f"   INFO: Billing: {package_info['billing_frequency']}")
                except:
                    pass
                
                # Extract Start Date
                try:
                    start_date_element = panel.find_element(By.XPATH, ".//label[contains(text(), 'Start Date')]/following-sibling::p")
                    package_info['start_date'] = start_date_element.text.strip()
                    print(f"   INFO: Start Date: {package_info['start_date']}")
                except:
                    pass
                
                # Extract Trainer
                try:
                    trainer_element = panel.find_element(By.XPATH, ".//label[contains(text(), 'Trainer')]/following-sibling::p")
                    package_info['trainer'] = trainer_element.text.strip()
                    print(f"   INFO: Trainer: {package_info['trainer']}")
                except:
                    pass
            
            # Extract from Package Configuration table
            config_panel = driver.find_elements(By.CSS_SELECTOR, ".package-configuration")
            
            if config_panel:
                panel = config_panel[0]
                
                # Extract Package Name and Units
                try:
                    package_name_element = panel.find_element(By.CSS_SELECTOR, ".edit-proposal__details-table__row-label__name")
                    package_info['package_name'] = package_name_element.text.strip()
                    print(f"   INFO: Package Name: {package_info['package_name']}")
                    
                    # Extract units
                    units_element = panel.find_element(By.CSS_SELECTOR, ".edit-proposal__details-table__row-label__units")
                    units_text = units_element.text.strip()
                    units_match = re.search(r'\((\d+)\s*Units?\)', units_text)
                    if units_match:
                        package_info['total_sessions'] = int(units_match.group(1))
                        print(f"   INFO: Total Units: {package_info['total_sessions']}")
                except:
                    pass
                
                # Extract Unit Price
                try:
                    unit_price_element = panel.find_element(By.XPATH, ".//label[contains(text(), 'Unit Price')]/following-sibling::p")
                    unit_price_text = unit_price_element.text.strip()
                    unit_price_match = re.search(r'\$?(\d+(?:\.\d{2})?)', unit_price_text)
                    if unit_price_match:
                        package_info['unit_price'] = float(unit_price_match.group(1))
                        print(f"   INFO: Unit Price: ${package_info['unit_price']:.2f}")
                except:
                    pass
                
                # Extract Units per Bill Cycle
                try:
                    units_per_cycle_element = panel.find_element(By.XPATH, ".//label[contains(text(), 'Units/Bill Cycle')]/following-sibling::p")
                    package_info['units_per_billing_cycle'] = int(units_per_cycle_element.text.strip())
                    print(f"   INFO: Units per Bill Cycle: {package_info['units_per_billing_cycle']}")
                except:
                    pass
            
            # Extract from Statistics table (MOST IMPORTANT)
            stats_table = driver.find_elements(By.CSS_SELECTOR, ".edit-proposal__details-table--statistics")
            
            if stats_table:
                table = stats_table[0]
                
                # Extract Remaining Payments
                try:
                    remaining_payments_element = table.find_element(By.XPATH, ".//span[contains(text(), 'Remaining Payments')]/following-sibling::span")
                    package_info['remaining_payments'] = int(remaining_payments_element.text.strip())
                    print(f"   INFO: Remaining Payments: {package_info['remaining_payments']}")
                except:
                    pass
                
                # Extract Remaining Agreement Value
                try:
                    agreement_value_element = table.find_element(By.XPATH, ".//span[contains(text(), 'Remaining Agreement Value')]/following-sibling::span")
                    value_text = agreement_value_element.text.strip()
                    value_match = re.search(r'\$?(\d+(?:,\d{3})*(?:\.\d{2})?)', value_text)
                    if value_match:
                        package_info['total_agreement_value'] = float(value_match.group(1).replace(',', ''))
                        print(f"   INFO: Remaining Agreement Value: ${package_info['total_agreement_value']:.2f}")
                except:
                    pass
                
                # Extract Past Due Amount (CRITICAL)
                try:
                    past_due_element = table.find_element(By.XPATH, ".//span[contains(text(), 'Past Due Amount')]/following-sibling::span")
                    past_due_text = past_due_element.text.strip()
                    past_due_match = re.search(r'\$?(\d+(?:,\d{3})*(?:\.\d{2})?)', past_due_text)
                    if past_due_match:
                        package_info['past_due_amount'] = float(past_due_match.group(1).replace(',', ''))
                        
                        if package_info['past_due_amount'] > 0:
                            package_info['payment_status'] = 'Past Due'
                            print(f"   CRITICAL: FOUND PAST DUE AMOUNT: ${package_info['past_due_amount']:.2f}")
                        else:
                            package_info['payment_status'] = 'Current'
                            print(f"   INFO: Account is current (past due: ${package_info['past_due_amount']:.2f})")
                except:
                    pass
            
            # Calculate monthly cost if we have the data
            if package_info['unit_price'] > 0 and package_info['units_per_billing_cycle'] > 0 and package_info['billing_cycle_days'] > 0:
                cost_per_cycle = package_info['unit_price'] * package_info['units_per_billing_cycle']
                
                if package_info['billing_cycle_days'] == 14:  # Bi-weekly
                    package_info['monthly_cost'] = cost_per_cycle * 2.167
                elif package_info['billing_cycle_days'] == 7:  # Weekly
                    package_info['monthly_cost'] = cost_per_cycle * 4.33
                elif package_info['billing_cycle_days'] == 30:  # Monthly
                    package_info['monthly_cost'] = cost_per_cycle
                else:
                    package_info['monthly_cost'] = cost_per_cycle * (30 / package_info['billing_cycle_days'])
                
                print(f"   INFO: Calculated monthly cost: ${package_info['monthly_cost']:.2f}")
            
        except Exception as e:
            print(f"   DEBUG: Package data extraction failed: {e}")
        
        return package_info
        
    except Exception as e:
        print(f"   ERROR: Failed to scrape package details: {e}")
        return None

# --- MAIN TRAINING PAYMENT SCRAPING FUNCTION ---

def scrape_training_payments():
    """
    Main function to scrape training package data for all members.
    Reads training_clients.csv and processes each member's package agreements.
    """
    print("INFO: Starting comprehensive training payment scraping...")
    
    driver = None
    try:
        # Read the training clients CSV file
        csv_path = os.path.join(os.path.dirname(__file__), 'gym-bot', 'training_clients.csv')
        if not os.path.exists(csv_path):
            csv_path = os.path.join(os.path.dirname(__file__), 'training_clients.csv')
        
        if not os.path.exists(csv_path):
            print(f"   ERROR: training_clients.csv not found")
            return []
        
        print(f"   INFO: Reading training clients from {csv_path}")
        df = pd.read_csv(csv_path)
        
        if df.empty:
            print("   ERROR: training_clients.csv is empty")
            return []
        
        print(f"   INFO: Found {len(df)} training clients to process")
        
        # Setup driver and login
        driver = setup_driver_and_login()
        if not driver:
            print("   ERROR: Failed to setup driver and login")
            return []
        
        print("   SUCCESS: Logged in successfully. Starting to process members...")
        
        training_data = []
        failed_members = []
        
        # Process each training client
        for index, row in df.iterrows():
            try:
                member_name = row['Name']
                print(f"\n   INFO: Processing {member_name} ({index+1}/{len(df)})")
                
                # Navigate to member's profile
                driver.get(CLUBOS_DASHBOARD_URL)
                search_box = WebDriverWait(driver, 20).until(
                    EC.element_to_be_clickable((By.ID, "quick-search-text"))
                )
                search_box.clear()
                search_box.send_keys(member_name)
                time.sleep(3)
                
                # Click on member's profile
                contact_result_xpath = f"//h4[normalize-space(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'))='{member_name.lower()}']"
                contact_element = WebDriverWait(driver, 15).until(
                    EC.element_to_be_clickable((By.XPATH, contact_result_xpath))
                )
                contact_element.click()
                time.sleep(3)
                
                # Navigate to Club Services
                training_packages = []
                
                try:
                    # Click Club Info tab
                    club_info_element = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "#sidenav-container > div > nav > ul > li:nth-child(5) > a"))
                    )
                    
                    if club_info_element.is_displayed():
                        from selenium.webdriver.common.action_chains import ActionChains
                        ActionChains(driver).move_to_element(club_info_element).perform()
                        time.sleep(2)
                        
                        # Click Club Services
                        club_services_element = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, "#sidenav-container .dropdown-menu a[href*='Services']"))
                        )
                        club_services_element.click()
                        time.sleep(3)
                        
                        # CRITICAL: Zoom page out to 25% to see all content and scroll to load all packages
                        print("   INFO: Zooming page to 25% to view all packages...")
                        driver.execute_script("document.body.style.zoom='25%';")
                        time.sleep(2)
                        
                        # Smart scroll to load all dynamic content on Club Services page
                        print("   INFO: Scrolling to load all dynamic content...")
                        for scroll_attempt in range(5):
                            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                            time.sleep(1)
                        
                        driver.execute_script("window.scrollTo(0, 0);")
                        time.sleep(2)
                        
                        # COLLECT ALL ACTIVE PACKAGES FIRST (while page is zoomed)
                        package_links = driver.find_elements(By.XPATH, "//a[contains(@href, 'package-agreement')]")
                        
                        # Build list of active packages with their data to avoid stale elements
                        active_packages = []
                        for link in package_links:
                            try:
                                link_text = link.text.strip()
                                if link_text and len(link_text) > 5:  # Valid package link
                                    # Get the parent row to check for status indicators
                                    try:
                                        parent_row = link.find_element(By.XPATH, "./ancestor::tr[1]")
                                        row_text = parent_row.text.lower()
                                        
                                        # Skip inactive packages - be very specific about cancelled/terminated status
                                        inactive_keywords = ['cancelled', 'terminated', 'completed', 'expired', 'collection', 'void']
                                        if any(keyword in row_text for keyword in inactive_keywords):
                                            print(f"   INFO: Skipping INACTIVE package: {link_text} (Status: {row_text[:100]})")
                                            continue
                                        
                                        # Store active package data to process later
                                        package_href = link.get_attribute('href')
                                        active_packages.append({
                                            'name': link_text,
                                            'href': package_href,
                                            'status': 'active'
                                        })
                                        print(f"   INFO: Found ACTIVE package: {link_text}")
                                        
                                    except:
                                        # If we can't find parent row, still add it but with warning
                                        package_href = link.get_attribute('href')
                                        active_packages.append({
                                            'name': link_text,
                                            'href': package_href,
                                            'status': 'unknown'
                                        })
                                        print(f"   WARNING: Could not verify status for: {link_text} - processing anyway")
                                        
                            except Exception as link_error:
                                continue
                        
                        if not active_packages:
                            print(f"   INFO: No active package agreements found for {member_name}")
                        else:
                            print(f"   INFO: Found {len(active_packages)} ACTIVE package(s) to process")
                            
                            # Process each active package
                            for i, package_data in enumerate(active_packages):
                                try:
                                    package_name = package_data['name']
                                    package_href = package_data['href']
                                    
                                    print(f"   INFO: Processing package {i+1}/{len(active_packages)}: {package_name}")
                                    
                                    # Navigate directly to package URL to avoid stale elements
                                    driver.get(package_href)
                                    time.sleep(3)
                                    
                                    # Zoom package details page to 75% for better visibility
                                    driver.execute_script("document.body.style.zoom='75%';")
                                    time.sleep(1)
                                    
                                    # Scrape package details
                                    package_details = scrape_package_details(driver, member_name)
                                    if package_details:
                                        package_details['package_name'] = package_name
                                        training_packages.append(package_details)
                                        print(f"   SUCCESS: Extracted package details for {package_name}")
                                    
                                    # Go back to Club Services page
                                    driver.back()
                                    time.sleep(2)
                                    
                                    # Restore 25% zoom for Club Services page if not last package
                                    if i < len(active_packages) - 1:
                                        driver.execute_script("document.body.style.zoom='25%';")
                                        time.sleep(1)
                                    
                                except Exception as package_error:
                                    print(f"   ERROR: Failed to process package {package_name}: {package_error}")
                                    # Try to get back to Club Services page
                                    try:
                                        driver.back()
                                        time.sleep(2)
                                        if i < len(active_packages) - 1:
                                            driver.execute_script("document.body.style.zoom='25%';")
                                            time.sleep(1)
                                    except:
                                        pass
                                    continue
                        
                        # Reset zoom back to normal when done
                        driver.execute_script("document.body.style.zoom='100%';")
                        time.sleep(1)
                
                except Exception as nav_error:
                    print(f"   ERROR: Failed to navigate to Club Services: {nav_error}")
                
                # Create member data record
                member_data = {
                    'member_name': member_name,
                    'profile_url': row.get('Profile', '') if hasattr(row, 'get') else '',
                    'assigned_trainers': row.get('Assigned Trainers', '') if hasattr(row, 'get') else '',
                    'training_packages': training_packages,
                    'training_package_count': len(training_packages),
                    'has_active_training': len(training_packages) > 0,
                    'extraction_timestamp': datetime.now().isoformat()
                }
                
                training_data.append(member_data)
                print(f"   SUCCESS: Processed {member_name} - Found {len(training_packages)} package(s)")
                
            except Exception as e:
                print(f"   ERROR: Failed to process {member_name}: {e}")
                failed_members.append(member_name)
                continue
        
        print(f"\n   SUCCESS: Processed {len(training_data)} of {len(df)} training clients")
        
        if failed_members:
            print(f"   WARN: Failed to process {len(failed_members)} members: {', '.join(failed_members[:5])}")
        
        # Save the extracted data
        if training_data:
            print("\n   INFO: Saving extracted training package data...")
            save_summary = save_training_package_data(training_data)
            
            if save_summary:
                print(f"   SUCCESS: Data saved successfully")
                
                # Generate overdue report
                overdue_summary = generate_overdue_report(training_data)
                if overdue_summary:
                    print(f"   SUCCESS: Overdue report generated")
            
            # Print summary statistics
            total_packages = sum([m.get('training_package_count', 0) for m in training_data])
            members_with_training = len([m for m in training_data if m.get('has_active_training', False)])
            
            print(f"\n   FINAL SUMMARY:")
            print(f"   - Total members processed: {len(training_data)}")
            print(f"   - Members with active training: {members_with_training}")
            print(f"   - Total packages found: {total_packages}")
            
            # Show past due summary
            all_packages = []
            for member in training_data:
                if member.get('training_packages'):
                    all_packages.extend(member['training_packages'])
            
            past_due_packages = [p for p in all_packages if p.get('past_due_amount', 0) > 0]
            if past_due_packages:
                total_past_due = sum([p.get('past_due_amount', 0) for p in past_due_packages])
                print(f"   - CRITICAL: {len(past_due_packages)} packages with past due amounts totaling ${total_past_due:.2f}")
            else:
                print(f"   - All accounts appear current (no past due amounts found)")
        
        return training_data
        
    except Exception as e:
        print(f"   ERROR: Failed during training payment scraping: {e}")
        return []
    
    finally:
        if driver:
            driver.quit()

# --- BEGIN: navigate_to_club_services_for_member (restored robust version) ---
def navigate_to_club_services_for_member(driver, member_name, current_url):
    """
    Navigate to Club Info > Club Services for a member using robust click-based navigation.
    
    Args:
        driver: Selenium WebDriver instance
        member_name: Name of the member we're navigating for
        current_url: Current URL (for debugging)
    
    Returns:
        bool: True if successful navigation, False otherwise
    """
    try:
        print(f"   INFO: Navigating to Club Services for {member_name}...")
        
        # Step 1: Hover over Club Info tab
        try:
            from selenium.webdriver.common.action_chains import ActionChains
            
            club_info_element = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "#sidenav-container > div > nav > ul > li:nth-child(5) > a"))
            )
            
            if club_info_element.is_displayed():
                ActionChains(driver).move_to_element(club_info_element).perform()
                time.sleep(2)
                print(f"   SUCCESS: Hovered over Club Info tab")
            else:
                print(f"   ERROR: Club Info element found but not displayed")
                return False
                
        except Exception as e:
            print(f"   ERROR: Failed to find Club Info element: {e}")
            return False
        
        # Step 2: Click Club Services
        try:
            club_services_element = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "#sidenav-container .dropdown-menu a[href*='Services']"))
            )
            
            if club_services_element.is_displayed():
                club_services_element.click()
                time.sleep(3)
                print(f"   SUCCESS: Clicked Club Services")
            else:
                print(f"   ERROR: Club Services element found but not displayed")
                return False
                
        except Exception as e:
            print(f"   ERROR: Failed to find Club Services element: {e}")
            return False
        
        # Step 3: Verify we're on the Club Services page
        try:
            # Wait for Club Services content to be visible
            services_indicators = [
                "//div[contains(@class, 'club-services')]",
                "//div[contains(@class, 'services')]",
                "//*[contains(text(), 'Training Package') or contains(text(), 'Service Package')]",
                "//table[contains(@class, 'services') or contains(@class, 'packages')]",
                "//*[contains(@class, 'service-item') or contains(@class, 'package-item')]"
            ]
            
            services_loaded = False
            for indicator in services_indicators:
                try:
                    WebDriverWait(driver, 8).until(
                        EC.presence_of_element_located((By.XPATH, indicator))
                    )
                    services_loaded = True
                    print(f"   SUCCESS: Club Services content detected")
                    break
                except:
                    continue
            
            if not services_loaded:
                print(f"   WARNING: Could not verify Club Services content loaded, but proceeding...")
            
            print(f"   SUCCESS: Navigation to Club Services completed for {member_name}")
            return True
            
        except Exception as e:
            print(f"   ERROR: Failed to verify Club Services page: {e}")
            return False
        
    except Exception as e:
        print(f"   ERROR: Navigation to Club Services failed for {member_name}: {e}")
        return False
# --- END: navigate_to_club_services_for_member ---

# --- SQUARE API CONNECTION AND BASIC FUNCTIONS ---

def test_square_connection():
    """Test the Square API connection and retrieve account information."""
    print("INFO: Testing Square API connection...")
    try:
        # Determine which environment to use
        use_sandbox = SQUARE_ENVIRONMENT == 'sandbox'
        print(f"   INFO: Using {'sandbox' if use_sandbox else 'production'} environment")
        
        # Get credentials from Secret Manager
        if use_sandbox:
            access_token = get_secret(SQUARE_SANDBOX_ACCESS_TOKEN_SECRET)
            app_id = get_secret(SQUARE_SANDBOX_APPLICATION_ID_SECRET)
        else:
            access_token = get_secret(SQUARE_PRODUCTION_ACCESS_TOKEN_SECRET)
            app_id = get_secret(SQUARE_PRODUCTION_APPLICATION_ID_SECRET)
        
        # Get location ID
        location_id = get_secret(SQUARE_LOCATION_ID_SECRET)
        
        print(f"   INFO: Retrieved credentials successfully")
        print(f"   INFO: App ID: {app_id[:10]}...")
        print(f"   INFO: Access Token: {access_token[:10]}...")
        print(f"   INFO: Location ID: {location_id}")
        
        # Initialize Square client
        from squareup import Client
        
        environment = 'sandbox' if use_sandbox else 'production'
        client = Client(
            access_token=access_token,
            environment=environment
        )
        
        print(f"   SUCCESS: Square client initialized for {environment}")
        
        # Test API call - get locations
        locations_api = client.locations
        result = locations_api.list_locations()
        
        if result.is_success():
            locations = result.body.get('locations', [])
            print(f"   SUCCESS: Connected to Square! Found {len(locations)} locations:")
            for loc in locations:
                print(f"     - {loc.get('name', 'Unknown')} (ID: {loc.get('id', 'Unknown')})")
            return True
        else:
            errors = result.errors
            print(f"   ERROR: Square API call failed: {errors}")
            return False
            
    except Exception as e:
        print(f"   ERROR: Square connection test failed: {e}")
        return False

# --- MAIN FUNCTION AND COMMAND LINE INTERFACE ---

def main():
    """Main function with command-line argument parsing."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Anytime Fitness Club OS Bot')
    parser.add_argument('--action', choices=['full-scrape', 'update-contacts', 'test-square'], 
                       required=True, help='Action to perform')
    parser.add_argument('--overwrite', action='store_true', 
                       help='Overwrite existing data (for update-contacts)')
    
    args = parser.parse_args()
    
    print(f"=== Anytime Fitness Club OS Bot ===")
    print(f"Action: {args.action}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 40)
    
    if args.action == 'full-scrape':
        print("Starting full training package scraping...")
        initialize_services()
        results = scrape_training_payments()
        
        if results:
            print(f"\n=== SCRAPING COMPLETED SUCCESSFULLY ===")
            print(f"Total members processed: {len(results)}")
            
            # Show summary of findings
            overdue_packages = []
            for member in results:
                if member.get('training_packages'):
                    for package in member['training_packages']:
                        if package.get('past_due_amount', 0) > 0:
                            overdue_packages.append({
                                'member': member['member_name'],
                                'package': package.get('package_name', ''),
                                'amount': package.get('past_due_amount', 0)
                            })
            
            if overdue_packages:
                print(f"\nCRITICAL OVERDUE ACCOUNTS:")
                for pkg in overdue_packages[:10]:  # Show first 10
                    print(f"  - {pkg['member']}: ${pkg['amount']:.2f} ({pkg['package']})")
            else:
                print(f"\nAll accounts appear current.")
        else:
            print(f"\n=== SCRAPING FAILED ===")
    
    elif args.action == 'update-contacts':
        update_contacts_from_source_workflow(overwrite=args.overwrite)
    
    elif args.action == 'test-square':
        print("Testing Square API connection...")
        initialize_services()
        success = test_square_connection()
        if success:
            print("\n=== SQUARE API TEST: SUCCESS ===")
        else:
            print("\n=== SQUARE API TEST: FAILED ===")
    
    print("\n=== Bot execution completed ===")

if __name__ == "__main__":
    main()