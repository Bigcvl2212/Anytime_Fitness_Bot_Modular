#!/usr/bin/env python3
"""
Complete Training Client Discovery - Jordan's Method

This replicates exactly how Jordan's training data was successfully pulled.
We'll run the same _fetch_fresh_funding_data() function for all members
to find everyone with active training packages.
"""

import sys
import os
import sqlite3
from datetime import datetime

# Add paths
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'services'))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.clubhub_api_client import ClubHubAPIClient
from config.clubhub_credentials import CLUBHUB_EMAIL, CLUBHUB_PASSWORD
from clean_dashboard import TrainingPackageCache

def main():
    print("=== JORDAN'S METHOD: COMPLETE TRAINING CLIENT DISCOVERY ===")
    print("Replicating the exact method that worked for Jordan's data")
    print()
    
    # Step 1: Get all members from ClubHub
    print("🔐 Connecting to ClubHub...")
    client = ClubHubAPIClient()
    
    if not client.authenticate(CLUBHUB_EMAIL, CLUBHUB_PASSWORD):
        print("❌ ClubHub authentication failed")
        return
    
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
        page += 1
        
        if len(members) < 100:
            break
    
    print(f"📋 Total members retrieved: {len(all_members)}")
    print()
    
    # Step 2: Initialize the training package cache (same as Jordan's method)
    cache = TrainingPackageCache()
    
    # Step 3: Test _fetch_fresh_funding_data on all members (Jordan's exact method)
    print("🔍 Testing Jordan's exact funding data method on all members...")
    print("This may take a while...")
    print()
    
    training_clients_found = []
    checked_count = 0
    
    for member in all_members:
        checked_count += 1
        member_name = f"{member.get('firstName', '')} {member.get('lastName', '')}".strip()
        member_id = str(member.get('id'))  # ClubHub ID
        
        if checked_count % 50 == 0:
            print(f"   Checked {checked_count}/{len(all_members)} members... Found {len(training_clients_found)} training clients so far")
        
        try:
            # Use Jordan's exact method: _fetch_fresh_funding_data
            funding_data = cache._fetch_fresh_funding_data(member_id, member_name)
            
            if funding_data:
                training_clients_found.append({
                    'member_name': member_name,
                    'clubhub_id': member_id,
                    'email': member.get('email', ''),
                    'phone': member.get('mobilePhone', ''),
                    'payment_status': funding_data.get('payment_status'),
                    'funding_status': funding_data.get('funding_status'),
                    'package_name': funding_data.get('package_name'),
                    'last_updated': funding_data.get('last_updated')
                })
                
                status_emoji = "✅" if funding_data.get('funding_status') == 'funded' else "⚠️"
                print(f"{status_emoji} TRAINING CLIENT: {member_name} - {funding_data.get('payment_status')}")
                
        except Exception as e:
            if checked_count <= 5:  # Only show first few errors
                print(f"⚠️ Error checking {member_name}: {str(e)}")
    
    # Step 4: Results
    print(f"\n=== DISCOVERY COMPLETE (JORDAN'S METHOD) ===")
    print(f"📊 Checked: {checked_count} members")
    print(f"✅ Found: {len(training_clients_found)} training clients")
    print()
    
    if training_clients_found:
        print("🏋️ COMPLETE TRAINING CLIENT LIST (Jordan's Method):")
        print("=" * 70)
        
        # Check if Dennis is in the list
        dennis_found = False
        for client in training_clients_found:
            status_emoji = "✅" if client['funding_status'] == 'funded' else "⚠️"
            print(f"{status_emoji} {client['member_name']} - {client['payment_status']}")
            
            if 'DENNIS' in client['member_name'].upper() and 'ROST' in client['member_name'].upper():
                dennis_found = True
                print(f"   🎯 DENNIS FOUND! Payment Status: {client['payment_status']}")
        
        print()
        print(f"📈 SUMMARY:")
        
        # Count by status
        status_counts = {}
        for client in training_clients_found:
            status = client['payment_status']
            status_counts[status] = status_counts.get(status, 0) + 1
        
        for status, count in sorted(status_counts.items()):
            print(f"   {status}: {count} clients")
        
        if dennis_found:
            print(f"\n🎉 SUCCESS: Dennis Rost found as training client!")
        else:
            print(f"\n❌ Dennis Rost NOT found - may need manual investigation")
    
    else:
        print("❌ No training clients found - there might be an issue with the API")
    
    print(f"\n✅ Jordan's method discovery complete!")

if __name__ == "__main__":
    main()
