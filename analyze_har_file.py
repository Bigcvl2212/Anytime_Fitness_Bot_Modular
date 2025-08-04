#!/usr/bin/env python3
"""
Analyze the ClubOS HAR file to extract the exact working sequence
"""

import json
import base64
from datetime import datetime

def analyze_har_file(har_path):
    """Analyze the HAR file to understand the exact working sequence"""
    
    print("=== ANALYZING CLUBOS HAR FILE ===")
    
    with open(har_path, 'r', encoding='utf-8') as f:
        har_data = json.load(f)
    
    entries = har_data['log']['entries']
    print(f"Total requests found: {len(entries)}")
    
    # Extract key information
    auth_requests = []
    calendar_requests = []
    api_requests = []
    tokens = {}
    cookies = {}
    
    for entry in entries:
        request = entry['request']
        response = entry['response']
        url = request['url']
        method = request['method']
        status = response['status']
        
        # Extract cookies
        for cookie in request.get('cookies', []):
            cookies[cookie['name']] = cookie['value']
        
        # Extract headers
        headers = {h['name']: h['value'] for h in request.get('headers', [])}
        
        # Extract authorization tokens
        if 'Authorization' in headers:
            auth_header = headers['Authorization']
            if auth_header.startswith('Bearer '):
                tokens['bearer_token'] = auth_header[7:]
        
        # Categorize requests
        if any(keyword in url.lower() for keyword in ['login', 'auth', 'signin']):
            auth_requests.append({
                'url': url,
                'method': method,
                'status': status,
                'headers': headers,
                'cookies': request.get('cookies', [])
            })
        
        elif 'calendar' in url.lower():
            calendar_requests.append({
                'url': url,
                'method': method,
                'status': status,
                'headers': headers,
                'response_size': response.get('bodySize', 0)
            })
        
        elif '/api/' in url:
            api_requests.append({
                'url': url,
                'method': method,
                'status': status,
                'headers': headers,
                'response': response
            })
    
    print(f"\n=== AUTHENTICATION REQUESTS ({len(auth_requests)}) ===")
    for req in auth_requests:
        print(f"{req['method']} {req['url']} -> {req['status']}")
    
    print(f"\n=== CALENDAR REQUESTS ({len(calendar_requests)}) ===")
    for req in calendar_requests:
        print(f"{req['method']} {req['url']} -> {req['status']}")
    
    print(f"\n=== API REQUESTS ({len(api_requests)}) ===")
    for req in api_requests:
        print(f"{req['method']} {req['url']} -> {req['status']}")
        
        # Look for calendar events API
        if 'calendar/events' in req['url']:
            print(f"  *** CALENDAR EVENTS API FOUND ***")
            print(f"  Headers: {req['headers']}")
            
            # Check response
            if req['response'].get('content'):
                content = req['response']['content']
                if content.get('text'):
                    try:
                        # Try to decode if base64
                        if content.get('encoding') == 'base64':
                            decoded = base64.b64decode(content['text']).decode('utf-8')
                            data = json.loads(decoded)
                            print(f"  Response: {len(data.get('events', []))} events found")
                        else:
                            data = json.loads(content['text'])
                            print(f"  Response: {len(data.get('events', []))} events found")
                    except:
                        print(f"  Response size: {len(content.get('text', ''))}")
    
    print(f"\n=== KEY TOKENS ===")
    for key, value in tokens.items():
        print(f"{key}: {value[:50]}...")
    
    print(f"\n=== KEY COOKIES ===")
    important_cookies = ['JSESSIONID', 'loggedInUserId', 'delegatedUserId', 'apiV3AccessToken']
    for cookie_name in important_cookies:
        if cookie_name in cookies:
            print(f"{cookie_name}: {cookies[cookie_name]}")
    
    return {
        'auth_requests': auth_requests,
        'calendar_requests': calendar_requests,
        'api_requests': api_requests,
        'tokens': tokens,
        'cookies': cookies
    }

def extract_working_sequence(analysis):
    """Extract the exact working sequence from HAR analysis"""
    
    print(f"\n=== EXTRACTING WORKING SEQUENCE ===")
    
    # Find the successful calendar events API call
    successful_api_call = None
    
    # Check both api_requests and calendar_requests for calendar/events calls
    all_requests = analysis['api_requests'] + analysis['calendar_requests']
    
    for req in all_requests:
        if 'calendar/events' in req['url'] and req['status'] == 200:
            successful_api_call = req
            break
    
    if successful_api_call:
        print(f"Found successful calendar API call:")
        print(f"URL: {successful_api_call['url']}")
        print(f"Method: {successful_api_call['method']}")
        print(f"Headers:")
        for name, value in successful_api_call['headers'].items():
            if name.lower() in ['authorization', 'cookie', 'referer', 'user-agent']:
                print(f"  {name}: {value[:100]}...")
        
        return successful_api_call
    
    return None

if __name__ == "__main__":
    har_file = "charles_session.chls/clubos_calendar_flow.har"
    
    try:
        analysis = analyze_har_file(har_file)
        working_sequence = extract_working_sequence(analysis)
        
        if working_sequence:
            print(f"\n*** SUCCESS: Found working API sequence! ***")
        else:
            print(f"\n*** No successful calendar API calls found ***")
            
    except Exception as e:
        print(f"Error analyzing HAR file: {e}")
