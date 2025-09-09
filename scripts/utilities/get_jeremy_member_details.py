#!/usr/bin/env python3
"""
Get Jeremy Mayo's detailed member information from ClubOS
"""

from src.services.api.clubos_api_client import ClubOSAPIClient
from config.secrets_local import get_secret
import json

def get_jeremy_member_details():
    """Get Jeremy Mayo's detailed member information"""
    
    print("🔍 Getting Jeremy Mayo's member details from ClubOS...")
    print("=" * 60)
    
    # Create API client and authenticate
    client = ClubOSAPIClient()
    username = get_secret("clubos-username")
    password = get_secret("clubos-password")
    
    print("1. Authenticating with ClubOS...")
    if not client.auth.login(username, password):
        print("❌ Authentication failed")
        return
    
    print("✅ Authentication successful")
    
    # Member IDs found in the search
    member_ids = [
        "160089696",  # First ID found
        "187032782",  # Staff ID from HAR
        "171493253",
        "172943137", 
        "171493425",
        "177305017",
        "171969865",
        "177869276",
        "185535724",
        "174195127"
    ]
    
    headers = client.auth.get_headers()
    
    for member_id in member_ids:
        print(f"\n2. Checking member ID: {member_id}")
        print("-" * 40)
        
        try:
            # Try to get member details using different endpoints
            endpoints_to_try = [
                f"/action/Members/profile/{member_id}",
                f"/action/Members/view/{member_id}",
                f"/api/members/{member_id}",
                f"/action/Delegate/{member_id}/url=false"
            ]
            
            for endpoint in endpoints_to_try:
                try:
                    response = client.auth.session.get(
                        f"{client.base_url}{endpoint}",
                        headers=headers,
                        timeout=30,
                        verify=False
                    )
                    
                    print(f"   Endpoint: {endpoint}")
                    print(f"   Status: {response.status_code}")
                    
                    if response.status_code == 200:
                        print(f"   ✅ Success!")
                        
                        # Check if this is Jeremy Mayo's profile
                        from bs4 import BeautifulSoup
                        soup = BeautifulSoup(response.text, 'html.parser')
                        text_content = soup.get_text().lower()
                        
                        if 'jeremy' in text_content and 'mayo' in text_content:
                            print(f"   🎯 This is Jeremy Mayo's profile!")
                            print(f"   📄 Profile preview:")
                            print(f"   {response.text[:1000]}...")
                            
                            # Extract key information
                            print(f"\n3. Extracting key information...")
                            
                            # Look for email
                            email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
                            import re
                            emails = re.findall(email_pattern, response.text)
                            if emails:
                                print(f"   📧 Emails found: {emails}")
                            
                            # Look for phone numbers
                            phone_pattern = r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
                            phones = re.findall(phone_pattern, response.text)
                            if phones:
                                print(f"   📞 Phone numbers found: {phones}")
                            
                            # Look for member ID patterns
                            id_patterns = [
                                r'Member ID[:\s]*(\d+)',
                                r'ID[:\s]*(\d+)',
                                r'Member[:\s]*(\d+)',
                                r'data-member-id="(\d+)"',
                                r'data-user-id="(\d+)"'
                            ]
                            
                            for pattern in id_patterns:
                                matches = re.findall(pattern, response.text, re.IGNORECASE)
                                if matches:
                                    print(f"   🔑 Member IDs found: {matches}")
                            
                            print(f"\n✅ Jeremy Mayo found!")
                            print(f"   Member ID: {member_id}")
                            print(f"   Profile URL: {client.base_url}{endpoint}")
                            
                            return {
                                "member_id": member_id,
                                "profile_url": f"{client.base_url}{endpoint}",
                                "emails": emails,
                                "phones": phones
                            }
                        
                        else:
                            print(f"   ❌ Not Jeremy Mayo's profile")
                        
                        break
                        
                except Exception as e:
                    print(f"   ⚠️ Endpoint failed: {e}")
                    continue
            
        except Exception as e:
            print(f"   ❌ Error checking member ID {member_id}: {e}")
            continue
    
    print(f"\n❌ Could not find Jeremy Mayo's detailed profile")
    return None

if __name__ == "__main__":
    get_jeremy_member_details() 