#!/usr/bin/env python3
"""
Debug ClubOS Login Page HTML Analysis
Analyzes the actual ClubOS login page to understand authentication mechanism
"""

import requests
import re
import json
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from config.secrets import get_secret

def analyze_clubos_login_page():
    """Analyze the ClubOS login page HTML to understand authentication"""
    
    print("🔍 Analyzing ClubOS Login Page HTML...")
    print("=" * 60)
    
    # Get credentials
    username = get_secret("clubos-username")
    password = get_secret("clubos-password")
    login_url = "https://anytime.club-os.com/action/Login/view?__fsk=1221801756"
    
    # Create session with browser-like headers
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    })
    
    try:
        # Step 1: Get the login page
        print("📄 Fetching login page...")
        response = session.get(login_url, timeout=30)
        
        if not response.ok:
            print(f"❌ Failed to load login page: {response.status_code}")
            return
        
        print(f"✅ Login page loaded successfully (Status: {response.status_code})")
        print(f"📄 URL: {response.url}")
        print(f"📄 Content-Type: {response.headers.get('content-type', 'unknown')}")
        
        # Step 2: Analyze the HTML content
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        
        print("\n🔍 HTML Analysis Results:")
        print("-" * 40)
        
        # Find all forms
        forms = soup.find_all('form')
        print(f"📋 Found {len(forms)} form(s) on the page")
        
        for i, form in enumerate(forms):
            print(f"\n📋 Form {i+1}:")
            print(f"   Action: {form.get('action', 'No action')}")
            print(f"   Method: {form.get('method', 'No method')}")
            print(f"   ID: {form.get('id', 'No ID')}")
            print(f"   Class: {form.get('class', 'No class')}")
            
            # Find all input fields
            inputs = form.find_all('input')
            print(f"   📝 Input fields ({len(inputs)}):")
            
            for inp in inputs:
                input_type = inp.get('type', 'text')
                input_name = inp.get('name', 'No name')
                input_id = inp.get('id', 'No ID')
                input_value = inp.get('value', '')
                print(f"      - Type: {input_type}, Name: {input_name}, ID: {input_id}, Value: {'[HIDDEN]' if input_type == 'password' else input_value}")
        
        # Step 3: Look for CSRF tokens and security tokens
        print("\n🔐 Security Token Analysis:")
        print("-" * 40)
        
        # Enhanced CSRF token patterns
        csrf_patterns = [
            (r'<meta name="csrf-token" content="([^"]+)"', 'Meta CSRF Token'),
            (r'<meta name="_token" content="([^"]+)"', 'Meta _token'),
            (r'<input[^>]*name="csrf_token"[^>]*value="([^"]+)"', 'Input CSRF Token'),
            (r'<input[^>]*name="_token"[^>]*value="([^"]+)"', 'Input _token'),
            (r'<input[^>]*name="csrf"[^>]*value="([^"]+)"', 'Input CSRF'),
            (r'window\.csrfToken\s*=\s*["\']([^"\']+)["\']', 'Window CSRF Token'),
            (r'window\._token\s*=\s*["\']([^"\']+)["\']', 'Window _token'),
            (r'data-csrf="([^"]+)"', 'Data CSRF'),
            (r'data-token="([^"]+)"', 'Data Token'),
            (r'csrf_token["\']?\s*[:=]\s*["\']([^"\']+)["\']', 'JSON CSRF Token'),
            (r'_token["\']?\s*[:=]\s*["\']([^"\']+)["\']', 'JSON _token'),
            (r'name="__fsk"[^>]*value="([^"]+)"', 'ClubOS __fsk'),
            (r'name="fsk"[^>]*value="([^"]+)"', 'ClubOS fsk'),
            (r'<input[^>]*name="__fsk"[^>]*value="([^"]+)"', 'Input __fsk'),
            (r'<input[^>]*name="fsk"[^>]*value="([^"]+)"', 'Input fsk'),
            (r'name="authenticity_token"[^>]*value="([^"]+)"', 'Authenticity Token'),
            (r'name="security_token"[^>]*value="([^"]+)"', 'Security Token'),
            (r'name="nonce"[^>]*value="([^"]+)"', 'Nonce'),
            (r'name="token"[^>]*value="([^"]+)"', 'Generic Token')
        ]
        
        found_tokens = []
        for pattern, description in csrf_patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            for match in matches:
                if match and len(match) > 5:
                    found_tokens.append((description, match))
                    print(f"   ✅ {description}: {match[:30]}...")
        
        if not found_tokens:
            print("   ❌ No CSRF tokens found with any pattern")
        
        # Step 4: Look for JavaScript variables and API endpoints
        print("\n🔍 JavaScript Analysis:")
        print("-" * 40)
        
        # Find all script tags
        scripts = soup.find_all('script')
        print(f"📜 Found {len(scripts)} script tag(s)")
        
        api_endpoints = []
        js_variables = []
        
        for i, script in enumerate(scripts):
            if script.string:
                script_content = script.string
                
                # Look for API endpoints
                api_patterns = [
                    r'["\'](/api/[^"\']+)["\']',
                    r'["\'](/ajax/[^"\']+)["\']',
                    r'["\'](/rest/[^"\']+)["\']',
                    r'["\'](/v1/[^"\']+)["\']',
                    r'["\'](/v2/[^"\']+)["\']',
                    r'url["\']?\s*[:=]\s*["\']([^"\']+)["\']',
                    r'endpoint["\']?\s*[:=]\s*["\']([^"\']+)["\']',
                    r'baseUrl["\']?\s*[:=]\s*["\']([^"\']+)["\']',
                    r'apiUrl["\']?\s*[:=]\s*["\']([^"\']+)["\']'
                ]
                
                for pattern in api_patterns:
                    matches = re.findall(pattern, script_content, re.IGNORECASE)
                    for match in matches:
                        if match.startswith('/'):
                            api_endpoints.append(match)
                
                # Look for JavaScript variables that might contain tokens
                js_patterns = [
                    r'window\.(\w+)\s*=\s*["\']([^"\']+)["\']',
                    r'var\s+(\w+)\s*=\s*["\']([^"\']+)["\']',
                    r'let\s+(\w+)\s*=\s*["\']([^"\']+)["\']',
                    r'const\s+(\w+)\s*=\s*["\']([^"\']+)["\']'
                ]
                
                for pattern in js_patterns:
                    matches = re.findall(pattern, script_content, re.IGNORECASE)
                    for var_name, var_value in matches:
                        if len(var_value) > 10:  # Likely a token
                            js_variables.append((var_name, var_value))
        
        # Remove duplicates
        api_endpoints = list(set(api_endpoints))
        js_variables = list(set(js_variables))
        
        print(f"🔗 Found {len(api_endpoints)} potential API endpoints:")
        for endpoint in api_endpoints[:10]:  # Show first 10
            print(f"   - {endpoint}")
        
        print(f"\n🔑 Found {len(js_variables)} JavaScript variables:")
        for var_name, var_value in js_variables[:10]:  # Show first 10
            print(f"   - {var_name}: {var_value[:30]}...")
        
        # Step 5: Test actual login submission
        print("\n🧪 Testing Login Submission:")
        print("-" * 40)
        
        # Prepare login data based on found form fields
        login_data = {
            "username": username,
            "password": password
        }
        
        # Add any found tokens to login data
        for description, token in found_tokens:
            if "csrf" in description.lower() or "token" in description.lower():
                login_data["csrf_token"] = token
                login_data["_token"] = token
                break
        
        print(f"📤 Submitting login with {len(login_data)} fields...")
        
        # Submit login
        login_response = session.post(login_url, data=login_data, allow_redirects=True, timeout=30)
        
        print(f"📥 Login response status: {login_response.status_code}")
        print(f"📥 Final URL: {login_response.url}")
        print(f"📥 Response headers: {dict(login_response.headers)}")
        
        # Check if login was successful
        if "dashboard" in login_response.url.lower() or "Dashboard" in login_response.url:
            print("✅ Login appears successful!")
        else:
            print("❌ Login may have failed")
        
        # Analyze post-login page
        post_login_html = login_response.text
        post_login_soup = BeautifulSoup(post_login_html, 'html.parser')
        
        # Look for new tokens in post-login page
        print("\n🔍 Post-Login Token Analysis:")
        print("-" * 40)
        
        post_login_tokens = []
        for pattern, description in csrf_patterns:
            matches = re.findall(pattern, post_login_html, re.IGNORECASE)
            for match in matches:
                if match and len(match) > 5:
                    post_login_tokens.append((description, match))
                    print(f"   ✅ {description}: {match[:30]}...")
        
        if not post_login_tokens:
            print("   ❌ No tokens found in post-login page")
        
        # Step 6: Look for actual API calls in network traffic
        print("\n🌐 Network Traffic Analysis:")
        print("-" * 40)
        
        # Look for AJAX calls or API endpoints in the HTML
        ajax_patterns = [
            r'fetch\(["\']([^"\']+)["\']',
            r'\.ajax\(["\']([^"\']+)["\']',
            r'axios\.(get|post|put|delete)\(["\']([^"\']+)["\']',
            r'\.get\(["\']([^"\']+)["\']',
            r'\.post\(["\']([^"\']+)["\']'
        ]
        
        all_ajax_calls = []
        for pattern in ajax_patterns:
            matches = re.findall(pattern, html_content + post_login_html, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    all_ajax_calls.extend(match)
                else:
                    all_ajax_calls.append(match)
        
        # Remove duplicates and filter
        all_ajax_calls = list(set([call for call in all_ajax_calls if call.startswith('/')]))
        
        print(f"🔗 Found {len(all_ajax_calls)} potential AJAX/API calls:")
        for call in all_ajax_calls[:15]:  # Show first 15
            print(f"   - {call}")
        
        # Step 7: Summary and recommendations
        print("\n📋 Summary and Recommendations:")
        print("=" * 60)
        
        print(f"📊 Analysis Summary:")
        print(f"   - Forms found: {len(forms)}")
        print(f"   - CSRF tokens found: {len(found_tokens)}")
        print(f"   - API endpoints found: {len(api_endpoints)}")
        print(f"   - JavaScript variables found: {len(js_variables)}")
        print(f"   - AJAX calls found: {len(all_ajax_calls)}")
        
        if found_tokens:
            print(f"\n🔐 Recommended CSRF token to use: {found_tokens[0][1][:30]}...")
        
        if api_endpoints:
            print(f"\n🔗 Recommended API endpoints to test:")
            for endpoint in api_endpoints[:5]:
                print(f"   - {endpoint}")
        
        print(f"\n💡 Next Steps:")
        print(f"   1. Test API endpoints with extracted tokens")
        print(f"   2. Implement proper CSRF token handling")
        print(f"   3. Use session cookies for authentication")
        print(f"   4. Monitor network traffic for real API calls")
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_clubos_login_page() 