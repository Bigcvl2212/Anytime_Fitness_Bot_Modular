#!/usr/bin/env python3
"""
Test the simplified ClubOS messaging client authentication
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_simplified_auth():
    """Test the simplified authentication"""
    try:
        from src.services.clubos_messaging_client_simple import SimplifiedClubOSMessagingClient
        
        print("🧪 Testing SimplifiedClubOSMessagingClient authentication...")
        
        # Initialize client (should auto-load credentials)
        client = SimplifiedClubOSMessagingClient()
        
        if not client.username or not client.password:
            print("❌ No credentials loaded")
            return False
        
        print(f"✅ Credentials loaded: {client.username[:5]}...")
        
        # Test authentication
        print("🔐 Testing authentication...")
        auth_result = client.authenticate()
        
        if auth_result:
            print(f"✅ Authentication successful!")
            print(f"   Staff ID: {client.staff_id}")
            print(f"   Club ID: {client.club_id}")
            print(f"   Session authenticated: {client.authenticated}")
            return True
        else:
            print("❌ Authentication failed")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_simplified_auth()
    if success:
        print("\n🎉 Authentication test passed!")
    else:
        print("\n💥 Authentication test failed!")
