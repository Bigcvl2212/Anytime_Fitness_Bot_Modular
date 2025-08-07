#!/usr/bin/env python3
"""
Quick test: Check Jordan specifically to see if the API works
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'services'))

from api.clubhub_api_client import ClubHubAPIClient
from config.clubhub_credentials import CLUBHUB_EMAIL, CLUBHUB_PASSWORD

# Import the actual ClubOS training API
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from clubos_training_api import ClubOSTrainingPackageAPI

print("=== TESTING JORDAN KRUEGER SPECIFICALLY ===")

client = ClubHubAPIClient()
if client.authenticate(CLUBHUB_EMAIL, CLUBHUB_PASSWORD):
    print("✅ ClubHub authenticated")
    
    clubos_api = ClubOSTrainingPackageAPI()
    print("✅ ClubOS training API initialized")
    
    # Get all members and find Jordan
    all_members = []
    page = 1
    while page <= 6:
        members = client.get_all_members(page=page, page_size=100)
        if not members:
            break
        all_members.extend(members)
        page += 1
    
    # Find Jordan
    jordan = None
    for member in all_members:
        if 'JORDAN' in member.get('firstName', '').upper() and 'KRUEGER' in member.get('lastName', '').upper():
            jordan = member
            break
    
    if jordan:
        print(f"\n=== JORDAN KRUEGER FOUND ===")
        print(f"ClubHub ID: {jordan.get('id')}")
        print(f"Name: {jordan.get('firstName')} {jordan.get('lastName')}")
        
        jordan_id = str(jordan.get('id'))
        
        try:
            print(f"🔍 Checking ClubOS for Jordan's training data...")
            payment_status = clubos_api.get_member_payment_status(jordan_id)
            
            if payment_status:
                print(f"✅ JORDAN HAS TRAINING DATA!")
                print(f"   Payment Status: {payment_status}")
                print(f"   Data Type: {type(payment_status)}")
            else:
                print(f"❌ Jordan has no training data in ClubOS")
                
        except Exception as e:
            print(f"⚠️ Error checking Jordan: {str(e)}")
    else:
        print("❌ Jordan not found in ClubHub")
        
    # Also find Dennis and check him
    dennis = None
    for member in all_members:
        if 'DENNIS' in member.get('firstName', '').upper() and 'ROST' in member.get('lastName', '').upper():
            dennis = member
            break
    
    if dennis:
        print(f"\n=== DENNIS ROST FOUND ===")
        print(f"ClubHub ID: {dennis.get('id')}")
        print(f"Name: {dennis.get('firstName')} {dennis.get('lastName')}")
        
        dennis_id = str(dennis.get('id'))
        
        try:
            print(f"🔍 Checking ClubOS for Dennis's training data...")
            payment_status = clubos_api.get_member_payment_status(dennis_id)
            
            if payment_status:
                print(f"✅ DENNIS HAS TRAINING DATA!")
                print(f"   Payment Status: {payment_status}")
                print(f"   Data Type: {type(payment_status)}")
            else:
                print(f"❌ Dennis has no training data in ClubOS")
                
        except Exception as e:
            print(f"⚠️ Error checking Dennis: {str(e)}")
    
    print(f"\nTotal members in ClubHub: {len(all_members)}")

else:
    print("❌ ClubHub authentication failed")
