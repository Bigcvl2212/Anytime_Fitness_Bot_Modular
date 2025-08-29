"""
Gym Bot Configuration Module
Constants, URLs, and configuration values used throughout the application.
"""

import os

# =============================================================================
# CLUBOS CONFIGURATION
# =============================================================================

# ClubOS URLs
CLUBOS_LOGIN_URL = "https://anytime.club-os.com/action/Login/view?__fsk=1221801756"
CLUBOS_DASHBOARD_URL = "https://anytime.club-os.com/action/Dashboard/view"
CLUBOS_MESSAGES_URL = "https://anytime.club-os.com/action/Dashboard/messages"
CLUBOS_CALENDAR_URL = "https://anytime.club-os.com/action/Calendar"

# ClubOS Element IDs
CLUBOS_TEXT_TAB_ID = "text-tab"
CLUBOS_EMAIL_TAB_ID = "email-tab"

# ClubOS Credentials Secret Names
CLUBOS_USERNAME_SECRET = "clubos-username"
CLUBOS_PASSWORD_SECRET = "clubos-password"

# =============================================================================
# CLUB HUB API CONFIGURATION
# =============================================================================

CLUBHUB_API_URL_MEMBERS = "https://clubhub-ios-api.anytimefitness.com/api/v1.0/clubs/1156/members"
CLUBHUB_API_URL_PROSPECTS = "https://clubhub-ios-api.anytimefitness.com/api/v1.0/clubs/1156/prospects"
CLUBHUB_HEADERS = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMDgyMDQ0OSIsImVtYWlsIjoibWF5by5qZXJlbXkyMjEyQGdtYWlsLmNvbSIsImdpdmVuX25hbWUiOiJKZXJlbXkiLCJhZl9hcGlfdG9rZW4iOiJlNVY4RFdVTUE0Q1dCMUFhOGpDTU1hTFNMTDNCR2RIMFZLQldPazZPME9uUkIweUVpUF9UMUFYNEdGWG1MTWJFa0ZjSmNhSm0zbjIwVEM3aUZVSmQxVzlnWk12VkRIY1F0TE1uOXZvSXk5UWhka3BIRHAyUndVVFR2WDJyM05SeEVwZHlPdVBWU19xWENXQmNBUHpnWjhVWktfbWZBSTBfUW40S1B0Wkdib3V3ZGJKcHRCWEhxY2ZUNzRUQy1oRUNCTnhIMWdyTkZLU19UeUhmcUpLdTZhMlBNd1A4MHZ5V0c4Si1LUnJyVlpPZXRuRzcyd2V5N1FBRUk3MHZqZlJjUFh0V1FBandXMk5DNFRhU0U2MndsMFRXT1BleEc2RmloRGR0SnpuVklkSER5SmV2a1l5TFlwaVZoTDllMXpTdFNSaVNhdHhaN18wVFFEb3hhYUU2ZTliOE5hVSIsInBob3RvX3VybCI6IiIsInVzZXJfdHlwZSI6IlRyYWluZXIiLCJjbHViX2lkcyI6WyIxMTU2IiwiMTY1NyJdLCJyb2xlIjoiVHJhaW5lciIsImFwcGxpY2F0aW9uX2lkcyI6WyIxIiwiMyIsIjgiLCIxMiJdLCJuYmYiOjE3NTIzODAxNjQsImV4cCI6MTc1MjQ2NjU2NCwiaWF0IjoxNzUyMzgwMTY0LCJpc3MiOiJodHRwczovL2NsdWJodWItaW9zLWFwaS5hbnl0aW1lZml0bmVzcy5jb20vIiwiYXVkIjoiQ2x1Ykh1Yklvc0FwaSJ9.K1hiET3Bg_-CDhdUfK7Fus4smHFbZUTwHFYZbJcSXvA",
    "API-version": "1",
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Cookie": "incap_ses_132_434694=pJ43Iiiq7AgIQwVIVvXUAX//b2gAAAAAcBM8Epq6mDANrol1AXD4VQ==; dtCookie=v_4_srv_2_sn_942031A186D4529AF35E56616641EB2B_perc_100000_ol_0_mul_1_app-3Aea7c4b59f27d43eb_0_app-3A4b32026d63ce75ab_0_rcs-3Acss_1; visid_incap_434694=RnkdTm5oTZGIHQp7qeKPZANjSGgAAAAAQUIPAAAAAADfxJ4/rmakILSU3890u2w3; _ga_E3V4XR2W24=GS2.1.s1748029777$o2$g1$t1748029958$j0$l0$h0; rl_anonymous_id=RS_ENC_v3_IjQ4N2UyYTBkLTQ3NjItNDRhYy04ZDVkLTQ5ZWJjM2M1MWMyYSI%3D; rl_page_init_referrer=RS_ENC_v3_Imh0dHBzOi8vcmVzb3VyY2VjZW50ZXIuc2VicmFuZHMuY29tLyI%3D; rl_page_init_referring_domain=RS_ENC_v3_InJlc291cmNlY2VudGVyLnNlYnJhbmRzLmNvbSI%3D; rl_session=RS_ENC_v3_eyJpZCI6MTc0ODAyOTc3ODU1MiwiZXhwaXJlc0F0IjoxNzQ4MDMxNTc4NTYxLCJ0aW1lb3V0IjoxODAwMDAwLCJhdXRvVHJhY2siOnRydWUsInNlc3Npb25TdGFydCI6dHJ1ZX0%3D; _ga=GA1.1.2023145946.1747779026; visid_incap_498134=n71aHYAISneGZ49qOGxwdM39LGgAAAAAQUIPAAAAAABKTx/MOoTZK3A95JgTilNy"
}

# Historical parameters for getting ALL prospects (like the working legacy script)
PARAMS_FOR_HISTORICAL_PULL = { "days": "10000", "page": "1", "pageSize": "100" }
PARAMS_FOR_MEMBERS_RECENT = {"recent": True}
PARAMS_FOR_PROSPECTS_RECENT = { 
    "days": "10000", 
    "page": "1", 
    "pageSize": "100",
    "includeInactive": "true",
    "includeAll": "true", 
    "status": "all"
}

# =============================================================================
# MULTI-CHANNEL NOTIFICATIONS CONFIGURATION
# =============================================================================

# Twilio SMS Configuration
TWILIO_SID_SECRET = "twilio-account-sid"
TWILIO_TOKEN_SECRET = "twilio-auth-token"
TWILIO_FROM_NUMBER_SECRET = "twilio-from-number"

# Gmail Configuration
GMAIL_CREDENTIALS_SECRET = "bot-gmail-credentials"
GMAIL_TOKEN_SECRET = "bot-gmail-token"

# =============================================================================
# SQUARE PAYMENT CONFIGURATION
# =============================================================================

# Square Environment
SQUARE_ENVIRONMENT = os.getenv("SQUARE_ENVIRONMENT", "sandbox")  # 'sandbox' or 'production'

# Square Secret Names (stored in Google Secret Manager)
# Dynamic secret selection based on environment
def get_square_access_token_secret():
    """Get the appropriate Square access token secret based on environment"""
    env = os.getenv("SQUARE_ENVIRONMENT", "sandbox").lower()
    if env == "production":
        return "square-production-access-token"
    else:
        return "square-sandbox-access-token"

def get_square_location_id_secret():
    """Get the appropriate Square location ID secret based on environment"""
    env = os.getenv("SQUARE_ENVIRONMENT", "sandbox").lower()
    if env == "production":
        return "square-production-location-id"
    else:
        return "square-sandbox-location-id"

# Individual secret names for each environment
SQUARE_SANDBOX_ACCESS_TOKEN_SECRET = "square-sandbox-access-token"
SQUARE_SANDBOX_APPLICATION_ID_SECRET = "square-sandbox-application-id"
SQUARE_SANDBOX_APPLICATION_SECRET_SECRET = "square-sandbox-application-secret"
SQUARE_SANDBOX_LOCATION_ID_SECRET = "square-sandbox-location-id"

SQUARE_PRODUCTION_ACCESS_TOKEN_SECRET = "square-production-access-token"
SQUARE_PRODUCTION_APPLICATION_ID_SECRET = "square-production-application-id"
SQUARE_PRODUCTION_APPLICATION_SECRET_SECRET = "square-production-application-secret"
SQUARE_PRODUCTION_LOCATION_ID_SECRET = "square-production-location-id"

# Legacy constants for backward compatibility
SQUARE_ACCESS_TOKEN_SECRET = get_square_access_token_secret()
SQUARE_LOCATION_ID_SECRET = get_square_location_id_secret()

# Payment Configuration
LATE_FEE_AMOUNT = 19.50
PROCESSING_FEE_PERCENTAGE = 0.03  # 3.0% processing fee

# =============================================================================
# GOOGLE CLOUD CONFIGURATION
# =============================================================================

# Google Cloud Project
GCP_PROJECT_ID = "round-device-460522-g8"

# Secret Names
GEMINI_API_KEY_SECRET = "gemini-api-key"
BOT_GMAIL_CREDENTIALS_SECRET = "bot-gmail-credentials"
BOT_GMAIL_TOKEN_SECRET = "bot-gmail-token"

# Firestore Collections
FIRESTORE_COLLECTION = "member_conversations_v77_MASTER"

# =============================================================================
# MESSAGING CONFIGURATION
# =============================================================================

# Staff identification
STAFF_NAMES = ["Gym-Bot AI", "Jeremy", "Staff"]

# Message limits
TEXT_MESSAGE_CHARACTER_LIMIT = 300
PROSPECT_DAILY_LIMIT = 100
PPV_MEMBER_DAILY_LIMIT = 10

# Note configuration
NOTE_AUTHOR_NAME = "Jeremy's AI Assistant"

# Message Templates
YELLOW_RED_MESSAGE_TEMPLATE = """Hi {member_name}! Your membership payment is overdue: ${membership_amount:.2f} + ${late_fee:.2f} late fee = ${total_amount:.2f}. Pay now: {invoice_link} IF YOU DO NOT RESPOND WITHIN 7 DAYS YOUR ACCOUNT WILL BE FLAGGED FOR COLLECTIONS! -Anytime Fitness FDL"""

# =============================================================================
# PAYMENT CONFIGURATION
# =============================================================================

# Late fee amount for overdue payments
LATE_FEE_AMOUNT = 19.50

# Message templates
YELLOW_RED_MESSAGE_TEMPLATE = """Hi {member_name}! Your membership payment is overdue: ${membership_amount:.2f} + ${late_fee:.2f} late fee = ${total_amount:.2f}. Pay now: {invoice_link} IF YOU DO NOT RESPOND WITHIN 7 DAYS YOUR ACCOUNT WILL BE FLAGGED FOR COLLECTIONS! -Anytime Fitness FDL"""

# =============================================================================
# FILE PATHS
# =============================================================================

# Data files are in the data directory relative to the gym-bot package
MASTER_CONTACT_LIST_PATH = os.path.join("..", "data", "master_contact_list.xlsx")
TRAINING_CLIENTS_CSV_PATH = os.path.join("..", "data", "training_clients.csv")

# =============================================================================
# WORKFLOW CONFIGURATION
# =============================================================================

# API data management
CREATE_OR_OVERWRITE_CONTACT_FILE_FROM_API = True

# Debug configuration
DEBUG_FOLDER = "debug"
PACKAGE_DATA_FOLDER = "package_data"

# =============================================================================
# SELENIUM CONFIGURATION
# =============================================================================

# WebDriver timeouts
DEFAULT_WAIT_TIMEOUT = 10
ELEMENT_WAIT_TIMEOUT = 5
PAGE_LOAD_TIMEOUT = 30

# Chrome options
CHROME_OPTIONS = [
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--disable-blink-features=AutomationControlled",
    "--disable-extensions",
    "--disable-plugins",
    "--disable-images",
    "--disable-javascript",
    "--headless"  # Remove this for debugging
]

# =============================================================================
# AI CONFIGURATION
# =============================================================================

# Gemini model configuration
GEMINI_MODEL_NAME = "gemini-pro"
GEMINI_TEMPERATURE = 0.7
GEMINI_MAX_TOKENS = 1024

# =============================================================================
# FLASK CONFIGURATION
# =============================================================================

FLASK_HOST = "0.0.0.0"
FLASK_PORT = 8080
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "False").lower() == "true"
