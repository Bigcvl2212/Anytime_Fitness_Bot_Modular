#!/usr/bin/env python3
"""
Find ONLY prospects API calls that return large datasets - looking for the 9000+ prospects
"""

import json
import os
import base64

def find_large_prospects_only():
    """Look specifically for prospects API calls with large response datasets"""
    har_files = [
        'charles_session.chls/newest.har',
        'charles_session.chls/newest_!.har', 
        'charles_session.chls/new_club_session.har',
        'charles_session.chls/Charles_session_mapping.har'
    ]

    for har_file in har_files:
        if os.path.exists(har_file):
            print(f'\n🎯 PROSPECTS ONLY: {har_file}...')
            try:
                with open(har_file, 'r', encoding='utf-8') as f:
                    har_data = json.load(f)
                
                entries = har_data['log']['entries']
                prospects_only = []
                
                for entry in entries:
                    request = entry['request']
                    response = entry['response']
                    url = request['url']
                    
                    # ONLY prospects endpoints
                    if 'prospects' in url.lower() and 'clubhub' in url.lower():
                        body_size = response.get('bodySize', 0)
                        content = response.get('content', {})
                        
                        prospects_only.append({
                            'url': url,
                            'method': request['method'],
                            'status': response['status'],
                            'bodySize': body_size,
                            'content': content,
                            'queryString': request.get('queryString', [])
                        })
                
                print(f'🎯 PROSPECTS API calls: {len(prospects_only)}')
                
                for call in prospects_only:
                    params = [f'{p["name"]}={p["value"]}' for p in call['queryString']]
                    params_str = '?' + '&'.join(params) if params else ''
                    print(f'  {call["method"]} {call["status"]} {call["bodySize"]}b: {call["url"]}{params_str}')
                    
                    # Try to analyze the response content for prospects count
                    content = call.get('content', {})
                    if content.get('text'):
                        try:
                            if content.get('encoding') == 'base64':
                                decoded = base64.b64decode(content['text']).decode('utf-8')
                                data = json.loads(decoded)
                            else:
                                data = json.loads(content['text'])
                            
                            # Check if it's a direct prospects array
                            if isinstance(data, list):
                                print(f'    → PROSPECTS ARRAY: {len(data)} prospects 🎯')
                                if len(data) > 1000:
                                    print(f'    🚀🚀🚀 HUGE PROSPECTS DATASET! {len(data)} prospects! 🚀🚀🚀')
                                    if data:
                                        print(f'    📋 First prospect structure: {list(data[0].keys()) if isinstance(data[0], dict) else "Not a dict"}')
                                        print(f'    📋 Sample prospect: {data[0] if isinstance(data[0], dict) else "Not a dict"}')
                                        
                            elif isinstance(data, dict):
                                # Check for prospects in dict
                                for key, value in data.items():
                                    if isinstance(value, list) and ('prospect' in key.lower() or key.lower() == 'data'):
                                        print(f'    → PROSPECTS in "{key}": {len(value)} prospects 🎯')
                                        if len(value) > 1000:
                                            print(f'    🚀🚀🚀 HUGE PROSPECTS in "{key}": {len(value)} prospects! 🚀🚀🚀')
                                            if value:
                                                print(f'    📋 First prospect structure: {list(value[0].keys()) if isinstance(value[0], dict) else "Not a dict"}')
                                                
                        except Exception as e:
                            print(f'    ❌ Could not parse prospects response: {e}')
                            # Show raw text preview if it's not JSON but might contain prospects data
                            text = content.get('text', '')
                            if len(text) > 1000 and 'prospect' in text.lower():
                                print(f'    📄 Large raw prospects text: {len(text)} characters')
                            
            except Exception as e:
                print(f'❌ Error reading {har_file}: {e}')
        else:
            print(f'❌ File not found: {har_file}')

if __name__ == "__main__":
    find_large_prospects_only()
