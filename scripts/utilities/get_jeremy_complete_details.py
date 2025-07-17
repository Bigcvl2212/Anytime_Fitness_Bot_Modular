#!/usr/bin/env python3
"""
Get Jeremy Mayo's complete member details using the confirmed member ID
"""

from services.api.clubos_api_client import ClubOSAPIClient
from config.secrets_local import get_secret
from bs4 import BeautifulSoup
import re
import json

def get_jeremy_complete_details():
    """Get Jeremy Mayo's complete member details"""
    
    print("🔍 Getting Jeremy Mayo's complete member details...")
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
    
    # Jeremy Mayo's confirmed member ID
    jeremy_member_id = "187032782"
    
    print(f"2. Getting details for Member ID: {jeremy_member_id}")
    print("-" * 40)
    
    headers = client.auth.get_headers()
    
    # Try different endpoints to get member details
    endpoints_to_try = [
        f"/action/Delegate/{jeremy_member_id}/url=/action/Dashboard",
        f"/action/Members/profile/{jeremy_member_id}",
        f"/action/Members/view/{jeremy_member_id}",
        f"/api/members/{jeremy_member_id}",
        f"/action/Delegate/{jeremy_member_id}/url=false"
    ]
    
    member_details = {
        "member_id": jeremy_member_id,
        "name": "Jeremy Mayo",
        "email": "mayojeremy2212@gmail.com",
        "profile_urls": [],
        "extracted_data": {}
    }
    
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
                member_details["profile_urls"].append(f"{client.base_url}{endpoint}")
                
                # Parse the HTML response
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract key information
                print(f"   📄 Extracting data...")
                
                # Look for email addresses
                email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
                emails = re.findall(email_pattern, response.text)
                if emails:
                    print(f"   📧 Emails found: {emails}")
                    member_details["extracted_data"]["emails"] = emails
                
                # Look for phone numbers
                phone_pattern = r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
                phones = re.findall(phone_pattern, response.text)
                if phones:
                    print(f"   📞 Phone numbers found: {phones}")
                    member_details["extracted_data"]["phones"] = phones
                
                # Look for member ID patterns
                id_patterns = [
                    r'Member ID[:\s]*(\d+)',
                    r'ID[:\s]*(\d+)',
                    r'Member[:\s]*(\d+)',
                    r'data-member-id="(\d+)"',
                    r'data-user-id="(\d+)"',
                    r'data-id="(\d+)"'
                ]
                
                for pattern in id_patterns:
                    matches = re.findall(pattern, response.text, re.IGNORECASE)
                    if matches:
                        print(f"   🔑 Member IDs found: {matches}")
                        member_details["extracted_data"]["member_ids"] = matches
                
                # Look for ProspectID specifically
                prospect_patterns = [
                    r'ProspectID[:\s]*(\d+)',
                    r'Prospect ID[:\s]*(\d+)',
                    r'prospect[:\s]*(\d+)',
                    r'prospect_id[:\s]*(\d+)'
                ]
                
                for pattern in prospect_patterns:
                    matches = re.findall(pattern, response.text, re.IGNORECASE)
                    if matches:
                        print(f"   🎯 ProspectID found: {matches}")
                        member_details["extracted_data"]["prospect_ids"] = matches
                
                # Look for address information
                address_patterns = [
                    r'Address[:\s]*([^\n\r]+)',
                    r'Street[:\s]*([^\n\r]+)',
                    r'City[:\s]*([^\n\r]+)',
                    r'State[:\s]*([^\n\r]+)',
                    r'Zip[:\s]*(\d{5})'
                ]
                
                for pattern in address_patterns:
                    matches = re.findall(pattern, response.text, re.IGNORECASE)
                    if matches:
                        print(f"   🏠 Address info found: {matches}")
                        member_details["extracted_data"]["address"] = matches
                
                # Look for membership information
                membership_patterns = [
                    r'Membership[:\s]*([^\n\r]+)',
                    r'Plan[:\s]*([^\n\r]+)',
                    r'Status[:\s]*([^\n\r]+)',
                    r'Join Date[:\s]*([^\n\r]+)',
                    r'Start Date[:\s]*([^\n\r]+)'
                ]
                
                for pattern in membership_patterns:
                    matches = re.findall(pattern, response.text, re.IGNORECASE)
                    if matches:
                        print(f"   💳 Membership info found: {matches}")
                        member_details["extracted_data"]["membership"] = matches
                
                # Save the response for detailed analysis
                filename = f"jeremy_details_{endpoint.replace('/', '_')}.html"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(response.text)
                print(f"   💾 Saved response to: {filename}")
                
            else:
                print(f"   ❌ Failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ⚠️ Error: {e}")
            continue
    
    # Print summary
    print(f"\n3. Summary of Jeremy Mayo's member details:")
    print("=" * 60)
    print(f"   Member ID: {member_details['member_id']}")
    print(f"   Name: {member_details['name']}")
    print(f"   Email: {member_details['email']}")
    print(f"   Profile URLs: {len(member_details['profile_urls'])} found")
    
    if member_details['extracted_data']:
        print(f"   Extracted Data:")
        for key, value in member_details['extracted_data'].items():
            print(f"     {key}: {value}")
    
    # Save the complete details to JSON
    with open('jeremy_member_details.json', 'w', encoding='utf-8') as f:
        json.dump(member_details, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Complete details saved to: jeremy_member_details.json")
    
    return member_details

if __name__ == "__main__":
    get_jeremy_complete_details() 