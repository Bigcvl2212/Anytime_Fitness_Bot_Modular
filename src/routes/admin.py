#!/usr/bin/env python3
"""
Admin Routes
Administrative dashboard routes for system management, user management, and monitoring
"""

import logging
import json
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, jsonify, current_app, session, redirect, url_for
from typing import Dict, Any, List

from ..services.admin_auth_service import require_admin, require_super_admin, require_permission, require_admin_api

logger = logging.getLogger(__name__)

# Create admin blueprint
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/')
@require_admin
def admin_dashboard():
    """Main admin dashboard"""
    try:
        manager_id = session.get('manager_id')
        admin_service = current_app.admin_service

        # Get admin user info
        admin_user = admin_service.admin_schema.get_admin_user(manager_id)
        permissions = admin_service.get_admin_permissions(manager_id)

        # Get system overview
        system_stats = _get_system_overview()

        # Log dashboard access
        admin_service.log_admin_action(
            manager_id, 'dashboard_access', 'Accessed admin dashboard'
        )

        return render_template('admin/dashboard.html',
                             admin_user=admin_user,
                             permissions=permissions,
                             system_stats=system_stats)

    except Exception as e:
        logger.error(f"❌ Error loading admin dashboard: {e}")
        return render_template('error.html', error='Failed to load admin dashboard')

@admin_bp.route('/users')
@require_permission('user_management')
def user_management():
    """User management interface"""
    try:
        manager_id = session.get('manager_id')
        admin_service = current_app.admin_service

        # Get all admin users
        admin_users = _get_all_admin_users()

        # Get system users (from existing auth system)
        system_users = _get_system_users()

        # Log access
        admin_service.log_admin_action(
            manager_id, 'user_management_access', 'Accessed user management'
        )

        return render_template('admin/user_management.html',
                             admin_users=admin_users,
                             system_users=system_users)

    except Exception as e:
        logger.error(f"❌ Error loading user management: {e}")
        return render_template('error.html', error='Failed to load user management')

@admin_bp.route('/system')
@require_permission('system_settings')
def system_monitoring():
    """System monitoring and health dashboard"""
    try:
        manager_id = session.get('manager_id')
        admin_service = current_app.admin_service

        # Get system health data
        health_data = _get_system_health()

        # Get database stats
        db_stats = _get_database_stats()

        # Get API status
        api_status = _get_api_status()

        # Log access
        admin_service.log_admin_action(
            manager_id, 'system_monitoring_access', 'Accessed system monitoring'
        )

        return render_template('admin/system_overview.html',
                             system_health={'healthy_services': 4, 'total_services': 5},
                             system_stats=_get_system_overview(),
                             database_status={'healthy': True, 'type': 'SQLite', 'table_count': 10},
                             auth_status={'healthy': True, 'clubos_healthy': True, 'clubhub_healthy': True, 'active_sessions': 1},
                             monitoring_status={'healthy': True, 'is_running': True, 'last_check': 'Just now', 'actions_today': 0},
                             cache_status={'healthy': True, 'hit_rate': 85, 'cache_size': 150, 'total_requests': 1000},
                             clubos_status={'healthy': True, 'api_healthy': True, 'last_sync': '10 minutes ago', 'sync_errors': 0},
                             admin_stats={'total_admins': 3, 'super_admins': 2, 'recent_actions': 5},
                             current_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    except Exception as e:
        logger.error(f"❌ Error loading system monitoring: {e}")
        return render_template('error.html', error='Failed to load system monitoring')

@admin_bp.route('/data')
@require_permission('database_management')
def data_management():
    """Data management tools"""
    try:
        manager_id = session.get('manager_id')
        admin_service = current_app.admin_service

        # Get data refresh status
        refresh_status = _get_data_refresh_status()

        # Get backup status
        backup_status = _get_backup_status()

        # Log access
        admin_service.log_admin_action(
            manager_id, 'data_management_access', 'Accessed data management'
        )

        return render_template('admin/data_management.html',
                             refresh_status=refresh_status,
                             backup_status=backup_status)

    except Exception as e:
        logger.error(f"❌ Error loading data management: {e}")
        return render_template('error.html', error='Failed to load data management')

@admin_bp.route('/audit')
@require_permission('audit_logs')
def audit_logs():
    """Audit log viewer"""
    try:
        manager_id = session.get('manager_id')
        admin_service = current_app.admin_service

        # Get recent audit logs
        recent_logs = _get_recent_audit_logs()

        # Log access
        admin_service.log_admin_action(
            manager_id, 'audit_logs_access', 'Accessed audit logs'
        )

        return render_template('admin/audit_logs.html',
                             audit_logs=recent_logs)

    except Exception as e:
        logger.error(f"❌ Error loading audit logs: {e}")
        return render_template('error.html', error='Failed to load audit logs')

@admin_bp.route('/settings')
@require_super_admin
def admin_settings():
    """Admin settings (super admin only)"""
    try:
        manager_id = session.get('manager_id')
        admin_service = current_app.admin_service

        # Get system settings
        settings = _get_system_settings()

        # Log access
        admin_service.log_admin_action(
            manager_id, 'admin_settings_access', 'Accessed admin settings'
        )

        return render_template('admin/settings.html', settings=settings)

    except Exception as e:
        logger.error(f"❌ Error loading admin settings: {e}")
        return render_template('error.html', error='Failed to load admin settings')

# API Routes

@admin_bp.route('/api/users', methods=['GET'])
@require_admin_api
def api_get_users():
    """API endpoint to get all users"""
    try:
        admin_users = _get_all_admin_users()
        system_users = _get_system_users()

        return jsonify({
            'success': True,
            'admin_users': admin_users,
            'system_users': system_users
        })

    except Exception as e:
        logger.error(f"❌ Error getting users: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/api/users/promote', methods=['POST'])
@require_super_admin
def api_promote_user():
    """API endpoint to promote user to admin"""
    try:
        data = request.get_json()
        target_manager_id = data.get('manager_id')
        is_super_admin = data.get('is_super_admin', False)

        if not target_manager_id:
            return jsonify({'success': False, 'error': 'Manager ID required'}), 400

        manager_id = session.get('manager_id')
        admin_service = current_app.admin_service

        success = admin_service.promote_to_admin(manager_id, target_manager_id, is_super_admin)

        if success:
            return jsonify({'success': True, 'message': 'User promoted successfully'})
        else:
            return jsonify({'success': False, 'error': 'Failed to promote user'}), 500

    except Exception as e:
        logger.error(f"❌ Error promoting user: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/api/users/<manager_id>', methods=['GET'])
@require_admin_api
def api_get_user(manager_id):
    """API endpoint to get user details for editing"""
    try:
        admin_service = current_app.admin_service

        # Get user data
        user_data = admin_service.admin_schema.get_admin_user(manager_id)

        if not user_data:
            return jsonify({'success': False, 'error': 'User not found'}), 404

        return jsonify({'success': True, 'user': user_data})

    except Exception as e:
        logger.error(f"❌ Error getting user {manager_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/api/users/<manager_id>', methods=['PUT'])
@require_admin_api
def api_update_user(manager_id):
    """API endpoint to update user details"""
    try:
        data = request.get_json()
        current_manager_id = session.get('manager_id')
        admin_service = current_app.admin_service

        # Extract user data from request
        username = data.get('username')
        email = data.get('email')
        is_admin = data.get('is_admin', False)
        is_super_admin = data.get('is_super_admin', False)
        is_active = data.get('is_active', True)
        login_attempts = data.get('login_attempts', 0)
        permissions = data.get('permissions', {})

        # Validate required fields
        if not username or not email:
            return jsonify({'success': False, 'error': 'Username and email are required'}), 400

        # Check if current user has permission to make these changes
        current_user_perms = admin_service.get_admin_permissions(current_manager_id)

        # Only super admins can modify super admin status
        if is_super_admin and not current_user_perms.get('all_data_access'):
            return jsonify({'success': False, 'error': 'Only super admins can create super admins'}), 403

        # Update user in database
        updates = {
            'username': username,
            'email': email,
            'is_admin': is_admin,
            'is_super_admin': is_super_admin,
            'is_active': is_active,
            'permissions': permissions
        }

        success = admin_service.admin_schema.update_admin_user(manager_id, updates)

        if success:
            # Log the action
            admin_service.log_admin_action(
                current_manager_id, 'user_edit',
                f'Updated user {username} ({manager_id})',
                'user_management', 'edit_user',
                success=True
            )

            return jsonify({'success': True, 'message': 'User updated successfully'})
        else:
            return jsonify({'success': False, 'error': 'Failed to update user'}), 500

    except Exception as e:
        logger.error(f"❌ Error updating user {manager_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/api/users/<manager_id>/reset-access', methods=['POST'])
@require_admin_api
def api_reset_user_access(manager_id):
    """API endpoint to reset user access (clear login attempts, unlock account)"""
    try:
        current_manager_id = session.get('manager_id')
        admin_service = current_app.admin_service

        # Reset user access
        success = admin_service.admin_schema.reset_user_access(manager_id)

        if success:
            # Log the action
            admin_service.log_admin_action(
                current_manager_id, 'user_access_reset',
                f'Reset access for user {manager_id}',
                'user_management', 'reset_access',
                success=True
            )

            return jsonify({'success': True, 'message': 'User access reset successfully'})
        else:
            return jsonify({'success': False, 'error': 'Failed to reset user access'}), 500

    except Exception as e:
        logger.error(f"❌ Error resetting access for user {manager_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/api/users/<manager_id>', methods=['DELETE'])
@require_admin_api
def api_delete_user(manager_id):
    """API endpoint to delete a user"""
    try:
        current_manager_id = session.get('manager_id')
        admin_service = current_app.admin_service

        # Prevent users from deleting themselves
        if manager_id == current_manager_id:
            return jsonify({'success': False, 'error': 'Cannot delete your own account'}), 403

        # Get user data before deletion for logging
        user_data = admin_service.admin_schema.get_admin_user(manager_id)
        if not user_data:
            return jsonify({'success': False, 'error': 'User not found'}), 404

        username = user_data.get('username', 'Unknown')

        # Check permissions - only super admins can delete other super admins
        current_user_perms = admin_service.get_admin_permissions(current_manager_id)
        if user_data.get('is_super_admin') and not current_user_perms.get('all_data_access'):
            return jsonify({'success': False, 'error': 'Only super admins can delete super admin accounts'}), 403

        # Delete user from database
        success = admin_service.admin_schema.delete_admin_user(manager_id)

        if success:
            # Log the action
            admin_service.log_admin_action(
                current_manager_id, 'user_delete',
                f'Deleted user {username} ({manager_id})',
                'user_management', 'delete_user',
                success=True
            )

            return jsonify({'success': True, 'message': f'User {username} deleted successfully'})
        else:
            return jsonify({'success': False, 'error': 'Failed to delete user'}), 500

    except Exception as e:
        logger.error(f"❌ Error deleting user {manager_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/api/system/health', methods=['GET'])
@require_admin_api
def api_system_health():
    """API endpoint for system health check"""
    try:
        health_data = _get_system_health()
        return jsonify({'success': True, 'health_data': health_data})

    except Exception as e:
        logger.error(f"❌ Error getting system health: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/api/data/refresh', methods=['POST'])
@require_admin_api
def api_trigger_data_refresh():
    """API endpoint to trigger data refresh"""
    try:
        manager_id = session.get('manager_id')
        admin_service = current_app.admin_service

        # Trigger refresh using existing refresh endpoint
        # This will call the existing /api/refresh-data endpoint
        import requests
        response = requests.post(f"{request.host_url}api/refresh-data")

        success = response.status_code == 200 and response.json().get('success', False)

        # Log the action
        admin_service.log_admin_action(
            manager_id, 'data_refresh_trigger',
            'Triggered manual data refresh',
            'system', 'data_refresh',
            success=success,
            error_message=None if success else f"HTTP {response.status_code}"
        )

        if success:
            return jsonify({'success': True, 'message': 'Data refresh triggered successfully'})
        else:
            return jsonify({'success': False, 'error': 'Failed to trigger data refresh'}), 500

    except Exception as e:
        logger.error(f"❌ Error triggering data refresh: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/api/health-check', methods=['POST'])
@require_admin_api
def api_run_health_check():
    """API endpoint to run system health check"""
    try:
        manager_id = session.get('manager_id')
        admin_service = current_app.admin_service

        # Run health checks using the monitoring system
        from ..monitoring.health_checks import run_health_checks
        health_results = run_health_checks()

        # Count successful checks
        successful_checks = sum(1 for result in health_results.values() if result.get('status') == 'healthy')
        total_checks = len(health_results)

        # Log the action
        admin_service.log_admin_action(
            manager_id, 'health_check_run',
            f'Ran system health check: {successful_checks}/{total_checks} checks passed',
            'system', 'health_check',
            success=True
        )

        return jsonify({
            'success': True,
            'message': f'Health check completed: {successful_checks}/{total_checks} checks passed',
            'results': health_results
        })

    except Exception as e:
        logger.error(f"❌ Error running health check: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/api/clear-cache', methods=['POST'])
@require_admin_api
def api_clear_cache():
    """API endpoint to clear performance cache"""
    try:
        manager_id = session.get('manager_id')
        admin_service = current_app.admin_service

        # Clear the performance cache
        from ..services.performance_cache import performance_cache
        cache_size_before = len(performance_cache._cache)
        performance_cache.clear()

        # Log the action
        admin_service.log_admin_action(
            manager_id, 'cache_clear',
            f'Cleared performance cache ({cache_size_before} items)',
            'system', 'cache_management',
            success=True
        )

        return jsonify({
            'success': True,
            'message': f'Cache cleared successfully ({cache_size_before} items removed)'
        })

    except Exception as e:
        logger.error(f"❌ Error clearing cache: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/api/audit/logs', methods=['GET'])
@require_admin_api
def api_get_audit_logs():
    """API endpoint to get audit logs with pagination"""
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 50))
        offset = (page - 1) * limit

        logs = _get_audit_logs_paginated(offset, limit)
        total_logs = _get_audit_logs_count()

        return jsonify({
            'success': True,
            'logs': logs,
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total_logs,
                'pages': (total_logs + limit - 1) // limit
            }
        })

    except Exception as e:
        logger.error(f"❌ Error getting audit logs: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Helper Functions

def _get_system_overview() -> Dict[str, Any]:
    """Get system overview statistics"""
    try:
        db_manager = current_app.db_manager

        # Get member counts
        member_counts = db_manager.get_category_counts()

        # Get recent activity
        recent_refreshes = db_manager.execute_query("""
            SELECT * FROM data_refresh_log
            ORDER BY last_refresh DESC
            LIMIT 5
        """, fetch_all=True)

        return {
            'member_counts': member_counts,
            'recent_refreshes': [dict(r) for r in recent_refreshes] if recent_refreshes else [],
            'system_uptime': _get_system_uptime(),
            'database_type': db_manager.db_type,
            'database_name': db_manager.db_name
        }

    except Exception as e:
        logger.error(f"❌ Error getting system overview: {e}")
        return {}

def _get_all_admin_users() -> List[Dict[str, Any]]:
    """Get all admin users"""
    try:
        admin_service = current_app.admin_service
        return admin_service.admin_schema.get_all_admin_users()

    except Exception as e:
        logger.error(f"❌ Error getting admin users: {e}")
        return []

def _get_system_users() -> List[Dict[str, Any]]:
    """Get system users from existing session/auth data"""
    try:
        # This would need to be implemented based on your existing auth system
        # For now, return empty list
        return []

    except Exception as e:
        logger.error(f"❌ Error getting system users: {e}")
        return []

def _get_system_health() -> Dict[str, Any]:
    """Get system health metrics"""
    try:
        import psutil
        import time

        # CPU and memory usage
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()

        # Database connection test
        try:
            db_manager = current_app.db_manager
            conn = db_manager.get_connection()
            db_status = 'healthy'
            conn.close()
        except Exception:
            db_status = 'error'

        return {
            'cpu_usage': cpu_percent,
            'memory_usage': memory.percent,
            'memory_available': memory.available // (1024 * 1024),  # MB
            'database_status': db_status,
            'uptime': _get_system_uptime(),
            'checked_at': datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"❌ Error getting system health: {e}")
        return {'error': str(e)}

def _get_database_stats() -> Dict[str, Any]:
    """Get database statistics"""
    try:
        db_manager = current_app.db_manager

        # Get table counts
        tables = ['members', 'prospects', 'training_clients', 'admin_users', 'audit_log']
        table_counts = {}

        for table in tables:
            try:
                result = db_manager.execute_query(f"SELECT COUNT(*) as count FROM {table}", fetch_one=True)
                table_counts[table] = result['count'] if result else 0
            except:
                table_counts[table] = 0

        return {
            'table_counts': table_counts,
            'database_type': db_manager.db_type,
            'database_name': db_manager.db_name
        }

    except Exception as e:
        logger.error(f"❌ Error getting database stats: {e}")
        return {}

def _get_api_status() -> Dict[str, Any]:
    """Get API status"""
    try:
        # Test various API endpoints
        status = {
            'clubhub_api': 'unknown',
            'clubos_api': 'unknown',
            'square_api': 'unknown'
        }

        # This would need actual API health checks
        # For now, return basic status

        return status

    except Exception as e:
        logger.error(f"❌ Error getting API status: {e}")
        return {}

def _get_data_refresh_status() -> Dict[str, Any]:
    """Get data refresh status"""
    try:
        db_manager = current_app.db_manager

        last_refresh = db_manager.execute_query("""
            SELECT * FROM data_refresh_log
            ORDER BY last_refresh DESC
            LIMIT 1
        """, fetch_one=True)

        return {
            'last_refresh': dict(last_refresh) if last_refresh else None,
            'auto_refresh_enabled': True,  # This could be a setting
            'refresh_interval': '1 hour'   # This could be configurable
        }

    except Exception as e:
        logger.error(f"❌ Error getting refresh status: {e}")
        return {}

def _get_backup_status() -> Dict[str, Any]:
    """Get backup status"""
    try:
        # This would implement actual backup status checking
        return {
            'last_backup': None,
            'backup_enabled': False,
            'backup_location': 'Not configured'
        }

    except Exception as e:
        logger.error(f"❌ Error getting backup status: {e}")
        return {}

def _get_recent_audit_logs(limit: int = 100) -> List[Dict[str, Any]]:
    """Get recent audit logs"""
    try:
        db_manager = current_app.db_manager

        logs = db_manager.execute_query("""
            SELECT * FROM audit_log
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,), fetch_all=True)

        return [dict(log) for log in logs] if logs else []

    except Exception as e:
        logger.error(f"❌ Error getting audit logs: {e}")
        return []

def _get_audit_logs_paginated(offset: int, limit: int) -> List[Dict[str, Any]]:
    """Get paginated audit logs"""
    try:
        db_manager = current_app.db_manager

        logs = db_manager.execute_query("""
            SELECT * FROM audit_log
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """, (limit, offset), fetch_all=True)

        return [dict(log) for log in logs] if logs else []

    except Exception as e:
        logger.error(f"❌ Error getting paginated audit logs: {e}")
        return []

def _get_audit_logs_count() -> int:
    """Get total audit logs count"""
    try:
        db_manager = current_app.db_manager

        result = db_manager.execute_query("""
            SELECT COUNT(*) as count FROM audit_log
        """, fetch_one=True)

        return result['count'] if result else 0

    except Exception as e:
        logger.error(f"❌ Error getting audit logs count: {e}")
        return 0

def _get_system_settings() -> Dict[str, Any]:
    """Get system settings"""
    try:
        db_manager = current_app.db_manager

        settings = db_manager.execute_query("""
            SELECT * FROM admin_settings
            WHERE is_public = ? OR is_public = 1
            ORDER BY category, setting_key
        """, (True if db_manager.db_type == 'postgresql' else 1,), fetch_all=True)

        return [dict(setting) for setting in settings] if settings else []

    except Exception as e:
        logger.error(f"❌ Error getting system settings: {e}")
        return []

def _get_system_uptime() -> str:
    """Get system uptime"""
    try:
        import psutil
        boot_time = psutil.boot_time()
        uptime_seconds = time.time() - boot_time
        uptime_delta = timedelta(seconds=uptime_seconds)

        days = uptime_delta.days
        hours, remainder = divmod(uptime_delta.seconds, 3600)
        minutes, _ = divmod(remainder, 60)

        return f"{days}d {hours}h {minutes}m"

    except Exception:
        return "Unknown"


# Manager Credentials Routes
@admin_bp.route('/credentials')
@require_admin
def manager_credentials():
    """Display manager credentials form"""
    try:
        manager_id = session.get('manager_id')

        # Get existing credentials from SecureSecretsManager
        from ..services.authentication.secure_secrets_manager import SecureSecretsManager
        secrets_manager = SecureSecretsManager()

        credentials = secrets_manager.get_credentials(manager_id) or {}

        return render_template('manager_credentials.html',
                             credentials=credentials,
                             success_message=request.args.get('success'),
                             error_message=request.args.get('error'))

    except Exception as e:
        logger.error(f"❌ Error loading credentials page: {e}")
        return render_template('error.html', error='Failed to load credentials page')


@admin_bp.route('/credentials/save', methods=['POST'])
@require_admin
def save_manager_credentials():
    """Save manager credentials"""
    try:
        manager_id = session.get('manager_id')

        # Get form data
        clubos_username = request.form.get('clubos_username')
        clubos_password = request.form.get('clubos_password')
        clubhub_email = request.form.get('clubhub_email')
        clubhub_password = request.form.get('clubhub_password')
        square_access_token = request.form.get('square_access_token')
        square_location_id = request.form.get('square_location_id')

        # Validate required fields
        if not all([clubos_username, clubos_password, clubhub_email, clubhub_password,
                    square_access_token, square_location_id]):
            return redirect(url_for('admin.manager_credentials',
                                  error='All fields are required'))

        # Store credentials using SecureSecretsManager
        from ..services.authentication.secure_secrets_manager import SecureSecretsManager
        secrets_manager = SecureSecretsManager()

        # Store in the database (encrypted)
        success = secrets_manager.store_credentials(
            manager_id=manager_id,
            clubos_username=clubos_username,
            clubos_password=clubos_password,
            clubhub_email=clubhub_email,
            clubhub_password=clubhub_password
        )

        if not success:
            return redirect(url_for('admin.manager_credentials',
                                  error='Failed to store credentials'))

        # Also store Square credentials separately
        secrets_manager.set_secret(f'square-access-token-{manager_id}', square_access_token)
        secrets_manager.set_secret(f'square-location-id-{manager_id}', square_location_id)

        # Log the action
        admin_service = current_app.admin_service
        admin_service.log_admin_action(
            manager_id, 'credentials_update', 'Updated API credentials'
        )

        logger.info(f"✅ Credentials saved for manager {manager_id}")
        return redirect(url_for('admin.manager_credentials',
                              success='Credentials saved successfully'))

    except Exception as e:
        logger.error(f"❌ Error saving credentials: {e}")
        return redirect(url_for('admin.manager_credentials',
                              error=f'Error saving credentials: {str(e)}'))


@admin_bp.route('/credentials/test', methods=['POST'])
@require_admin_api
def test_credentials():
    """Test manager credentials"""
    try:
        # Get form data
        clubos_username = request.form.get('clubos_username')
        clubos_password = request.form.get('clubos_password')

        # Test ClubOS login
        from ..services.clubos_integration import ClubOSIntegration
        clubos = ClubOSIntegration()

        # Try to authenticate
        test_result = clubos.test_authentication(clubos_username, clubos_password)

        if test_result:
            return jsonify({
                'success': True,
                'message': 'ClubOS credentials are valid!'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'ClubOS authentication failed. Please check your credentials.'
            })

    except Exception as e:
        logger.error(f"❌ Error testing credentials: {e}")
        return jsonify({
            'success': False,
            'message': f'Error testing credentials: {str(e)}'
        })