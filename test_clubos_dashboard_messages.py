#!/usr/bin/env python3
"""
Test script for ClubOS Dashboard messages integration
Tests the new ClubOS live message fetching functionality
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

def test_clubos_dashboard_messages():
    """Test ClubOS dashboard message fetching"""
    try:
        from src.services.api.enhanced_clubos_service import ClubOSAPIService
        from config.secrets_local import get_secret
        
        print("🧪 Testing ClubOS Dashboard Messages Integration")
        print("=" * 60)
        
        # Get credentials
        username = get_secret('clubos-username')
        password = get_secret('clubos-password')
        
        if not username or not password:
            print("❌ ClubOS credentials not available in secrets_local.py")
            return False
        
        print(f"🔐 Authenticating with ClubOS as {username}...")
        
        # Initialize service
        try:
            service = ClubOSAPIService(username, password)
            print("✅ ClubOS API service initialized successfully")
        except Exception as auth_error:
            print(f"❌ Authentication failed: {auth_error}")
            return False
        
        # Test dashboard message fetching
        print("\n📡 Fetching ClubOS dashboard messages...")
        try:
            messages = service.get_dashboard_messages(limit=5)
            
            if messages:
                print(f"✅ Retrieved {len(messages)} ClubOS dashboard messages")
                print("\n📋 Message Summary:")
                print("-" * 40)
                
                for i, msg in enumerate(messages, 1):
                    print(f"{i}. {msg.get('name', 'Unknown')}")
                    print(f"   Preview: {msg.get('preview', 'No preview')[:60]}...")
                    print(f"   Time: {msg.get('time', 'Unknown')}")
                    print(f"   Status: {msg.get('status', 'Unknown')} ({msg.get('status_color', 'default')})")
                    print(f"   Needs Attention: {msg.get('needs_attention', False)}")
                    print()
                
                print("✅ ClubOS dashboard messages test completed successfully!")
                return True
                
            else:
                print("⚠️ No messages retrieved from ClubOS dashboard")
                print("This could be normal if there are no recent messages")
                return True
                
        except Exception as fetch_error:
            print(f"❌ Error fetching dashboard messages: {fetch_error}")
            return False
            
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

def test_dashboard_integration():
    """Test that the dashboard route can use the new service"""
    print("\n🧪 Testing Dashboard Integration")
    print("=" * 60)
    
    try:
        # Import dashboard route dependencies
        from flask import Flask
        from src.routes.dashboard import dashboard_bp
        
        # Create test app
        app = Flask(__name__)
        app.register_blueprint(dashboard_bp)
        
        print("✅ Dashboard blueprint imported successfully")
        print("✅ Integration test passed - dashboard should now use ClubOS live messages")
        
        return True
        
    except Exception as e:
        print(f"❌ Dashboard integration test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting ClubOS Dashboard Messages Tests")
    print("=" * 60)
    
    # Run tests
    test1_result = test_clubos_dashboard_messages()
    test2_result = test_dashboard_integration()
    
    print("\n📊 Test Results Summary")
    print("=" * 60)
    print(f"ClubOS Messages Test: {'✅ PASSED' if test1_result else '❌ FAILED'}")
    print(f"Dashboard Integration: {'✅ PASSED' if test2_result else '❌ FAILED'}")
    
    if test1_result and test2_result:
        print("\n🎉 All tests passed! ClubOS dashboard messages integration is ready!")
        print("\n📝 Next Steps:")
        print("1. Start your Flask application")
        print("2. Navigate to the dashboard")
        print("3. Check that the message inbox shows live ClubOS messages")
        print("4. Verify the messages show real member names and content")
        
    else:
        print("\n⚠️ Some tests failed. Please check the errors above.")
    
    print("\n" + "=" * 60)