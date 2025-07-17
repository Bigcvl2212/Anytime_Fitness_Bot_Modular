#!/usr/bin/env python3
"""
Test Square invoice creation and sending via ClubOS SMS/Email
"""

from services.payments.square_client_fixed import create_square_invoice
from services.api.clubos_api_client import ClubOSAPIClient
from config.secrets_local import get_secret
import requests

# ClubOS configuration
BASE_URL = "https://anytime.club-os.com"
LOGIN_URL = f"{BASE_URL}/action/Login"
FOLLOWUP_URL = f"{BASE_URL}/action/FollowUp/save"
CERT_PATH = "clubos_chain.pem"

# Your member details
RECIPIENT_ID = "187032782"  # Jeremy Mayo
SENDER_ID = "184027841"     # Example sender (from HAR)
CLUB_ID = "291"
CLUB_LOCATION_ID = "3586"

# Authentication
USERNAME = get_secret("clubos-username")
PASSWORD = get_secret("clubos-password")

# Use the captured _sourcePage and __fp values from HAR
_SOURCE_PAGE = "O420r3yCvcUOvmEhX_xkdZpAZ6mTO1xoo1NyAKsnoN4="
__FP = "_x48rx_II-0="

LOGIN_HEADERS = {
    "Content-Type": "application/x-www-form-urlencoded",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0",
    "Origin": "https://anytime.club-os.com",
    "Referer": "https://anytime.club-os.com/action/Login/view?__fsk=812871943",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
}

def login_and_get_session():
    session = requests.Session()
    session.verify = CERT_PATH
    login_payload = {
        "login": "Submit",
        "username": USERNAME,
        "password": PASSWORD,
        "_sourcePage": _SOURCE_PAGE,
        "__fp": __FP,
    }
    resp = session.post(LOGIN_URL, data=login_payload, headers=LOGIN_HEADERS)
    print(f"Login status code: {resp.status_code}")
    if resp.status_code == 200 and "Dashboard" in resp.text:
        print("✅ Logged in to ClubOS successfully.")
        return session
    print("❌ Login failed.")
    return None

def create_square_invoice_for_test():
    """Create a test Square invoice"""
    print("💰 Creating Square invoice...")
    
    invoice_url = create_square_invoice(
        member_name="Jeremy Mayo",
        amount=49.99,
        description="Test Invoice - Gym Bot Automation"
    )
    
    if invoice_url:
        print(f"✅ Square invoice created successfully!")
        print(f"   Invoice URL: {invoice_url}")
        return invoice_url
    else:
        print("❌ Failed to create Square invoice")
        return None

def send_invoice_via_clubos(session, invoice_url):
    """Send the invoice via ClubOS SMS and email"""
    print("📤 Sending invoice via ClubOS...")
    
    # Create message with invoice link
    email_subject = "Test Invoice - Gym Bot Automation"
    email_message = f"""
<p>Hi Jeremy Mayo!</p>

<p>This is a test invoice from the Gym Bot automation system.</p>

<p><strong>Amount:</strong> $49.99</p>
<p><strong>Description:</strong> Test Invoice - Gym Bot Automation</p>

<p>Please click the link below to pay:</p>
<p><a href="{invoice_url}">{invoice_url}</a></p>

<p>Thanks,<br>
Gym Bot AI</p>
"""
    
    text_message = f"Test invoice: $49.99 - Pay here: {invoice_url}"
    
    # First request with followUpAction: 2 (email)
    payload = {
        "followUpStatus": "1",
        "followUpType": "3",
        "memberSalesFollowUpStatus": "6",
        "followUpLog.tfoUserId": SENDER_ID,
        "followUpLog.outcome": "2",
        "emailSubject": email_subject,
        "emailMessage": email_message,
        "textMessage": text_message,
        "event.createdFor.tfoUserId": RECIPIENT_ID,
        "event.eventType": "ORIENTATION",
        "duration": "2",
        "event.remindAttendeesMins": "120",
        "followUpUser.tfoUserId": SENDER_ID,
        "followUpUser.role.id": "7",
        "followUpUser.clubId": CLUB_ID,
        "followUpUser.clubLocationId": CLUB_LOCATION_ID,
        "followUpLog.followUpAction": "2",  # Email
        "memberStudioSalesDefaultAccount": RECIPIENT_ID,
        "memberStudioSupportDefaultAccount": RECIPIENT_ID,
        "ptSalesDefaultAccount": RECIPIENT_ID,
        "ptSupportDefaultAccount": RECIPIENT_ID,
        "followUpUser.firstName": "Jeremy",
        "followUpUser.lastName": "Mayo",
        "followUpUser.email": "mayo.jeremy2212@gmail.com",
        "followUpUser.mobilePhone": "+1 (715) 586-8669",
    }
    
    resp = session.post(FOLLOWUP_URL, data=payload)
    print(f"Email request status: {resp.status_code}")
    print(f"Email response: {resp.text[:200]}")
    
    # Second request with followUpAction: 3 (SMS)
    payload["followUpLog.followUpAction"] = "3"
    resp2 = session.post(FOLLOWUP_URL, data=payload)
    print(f"SMS request status: {resp2.status_code}")
    print(f"SMS response: {resp2.text[:200]}")
    
    return resp.status_code == 200 and resp2.status_code == 200

def main():
    print("🚀 TESTING SQUARE INVOICE + CLUBOS MESSAGING")
    print("=" * 60)
    
    # Step 1: Create Square invoice
    invoice_url = create_square_invoice_for_test()
    if not invoice_url:
        print("❌ Cannot proceed without Square invoice")
        return
    
    # Step 2: Login to ClubOS
    session = login_and_get_session()
    if not session:
        print("❌ Cannot proceed without ClubOS login")
        return
    
    # Step 3: Send invoice via ClubOS
    success = send_invoice_via_clubos(session, invoice_url)
    
    if success:
        print("\n🎉 SUCCESS! Test invoice sent via ClubOS SMS and email!")
        print(f"   Invoice URL: {invoice_url}")
    else:
        print("\n❌ Failed to send invoice via ClubOS")

if __name__ == "__main__":
    main() 