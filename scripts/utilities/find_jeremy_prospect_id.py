#!/usr/bin/env python3
"""
Find Jeremy Mayo's prospectID from ClubHub master contact list
"""

import requests
import json
import re
from typing import Dict, Any, Optional

def get_clubhub_auth_token() -> Optional[str]:
    """Get ClubHub authentication token from the HAR file"""
    
    # Read the ClubHub endpoints file to get auth token
    try:
        with open('clubhub_api_endpoints.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Look for login requests to extract auth token
        for api_call in data.get('api_calls', []):
            if 'login' in api_call['path'].lower():
                auth_header = api_call['headers'].get('Authorization', '')
                if auth_header.startswith('Bearer '):
                    return auth_header.replace('Bearer ', '')
        
        # If no login found, look for any Authorization header
        for api_call in data.get('api_calls', []):
            auth_header = api_call['headers'].get('Authorization', '')
            if auth_header.startswith('Bearer '):
                return auth_header.replace('Bearer ', '')
                
    except Exception as e:
        print(f"❌ Error reading ClubHub endpoints: {e}")
    
    return None

def fetch_clubhub_members(token: str) -> Optional[Dict[str, Any]]:
    """Fetch the master contact list from ClubHub"""
    
    url = "https://clubhub-ios-api.anytimefitness.com/api/clubs/1156/members/all"
    
    headers = {
        "Host": "clubhub-ios-api.anytimefitness.com",
        "API-version": "1",
        "Accept": "application/json",
        "User-Agent": "ClubHub Store/2.15.1 (com.anytimefitness.Club-Hub; build:1007; iOS 18.5.0) Alamofire/5.6.4",
        "Accept-Language": "en-US",
        "Authorization": f"Bearer {token}",
        "Accept-Encoding": "br;q=1.0, gzip;q=0.9, deflate;q=0.8"
    }
    
    try:
        print("🔍 Fetching ClubHub master contact list...")
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            print("✅ Successfully fetched contact list")
            return response.json()
        else:
            print(f"❌ Failed to fetch contact list: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error fetching contact list: {e}")
        return None

def find_jeremy_mayo(members_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Find Jeremy Mayo in the members data"""
    
    print("🔍 Searching for Jeremy Mayo in contact list...")
    
    # Look for members array
    members = members_data.get('members', [])
    if not members:
        print("❌ No members array found in response")
        print(f"Response keys: {list(members_data.keys())}")
        return None
    
    print(f"📊 Found {len(members)} members in contact list")
    
    # Search for Jeremy Mayo
    jeremy_matches = []
    
    for member in members:
        first_name = member.get('firstName', '').lower()
        last_name = member.get('lastName', '').lower()
        full_name = f"{first_name} {last_name}".strip()
        
        if 'jeremy' in first_name and 'mayo' in last_name:
            jeremy_matches.append(member)
            print(f"✅ Found Jeremy Mayo: {member.get('firstName')} {member.get('lastName')}")
            print(f"   Prospect ID: {member.get('prospectId')}")
            print(f"   Member ID: {member.get('memberId')}")
            print(f"   User ID: {member.get('userId')}")
            print(f"   Email: {member.get('email')}")
            print()
    
    if not jeremy_matches:
        print("❌ Jeremy Mayo not found in contact list")
        print("🔍 Checking first 10 members for reference:")
        for i, member in enumerate(members[:10]):
            print(f"   {i+1}. {member.get('firstName')} {member.get('lastName')} - ID: {member.get('prospectId')}")
        return None
    
    return jeremy_matches[0] if jeremy_matches else None

def main():
    """Main function to find Jeremy Mayo's prospectID"""
    
    print("🚀 Starting search for Jeremy Mayo's prospectID...")
    
    # Get auth token
    token = get_clubhub_auth_token()
    if not token:
        print("❌ Could not extract auth token from HAR file")
        return
    
    print("✅ Found ClubHub auth token")
    
    # Fetch members list
    members_data = fetch_clubhub_members(token)
    if not members_data:
        print("❌ Could not fetch members data")
        return
    
    # Find Jeremy Mayo
    jeremy = find_jeremy_mayo(members_data)
    if not jeremy:
        print("❌ Jeremy Mayo not found")
        return
    
    # Extract prospectID
    prospect_id = jeremy.get('prospectId')
    if prospect_id:
        print(f"🎯 Jeremy Mayo's Prospect ID: {prospect_id}")
        
        # Check if it's 8 digits
        if re.match(r'^\d{8}$', str(prospect_id)):
            print("✅ Prospect ID is 8 digits as expected!")
        else:
            print(f"⚠️  Prospect ID is {len(str(prospect_id))} digits, not 8")
    else:
        print("❌ No prospectID found for Jeremy Mayo")
        print(f"Available fields: {list(jeremy.keys())}")

if __name__ == "__main__":
    main() 