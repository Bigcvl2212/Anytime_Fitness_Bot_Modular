#!/usr/bin/env python3
"""
Advanced Square Token Diagnostics
"""
import requests
import json
import base64
import os
import sys
sys.path.append('src')

from config.secrets_local import get_secret

def decode_square_token(token):
    """Try to decode Square token structure"""
    print(f"🔍 TOKEN ANALYSIS")
    print("=" * 30)
    
    print(f"Token: {token[:20]}...{token[-10:]}")
    print(f"Length: {len(token)} characters")
    print(f"Starts with EAAA: {'✅' if token.startswith('EAAA') else '❌'}")
    
    # Square tokens are not JWT, but let's see if there's any pattern
    try:
        # Check character composition
        alpha_count = sum(c.isalpha() for c in token)
        digit_count = sum(c.isdigit() for c in token)
        special_count = len(token) - alpha_count - digit_count
        
        print(f"Character composition:")
        print(f"  - Alphabetic: {alpha_count}")
        print(f"  - Numeric: {digit_count}")
        print(f"  - Special: {special_count}")
        
        # Check for common invalid patterns
        if token.count('x') > 5:
            print("⚠️  WARNING: Token contains many 'x' characters - might be placeholder")
        if token == token.upper() or token == token.lower():
            print("⚠️  WARNING: Token is all same case - might be placeholder")
            
    except Exception as e:
        print(f"❌ Error analyzing token: {e}")

def test_token_variations():
    """Test different ways of using the token"""
    print(f"\n🧪 TOKEN VARIATION TESTS")
    print("=" * 40)
    
    prod_token = get_secret("square-production-access-token")
    sandbox_token = get_secret("square-sandbox-access-token")
    
    # Test different API versions
    api_versions = ['2024-07-17', '2023-10-18', '2022-08-17']
    
    for version in api_versions:
        print(f"\n📅 Testing API Version: {version}")
        headers = {
            'Authorization': f'Bearer {prod_token}',
            'Square-Version': version,
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.get(
                'https://connect.squareup.com/v2/locations',
                headers=headers,
                timeout=10
            )
            print(f"   Status: {response.status_code}")
            if response.status_code != 401:
                print(f"   ✅ Different response with version {version}!")
                try:
                    data = response.json()
                    print(f"   Response: {json.dumps(data, indent=2)[:200]}...")
                except:
                    print(f"   Response: {response.text[:200]}...")
                break
        except Exception as e:
            print(f"   ❌ Exception: {e}")

def check_token_format_validity():
    """Check if tokens match Square's expected format"""
    print(f"\n📏 TOKEN FORMAT VALIDATION")
    print("=" * 40)
    
    prod_token = get_secret("square-production-access-token")
    sandbox_token = get_secret("square-sandbox-access-token")
    
    def validate_token(token, env_name):
        print(f"\n{env_name} Token:")
        print(f"  Raw: {token}")
        print(f"  Length: {len(token)}")
        
        # Square production tokens should start with EAAA
        # and be 64+ characters
        if token.startswith('EAAA') and len(token) >= 60:
            print(f"  ✅ Format appears valid")
            
            # Check if it looks like a real token vs example/dummy
            suspicious_patterns = [
                'example', 'test', 'dummy', 'placeholder', 
                '1234', '0000', 'xxxx', 'abcd'
            ]
            
            is_suspicious = any(pattern in token.lower() for pattern in suspicious_patterns)
            if is_suspicious:
                print(f"  ⚠️  Token contains suspicious patterns - might be example")
            else:
                print(f"  ✅ Token appears to be legitimate")
                
            # Try to identify token type from patterns
            if 'sandbox' in token.lower() or token.startswith('EAAAlsandbox'):
                print(f"  📝 Appears to be sandbox token")
            elif 'prod' in token.lower() or 'live' in token.lower():
                print(f"  📝 Appears to be production token")
        else:
            print(f"  ❌ Invalid format - should start with EAAA and be 60+ chars")
    
    validate_token(prod_token, "PRODUCTION")
    validate_token(sandbox_token, "SANDBOX")

def test_oauth_flow():
    """Check if this might be an OAuth issue"""
    print(f"\n🔐 OAUTH/PERMISSIONS CHECK")
    print("=" * 40)
    
    prod_token = get_secret("square-production-access-token")
    
    # Try the OAuth token info endpoint
    headers = {
        'Authorization': f'Bearer {prod_token}',
        'Content-Type': 'application/json',
        'Square-Version': '2024-07-17'
    }
    
    try:
        response = requests.get(
            'https://connect.squareup.com/v2/oauth2/token/status',
            headers=headers,
            timeout=10
        )
        
        print(f"OAuth Token Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Token is valid!")
            print(f"Token info: {json.dumps(data, indent=2)}")
        else:
            print(f"❌ OAuth check failed: {response.text}")
    except Exception as e:
        print(f"❌ OAuth check exception: {e}")

if __name__ == "__main__":
    prod_token = get_secret("square-production-access-token")
    sandbox_token = get_secret("square-sandbox-access-token")
    
    if prod_token:
        decode_square_token(prod_token)
        check_token_format_validity()
        test_token_variations()
        test_oauth_flow()
    else:
        print("❌ No production token found")
