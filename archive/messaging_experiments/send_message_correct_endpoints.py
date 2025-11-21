#!/usr/bin/env python3
"""
Send messages using the correct ClubOS endpoints based on working Selenium implementation
"""

from src.services.api.clubos_api_client import ClubOSAPIClient, ClubOSAPIAuthentication
from config.secrets_local import get_secret
import requests
from bs4 import BeautifulSoup
import time

TARGET_NAME = "Jeremy Mayo"
TARGET_MEMBER_ID = "187032782"
SMS_MESSAGE = "🎉 This is a test SMS sent via the correct ClubOS endpoints!"
EMAIL_MESSAGE = "🎉 This is a test EMAIL sent via the correct ClubOS endpoints!"

def send_message_correct_endpoints():
    """Send messages using the correct ClubOS endpoints"""
    
    print("🚀 SENDING MESSAGES USING CORRECT ENDPOINTS")
    print("=" * 50)
    print(f"Target: {TARGET_NAME}")
    print(f"Member ID: {TARGET_MEMBER_ID}")
    print()
    
    # Get credentials
    username = get_secret("clubos-username")
    password = get_secret("clubos-password")
    
    # Create authentication service and authenticate
    print("🔐 Authenticating with ClubOS...")
    auth_service = ClubOSAPIAuthentication()
    
    if not auth_service.login(username, password):
        print("❌ Authentication failed")
        return False
    
    print("✅ Authentication successful")
    print()
    
    # Step 1: Navigate to member profile (this is what Selenium does)
    print("📄 Step 1: Loading member profile...")
    member_profile_url = f"{auth_service.base_url}/action/Delegate/{TARGET_MEMBER_ID}/url=/action/LeadProfile"
    print(f"   URL: {member_profile_url}")
    
    profile_response = auth_service.session.get(member_profile_url, timeout=30, verify=False)
    print(f"   Status: {profile_response.status_code}")
    print(f"   Final URL: {profile_response.url}")
    
    if not profile_response.ok:
        print("   ❌ Could not load member profile")
        return False
    
    print("   ✅ Member profile loaded successfully")
    print()
    
    # Step 2: Use the working /action/FollowUp/save endpoint (this is what actually works)
    print("📤 Step 2: Sending SMS via /action/FollowUp/save...")
    
    # This is the form data structure that works based on the working scripts
    sms_form_data = {
        "followUpStatus": "1",
        "followUpType": "3",
        "memberSalesFollowUpStatus": "6",
        "followUpLog.tfoUserId": TARGET_MEMBER_ID,
        "followUpLog.outcome": "3",  # 3 for SMS
        "textMessage": SMS_MESSAGE,
        "event.createdFor.tfoUserId": TARGET_MEMBER_ID,
        "event.eventType": "ORIENTATION",
        "duration": "2",
        "event.remindAttendeesMins": "120",
        "followUpUser.tfoUserId": TARGET_MEMBER_ID,
        "followUpUser.role.id": "7",
        "followUpUser.clubId": "291",
        "followUpUser.clubLocationId": "3586",
        "followUpLog.followUpAction": "3",  # 3 for SMS
        "memberStudioSalesDefaultAccount": TARGET_MEMBER_ID,
        "memberStudioSupportDefaultAccount": TARGET_MEMBER_ID,
        "ptSalesDefaultAccount": TARGET_MEMBER_ID,
        "ptSupportDefaultAccount": TARGET_MEMBER_ID
    }
    
    # Headers for form submission
    headers = auth_service.get_headers()
    headers.update({
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Referer": member_profile_url,
        "Origin": auth_service.base_url
    })
    
    # Submit SMS
    followup_url = f"{auth_service.base_url}/action/FollowUp/save"
    print(f"   URL: {followup_url}")
    print(f"   Data: {sms_form_data}")
    
    sms_response = auth_service.session.post(
        followup_url,
        data=sms_form_data,
        headers=headers,
        timeout=30,
        verify=False
    )
    
    print(f"   Status: {sms_response.status_code}")
    print(f"   Final URL: {sms_response.url}")
    
    # Save response for debugging
    with open("sms_response_debug.html", "w", encoding="utf-8") as f:
        f.write(sms_response.text)
    print("   💾 Saved SMS response to sms_response_debug.html")
    
    # Check if SMS was successful
    if sms_response.ok:
        response_text = sms_response.text.lower()
        if "success" in response_text or "sent" in response_text or "saved" in response_text:
            print("   ✅ SMS sent successfully!")
            sms_success = True
        else:
            print("   ⚠️ SMS response unclear - checking content...")
            print(f"   Response preview: {sms_response.text[:500]}...")
            sms_success = False
    else:
        print(f"   ❌ SMS failed with status {sms_response.status_code}")
        sms_success = False
    
    print()
    
    # Step 3: Send Email using the same endpoint but different form data
    print("📧 Step 3: Sending Email via /action/FollowUp/save...")
    
    # Email form data (followUpAction: "2" for email)
    email_form_data = {
        "followUpStatus": "1",
        "followUpType": "2",
        "memberSalesFollowUpStatus": "6",
        "followUpLog.tfoUserId": TARGET_MEMBER_ID,
        "followUpLog.outcome": "2",  # 2 for Email
        "emailSubject": "Test Email from ClubOS API",
        "emailMessage": f"<p>{EMAIL_MESSAGE}</p>",
        "event.createdFor.tfoUserId": TARGET_MEMBER_ID,
        "event.eventType": "ORIENTATION",
        "duration": "2",
        "event.remindAttendeesMins": "120",
        "followUpUser.tfoUserId": TARGET_MEMBER_ID,
        "followUpUser.role.id": "7",
        "followUpUser.clubId": "291",
        "followUpUser.clubLocationId": "3586",
        "followUpLog.followUpAction": "2",  # 2 for Email
        "memberStudioSalesDefaultAccount": TARGET_MEMBER_ID,
        "memberStudioSupportDefaultAccount": TARGET_MEMBER_ID,
        "ptSalesDefaultAccount": TARGET_MEMBER_ID,
        "ptSupportDefaultAccount": TARGET_MEMBER_ID
    }
    
    print(f"   URL: {followup_url}")
    print(f"   Data: {email_form_data}")
    
    email_response = auth_service.session.post(
        followup_url,
        data=email_form_data,
        headers=headers,
        timeout=30,
        verify=False
    )
    
    print(f"   Status: {email_response.status_code}")
    print(f"   Final URL: {email_response.url}")
    
    # Save response for debugging
    with open("email_response_debug.html", "w", encoding="utf-8") as f:
        f.write(email_response.text)
    print("   💾 Saved Email response to email_response_debug.html")
    
    # Check if Email was successful
    if email_response.ok:
        response_text = email_response.text.lower()
        if "success" in response_text or "sent" in response_text or "saved" in response_text:
            print("   ✅ Email sent successfully!")
            email_success = True
        else:
            print("   ⚠️ Email response unclear - checking content...")
            print(f"   Response preview: {email_response.text[:500]}...")
            email_success = False
    else:
        print(f"   ❌ Email failed with status {email_response.status_code}")
        email_success = False
    
    print()
    print("📊 FINAL RESULTS:")
    print("=" * 30)
    print(f"SMS: {'✅ SUCCESS' if sms_success else '❌ FAILED'}")
    print(f"Email: {'✅ SUCCESS' if email_success else '❌ FAILED'}")
    
    if sms_success and email_success:
        print("\n🎉 BOTH MESSAGES SENT SUCCESSFULLY!")
        print("The correct endpoints are working!")
    elif sms_success or email_success:
        print("\n⚠️ PARTIAL SUCCESS - One message type worked")
    else:
        print("\n❌ BOTH MESSAGES FAILED")
        print("Need to investigate further...")
    
    return sms_success and email_success

if __name__ == "__main__":
    send_message_correct_endpoints() 