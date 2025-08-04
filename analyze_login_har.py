#!/usr/bin/env python3
import json

with open('charles_session.chls/Newest_clubhub_scrape.har', 'r', encoding='utf-8') as f:
    har = json.load(f)
    
entries = har['log']['entries']
print('=== LOOKING FOR CLUBHUB LOGIN AND AUTH DATA ===')
for i, entry in enumerate(entries):
    request = entry.get('request', {})
    response = entry.get('response', {})
    url = request.get('url', '')
    method = request.get('method', '')
    
    # Look for ClubHub API login/auth patterns
    if (method == 'POST' and ('clubhub' in url.lower() or 'anytimefitness.com' in url) and 
        ('/login' in url or '/auth' in url or '/api/v1.0' in url)):
        print(f'ClubHub AUTH request {i}:')
        print(f'  URL: {url}')
        print(f'  Method: {method}')
        
        # Print request headers
        headers = request.get('headers', [])
        print(f'  Request Headers:')
        for header in headers:
            name = header.get('name', '')
            value = header.get('value', '')
            if 'authorization' in name.lower() or 'bearer' in value.lower():
                print(f'    {name}: {value}')
            elif name.lower() in ['user-agent', 'api-version', 'accept', 'content-type']:
                print(f'    {name}: {value}')
        
        # Check form data
        post_data = request.get('postData', {})
        if post_data:
            print(f'  Post Data:')
            mime_type = post_data.get('mimeType', '')
            print(f'    mimeType: {mime_type}')
            text_data = post_data.get('text', '')
            print(f'    text: {text_data}')
            
            # Check if there are params
            params = post_data.get('params', [])
            if params:
                print(f'  Form Parameters:')
                for param in params:
                    name = param.get('name', '')
                    value = param.get('value', '')
                    if 'password' in name.lower():
                        value = '***HIDDEN***'
                    print(f'    {name}: {value}')
        
        print(f'  Response Status: {response.get("status", "")}')
        
        # Check response for bearer tokens
        response_headers = response.get('headers', [])
        print(f'  Response Headers:')
        for header in response_headers:
            name = header.get('name', '')
            value = header.get('value', '')
            if 'authorization' in name.lower() or 'token' in name.lower():
                print(f'    {name}: {value}')
        
        # Check response body for tokens
        content = response.get('content', {})
        response_text = content.get('text', '')
        if response_text and ('token' in response_text.lower() or 'bearer' in response_text.lower()):
            print(f'  Response Body (contains token):')
            print(f'    {response_text[:500]}...')
        
        print('---')

# Also look for any successful API calls with Bearer tokens
print('\n=== LOOKING FOR BEARER TOKEN USAGE ===')
for i, entry in enumerate(entries):
    request = entry.get('request', {})
    url = request.get('url', '')
    
    if 'clubhub' in url.lower() or 'anytimefitness.com' in url:
        headers = request.get('headers', [])
        for header in headers:
            if header.get('name', '').lower() == 'authorization' and 'bearer' in header.get('value', '').lower():
                print(f'Request {i} using Bearer token:')
                print(f'  URL: {url}')
                print(f'  Authorization: {header.get("value", "")}')
                print('---')
                break
