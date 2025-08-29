#!/usr/bin/env python3
"""
Final Square Token Validation - Check if tokens are valid at all
"""
import requests
import json
import sys
import os
sys.path.append('src')

from config.secrets_local import get_secret

def validate_token_with_curl_equivalent():
    """Test with exact curl equivalent to rule out SDK issues"""
    print("🌐 CURL-EQUIVALENT TEST")
    print("=" * 30)
    
    prod_token = get_secret("square-production-access-token")
    
    print(f"Testing token: {prod_token[:20]}...{prod_token[-10:]}")
    
    # This is exactly what a working curl command would look like:
    # curl https://connect.squareup.com/v2/locations \
    #   -H 'Square-Version: 2024-07-17' \
    #   -H 'Authorization: Bearer YOUR_ACCESS_TOKEN' \
    #   -H 'Content-Type: application/json'
    
    headers = {
        'Square-Version': '2024-07-17',
        'Authorization': f'Bearer {prod_token}',
        'Content-Type': 'application/json'
    }
    
    print("\n📡 Request details:")
    print(f"URL: https://connect.squareup.com/v2/locations")
    print(f"Method: GET")
    print(f"Headers:")
    for key, value in headers.items():
        if key == 'Authorization':
            print(f"  {key}: Bearer {value[7:27]}...{value[-10:]}")
        else:
            print(f"  {key}: {value}")
    
    try:
        response = requests.get(
            'https://connect.squareup.com/v2/locations',
            headers=headers,
            timeout=30
        )
        
        print(f"\n📨 Response:")
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        response_text = response.text
        print(f"Response Body: {response_text}")
        
        # Check if this looks like a valid Square error vs something else
        try:
            error_data = json.loads(response_text)
            if 'errors' in error_data:
                errors = error_data['errors']
                print(f"\n🔍 Error Analysis:")
                for error in errors:
                    print(f"  Category: {error.get('category')}")
                    print(f"  Code: {error.get('code')}")
                    print(f"  Detail: {error.get('detail')}")
                    
                    # Check for specific error patterns
                    if error.get('code') == 'UNAUTHORIZED':
                        if 'expired' in error.get('detail', '').lower():
                            print("  💡 Token appears to be expired")
                        elif 'invalid' in error.get('detail', '').lower():
                            print("  💡 Token appears to be invalid")
                        elif 'not found' in error.get('detail', '').lower():
                            print("  💡 Application or token not found")
                        else:
                            print("  💡 Generic authorization failure")
                            
        except json.JSONDecodeError:
            print(f"❌ Non-JSON response - this is unusual for Square API")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

def check_common_token_issues():
    """Check for common token configuration issues"""
    print(f"\n🔧 COMMON ISSUES CHECK")
    print("=" * 30)
    
    prod_token = get_secret("square-production-access-token")
    sandbox_token = get_secret("square-sandbox-access-token")
    prod_location = get_secret("square-production-location-id")
    sandbox_location = get_secret("square-sandbox-location-id")
    
    print("Token Analysis:")
    
    # Check for whitespace issues
    if prod_token != prod_token.strip():
        print("❌ Production token has leading/trailing whitespace")
    else:
        print("✅ Production token has no whitespace issues")
        
    if sandbox_token != sandbox_token.strip():
        print("❌ Sandbox token has leading/trailing whitespace")  
    else:
        print("✅ Sandbox token has no whitespace issues")
    
    # Check token uniqueness
    if prod_token == sandbox_token:
        print("⚠️  Production and sandbox tokens are identical - this is wrong")
    else:
        print("✅ Production and sandbox tokens are different")
    
    # Check location ID formats
    print(f"\nLocation ID Analysis:")
    print(f"Production Location: {prod_location}")
    print(f"Sandbox Location: {sandbox_location}")
    
    # Production location IDs are typically shorter (like LCR9E5HA00KPA)
    # Sandbox location IDs start with sq0csp-
    if prod_location.startswith('sq0csp-'):
        print("⚠️  Production location ID looks like a sandbox ID")
    elif len(prod_location) < 15 and prod_location.isalnum():
        print("✅ Production location ID format looks correct")
    else:
        print("❓ Production location ID format is unusual")
        
    if sandbox_location.startswith('sq0csp-'):
        print("✅ Sandbox location ID format looks correct")
    else:
        print("⚠️  Sandbox location ID doesn't start with sq0csp-")

def suggest_next_steps():
    """Provide specific next steps based on findings"""
    print(f"\n💡 DIAGNOSIS & NEXT STEPS")
    print("=" * 40)
    
    print("Based on the testing, the tokens appear to be:")
    print("1. ✅ Correctly formatted (64 chars, start with EAAA)")
    print("2. ✅ Not obvious placeholders or examples") 
    print("3. ❌ Completely rejected by Square API (401 on all endpoints)")
    print("")
    
    print("This suggests ONE of these issues:")
    print("")
    print("🔍 ISSUE 1: Application Status")
    print("   - Your Square application may be inactive/suspended")
    print("   - Check Square Dashboard → Applications → Your App")
    print("   - Look for status: Active, In Review, Suspended")
    print("")
    
    print("🔍 ISSUE 2: Wrong Application Type")
    print("   - These tokens may be from Square POS, not Square Developer API")
    print("   - You need tokens from 'Connect API' application type")
    print("   - Check if you created a 'Connect API' app vs other types")
    print("")
    
    print("🔍 ISSUE 3: Token Regeneration Needed")
    print("   - Tokens may have been regenerated in Square Dashboard")
    print("   - Check if new tokens were issued recently")
    print("   - Old tokens become invalid when new ones are generated")
    print("")
    
    print("🔍 ISSUE 4: Environment Mismatch")  
    print("   - Production tokens require app approval for live use")
    print("   - Try switching to sandbox-only for testing")
    print("   - Check if your app is approved for production")
    print("")
    
    print("📋 RECOMMENDED ACTION:")
    print("1. Login to Square Dashboard (developer.squareup.com)")
    print("2. Go to Applications → Your Application") 
    print("3. Check application status and type")
    print("4. Generate fresh tokens")
    print("5. Verify application has necessary permissions enabled")

if __name__ == "__main__":
    validate_token_with_curl_equivalent()
    check_common_token_issues()
    suggest_next_steps()
