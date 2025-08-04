#!/usr/bin/env python3
"""
Test ClubHub API integration to get real-time member data
"""
import requests
import json
from config.clubhub_credentials import CLUBHUB_EMAIL, CLUBHUB_PASSWORD

def test_clubhub_api():
    """Test the ClubHub API to get fresh member data"""
    try:
        print("🔄 Testing ClubHub API integration...")
        
        session = requests.Session()
        
        # Step 1: Login to ClubHub
        print("🔐 Logging into ClubHub...")
        login_url = "https://app.clubhub.com/api/auth/login"
        login_data = {
            'email': CLUBHUB_EMAIL,
            'password': CLUBHUB_PASSWORD
        }
        
        login_response = session.post(login_url, json=login_data)
        print(f"Login response status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            print("✅ ClubHub login successful!")
            
            # Check if we got a token
            try:
                login_result = login_response.json()
                print(f"Login result: {login_result}")
                
                if 'token' in login_result:
                    session.headers.update({
                        'Authorization': f"Bearer {login_result['token']}"
                    })
                    print("✅ Authorization token set")
            except:
                print("ℹ️ No JSON response or token, proceeding with cookies")
            
            # Step 2: Get all members
            print("📊 Fetching all members from ClubHub...")
            members_url = "https://app.clubhub.com/api/members/export"
            
            members_response = session.get(members_url)
            print(f"Members response status: {members_response.status_code}")
            
            if members_response.status_code == 200:
                try:
                    members_data = members_response.json()
                    print(f"✅ Got {len(members_data)} members from ClubHub!")
                    
                    # Count past due members
                    red_count = 0
                    yellow_count = 0
                    
                    for member in members_data:
                        status_msg = str(member.get('status_message', member.get('StatusMessage', ''))).strip()
                        
                        if 'Past Due more than 30 days' in status_msg or 'Delinquent' in status_msg:
                            red_count += 1
                        elif ('Past Due 6-30 days' in status_msg or 
                              'pending cancel' in status_msg.lower() or 
                              'expire within 30 days' in status_msg):
                            yellow_count += 1
                    
                    print(f"📊 ClubHub Counts: {red_count} red, {yellow_count} yellow")
                    
                    # Show a sample member
                    if members_data:
                        sample_member = members_data[0]
                        print(f"📋 Sample member data structure:")
                        for key, value in sample_member.items():
                            print(f"  {key}: {value}")
                    
                    return True
                    
                except Exception as e:
                    print(f"❌ Error parsing members response: {e}")
                    print(f"Response content: {members_response.text[:500]}...")
                    return False
            else:
                print(f"❌ Failed to get members: {members_response.status_code}")
                print(f"Response: {members_response.text[:500]}...")
                return False
        else:
            print(f"❌ ClubHub login failed: {login_response.status_code}")
            print(f"Response: {login_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing ClubHub API: {e}")
        return False

if __name__ == "__main__":
    test_clubhub_api()
