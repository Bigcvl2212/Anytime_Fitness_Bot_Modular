"""
Test script to figure out the REAL ClubOS training package endpoints
by exploring the ClubOS web interface
"""

import os
import sys
import json
import re
from datetime import datetime

# Add the services directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from services.api.enhanced_clubos_client import EnhancedClubOSAPIClient
    from services.api.clubos_api_client import ClubOSAPIAuthentication
    from config.secrets_local import get_secret
    
    print("✅ Successfully imported ClubOS API modules")
    
    def explore_clubos_endpoints():
        """Explore ClubOS to find the real training package endpoints"""
        
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
        
        # Test different ClubOS pages to find where training data lives
        test_endpoints = [
            "/action/Calendar",
            "/action/Dashboard",
            "/action/Members",
            "/action/Training",
            "/action/Reports",
            "/action/Agreements",
            "/action/Packages",
            "/ajax/members/search",
            "/ajax/calendar/events",
            "/ajax/dashboard/training",
            "/api/v3/members",
            "/api/v3/training",
            "/api/v3/packages",
        ]
        
        print(f"\n🔍 Testing {len(test_endpoints)} potential endpoints...")
        
        for endpoint in test_endpoints:
            try:
                url = f"{client.base_url}{endpoint}"
                print(f"\n📡 Testing: {endpoint}")
                
                response = client.session.get(
                    url,
                    headers=client.auth.get_headers(),
                    timeout=30,
                    allow_redirects=True
                )
                
                print(f"   Status: {response.status_code}")
                print(f"   Content-Type: {response.headers.get('content-type', 'unknown')}")
                print(f"   Content Length: {len(response.text)}")
                
                if response.status_code == 200:
                    content = response.text.lower()
                    
                    # Look for training-related keywords
                    training_keywords = [
                        'training package', 'training client', 'session', 'package',
                        'agreement', 'payment', 'funded', 'expires', 'remaining'
                    ]
                    
                    found_keywords = [kw for kw in training_keywords if kw in content]
                    if found_keywords:
                        print(f"   🎯 Found training keywords: {found_keywords}")
                        
                        # If this looks promising, save a sample
                        if len(found_keywords) >= 3:
                            filename = f"clubos_sample_{endpoint.replace('/', '_').replace('?', '_')}.html"
                            with open(filename, 'w', encoding='utf-8') as f:
                                f.write(response.text)
                            print(f"   💾 Saved sample to: {filename}")
                
                elif response.status_code == 401:
                    print(f"   🔒 Unauthorized - might need different auth")
                elif response.status_code == 404:
                    print(f"   ❌ Not found")
                else:
                    print(f"   ⚠️ Unexpected status")
                    
            except Exception as e:
                print(f"   💥 Error: {e}")
        
        # Also try accessing a specific member page to see the structure
        print(f"\n🔍 Testing member pages...")
        
        # Try some common member IDs
        test_member_ids = ["1", "100", "1000", "187032782"]  # 187032782 is our user ID
        
        for member_id in test_member_ids:
            try:
                member_url = f"{client.base_url}/action/Members/details/{member_id}"
                print(f"\n👤 Testing member page: {member_id}")
                
                response = client.session.get(
                    member_url,
                    headers=client.auth.get_headers(),
                    timeout=30
                )
                
                print(f"   Status: {response.status_code}")
                
                if response.status_code == 200 and len(response.text) > 1000:
                    content = response.text.lower()
                    if 'training' in content or 'package' in content:
                        print(f"   🎯 Member {member_id} page contains training data!")
                        filename = f"member_{member_id}_page.html"
                        with open(filename, 'w', encoding='utf-8') as f:
                            f.write(response.text)
                        print(f"   💾 Saved to: {filename}")
                        
            except Exception as e:
                print(f"   💥 Error: {e}")
                
        return True
    
    if __name__ == "__main__":
        explore_clubos_endpoints()
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("   Make sure you're running from the gym-bot-modular directory")
    print("   And that all required files exist in services/api/")
