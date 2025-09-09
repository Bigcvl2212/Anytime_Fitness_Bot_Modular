#!/usr/bin/env python3
"""
Extract EXACT form data from successful HAR messaging requests
"""

import json
from urllib.parse import unquote

def extract_form_data_from_har():
    """Extract form data from HAR file"""
    har_file = "c:\\Users\\mayoj\\OneDrive\\Documents\\Gym-Bot\\gym-bot\\gym-bot-modular\\charles_session.chls\\Clubos_Newest_Message.har"
    
    with open(har_file, 'r', encoding='utf-8') as f:
        har_data = json.load(f)
    
    entries = har_data.get('log', {}).get('entries', [])
    
    print("🔍 EXTRACTING EXACT FORM DATA FROM SUCCESSFUL MESSAGING REQUESTS")
    print("=" * 70)
    
    for i, entry in enumerate(entries):
        request = entry.get('request', {})
        response = entry.get('response', {})
        url = request.get('url', '')
        method = request.get('method', '')
        status = response.get('status', 0)
        
        # Look for successful FollowUp/save requests
        if (method == 'POST' and 
            'FollowUp/save' in url and 
            status == 200):
            
            # Check if response indicates success
            response_content = response.get('content', {}).get('text', '')
            if 'texted' in response_content.lower():
                print(f"\n✅ SUCCESSFUL MESSAGE #{i+1}")
                print(f"   URL: {url}")
                print(f"   Status: {status}")
                print(f"   Response: {response_content[:100]}...")
                
                # Extract form data
                post_data = request.get('postData', {})
                if post_data:
                    # Try to get form parameters from params array
                    params = post_data.get('params', [])
                    if params:
                        print(f"\\n   📋 FORM PARAMETERS ({len(params)}):")
                        form_dict = {}
                        for param in params:
                            name = param.get('name', '')
                            value = param.get('value', '')
                            form_dict[name] = value
                            print(f"      {name}: {value}")
                        
                        print("\\n   🐍 PYTHON DICT FORMAT:")
                        print("   form_data = {")
                        for name, value in form_dict.items():
                            print(f'      "{name}": "{value}",')
                        print("   }")
                        
                    # Also try to parse raw text
                    text = post_data.get('text', '')
                    if text and not params:
                        print(f"\\n   📄 RAW FORM DATA:")
                        print(f"      {text[:200]}...")
                        
                        # Parse URL-encoded data
                        try:
                            pairs = text.split('&')
                            form_dict = {}
                            for pair in pairs:
                                if '=' in pair:
                                    key, value = pair.split('=', 1)
                                    form_dict[unquote(key)] = unquote(value)
                            
                            print(f"\\n   📋 PARSED FORM PARAMETERS ({len(form_dict)}):")
                            for key, value in form_dict.items():
                                print(f"      {key}: {value}")
                        except Exception as e:
                            print(f"      ⚠️ Error parsing: {e}")

if __name__ == "__main__":
    extract_form_data_from_har()
