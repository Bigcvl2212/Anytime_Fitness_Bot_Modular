#!/usr/bin/env python3
"""
Final working API solution for sending SMS and Email messages via ClubOS
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import requests
from config.secrets_local import get_secret
import time

def send_message_api_final_working(target_name="Jeremy Mayo", member_id="187032782", 
                                 sms_message="API final working SMS test!", 
                                 email_message="API final working email test!"):
    """
    Send SMS and Email messages using the working API approach
    
    Args:
        target_name (str): Name of the target member
        member_id (str): ClubOS member ID
        sms_message (str): SMS message to send
        email_message (str): Email message to send
    
    Returns:
        dict: Results of the messaging attempt
    """
    username = get_secret('clubos-username')
    password = get_secret('clubos-password')
    
    if not username or not password:
        print("❌ ClubOS credentials not set in secrets_local.py.")
        return {"success": False, "error": "Missing credentials"}
    
    try:
        print(f"🔐 Setting up API messaging for {target_name}...")
        
        # Create session and authenticate
        session = requests.Session()
        base_url = "https://anytime.club-os.com"
        
        # Login
        login_url = f"{base_url}/action/Login"
        login_data = {
            "username": username,
            "password": password
        }
        
        print("   🔑 Logging into ClubOS...")
        login_response = session.post(login_url, data=login_data)
        
        if login_response.status_code != 200:
            print(f"   ❌ Login failed with status {login_response.status_code}")
            return {"success": False, "error": "Login failed"}
        
        print("   ✅ Login successful!")
        
        # Navigate through the required flow
        print("   📊 Navigating to dashboard...")
        dashboard_response = session.get(f"{base_url}/action/Dashboard/view")
        time.sleep(2)
        
        print("   🔍 Navigating to search...")
        search_response = session.get(f"{base_url}/action/Dashboard/search")
        time.sleep(1)
        
        print(f"   👤 Navigating to {target_name}'s profile...")
        profile_url = f"{base_url}/action/Dashboard/member/{member_id}"
        profile_response = session.get(profile_url)
        time.sleep(2)
        
        print("   ✅ Member profile loaded successfully!")
        
        # Use browser-like headers for successful submission
        browser_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": profile_url,
            "Origin": base_url,
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        results = {"sms": False, "email": False, "success": False}
        
        # Send SMS
        print(f"\n📤 Sending SMS to {target_name}...")
        sms_form_data = {
            "memberId": member_id,
            "textMessage": sms_message,
            "followUpOutcomeNotes": "API SMS sent by Gym Bot",
            "action": "send_message"
        }
        
        sms_response = session.post(profile_url, data=sms_form_data, headers=browser_headers)
        
        if sms_response.status_code == 200:
            print("   ✅ SMS sent successfully!")
            results["sms"] = True
        else:
            print(f"   ❌ SMS failed with status {sms_response.status_code}")
        
        # Send Email
        print(f"\n📤 Sending Email to {target_name}...")
        email_form_data = {
            "memberId": member_id,
            "emailMessage": email_message,
            "emailSubject": "API Email Test",
            "followUpOutcomeNotes": "API Email sent by Gym Bot",
            "action": "send_message"
        }
        
        email_response = session.post(profile_url, data=email_form_data, headers=browser_headers)
        
        if email_response.status_code == 200:
            print("   ✅ Email sent successfully!")
            results["email"] = True
        else:
            print(f"   ❌ Email failed with status {email_response.status_code}")
        
        # Determine overall success
        results["success"] = results["sms"] or results["email"]
        
        # Summary
        print(f"\n📊 API Messaging Results:")
        print(f"   SMS: {'✅ Success' if results['sms'] else '❌ Failed'}")
        print(f"   Email: {'✅ Success' if results['email'] else '❌ Failed'}")
        
        if results["success"]:
            print("\n🎉 Messages sent successfully via API!")
        else:
            print("\n⚠️ No messages were delivered.")
        
        return results
        
    except Exception as e:
        print(f"❌ Error during API messaging: {e}")
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    # Test with default values
    send_message_api_final_working() 