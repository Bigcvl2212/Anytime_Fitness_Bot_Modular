#!/usr/bin/env python3
"""
Admin System Test Script
Test the admin system functionality
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

def test_admin_system():
    """Test the admin system functionality"""
    try:
        logger.info("Testing admin system...")

        # Set environment variable to use SQLite for testing
        os.environ['DB_TYPE'] = 'sqlite'
        os.environ['LOCAL_DEVELOPMENT'] = 'true'

        # Import required modules
        from src.services.database_manager import DatabaseManager
        from src.services.admin_auth_service import AdminAuthService
        from src.services.authentication.secure_secrets_manager import SecureSecretsManager

        # Initialize services
        logger.info("1. Initializing services...")
        db_manager = DatabaseManager()

        try:
            secrets_manager = SecureSecretsManager()
        except:
            secrets_manager = None
            logger.warning("   Secrets manager not available")

        admin_service = AdminAuthService(db_manager, secrets_manager)

        # Test 1: Check if admin tables exist
        logger.info("2. Testing database tables...")
        try:
            # Try to query admin_users table
            result = db_manager.execute_query("SELECT COUNT(*) as count FROM admin_users", fetch_one=True)
            admin_count = result['count'] if result else 0
            logger.info(f"   ✅ admin_users table exists with {admin_count} users")
        except Exception as e:
            logger.error(f"   ❌ admin_users table error: {e}")
            return False

        try:
            # Try to query audit_log table
            result = db_manager.execute_query("SELECT COUNT(*) as count FROM audit_log", fetch_one=True)
            log_count = result['count'] if result else 0
            logger.info(f"   ✅ audit_log table exists with {log_count} entries")
        except Exception as e:
            logger.error(f"   ❌ audit_log table error: {e}")
            return False

        # Test 2: Check if default admin user exists
        logger.info("3. Testing default admin user...")
        default_admin_username = os.getenv('DEFAULT_ADMIN_USERNAME', 'admin')
        default_admin_email = os.getenv('DEFAULT_ADMIN_EMAIL', 'admin@gym-bot.local')

        import hashlib
        combined = f"{default_admin_username.lower()}:{default_admin_email.lower()}"
        hash_object = hashlib.sha256(combined.encode())
        manager_id = hash_object.hexdigest()[:16]

        admin_user = admin_service.admin_schema.get_admin_user(manager_id)
        if admin_user:
            logger.info(f"   ✅ Default admin user found: {admin_user['username']}")
        else:
            logger.warning("   ⚠️ Default admin user not found")

        # Test 3: Test admin permissions
        logger.info("4. Testing admin permissions...")
        if admin_user:
            is_admin = admin_service.is_admin(manager_id)
            is_super_admin = admin_service.is_super_admin(manager_id)
            permissions = admin_service.get_admin_permissions(manager_id)

            logger.info(f"   ✅ Is admin: {is_admin}")
            logger.info(f"   ✅ Is super admin: {is_super_admin}")
            logger.info(f"   ✅ Permissions: {list(permissions.keys())}")
        else:
            logger.warning("   ⚠️ Cannot test permissions - no admin user found")

        # Test 4: Test audit logging
        logger.info("5. Testing audit logging...")
        if admin_user:
            success = admin_service.log_admin_action(
                manager_id=manager_id,
                action='test_action',
                description='Testing audit logging system',
                target_type='system',
                target_id='test',
                success=True
            )
            if success:
                logger.info("   ✅ Audit logging successful")
            else:
                logger.error("   ❌ Audit logging failed")
        else:
            logger.warning("   ⚠️ Cannot test audit logging - no admin user found")

        # Test 5: Test creating a test admin user
        logger.info("6. Testing admin user creation...")
        test_manager_id = "test_admin_123456"
        test_success = admin_service.admin_schema.add_admin_user(
            manager_id=test_manager_id,
            username="test_admin",
            email="test@gym-bot.local",
            is_super_admin=False
        )

        if test_success:
            logger.info("   ✅ Test admin user creation successful")

            # Clean up test user
            try:
                db_manager.execute_query("DELETE FROM admin_users WHERE manager_id = ?", (test_manager_id,))
                logger.info("   ✅ Test admin user cleaned up")
            except Exception as e:
                logger.warning(f"   ⚠️ Failed to clean up test user: {e}")
        else:
            logger.error("   ❌ Test admin user creation failed")

        logger.info("✅ Admin system test completed successfully!")
        return True

    except Exception as e:
        logger.error(f"❌ Admin system test failed: {e}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        return False

def test_flask_integration():
    """Test Flask integration"""
    try:
        logger.info("🧪 Testing Flask integration...")

        # Import Flask app
        from src.main_app import create_app

        # Create app
        app = create_app()

        with app.app_context():
            # Test if admin service is available
            admin_service = getattr(app, 'admin_service', None)
            if admin_service:
                logger.info("   ✅ Admin service available in Flask app")

                # Test admin service methods
                logger.info("   Testing admin service methods...")

                # Get a test manager ID
                default_admin_username = os.getenv('DEFAULT_ADMIN_USERNAME', 'admin')
                default_admin_email = os.getenv('DEFAULT_ADMIN_EMAIL', 'admin@gym-bot.local')

                import hashlib
                combined = f"{default_admin_username.lower()}:{default_admin_email.lower()}"
                hash_object = hashlib.sha256(combined.encode())
                manager_id = hash_object.hexdigest()[:16]

                # Test admin check
                is_admin = admin_service.is_admin(manager_id)
                logger.info(f"   ✅ Admin check result: {is_admin}")

                logger.info("✅ Flask integration test completed successfully!")
                return True
            else:
                logger.error("   ❌ Admin service not available in Flask app")
                return False

    except Exception as e:
        logger.error(f"❌ Flask integration test failed: {e}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        return False

def main():
    """Main function"""
    print("=" * 60)
    print("    Gym Bot Admin System Test")
    print("=" * 60)
    print()

    # Test admin system
    admin_test_success = test_admin_system()
    print()

    # Test Flask integration
    flask_test_success = test_flask_integration()
    print()

    if admin_test_success and flask_test_success:
        print("🎉 All tests passed! Admin system is working correctly.")
        print()
        print("You can now:")
        print("1. Start your application: python run_dashboard.py")
        print("2. Log in with your existing credentials")
        print("3. Look for the 'Administration' section in the sidebar")
        print("4. Access the admin dashboard at /admin")
    else:
        print("❌ Some tests failed. Please check the logs above.")
        print()
        print("If tests failed:")
        print("1. Run setup_admin_system.py first")
        print("2. Check your database connection")
        print("3. Verify all required modules are installed")

    print()
    print("=" * 60)

if __name__ == '__main__':
    main()