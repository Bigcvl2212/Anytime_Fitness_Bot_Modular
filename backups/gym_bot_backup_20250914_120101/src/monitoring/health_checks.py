#!/usr/bin/env python3
"""
Production Health Check System
Comprehensive monitoring without interfering with existing functionality
"""

import os
import sqlite3
import time
import logging
import json
import psutil
from datetime import datetime, timedelta
from typing import Dict, Any, List
from flask import Flask, Blueprint, jsonify, current_app

logger = logging.getLogger(__name__)

# Create monitoring blueprint
monitoring_bp = Blueprint('monitoring', __name__, url_prefix='/monitoring')

class HealthChecker:
    """Comprehensive health checking system"""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.checks = {}
        
    def register_check(self, name: str, check_func, timeout: int = 30):
        """Register a health check"""
        self.checks[name] = {
            'function': check_func,
            'timeout': timeout,
            'last_run': None,
            'last_result': None,
            'last_duration': None
        }
    
    def run_check(self, name: str) -> Dict[str, Any]:
        """Run a specific health check"""
        if name not in self.checks:
            return {'status': 'error', 'message': f'Check {name} not found'}
        
        check_info = self.checks[name]
        start_time = time.time()
        
        try:
            result = check_info['function']()
            duration = time.time() - start_time
            
            # Update check info
            check_info['last_run'] = datetime.now()
            check_info['last_duration'] = duration
            check_info['last_result'] = result
            
            return {
                'status': 'healthy' if result.get('healthy', False) else 'unhealthy',
                'message': result.get('message', ''),
                'details': result.get('details', {}),
                'duration_ms': round(duration * 1000, 2),
                'timestamp': check_info['last_run'].isoformat()
            }
            
        except Exception as e:
            duration = time.time() - start_time
            check_info['last_run'] = datetime.now()
            check_info['last_duration'] = duration
            error_result = {
                'status': 'error',
                'message': str(e),
                'duration_ms': round(duration * 1000, 2),
                'timestamp': datetime.now().isoformat()
            }
            check_info['last_result'] = error_result
            return error_result
    
    def run_all_checks(self) -> Dict[str, Any]:
        """Run all registered health checks"""
        results = {}
        overall_healthy = True
        
        for check_name in self.checks:
            result = self.run_check(check_name)
            results[check_name] = result
            if result['status'] != 'healthy':
                overall_healthy = False
        
        return {
            'status': 'healthy' if overall_healthy else 'unhealthy',
            'timestamp': datetime.now().isoformat(),
            'uptime_seconds': (datetime.now() - self.start_time).total_seconds(),
            'checks': results
        }

# Global health checker instance
health_checker = HealthChecker()

# Health Check Functions
def check_database_connection():
    """Check database connectivity"""
    try:
        # Try to access the database manager
        if hasattr(current_app, 'db_manager'):
            db_path = current_app.db_manager.db_path
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
            table_count = cursor.fetchone()[0]
            conn.close()
            
            return {
                'healthy': True,
                'message': f'Database connection successful',
                'details': {
                    'database_path': db_path,
                    'table_count': table_count
                }
            }
        else:
            return {
                'healthy': False,
                'message': 'Database manager not initialized'
            }
            
    except Exception as e:
        return {
            'healthy': False,
            'message': f'Database connection failed: {e}'
        }

def check_secrets_manager():
    """Check Google Secrets Manager connectivity"""
    try:
        if hasattr(current_app, 'db_manager'):
            # Try to import and test secret manager
            from src.services.authentication.secure_secrets_manager import SecureSecretsManager
            secrets_manager = SecureSecretsManager()
            
            # Test with a basic check (this won't create or modify anything)
            if hasattr(secrets_manager, 'client') and secrets_manager.client:
                return {
                    'healthy': True,
                    'message': 'Secrets Manager connection successful',
                    'details': {
                        'project_id': secrets_manager.project_id
                    }
                }
            else:
                return {
                    'healthy': False,
                    'message': 'Secrets Manager client not initialized'
                }
        else:
            return {
                'healthy': False,
                'message': 'Application not fully initialized'
            }
            
    except Exception as e:
        return {
            'healthy': False,
            'message': f'Secrets Manager check failed: {e}'
        }

def check_square_integration():
    """Check Square payment integration"""
    try:
        # Check if Square is configured
        if hasattr(current_app, 'config') and current_app.config.get('SQUARE_AVAILABLE'):
            return {
                'healthy': True,
                'message': 'Square integration available',
                'details': {
                    'environment': os.getenv('SQUARE_ENVIRONMENT', 'unknown')
                }
            }
        else:
            return {
                'healthy': False,
                'message': 'Square integration not available'
            }
            
    except Exception as e:
        return {
            'healthy': False,
            'message': f'Square integration check failed: {e}'
        }

def check_system_resources():
    """Check system resource usage"""
    try:
        # Get CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Get memory usage
        memory = psutil.virtual_memory()
        
        # Get disk usage
        disk = psutil.disk_usage('.')
        
        # Determine health based on thresholds
        healthy = (
            cpu_percent < 80 and 
            memory.percent < 85 and 
            disk.percent < 90
        )
        
        return {
            'healthy': healthy,
            'message': 'System resources within normal limits' if healthy else 'System resources under pressure',
            'details': {
                'cpu_percent': round(cpu_percent, 2),
                'memory_percent': round(memory.percent, 2),
                'disk_percent': round(disk.percent, 2),
                'memory_available_mb': round(memory.available / (1024 * 1024), 2),
                'disk_free_gb': round(disk.free / (1024 * 1024 * 1024), 2)
            }
        }
        
    except Exception as e:
        return {
            'healthy': False,
            'message': f'System resource check failed: {e}'
        }

def check_flask_app():
    """Check Flask application health"""
    try:
        # Basic app health indicators
        app_details = {
            'debug_mode': current_app.debug,
            'testing': current_app.testing,
            'config_loaded': bool(current_app.config),
            'blueprints_registered': len(current_app.blueprints),
            'url_rules': len(current_app.url_map._rules)
        }
        
        # Check if key services are initialized
        services_status = {
            'db_manager': hasattr(current_app, 'db_manager'),
            'training_package_cache': hasattr(current_app, 'training_package_cache'),
            'clubos': hasattr(current_app, 'clubos'),
            'messaging_client': hasattr(current_app, 'messaging_client'),
            'clubhub_client': hasattr(current_app, 'clubhub_client')
        }
        
        healthy = all(services_status.values())
        
        return {
            'healthy': healthy,
            'message': 'Flask application healthy' if healthy else 'Some services not initialized',
            'details': {
                'app_info': app_details,
                'services': services_status
            }
        }
        
    except Exception as e:
        return {
            'healthy': False,
            'message': f'Flask app check failed: {e}'
        }

# Register all health checks
health_checker.register_check('database', check_database_connection)
health_checker.register_check('secrets_manager', check_secrets_manager)
health_checker.register_check('square_integration', check_square_integration)
health_checker.register_check('system_resources', check_system_resources)
health_checker.register_check('flask_app', check_flask_app)

# Health Check Routes
@monitoring_bp.route('/health')
def health_check():
    """Basic health check endpoint"""
    try:
        result = health_checker.run_all_checks()
        status_code = 200 if result['status'] == 'healthy' else 503
        return jsonify(result), status_code
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Health check failed: {e}',
            'timestamp': datetime.now().isoformat()
        }), 500

@monitoring_bp.route('/health/<check_name>')
def individual_health_check(check_name):
    """Check individual health component"""
    try:
        result = health_checker.run_check(check_name)
        status_code = 200 if result['status'] == 'healthy' else 503
        return jsonify(result), status_code
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Health check {check_name} failed: {e}',
            'timestamp': datetime.now().isoformat()
        }), 500

@monitoring_bp.route('/metrics')
def metrics():
    """Basic application metrics"""
    try:
        uptime = datetime.now() - health_checker.start_time
        
        # Get basic system metrics
        try:
            system_metrics = {
                'cpu_percent': psutil.cpu_percent(),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('.').percent
            }
        except:
            system_metrics = {'error': 'Could not collect system metrics'}
        
        # Get application metrics
        app_metrics = {
            'uptime_seconds': uptime.total_seconds(),
            'uptime_human': str(uptime),
            'registered_health_checks': len(health_checker.checks),
            'flask_debug': current_app.debug
        }
        
        # Get database metrics if available
        db_metrics = {}
        try:
            if hasattr(current_app, 'db_manager'):
                conn = sqlite3.connect(current_app.db_manager.db_path)
                cursor = conn.cursor()
                
                # Count records in main tables
                tables = ['members', 'prospects', 'training_clients']
                for table in tables:
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM {table}")
                        count = cursor.fetchone()[0]
                        db_metrics[f'{table}_count'] = count
                    except:
                        db_metrics[f'{table}_count'] = 'N/A'
                
                conn.close()
        except Exception as e:
            db_metrics['error'] = str(e)
        
        return jsonify({
            'timestamp': datetime.now().isoformat(),
            'system': system_metrics,
            'application': app_metrics,
            'database': db_metrics
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Metrics collection failed: {e}',
            'timestamp': datetime.now().isoformat()
        }), 500

@monitoring_bp.route('/status')
def status():
    """Application status overview"""
    try:
        # Run a quick health check
        health_result = health_checker.run_all_checks()
        
        return jsonify({
            'service': 'Gym Bot Dashboard',
            'version': '2.0.0-production-ready',
            'status': health_result['status'],
            'uptime': health_result['uptime_seconds'],
            'timestamp': datetime.now().isoformat(),
            'environment': os.getenv('FLASK_ENV', 'development'),
            'checks_passed': sum(1 for check in health_result['checks'].values() if check['status'] == 'healthy'),
            'total_checks': len(health_result['checks'])
        })
        
    except Exception as e:
        return jsonify({
            'service': 'Gym Bot Dashboard',
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

def register_monitoring(app: Flask):
    """Register monitoring blueprint with the Flask app"""
    app.register_blueprint(monitoring_bp)
    logger.info("✅ Production monitoring system registered")
    
    # Initialize health checker with app context
    with app.app_context():
        # Set start time
        health_checker.start_time = datetime.now()
        logger.info("✅ Health checker initialized")

def run_startup_health_check(app: Flask):
    """Run health checks during application startup"""
    with app.app_context():
        try:
            logger.info("🔍 Running startup health checks...")
            results = health_checker.run_all_checks()
            
            healthy_checks = sum(1 for check in results['checks'].values() if check['status'] == 'healthy')
            total_checks = len(results['checks'])
            
            if results['status'] == 'healthy':
                logger.info(f"✅ All health checks passed ({healthy_checks}/{total_checks})")
            else:
                logger.warning(f"⚠️ Some health checks failed ({healthy_checks}/{total_checks})")
                for check_name, check_result in results['checks'].items():
                    if check_result['status'] != 'healthy':
                        logger.warning(f"  ❌ {check_name}: {check_result['message']}")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Startup health check failed: {e}")
            return None