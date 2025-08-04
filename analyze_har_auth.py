#!/usr/bin/env python3
"""
Analyze HAR file to find event manipulation endpoints and form parameters
"""

import json

def analyze_event_manipulation():
    """Analyze how ClubOS manipulates calendar events"""
    
    # Load the HAR file
    with open('charles_session.chls/clubos_calendar_flow.har', 'r', encoding='utf-8') as f:
        har_data = json.load(f)
    
    entries = har_data.get('log', {}).get('entries', [])
    
    print("=== ClubOS Calendar Event Manipulation Analysis ===\n")
    
    critical_endpoints = [
        '/action/EventPopup/save',
        '/action/EventPopup/remove', 
        '/action/EventPopup/open',
        '/action/UserSuggest/attendee-search',
        '/action/Options/club-services'
    ]
    
    for i, entry in enumerate(entries):
        request = entry.get('request', {})
        response = entry.get('response', {})
        url = request.get('url', '')
        method = request.get('method', '')
        status = response.get('status', 0)
        
        if any(endpoint in url for endpoint in critical_endpoints):
            print(f"=== {method} {url} ===")
            print(f"Status: {status}")
            
            # Get authorization header
            for header in request.get('headers', []):
                if header.get('name', '').lower() == 'authorization':
                    auth = header.get('value', '')
                    print(f"Auth: Bearer {auth.split('Bearer ')[-1][:30]}...")
                    break
            
            # Check for URL parameters
            if '?' in url:
                query_part = url.split('?', 1)[1]
                print(f"URL Query: {query_part}")
            
            # Analyze POST data
            post_data = request.get('postData', {})
            if post_data:
                mime_type = post_data.get('mimeType', '')
                print(f"Content-Type: {mime_type}")
                
                if mime_type == 'application/x-www-form-urlencoded':
                    if 'params' in post_data:
                        params = post_data['params']
                        print(f"Form Parameters ({len(params)}):")
                        for param in params:
                            name = param.get('name', '')
                            value = param.get('value', '')
                            print(f"  {name}: {value}")
                        
                        # Debug: print raw params structure
                        if len(params) == 0:
                            print(f"  DEBUG: params structure = {params}")
                    else:
                        print("No params found in form data")
                
                elif 'text' in post_data:
                    text_data = post_data['text']
                    if text_data:
                        print(f"Body: {text_data}")
                    else:
                        print("Body: [EMPTY]")
                
                # Print all keys in post_data for debugging
                print(f"PostData keys: {list(post_data.keys())}")
            
            print()

if __name__ == "__main__":
    analyze_event_manipulation()
