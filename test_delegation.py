#!/usr/bin/env python3
"""
Test ClubOS delegation and agreement API access
"""

import requests
import json
import time
from config.clubhub_credentials import CLUBOS_USERNAME, CLUBOS_PASSWORD

def test_delegation_flow():
    """Test if we need to delegate to a specific user to access agreements"""
    
    print("🧪 Testing ClubOS delegation for agreement access...")
    
    # Set up session with exact same authentication as existing code
    session = requests.Session()
    
    # Use the exact same authentication flow from clubos_training_api.py
    try:
        # Step 1: GET login page and extract tokens
        r0 = session.get("https://anytime.club-os.com/action/Login/view", timeout=20)
        if r0.status_code not in (200, 302):
            print(f"❌ Login view failed: {r0.status_code}")
            return
        
        # Extract form tokens
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(r0.text, 'html.parser')
        sp = soup.find('input', {'name': '_sourcePage'})
        fp = soup.find('input', {'name': '__fp'})
        _sourcePage = sp.get('value') if sp else ''
        __fp = fp.get('value') if fp else ''
        
        # Step 2: POST credentials to /action/Login
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Referer': 'https://anytime.club-os.com/action/Login/view',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        }
        form = {
            'login': 'Submit',
            'username': CLUBOS_USERNAME,
            'password': CLUBOS_PASSWORD,
            '_sourcePage': _sourcePage or '',
            '__fp': __fp or '',
        }
        r1 = session.post("https://anytime.club-os.com/action/Login", data=form, headers=headers, timeout=30, allow_redirects=True)
        
        if r1.status_code not in (200, 302):
            print(f"❌ Login failed: {r1.status_code}")
            return
        
        # Step 3: Touch dashboard to finalize (like the existing code)
        session.get("https://anytime.club-os.com/action/Dashboard", timeout=15)
        print("✅ Authenticated successfully")
        
        # Get Bearer token
        bearer_token = None
        for cookie in session.cookies:
            if cookie.name == 'apiV3AccessToken':
                bearer_token = cookie.value
                break
        
        if not bearer_token:
            print("❌ No Bearer token found")
            return
        
        print(f"🔑 Bearer token: {bearer_token[:50]}...")
        
        # Now try to find who we can delegate to
        print("\n🔍 Looking for delegation options...")
        
        # The training clients we already know about are assignees, so let's use the existing assignees endpoint
        assignees_url = f"https://anytime.club-os.com/action/Assignees/members?_={int(time.time() * 1000)}"
        
        assignees_response = session.get(assignees_url)
        print(f"📊 Assignees response: {assignees_response.status_code}")
        
        if assignees_response.status_code == 200:
            # Parse the HTML to get training client IDs
            soup = BeautifulSoup(assignees_response.text, 'html.parser')
            
            # Look for client elements with onclick handlers
            client_elements = soup.find_all('li', class_='client')
            if client_elements:
                print(f"📋 Found {len(client_elements)} training clients")
                
                # Extract member IDs from onclick handlers
                member_ids = []
                for i, element in enumerate(client_elements[:5]):  # Test with first 5
                    onclick = element.get('onclick', '')
                    name = element.get_text().strip()
                    print(f"   Element {i+1}: {name}")
                    print(f"     onclick: {onclick}")
                    print(f"     classes: {element.get('class', [])}")
                    
                    # Try different patterns to extract member ID
                    import re
                    
                    # Pattern 1: delegate('123456') 
                    match1 = re.search(r"delegate\('(\d+)'\)", onclick)
                    if match1:
                        member_id = match1.group(1)
                        member_ids.append(member_id)
                        print(f"     ✅ Found member ID (pattern 1): {member_id}")
                        continue
                    
                    # Pattern 2: delegate("123456")
                    match2 = re.search(r'delegate\("(\d+)"\)', onclick)
                    if match2:
                        member_id = match2.group(1)
                        member_ids.append(member_id)
                        print(f"     ✅ Found member ID (pattern 2): {member_id}")
                        continue
                    
                    # Pattern 3: any number in onclick
                    match3 = re.search(r'(\d{6,})', onclick)
                    if match3:
                        member_id = match3.group(1)
                        member_ids.append(member_id)
                        print(f"     ✅ Found member ID (pattern 3): {member_id}")
                        continue
                    
                    # Pattern 4: look in other attributes
                    data_id = element.get('data-id', '')
                    data_member_id = element.get('data-member-id', '')
                    if data_id:
                        print(f"     data-id: {data_id}")
                        if data_id.isdigit():
                            member_ids.append(data_id)
                            print(f"     ✅ Found member ID in data-id: {data_id}")
                            continue
                    if data_member_id:
                        print(f"     data-member-id: {data_member_id}")
                        if data_member_id.isdigit():
                            member_ids.append(data_member_id)
                            print(f"     ✅ Found member ID in data-member-id: {data_member_id}")
                            continue
                    
                    print(f"     ❌ No member ID found")
                
                # Also save the HTML for manual inspection
                with open('assignees_html_debug.html', 'w', encoding='utf-8') as f:
                    f.write(assignees_response.text)
                print(f"\n💾 Saved assignees HTML to 'assignees_html_debug.html' for inspection")
                
                # Test delegation to one of these members
                if member_ids:
                    test_member_id = member_ids[0]  # Use first member
                    print(f"\n🎯 Testing delegation to member: {test_member_id}")
                    
                    # Try to delegate (this might be a form POST or AJAX call)
                    delegate_url = "https://anytime.club-os.com/action/Delegate"
                    delegate_data = {'memberId': test_member_id}
                    
                    delegate_response = session.post(delegate_url, data=delegate_data)
                    print(f"📊 Delegation response: {delegate_response.status_code}")
                    
                    if delegate_response.status_code in (200, 302):
                        print("✅ Delegation successful")
                        
                        # Update Bearer token if we got a new one
                        new_bearer_token = None
                        for cookie in session.cookies:
                            if cookie.name == 'apiV3AccessToken':
                                new_bearer_token = cookie.value
                                break
                        
                        if new_bearer_token and new_bearer_token != bearer_token:
                            print(f"🔑 New Bearer token after delegation: {new_bearer_token[:50]}...")
                            bearer_token = new_bearer_token
                        
                        # Now try the agreements API again
                        api_headers = {
                            'Authorization': f'Bearer {bearer_token}',
                            'Accept': 'application/json, text/plain, */*',
                            'Referer': 'https://anytime.club-os.com/action/ClubServicesNew',
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                        }
                        
                        list_url = "https://anytime.club-os.com/api/agreements/package_agreements/list"
                        print(f"\n📋 Testing agreements API after delegation: {list_url}")
                        
                        list_response = session.get(list_url, headers=api_headers)
                        print(f"📊 Status: {list_response.status_code}")
                        
                        if list_response.status_code == 200:
                            print("🎉 SUCCESS! Agreements API working after delegation!")
                            try:
                                data = list_response.json()
                                print(f"📋 Found {len(data) if isinstance(data, list) else 'N/A'} agreements")
                                
                                # Save the response
                                with open('agreements_after_delegation.json', 'w') as f:
                                    json.dump(data, f, indent=2)
                                print("💾 Saved to 'agreements_after_delegation.json'")
                                
                            except Exception as e:
                                print(f"⚠️ JSON parse error: {e}")
                                print(f"📄 Raw response: {list_response.text[:500]}")
                        else:
                            print(f"❌ Still failing: {list_response.text[:200]}")
                    else:
                        print(f"❌ Delegation failed: {delegate_response.text[:200]}")
                else:
                    print("❌ No member IDs found in assignees")
            else:
                print("❌ No client elements found")
        else:
            print(f"❌ Assignees request failed: {assignees_response.status_code}")
    
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_delegation_flow()
