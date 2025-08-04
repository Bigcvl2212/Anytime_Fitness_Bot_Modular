#!/usr/bin/env python3
"""
HAR Authentication Analyzer
Extracts exact authentication flow from HAR files
"""

import json
import re
import os
from pathlib import Path

def analyze_har_auth_flow(har_file_path):
    """Analyze HAR file to extract exact authentication flow"""
    
    print(f"🔍 Analyzing: {har_file_path}")
    
    try:
        file_size = os.path.getsize(har_file_path)
        print(f"   File size: {file_size / 1024 / 1024:.1f} MB")
        
        # For large files, search for login patterns first
        with open(har_file_path, 'r', encoding='utf-8', errors='ignore') as f:
            if file_size > 20 * 1024 * 1024:  # 20MB
                print("   Large file - searching for login patterns...")
                
                # Read in chunks and look for login patterns
                chunk_size = 1024 * 1024  # 1MB chunks
                login_found = False
                
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    
                    # Look for login endpoint
                    if '/api/login' in chunk or '/login' in chunk:
                        print("   ✅ Found login endpoint in chunk!")
                        login_found = True
                        
                        # Extract the surrounding context
                        login_pos = chunk.find('/api/login')
                        if login_pos == -1:
                            login_pos = chunk.find('/login')
                        
                        # Get context around login
                        start = max(0, login_pos - 2000)
                        end = min(len(chunk), login_pos + 2000)
                        context = chunk[start:end]
                        
                        # Find JSON structures around login
                        json_pattern = r'\{[^{}]*"(?:request|response)"[^{}]*\{[^{}]*"url"[^{}]*login[^{}]*\}[^{}]*\}'
                        matches = re.findall(json_pattern, context, re.IGNORECASE)
                        
                        for match in matches:
                            try:
                                # Try to parse as JSON
                                data = json.loads(match)
                                print_login_details(data)
                            except:
                                # If not valid JSON, look for key patterns
                                print("   Raw login context found:")
                                print(f"   {match[:500]}...")
                
                if not login_found:
                    print("   ❌ No login endpoint found in file")
                    
            else:
                # Small file - parse normally
                content = f.read()
                try:
                    har_data = json.loads(content)
                    analyze_har_entries(har_data)
                except json.JSONDecodeError:
                    print("   Not valid JSON, searching raw content...")
                    search_raw_content(content)
                    
    except Exception as e:
        print(f"   ❌ Error: {e}")

def analyze_har_entries(har_data):
    """Analyze HAR entries for login flow"""
    
    if 'log' not in har_data or 'entries' not in har_data['log']:
        print("   ❌ Invalid HAR structure")
        return
    
    entries = har_data['log']['entries']
    print(f"   Found {len(entries)} entries")
    
    login_entries = []
    
    for entry in entries:
        request = entry.get('request', {})
        url = request.get('url', '')
        
        if '/login' in url.lower() or '/auth' in url.lower():
            login_entries.append(entry)
    
    print(f"   Found {len(login_entries)} login-related entries")
    
    for entry in login_entries:
        print_login_details(entry)

def print_login_details(entry):
    """Print detailed login information"""
    
    request = entry.get('request', {})
    response = entry.get('response', {})
    
    print("\n🎯 LOGIN REQUEST FOUND:")
    print(f"   URL: {request.get('url', 'N/A')}")
    print(f"   Method: {request.get('method', 'N/A')}")
    
    # Print all headers
    print("   Headers:")
    for header in request.get('headers', []):
        if isinstance(header, dict):
            name = header.get('name', '')
            value = header.get('value', '')
            print(f"     {name}: {value}")
    
    # Print request body
    if 'postData' in request:
        post_data = request['postData']
        print(f"   Content-Type: {post_data.get('mimeType', 'N/A')}")
        print(f"   Body: {post_data.get('text', 'N/A')[:200]}...")
    
    # Print response
    print(f"   Response Status: {response.get('status', 'N/A')}")
    
    if 'content' in response and 'text' in response['content']:
        response_text = response['content']['text']
        print(f"   Response: {response_text[:200]}...")
        
        # Try to parse response as JSON for tokens
        try:
            response_json = json.loads(response_text)
            if 'token' in response_json:
                token = response_json['token']
                print(f"   🎫 TOKEN FOUND: {token[:50]}...")
        except:
            pass

def search_raw_content(content):
    """Search raw content for login patterns"""
    
    # Look for login URLs
    login_urls = re.findall(r'https://[^"]*login[^"]*', content, re.IGNORECASE)
    if login_urls:
        print(f"   Found login URLs: {len(login_urls)}")
        for url in set(login_urls[:5]):
            print(f"     {url}")
    
    # Look for request headers patterns
    header_patterns = [
        r'"Content-Type":\s*"([^"]+)"',
        r'"Accept":\s*"([^"]+)"',
        r'"User-Agent":\s*"([^"]+)"',
        r'"API-version":\s*"([^"]+)"'
    ]
    
    print("   Headers found:")
    for pattern in header_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        if matches:
            header_name = pattern.split('"')[1]
            print(f"     {header_name}: {matches[0][:50]}...")

def main():
    print("🔍 HAR Authentication Flow Analyzer")
    print("=" * 50)
    
    # Priority order for analysis
    har_files = [
        "charles_session.chls/Charles_session_mapping.har",
        "charles_session.chls/newest.har",
        "charles_session.chls/newest_!.har", 
        "charles_session.chls/new_club_session.har"
    ]
    
    for har_file in har_files:
        if os.path.exists(har_file):
            analyze_har_auth_flow(har_file)
            print("\n" + "="*50)
        else:
            print(f"❌ File not found: {har_file}")

if __name__ == "__main__":
    main()
