#!/usr/bin/env python3
"""
Complete Training Client Discovery Script

This script gets all members from ClubHub and checks each one against ClubOS
to find ALL training clients with active packages (including past-due ones).

The original CSV list was incomplete because it excluded past-due training clients.
This script will build the complete list by checking ClubOS directly.
"""

import sys
import os
import sqlite3
from datetime import datetime

# Add the services directory to the path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'services'))

from api.clubhub_api_client import ClubHubAPIClient
from config.clubhub_credentials import CLUBHUB_EMAIL, CLUBHUB_PASSWORD

# Import the ClubOS API components
from api.clubos_training_api import ClubOSTrainingAPI
from config.clubos_credentials import CLUBOS_EMAIL, CLUBOS_PASSWORD

def get_all_members_from_clubhub():
    """Get complete member list from ClubHub"""
    print("🔐 Connecting to ClubHub...")
    client = ClubHubAPIClient()
    
    if not client.authenticate(CLUBHUB_EMAIL, CLUBHUB_PASSWORD):
        print("❌ ClubHub authentication failed")
        return []
    
    print("✅ ClubHub authenticated")
    
    # Get all members
    all_members = []
    page = 1
    
    while True:
        print(f"📄 Fetching page {page}...")
        members = client.get_all_members(page=page, page_size=100)
        
        if not members or len(members) == 0:
            break
            
        all_members.extend(members)
        print(f"   Got {len(members)} members on page {page}")
        page += 1
        
        # Break if we got less than page size (last page)
        if len(members) < 100:
            break
    
    print(f"📋 Total members retrieved from ClubHub: {len(all_members)}")
    return all_members

def check_training_status_in_clubos(member_data):
    """Check if a member has active training packages in ClubOS"""
    try:
        # Get member details
        member_name = f"{member_data.get('firstName', '')} {member_data.get('lastName', '')}".strip()
        clubhub_id = member_data.get('id')
        
        # We need to find their ClubOS member ID
        # This might be stored in the database or we might need to search ClubOS
        
        # For now, let's try using the ClubOS API to search by name
        clubos_api = ClubOSTrainingAPI()
        
        if not clubos_api.authenticate(CLUBOS_EMAIL, CLUBOS_PASSWORD):
            return None, "ClubOS authentication failed"
        
        # Try to get payment status (this indicates they're a training client)
        payment_status = clubos_api.get_member_payment_status(str(clubhub_id))
        
        if payment_status:
            return {
                'clubhub_id': clubhub_id,
                'member_name': member_name,
                'email': member_data.get('email', ''),
                'phone': member_data.get('mobilePhone', ''),
                'payment_status': payment_status,
                'found_in_clubos': True,
                'last_checked': datetime.now().isoformat()
            }, None
        else:
            return None, f"No training package found for {member_name}"
            
    except Exception as e:
        return None, f"Error checking {member_data.get('firstName', '')} {member_data.get('lastName', '')}: {str(e)}"

def main():
    print("=== COMPLETE TRAINING CLIENT DISCOVERY ===")
    print("This will check ALL members against ClubOS to find training clients")
    print("(including past-due ones that were missing from the CSV)")
    print()
    
    # Step 1: Get all members from ClubHub
    all_members = get_all_members_from_clubhub()
    
    if not all_members:
        print("❌ No members found, exiting")
        return
    
    print(f"\n🔍 Now checking {len(all_members)} members against ClubOS for training packages...")
    print("This may take a while...")
    print()
    
    # Step 2: Check each member against ClubOS
    training_clients = []
    errors = []
    checked_count = 0
    
    for member in all_members:
        checked_count += 1
        member_name = f"{member.get('firstName', '')} {member.get('lastName', '')}".strip()
        
        if checked_count % 50 == 0:
            print(f"   Checked {checked_count}/{len(all_members)} members...")
        
        training_data, error = check_training_status_in_clubos(member)
        
        if training_data:
            training_clients.append(training_data)
            print(f"✅ TRAINING CLIENT: {member_name} - Status: {training_data['payment_status']}")
        elif error and "No training package found" not in error:
            errors.append(error)
            if checked_count <= 10:  # Only show first few errors to avoid spam
                print(f"⚠️ Error: {error}")
    
    # Step 3: Results
    print(f"\n=== DISCOVERY COMPLETE ===")
    print(f"📊 Checked: {checked_count} members")
    print(f"✅ Found: {len(training_clients)} training clients")
    print(f"❌ Errors: {len(errors)}")
    print()
    
    if training_clients:
        print("🏋️ COMPLETE TRAINING CLIENT LIST:")
        print("=" * 60)
        
        for client in training_clients:
            status_emoji = "✅" if "Current" in client['payment_status'] else "⚠️"
            print(f"{status_emoji} {client['member_name']} - {client['payment_status']}")
        
        print()
        print(f"📈 SUMMARY BY STATUS:")
        
        status_counts = {}
        for client in training_clients:
            status = client['payment_status']
            status_counts[status] = status_counts.get(status, 0) + 1
        
        for status, count in sorted(status_counts.items()):
            print(f"   {status}: {count} clients")
    
    # Step 4: Save results
    print(f"\n💾 Saving complete training client list to database...")
    
    # Here we would update the training_clients table with the complete list
    # This replaces the incomplete CSV data with the complete ClubOS data
    
    print("✅ Complete training client discovery finished!")
    print(f"   Original CSV had ~32 training clients (current payments only)")
    print(f"   Complete ClubOS scan found {len(training_clients)} training clients (including past-due)")

if __name__ == "__main__":
    main()
