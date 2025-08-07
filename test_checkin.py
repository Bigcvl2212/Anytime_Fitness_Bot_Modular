#!/usr/bin/env python3
"""
Test Member Check-in System - Pick first member and test
"""

import sys
import os
import requests
import json
import sqlite3
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_member_checkin():
    """Test the check-in system with the first available member"""
    
    print("🏋️ Testing Member Check-in System")
    print("=" * 40)
    
    # Get first member from database
    try:
        conn = sqlite3.connect('gym_bot.db')
        cursor = conn.cursor()
        
        # Get first member with a valid ID
        cursor.execute("SELECT id, email FROM members WHERE id IS NOT NULL LIMIT 1")
        member = cursor.fetchone()
        conn.close()
        
        if not member:
            print("❌ No members found in database")
            return
        
        member_id, email = member
        print(f"🎯 Testing with Member ID: {member_id}, Email: {email}")
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return
    
    # Set up API call
    base_url = "https://clubhub-ios-api.anytimefitness.com"
    club_id = 1156
    door_id = 772
    
    # Get auth token from user
    print("\n🔑 Need ClubHub authentication token...")
    auth_token = input("Enter Bearer token (from ClubHub app/browser): ").strip()
    
    if not auth_token:
        print("❌ No auth token provided")
        return
    
    # Prepare check-in data
    checkin_time = datetime.now()
    formatted_date = checkin_time.strftime("%Y-%m-%dT%H:%M:%S-05:00")
    
    checkin_data = {
        "date": formatted_date,
        "door": {"id": door_id},
        "club": {"id": club_id},
        "manual": True
    }
    
    # Set up headers
    headers = {
        "Host": "clubhub-ios-api.anytimefitness.com",
        "Content-Type": "application/json",
        "API-version": "1",
        "Accept": "application/json",
        "User-Agent": "ClubHub Store/2.15.1 (com.anytimefitness.Club-Hub; build:1007; iOS 18.5.0) Alamofire/5.6.4",
        "Accept-Language": "en-US",
        "Authorization": f"Bearer {auth_token}",
        "Accept-Encoding": "br;q=1.0, gzip;q=0.9, deflate;q=0.8",
        "Connection": "keep-alive"
    }
    
    # Make the API call
    url = f"{base_url}/api/members/{member_id}/usages"
    
    print(f"\n🚀 Attempting check-in...")
    print(f"URL: {url}")
    print(f"Data: {json.dumps(checkin_data, indent=2)}")
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(checkin_data))
        
        print(f"\n📡 Response Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.text:
            print(f"Response Body: {response.text}")
        
        if response.status_code == 200:
            print("✅ SUCCESS! Member checked in successfully!")
        elif response.status_code == 401:
            print("❌ UNAUTHORIZED - Auth token may be expired")
        elif response.status_code == 404:
            print("❌ NOT FOUND - Member ID may not exist in ClubHub")
        else:
            print(f"❌ FAILED - Status code: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    test_member_checkin()
