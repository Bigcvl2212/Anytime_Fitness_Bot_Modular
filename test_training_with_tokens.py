"""
Test script to verify ClubOS training package API calls with proper form submission authentication
including fp and source tokens
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
    
    def test_training_package_urls_with_tokens():
        """Test the training package URLs with proper form authentication including fp and source tokens"""
        
        print("\n🔐 Testing ClubOS Authentication with Form Submission...")
        
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
        
        print("\n🔧 Testing token extraction...")
        
        # Test token extraction
        try:
            fp_token = client.get_fingerprint_token()
            source_token = client.get_source_page_token()
            print(f"   🔑 FP Token: {fp_token[:50]}...")
            print(f"   📄 Source Token: {source_token}")
        except Exception as e:
            print(f"   ❌ Error extracting tokens: {e}")
            return False
        
        print("\n🔍 Testing the training package URLs you discovered...")
        
        # Test the URLs you found with proper form authentication
        test_urls = [
            "/action/ClubServicesNew",
            "/action/PackageAgreementUpdated/spa/"
        ]
        
        for url_path in test_urls:
            print(f"\n📋 Testing URL: {url_path}")
            
            try:
                # Use the session with proper authentication and tokens
                full_url = f"{client.base_url}{url_path}"
                
                # Test with GET first (like in your browser)
                headers = auth.get_headers()
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
                print(f"   Final URL: {response.url}")
                
                if response.status_code == 200:
                    # Check if we got training package data
                    response_lower = response.text.lower()
                    training_indicators = [
                        "training package", "package agreement", "training agreement",
                        "training client", "personal training", "pt package",
                        "training sessions", "package details", "training balance",
                        "package status", "sessions remaining", "package amount"
                    ]
                    
                    found_indicators = [indicator for indicator in training_indicators if indicator in response_lower]
                    
                    if found_indicators:
                        print(f"   ✅ Found training indicators: {found_indicators}")
                        
                        # Save HTML for analysis
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        safe_path = url_path.replace('/', '_').replace(':', '_')
                        filename = f"training_page_with_tokens_{safe_path}_{timestamp}.html"
                        
                        with open(filename, 'w', encoding='utf-8') as f:
                            f.write(response.text)
                        print(f"   💾 Saved response to {filename}")
                        
                        # Look for specific training package data patterns
                        import re
                        
                        # Look for JSON data that might contain training package info
                        json_patterns = [
                            r'window\.trainingData\s*=\s*(\{[^;]+\});',
                            r'window\.packageData\s*=\s*(\{[^;]+\});',
                            r'var\s+trainingPackages\s*=\s*(\[[^\]]+\]);',
                            r'"training_packages":\s*(\[[^\]]+\])',
                            r'"packages":\s*(\[[^\]]+\])',
                            r'"packageAgreements":\s*(\[[^\]]+\])',
                            r'"agreementData":\s*(\{[^}]+\})'
                        ]
                        
                        for pattern in json_patterns:
                            matches = re.findall(pattern, response.text, re.IGNORECASE | re.DOTALL)
                            if matches:
                                print(f"   🎯 Found JSON pattern: {pattern}")
                                for match in matches[:2]:  # Limit to first 2 matches
                                    try:
                                        data = json.loads(match)
                                        print(f"   📊 JSON data: {json.dumps(data, indent=2)[:500]}...")
                                    except:
                                        print(f"   📝 Raw match: {match[:200]}...")
                        
                        # Look for HTML elements that might contain training data
                        html_patterns = [
                            r'<div[^>]*class="[^"]*training[^"]*"[^>]*>([^<]+)</div>',
                            r'<span[^>]*class="[^"]*package[^"]*"[^>]*>([^<]+)</span>',
                            r'<td[^>]*>([^<]*training[^<]*)</td>',
                            r'<li[^>]*>([^<]*package[^<]*)</li>'
                        ]
                        
                        for pattern in html_patterns:
                            matches = re.findall(pattern, response.text, re.IGNORECASE | re.DOTALL)
                            if matches:
                                print(f"   📋 Found HTML training elements: {matches[:3]}...")
                        
                        # Check if this is actually a real training page or just login
                        if "dashboard" in response.url.lower() and len(response.text) > 50000:
                            print(f"   🎯 This appears to be the actual training dashboard!")
                            
                    else:
                        print(f"   ⚠️ No training indicators found")
                        # Check if it's a login redirect
                        if "login" in response_lower or "username" in response_lower:
                            print(f"   🔄 Appears to be login page - authentication may have expired")
                        elif "dashboard" in response.url.lower():
                            print(f"   📋 Appears to be dashboard page - might need to navigate to training section")
                        
                else:
                    print(f"   ❌ Request failed with status {response.status_code}")
                    print(f"   Response preview: {response.text[:200]}")
                    
            except Exception as e:
                print(f"   ❌ Error testing {url_path}: {e}")
        
        print(f"\n🔍 Testing training package API endpoints...")
        
        # Test the training package endpoints with proper authentication and tokens
        try:
            print(f"\n📋 Testing get_all_training_clients...")
            training_clients = client.get_all_training_clients()
            print(f"   📊 Result: {json.dumps(training_clients, indent=2)[:500]}...")
            
        except Exception as e:
            print(f"   ❌ Error testing training clients: {e}")
        
        # Test member search with specific member ID
        test_member_id = "190295458"  # From your delegatedUserId cookie
        try:
            print(f"\n🔍 Testing training packages for member {test_member_id}...")
            member_packages = client.get_training_packages_for_client(test_member_id)
            print(f"   📊 Result: {json.dumps(member_packages, indent=2)[:500]}...")
            
        except Exception as e:
            print(f"   ❌ Error testing member packages: {e}")
                
        return True
    
    if __name__ == "__main__":
        test_training_package_urls_with_tokens()
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("   Make sure you're running from the gym-bot-modular directory")
    print("   And that all required files exist in services/api/")
