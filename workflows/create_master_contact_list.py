#!/usr/bin/env python3
"""
Create Master Contact List from ClubHub API
Pulls ALL members and prospects from ClubHub API and creates a comprehensive contact list.
Uses dynamic authentication similar to ClubOS approach.
"""

import pandas as pd
import json
import time
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from src.services.api.clubhub_api_client import ClubHubAPIClient
from config.constants import CLUBHUB_HEADERS
import os

# ClubHub Authentication Configuration  
CLUBHUB_LOGIN_URL = "https://clubhub.anytimefitness.com/login"
CLUBHUB_API_BASE = "https://clubhub-ios-api.anytimefitness.com/api/v1.0"

def get_secret(secret_name: str) -> str:
    """Get secret from environment variables"""
    secrets = {
        "clubhub-username": os.getenv("CLUBHUB_USERNAME", "mayo.jeremy2212@gmail.com"),
        "clubhub-password": os.getenv("CLUBHUB_PASSWORD", "L*KYqnec5z7nEL$")
    }
    return secrets.get(secret_name, "")

def login_to_clubhub():
    """
    Login to ClubHub and get fresh authentication headers
    Returns a session with valid authentication
    """
    print("🔐 Authenticating with ClubHub API...")
    
    try:
        # First try using the ClubHub token capture system for fresh tokens
        print("   🔄 Attempting to get fresh tokens from token capture system...")
        
        try:
            from src.services.authentication.clubhub_token_capture import ClubHubTokenCapture
            
            capture = ClubHubTokenCapture()
            latest_tokens = capture.get_latest_valid_tokens()
            
            if latest_tokens and latest_tokens.get('bearer_token'):
                print("   ✅ Found valid tokens from capture system!")
                
                session = requests.Session()
                session.headers.update({
                    "Authorization": f"Bearer {latest_tokens['bearer_token']}",
                    "API-version": "1",
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "User-Agent": "ClubHub Store/2.15.1 (com.anytimefitness.Club-Hub; build:1007; iOS 18.5.0) Alamofire/5.6.4",
                    "Accept-Language": "en-US",
                    "Accept-Encoding": "br;q=1.0, gzip;q=0.9, deflate;q=0.8"
                })
                
                # Add session cookie if available
                if latest_tokens.get('session_cookie'):
                    session.headers["Cookie"] = f"incap_ses_132_434694={latest_tokens['session_cookie']}"
                
                # Test the authentication
                test_url = f"{CLUBHUB_API_BASE}/clubs/1156/members"
                test_params = {"page": "1", "pageSize": "1"}
                test_response = session.get(test_url, params=test_params, verify=False, timeout=30)
                
                if test_response.status_code == 200:
                    print("   ✅ Token capture authentication validated!")
                    return session
                else:
                    print(f"   ⚠️ Token capture auth test failed ({test_response.status_code})")
                    
        except Exception as e:
            print(f"   ⚠️ Token capture system unavailable: {e}")
        
        # Try automated login system as backup
        print("   🔄 Trying automated login system...")
        
        try:
            from src.services.authentication.clubhub_automated_login import ClubHubAutomatedLogin
            
            auto_login = ClubHubAutomatedLogin()
            success, auth_data = auto_login.login()
            
            if success and auth_data.get("bearer_token"):
                print("   ✅ Automated login successful!")
                
                session = requests.Session()
                session.headers.update({
                    "Authorization": f"Bearer {auth_data['bearer_token']}",
                    "API-version": "1",
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "User-Agent": "ClubHub Store/2.15.1 (com.anytimefitness.Club-Hub; build:1007; iOS 18.5.0) Alamofire/5.6.4",
                    "Accept-Language": "en-US",
                    "Accept-Encoding": "br;q=1.0, gzip;q=0.9, deflate;q=0.8"
                })
                
                if auth_data.get("cookies"):
                    cookie_string = "; ".join([f"{k}={v}" for k, v in auth_data["cookies"].items()])
                    session.headers["Cookie"] = cookie_string
                
                return session
                
        except Exception as e:
            print(f"   ⚠️ Automated login failed: {e}")
        
        print("   📝 Using fallback headers from constants...")
        
    except Exception as e:
        print(f"   ❌ Authentication error: {e}")
        print("   📝 Using fallback headers")
    
    # Fallback to existing headers
    session = requests.Session()
    session.headers.update(CLUBHUB_HEADERS)
    return session

# Map of club_id to headers (for scalability)
# For now, use the same headers for all clubs, but you can add more entries as you scale
CLUB_HEADERS_MAP = {
    "1156": CLUBHUB_HEADERS,
    "291": CLUBHUB_HEADERS,
    "3586": CLUBHUB_HEADERS,
    # Add more club_id: headers pairs as you scale
}

def create_master_contact_list():
    print("🚀 CREATING COMPREHENSIVE MASTER CONTACT LIST FROM CLUBHUB API")
    print("=" * 70)
    print("⚠️ NO PAGINATION LIMITS - Will retrieve ALL 9000+ records!")
    print("📋 Enhanced with full agreement and billing information...")
    print("🔐 Using dynamic authentication for fresh API access...")
    print()
    
    # Get authenticated session
    session = login_to_clubhub()
    
    club_ids = [1156, 291, 3586]
    all_members = []
    all_prospects = []
    
    # Pull members from all clubs
    for club_id in club_ids:
        print(f"\n🏢 Pulling ALL members from Club {club_id}...")
        page = 1
        club_members = []
        while True:
            try:
                params = {
                    "page": str(page),
                    "pageSize": "100",
                    "includeInactive": "true",
                    "includeAll": "true",
                    "status": "all",
                    "days": "10000"
                }
                print(f"   📄 Requesting page {page}...")
                api_url = f"{CLUBHUB_API_BASE}/clubs/{club_id}/members"
                response = session.get(api_url, params=params, verify=False, timeout=30)
                if response.status_code == 200:
                    members_data = response.json()
                    if isinstance(members_data, list):
                        members = members_data
                    elif isinstance(members_data, dict):
                        members = members_data.get('members', members_data.get('data', []))
                    else:
                        members = []
                    if not members:
                        print(f"   ✅ No more members found on page {page}")
                        break
                    print(f"   ✅ Found {len(members)} members on page {page} (Running total: {len(club_members)})")
                    club_members.extend(members)
                    if len(members) < 100:
                        print(f"   🎯 Reached end of data - last page had {len(members)} members")
                        break
                    page += 1
                    # Continue until all data is retrieved - no artificial limits
                    time.sleep(0.5)  # Small delay to be respectful to API
                else:
                    print(f"   ❌ API request failed: {response.status_code}")
                    break
            except Exception as e:
                print(f"   ❌ Error on page {page}: {e}")
                break
        print(f"   📊 Total members from Club {club_id}: {len(club_members)}")
        all_members.extend(club_members)
    
    # Pull prospects from all clubs    
    for club_id in club_ids:
        print(f"\n🎯 Pulling ALL prospects from Club {club_id}...")
        page = 1
        club_prospects = []
        while True:
            try:
                params = {
                    "page": str(page),
                    "pageSize": "100",
                    "recent": "true"
                }
                print(f"   📄 Requesting page {page}...")
                api_url = f"{CLUBHUB_API_BASE}/clubs/{club_id}/prospects"
                response = session.get(api_url, params=params, verify=False, timeout=30)
                if response.status_code == 200:
                    prospects_data = response.json()
                    if isinstance(prospects_data, list):
                        prospects = prospects_data
                    elif isinstance(prospects_data, dict):
                        prospects = prospects_data.get('prospects', prospects_data.get('data', []))
                    else:
                        prospects = []
                    if not prospects:
                        print(f"   ✅ No more prospects found on page {page}")
                        break
                    print(f"   ✅ Found {len(prospects)} prospects on page {page} (Running total: {len(club_prospects)})")
                    club_prospects.extend(prospects)
                    if len(prospects) < 100:
                        print(f"   🎯 Reached end of data - last page had {len(prospects)} prospects")
                        break
                    page += 1
                    # Continue until all data is retrieved - no artificial limits
                    time.sleep(0.5)  # Small delay to be respectful to API
                else:
                    print(f"   ❌ API request failed: {response.status_code}")
                    break
            except Exception as e:
                print(f"   ❌ Error on page {page}: {e}")
                break
        print(f"   📊 Total prospects from Club {club_id}: {len(club_prospects)}")
        all_prospects.extend(club_prospects)
    print(f"\n📋 Processing contact data...")
    print(f"   Members: {len(all_members)}")
    print(f"   Prospects: {len(all_prospects)}")
    contacts = []
    for member in all_members:
        first_name = member.get('firstName', '')
        last_name = member.get('lastName', '')
        full_name = f"{first_name} {last_name}".strip()
        if not full_name:
            continue
        contacts.append({
            'Name': full_name,
            'FirstName': first_name,
            'LastName': last_name,
            'Email': member.get('email', member.get('emailAddress', '')),
            'Phone': member.get('phone', member.get('phoneNumber', member.get('mobilePhone', ''))),
            'Address': member.get('address1', member.get('address', '')),
            'Address2': member.get('address2', ''),
            'City': member.get('city', ''),
            'State': member.get('state', ''),
            'ZipCode': member.get('zip', member.get('zipCode', '')),
            'Country': member.get('country', ''),
            'MemberSince': member.get('membershipStart', member.get('memberSince', member.get('joinDate', member.get('startDate', '')))),
            'MembershipEnd': member.get('membershipEnd', ''),
            'LastVisit': member.get('lastVisit', member.get('lastCheckIn', '')),
            'Status': member.get('status', member.get('memberStatus', '')),
            'StatusMessage': member.get('statusMessage', ''),
            'Type': member.get('type', ''),
            'UserType': member.get('userType', ''),
            'UserStatus': member.get('userStatus', ''),
            'Category': 'Member',
            'ProspectID': member.get('id', ''),
            'GUID': member.get('guid', ''),
            'MemberID': member.get('memberId', member.get('memberNumber', '')),
            'AgreementID': member.get('agreementId', member.get('agreement', {}).get('id', '')),
            'AgreementType': member.get('agreementType', member.get('agreement', {}).get('type', '')),
            'BillingFrequency': member.get('billingFrequency', member.get('agreement', {}).get('billingFrequency', '')),
            'MonthlyRate': member.get('monthlyRate', member.get('agreement', {}).get('recurringCost', {}).get('total', '')),
            'AmountPastDue': member.get('amountPastDue', member.get('agreement', {}).get('amountPastDue', '')),
            'NextPaymentDate': member.get('nextPaymentDate', member.get('agreement', {}).get('dateOfNextPayment', '')),
            'ContractValue': member.get('contractValue', member.get('agreement', {}).get('valueRemaining', '')),
            'PaymentMethod': member.get('paymentMethod', member.get('agreement', {}).get('paymentMethod', '')),
            'AutoPay': member.get('autoPay', member.get('agreement', {}).get('autoPay', '')),
            'Gender': member.get('gender', ''),
            'DateOfBirth': member.get('dateOfBirth', ''),
            'Source': member.get('source', ''),
            'Rating': member.get('rating', ''),
            'LastActivity': member.get('lastActivity', ''),
            'HasApp': member.get('hasApp', ''),
            'HomeClub': member.get('homeClub', ''),
            'ClubID': member.get('clubId', ''),
            'RawData': json.dumps(member)
        })
    for prospect in all_prospects:
        first_name = prospect.get('firstName', '')
        last_name = prospect.get('lastName', '')
        full_name = f"{first_name} {last_name}".strip()
        if not full_name:
            continue
        contacts.append({
            'Name': full_name,
            'FirstName': first_name,
            'LastName': last_name,
            'Email': prospect.get('email', prospect.get('emailAddress', '')),
            'Phone': prospect.get('phone', prospect.get('phoneNumber', prospect.get('mobilePhone', ''))),
            'Address': prospect.get('address1', prospect.get('address', '')),
            'Address2': prospect.get('address2', ''),
            'City': prospect.get('city', ''),
            'State': prospect.get('state', ''),
            'ZipCode': prospect.get('zip', prospect.get('zipCode', '')),
            'Country': prospect.get('country', ''),
            'MemberSince': prospect.get('membershipStart', prospect.get('memberSince', prospect.get('joinDate', prospect.get('startDate', '')))),
            'MembershipEnd': prospect.get('membershipEnd', ''),
            'LastVisit': prospect.get('lastVisit', prospect.get('lastCheckIn', '')),
            'Status': prospect.get('status', prospect.get('memberStatus', '')),
            'StatusMessage': prospect.get('statusMessage', ''),
            'Type': prospect.get('type', ''),
            'UserType': prospect.get('userType', ''),
            'UserStatus': prospect.get('userStatus', ''),
            'Category': 'Prospect',
            'ProspectID': prospect.get('id', ''),
            'GUID': prospect.get('guid', ''),
            'MemberID': prospect.get('memberId', prospect.get('memberNumber', '')),
            'AgreementID': prospect.get('agreementId', prospect.get('agreement', {}).get('id', '')),
            'AgreementType': prospect.get('agreementType', prospect.get('agreement', {}).get('type', '')),
            'BillingFrequency': prospect.get('billingFrequency', prospect.get('agreement', {}).get('billingFrequency', '')),
            'MonthlyRate': prospect.get('monthlyRate', prospect.get('agreement', {}).get('recurringCost', {}).get('total', '')),
            'AmountPastDue': prospect.get('amountPastDue', prospect.get('agreement', {}).get('amountPastDue', '')),
            'NextPaymentDate': prospect.get('nextPaymentDate', prospect.get('agreement', {}).get('dateOfNextPayment', '')),
            'ContractValue': prospect.get('contractValue', prospect.get('agreement', {}).get('valueRemaining', '')),
            'PaymentMethod': prospect.get('paymentMethod', prospect.get('agreement', {}).get('paymentMethod', '')),
            'AutoPay': prospect.get('autoPay', prospect.get('agreement', {}).get('autoPay', '')),
            'Gender': prospect.get('gender', ''),
            'DateOfBirth': prospect.get('dateOfBirth', ''),
            'Source': prospect.get('source', ''),
            'Rating': prospect.get('rating', ''),
            'LastActivity': prospect.get('lastActivity', ''),
            'HasApp': prospect.get('hasApp', ''),
            'HomeClub': prospect.get('homeClub', ''),
            'ClubID': prospect.get('clubId', ''),
            'RawData': json.dumps(prospect)
        })
    df = pd.DataFrame(contacts)
    
    if len(df) == 0:
        print("\n⚠️ No contacts retrieved - creating empty CSV with headers only")
        # Create empty DataFrame with expected columns
        columns = ['Name', 'FirstName', 'LastName', 'Email', 'Phone', 'Address', 'Address2', 
                  'City', 'State', 'ZipCode', 'Country', 'MemberSince', 'MembershipEnd', 
                  'LastVisit', 'Status', 'StatusMessage', 'Type', 'UserType', 'UserStatus', 
                  'Category', 'ProspectID', 'GUID', 'MemberID', 'AgreementID', 'AgreementType', 
                  'BillingFrequency', 'MonthlyRate', 'AmountPastDue', 'NextPaymentDate', 
                  'ContractValue', 'PaymentMethod', 'AutoPay', 'Gender', 'DateOfBirth', 
                  'Source', 'Rating', 'LastActivity', 'HasApp', 'HomeClub', 'ClubID', 'RawData']
        df = pd.DataFrame(columns=columns)
    else:
        df = df.drop_duplicates(subset=['Name', 'Email'], keep='first')
        df = df.sort_values(['Category', 'Name'])
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"master_contact_list_{timestamp}.csv"
    df.to_csv(filename, index=False)
    print(f"\n🎉 MASTER CONTACT LIST CREATED!")
    print(f"   📄 File: {filename}")
    print(f"   📊 Total contacts: {len(df)}")
    
    if len(df) > 0:
        print(f"   👥 Members: {len(df[df['Category'] == 'Member'])}")
        print(f"   🎯 Prospects: {len(df[df['Category'] == 'Prospect'])}")
        print(f"\n📋 Sample contacts:")
        print(df.head(10)[['Name', 'Email', 'Phone', 'Category', 'Status']].to_string(index=False))
    else:
        print("   ⚠️ No data retrieved - check authentication or API status")
    
    return df

if __name__ == "__main__":
    create_master_contact_list() 