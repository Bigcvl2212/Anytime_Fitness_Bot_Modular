#!/usr/bin/env python3
"""
Find any API calls in HAR files that return large datasets (looking for the 9000+ prospects)
"""

import json
import os
import base64

def analyze_large_responses():
    """Look for any API calls with large response datasets"""
    har_files = [
        'charles_session.chls/newest.har',
        'charles_session.chls/newest_!.har', 
        'charles_session.chls/new_club_session.har',
        'charles_session.chls/Charles_session_mapping.har'
    ]

    for har_file in har_files:
        if os.path.exists(har_file):
            print(f'\n🔍 Analyzing {har_file}...')
            try:
                with open(har_file, 'r', encoding='utf-8') as f:
                    har_data = json.load(f)
                
                entries = har_data['log']['entries']
                large_responses = []
                
                for entry in entries:
                    request = entry['request']
                    response = entry['response']
                    url = request['url']
                    
                    # Look for API calls to ClubHub
                    if 'clubhub' in url.lower() or 'anytimefitness.com' in url.lower():
                        body_size = response.get('bodySize', 0)
                        content = response.get('content', {})
                        
                        # Check if response might contain large dataset
                        if body_size > 10000 or (content.get('text') and len(content.get('text', '')) > 10000):
                            large_responses.append({
                                'url': url,
                                'method': request['method'],
                                'status': response['status'],
                                'bodySize': body_size,
                                'content': content,
                                'queryString': request.get('queryString', [])
                            })
                
                print(f'📊 Total entries: {len(entries)}')
                print(f'🎯 Large ClubHub responses: {len(large_responses)}')
                
                for resp in large_responses:
                    params = [f'{p["name"]}={p["value"]}' for p in resp['queryString']]
                    params_str = '?' + '&'.join(params) if params else ''
                    print(f'  {resp["method"]} {resp["status"]} {resp["bodySize"]}b: {resp["url"]}{params_str}')
                    
                    # Try to analyze the response content
                    content = resp.get('content', {})
                    if content.get('text'):
                        try:
                            if content.get('encoding') == 'base64':
                                decoded = base64.b64decode(content['text']).decode('utf-8')
                                data = json.loads(decoded)
                            else:
                                data = json.loads(content['text'])
                            
                            # Look for any arrays with lots of items
                            if isinstance(data, list):
                                print(f'    → DIRECT ARRAY: {len(data)} items 🎯')
                                if len(data) > 1000:
                                    print(f'    🚀 HUGE DATASET! {len(data)} items!')
                                    if data:
                                        print(f'    📋 First item keys: {list(data[0].keys()) if isinstance(data[0], dict) else "Not a dict"}')
                                        
                            elif isinstance(data, dict):
                                for key, value in data.items():
                                    if isinstance(value, list) and len(value) > 50:
                                        print(f'    → ARRAY "{key}": {len(value)} items 🎯')
                                        if len(value) > 1000:
                                            print(f'    🚀 HUGE DATASET in "{key}": {len(value)} items!')
                                            if value:
                                                print(f'    📋 First {key} keys: {list(value[0].keys()) if isinstance(value[0], dict) else "Not a dict"}')
                                    elif isinstance(value, dict):
                                        print(f'    → DICT "{key}": {len(value)} keys')
                                        
                        except Exception as e:
                            print(f'    ❌ Could not parse JSON response: {e}')
                            # Show raw text preview if it's not JSON
                            text = content.get('text', '')
                            if len(text) > 100:
                                print(f'    📄 Raw text preview: {text[:200]}...')
                            
            except Exception as e:
                print(f'❌ Error reading {har_file}: {e}')
        else:
            print(f'❌ File not found: {har_file}')

if __name__ == "__main__":
    analyze_large_responses()
