#!/usr/bin/env python3
"""
Analyze ALL ClubHub API calls to find large prospects datasets
"""

import json
import base64

def analyze_all_clubhub_calls():
    """Find all ClubHub API calls that might contain prospects"""
    
    har_file = 'charles_session.chls/Newest_clubhub_scrape.har'
    print('🔍 Looking for ALL ClubHub API calls that might contain prospects...')
    
    try:
        with open(har_file, 'r', encoding='utf-8') as f:
            har_data = json.load(f)
        
        entries = har_data['log']['entries']
        clubhub_calls = []
        
        for entry in entries:
            request = entry['request']
            response = entry['response']
            url = request['url']
            method = request['method']
            status = response['status']
            
            # Look for ALL ClubHub API calls
            if 'clubhub-ios-api.anytimefitness.com' in url and '/api/' in url:
                clubhub_calls.append({
                    'url': url,
                    'method': method,
                    'status': status,
                    'response_size': response.get('bodySize', 0),
                    'queryString': request.get('queryString', []),
                    'content': response.get('content', {})
                })
        
        print(f'📊 Found {len(clubhub_calls)} ClubHub API calls')
        
        # Group by endpoint type
        endpoints = {}
        for call in clubhub_calls:
            # Extract endpoint from URL
            parts = call['url'].split('/api/')
            if len(parts) > 1:
                endpoint = parts[1].split('?')[0]
                if endpoint not in endpoints:
                    endpoints[endpoint] = []
                endpoints[endpoint].append(call)
        
        for endpoint, calls in sorted(endpoints.items()):
            print(f'\n📍 ENDPOINT: {endpoint}')
            for call in calls:
                params_str = ''
                if call['queryString']:
                    params = []
                    for p in call['queryString']:
                        params.append(f'{p["name"]}={p["value"]}')
                    params_str = '?' + '&'.join(params)
                
                print(f'  {call["method"]} {call["status"]} {call["response_size"]}b {params_str}')
                
                # Check for large responses that might contain lots of data
                if call["response_size"] > 10000:
                    print(f'    🎯 LARGE RESPONSE! Analyzing...')
                    content = call["content"]
                    if content.get('text'):
                        try:
                            if content.get('encoding') == 'base64':
                                decoded = base64.b64decode(content['text']).decode('utf-8')
                                data = json.loads(decoded)
                            else:
                                data = json.loads(content['text'])
                            
                            if isinstance(data, list):
                                print(f'    📋 Direct list with {len(data)} items')
                                if data and isinstance(data[0], dict):
                                    keys = list(data[0].keys())
                                    if 'prospect' in str(keys).lower() or 'firstName' in keys or 'email' in keys:
                                        print(f'    🎯 LOOKS LIKE PROSPECTS DATA! Keys: {keys[:10]}')
                            elif isinstance(data, dict):
                                for key, value in data.items():
                                    if isinstance(value, list) and len(value) > 100:
                                        print(f'    📋 {key}: {len(value)} items')
                                        if value and isinstance(value[0], dict):
                                            item_keys = list(value[0].keys())
                                            if 'prospect' in str(item_keys).lower() or 'firstName' in item_keys:
                                                print(f'    🎯 FOUND LARGE PROSPECTS DATASET! Key: {key}, Count: {len(value)}')
                        except Exception as e:
                            print(f'    ❌ Could not parse large response: {e}')

    except Exception as e:
        print(f'❌ Error: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_all_clubhub_calls()
