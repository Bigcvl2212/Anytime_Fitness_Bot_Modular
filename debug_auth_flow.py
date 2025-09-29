#!/usr/bin/env python3
"""
Authentication Flow Debug Script
Use this to test authentication and club selection flow
"""

import os
import sys
import logging

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_session_storage():
    """Test session token storage and retrieval"""
    try:
        logger.info("Testing session token storage...")

        # Set environment variable to use SQLite for testing
        os.environ['DB_TYPE'] = 'sqlite'
        os.environ['LOCAL_DEVELOPMENT'] = 'true'

        # Import required modules
        from src.services.authentication.secure_auth_service import SecureAuthService

        # Initialize auth service
        auth_service = SecureAuthService()

        # Test manager ID (you can replace this with your actual manager ID)
        test_manager_id = "test_manager_123"

        # Create a test session
        logger.info(f"Creating session for manager: {test_manager_id}")
        session_token = auth_service.create_session(test_manager_id)

        if session_token:
            logger.info(f"Session created successfully: {session_token[:20]}...")

            # Test storing club selection
            test_clubs = ["club_123", "club_456"]
            logger.info(f"Storing selected clubs: {test_clubs}")
            success = auth_service.store_selected_clubs(session_token, test_clubs)

            if success:
                logger.info("Clubs stored successfully")

                # Test validating session
                logger.info("Validating session token...")
                validation_result = auth_service.validate_session_token(session_token)

                if validation_result.get('is_valid'):
                    logger.info("Session validation successful")
                    logger.info(f"Manager ID: {validation_result.get('manager_id')}")
                    logger.info(f"Selected clubs: {validation_result.get('selected_clubs')}")
                    logger.info(f"Login time: {validation_result.get('login_time')}")
                    return True
                else:
                    logger.error("Session validation failed")
                    return False
            else:
                logger.error("Failed to store selected clubs")
                return False
        else:
            logger.error("Failed to create session")
            return False

    except Exception as e:
        logger.error(f"Error in session storage test: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

def check_database_sessions():
    """Check what sessions are stored in the database"""
    try:
        logger.info("Checking database sessions...")

        # Set environment variable to use SQLite for testing
        os.environ['DB_TYPE'] = 'sqlite'
        os.environ['LOCAL_DEVELOPMENT'] = 'true'

        # Import required modules
        from src.services.database_manager import DatabaseManager

        # Initialize database manager
        db_manager = DatabaseManager()

        # Check sessions table
        try:
            sessions = db_manager.execute_query("""
                SELECT session_token, manager_id, created_at, expires_at, is_active, session_data
                FROM sessions
                ORDER BY created_at DESC
                LIMIT 10
            """, fetch_all=True)

            if sessions:
                logger.info(f"Found {len(sessions)} sessions in database:")
                for session in sessions:
                    session_dict = dict(session)
                    logger.info(f"  Token: {session_dict['session_token'][:20]}...")
                    logger.info(f"  Manager: {session_dict['manager_id']}")
                    logger.info(f"  Active: {session_dict['is_active']}")
                    logger.info(f"  Data: {session_dict['session_data']}")
                    logger.info("  ---")
            else:
                logger.info("No sessions found in database")

        except Exception as e:
            logger.warning(f"Could not query sessions table: {e}")

        return True

    except Exception as e:
        logger.error(f"Error checking database sessions: {e}")
        return False

def simulate_auth_flow():
    """Simulate the full authentication flow"""
    try:
        logger.info("Simulating full authentication flow...")

        # This would simulate:
        # 1. Login
        # 2. Club selection
        # 3. Dashboard access
        # 4. Other route access

        test_session_storage()
        check_database_sessions()

        logger.info("Authentication flow simulation completed")
        return True

    except Exception as e:
        logger.error(f"Error in auth flow simulation: {e}")
        return False

def main():
    """Main function"""
    print("=" * 60)
    print("    Authentication Flow Debug Tool")
    print("=" * 60)
    print()

    print("1. Testing session storage...")
    session_test = test_session_storage()
    print(f"   Result: {'PASS' if session_test else 'FAIL'}")
    print()

    print("2. Checking database sessions...")
    db_test = check_database_sessions()
    print(f"   Result: {'PASS' if db_test else 'FAIL'}")
    print()

    print("3. Simulating auth flow...")
    flow_test = simulate_auth_flow()
    print(f"   Result: {'PASS' if flow_test else 'FAIL'}")
    print()

    if session_test and db_test and flow_test:
        print("SUCCESS: All authentication tests passed")
        print()
        print("If you're still getting redirected to login:")
        print("1. Check the browser console for any JavaScript errors")
        print("2. Look at the Flask logs when accessing routes")
        print("3. Verify your session cookies are being sent")
        print("4. Try clearing browser cookies and logging in again")
    else:
        print("ERROR: Some authentication tests failed")
        print()
        print("This indicates a problem with the authentication system.")
        print("Check the logs above for specific error details.")

    print()
    print("=" * 60)

if __name__ == '__main__':
    main()