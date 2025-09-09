#!/usr/bin/env python3
"""
Find the correct member ID for Jeremy Mayo to receive messages
The issue is that 187032782 is the staff account ID, but we need the member ID for receiving messages
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.clubos_messaging_client import ClubOSMessagingClient
from src.config.secrets_local import get_secret
import requests
from bs4 import BeautifulSoup
import re

def find_correct_member_id():
    """Find the correct member ID for Jeremy Mayo to receive messages"""
    
    print("🔍 FINDING CORRECT MEMBER ID FOR MESSAGE RECEPTION")
    print("=" * 60)
    print("Issue: 187032782 is staff account ID, need member ID for receiving messages")
    print()
    
    # Get credentials
    username = get_secret("clubos-username")
    password = get_secret("clubos-password")
    
    # Create client and authenticate
    client = ClubOSMessagingClient(username, password)
    if not client.authenticate():
        print("❌ Authentication failed")
        return None
    
    print("✅ Authentication successful")
    print()
    
    try:
        # Search for Jeremy Mayo in the member search
        print("🔍 Searching for Jeremy Mayo in member search...")
        
        search_url = f"{client.base_url}/action/Dashboard/search"
        search_data = {
            "searchText": "Jeremy Mayo",
            "searchType": "member"
        }
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Referer": f"{client.base_url}/action/Dashboard/view",
            "Origin": client.base_url,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        response = client.session.post(search_url, data=search_data, headers=headers, timeout=30, verify=False)
        
        if response.ok:
            print(f"✅ Search response received: {response.status_code}")
            
            # Parse the search results
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for member search results
            search_results = soup.find_all('div', class_='search-result')
            
            print(f"📊 Found {len(search_results)} search results")
            
            for i, result in enumerate(search_results):
                text = result.get_text(strip=True)
                print(f"   Result {i+1}: {text[:100]}...")
                
                # Look for data attributes that might contain member IDs
                data_attrs = [attr for attr in result.attrs if attr.startswith('data-')]
                for attr in data_attrs:
                    value = result.get(attr)
                    if value and '187032782' in str(value):
                        print(f"   ✅ Found matching data attribute: {attr} = {value}")
                
                # Look for onclick handlers
                onclick = result.get('onclick', '')
                if onclick and '187032782' in onclick:
                    print(f"   ✅ Found matching onclick: {onclick}")
                
                # Look for href attributes
                href = result.get('href', '')
                if href and '187032782' in href:
                    print(f"   ✅ Found matching href: {href}")
            
            # Save the search results for analysis
            with open('member_search_results.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            print("💾 Saved search results to member_search_results.html")
            
        else:
            print(f"❌ Search failed: {response.status_code}")
            
        # Try a different approach - look at the member profile page
        print("\n🔍 Checking member profile page...")
        
        profile_url = f"{client.base_url}/action/Dashboard/member/187032782"
        profile_response = client.session.get(profile_url, headers=headers, timeout=30, verify=False)
        
        if profile_response.ok:
            print(f"✅ Profile page loaded: {profile_response.status_code}")
            
            # Look for messaging elements on the profile page
            soup = BeautifulSoup(profile_response.text, 'html.parser')
            
            # Look for messaging buttons or forms
            messaging_elements = soup.find_all(['a', 'button', 'form'], string=re.compile(r'message|text|email', re.I))
            
            print(f"📊 Found {len(messaging_elements)} messaging elements")
            
            for i, element in enumerate(messaging_elements):
                print(f"   Element {i+1}: {element.name} - {element.get_text(strip=True)[:50]}...")
                
                # Look for data attributes
                data_attrs = [attr for attr in element.attrs if attr.startswith('data-')]
                for attr in data_attrs:
                    value = element.get(attr)
                    print(f"     {attr}: {value}")
            
            # Save the profile page for analysis
            with open('member_profile_page.html', 'w', encoding='utf-8') as f:
                f.write(profile_response.text)
            print("💾 Saved profile page to member_profile_page.html")
            
        else:
            print(f"❌ Profile page failed: {profile_response.status_code}")
            
        print("\n💡 POSSIBLE SOLUTIONS:")
        print("1. Jeremy Mayo might need a separate member account for receiving messages")
        print("2. The staff account might not be able to receive messages")
        print("3. We might need to use a different member ID for message reception")
        print("4. The messaging system might be configured differently for staff members")
        
        return None
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    member_id = find_correct_member_id()
    if member_id:
        print(f"🎯 Correct Member ID for receiving messages: {member_id}")
    else:
        print("❌ Could not find correct member ID")


