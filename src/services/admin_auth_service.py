#!/usr/bin/env python3
"""
Admin Authentication Service
Handles admin user authentication, authorization, and session management
"""

import logging
import secrets
import hashlib
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from functools import wraps
from flask import session, request, redirect, url_for, current_app, jsonify

from .admin_database_schema import AdminDatabaseSchema

logger = logging.getLogger(__name__)

class AdminAuthService:
    """Admin authentication and authorization service"""

    def __init__(self, db_manager, secrets_manager=None):
        """
        Initialize admin auth service

        Args:
            db_manager: DatabaseManager instance
            secrets_manager: SecureSecretsManager instance (optional)
        """
        self.db_manager = db_manager
        self.secrets_manager = secrets_manager
        self.admin_schema = AdminDatabaseSchema(db_manager)
        self.session_timeout = timedelta(hours=8)

    def initialize_admin_system(self):
        """Initialize the admin system and create default admin user"""
        try:
            logger.info("🔧 Initializing admin system...")

            # Create admin tables
            self.admin_schema.create_admin_tables()

            # Create default super admin if none exists
            self._create_default_admin()

            logger.info("✅ Admin system initialized successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Error initializing admin system: {e}")
            return False

    def _create_default_admin(self):
        """Create default super admin user"""
        try:
            # Check if any admin users exist
            existing_admins = self.db_manager.execute_query("""
                SELECT COUNT(*) as count FROM admin_users WHERE is_admin = ?
            """, (1 if self.db_manager.db_type == 'sqlite' else True,), fetch_one=True)

            if existing_admins and existing_admins['count'] > 0:
                logger.info("ℹ️ Admin users already exist, skipping default admin creation")
                return

            # Create default admin from environment or use hardcoded values
            import os
            default_username = os.getenv('DEFAULT_ADMIN_USERNAME', 'admin')
            default_email = os.getenv('DEFAULT_ADMIN_EMAIL', 'admin@gym-bot.local')

            # Generate manager ID for default admin
            manager_id = self._generate_manager_id(default_username, default_email)

            # Add default super admin
            success = self.admin_schema.add_admin_user(
                manager_id=manager_id,
                username=default_username,
                email=default_email,
                is_super_admin=True
            )

            if success:
                logger.info(f"✅ Default super admin created: {default_username}")
            else:
                logger.error("❌ Failed to create default super admin")

        except Exception as e:
            logger.error(f"❌ Error creating default admin: {e}")

    def _generate_manager_id(self, username: str, email: str) -> str:
        """Generate unique manager ID from username and email"""
        combined = f"{username.lower()}:{email.lower()}"
        hash_object = hashlib.sha256(combined.encode())
        return hash_object.hexdigest()[:16]

    def is_admin(self, manager_id: str) -> bool:
        """
        Check if a manager ID belongs to an admin user

        Args:
            manager_id: Manager ID to check

        Returns:
            True if user is admin, False otherwise
        """
        try:
            admin_user = self.admin_schema.get_admin_user(manager_id)
            if not admin_user:
                return False

            # Check if user is admin and account is active
            is_admin = admin_user.get('is_admin', False)
            is_active = admin_user.get('is_active', False)

            # Handle boolean values for different database types
            if self.db_manager.db_type == 'sqlite':
                is_admin = bool(is_admin)
                is_active = bool(is_active)

            return is_admin and is_active

        except Exception as e:
            logger.error(f"❌ Error checking admin status: {e}")
            return False

    def is_super_admin(self, manager_id: str) -> bool:
        """
        Check if a manager ID belongs to a super admin user

        Args:
            manager_id: Manager ID to check

        Returns:
            True if user is super admin, False otherwise
        """
        try:
            admin_user = self.admin_schema.get_admin_user(manager_id)
            if not admin_user:
                return False

            # Check if user is super admin and account is active
            is_super_admin = admin_user.get('is_super_admin', False)
            is_active = admin_user.get('is_active', False)

            # Handle boolean values for different database types
            if self.db_manager.db_type == 'sqlite':
                is_super_admin = bool(is_super_admin)
                is_active = bool(is_active)

            return is_super_admin and is_active

        except Exception as e:
            logger.error(f"❌ Error checking super admin status: {e}")
            return False

    def get_admin_permissions(self, manager_id: str) -> Dict[str, Any]:
        """
        Get admin user permissions

        Args:
            manager_id: Manager ID

        Returns:
            Dictionary of permissions
        """
        try:
            admin_user = self.admin_schema.get_admin_user(manager_id)
            if not admin_user:
                return {}

            # Parse permissions JSON
            permissions_str = admin_user.get('permissions', '{}')
            if isinstance(permissions_str, str):
                permissions = json.loads(permissions_str)
            else:
                permissions = permissions_str or {}

            # Add default permissions based on admin level
            if self.is_super_admin(manager_id):
                permissions.update({
                    'user_management': True,
                    'system_settings': True,
                    'database_management': True,
                    'audit_logs': True,
                    'all_data_access': True
                })
            elif self.is_admin(manager_id):
                permissions.update({
                    'user_management': permissions.get('user_management', False),
                    'system_settings': permissions.get('system_settings', False),
                    'database_management': permissions.get('database_management', False),
                    'audit_logs': permissions.get('audit_logs', True),
                    'all_data_access': permissions.get('all_data_access', True)
                })

            return permissions

        except Exception as e:
            logger.error(f"❌ Error getting admin permissions: {e}")
            return {}

    def log_admin_action(self, manager_id: str, action: str, description: str,
                        target_type: str = None, target_id: str = None,
                        success: bool = True, error_message: str = None,
                        request_data: Dict = None, response_data: Dict = None):
        """
        Log an admin action

        Args:
            manager_id: Manager ID performing action
            action: Action performed
            description: Description of action
            target_type: Type of target
            target_id: ID of target
            success: Whether action was successful
            error_message: Error message if failed
            request_data: Request data
            response_data: Response data
        """
        try:
            ip_address = request.remote_addr if request else None

            self.admin_schema.log_admin_action(
                admin_user_id=manager_id,
                action=action,
                description=description,
                target_type=target_type,
                target_id=target_id,
                ip_address=ip_address,
                success=success,
                error_message=error_message,
                request_data=request_data,
                response_data=response_data
            )

        except Exception as e:
            logger.error(f"❌ Error logging admin action: {e}")

    def promote_to_admin(self, manager_id: str, target_manager_id: str, is_super_admin: bool = False) -> bool:
        """
        Promote a user to admin status

        Args:
            manager_id: Admin performing the promotion
            target_manager_id: User to promote
            is_super_admin: Whether to make super admin

        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if promoter has permission
            if not self.is_super_admin(manager_id):
                logger.warning(f"❌ User {manager_id} attempted to promote user without super admin privileges")
                self.log_admin_action(
                    manager_id, 'promote_user', f'Attempted to promote {target_manager_id}',
                    'user', target_manager_id, False, 'Insufficient privileges'
                )
                return False

            # Get target user info from existing auth system
            # We'll need to create the admin user record
            # For now, we'll create a basic record
            success = self.admin_schema.add_admin_user(
                manager_id=target_manager_id,
                username=f"user_{target_manager_id[:8]}",  # Placeholder username
                email=f"admin_{target_manager_id[:8]}@gym-bot.local",  # Placeholder email
                is_super_admin=is_super_admin
            )

            if success:
                self.log_admin_action(
                    manager_id, 'promote_user',
                    f'Promoted user {target_manager_id} to {"super admin" if is_super_admin else "admin"}',
                    'user', target_manager_id, True
                )
                logger.info(f"✅ User {target_manager_id} promoted to admin by {manager_id}")
                return True
            else:
                self.log_admin_action(
                    manager_id, 'promote_user', f'Failed to promote {target_manager_id}',
                    'user', target_manager_id, False, 'Database error'
                )
                return False

        except Exception as e:
            logger.error(f"❌ Error promoting user to admin: {e}")
            self.log_admin_action(
                manager_id, 'promote_user', f'Error promoting {target_manager_id}',
                'user', target_manager_id, False, str(e)
            )
            return False

def require_admin(f):
    """Decorator to require admin access for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # Get manager ID from session
            manager_id = session.get('manager_id')
            if not manager_id:
                logger.warning("❌ Admin route accessed without manager_id in session")
                return redirect(url_for('auth.login'))

            # Check if user is admin
            admin_service = getattr(current_app, 'admin_service', None)
            if not admin_service:
                logger.error("❌ Admin service not available")
                return redirect(url_for('auth.login'))

            if not admin_service.is_admin(manager_id):
                logger.warning(f"❌ Non-admin user {manager_id} attempted to access admin route")
                admin_service.log_admin_action(
                    manager_id, 'unauthorized_access',
                    f'Attempted to access admin route: {request.endpoint}',
                    'route', request.endpoint, False, 'Insufficient privileges'
                )
                return redirect(url_for('dashboard.dashboard'))

            # Log admin access
            admin_service.log_admin_action(
                manager_id, 'admin_access',
                f'Accessed admin route: {request.endpoint}',
                'route', request.endpoint, True
            )

            return f(*args, **kwargs)

        except Exception as e:
            logger.error(f"❌ Error in admin auth decorator: {e}")
            return redirect(url_for('auth.login'))

    return decorated_function

def require_super_admin(f):
    """Decorator to require super admin access for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # Get manager ID from session
            manager_id = session.get('manager_id')
            if not manager_id:
                logger.warning("❌ Super admin route accessed without manager_id in session")
                return redirect(url_for('auth.login'))

            # Check if user is super admin
            admin_service = getattr(current_app, 'admin_service', None)
            if not admin_service:
                logger.error("❌ Admin service not available")
                return redirect(url_for('auth.login'))

            if not admin_service.is_super_admin(manager_id):
                logger.warning(f"❌ Non-super-admin user {manager_id} attempted to access super admin route")
                admin_service.log_admin_action(
                    manager_id, 'unauthorized_access',
                    f'Attempted to access super admin route: {request.endpoint}',
                    'route', request.endpoint, False, 'Insufficient privileges'
                )
                return redirect(url_for('dashboard.dashboard'))

            # Log super admin access
            admin_service.log_admin_action(
                manager_id, 'super_admin_access',
                f'Accessed super admin route: {request.endpoint}',
                'route', request.endpoint, True
            )

            return f(*args, **kwargs)

        except Exception as e:
            logger.error(f"❌ Error in super admin auth decorator: {e}")
            return redirect(url_for('auth.login'))

    return decorated_function

def require_permission(permission: str):
    """Decorator to require specific permission for routes"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # Get manager ID from session
                manager_id = session.get('manager_id')
                if not manager_id:
                    logger.warning(f"❌ Route requiring permission '{permission}' accessed without manager_id")
                    return redirect(url_for('auth.login'))

                # Check if user has permission
                admin_service = getattr(current_app, 'admin_service', None)
                if not admin_service:
                    logger.error("❌ Admin service not available")
                    return redirect(url_for('auth.login'))

                permissions = admin_service.get_admin_permissions(manager_id)
                if not permissions.get(permission, False):
                    logger.warning(f"❌ User {manager_id} lacks permission '{permission}' for route")
                    admin_service.log_admin_action(
                        manager_id, 'permission_denied',
                        f'Lacks permission "{permission}" for route: {request.endpoint}',
                        'route', request.endpoint, False, f'Missing permission: {permission}'
                    )
                    return redirect(url_for('dashboard.dashboard'))

                # Log permission-based access
                admin_service.log_admin_action(
                    manager_id, 'permission_access',
                    f'Used permission "{permission}" for route: {request.endpoint}',
                    'route', request.endpoint, True
                )

                return f(*args, **kwargs)

            except Exception as e:
                logger.error(f"❌ Error in permission decorator: {e}")
                return redirect(url_for('auth.login'))

        return decorated_function
    return decorator

# API decorators for JSON responses
def require_admin_api(f):
    """Decorator to require admin access for API routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # Get manager ID from session
            manager_id = session.get('manager_id')
            if not manager_id:
                return jsonify({'success': False, 'error': 'Authentication required'}), 401

            # Check if user is admin
            admin_service = getattr(current_app, 'admin_service', None)
            if not admin_service:
                return jsonify({'success': False, 'error': 'Admin service unavailable'}), 500

            if not admin_service.is_admin(manager_id):
                admin_service.log_admin_action(
                    manager_id, 'unauthorized_api_access',
                    f'Attempted to access admin API: {request.endpoint}',
                    'api', request.endpoint, False, 'Insufficient privileges'
                )
                return jsonify({'success': False, 'error': 'Admin access required'}), 403

            return f(*args, **kwargs)

        except Exception as e:
            logger.error(f"❌ Error in admin API decorator: {e}")
            return jsonify({'success': False, 'error': 'Authentication error'}), 500

    return decorated_function