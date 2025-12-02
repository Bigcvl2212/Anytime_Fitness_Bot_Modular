#!/usr/bin/env python3
"""
Admin Database Schema
Creates and manages admin-specific database tables for the admin account system
"""

import logging
import os
from datetime import datetime
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class AdminDatabaseSchema:
    """Manages admin-specific database tables and operations"""

    def __init__(self, db_manager):
        """
        Initialize with database manager

        Args:
            db_manager: DatabaseManager instance
        """
        self.db_manager = db_manager

    def create_admin_tables(self):
        """Create all admin-related database tables"""
        try:
            logger.info("🔧 Creating admin database tables...")

            # Create admin users table
            self._create_admin_users_table()

            # Create admin sessions table
            self._create_admin_sessions_table()

            # Create audit log table
            self._create_audit_log_table()

            # Create system monitoring table
            self._create_system_monitoring_table()

            # Create admin settings table
            self._create_admin_settings_table()

            # Run migrations for existing tables
            self._run_migrations()

            logger.info("✅ All admin tables created successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Error creating admin tables: {e}")
            return False

    def _run_migrations(self):
        """Run database migrations to add missing columns"""
        try:
            # Check if password_hash column exists, add if missing
            with self.db_manager.get_cursor() as cursor:
                # Check if column exists
                if self.db_manager.db_type == 'postgresql':
                    cursor.execute("""
                        SELECT column_name
                        FROM information_schema.columns
                        WHERE table_name='admin_users' AND column_name='password_hash'
                    """)
                    result = cursor.fetchone()

                    if not result:
                        cursor.execute("ALTER TABLE admin_users ADD COLUMN password_hash TEXT")
                        cursor.connection.commit()
                        logger.info("✅ Added password_hash column to admin_users table")
                else:  # SQLite
                    cursor.execute("PRAGMA table_info(admin_users)")
                    columns = [row[1] for row in cursor.fetchall()]

                    if 'password_hash' not in columns:
                        cursor.execute("ALTER TABLE admin_users ADD COLUMN password_hash TEXT")
                        cursor.connection.commit()
                        logger.info("✅ Added password_hash column to admin_users table")

        except Exception as e:
            logger.warning(f"⚠️ Migration warning (may be safe to ignore): {e}")

    def _create_admin_users_table(self):
        """Create admin users table"""
        if self.db_manager.db_type == 'postgresql':
            create_sql = """
                CREATE TABLE IF NOT EXISTS admin_users (
                    id SERIAL PRIMARY KEY,
                    manager_id TEXT UNIQUE NOT NULL,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT,
                    is_admin BOOLEAN DEFAULT FALSE,
                    is_super_admin BOOLEAN DEFAULT FALSE,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    login_attempts INTEGER DEFAULT 0,
                    account_locked_until TIMESTAMP,
                    permissions JSONB DEFAULT '{}',
                    settings JSONB DEFAULT '{}'
                )
            """
        else:  # SQLite
            create_sql = """
                CREATE TABLE IF NOT EXISTS admin_users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    manager_id TEXT UNIQUE NOT NULL,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT,
                    is_admin INTEGER DEFAULT 0,
                    is_super_admin INTEGER DEFAULT 0,
                    is_active INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    login_attempts INTEGER DEFAULT 0,
                    account_locked_until TIMESTAMP,
                    permissions TEXT DEFAULT '{}',
                    settings TEXT DEFAULT '{}'
                )
            """

        with self.db_manager.get_cursor() as cursor:
            cursor.execute(create_sql)
            cursor.connection.commit()
        logger.info("✅ Admin users table created")

    def _create_admin_sessions_table(self):
        """Create admin sessions table for session management"""
        if self.db_manager.db_type == 'postgresql':
            create_sql = """
                CREATE TABLE IF NOT EXISTS admin_sessions (
                    id SERIAL PRIMARY KEY,
                    session_token TEXT UNIQUE NOT NULL,
                    manager_id TEXT NOT NULL,
                    ip_address TEXT,
                    user_agent TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    session_data JSONB DEFAULT '{}'
                )
            """
        else:  # SQLite
            create_sql = """
                CREATE TABLE IF NOT EXISTS admin_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_token TEXT UNIQUE NOT NULL,
                    manager_id TEXT NOT NULL,
                    ip_address TEXT,
                    user_agent TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL,
                    is_active INTEGER DEFAULT 1,
                    session_data TEXT DEFAULT '{}'
                )
            """

        with self.db_manager.get_cursor() as cursor:
            cursor.execute(create_sql)
            cursor.connection.commit()
        logger.info("✅ Admin sessions table created")

    def _create_audit_log_table(self):
        """Create audit log table for tracking admin actions"""
        if self.db_manager.db_type == 'postgresql':
            create_sql = """
                CREATE TABLE IF NOT EXISTS audit_log (
                    id SERIAL PRIMARY KEY,
                    admin_user_id TEXT NOT NULL,
                    action TEXT NOT NULL,
                    target_type TEXT,
                    target_id TEXT,
                    description TEXT,
                    ip_address TEXT,
                    user_agent TEXT,
                    success BOOLEAN DEFAULT TRUE,
                    error_message TEXT,
                    request_data JSONB,
                    response_data JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
        else:  # SQLite
            create_sql = """
                CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    admin_user_id TEXT NOT NULL,
                    action TEXT NOT NULL,
                    target_type TEXT,
                    target_id TEXT,
                    description TEXT,
                    ip_address TEXT,
                    user_agent TEXT,
                    success INTEGER DEFAULT 1,
                    error_message TEXT,
                    request_data TEXT,
                    response_data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """

        with self.db_manager.get_cursor() as cursor:
            cursor.execute(create_sql)
            cursor.connection.commit()
        logger.info("✅ Audit log table created")

    def _create_system_monitoring_table(self):
        """Create system monitoring table for health checks"""
        if self.db_manager.db_type == 'postgresql':
            create_sql = """
                CREATE TABLE IF NOT EXISTS system_monitoring (
                    id SERIAL PRIMARY KEY,
                    check_type TEXT NOT NULL,
                    component TEXT NOT NULL,
                    status TEXT NOT NULL,
                    message TEXT,
                    response_time_ms INTEGER,
                    details JSONB,
                    checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
        else:  # SQLite
            create_sql = """
                CREATE TABLE IF NOT EXISTS system_monitoring (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    check_type TEXT NOT NULL,
                    component TEXT NOT NULL,
                    status TEXT NOT NULL,
                    message TEXT,
                    response_time_ms INTEGER,
                    details TEXT,
                    checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """

        with self.db_manager.get_cursor() as cursor:
            cursor.execute(create_sql)
            cursor.connection.commit()
        logger.info("✅ System monitoring table created")

    def _create_admin_settings_table(self):
        """Create admin settings table for system configuration"""
        if self.db_manager.db_type == 'postgresql':
            create_sql = """
                CREATE TABLE IF NOT EXISTS admin_settings (
                    id SERIAL PRIMARY KEY,
                    setting_key TEXT UNIQUE NOT NULL,
                    setting_value TEXT,
                    setting_type TEXT DEFAULT 'string',
                    category TEXT DEFAULT 'general',
                    description TEXT,
                    is_encrypted BOOLEAN DEFAULT FALSE,
                    is_public BOOLEAN DEFAULT FALSE,
                    created_by TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
        else:  # SQLite
            create_sql = """
                CREATE TABLE IF NOT EXISTS admin_settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    setting_key TEXT UNIQUE NOT NULL,
                    setting_value TEXT,
                    setting_type TEXT DEFAULT 'string',
                    category TEXT DEFAULT 'general',
                    description TEXT,
                    is_encrypted INTEGER DEFAULT 0,
                    is_public INTEGER DEFAULT 0,
                    created_by TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """

        with self.db_manager.get_cursor() as cursor:
            cursor.execute(create_sql)
            cursor.connection.commit()
        logger.info("✅ Admin settings table created")

    def add_admin_user(self, manager_id: str, username: str, email: str, is_super_admin: bool = False, password_hash: str = None) -> bool:
        """
        Add a new admin user to the system

        Args:
            manager_id: Unique manager ID
            username: Username
            email: Email address
            is_super_admin: Whether user is a super admin
            password_hash: Hashed password (optional)

        Returns:
            True if successful, False otherwise
        """
        try:
            with self.db_manager.get_cursor() as cursor:
                if self.db_manager.db_type == 'postgresql':
                    cursor.execute("""
                        INSERT INTO admin_users (manager_id, username, email, is_admin, is_super_admin, password_hash)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON CONFLICT (manager_id) DO UPDATE SET
                            username = EXCLUDED.username,
                            email = EXCLUDED.email,
                            is_admin = TRUE,
                            is_super_admin = EXCLUDED.is_super_admin,
                            password_hash = COALESCE(EXCLUDED.password_hash, admin_users.password_hash),
                            updated_at = CURRENT_TIMESTAMP
                    """, (manager_id, username, email, True, is_super_admin, password_hash))
                else:  # SQLite
                    cursor.execute("""
                        INSERT OR REPLACE INTO admin_users (manager_id, username, email, is_admin, is_super_admin, password_hash)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (manager_id, username, email, 1, 1 if is_super_admin else 0, password_hash))

                cursor.connection.commit()

            logger.info(f"✅ Admin user added/updated: {username} ({email})")
            return True

        except Exception as e:
            logger.error(f"❌ Error adding admin user: {e}")
            return False

    def get_admin_user(self, manager_id: str) -> Optional[Dict[str, Any]]:
        """
        Get admin user by manager ID

        Args:
            manager_id: Manager ID to look up

        Returns:
            Admin user data or None if not found
        """
        try:
            result = self.db_manager.execute_query("""
                SELECT * FROM admin_users WHERE manager_id = ?
            """, (manager_id,), fetch_one=True)

            return dict(result) if result else None

        except Exception as e:
            logger.error(f"❌ Error getting admin user: {e}")
            return None

    def get_admin_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Get admin user by username

        Args:
            username: Username to look up

        Returns:
            Admin user data or None if not found
        """
        try:
            result = self.db_manager.execute_query("""
                SELECT * FROM admin_users WHERE username = ?
            """, (username,), fetch_one=True)

            return dict(result) if result else None

        except Exception as e:
            logger.error(f"❌ Error getting admin user by username: {e}")
            return None

    def log_admin_action(self, admin_user_id: str, action: str, description: str,
                        target_type: str = None, target_id: str = None,
                        ip_address: str = None, success: bool = True,
                        error_message: str = None, request_data: Dict = None,
                        response_data: Dict = None) -> bool:
        """
        Log an admin action to the audit log

        Args:
            admin_user_id: ID of admin user performing action
            action: Action performed
            description: Description of the action
            target_type: Type of target (member, system, etc.)
            target_id: ID of target
            ip_address: IP address of admin
            success: Whether action was successful
            error_message: Error message if failed
            request_data: Request data
            response_data: Response data

        Returns:
            True if logged successfully, False otherwise
        """
        try:
            import json

            with self.db_manager.get_cursor() as cursor:
                if self.db_manager.db_type == 'postgresql':
                    cursor.execute("""
                        INSERT INTO audit_log (
                            admin_user_id, action, target_type, target_id, description,
                            ip_address, success, error_message, request_data, response_data
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        admin_user_id, action, target_type, target_id, description,
                        ip_address, success, error_message,
                        json.dumps(request_data) if request_data else None,
                        json.dumps(response_data) if response_data else None
                    ))
                else:  # SQLite
                    cursor.execute("""
                        INSERT INTO audit_log (
                            admin_user_id, action, target_type, target_id, description,
                            ip_address, success, error_message, request_data, response_data
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        admin_user_id, action, target_type, target_id, description,
                        ip_address, 1 if success else 0, error_message,
                        json.dumps(request_data) if request_data else None,
                        json.dumps(response_data) if response_data else None
                    ))
                cursor.connection.commit()

            return True

        except Exception as e:
            logger.error(f"❌ Error logging admin action: {e}")
            return False

    def update_admin_user(self, manager_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update admin user details

        Args:
            manager_id: Manager ID of user to update
            updates: Dictionary of fields to update

        Returns:
            True if successful, False otherwise
        """
        try:
            if not updates:
                return True

            # Build dynamic update query
            set_clauses = []
            values = []

            for field, value in updates.items():
                if field in ['username', 'email', 'password_hash', 'is_admin', 'is_super_admin', 'is_active', 'permissions', 'settings']:
                    set_clauses.append(f"{field} = ?")

                    # Handle JSON fields
                    if field in ['permissions', 'settings'] and isinstance(value, dict):
                        import json
                        values.append(json.dumps(value))
                    # Handle boolean fields for SQLite
                    elif field in ['is_admin', 'is_super_admin', 'is_active'] and self.db_manager.db_type != 'postgresql':
                        values.append(1 if value else 0)
                    else:
                        values.append(value)

            if not set_clauses:
                return True

            # Add updated_at timestamp
            set_clauses.append("updated_at = CURRENT_TIMESTAMP")
            values.append(manager_id)

            query = f"UPDATE admin_users SET {', '.join(set_clauses)} WHERE manager_id = ?"

            with self.db_manager.get_cursor() as cursor:
                cursor.execute(query, values)
                cursor.connection.commit()
                rows_affected = cursor.rowcount

            if rows_affected > 0:
                logger.info(f"✅ Admin user updated: {manager_id}")
                return True
            else:
                logger.warning(f"⚠️ No admin user found with manager_id: {manager_id}")
                return False

        except Exception as e:
            logger.error(f"❌ Error updating admin user: {e}")
            return False

    def reset_user_access(self, manager_id: str) -> bool:
        """
        Reset user access by clearing login attempts and unlocking account

        Args:
            manager_id: Manager ID of user to reset

        Returns:
            True if successful, False otherwise
        """
        try:
            with self.db_manager.get_cursor() as cursor:
                cursor.execute("""
                    UPDATE admin_users
                    SET login_attempts = 0,
                        account_locked_until = NULL,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE manager_id = ?
                """, (manager_id,))
                cursor.connection.commit()
                rows_affected = cursor.rowcount

            if rows_affected > 0:
                logger.info(f"✅ User access reset for: {manager_id}")
                return True
            else:
                logger.warning(f"⚠️ No admin user found with manager_id: {manager_id}")
                return False

        except Exception as e:
            logger.error(f"❌ Error resetting user access: {e}")
            return False

    def get_all_admin_users(self) -> list:
        """
        Get all admin users for management interface

        Returns:
            List of admin user records
        """
        try:
            results = self.db_manager.execute_query("""
                SELECT id, manager_id, username, email, is_admin, is_super_admin,
                       is_active, created_at, updated_at, last_login, login_attempts,
                       account_locked_until, permissions, settings
                FROM admin_users
                ORDER BY created_at DESC
            """, fetch_all=True)

            # Handle None or empty results
            if not results:
                return []

            users = []
            for row in results:
                user = dict(row)

                # Parse JSON fields
                import json
                try:
                    user['permissions'] = json.loads(user['permissions']) if user['permissions'] else {}
                except (json.JSONDecodeError, TypeError):
                    user['permissions'] = {}

                try:
                    user['settings'] = json.loads(user['settings']) if user['settings'] else {}
                except (json.JSONDecodeError, TypeError):
                    user['settings'] = {}

                users.append(user)

            return users

        except Exception as e:
            logger.error(f"❌ Error getting all admin users: {e}")
            return []

    def delete_admin_user(self, manager_id: str) -> bool:
        """
        Delete admin user from the system

        Args:
            manager_id: Manager ID of user to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            with self.db_manager.get_cursor() as cursor:
                # First check if user exists
                cursor.execute("SELECT username FROM admin_users WHERE manager_id = ?", (manager_id,))
                user = cursor.fetchone()

                if not user:
                    logger.warning(f"⚠️ No admin user found with manager_id: {manager_id}")
                    return False

                username = user[0]

                # Delete the user
                cursor.execute("DELETE FROM admin_users WHERE manager_id = ?", (manager_id,))
                cursor.connection.commit()
                rows_affected = cursor.rowcount

            if rows_affected > 0:
                logger.info(f"✅ Admin user deleted: {username} ({manager_id})")
                return True
            else:
                logger.warning(f"⚠️ Failed to delete admin user: {manager_id}")
                return False

        except Exception as e:
            logger.error(f"❌ Error deleting admin user: {e}")
            return False