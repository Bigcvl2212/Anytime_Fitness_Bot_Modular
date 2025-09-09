#!/usr/bin/env python3
"""
Test script to validate the messaging client fixes
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.clubos_messaging_client_simple import ClubOSMessagingClient
import logging

# Set up logging to see detailed output
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_member_data_fetch():
    """Test member data fetching with the new HAR-based approach"""
    print("🧪 Testing ClubOS Messaging Client - Member Data Fetch")
    print("=" * 60)
    
    client = ClubOSMessagingClient()
    
    # Test authentication
    print("🔐 Testing authentication...")
    if not client.authenticate():
        print("❌ Authentication failed")
        return False
    
    print(f"✅ Authentication successful")
    print(f"✅ Staff ID: {client.staff_id}")
    print(f"✅ Club ID: {client.club_id}")
    
    # Test member data fetching with a known member ID
    test_member_ids = [
        "192224494",  # Kymberley Marr from HAR
        "189425730",  # Dennis Rost from HAR
    ]
    
    for member_id in test_member_ids:
        print(f"\n📋 Testing member data fetch for {member_id}...")
        member_data = client.fetch_member_data(member_id)
        
        if member_data:
            print(f"✅ Member data retrieved: {member_data}")
            
            # Validate required fields
            required_fields = ['firstName', 'lastName']
            missing_fields = [field for field in required_fields if not member_data.get(field)]
            
            if missing_fields:
                print(f"⚠️ Missing required fields: {missing_fields}")
            else:
                print(f"✅ All required fields present")
                
                # Test if this data would work for messaging
                name = f"{member_data.get('firstName', '')} {member_data.get('lastName', '')}"
                print(f"✅ Member name: {name}")
                if member_data.get('mobilePhone'):
                    print(f"✅ Mobile phone: {member_data.get('mobilePhone')}")
                if member_data.get('email'):
                    print(f"✅ Email: {member_data.get('email')}")
        else:
            print(f"❌ No member data retrieved for {member_id}")
    
    print(f"\n✅ Member data fetch test completed")
    return True

def test_message_validation():
    """Test message sending validation without actually sending"""
    print("\n🧪 Testing Message Validation")
    print("=" * 40)
    
    client = ClubOSMessagingClient()
    
    if not client.authenticate():
        print("❌ Authentication failed")
        return False
    
    # Test with member data from HAR
    test_data = {
        'firstName': 'Kymberley',
        'lastName': 'Marr', 
        'email': 'nixon.alex53@gmail.com',
        'mobilePhone': '+1 (765) 271-6832'
    }
    
    # Test validation
    is_valid, error_msg = client.validate_recipient(test_data)
    
    if is_valid:
        print(f"✅ Member data validation passed")
    else:
        print(f"❌ Member data validation failed: {error_msg}")
    
    return is_valid

if __name__ == "__main__":
    print("🚀 Starting ClubOS Messaging Client Tests")
    print("=" * 60)
    
    try:
        # Test member data fetching
        data_test_passed = test_member_data_fetch()
        
        # Test message validation  
        validation_test_passed = test_message_validation()
        
        print("\n📊 Test Results Summary")
        print("=" * 30)
        print(f"Member Data Fetch: {'✅ PASS' if data_test_passed else '❌ FAIL'}")
        print(f"Message Validation: {'✅ PASS' if validation_test_passed else '❌ FAIL'}")
        
        if data_test_passed and validation_test_passed:
            print("\n🎉 All tests passed! The messaging client should now work properly.")
        else:
            print("\n⚠️ Some tests failed. Please check the logs above for details.")
            
    except Exception as e:
        print(f"❌ Test execution error: {e}")
        import traceback
        traceback.print_exc()
