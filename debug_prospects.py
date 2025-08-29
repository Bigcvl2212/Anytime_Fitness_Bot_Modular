#!/usr/bin/env python3

import sys
import os
sys.path.append('src/services')
from api.clubhub_api_client import ClubHubAPIClient
sys.path.append('src/config')
from clubhub_credentials import CLUBHUB_EMAIL, CLUBHUB_PASSWORD
sys.path.append('src')
from clubos_fresh_data_api import ClubOSFreshDataAPI

def main():
    print("🔍 PROSPECT LOADING COMPARISON")
    print("="*60)
    
    # Check current ClubHub API
    print("1️⃣ Current ClubHub API:")
    client = ClubHubAPIClient()
    if client.authenticate(CLUBHUB_EMAIL, CLUBHUB_PASSWORD):
        print('✅ ClubHub authenticated')
        prospects = client.get_all_prospects_paginated()
        print(f'Current ClubHub prospects: {len(prospects)}')
        
        if prospects:
            print('First 3 ClubHub prospect examples:')
            for i, prospect in enumerate(prospects[:3]):
                name = f"{prospect.get('firstName', '')} {prospect.get('lastName', '')}".strip()
                status = prospect.get('status', 'Unknown')
                print(f'  {i+1}: {name} - {status}')
    else:
        print('❌ ClubHub authentication failed')
    
    print("\n" + "="*60)
    
    # Check old ClubOS Fresh Data API  
    print("2️⃣ Old ClubOS Fresh Data API:")
    api = ClubOSFreshDataAPI()
    old_prospects = api.get_fresh_prospects()
    print(f'Old ClubOS prospects: {len(old_prospects)}')
    
    if old_prospects:
        print('First 3 ClubOS prospect examples:')
        for i, prospect in enumerate(old_prospects[:3]):
            name = prospect.get('name', 'Unknown')
            status = prospect.get('status', 'Unknown')
            print(f'  {i+1}: {name} - {status}')
    
    print(f"\n📊 SUMMARY:")
    print(f"ClubHub API: {len(prospects) if 'prospects' in locals() else 0} prospects")
    print(f"ClubOS API: {len(old_prospects)} prospects")
    print(f"Missing: {9000 - (len(prospects) if 'prospects' in locals() else 0)} prospects from expected 9000")

if __name__ == "__main__":
    main()
