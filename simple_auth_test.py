#!/usr/bin/env python3
"""
Simple authentication test without full app initialization
"""

def test_auth_service_directly():
    """Test the auth service without Flask context"""
    print("🔍 Testing authentication service directly...")

    try:
        from src.services.authentication.secure_auth_service import SecureAuthService
        auth_service = SecureAuthService()

        # Test session validation (should fail without Flask session)
        is_valid, manager_id = auth_service.validate_session()
        print(f"Auth service validation: is_valid={is_valid}, manager_id='{manager_id}'")

        if not is_valid:
            print("✅ Authentication correctly returns invalid when no session exists")
        else:
            print("❌ Authentication incorrectly returns valid without a session")

    except Exception as e:
        print(f"❌ Auth service test error: {e}")

def test_require_auth_decorator():
    """Test the require_auth decorator behavior"""
    print("\n🔍 Testing require_auth decorator...")

    try:
        from src.routes.auth import require_auth
        print("✅ require_auth decorator imported successfully")

        # Check if it's callable
        if callable(require_auth):
            print("✅ require_auth is callable")
        else:
            print("❌ require_auth is not callable")

    except Exception as e:
        print(f"❌ require_auth import error: {e}")

def check_session_config():
    """Check session configuration"""
    print("\n🔍 Checking session configuration...")

    try:
        import os
        print("Current working directory:", os.getcwd())
        print("Python path includes src:", 'src' in str(os.sys.path))

        # Check if session files exist
        import glob
        session_files = glob.glob('flask_session/*')
        print(f"Session files found: {len(session_files)}")

        if session_files:
            print("⚠️ Session files exist - these persist between restarts")
            for f in session_files[:3]:  # Show first 3
                print(f"   {f}")
        else:
            print("✅ No persistent session files found")

    except Exception as e:
        print(f"❌ Session config check error: {e}")

if __name__ == "__main__":
    print("🧪 Simple Authentication Test")
    print("=" * 50)

    test_auth_service_directly()
    test_require_auth_decorator()
    check_session_config()

    print("\n" + "=" * 50)
    print("✅ Simple test completed")

