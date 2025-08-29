#!/usr/bin/env python3
"""
Check all HAR files for prospects data to find the one with 9000+ prospects
"""

import json
import os
import base64

def check_all_har_files():
    # Check all HAR files for prospects data
    har_files = [
        'charles_session.chls/newest.har',
        'charles_session.chls/newest_!.har', 
        'charles_session.chls/new_club_session.har',
        'charles_session.chls/Charles_session_mapping.har'
    ]

    for har_file in har_files:
        if os.path.exists(har_file):
            print(f'\n🔍 Checking {har_file}...')
            try:
                with open(har_file, 'r', encoding='utf-8') as f:
                    har_data = json.load(f)
                
                entries = har_data['log']['entries']
                prospects_calls = []
                
                for entry in entries:
                    request = entry['request']
                    url = request['url']
                    if 'prospects' in url.lower():
                        response = entry['response']
                        prospects_calls.append({
                            'url': url,
                            'method': request['method'],
                            'status': response['status'],
                            'queryString': request.get('queryString', []),
                            'response_size': response.get('bodySize', 0),
                            'content': response.get('content', {})
                        })
                
                print(f'📊 Total entries: {len(entries)}')
                print(f'🎯 Prospects calls: {len(prospects_calls)}')
                
                for call in prospects_calls:
                    params = [f'{p["name"]}={p["value"]}' for p in call['queryString']]
                    params_str = '?' + '&'.join(params) if params else ''
                    print(f'  {call["method"]} {call["status"]} {call["response_size"]}b: {call["url"]}{params_str}')
                    
                    # Try to get response count
                    content = call.get('content', {})
                    if content.get('text'):
                        try:
                            if content.get('encoding') == 'base64':
                                decoded = base64.b64decode(content['text']).decode('utf-8')
                                data = json.loads(decoded)
                            else:
                                data = json.loads(content['text'])
                            
                            if isinstance(data, list):
                                print(f'    → RESPONSE: {len(data)} prospects in direct list 🎯')
                                if len(data) > 100:  # Found a big one!
                                    print(f'    🚀 JACKPOT! This has {len(data)} prospects!')
                                    # Show first prospect structure
                                    if data:
                                        print(f'    📋 First prospect keys: {list(data[0].keys())}')
                            elif isinstance(data, dict):
                                if 'prospects' in data:
                                    count = len(data['prospects'])
                                    print(f'    → RESPONSE: {count} prospects in dict 🎯')
                                    if count > 100:
                                        print(f'    🚀 JACKPOT! This has {count} prospects!')
                                else:
                                    for key in data:
                                        if isinstance(data[key], list):
                                            print(f'    → RESPONSE: {len(data[key])} items in "{key}"')
                        except Exception as e:
                            print(f'    ❌ Could not parse response: {e}')
                            
            except Exception as e:
                print(f'❌ Error reading {har_file}: {e}')
        else:
            print(f'❌ File not found: {har_file}')

if __name__ == "__main__":
    check_all_har_files()
