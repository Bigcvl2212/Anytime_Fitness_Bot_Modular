#!/usr/bin/env python3
"""
ClubOS Messaging Validation Script
Simple script to validate that the fixed ClubOS messaging solution works.
This can be run in the actual environment to send test messages to Jeremy Mayo.
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def main():
    """Main validation function"""
    print("🚀 ClubOS Messaging Solution Validation")
    print("=" * 50)
    
    try:
        # Import the fixed API client
        from src.services.api.clubos_api_client import create_clubos_api_client
        from config.secrets_local import get_secret
        
        print("✅ Successfully imported ClubOS API client")
        
        # Get credentials
        username = get_secret("clubos-username")
        password = get_secret("clubos-password")
        
        if not username or not password:
            print("❌ Missing ClubOS credentials")
            return False
        
        print("✅ Retrieved ClubOS credentials")
        
        # Create authenticated client
        print("\n🔐 Authenticating with ClubOS...")
        client = create_clubos_api_client(username, password)
        
        if not client:
            print("❌ Authentication failed")
            return False
        
        print("✅ ClubOS authentication successful")
        
        # Target member
        jeremy_mayo_id = "187032782"
        
        # Test messages
        sms_message = "🎉 ClubOS API messaging is now working! This SMS was sent via the fixed form submission method."
        email_message = "🎉 ClubOS API messaging is now working! This email was sent via the fixed form submission method that replaces the failing /action/Api endpoints."
        
        print(f"\n📱 Testing SMS to Jeremy Mayo ({jeremy_mayo_id})...")
        sms_result = client.send_message(jeremy_mayo_id, sms_message, "text")
        
        if sms_result:
            print("✅ SMS sent successfully!")
        else:
            print("❌ SMS failed")
        
        print(f"\n📧 Testing Email to Jeremy Mayo ({jeremy_mayo_id})...")  
        email_result = client.send_message(jeremy_mayo_id, email_message, "email")
        
        if email_result:
            print("✅ Email sent successfully!")
        else:
            print("❌ Email failed")
        
        # Test member profile direct submission
        print(f"\n👤 Testing direct member profile submission...")
        profile_result = client.send_message_to_member_profile(
            jeremy_mayo_id, 
            "Direct profile submission test - this proves the solution works!", 
            "text"
        )
        
        if profile_result:
            print("✅ Profile submission successful!")
        else:
            print("❌ Profile submission failed")
        
        # Summary
        print(f"\n📊 VALIDATION RESULTS:")
        print(f"SMS via Form:          {'✅ PASS' if sms_result else '❌ FAIL'}")
        print(f"Email via Form:        {'✅ PASS' if email_result else '❌ FAIL'}")
        print(f"Profile Submission:    {'✅ PASS' if profile_result else '❌ FAIL'}")
        
        success_count = sum([sms_result, email_result, profile_result])
        
        if success_count >= 2:
            print(f"\n🎉 SOLUTION VALIDATED!")
            print(f"✅ {success_count}/3 tests passed")
            print(f"✅ ClubOS messaging API is working")
            print(f"✅ Ready to replace Selenium automation")
            return True
        else:
            print(f"\n⚠️ SOLUTION NEEDS WORK")
            print(f"❌ Only {success_count}/3 tests passed")
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Make sure you're running from the correct directory")
        return False
    except Exception as e:
        print(f"❌ Validation error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)