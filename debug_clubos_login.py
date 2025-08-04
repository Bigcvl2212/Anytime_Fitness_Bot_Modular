#!/usr/bin/env python3
"""
Debug ClubOS login process to understand why authentication is failing
"""

import requests
from bs4 import BeautifulSoup
import re

def debug_login():
    """Debug the login process step by step"""
    
    print("🔍 Debugging ClubOS Login Process")
    print("="*50)
    
    session = requests.Session()
    base_url = "https://anytime.club-os.com"
    
    # Step 1: Get login page
    print("\n1. Getting login page...")
    response = session.get(f"{base_url}/action/Login")
    print(f"   Status: {response.status_code}")
    print(f"   URL: {response.url}")
    
    if response.status_code != 200:
        print(f"   ❌ Failed to get login page")
        return
    
    # Step 2: Analyze login form
    print("\n2. Analyzing login form...")
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find login form
    forms = soup.find_all('form')
    print(f"   Found {len(forms)} forms")
    
    login_form = None
    for form in forms:
        # Look for forms with username/password or login action
        if any(input_tag.get('name', '').lower() in ['username', 'email', 'user', 'login'] 
               for input_tag in form.find_all('input')):
            login_form = form
            break
    
    if not login_form:
        print("   ❌ No login form found")
        return
    
    print("   ✅ Login form found")
    print(f"   Form action: {login_form.get('action', 'Not specified')}")
    print(f"   Form method: {login_form.get('method', 'GET')}")
    
    # Step 3: Analyze form fields
    print("\n3. Analyzing form fields...")
    inputs = login_form.find_all('input')
    
    required_fields = {}
    optional_fields = {}
    
    for input_tag in inputs:
        name = input_tag.get('name', '')
        input_type = input_tag.get('type', 'text')
        value = input_tag.get('value', '')
        required = input_tag.get('required') is not None
        
        if name:
            field_info = {
                'type': input_type,
                'value': value,
                'required': required
            }
            
            if required or input_type in ['hidden']:
                required_fields[name] = field_info
            else:
                optional_fields[name] = field_info
            
            print(f"   Field: {name} ({input_type}) = '{value}' {'[REQUIRED]' if required else ''}")
    
    # Step 4: Look for CSRF tokens
    print("\n4. Looking for CSRF/security tokens...")
    csrf_candidates = []
    
    for name, field in required_fields.items():
        if any(token_name in name.lower() for token_name in ['token', 'csrf', '_source', '__fp', 'nonce']):
            csrf_candidates.append((name, field['value']))
            print(f"   CSRF candidate: {name} = {field['value']}")
    
    # Also check for tokens in script tags
    scripts = soup.find_all('script')
    for script in scripts:
        if script.string:
            token_matches = re.findall(r'(?:token|csrf)["\']?\s*[:=]\s*["\']([^"\']+)', script.string, re.IGNORECASE)
            for match in token_matches:
                csrf_candidates.append(('script_token', match))
                print(f"   Script token: {match}")
    
    # Step 5: Test credentials from secrets
    print("\n5. Testing with secrets...")
    try:
        from config.secrets_local import get_secret
        username = get_secret("clubos-username")
        password = get_secret("clubos-password")
        print(f"   Username from secrets: {username}")
        print(f"   Password from secrets: {'*' * len(password)}")
    except Exception as e:
        print(f"   ❌ Could not load secrets: {e}")
        return
    
    # Step 6: Attempt login with discovered fields
    print("\n6. Attempting login...")
    
    # Build login data
    login_data = {}
    
    # Add all required hidden fields
    for name, field in required_fields.items():
        if field['type'] == 'hidden' and field['value']:
            login_data[name] = field['value']
    
    # Try different username field names
    username_fields = ['username', 'email', 'user', 'login', 'loginName']
    password_fields = ['password', 'pass', 'pwd']
    
    username_field = None
    password_field = None
    
    for field_name in username_fields:
        if field_name in required_fields or field_name in optional_fields:
            username_field = field_name
            break
    
    for field_name in password_fields:
        if field_name in required_fields or field_name in optional_fields:
            password_field = field_name
            break
    
    if not username_field or not password_field:
        print(f"   ❌ Could not find username/password fields")
        print(f"   Available fields: {list(required_fields.keys()) + list(optional_fields.keys())}")
        return
    
    login_data[username_field] = username
    login_data[password_field] = password
    
    print(f"   Using username field: {username_field}")
    print(f"   Using password field: {password_field}")
    print(f"   Login data: {[k for k in login_data.keys()]}")
    
    # Submit login
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Referer': f'{base_url}/action/Login'
    }
    
    form_action = login_form.get('action', '/action/Login')
    if not form_action.startswith('http'):
        if form_action.startswith('/'):
            form_action = base_url + form_action
        else:
            form_action = f"{base_url}/action/{form_action}"
    
    print(f"   Submitting to: {form_action}")
    
    response = session.post(
        form_action,
        data=login_data,
        headers=headers,
        allow_redirects=False
    )
    
    print(f"   Response status: {response.status_code}")
    print(f"   Response headers: {dict(response.headers)}")
    
    if response.status_code in [301, 302, 303]:
        redirect_url = response.headers.get('Location', '')
        print(f"   ✅ Redirect to: {redirect_url}")
        
        # Follow redirect
        if redirect_url:
            if redirect_url.startswith('/'):
                redirect_url = base_url + redirect_url
            
            response = session.get(redirect_url)
            print(f"   Final page status: {response.status_code}")
            print(f"   Final page URL: {response.url}")
            
            if 'Dashboard' in response.url or 'dashboard' in response.url.lower():
                print("   🎉 LOGIN SUCCESSFUL!")
                
                # Check cookies
                cookies = session.cookies.get_dict()
                print(f"   Cookies received: {list(cookies.keys())}")
                for name, value in cookies.items():
                    print(f"     {name}: {value[:50]}...")
                
                return True
            else:
                print("   ❌ Login failed - not redirected to dashboard")
        
    else:
        print("   ❌ No redirect - login likely failed")
        print(f"   Response preview: {response.text[:300]}...")
    
    return False

if __name__ == "__main__":
    debug_login()
