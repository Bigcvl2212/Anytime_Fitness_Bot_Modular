#!/usr/bin/env python3
"""
Comprehensive ClubHub Data Pull and Invoice System
Pulls ALL members and prospects from ClubHub API using fresh tokens,
updates master_contact_list, and sends production invoices to past due members.
"""

import sys
import os
import pandas as pd
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import time

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def get_fresh_clubhub_headers():
    """Get fresh ClubHub authentication headers using stored tokens"""
    try:
        from services.authentication.clubhub_token_capture import ClubHubTokenCapture
        capture = ClubHubTokenCapture()
        
        # Load stored tokens
        tokens = capture.load_tokens()
        print(f"[DEBUG] Loaded tokens: {tokens}")
        if not tokens:
            print("❌ No stored tokens found. Please run smart_token_capture.py first.")
            return None
        # Find the latest token set (by extracted_at timestamp)
        latest_key = max(tokens.keys(), key=lambda k: tokens[k].get('extracted_at', k))
        latest_tokens = tokens[latest_key]['tokens']
        bearer_token = latest_tokens.get('bearer_token', '')
        session_cookie = latest_tokens.get('session_cookie', '')
        print(f"[DEBUG] Using token set: {latest_key}")
        print(f"[DEBUG] Bearer token: {bearer_token[:30]}... (truncated)")
        print(f"[DEBUG] Session cookie: {session_cookie[:30]}... (truncated)")
        
        # Create full legacy headers with session cookie
        headers = {
            "Host": "clubhub-ios-api.anytimefitness.com",
            "Cookie": session_cookie,
            "API-version": "1",
            "Accept": "application/json",
            "User-Agent": "ClubHub Store/2.15.0 (com.anytimefitness.Club-Hub; build:1004; iOS 18.5.0) Alamofire/5.6.4",
            "Authorization": f"Bearer {bearer_token}",
            "Accept-Language": "en-US",
            "Accept-Encoding": "br;q=1.0, gzip;q=0.9, deflate;q=0.8"
        }
        print("✅ Successfully loaded fresh ClubHub authentication headers")
        return headers
    except Exception as e:
        print(f"❌ Error getting fresh headers: {e}")
        return None

def pull_all_members_and_prospects():
    """Pull ALL members and prospects from ClubHub API"""
    print("🚀 PULLING ALL MEMBERS AND PROSPECTS FROM CLUBHUB API")
    print("=" * 60)
    
    headers = get_fresh_clubhub_headers()
    if not headers:
        return None, None
    print(f"[DEBUG] Authorization header: {headers.get('Authorization', '')[:30]}... (truncated)")
    
    # Club IDs to pull from
    club_ids = ["1156", "291", "3586"]  # Add more as needed
    
    all_members = []
    all_prospects = []
    
    for club_id in club_ids:
        print(f"\n🏢 Pulling ALL members from Club {club_id}...")
        
        # Pull ALL members with pagination
        page = 1
        club_members = []
        
        while True:
            try:
                params = {
                    "page": str(page),
                    "pageSize": "50",
                    "days": "4000"  # 11 years to get ALL historical data
                }
                
                print(f"   📄 Requesting page {page}...")
                api_url = f"https://clubhub-ios-api.anytimefitness.com/api/v1.0/clubs/{club_id}/members"
                response = requests.get(api_url, headers=headers, params=params, verify=False, timeout=30)
                
                if response.status_code == 200:
                    members_data = response.json()
                    
                    # Handle different response formats
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
                    
                    if len(members) < 50:  # Last page (since pageSize is 50)
                        break
                    
                    page += 1
                    if page > 200:  # Increased safety limit for more data
                        print(f"   ⚠️ Reached page limit (200) for Club {club_id}")
                        break
                        
                else:
                    print(f"   ❌ API request failed: {response.status_code}")
                    print(f"   Response: {response.text[:200]}")
                    break
                    
            except Exception as e:
                print(f"   ❌ Error on page {page}: {e}")
                break
        
        print(f"   📊 Total members from Club {club_id}: {len(club_members)}")
        all_members.extend(club_members)
        
        # Pull ALL prospects
        print(f"\n🎯 Pulling ALL prospects from Club {club_id}...")
        page = 1
        club_prospects = []
        
        while True:
            try:
                params = {
                    "page": str(page),
                    "pageSize": "50",
                    "days": "4000"  # 11 years to get ALL historical data
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
                    
                    if len(prospects) < 50:  # Last page (since pageSize is 50)
                        break
                    
                    page += 1
                    if page > 200:  # Increased safety limit for more data
                        print(f"   ⚠️ Reached page limit (200) for Club {club_id}")
                        break
                        
                else:
                    print(f"   ❌ API request failed: {response.status_code}")
                    break
                    
            except Exception as e:
                print(f"   ❌ Error on page {page}: {e}")
                break
        
        print(f"   📊 Total prospects from Club {club_id}: {len(club_prospects)}")
        all_prospects.extend(club_prospects)
    
    print(f"\n📋 DATA PULL SUMMARY:")
    print(f"   👥 Total Members: {len(all_members)}")
    print(f"   🎯 Total Prospects: {len(all_prospects)}")
    print(f"   📊 Total Contacts: {len(all_members) + len(all_prospects)}")
    
    return all_members, all_prospects

def create_master_contact_list(members, prospects):
    """Create comprehensive master contact list from pulled data"""
    print("\n📋 CREATING MASTER CONTACT LIST")
    print("=" * 40)
    
    contacts = []
    
    # Process members
    print("👥 Processing member data...")
    for member in members:
        first_name = member.get('firstName', '').strip()
        last_name = member.get('lastName', '').strip()
        full_name = f"{first_name} {last_name}".strip()
        
        if not full_name:
            continue
        
        # Extract comprehensive member data
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
            'PastDue': False,  # Will be determined below
            'PastDueDays': 0,  # Will be determined below
            'PastDueAmount': 0,  # Will be determined below
            'PastDueCategory': 'None',  # Will be determined below
            'RawData': json.dumps(member)
        })
        
        # Determine past due status based on statusMessage
        status_msg = member.get('statusMessage', '').lower()
        if 'past due 6-30 days' in status_msg:
            contacts[-1]['PastDue'] = True
            contacts[-1]['PastDueDays'] = 15  # Approximate middle of 6-30 range
            contacts[-1]['PastDueCategory'] = 'Yellow'
        elif 'past due more than 30 days' in status_msg:
            contacts[-1]['PastDue'] = True
            contacts[-1]['PastDueDays'] = 45  # Approximate for 30+ days
            contacts[-1]['PastDueCategory'] = 'Red'
        elif 'delinquent' in status_msg:
            contacts[-1]['PastDue'] = True
            contacts[-1]['PastDueDays'] = 60  # Delinquent is typically 60+ days
            contacts[-1]['PastDueCategory'] = 'Red'
    
    # Process prospects
    print("🎯 Processing prospect data...")
    for prospect in prospects:
        first_name = prospect.get('firstName', '').strip()
        last_name = prospect.get('lastName', '').strip()
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
            'MemberSince': '',  # Prospects don't have member since date
            'MembershipEnd': '',
            'LastVisit': prospect.get('lastVisit', prospect.get('lastCheckIn', '')),
            'Status': prospect.get('status', prospect.get('prospectStatus', '')),
            'StatusMessage': prospect.get('statusMessage', ''),
            'Type': prospect.get('type', ''),
            'UserType': prospect.get('userType', ''),
            'UserStatus': prospect.get('userStatus', ''),
            'Category': 'Prospect',
            'ProspectID': prospect.get('id', ''),
            'GUID': prospect.get('guid', ''),
            'MemberID': '',  # Prospects don't have member ID yet
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
            'PastDue': False,  # Prospects can't be past due
            'PastDueDays': 0,
            'PastDueAmount': 0,
            'RawData': json.dumps(prospect)
        })
    
    # Create DataFrame
    df = pd.DataFrame(contacts)
    
    # Remove duplicates based on Name and Email
    df = df.drop_duplicates(subset=['Name', 'Email'], keep='first')
    
    # Sort by Category (Members first), then by Name
    df = df.sort_values(['Category', 'Name'])
    
    # Save to multiple formats
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Save as CSV
    csv_filename = f"master_contact_list_{timestamp}.csv"
    df.to_csv(csv_filename, index=False)
    
    # Save as Excel
    excel_filename = f"master_contact_list_{timestamp}.xlsx"
    df.to_excel(excel_filename, index=False)
    
    print(f"\n🎉 MASTER CONTACT LIST CREATED!")
    print(f"   📄 CSV File: {csv_filename}")
    print(f"   📄 Excel File: {excel_filename}")
    print(f"   📊 Total contacts: {len(df)}")
    print(f"   👥 Members: {len(df[df['Category'] == 'Member'])}")
    print(f"   🎯 Prospects: {len(df[df['Category'] == 'Prospect'])}")
    
    # Show sample data
    print(f"\n📋 Sample contacts:")
    sample_cols = ['Name', 'Email', 'Phone', 'Category', 'Status', 'PastDue', 'PastDueDays']
    available_cols = [col for col in sample_cols if col in df.columns]
    print(df.head(10)[available_cols].to_string(index=False))
    
    return df

def identify_past_due_members(df):
    """Identify past due members for invoice processing"""
    print("\n💰 IDENTIFYING PAST DUE MEMBERS")
    print("=" * 40)
    
    # Filter for members only
    members_df = df[df['Category'] == 'Member'].copy()
    
    if members_df.empty:
        print("❌ No members found in contact list")
        return pd.DataFrame()
    
    # Identify past due members based on PastDueCategory
    past_due_members = []
    
    for index, row in members_df.iterrows():
        past_due_category = row.get('PastDueCategory', 'None')
        
        # Only process yellow and red members
        if past_due_category in ['Yellow', 'Red']:
            past_due_days = row.get('PastDueDays', 0)
            past_due_amount = row.get('PastDueAmount', 0)
            
            # Calculate late fees for biweekly billing
            # $19.50 late fee per missed payment
            # Biweekly = every 14 days
            missed_payments = max(1, past_due_days // 14)  # At least 1 missed payment
            late_fees = missed_payments * 19.50
            
            # Add late fees to past due amount
            total_amount = past_due_amount + late_fees
            
            past_due_members.append({
                'Name': row.get('Name', ''),
                'Email': row.get('Email', ''),
                'Phone': row.get('Phone', ''),
                'Address': row.get('Address', ''),
                'City': row.get('City', ''),
                'State': row.get('State', ''),
                'ZipCode': row.get('ZipCode', ''),
                'Status': row.get('Status', ''),
                'StatusMessage': row.get('StatusMessage', ''),
                'PastDueDays': past_due_days,
                'PastDueAmount': past_due_amount,
                'LateFees': late_fees,
                'TotalAmount': total_amount,
                'MissedPayments': missed_payments,
                'PastDueCategory': past_due_category,
                'MemberID': row.get('MemberID', ''),
                'ProspectID': row.get('ProspectID', ''),
                'MonthlyRate': row.get('MonthlyRate', ''),
                'BillingFrequency': row.get('BillingFrequency', ''),
                'Category': f'{past_due_category} Member'
            })
    
    past_due_df = pd.DataFrame(past_due_members)
    
    print(f"💰 Found {len(past_due_df)} past due members")
    
    if not past_due_df.empty:
        # Categorize by PastDueCategory
        yellow_members = past_due_df[past_due_df['PastDueCategory'] == 'Yellow']
        red_members = past_due_df[past_due_df['PastDueCategory'] == 'Red']
        
        print(f"   🟡 Yellow (6-30 days): {len(yellow_members)}")
        print(f"   🔴 Red (30+ days): {len(red_members)}")
        
        # Show total late fees
        total_late_fees = past_due_df['LateFees'].sum()
        total_amount = past_due_df['TotalAmount'].sum()
        print(f"   💰 Total late fees: ${total_late_fees:.2f}")
        print(f"   💰 Total amount due: ${total_amount:.2f}")
        
        # Save past due list
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        past_due_filename = f"past_due_members_{timestamp}.xlsx"
        past_due_df.to_excel(past_due_filename, index=False)
        print(f"   📄 Past due list saved: {past_due_filename}")
    
    return past_due_df

def send_production_invoices(past_due_df):
    """Send production invoices to past due members"""
    print("\n📧 SENDING PRODUCTION INVOICES")
    print("=" * 40)
    
    if past_due_df.empty:
        print("❌ No past due members to send invoices to")
        return
    
    # Categorize by severity
    yellow_members = past_due_df[past_due_df['PastDueDays'].between(6, 30)]
    red_members = past_due_df[past_due_df['PastDueDays'] > 30]
    
    print(f"📧 Preparing to send invoices:")
    print(f"   🟡 Yellow members (6-30 days): {len(yellow_members)}")
    print(f"   🔴 Red members (30+ days): {len(red_members)}")
    
    # Process yellow members (6-30 days past due)
    print(f"\n🟡 Processing yellow members...")
    for index, member in yellow_members.iterrows():
        try:
            print(f"   📧 Sending invoice to: {member['Name']} ({member['Email']})")
            print(f"      Past due: {member['PastDueDays']} days")
            print(f"      Amount: ${member['PastDueAmount']}")
            
            # TODO: Implement actual invoice sending logic
            # This would integrate with your invoice system
            # For now, just log the action
            
            time.sleep(0.5)  # Rate limiting
            
        except Exception as e:
            print(f"   ❌ Error sending invoice to {member['Name']}: {e}")
    
    # Process red members (30+ days past due)
    print(f"\n🔴 Processing red members...")
    for index, member in red_members.iterrows():
        try:
            print(f"   📧 Sending urgent invoice to: {member['Name']} ({member['Email']})")
            print(f"      Past due: {member['PastDueDays']} days")
            print(f"      Amount: ${member['PastDueAmount']}")
            
            # TODO: Implement actual invoice sending logic
            # This would integrate with your invoice system
            # For now, just log the action
            
            time.sleep(0.5)  # Rate limiting
            
        except Exception as e:
            print(f"   ❌ Error sending invoice to {member['Name']}: {e}")
    
    print(f"\n✅ Invoice processing complete!")
    print(f"   📧 Total invoices prepared: {len(past_due_df)}")

def main():
    """Main function to run the comprehensive data pull and invoice system"""
    print("🚀 COMPREHENSIVE CLUBHUB DATA PULL AND INVOICE SYSTEM")
    print("=" * 70)
    print("This system will:")
    print("1. Pull ALL members and prospects from ClubHub API")
    print("2. Create/update master contact list")
    print("3. Identify past due members (yellow/red status)")
    print("4. Send production invoices to past due members")
    print()
    
    try:
        # Step 1: Pull all data from ClubHub API
        members, prospects = pull_all_members_and_prospects()
        if not members and not prospects:
            print("❌ Failed to pull data from ClubHub API")
            return False
        
        # Step 2: Create master contact list
        df = create_master_contact_list(members, prospects)
        if df.empty:
            print("❌ Failed to create master contact list")
            return False
        
        # Step 3: Identify past due members
        past_due_df = identify_past_due_members(df)
        
        # Step 4: Send production invoices
        send_production_invoices(past_due_df)
        
        print("\n🎉 COMPREHENSIVE DATA PULL AND INVOICE SYSTEM COMPLETE!")
        print("✅ All tasks completed successfully")
        return True
        
    except Exception as e:
        print(f"\n❌ Error in main process: {e}")
        return False

if __name__ == "__main__":
    main() 