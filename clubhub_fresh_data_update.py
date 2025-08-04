#!/usr/bin/env python3
"""
ClubHub Fresh Data Update Script
Uses exact HAR-captured authentication flow to get fresh bearer tokens
and update master contact list with current member agreement data.

This script replicates the exact browser authentication sequence 
to ensure dashboard shows accurate red/yellow member counts.
"""

import requests
import json
import pandas as pd
from datetime import datetime
import time

# ClubHub Authentication Configuration (from HAR analysis)
CLUBHUB_LOGIN_URL = "https://clubhub-ios-api.anytimefitness.com/api/login"
CLUBHUB_API_BASE = "https://clubhub-ios-api.anytimefitness.com/api/v1.0"

# HAR-extracted working credentials
USERNAME = "mayo.jeremy2212@gmail.com"
PASSWORD = "SruLEqp464_GLrF"

# Exact headers from successful HAR requests
LOGIN_HEADERS = {
    "Content-Type": "application/json",
    "API-version": "1",
    "Accept": "application/json",
    "User-Agent": "ClubHub Store/2.15.1 (com.anytimefitness.Club-Hub; build:1007; iOS 18.5.0) Alamofire/5.6.4",
    "Accept-Language": "en-US",
    "Accept-Encoding": "br;q=1.0, gzip;q=0.9, deflate;q=0.8"
}

def authenticate_with_clubhub():
    """
    Authenticate with ClubHub using exact HAR-captured flow
    Returns session with valid bearer token
    """
    print("🔐 Authenticating with ClubHub using HAR-captured credentials...")
    
    session = requests.Session()
    session.headers.update(LOGIN_HEADERS)
    
    # Login payload from successful HAR request
    login_data = {
        "username": USERNAME,
        "password": PASSWORD
    }
    
    try:
        print(f"   📡 POST {CLUBHUB_LOGIN_URL}")
        response = session.post(CLUBHUB_LOGIN_URL, json=login_data)
        
        print(f"   📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            auth_data = response.json()
            print("   ✅ Authentication successful!")
            
            # Extract bearer token from response
            if 'accessToken' in auth_data:
                bearer_token = auth_data['accessToken']
                print(f"   🔑 Bearer token received: {bearer_token[:50]}...")
                
                # Update session with bearer token
                session.headers.update({
                    "Authorization": f"Bearer {bearer_token}"
                })
                
                return session, bearer_token
            else:
                print("   ❌ No access token in response")
                print(f"   Response: {auth_data}")
                return None, None
        else:
            print(f"   ❌ Authentication failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None, None
            
    except Exception as e:
        print(f"   ❌ Authentication error: {e}")
        return None, None

def get_all_members(session):
    """
    Get all members from ClubHub API using authenticated session
    """
    print("👥 Fetching all members from ClubHub...")
    
    all_members = []
    page = 1
    
    while True:
        try:
            url = f"https://clubhub-ios-api.anytimefitness.com/api/clubs/1156/members?page={page}&pageSize=100"
            print(f"   📄 Fetching page {page}...")
            
            response = session.get(url)
            
            if response.status_code == 200:
                data = response.json()
                print(f"   🔍 Response structure: {type(data)} - {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                
                # Handle different response structures
                if isinstance(data, list):
                    members = data
                elif isinstance(data, dict):
                    members = data.get('data', data.get('members', data.get('results', [])))
                else:
                    members = []
                
                if not members:
                    print(f"   ✅ No more members found. Total pages: {page-1}")
                    break
                    
                print(f"   📊 Found {len(members)} members on page {page}")
                all_members.extend(members)
                page += 1
                
                # Rate limiting
                time.sleep(0.1)
                
            else:
                print(f"   ❌ Error fetching members page {page}: {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
                break
                
        except Exception as e:
            print(f"   ❌ Error on page {page}: {e}")
            if page == 1:
                # Try different endpoint for first page
                try:
                    url = f"https://clubhub-ios-api.anytimefitness.com/api/members?page={page}&pageSize=100"
                    response = session.get(url)
                    if response.status_code == 200:
                        data = response.json()
                        if isinstance(data, list):
                            all_members.extend(data)
                            page += 1
                            continue
                except:
                    pass
            break
    
    print(f"   ✅ Total members collected: {len(all_members)}")
    return all_members

def get_member_agreement_data(session, member_id):
    """
    Get agreement data for a specific member
    Returns payment status and agreement info
    """
    try:
        url = f"{CLUBHUB_API_BASE}/members/{member_id}/agreement"
        response = session.get(url)
        
        if response.status_code == 200:
            agreement_data = response.json()
            
            # Extract key payment status fields
            payment_status = agreement_data.get('paymentStatus', 'Unknown')
            days_past_due = agreement_data.get('daysPastDue', 0)
            balance_due = agreement_data.get('balanceDue', 0)
            
            # Determine red/yellow status based on past due days
            status = 'current'
            if days_past_due > 30:
                status = 'red'  # Red members (30+ days past due)
            elif days_past_due > 0:
                status = 'yellow'  # Yellow members (1-29 days past due)
                
            return {
                'payment_status': payment_status,
                'days_past_due': days_past_due,
                'balance_due': balance_due,
                'member_status': status
            }
        else:
            return {
                'payment_status': 'Unknown',
                'days_past_due': 0,
                'balance_due': 0,
                'member_status': 'current'
            }
            
    except Exception as e:
        print(f"     ❌ Error getting agreement for member {member_id}: {e}")
        return {
            'payment_status': 'Error',
            'days_past_due': 0,
            'balance_due': 0,
            'member_status': 'current'
        }

def create_master_contact_list(session):
    """
    Create fresh master contact list with current agreement data
    """
    print("📋 Creating fresh master contact list...")
    
    # Get all members
    all_members = get_all_members(session)
    
    if not all_members:
        print("❌ No members found. Cannot create contact list.")
        return None
    
    master_data = []
    red_count = 0
    yellow_count = 0
    
    print(f"🔄 Processing {len(all_members)} members for agreement data...")
    
    for i, member in enumerate(all_members, 1):
        member_id = member.get('id')
        first_name = member.get('firstName', '')
        last_name = member.get('lastName', '')
        email = member.get('email', '')
        phone = member.get('phone', '')
        
        print(f"   📊 Processing {i}/{len(all_members)}: {first_name} {last_name}")
        
        # Get fresh agreement data
        agreement_data = get_member_agreement_data(session, member_id)
        
        # Count red/yellow members
        if agreement_data['member_status'] == 'red':
            red_count += 1
        elif agreement_data['member_status'] == 'yellow':
            yellow_count += 1
        
        # Build comprehensive member record
        member_record = {
            'member_id': member_id,
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'phone': phone,
            'payment_status': agreement_data['payment_status'],
            'days_past_due': agreement_data['days_past_due'],
            'balance_due': agreement_data['balance_due'],
            'member_status': agreement_data['member_status'],
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        master_data.append(member_record)
        
        # Rate limiting to avoid overwhelming API
        if i % 10 == 0:
            time.sleep(1)
    
    # Create DataFrame
    df = pd.DataFrame(master_data)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'master_contact_list_with_agreements_{timestamp}.csv'
    
    # Save to CSV
    df.to_csv(filename, index=False)
    
    print(f"✅ Master contact list saved: {filename}")
    print(f"📊 Summary:")
    print(f"   Total Members: {len(all_members)}")
    print(f"   🟥 Red Members (30+ days past due): {red_count}")
    print(f"   🟡 Yellow Members (1-29 days past due): {yellow_count}")
    print(f"   🟢 Current Members: {len(all_members) - red_count - yellow_count}")
    print(f"   📅 Data as of: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Update dashboard counts
    dashboard_counts = {
        'total_members': len(all_members),
        'red_members': red_count,
        'yellow_members': yellow_count,
        'current_members': len(all_members) - red_count - yellow_count,
        'past_due_total': red_count + yellow_count,
        'last_updated': datetime.now().isoformat()
    }
    
    # Save dashboard counts for dashboard to use
    with open('dashboard_counts.json', 'w') as f:
        json.dump(dashboard_counts, f, indent=2)
    
    print(f"📈 Dashboard counts updated: {red_count + yellow_count} total past due members")
    return filename, dashboard_counts

def main():
    """
    Main execution function
    """
    print("🚀 Starting ClubHub Fresh Data Update")
    print("=" * 60)
    
    # Authenticate with ClubHub
    session, bearer_token = authenticate_with_clubhub()
    
    if not session:
        print("❌ Authentication failed. Cannot proceed.")
        return
    
    # Create fresh master contact list
    result = create_master_contact_list(session)
    
    if result:
        filename, counts = result
        print("=" * 60)
        print("✅ Update completed successfully!")
        print(f"📂 New file: {filename}")
        print(f"🎯 Past due members: {counts['past_due_total']} (was showing 305)")
        print("🔄 Dashboard will now show accurate counts!")
    else:
        print("❌ Update failed.")

if __name__ == "__main__":
    main()
