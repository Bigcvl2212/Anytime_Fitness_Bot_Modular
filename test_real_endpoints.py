"""
Test script to verify the real ClubOS training package endpoints found from browser inspection
"""

import os
import sys
import json
from datetime import datetime

# Add the services directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from src.services.api.enhanced_clubos_client import EnhancedClubOSAPIClient
    from src.services.api.clubos_api_client import ClubOSAPIAuthentication
    from config.secrets_local import get_secret
    
    print("✅ Successfully imported ClubOS API modules")
    
    def test_real_endpoints():
        """Test the real ClubOS endpoints found from browser inspection"""
        
        print("\n🔐 Testing ClubOS Authentication...")
        
        # Initialize authentication
        auth = ClubOSAPIAuthentication()
        
        # Get credentials
        username = get_secret('clubos-username')
        password = get_secret('clubos-password')
        
        if not username or not password:
            print("❌ Missing ClubOS credentials in secrets")
            return False
        
        # Authenticate
        if not auth.login(username, password):
            print("❌ ClubOS authentication failed")
            return False
        
        print("✅ ClubOS authentication successful")
        
        # Initialize enhanced client
        client = EnhancedClubOSAPIClient(auth)
        
        # Test the real endpoints found from browser inspection
        endpoints_to_test = [
            {
                'name': 'Club Services New',
                'url': '/action/ClubServicesNew',
                'method': 'GET',
                'description': 'Main services page - might contain training services data'
            },
            {
                'name': 'Package Agreement Updated SPA',
                'url': '/action/PackageAgreementUpdated/spa/',
                'method': 'GET', 
                'description': 'Training package agreement endpoint - this looks very promising!'
            },
            {
                'name': 'Package Agreement Updated',
                'url': '/action/PackageAgreementUpdated/',
                'method': 'GET',
                'description': 'Training package agreement endpoint (non-SPA version)'
            }
        ]
        
        for endpoint in endpoints_to_test:
            print(f"\n🔍 Testing: {endpoint['name']}")
            print(f"   URL: {endpoint['url']}")
            print(f"   Description: {endpoint['description']}")
            
            try:
                full_url = f"{client.base_url}{endpoint['url']}"
                
                response = client.session.request(
                    method=endpoint['method'],
                    url=full_url,
                    headers=client.auth.get_headers(),
                    timeout=30
                )
                
                print(f"   Status: {response.status_code}")
                print(f"   Content-Type: {response.headers.get('content-type', 'unknown')}")
                print(f"   Content Length: {len(response.text)} characters")
                
                if response.status_code == 200:
                    # Check if response contains training package related content
                    content_lower = response.text.lower()
                    training_keywords = [
                        'training', 'package', 'agreement', 'session', 'client',
                        'active', 'remaining', 'purchased', 'trainer', 'personal'
                    ]
                    
                    found_keywords = [kw for kw in training_keywords if kw in content_lower]
                    
                    if found_keywords:
                        print(f"   ✅ Found training-related keywords: {found_keywords}")
                        
                        # Save a sample of the response for analysis
                        filename = f"sample_{endpoint['name'].lower().replace(' ', '_')}.html"
                        with open(filename, 'w', encoding='utf-8') as f:
                            f.write(response.text)
                        print(f"   💾 Saved response sample to: {filename}")
                        
                        # Look for JSON data embedded in the HTML
                        if 'json' in content_lower or '{' in response.text:
                            print(f"   🔍 Response appears to contain JSON data!")
                            
                            # Try to extract JSON from the response
                            lines = response.text.split('\n')
                            for i, line in enumerate(lines):
                                if '{' in line and ('training' in line.lower() or 'package' in line.lower() or 'agreement' in line.lower()):
                                    print(f"   📋 Found potential JSON on line {i+1}: {line.strip()[:200]}...")
                    else:
                        print(f"   ⚠️ No training-related keywords found")
                        
                    # Show first 300 characters of response
                    print(f"   📄 Response preview: {response.text[:300]}...")
                    
                else:
                    print(f"   ❌ Request failed")
                    print(f"   Response: {response.text[:200]}...")
                    
            except Exception as e:
                print(f"   ❌ Error testing {endpoint['name']}: {e}")
        
        # Test if we can find any AJAX endpoints by looking for common patterns
        print(f"\n🔍 Testing common AJAX patterns...")
        ajax_patterns = [
            '/ajax/training/packages',
            '/ajax/packages/list',
            '/ajax/agreements/training', 
            '/api/v3/training/packages',
            '/api/v3/packages',
            '/api/v3/agreements',
            '/rest/training/packages',
            '/rest/packages',
            '/rest/agreements'
        ]
        
        for pattern in ajax_patterns:
            try:
                full_url = f"{client.base_url}{pattern}"
                response = client.session.get(
                    full_url,
                    headers=client.auth.get_headers(),
                    timeout=10
                )
                
                if response.status_code != 404:
                    print(f"   🎯 Found endpoint: {pattern} (Status: {response.status_code})")
                    if response.status_code == 200:
                        print(f"      Content-Type: {response.headers.get('content-type', 'unknown')}")
                        print(f"      Response preview: {response.text[:200]}...")
                        
            except Exception as e:
                pass  # Expected for most patterns
        
        return True
    
    if __name__ == "__main__":
        test_real_endpoints()
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("   Make sure you're running from the gym-bot-modular directory")
    print("   And that all required files exist in services/api/")
