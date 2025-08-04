#!/usr/bin/env python3
"""
Extract Fresh ClubHub Data Using HAR Authentication
Uses the exact authentication pattern from successful HAR capture.
"""

import pandas as pd
import json
import time
import requests
from datetime import datetime
import os

# Successful authentication from HAR analysis
CLUBHUB_LOGIN_URL = "https://clubhub-ios-api.anytimefitness.com/api/login"
CLUBHUB_API_BASE = "https://clubhub-ios-api.anytimefitness.com/api/v1.0"

# Headers from successful HAR capture
HEADERS = {
    "Content-Type": "application/json",
    "API-version": "1",
    "Accept": "application/json",
    "User-Agent": "ClubHub Store/2.15.1 (com.anytimefitness.Club-Hub; build:1007; iOS 18.5.0) Alamofire/5.6.4",
    "Accept-Language": "en-US",
    "Accept-Encoding": "br;q=1.0, gzip;q=0.9, deflate;q=0.8"
}

# Login credentials from successful HAR login
LOGIN_PAYLOAD = {
    "username": "mayo.jeremy2212@gmail.com",
    "password": "SruLEqp464_GLrF"
}

def login_and_get_token():
    """Login to ClubHub and get fresh bearer token"""
    print("🔐 Logging into ClubHub with HAR credentials...")
    
    session = requests.Session()
    session.headers.update(HEADERS)
    
    try:
        # Login request
        response = session.post(CLUBHUB_LOGIN_URL, json=LOGIN_PAYLOAD, verify=False, timeout=30)
        
        if response.status_code == 200:
            print("✅ Login successful!")
            
            # Parse response for token
            try:
                login_data = response.json()
                if 'accessToken' in login_data:
                    bearer_token = login_data['accessToken']
                elif 'access_token' in login_data:
                    bearer_token = login_data['access_token']
                elif 'token' in login_data:
                    bearer_token = login_data['token']
                else:
                    print("❌ No token found in login response")
                    print(f"Response: {response.text[:500]}")
                    return None
                
                # Update session with bearer token
                session.headers.update({
                    "Authorization": f"Bearer {bearer_token}"
                })
                
                print(f"🎫 Got bearer token: {bearer_token[:50]}...")
                return session, bearer_token
                
            except Exception as e:
                print(f"❌ Error parsing login response: {e}")
                print(f"Response text: {response.text[:500]}")
                return None
                
        else:
            print(f"❌ Login failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def get_members_with_agreements(session):
    """Get all members with agreement data"""
    print("📋 Fetching members with agreement data...")
    
    all_members = []
    page = 1
    
    while True:
        print(f"   📄 Fetching page {page}...")
        
        # Get members for club 1156
        url = f"https://clubhub-ios-api.anytimefitness.com/api/clubs/1156/members"
        params = {
            "page": page,
            "pageSize": 100
        }
        
        try:
            response = session.get(url, params=params, verify=False, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                # Handle different response formats
                if isinstance(data, list):
                    members = data
                elif isinstance(data, dict):
                    members = data.get('data', data.get('results', data.get('members', [])))
                else:
                    members = []
                
                if not members:
                    print(f"   ✅ No more members found. Total pages: {page-1}")
                    break
                
                print(f"   📊 Found {len(members)} members on page {page}")
                
                # For each member, get their agreement data
                for member in members:
                    if isinstance(member, dict):
                        member_id = member.get('id')
                        if member_id:
                            try:
                                # Get agreement data
                                agreement_url = f"https://clubhub-ios-api.anytimefitness.com/api/members/{member_id}/agreement"
                                agreement_response = session.get(agreement_url, verify=False, timeout=30)
                                
                                if agreement_response.status_code == 200:
                                    agreement_data = agreement_response.json()
                                    member['agreement_data'] = agreement_data
                                else:
                                    member['agreement_data'] = None
                                    
                            except Exception as e:
                                print(f"     ⚠️ Error getting agreement for member {member_id}: {e}")
                                member['agreement_data'] = None
                
                all_members.extend(members)
                page += 1
                
                # Respect rate limits
                time.sleep(0.5)
                
            else:
                print(f"   ❌ Error fetching page {page}: {response.status_code}")
                if response.status_code == 401:
                    print("   🔐 Authentication expired")
                break
                
        except Exception as e:
            print(f"   ❌ Error on page {page}: {e}")
            break
    
    print(f"🎯 Total members collected: {len(all_members)}")
    return all_members

def process_and_save_data(members_data):
    """Process the member data and save to CSV"""
    print("💾 Processing and saving member data...")
    
    processed_members = []
    
    for member in members_data:
        try:
            # Extract basic member info
            member_info = {
                'id': member.get('id'),
                'first_name': member.get('firstName'),
                'last_name': member.get('lastName'),
                'email': member.get('email'),
                'phone': member.get('phone'),
                'status': member.get('status'),
                'membership_type': member.get('membershipType'),
                'join_date': member.get('joinDate'),
                'last_visit': member.get('lastVisit'),
            }
            
            # Extract agreement data
            agreement = member.get('agreement_data', {})
            if agreement:
                member_info.update({
                    'agreement_status': agreement.get('status'),
                    'next_billing_date': agreement.get('nextBillingDate'),
                    'billing_amount': agreement.get('billingAmount'),
                    'past_due_amount': agreement.get('pastDueAmount'),
                    'agreement_type': agreement.get('agreementType'),
                    'freeze_status': agreement.get('freezeStatus'),
                })
            
            processed_members.append(member_info)
            
        except Exception as e:
            print(f"   ⚠️ Error processing member {member.get('id', 'unknown')}: {e}")
    
    # Convert to DataFrame
    df = pd.DataFrame(processed_members)
    
    # Save to CSV with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"master_contact_list_with_agreements_{timestamp}.csv"
    
    df.to_csv(filename, index=False)
    print(f"✅ Data saved to: {filename}")
    print(f"📊 Total records: {len(df)}")
    
    # Show past due summary
    if 'past_due_amount' in df.columns:
        past_due = df[df['past_due_amount'].notna() & (df['past_due_amount'] > 0)]
        print(f"💰 Past due members: {len(past_due)}")
    
    return filename

def main():
    """Main execution function"""
    print("🚀 EXTRACTING FRESH CLUBHUB DATA WITH HAR AUTHENTICATION")
    print("=" * 60)
    
    # Login and get authenticated session
    auth_result = login_and_get_token()
    if not auth_result:
        print("❌ Failed to authenticate")
        return
    
    session, token = auth_result
    
    # Get members with agreement data
    members_data = get_members_with_agreements(session)
    
    if members_data:
        # Process and save the data
        filename = process_and_save_data(members_data)
        print(f"\n🎉 SUCCESS! Fresh data saved to: {filename}")
    else:
        print("❌ No member data retrieved")

if __name__ == "__main__":
    main()
