#!/usr/bin/env python3
"""Test ClubOS leads endpoints to find the working one."""

import re
from clubos_training_api import ClubOSTrainingPackageAPI

def main():
    api = ClubOSTrainingPackageAPI()
    api.authenticate()
    
    session = api.session
    token = api.access_token
    user_id = api.session_data.get('loggedInUserId')
    
    print(f"User ID: {user_id}")
    print(f"Token: {token[:50] if token else 'None'}...")
    
    # Try to get the Leads dashboard page
    print("\n--- Checking Leads Dashboard Page ---")
    resp = session.get('https://anytime.club-os.com/action/Leads', timeout=30)
    print(f"Status: {resp.status_code}")
    print(f"Final URL: {resp.url}")
    
    html = resp.text
    
    # Search for API endpoints
    api_pattern = r'["\'](/api/[^"\']+)["\']'
    action_pattern = r'["\'](/action/[^"\']+)["\']'
    
    apis = re.findall(api_pattern, html)
    actions = re.findall(action_pattern, html)
    
    print(f"\nFound {len(apis)} API endpoint references:")
    for a in sorted(set(apis))[:20]:
        print(f"  {a}")
    
    print(f"\nFound {len(actions)} Action endpoint references:")
    for a in sorted(set(actions))[:20]:
        print(f"  {a}")
    
    # Also check for lead-related keywords
    print("\n--- Searching for 'lead' related patterns ---")
    lead_patterns = re.findall(r'["\'][^"\']*[Ll]ead[^"\']*["\']', html)
    for p in sorted(set(lead_patterns))[:15]:
        print(f"  {p}")
    
    # Try some specific data table endpoints
    print("\n--- Testing Data Table Endpoints ---")
    headers = {
        'accept': 'application/json',
        'authorization': f'Bearer {token}',
        'x-requested-with': 'XMLHttpRequest',
        'referer': 'https://anytime.club-os.com/action/Leads'
    }
    
    test_endpoints = [
        '/action/Leads/data',
        '/action/Leads/list/data',
        '/action/Lead/data',
        '/action/Leads/search',
        '/action/LeadSearch',
        '/action/LeadTable',
        '/action/LeadList',
        '/ajax/Leads/data',
    ]
    
    for ep in test_endpoints:
        url = f'https://anytime.club-os.com{ep}'
        try:
            r = session.get(url, headers=headers, timeout=10)
            print(f"{r.status_code} - {ep}")
            if r.status_code == 200 and len(r.text) > 100:
                preview = r.text[:200].replace('\n', ' ').replace('\r', '')
                print(f"    Content: {preview}")
        except Exception as e:
            print(f"ERR - {ep}: {e}")


if __name__ == "__main__":
    main()
