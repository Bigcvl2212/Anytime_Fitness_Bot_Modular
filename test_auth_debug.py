#!/usr/bin/env python3
"""
Debug script to test authentication system
"""

from flask import Flask, session, request
from src.main_app import create_app
from src.routes.auth import require_auth

app = create_app()

def test_auth_status():
    """Test current authentication status"""
    with app.app_context():
        print("🔍 Testing authentication status...")

        # Check session
        print(f"Session authenticated: {session.get('authenticated', False)}")
        print(f"Session manager_id: {session.get('manager_id', 'None')}")
        print(f"Session keys: {list(session.keys()) if session else 'No session'}")

        # Test the auth service directly
        try:
            from src.services.authentication.secure_auth_service import SecureAuthService
            auth_service = SecureAuthService()
            is_valid, manager_id = auth_service.validate_session()
            print(f"Auth service validation: is_valid={is_valid}, manager_id={manager_id}")
        except Exception as e:
            print(f"❌ Auth service error: {e}")

def test_dashboard_access():
    """Test if dashboard would require authentication"""
    with app.test_request_context('/'):
        print("\n🔍 Testing dashboard access...")

        # Simulate unauthenticated request
        session.clear()

        try:
            from src.routes.dashboard import dashboard
            # This should redirect to login if auth is working
            result = dashboard()
            if hasattr(result, 'status_code') and result.status_code == 302:
                print("✅ Dashboard correctly redirected to login (authentication working)")
            else:
                print("❌ Dashboard did not redirect to login (authentication bypassed)")
                print(f"Result type: {type(result)}")
        except Exception as e:
            print(f"❌ Dashboard access error: {e}")

if __name__ == "__main__":
    print("🧪 Authentication Debug Test")
    print("=" * 50)

    test_auth_status()
    test_dashboard_access()

    print("\n" + "=" * 50)
    print("✅ Debug test completed")

