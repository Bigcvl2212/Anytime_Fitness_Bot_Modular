#!/usr/bin/env python3
"""
Extract fresh ClubHub auth token from HAR file
"""

import json
import re

def extract_fresh_token():
    """Extract the most recent auth token from the ClubHub HAR file"""
    
    har_file = "charles_session.chls/Newest_clubhub_scrape.har"
    
    try:
        with open(har_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("🔍 Parsing ClubHub HAR file for auth tokens...")
        
        # Parse the HAR file
        har_data = json.loads(content)
        entries = har_data['log']['entries']
        
        # Look for the most recent Authorization header
        auth_tokens = []
        
        for entry in entries:
            request = entry.get('request', {})
            headers = request.get('headers', [])
            
            for header in headers:
                if header.get('name') == 'Authorization':
                    token = header.get('value', '')
                    if token.startswith('Bearer '):
                        # Extract just the token part
                        token_value = token.replace('Bearer ', '')
                        auth_tokens.append({
                            'token': token_value,
                            'url': request.get('url', ''),
                            'method': request.get('method', ''),
                            'timestamp': entry.get('startedDateTime', '')
                        })
        
        if auth_tokens:
            # Get the most recent token (last in the list)
            latest_token = auth_tokens[-1]
            print(f"✅ Found {len(auth_tokens)} auth tokens")
            print(f"🎯 Latest token from: {latest_token['method']} {latest_token['url']}")
            print(f"📅 Timestamp: {latest_token['timestamp']}")
            
            return latest_token['token']
        else:
            print("❌ No auth tokens found in HAR file")
            return None
            
    except Exception as e:
        print(f"❌ Error parsing HAR file: {e}")
        return None

def update_constants_with_fresh_token():
    """Update the constants file with the fresh token"""
    
    token = extract_fresh_token()
    if not token:
        print("❌ Could not extract fresh token")
        return False
    
    print(f"\n🔑 Fresh token extracted: {token[:50]}...")
    
    # Read the constants file
    constants_file = "config/constants.py"
    try:
        with open(constants_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find and replace the Authorization header
        old_pattern = r'("Authorization": "Bearer )[^"]+(")'
        new_auth_header = f'"Authorization": "Bearer {token}"'
        
        if re.search(old_pattern, content):
            new_content = re.sub(old_pattern, f'\\1{token}\\2', content)
            
            # Write back to file
            with open(constants_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print("✅ Updated constants.py with fresh token")
            return True
        else:
            print("❌ Could not find Authorization header in constants.py")
            return False
            
    except Exception as e:
        print(f"❌ Error updating constants file: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Extracting fresh ClubHub auth token...")
    
    if update_constants_with_fresh_token():
        print("\n✅ Successfully updated auth token!")
        print("🔄 You can now run the ClubHub data fetch script again.")
    else:
        print("\n❌ Failed to update auth token") 