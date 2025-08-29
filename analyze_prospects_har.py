#!/usr/bin/env python3
"""
Analyze ClubHub HAR file to find the EXACT working prospects API call
"""

import json
import base64

def analyze_prospects_har():
    """Find the exact working prospects API call from HAR file"""
    
    har_file = 'charles_session.chls/Newest_clubhub_scrape.har'
    print(f'🔍 Analyzing {har_file} for prospects API calls...')
    
    try:
        with open(har_file, 'r', encoding='utf-8') as f:
            har_data = json.load(f)
        
        entries = har_data['log']['entries']
        print(f'📊 Total requests found: {len(entries)}')
        
        prospects_calls = []
        
        for entry in entries:
            request = entry['request']
            response = entry['response']
            url = request['url']
            method = request['method']
            status = response['status']
            
            # Look for prospects API calls
            if 'prospects' in url.lower():
                prospects_calls.append({
                    'url': url,
                    'method': method,
                    'status': status,
                    'headers': {h['name']: h['value'] for h in request.get('headers', [])},
                    'queryString': request.get('queryString', []),
                    'response_size': response.get('bodySize', 0),
                    'content': response.get('content', {})
                })
        
        print(f'🎯 Found {len(prospects_calls)} prospects API calls:')
        
        for i, call in enumerate(prospects_calls, 1):
            print(f'\n=== PROSPECTS CALL #{i} ===')
            print(f'URL: {call["url"]}')
            print(f'Method: {call["method"]} -> Status: {call["status"]}')
            print(f'Response Size: {call["response_size"]} bytes')
            
            # Print query parameters
            if call["queryString"]:
                print(f'Query Parameters:')
                for param in call["queryString"]:
                    print(f'  {param["name"]}: {param["value"]}')
            
            # Print important headers
            headers = call["headers"]
            important_headers = ['Authorization', 'Cookie', 'User-Agent', 'API-version']
            for header in important_headers:
                if header in headers:
                    value = headers[header]
                    if len(value) > 100:
                        value = value[:100] + '...'
                    print(f'{header}: {value}')
            
            # Try to analyze response
            content = call["content"]
            if content.get('text'):
                try:
                    if content.get('encoding') == 'base64':
                        decoded = base64.b64decode(content['text']).decode('utf-8')
                        data = json.loads(decoded)
                    else:
                        data = json.loads(content['text'])
                    
                    if isinstance(data, list):
                        print(f'✅ RESPONSE: Direct list with {len(data)} prospects')
                        if data:
                            print(f'First prospect keys: {list(data[0].keys())}')
                    elif isinstance(data, dict):
                        if 'prospects' in data:
                            prospects = data['prospects']
                            print(f'✅ RESPONSE: Dict with {len(prospects)} prospects in "prospects" key')
                        else:
                            print(f'✅ RESPONSE: Dict with keys: {list(data.keys())}')
                            for key in data.keys():
                                if isinstance(data[key], list):
                                    print(f'  {key}: {len(data[key])} items')
                    else:
                        print(f'✅ RESPONSE: {type(data)} - {str(data)[:200]}...')
                        
                except Exception as e:
                    print(f'❌ Could not parse response: {e}')
    
    except Exception as e:
        print(f'❌ Error analyzing HAR file: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_prospects_har()
