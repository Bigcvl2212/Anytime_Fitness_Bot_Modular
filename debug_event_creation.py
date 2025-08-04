#!/usr/bin/env python3
"""
Debug ClubOS event creation by inspecting the actual form requirements
"""

import json
from clubos_real_calendar_api import ClubOSRealCalendarAPI

def debug_event_creation():
    """Debug what's needed for actual event creation"""
    
    print("🔍 Debugging ClubOS Event Creation")
    print("=" * 50)
    
    # Check what's in the HAR file for the save action
    print("\n1. Analyzing HAR file for EventPopup/save...")
    
    with open('charles_session.chls/clubos_calendar_flow.har', 'r', encoding='utf-8') as f:
        har_data = json.load(f)
    
    entries = har_data.get('log', {}).get('entries', [])
    
    # Find the save request
    for entry in entries:
        request = entry.get('request', {})
        response = entry.get('response', {})
        url = request.get('url', '')
        
        if '/action/EventPopup/save' in url:
            print(f"\n=== EventPopup/save Request ===")
            print(f"Status: {response.get('status')}")
            print(f"URL: {url}")
            
            # Check for redirects
            if response.get('status') == 302:
                for header in response.get('headers', []):
                    if header.get('name', '').lower() == 'location':
                        print(f"Redirect to: {header.get('value')}")
            
            # Analyze all headers
            print("\nRequest Headers:")
            for header in request.get('headers', []):
                name = header.get('name', '')
                value = header.get('value', '')
                if 'authorization' in name.lower():
                    value = value[:50] + '...'
                print(f"  {name}: {value}")
            
            # Analyze POST data structure
            post_data = request.get('postData', {})
            print(f"\nPOST Data Structure:")
            print(f"  Keys: {list(post_data.keys())}")
            
            if 'params' in post_data:
                params = post_data['params']
                print(f"  Parameters count: {len(params)}")
                for param in params:
                    print(f"    {param}")
            
            if 'text' in post_data:
                text = post_data['text']
                print(f"  Text data: '{text}'")
            
            break
    
    print("\n2. Testing API connection...")
    api = ClubOSRealCalendarAPI("j.mayo", "L*KYqnec5z7nEL$")
    
    if api.authenticate():
        print("✅ Authentication successful")
        
        # Try to open the popup and see what we get back
        print("\n3. Opening event popup and checking response...")
        
        headers = api.standard_headers.copy()
        headers.update({
            'Authorization': f'Bearer {api.get_bearer_token()}',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': f'{api.base_url}/action/Calendar'
        })
        
        response = api.session.post(
            f"{api.base_url}/action/EventPopup/open",
            headers=headers,
            data={}
        )
        
        print(f"Popup response status: {response.status_code}")
        print(f"Response length: {len(response.text)}")
        
        # Look for form fields in the response
        if 'input' in response.text.lower():
            print("✅ Response contains form inputs")
            
            # Save the response to analyze form structure
            with open('event_popup_response.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            print("💾 Saved popup HTML to event_popup_response.html")
        else:
            print("❌ No form inputs found in response")
    
    else:
        print("❌ Authentication failed")

if __name__ == "__main__":
    debug_event_creation()
