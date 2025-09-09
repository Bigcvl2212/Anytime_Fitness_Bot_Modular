#!/usr/bin/env python3
"""
Debug script to check what damage we caused to ClubOS
"""

import requests
import logging
import sys
import os
from bs4 import BeautifulSoup

# Add path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.services.authentication.secure_secrets_manager import SecureSecretsManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_clubos_damage():
    """Check what we broke in ClubOS"""
    
    # Get credentials
    secrets_manager = SecureSecretsManager()
    username = secrets_manager.get_secret('clubos-username')
    password = secrets_manager.get_secret('clubos-password')
    
    session = requests.Session()
    base_url = "https://anytime.club-os.com"
    
    # Authenticate
    print("🔐 Authenticating to check damage...")
    login_url = f"{base_url}/action/Login/view?__fsk=1221801756"
    login_response = session.get(login_url, verify=False)
    
    soup = BeautifulSoup(login_response.text, 'html.parser')
    source_page = soup.find('input', {'name': '_sourcePage'})
    fp_token = soup.find('input', {'name': '__fp'})
    
    login_data = {
        'login': 'Submit',
        'username': username,
        'password': password,
        '_sourcePage': source_page.get('value') if source_page else '',
        '__fp': fp_token.get('value') if fp_token else ''
    }
    
    auth_response = session.post(f"{base_url}/action/Login", data=login_data, verify=False)
    
    if session.cookies.get('JSESSIONID'):
        print("✅ Authentication successful")
    else:
        print("❌ Authentication failed")
        return
    
    # Check the problematic members
    problem_members = [
        ("192224494", "Kymberley Marr"),
        ("189425730", "Dennis Rost")
    ]
    
    for member_id, member_name in problem_members:
        print(f"\n🔍 Checking member {member_name} (ID: {member_id})")
        
        try:
            # Try to access member profile
            profile_url = f"{base_url}/action/LeadProfile/view/{member_id}"
            profile_response = session.get(profile_url, verify=False)
            
            print(f"   Profile access: HTTP {profile_response.status_code}")
            
            if profile_response.status_code != 200:
                print(f"   ❌ Cannot access profile - HTTP {profile_response.status_code}")
                print(f"   Response preview: {profile_response.text[:200]}")
            else:
                print("   ✅ Profile accessible")
                
                # Check for any error messages in the profile
                soup = BeautifulSoup(profile_response.text, 'html.parser')
                error_divs = soup.find_all(['div', 'span'], class_=['error', 'alert', 'warning'])
                if error_divs:
                    print("   ⚠️ Found error messages:")
                    for error in error_divs:
                        print(f"      {error.get_text().strip()}")
            
            # Try to access follow-up records for this member
            followup_url = f"{base_url}/action/FollowUp/view?followUpUserId={member_id}"
            followup_response = session.get(followup_url, verify=False)
            
            print(f"   Follow-up access: HTTP {followup_response.status_code}")
            
            if followup_response.status_code == 200:
                # Look for any recent follow-up records we might have created
                soup = BeautifulSoup(followup_response.text, 'html.parser')
                
                # Look for recent entries (today's date)
                from datetime import datetime
                today = datetime.now().strftime("%m/%d/%Y")
                
                if today in followup_response.text:
                    print(f"   ⚠️ Found recent follow-up records from today")
                    
                # Look for our test messages
                test_messages = [
                    "Test message from updated messaging client",
                    "Hey Dennis! This is a test message from the updated messaging system"
                ]
                
                for msg in test_messages:
                    if msg in followup_response.text:
                        print(f"   ⚠️ Found our test message: '{msg[:30]}...'")
                        
        except Exception as e:
            print(f"   ❌ Error checking member: {e}")
    
    # Check general dashboard for any system alerts
    print(f"\n🏠 Checking dashboard for system alerts...")
    dashboard_response = session.get(f"{base_url}/action/Dashboard/view", verify=False)
    
    if dashboard_response.status_code == 200:
        soup = BeautifulSoup(dashboard_response.text, 'html.parser')
        alerts = soup.find_all(['div', 'span'], class_=['alert', 'error', 'warning', 'notification'])
        
        if alerts:
            print("   ⚠️ System alerts found:")
            for alert in alerts:
                text = alert.get_text().strip()
                if text and len(text) > 10:  # Filter out empty/short alerts
                    print(f"      {text}")
        else:
            print("   ✅ No obvious system alerts")
    
    print(f"\n📊 Damage assessment complete")

if __name__ == "__main__":
    check_clubos_damage()
