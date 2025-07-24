#!/usr/bin/env python3
"""
HAR File Token Extractor
Extracts ClubHub authentication tokens from HAR files
"""

import json
import re
from pathlib import Path
import os

def extract_from_har_file(har_file_path):
    """Extract tokens from a single HAR file"""
    
    print(f"📁 Analyzing HAR file: {har_file_path}")
    
    tokens = {
        "bearer_token": None,
        "session_cookie": None,
        "authorization_header": None,
        "login_requests": [],
        "api_requests": []
    }
    
    try:
        file_size = os.path.getsize(har_file_path)
        if file_size > 50 * 1024 * 1024:  # 50MB
            print(f"⚠️ File too large ({file_size / 1024 / 1024:.1f} MB), sampling first 10MB...")
            
            # Read first 10MB for large files
            with open(har_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(10 * 1024 * 1024)
        else:
            with open(har_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        
        # Try to parse as JSON
        try:
            har_data = json.loads(content)
        except json.JSONDecodeError:
            # If full parse fails, try to find JSON objects in the content
            print("   Searching for ClubHub requests in raw content...")
            
            # Look for ClubHub URLs
            clubhub_matches = re.findall(r'https://[^"]*clubhub[^"]*', content, re.IGNORECASE)
            if clubhub_matches:
                print(f"   Found {len(clubhub_matches)} ClubHub URLs:")
                for url in set(clubhub_matches[:10]):  # Show unique URLs, max 10
                    print(f"     {url}")
            
            # Look for bearer tokens
            bearer_matches = re.findall(r'Bearer\s+([A-Za-z0-9\-._~+/=]+)', content)
            if bearer_matches:
                print(f"   Found {len(bearer_matches)} Bearer tokens:")
                for token in set(bearer_matches[:3]):  # Show first 3 unique tokens
                    print(f"     Bearer {token[:30]}...")
                    tokens['bearer_token'] = bearer_matches[0]  # Use first token
            
            # Look for login endpoints
            login_matches = re.findall(r'https://[^"]*(?:login|auth)[^"]*', content, re.IGNORECASE)
            if login_matches:
                print(f"   Found {len(login_matches)} login endpoints:")
                for url in set(login_matches[:5]):
                    print(f"     {url}")
            
            return tokens
        
        # Parse HAR structure
        if isinstance(har_data, dict) and 'log' in har_data:
            entries = har_data['log'].get('entries', [])
            print(f"   Found {len(entries)} HTTP entries")
            
            for entry in entries:
                request = entry.get('request', {})
                response = entry.get('response', {})
                url = request.get('url', '')
                
                # Look for ClubHub requests
                if 'clubhub' in url.lower() or 'anytimefitness.com' in url.lower():
                    print(f"🎯 ClubHub request: {request.get('method', '')} {url}")
                    
                    # Check for login endpoint
                    if '/login' in url or '/api/login' in url:
                        print(f"   🚪 LOGIN ENDPOINT FOUND!")
                        tokens['login_requests'].append({
                            'url': url,
                            'method': request.get('method', '')
                        })
                        
                        # Extract credentials from request
                        if 'postData' in request:
                            post_data = request['postData'].get('text', '')
                            if post_data:
                                try:
                                    body = json.loads(post_data)
                                    print(f"       📧 Email: {body.get('email', 'N/A')}")
                                    print(f"       🔐 Password: {'*' * len(body.get('password', ''))}")
                                except:
                                    print(f"       📄 Body: {post_data[:100]}...")
                        
                        # Check response for tokens
                        if 'content' in response and 'text' in response['content']:
                            try:
                                response_body = json.loads(response['content']['text'])
                                if isinstance(response_body, dict) and 'token' in response_body:
                                    print(f"       🎫 TOKEN FOUND in response!")
                                    tokens['bearer_token'] = response_body['token']
                                    print(f"       🔑 Bearer: {tokens['bearer_token'][:30]}...")
                            except:
                                pass
                    
                    # Check request headers for existing auth
                    for header in request.get('headers', []):
                        if isinstance(header, dict):
                            name = header.get('name', '').lower()
                            value = header.get('value', '')
                            
                            if name == 'authorization' and 'bearer' in value.lower():
                                print(f"       🔑 Auth header: {value[:50]}...")
                                if not tokens['bearer_token']:
                                    tokens['bearer_token'] = value.split(' ')[-1]
                                    tokens['authorization_header'] = value
                    
                    # Check response headers for cookies
                    for header in response.get('headers', []):
                        if isinstance(header, dict):
                            name = header.get('name', '').lower()
                            value = header.get('value', '')
                            
                            if name == 'set-cookie' and 'incap_ses' in value:
                                print(f"       🍪 Session cookie found!")
                                match = re.search(r'incap_ses_\d+_\d+=([^;]+)', value)
                                if match:
                                    tokens['session_cookie'] = match.group(1)
                    
                    # Store API request
                    tokens['api_requests'].append({
                        'url': url,
                        'method': request.get('method', '')
                    })
    
    except Exception as e:
        print(f"❌ Error processing HAR file: {e}")
        return None
    
    return tokens

def main():
    print("🔍 HAR File ClubHub Token Extractor")
    print("=" * 50)
    
    # Check available HAR files
    har_directory = Path("charles_session.chls")
    har_files = list(har_directory.glob("*.har"))
    
    print(f"📁 Found {len(har_files)} HAR files:")
    for har_file in har_files:
        file_size = har_file.stat().st_size / 1024 / 1024  # MB
        print(f"   {har_file.name} ({file_size:.1f} MB)")
    
    # Prioritize files that likely contain login flows
    priority_files = [
        "Newest_clubhub_scrape.har",
        "newest.har", 
        "newest_!.har",
        "new_club_session.har",
        "Charles_session_mapping.har"
    ]
    
    all_tokens = {}
    
    for priority_file in priority_files:
        har_file = har_directory / priority_file
        if har_file.exists():
            print(f"\n🎯 Processing priority file: {priority_file}")
            tokens = extract_from_har_file(har_file)
            
            if tokens and (tokens['bearer_token'] or tokens['login_requests']):
                all_tokens[priority_file] = tokens
                
                if tokens['bearer_token']:
                    print(f"✅ Found bearer token in {priority_file}!")
                    break  # Stop if we found a token
    
    # Save results
    if all_tokens:
        output_file = "data/clubhub_har_tokens.json"
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(all_tokens, f, indent=2)
        
        print(f"\n💾 Results saved to: {output_file}")
        
        # Test any found tokens
        for file_name, tokens in all_tokens.items():
            if tokens['bearer_token']:
                print(f"\n🧪 Testing token from {file_name}...")
                test_token(tokens['bearer_token'])
    else:
        print("\n❌ No tokens found in HAR files")

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
            return True
        elif response.status_code == 401:
            print("❌ Token is expired or invalid")
        else:
            print(f"⚠️ Unexpected response: {response.status_code}")
            
    except Exception as e:
        print(f"⚠️ Error testing token: {e}")
    
    return False

if __name__ == "__main__":
    main()
