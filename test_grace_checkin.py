#!/usr/bin/env python3
"""
Test member check-in on Grace Sphatt
"""

import sys
import os
import sqlite3
import requests
import json
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_grace_checkin():
    """Test checking in Grace Sphatt"""
    
    print("🧪 Testing member check-in on Grace Sphatt...")
    
    # First, find Grace in the database
    try:
        conn = sqlite3.connect('gym_bot.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, full_name, email FROM members WHERE full_name LIKE ?", ('%grace%',))
        grace = cursor.fetchone()
        
        if grace:
            member_id, name, email = grace
            print(f"✅ Found Grace: ID={member_id}, Name={name}, Email={email}")
        else:
            print("❌ Grace not found in database")
            conn.close()
            return
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return
    
    # Get auth token
    auth_token = input("Enter ClubHub Bearer token: ").strip()
    if not auth_token:
        print("❌ No auth token provided")
        return
    
    # Prepare check-in data
    checkin_data = {
        "date": datetime.now().strftime("%Y-%m-%dT%H:%M:%S-05:00"),
        "door": {"id": 772},  # Main door ID from API logs
        "club": {"id": 1156},  # Your club ID
        "manual": True
    }
    
    # Make the API call
    url = f"https://clubhub-ios-api.anytimefitness.com/api/members/{member_id}/usages"
    
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
    
    print(f"🔄 Attempting to check in Grace (ID: {member_id})...")
    print(f"📍 Check-in data: {json.dumps(checkin_data, indent=2)}")
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(checkin_data))
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📄 Response Headers: {dict(response.headers)}")
        print(f"📝 Response Text: {response.text}")
        
        if response.status_code == 200:
            print("✅ SUCCESS! Grace has been checked in!")
        else:
            print(f"❌ FAILED! Status code: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Network error: {e}")

if __name__ == "__main__":
    test_grace_checkin()
