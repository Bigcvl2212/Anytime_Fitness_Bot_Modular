#!/usr/bin/env python3
"""
Charles Session Token Extractor
Extracts ClubHub authentication tokens from Charles Proxy session files
"""

import zipfile
import json
import re
from pathlib import Path
import sys
import os

def extract_clubhub_tokens():
    """Extract ClubHub tokens from Charles session"""
    
    session_file = Path("charles_session.chls/charles_session.chlz")
    
    if not session_file.exists():
        print(f"❌ Session file not found: {session_file}")
        return None
    
    print(f"📁 Analyzing Charles session: {session_file}")
    print(f"   File size: {session_file.stat().st_size / 1024:.1f} KB")
    
    tokens = {
        "bearer_token": None,
        "session_cookie": None,
        "authorization_header": None,
        "login_requests": [],
        "api_requests": []
    }
    
    try:
        with zipfile.ZipFile(session_file, 'r') as zip_file:
            json_files = [name for name in zip_file.namelist() if name.endswith('.json')]
            print(f"   Found {len(json_files)} JSON files to analyze")
            
            for i, json_file in enumerate(json_files):
                if i % 100 == 0:
                    print(f"   Processing file {i}/{len(json_files)}...")
                
                try:
                    with zip_file.open(json_file) as f:
                        data = json.load(f)
                    
                    # Check if this is a request/response structure
                    if isinstance(data, dict) and 'request' in data:
                        request = data['request']
                        url = request.get('url', '')
                        
                        # Look for ClubHub requests
                        if 'clubhub' in url.lower() or 'anytimefitness.com' in url.lower():
                            
                            # Check for login endpoint
                            if '/login' in url or '/api/login' in url:
                                print(f"🎯 Found login request: {url}")
                                tokens['login_requests'].append({
                                    'url': url,
                                    'method': request.get('method', ''),
                                    'file': json_file
                                })
                                
                                # Extract request body (credentials)
                                if 'postData' in request:
                                    post_data = request['postData'].get('text', '')
                                    if post_data:
                                        try:
                                            body = json.loads(post_data)
                                            print(f"   📧 Email: {body.get('email', 'N/A')}")
                                            print(f"   🔐 Password: {'*' * len(body.get('password', ''))}")
                                        except:
                                            print(f"   📄 Body: {post_data[:100]}...")
                            
                            # Check response for tokens
                            if 'response' in data:
                                response = data['response']
                                
                                # Check response headers for auth tokens
                                for header in response.get('headers', []):
                                    if isinstance(header, dict):
                                        name = header.get('name', '').lower()
                                        value = header.get('value', '')
                                        
                                        if name == 'authorization' and 'bearer' in value.lower():
                                            print(f"🔑 Found bearer token in response!")
                                            tokens['bearer_token'] = value.split(' ')[-1]
                                            tokens['authorization_header'] = value
                                        
                                        elif name == 'set-cookie' and 'incap_ses' in value:
                                            print(f"🍪 Found session cookie!")
                                            match = re.search(r'incap_ses_\d+_\d+=([^;]+)', value)
                                            if match:
                                                tokens['session_cookie'] = match.group(1)
                                
                                # Check response body for tokens
                                if 'content' in response and 'text' in response['content']:
                                    try:
                                        response_body = json.loads(response['content']['text'])
                                        if isinstance(response_body, dict) and 'token' in response_body:
                                            print(f"🎫 Found token in response body!")
                                            tokens['bearer_token'] = response_body['token']
                                    except:
                                        pass
                            
                            # Store API request info
                            tokens['api_requests'].append({
                                'url': url,
                                'method': request.get('method', ''),
                                'file': json_file
                            })
                
                except Exception as e:
                    # Skip corrupted files
                    continue
    
    except Exception as e:
        print(f"❌ Error processing session file: {e}")
        return None
    
    return tokens

def save_tokens(tokens):
    """Save extracted tokens to file"""
    if not tokens:
        return
    
    # Save to JSON file
    output_file = "data/clubhub_extracted_tokens.json"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(tokens, f, indent=2)
    
    print(f"💾 Tokens saved to: {output_file}")

def main():
    print("🔍 ClubHub Token Extractor")
    print("=" * 50)
    
    tokens = extract_clubhub_tokens()
    
    if tokens:
        print("\n📋 EXTRACTION RESULTS:")
        print(f"   🔑 Bearer Token: {'✅' if tokens['bearer_token'] else '❌'}")
        print(f"   🍪 Session Cookie: {'✅' if tokens['session_cookie'] else '❌'}")
        print(f"   📝 Login Requests: {len(tokens['login_requests'])}")
        print(f"   🌐 API Requests: {len(tokens['api_requests'])}")
        
        if tokens['bearer_token']:
            print(f"\n🎫 Bearer Token: {tokens['bearer_token'][:30]}...")
        
        if tokens['session_cookie']:
            print(f"🍪 Session Cookie: {tokens['session_cookie'][:30]}...")
        
        save_tokens(tokens)
        
        # Test the token
        if tokens['bearer_token']:
            print("\n🧪 Testing extracted token...")
            test_token(tokens['bearer_token'])
    
    else:
        print("❌ No tokens extracted")

def test_token(bearer_token):
    """Test the extracted bearer token"""
    try:
        import requests
        
        url = "https://clubhub-ios-api.anytimefitness.com/api/clubs/1156/members"
        headers = {
            'Authorization': f'Bearer {bearer_token}',
            'Accept': 'application/json',
            'API-version': '1'
        }
        
        response = requests.get(url, headers=headers, params={'page': 1, 'pageSize': 1}, timeout=10)
        
        if response.status_code == 200:
            print("✅ Token is valid! API access confirmed.")
        elif response.status_code == 401:
            print("❌ Token is expired or invalid")
        else:
            print(f"⚠️ Unexpected response: {response.status_code}")
            
    except Exception as e:
        print(f"⚠️ Error testing token: {e}")

if __name__ == "__main__":
    main()
