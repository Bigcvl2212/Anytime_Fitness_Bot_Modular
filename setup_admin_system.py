#!/usr/bin/env python3
"""
Admin System Setup Script
Initialize the admin system and create the first admin user
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

def setup_admin_system():
    """Set up the admin system"""
    try:
        logger.info("Setting up admin system...")

        # Set environment variable to use SQLite for testing
        os.environ['DB_TYPE'] = 'sqlite'
        os.environ['LOCAL_DEVELOPMENT'] = 'true'

        # Import required modules
        from src.services.database_manager import DatabaseManager
        from src.services.admin_auth_service import AdminAuthService
        from src.services.authentication.secure_secrets_manager import SecureSecretsManager

        # Initialize database manager
        db_manager = DatabaseManager()
        logger.info("Database manager initialized")

        # Initialize secrets manager (optional)
        try:
            secrets_manager = SecureSecretsManager()
            logger.info("Secrets manager initialized")
        except Exception as e:
            logger.warning(f"Could not initialize secrets manager: {e}")
            secrets_manager = None

        # Initialize admin service
        admin_service = AdminAuthService(db_manager, secrets_manager)
        logger.info("Admin service initialized")

        # Initialize admin system (create tables and default admin)
        success = admin_service.initialize_admin_system()

        if success:
            logger.info("Admin system setup completed successfully!")

            # Check if default admin was created
            default_admin_username = os.getenv('DEFAULT_ADMIN_USERNAME', 'admin')
            default_admin_email = os.getenv('DEFAULT_ADMIN_EMAIL', 'admin@gym-bot.local')

            # Generate manager ID for default admin
            import hashlib
            combined = f"{default_admin_username.lower()}:{default_admin_email.lower()}"
            hash_object = hashlib.sha256(combined.encode())
            manager_id = hash_object.hexdigest()[:16]

            admin_user = admin_service.admin_schema.get_admin_user(manager_id)
            if admin_user:
                logger.info("Default admin user found:")
                logger.info(f"   Username: {admin_user['username']}")
                logger.info(f"   Email: {admin_user['email']}")
                logger.info(f"   Manager ID: {admin_user['manager_id']}")
                logger.info(f"   Super Admin: {'Yes' if admin_user.get('is_super_admin') else 'No'}")
            else:
                logger.warning("Default admin user not found")

            return True
        else:
            logger.error("Admin system setup failed")
            return False

    except Exception as e:
        logger.error(f"Error setting up admin system: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

def create_custom_admin():
    """Create a custom admin user"""
    try:
        logger.info("Creating custom admin user...")

        # Get user input
        username = input("Enter admin username: ").strip()
        email = input("Enter admin email: ").strip()
        is_super_admin = input("Make super admin? (y/N): ").strip().lower() == 'y'

        if not username or not email:
            logger.error("Username and email are required")
            return False

        # Import required modules
        from src.services.database_manager import DatabaseManager
        from src.services.admin_auth_service import AdminAuthService
        from src.services.authentication.secure_secrets_manager import SecureSecretsManager

        # Initialize services
        db_manager = DatabaseManager()
        try:
            secrets_manager = SecureSecretsManager()
        except:
            secrets_manager = None

        admin_service = AdminAuthService(db_manager, secrets_manager)

        # Generate manager ID
        import hashlib
        combined = f"{username.lower()}:{email.lower()}"
        hash_object = hashlib.sha256(combined.encode())
        manager_id = hash_object.hexdigest()[:16]

        # Create admin user
        success = admin_service.admin_schema.add_admin_user(
            manager_id=manager_id,
            username=username,
            email=email,
            is_super_admin=is_super_admin
        )

        if success:
            logger.info("Custom admin user created successfully!")
            logger.info(f"   Username: {username}")
            logger.info(f"   Email: {email}")
            logger.info(f"   Manager ID: {manager_id}")
            logger.info(f"   Super Admin: {'Yes' if is_super_admin else 'No'}")
            return True
        else:
            logger.error("Failed to create custom admin user")
            return False

    except Exception as e:
        logger.error(f"Error creating custom admin user: {e}")
        return False

def main():
    """Main function"""
    print("=" * 60)
    print("    Gym Bot Admin System Setup")
    print("=" * 60)
    print()

    if len(sys.argv) > 1 and sys.argv[1] == '--create-admin':
        # Create custom admin user
        success = create_custom_admin()
    else:
        # Set up admin system with default admin
        success = setup_admin_system()

    print()
    if success:
        print("SUCCESS: Admin system setup completed successfully!")
        print()
        print("Next steps:")
        print("1. Start your application: python run_dashboard.py")
        print("2. Log in with your existing credentials")
        print("3. Navigate to the admin panel using the sidebar")
        print("4. Use the admin interface to manage users and system settings")
        print()
        print("Notes:")
        print("- Admin users can access the admin panel via the sidebar")
        print("- Super admins have full access to all admin features")
        print("- Regular admins have limited permissions based on their role")
        print("- Admin actions are logged in the audit log")
    else:
        print("ERROR: Admin system setup failed. Please check the logs above.")
        print()
        print("Troubleshooting:")
        print("1. Make sure your database is accessible")
        print("2. Check that all required modules are installed")
        print("3. Verify your environment variables are set correctly")

    print()
    print("=" * 60)

if __name__ == '__main__':
    main()