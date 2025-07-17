#!/usr/bin/env python3
"""
Create Master Contact List from ClubHub API
Pulls ALL members and prospects from ClubHub API and creates a comprehensive contact list.
"""

import pandas as pd
import json
from datetime import datetime
from services.api.clubhub_api_client import ClubHubAPIClient
from config.constants import CLUBHUB_HEADERS
import requests

# Map of club_id to headers (for scalability)
# For now, use the same headers for all clubs, but you can add more entries as you scale
CLUB_HEADERS_MAP = {
    "1156": CLUBHUB_HEADERS,
    "291": CLUBHUB_HEADERS,
    "3586": CLUBHUB_HEADERS,
    # Add more club_id: headers pairs as you scale
}

def create_master_contact_list():
    print("🚀 CREATING MASTER CONTACT LIST FROM CLUBHUB API")
    print("=" * 60)
    club_ids = list(CLUB_HEADERS_MAP.keys())
    all_members = []
    all_prospects = []
    for club_id in club_ids:
        headers = CLUB_HEADERS_MAP[club_id]
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
                api_url = f"https://clubhub-ios-api.anytimefitness.com/api/v1.0/clubs/{club_id}/members"
                response = requests.get(api_url, headers=headers, params=params, verify=False, timeout=30)
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
                    print(f"   ✅ Found {len(members)} members on page {page}")
                    club_members.extend(members)
                    if len(members) < 100:
                        break
                    page += 1
                    if page > 50:
                        print(f"   ⚠️ Reached page limit (50) for Club {club_id}")
                        break
                else:
                    print(f"   ❌ API request failed: {response.status_code}")
                    break
            except Exception as e:
                print(f"   ❌ Error on page {page}: {e}")
                break
        print(f"   📊 Total members from Club {club_id}: {len(club_members)}")
        all_members.extend(club_members)
    for club_id in club_ids:
        headers = CLUB_HEADERS_MAP[club_id]
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
                api_url = f"https://clubhub-ios-api.anytimefitness.com/api/v1.0/clubs/{club_id}/prospects"
                response = requests.get(api_url, headers=headers, params=params, verify=False, timeout=30)
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
                    print(f"   ✅ Found {len(prospects)} prospects on page {page}")
                    club_prospects.extend(prospects)
                    if len(prospects) < 100:
                        break
                    page += 1
                    if page > 50:
                        print(f"   ⚠️ Reached page limit (50) for Club {club_id}")
                        break
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
            'AgreementID': member.get('agreementId', ''),
            'AgreementType': member.get('agreementType', ''),
            'BillingFrequency': member.get('billingFrequency', ''),
            'MonthlyRate': member.get('monthlyRate', ''),
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
            'AgreementID': prospect.get('agreementId', ''),
            'AgreementType': prospect.get('agreementType', ''),
            'BillingFrequency': prospect.get('billingFrequency', ''),
            'MonthlyRate': prospect.get('monthlyRate', ''),
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
    df = df.drop_duplicates(subset=['Name', 'Email'], keep='first')
    df = df.sort_values(['Category', 'Name'])
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"master_contact_list_{timestamp}.csv"
    df.to_csv(filename, index=False)
    print(f"\n🎉 MASTER CONTACT LIST CREATED!")
    print(f"   📄 File: {filename}")
    print(f"   📊 Total contacts: {len(df)}")
    print(f"   👥 Members: {len(df[df['Category'] == 'Member'])}")
    print(f"   🎯 Prospects: {len(df[df['Category'] == 'Prospect'])}")
    print(f"\n📋 Sample contacts:")
    print(df.head(10)[['Name', 'Email', 'Phone', 'Category', 'Status']].to_string(index=False))
    return df

if __name__ == "__main__":
    create_master_contact_list() 