#!/usr/bin/env python3
"""
Direct Message Test Script
Tests sending a message to Jeremy Mayo via ClubOS API
"""

import sys
import time
from datetime import datetime

# Add the project root to the path for imports
sys.path.insert(0, '.')

from services.api.migration_service import get_migration_service
from config.secrets import get_secret
from config.constants import CLUBOS_USERNAME_SECRET, CLUBOS_PASSWORD_SECRET


def test_direct_message():
    """Test sending a message directly to Jeremy Mayo"""
    print("🧪 Testing direct message send to Jeremy Mayo...")
    
    try:
        # Get ClubOS credentials
        username = get_secret(CLUBOS_USERNAME_SECRET)
        password = get_secret(CLUBOS_PASSWORD_SECRET)
        
        if not username or not password:
            print("❌ ClubOS credentials not available")
            return False
        
        print(f"✅ Using credentials for: {username}")
        
        # Initialize migration service in hybrid mode
        migration_service = get_migration_service("hybrid")
        
        # Test message content
        test_subject = "API Test Message"
        test_body = f"This is a test message sent via ClubOS API at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}. This message is testing the API integration for the Gym Bot system."
        
        print(f"\n📧 Sending test message:")
        print(f"   To: Jeremy Mayo")
        print(f"   Subject: {test_subject}")
        print(f"   Body: {test_body[:50]}...")
        
        # Send the message
        start_time = time.time()
        result = migration_service.send_message("Jeremy Mayo", test_subject, test_body)
        end_time = time.time()
        
        print(f"\n⏱️  Message send completed in {end_time - start_time:.2f} seconds")
        
        # Analyze results
        if result is True:
            print("✅ SUCCESS: Message sent successfully via API!")
            return True
        elif result == "OPTED_OUT":
            print("⚠️  RESULT: Member has opted out of communications")
            return True  # This is still a successful test
        else:
            print("❌ FAILED: Message send failed")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def test_member_search():
    """Test member search functionality"""
    print("\n🔍 Testing member search for Jeremy Mayo...")
    
    try:
        from services.api.enhanced_clubos_service import ClubOSAPIService
        from config.secrets import get_secret
        from config.constants import CLUBOS_USERNAME_SECRET, CLUBOS_PASSWORD_SECRET
        
        username = get_secret(CLUBOS_USERNAME_SECRET)
        password = get_secret(CLUBOS_PASSWORD_SECRET)
        
        service = ClubOSAPIService(username, password)
        
        # Test member search
        member_info = service._api_search_member("Jeremy Mayo")
        
        if member_info:
            print(f"✅ Member found:")
            print(f"   ID: {member_info.get('id')}")
            print(f"   Name: {member_info.get('name')}")
            print(f"   Email: {member_info.get('email')}")
            print(f"   Phone: {member_info.get('phone')}")
            return True
        else:
            print("❌ Member not found")
            return False
            
    except Exception as e:
        print(f"❌ Search error: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Starting direct message test...")
    
    # Test 1: Member search
    search_success = test_member_search()
    
    # Test 2: Direct message send
    message_success = test_direct_message()
    
    # Summary
    print(f"\n📊 Test Summary:")
    print(f"   Member Search: {'✅ PASSED' if search_success else '❌ FAILED'}")
    print(f"   Message Send: {'✅ PASSED' if message_success else '❌ FAILED'}")
    
    if search_success and message_success:
        print("\n🎉 All tests passed! ClubOS API integration is working.")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.") 