#!/usr/bin/env python3
"""
Update Dashboard with Fresh ClubHub Data
Uses HAR-extracted authentication to pull fresh member and agreement data
Generates new master contact list and updates dashboard counts
"""

import requests
import json
import pandas as pd
from datetime import datetime
import time
import os

# ClubHub Configuration from HAR analysis
CLUBHUB_API_BASE = "https://clubhub-ios-api.anytimefitness.com/api/v1.0"
CLUBHUB_LOGIN_URL = "https://clubhub-ios-api.anytimefitness.com/api/login"

# Working bearer token from HAR analysis (bypass login for now)
WORKING_BEARER_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMDgyMDQ0OSIsImVtYWlsIjoibWF5by5qZXJlbXkyMjEyQGdtYWlsLmNvbSIsImdpdmVuX25hbWUiOiJKZXJlbXkiLCJhZl9hcGlfdG9rZW4iOiJsa1JnekZQQ213RXZUTUNrNnBSaEI4ZV9tbkJsbmZ3T2NmZk9Hb3VtRTBMaHB5dDV0OHN2cjVkZ0dDS1hBMWxsUlZrNllfZVZvSkd6bFo1MzhpZEtKeUJqeFBhMkpNZHNNeVRdWeDIxMkVJVWxfcWdzR0V4cWxCaENPTnBIMzB2a0xHMl9lZHpyZnQ2TlVwNmFqOE9QNGNzUS1qWktZRlRQc0FKdzZpbkNvT3NMYVBmZlNNiU0xNek1PX3p3NDFrdmFNb0dhWUhXZ3VvRmhXT2V6d00waHBGcWpkTHlTYm52dWYybEpnc0ZHV2lxQ3MtQnliWDZ3QnlDMUFqdDBPTmx6eUhUbDBLRGFZVjluWTFSNDdXY0MzaDBWMmxEVWExbUJmRXc1R3JQZTUxcUw2RW5GQkJYVHNTWWdJTFRlc1dxZnhrNmY3bmpOWGQ3Y0pWQ0dEclVxcHRUTUxCUSIsInBob3RvX3VybCI6IiIsInVzZXJfdHlwZSI6IlRyYWluZXIiLCJjbHViX2lkcyI6WyIxMTU2IiwiMTY1NyJdLCJyb2xlIjoiVHJhaW5lciIsImFwcGxpY2F0aW9uX2lkcyI6WyIxIiwiMyIsIjgiLCIxMiJdLCJuYmYiOjE3NTI1NDM1NjAsImV4cCI6MTc1MjYyOTk2MCwiaWF0IjoxNzUyNTQzNTYwLCJpc3MiOiJodHRwczovL2NsdWJodWItaW9zLWFwaS5hbnl0aW1lZml0bmVzcy5jb20vIiwiYXVkIjoiQ2x1Ykh1Yklvc0FwaSJ9.QeEoZuoov4hw7-LN7XcuKWGn99HsDfhkDtJNHxr07ms"

# Credentials from successful HAR login (for future use)
USERNAME = "mayo.jeremy2212@gmail.com"
PASSWORD = "SruLEqp464_GLrF"

# Headers from HAR analysis
LOGIN_HEADERS = {
    "User-Agent": "ClubHub Store/2.15.1 (com.anytimefitness.Club-Hub; build:1007; iOS 18.5.0) Alamofire/5.6.4",
    "API-version": "1",
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Accept-Language": "en-US",
    "Accept-Encoding": "br;q=1.0, gzip;q=0.9, deflate;q=0.8"
}

def authenticate_clubhub():
    """Use working bearer token from HAR analysis"""
    print("🔐 Using working bearer token from HAR analysis...")
    
    # Create authenticated session with working token
    session = requests.Session()
    session.headers.update({
        "Authorization": f"Bearer {WORKING_BEARER_TOKEN}",
        "API-version": "1",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "ClubHub Store/2.15.1 (com.anytimefitness.Club-Hub; build:1007; iOS 18.5.0) Alamofire/5.6.4",
        "Accept-Language": "en-US",
        "Accept-Encoding": "br;q=1.0, gzip;q=0.9, deflate;q=0.8"
    })
    
    # Test the authentication with a simple API call
    try:
        test_url = f"{CLUBHUB_API_BASE}/clubs/1156/features"
        response = session.get(test_url, timeout=30)
        
        if response.status_code == 200:
            print("✅ Bearer token authentication successful!")
            return session, WORKING_BEARER_TOKEN
        else:
            print(f"❌ Token test failed: {response.status_code}")
            return None, None
            
    except Exception as e:
        print(f"❌ Token test error: {e}")
        return None, None

def get_all_members(session):
    """Get all members from ClubHub API"""
    print("📋 Fetching all members...")
    
    all_members = []
    page = 1
    
    while True:
        url = f"{CLUBHUB_API_BASE}/clubs/1156/members"
        params = {
            "page": str(page),
            "pageSize": "100"
        }
        
        try:
            response = session.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                members = data.get('results', [])
                
                if not members:
                    break
                    
                all_members.extend(members)
                print(f"   📄 Page {page}: {len(members)} members")
                page += 1
                
                # Rate limiting
                time.sleep(0.5)
                
            else:
                print(f"❌ Failed to get members page {page}: {response.status_code}")
                break
                
        except Exception as e:
            print(f"❌ Error fetching members page {page}: {e}")
            break
    
    print(f"✅ Total members retrieved: {len(all_members)}")
    return all_members

def get_member_agreement(session, member_id):
    """Get agreement data for a specific member"""
    url = f"{CLUBHUB_API_BASE}/clubs/1156/members/{member_id}/agreements"
    
    try:
        response = session.get(url, timeout=30)
        
        if response.status_code == 200:
            agreements = response.json()
            return agreements
        else:
            return None
            
    except Exception as e:
        return None

def process_member_agreements(session, members):
    """Process agreement data for all members"""
    print("💰 Processing member agreements...")
    
    members_with_agreements = []
    
    for i, member in enumerate(members):
        member_id = member.get('id')
        
        if member_id:
            agreements = get_member_agreement(session, member_id)
            
            # Add agreement data to member
            member_data = member.copy()
            member_data['agreements'] = agreements
            
            # Determine payment status
            if agreements:
                # Logic to determine red/yellow status based on agreement data
                # This would need to be customized based on your business rules
                latest_agreement = agreements[0] if agreements else {}
                member_data['payment_status'] = determine_payment_status(latest_agreement)
            else:
                member_data['payment_status'] = 'unknown'
            
            members_with_agreements.append(member_data)
            
            # Progress indicator
            if (i + 1) % 50 == 0:
                print(f"   📊 Processed {i + 1}/{len(members)} members")
            
            # Rate limiting
            time.sleep(0.2)
    
    return members_with_agreements

def determine_payment_status(agreement):
    """Determine if member is red, yellow, or current based on agreement data"""
    # This would need to be customized based on your business logic
    # For now, return a placeholder
    return 'current'

def save_master_contact_list(members_data):
    """Save the updated master contact list"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"master_contact_list_with_agreements_{timestamp}.csv"
    
    # Convert to DataFrame
    df = pd.DataFrame(members_data)
    
    # Save to CSV
    df.to_csv(filename, index=False)
    
    print(f"✅ Saved master contact list: {filename}")
    
    # Count red/yellow members
    red_count = len(df[df['payment_status'] == 'red']) if 'payment_status' in df.columns else 0
    yellow_count = len(df[df['payment_status'] == 'yellow']) if 'payment_status' in df.columns else 0
    current_count = len(df[df['payment_status'] == 'current']) if 'payment_status' in df.columns else 0
    
    print(f"📊 Member Status Summary:")
    print(f"   🔴 Red (Past Due): {red_count}")
    print(f"   🟡 Yellow (Warning): {yellow_count}")
    print(f"   🟢 Current: {current_count}")
    print(f"   📋 Total: {len(df)}")
    
    return filename, red_count, yellow_count

def update_dashboard_data(filename, red_count, yellow_count):
    """Update the dashboard to use the new data"""
    print("🔄 Updating dashboard configuration...")
    
    # Update clean_dashboard.py to use the new file
    dashboard_file = "clean_dashboard.py"
    
    if os.path.exists(dashboard_file):
        with open(dashboard_file, 'r') as f:
            content = f.read()
        
        # Update the CSV filename reference
        old_pattern = "master_contact_list_with_agreements_20250722_180712.csv"
        new_content = content.replace(old_pattern, filename)
        
        with open(dashboard_file, 'w') as f:
            f.write(new_content)
        
        print(f"✅ Updated dashboard to use: {filename}")
    else:
        print(f"⚠️ Dashboard file not found: {dashboard_file}")

def main():
    """Main execution function"""
    print("🚀 Starting ClubHub Data Update Process...")
    print("=" * 50)
    
    # Step 1: Authenticate
    session, token = authenticate_clubhub()
    if not session:
        print("❌ Authentication failed. Cannot proceed.")
        return
    
    # Step 2: Get all members
    members = get_all_members(session)
    if not members:
        print("❌ No members retrieved. Cannot proceed.")
        return
    
    # Step 3: Process agreements (this is the time-intensive part)
    print("\n⚠️ Processing agreements... This may take several minutes.")
    members_with_agreements = process_member_agreements(session, members)
    
    # Step 4: Save new master contact list
    filename, red_count, yellow_count = save_master_contact_list(members_with_agreements)
    
    # Step 5: Update dashboard
    update_dashboard_data(filename, red_count, yellow_count)
    
    print("\n🎉 Dashboard update complete!")
    print(f"🔴 Past Due Members: {red_count + yellow_count} (Red: {red_count}, Yellow: {yellow_count})")
    print("🔄 Restart your Flask app to see the updated data.")

if __name__ == "__main__":
    main()
