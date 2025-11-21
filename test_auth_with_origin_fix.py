#!/usr/bin/env python3
"""
Test ClubOS authentication with Origin header fix
"""

import sys
import os

# Add workspace root to path
workspace_root = os.path.abspath(os.path.dirname(__file__))
if workspace_root not in sys.path:
    sys.path.insert(0, workspace_root)

from src.services.authentication.unified_auth_service import UnifiedAuthService

def test_clubos_auth():
    """Test ClubOS authentication with Origin header fix"""
    print("Testing ClubOS Authentication with Origin Header Fix")
    print("=" * 60)

    # Initialize auth service
    auth_service = UnifiedAuthService()

    # Test credentials from config
    from config.clubhub_credentials import CLUBOS_USERNAME, CLUBOS_PASSWORD

    print(f"Username: {CLUBOS_USERNAME}")
    print(f"Password: {'*' * len(CLUBOS_PASSWORD)}")
    print()

    # Attempt authentication
    print("Attempting authentication...")
    session = auth_service.authenticate_clubos(
        username=CLUBOS_USERNAME,
        password=CLUBOS_PASSWORD
    )

    if session and session.authenticated:
        print("SUCCESS - AUTHENTICATION SUCCESSFUL!")
        print(f"User ID: {session.logged_in_user_id}")
        print(f"Session ID: {session.session_id[:20]}..." if session.session_id else "None")
        print(f"Bearer Token: {session.bearer_token[:30]}..." if session.bearer_token else "None")
        return True
    else:
        print("FAILED - AUTHENTICATION FAILED")
        print("Please check credentials or account status")
        return False

if __name__ == '__main__':
    success = test_clubos_auth()
    sys.exit(0 if success else 1)
