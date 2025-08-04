"""
Test script to verify ClubOS training package API calls are working
"""

import os
import sys
import json
from datetime import datetime

# Add the services directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from services.api.enhanced_clubos_client import EnhancedClubOSAPIClient
    from services.api.clubos_api_client import ClubOSAPIAuthentication
    from config.secrets_local import get_secret
    
    print("✅ Successfully imported ClubOS API modules")
    
    def test_training_package_api():
        """Test the training package API calls with proper form authentication"""
        
        print("\n🔐 Testing ClubOS Authentication...")
        
        # Initialize authentication
        auth = ClubOSAPIAuthentication()
        
        # Get credentials
        username = get_secret('clubos-username')
        password = get_secret('clubos-password')
        
        if not username or not password:
            print("❌ Missing ClubOS credentials in secrets")
            return False
        
        # Authenticate using proper form submission
        if not auth.login(username, password):
            print("❌ ClubOS authentication failed")
            return False
        
        print("✅ ClubOS authentication successful")
        print(f"   📊 Session has {len(auth.session.cookies)} cookies")
        print(f"   🔑 Access token: {'✅ Present' if auth.access_token else '❌ Missing'}")
        
        # Initialize enhanced client
        client = EnhancedClubOSAPIClient(auth)
        
        print("\n🔍 Testing the URLs you found...")
        
        # Test the URLs you discovered in the browser
        test_urls = [
            "/action/ClubServicesNew",
            "/action/PackageAgreementUpdated/spa/"
        ]
        
        for url_path in test_urls:
            print(f"\n📋 Testing URL: {url_path}")
            
            try:
                # Use the session with proper authentication
                full_url = f"{client.base_url}{url_path}"
                
                # Use the authenticated session with proper headers
                headers = auth.get_headers()
                # Add additional browser-like headers
                headers.update({
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                    "Accept-Language": "en-US,en;q=0.9",
                    "Cache-Control": "no-cache",
                    "Pragma": "no-cache",
                    "Sec-Fetch-Dest": "document",
                    "Sec-Fetch-Mode": "navigate",
                    "Sec-Fetch-Site": "same-origin",
                    "Sec-Fetch-User": "?1",
                    "Upgrade-Insecure-Requests": "1",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
                })
                
                response = auth.session.get(
                    full_url,
                    headers=headers,
                    timeout=30
                )
                
                print(f"   Status: {response.status_code}")
                print(f"   Response length: {len(response.text)} characters")
                print(f"   Content-Type: {response.headers.get('content-type', 'Unknown')}")
                
                if response.status_code == 200:
                    # Check if we got training package data
                    response_lower = response.text.lower()
                    training_indicators = [
                        "training package", "package agreement", "training agreement",
                        "training client", "personal training", "pt package",
                        "training sessions", "package details", "training balance"
                    ]
                    
                    found_indicators = [indicator for indicator in training_indicators if indicator in response_lower]
                    
                    if found_indicators:
                        print(f"   ✅ Found training indicators: {found_indicators}")
                        
                        # Save HTML for analysis
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"training_page_{url_path.replace('/', '_')}_{timestamp}.html"
                        
                        with open(filename, 'w', encoding='utf-8') as f:
                            f.write(response.text)
                        print(f"   � Saved response to {filename}")
                        
                        # Look for JSON data embedded in the page
                        import re
                        json_patterns = [
                            r'window\.trainingData\s*=\s*(\{[^;]+\});',
                            r'window\.packageData\s*=\s*(\{[^;]+\});',
                            r'var\s+trainingPackages\s*=\s*(\[[^\]]+\]);',
                            r'"training_packages":\s*(\[[^\]]+\])',
                            r'"packages":\s*(\[[^\]]+\])'
                        ]
                        
                        for pattern in json_patterns:
                            matches = re.findall(pattern, response.text, re.IGNORECASE | re.DOTALL)
                            if matches:
                                print(f"   🎯 Found JSON pattern: {pattern}")
                                for match in matches[:2]:  # Limit to first 2 matches
                                    try:
                                        data = json.loads(match)
                                        print(f"   � JSON data: {json.dumps(data, indent=2)[:500]}...")
                                    except:
                                        print(f"   📝 Raw match: {match[:200]}...")
                    else:
                        print(f"   ⚠️ No training indicators found")
                        # Check if it's a login redirect
                        if "login" in response_lower or "username" in response_lower:
                            print(f"   � Appears to be login page - authentication may have expired")
                        
                else:
                    print(f"   ❌ Request failed with status {response.status_code}")
                    print(f"   Response: {response.text[:200]}")
                    
            except Exception as e:
                print(f"   ❌ Error testing {url_path}: {e}")
        
        # Also test training package endpoints we had before
        print(f"\n🔍 Testing existing training package methods...")
        
        try:
            # Test get_all_training_clients
            print(f"\n📋 Testing get_all_training_clients...")
            training_clients = client.get_all_training_clients()
            print(f"   📊 Result: {json.dumps(training_clients, indent=2)[:500]}...")
            
        except Exception as e:
            print(f"   ❌ Error testing training clients: {e}")
                
        return True
    
    if __name__ == "__main__":
        test_training_package_api()
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("   Make sure you're running from the gym-bot-modular directory")
    print("   And that all required files exist in services/api/")
