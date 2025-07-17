#!/usr/bin/env python3
"""
Fetch ALL members and prospects from ClubHub API
"""

import json
import pandas as pd
from services.api.clubhub_api_client import ClubHubAPIClient
from config.constants import CLUBHUB_HEADERS

def extract_auth_token():
    """Extract auth token from constants"""
    auth_header = CLUBHUB_HEADERS.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        return auth_header.replace('Bearer ', '')
    return None

def fetch_all_clubhub_data():
    """Fetch all members and prospects from ClubHub"""
    
    print("🚀 Starting comprehensive ClubHub data fetch...")
    
    # Initialize ClubHub API client
    client = ClubHubAPIClient()
    
    # Set auth token from constants
    token = extract_auth_token()
    if not token:
        print("❌ No auth token found in constants")
        return False
    
    client.set_auth_token(token)
    
    # Fetch ALL members with pagination
    print("\n📊 Fetching ALL members...")
    all_members = []
    page = 1
    while True:
        response = client.get_all_members(page=page, page_size=100)
        if not response:
            print(f"❌ Failed to fetch page {page}")
            break
        members = response.get('members', [])
        if not members:
            print(f"✅ No more members found on page {page}")
            break
        all_members.extend(members)
        print(f"✅ Page {page}: {len(members)} members (Total: {len(all_members)})")
        if len(members) < 100:
            print("✅ Reached end of members list")
            break
        page += 1
    print(f"✅ Fetched {len(all_members)} total members")
    
    # Fetch ALL prospects with pagination
    print("\n📊 Fetching ALL prospects...")
    all_prospects = []
    page = 1
    while True:
        response = client.get_all_prospects(page=page, page_size=100)
        if not response:
            print(f"❌ Failed to fetch page {page}")
            break
        prospects = response.get('prospects', [])
        if not prospects:
            print(f"✅ No more prospects found on page {page}")
            break
        all_prospects.extend(prospects)
        print(f"✅ Page {page}: {len(prospects)} prospects (Total: {len(all_prospects)})")
        if len(prospects) < 100:
            print("✅ Reached end of prospects list")
            break
        page += 1
    print(f"✅ Fetched {len(all_prospects)} total prospects")
    
    # Create comprehensive DataFrames
    print("\n📋 Processing member data...")
    members_data = []
    for member in all_members:
        members_data.append({
            'Name': f"{member.get('firstName', '')} {member.get('lastName', '')}".strip(),
            'FirstName': member.get('firstName', ''),
            'LastName': member.get('lastName', ''),
            'Email': member.get('email', ''),
            'Phone': member.get('phone', ''),
            'Address': member.get('address1', ''),
            'Address2': member.get('address2', ''),
            'City': member.get('city', ''),
            'State': member.get('state', ''),
            'ZipCode': member.get('zip', ''),
            'Country': member.get('country', ''),
            'MemberSince': member.get('membershipStart', ''),
            'MembershipEnd': member.get('membershipEnd', ''),
            'LastVisit': member.get('lastVisit', ''),
            'Status': member.get('status', ''),
            'StatusMessage': member.get('statusMessage', ''),
            'Type': member.get('type', ''),
            'UserType': member.get('userType', ''),
            'UserStatus': member.get('userStatus', ''),
            'Category': 'Member',
            'ProspectID': member.get('id', ''),
            'GUID': member.get('guid', ''),
            'MemberID': member.get('memberId', ''),
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
            'PreferredAccessType': member.get('preferredAccessType', ''),
            'MessagingStatus': '',
            'LastMessageDate': '',
            'OptedOut': member.get('optedOut', False),
            'Source': 'ClubHub-Members'
        })
    
    print("📋 Processing prospect data...")
    prospects_data = []
    for prospect in all_prospects:
        prospects_data.append({
            'Name': f"{prospect.get('firstName', '')} {prospect.get('lastName', '')}".strip(),
            'FirstName': prospect.get('firstName', ''),
            'LastName': prospect.get('lastName', ''),
            'Email': prospect.get('email', ''),
            'Phone': prospect.get('phone', ''),
            'Address': prospect.get('address', ''),
            'City': prospect.get('city', ''),
            'State': prospect.get('state', ''),
            'ZipCode': prospect.get('zipCode', ''),
            'MemberSince': '',  # Prospects don't have member since date
            'LastVisit': prospect.get('lastVisit', ''),
            'Status': prospect.get('status', ''),
            'StatusMessage': prospect.get('statusMessage', ''),
            'Category': 'Prospect',
            'ProspectID': prospect.get('id', ''),
            'MemberID': '',  # Prospects don't have member ID yet
            'AgreementType': '',
            'BillingFrequency': '',
            'MonthlyRate': '',
            'MessagingStatus': '',
            'LastMessageDate': '',
            'OptedOut': prospect.get('optedOut', False),
            'Source': 'ClubHub-Prospects'
        })
    
    # Create DataFrames
    df_members = pd.DataFrame(members_data)
    df_prospects = pd.DataFrame(prospects_data)
    
    # Combine all data
    df_combined = pd.concat([df_members, df_prospects], ignore_index=True)
    
    print(f"\n📊 Data Summary:")
    print(f"   Members: {len(df_members)}")
    print(f"   Prospects: {len(df_prospects)}")
    print(f"   Total: {len(df_combined)}")
    
    # Save to Excel
    output_file = "data/master_contact_list_complete.xlsx"
    df_combined.to_excel(output_file, index=False)
    print(f"\n💾 Saved complete contact list to: {output_file}")
    
    # Search for Jeremy Mayo
    print("\n🔍 Searching for Jeremy Mayo...")
    jeremy_matches = []
    
    for index, row in df_combined.iterrows():
        first_name = str(row.get('FirstName', '')).lower()
        last_name = str(row.get('LastName', '')).lower()
        
        if 'jeremy' in first_name and 'mayo' in last_name:
            jeremy_matches.append({
                'index': index,
                'row': row
            })
            print(f"✅ Found Jeremy Mayo at row {index + 1}:")
            print(f"   Name: {row.get('Name', 'N/A')}")
            print(f"   First Name: {row.get('FirstName', 'N/A')}")
            print(f"   Last Name: {row.get('LastName', 'N/A')}")
            print(f"   Prospect ID: {row.get('ProspectID', 'N/A')}")
            print(f"   Member ID: {row.get('MemberID', 'N/A')}")
            print(f"   Email: {row.get('Email', 'N/A')}")
            print(f"   Category: {row.get('Category', 'N/A')}")
            print()
    
    if not jeremy_matches:
        print("❌ Jeremy Mayo not found in the data")
        print("🔍 Checking first 10 contacts for reference:")
        for i, (index, row) in enumerate(df_combined.head(10).iterrows()):
            print(f"   {i+1}. {row.get('Name', 'N/A')} - ProspectID: {row.get('ProspectID', 'N/A')}")
        return False
    
    # Check prospectID format
    for match in jeremy_matches:
        prospect_id = str(match['row'].get('ProspectID', ''))
        if prospect_id and prospect_id != 'nan':
            print(f"🎯 Jeremy Mayo's Prospect ID: {prospect_id}")
            
            # Check if it's 8 digits
            if len(prospect_id) == 8 and prospect_id.isdigit():
                print("✅ Prospect ID is 8 digits as expected!")
            else:
                print(f"⚠️  Prospect ID is {len(prospect_id)} digits, not 8")
        else:
            print("❌ No prospectID found for Jeremy Mayo")
    
    return True

if __name__ == "__main__":
    success = fetch_all_clubhub_data()
    if success:
        print("\n✅ Complete ClubHub data fetch successful!")
    else:
        print("\n❌ ClubHub data fetch failed!") 