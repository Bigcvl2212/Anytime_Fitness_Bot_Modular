"""
Simple test to verify authentication is working correctly
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
    
    def test_simple_authentication():
        """Test basic authentication and dashboard access"""
        
        print("\n🔐 Testing Basic ClubOS Authentication...")
        
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
        
        # Print all cookies
        print("\n📋 All cookies:")
        for cookie in auth.session.cookies:
            value_preview = cookie.value[:20] + "..." if len(cookie.value) > 20 else cookie.value
            print(f"   {cookie.name}: {value_preview}")
        
        # Test dashboard access
        print("\n🌐 Testing dashboard access...")
        headers = auth.get_headers()
        headers.update({
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
        })
        
        dashboard_response = auth.session.get(
            f"{auth.base_url}/action/Dashboard/view",
            headers=headers,
            timeout=30
        )
        
        print(f"   Status: {dashboard_response.status_code}")
        print(f"   Final URL: {dashboard_response.url}")
        print(f"   Response length: {len(dashboard_response.text)} characters")
        
        if "Login" in dashboard_response.url:
            print("   ❌ Still redirected to login - authentication not working")
            return False
        else:
            print("   ✅ Dashboard access successful!")
            
            # Save the dashboard HTML for inspection
            with open('dashboard_debug.html', 'w', encoding='utf-8') as f:
                f.write(dashboard_response.text)
            print("   💾 Saved dashboard HTML to 'dashboard_debug.html'")
            
            # Test calendar access
            print("\n📅 Testing calendar access...")
            calendar_response = auth.session.get(
                f"{auth.base_url}/action/Calendar",
                headers=headers,
                timeout=30
            )
            
            print(f"   Calendar Status: {calendar_response.status_code}")
            print(f"   Calendar Final URL: {calendar_response.url}")
            
            if "Login" not in calendar_response.url:
                print("   ✅ Calendar access successful!")
                
                # Save the calendar HTML for inspection
                with open('calendar_debug.html', 'w', encoding='utf-8') as f:
                    f.write(calendar_response.text)
                print("   💾 Saved calendar HTML to 'calendar_debug.html'")
                
                return True
            else:
                print("   ❌ Calendar redirected to login")
                return False
    
    if __name__ == "__main__":
        test_simple_authentication()
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("   Make sure you're running from the gym-bot-modular directory")
    print("   And that all required files exist in services/api/")
