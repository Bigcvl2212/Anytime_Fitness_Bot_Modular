#!/usr/bin/env python3
"""
Send a message and email to Jeremy Mayo via ClubOS /action/FollowUp/save endpoint using the correct payload structure, with SSL verification using a custom certificate.
"""
import requests
from config.secrets_local import get_secret

# ClubOS session setup
BASE_URL = "https://anytime.club-os.com"
LOGIN_URL = f"{BASE_URL}/action/Login"
FOLLOWUP_URL = f"{BASE_URL}/action/FollowUp/save"

# Path to the exported ClubOS certificate
CERT_PATH = "clubos_chain.pem"

# IDs from HAR and previous steps
RECIPIENT_ID = "187032782"  # Jeremy Mayo
SENDER_ID = "184027841"     # Example sender (from HAR)
CLUB_ID = "291"
CLUB_LOCATION_ID = "3586"

# Message content
EMAIL_SUBJECT = "Jeremy Mayo has sent you a message"
EMAIL_MESSAGE = "<p>This is a test email sent via the ClubOS API automation.</p>"
TEXT_MESSAGE = "This is a test SMS sent via the ClubOS API automation."

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
    print(f"Login response (first 500 chars):\n{resp.text[:500]}")
    if resp.status_code == 200 and "Dashboard" in resp.text:
        print("✅ Logged in to ClubOS successfully.")
        return session
    print("❌ Login failed.")
    return None


def send_followup_message(session):
    payload = {
        "followUpStatus": "1",
        "followUpType": "3",
        "memberSalesFollowUpStatus": "6",
        "followUpLog.tfoUserId": SENDER_ID,
        "followUpLog.outcome": "2",
        "emailSubject": EMAIL_SUBJECT,
        "emailMessage": EMAIL_MESSAGE,
        "textMessage": TEXT_MESSAGE,
        "event.createdFor.tfoUserId": RECIPIENT_ID,
        "event.eventType": "ORIENTATION",
        "duration": "2",
        "event.remindAttendeesMins": "120",
        "followUpUser.tfoUserId": SENDER_ID,
        "followUpUser.role.id": "7",
        "followUpUser.clubId": CLUB_ID,
        "followUpUser.clubLocationId": CLUB_LOCATION_ID,
        "followUpLog.followUpAction": "2",  # This was missing!
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
    print(f"Status code: {resp.status_code}")
    print(f"Response body:\n{resp.text[:1000]}")
    
    # Try the second request with followUpAction: 3
    payload["followUpLog.followUpAction"] = "3"
    resp2 = session.post(FOLLOWUP_URL, data=payload)
    print(f"\nSecond request status code: {resp2.status_code}")
    print(f"Second response body:\n{resp2.text[:1000]}")


def main():
    session = login_and_get_session()
    if not session:
        return
    send_followup_message(session)


if __name__ == "__main__":
    main() 