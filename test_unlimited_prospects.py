#!/usr/bin/env python3
"""
Test script to verify we can get all 9000+ prospects from ClubHub API
Uses the exact same approach as the working clean_dashboard.py
"""

import requests
import time
import sys
import json

def test_unlimited_prospects():
    """Test getting all prospects from ClubHub API with unlimited pagination"""
    print("🔄 Testing unlimited prospects from ClubHub API...")
    
    # ClubHub credentials - direct definition to avoid import issues
    CLUBHUB_EMAIL = "mayo.jeremy2212@gmail.com"
    CLUBHUB_PASSWORD = "SruLEqp464_GLrF"
    
    CLUBHUB_LOGIN_URL = "https://clubhub-ios-api.anytimefitness.com/api/login"
    USERNAME = CLUBHUB_EMAIL
    PASSWORD = CLUBHUB_PASSWORD
    
    headers = {
        "Content-Type": "application/json",
        "API-version": "1",
        "Accept": "application/json",
        "User-Agent": "ClubHub Store/2.15.1 (com.anytimefitness.Club-Hub; build:1007; iOS 18.5.0) Alamofire/5.6.4",
    }
    
    session = requests.Session()
    session.headers.update(headers)
    
    # Login to get bearer token
    login_data = {"username": USERNAME, "password": PASSWORD}
    login_response = session.post(CLUBHUB_LOGIN_URL, json=login_data)
    
    if login_response.status_code != 200:
        print(f"❌ Failed to authenticate with ClubHub API: {login_response.status_code}")
        return
        
    login_result = login_response.json()
    bearer_token = login_result.get('accessToken')
    
    if not bearer_token:
        print("❌ No access token received")
        return
        
    session.headers.update({"Authorization": f"Bearer {bearer_token}"})
    
    # Get prospects from ClubHub API - EXACT same implementation as working clean_dashboard.py
    club_id = "1156"
    all_prospects = []
    page = 1
    start_time = time.time()
    
    try:
        while True:
            # Try the v1.0 API endpoint with days=10000 parameter
            prospects_url = f"https://clubhub-ios-api.anytimefitness.com/api/v1.0/clubs/{club_id}/prospects"
            params = {
                "page": str(page),
                "pageSize": "100",
                "days": "10000",  # Get historical data going back 10,000 days
                "includeInactive": "true",
                "includeAll": "true",
                "status": "all"
            }
            print(f"📄 Fetching prospects page {page} with days=10000...")
            prospects_response = session.get(prospects_url, params=params)
            
            if prospects_response.status_code != 200:
                print(f"❌ Prospects API error on page {page}: {prospects_response.status_code}")
                break
                
            prospects_data = prospects_response.json()
            
            if len(prospects_data) == 0:
                print(f"📄 No more prospects found on page {page}")
                break
            
            all_prospects.extend(prospects_data)
            print(f"📄 Page {page}: Found {len(prospects_data)} prospects (Total so far: {len(all_prospects)})")
            
            # If we got less than the page size, we've reached the end
            if len(prospects_data) < 100:
                print(f"📄 Received less than full page size ({len(prospects_data)} < 100). Reached end of data.")
                break
                
            page += 1
            
            # NO PAGE LIMIT - REMOVED TO GET ALL 9000+ PROSPECTS
            # We're removing this limit to get ALL prospects
            
            # Add a progress update every 10 pages
            if page % 10 == 0:
                elapsed = time.time() - start_time
                print(f"⏱️ Progress: {len(all_prospects)} prospects after {elapsed:.2f} seconds")
                
                # Optional: Save progress to a file in case of interruption
                with open(f"prospects_progress_page_{page}.json", "w") as f:
                    json.dump(all_prospects, f)
                    
        # Done fetching all prospects
        elapsed = time.time() - start_time
        print(f"✅ Successfully fetched {len(all_prospects)} prospects in {elapsed:.2f} seconds")
        
        # Save all prospects to a file
        with open("all_prospects.json", "w") as f:
            json.dump(all_prospects, f)
            
        # Print some sample prospects
        print("\n📋 Sample prospects:")
        for i, prospect in enumerate(all_prospects[:5]):
            name = f"{prospect.get('firstName', '')} {prospect.get('lastName', '')}".strip()
            email = prospect.get('email', 'No email')
            print(f"  {i+1}. {name} - {email}")
            
        print(f"\n🎉 SUCCESS! Got {len(all_prospects)} prospects from ClubHub API")
        
    except Exception as e:
        print(f"❌ Error getting prospects: {e}")
        
if __name__ == "__main__":
    test_unlimited_prospects()



