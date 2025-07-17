"""
Gym Bot Dashboard - Web Interface for Anytime Fitness Bot Management

A Flask-based web dashboard for monitoring and controlling the gym bot system.
Provides real-time status monitoring, workflow execution, and system management.
"""

import sys
import os
import json
import threading
import time
from datetime import datetime
from typing import Dict, Any, Optional
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import gym bot modules
gym_bot_available = True
try:
    from gym_bot.core import get_driver, close_driver
    from gym_bot.services import (
        get_gemini_client,
        get_messaging_service,
        get_square_client,
        test_square_connection
    )
    from gym_bot.config import GCP_PROJECT_ID
    from gym_bot.config.migration_config import get_migration_mode
    from gym_bot.services.api.migration_service import get_migration_service
except ImportError as e:
    print(f"Warning: Could not import gym_bot modules: {e}")
    print("Dashboard will run in limited mode")
    gym_bot_available = False

# Import new services directly to avoid dependency issues
try:
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from new_services_social_media.social_media_manager import SocialMediaManager, get_social_media_manager
    from new_services_analytics.analytics_manager import AnalyticsManager, get_analytics_manager
    social_media_available = True
    analytics_available = True
except ImportError as e:
    print(f"Warning: New services not available: {e}")
    social_media_available = False
    analytics_available = False
    
    # Create mock functions for when services aren't available
    def get_social_media_manager():
        class MockSocialMediaManager:
            def get_connected_accounts(self): return []
            def get_scheduled_posts(self): return []
            def get_engagement_overview(self): return {}
            def get_content_recommendations(self): return []
        return MockSocialMediaManager()
    
    def get_analytics_manager():
        class MockAnalyticsManager:
            def get_kpis(self): return []
            def get_dashboard_summary(self): return {}
            def get_revenue_analytics(self): return {}
            def get_membership_analytics(self): return {}
            def get_operational_analytics(self): return {}
            def get_insights(self): return []
        return MockAnalyticsManager()
    
    # Mock values for demo mode
    GCP_PROJECT_ID = "demo-project"
    
    def get_migration_mode():
        return "demo"
    
    def test_square_connection():
        return True
    
    def get_driver(**kwargs):
        return "demo_driver"
    
    def close_driver():
        pass
    
    def get_gemini_client():
        class MockClient:
            def generate_response(self, text):
                return f"Mock response to: {text}"
        return MockClient()
    
    def get_migration_service(mode=None):
        class MockService:
            def get_migration_stats(self):
                return {'api_attempts': 42, 'selenium_fallbacks': 3, 'api_success_rate': 85.5}
        return MockService()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'gym-bot-dashboard-secret-key')

# Global status storage
system_status = {
    'services': {},
    'last_update': None,
    'workflows': {},
    'logs': []
}

# Background status updater
status_update_running = False


def log_message(level: str, message: str, component: str = "Dashboard"):
    """Add a log message to the system logs."""
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'level': level,
        'component': component,
        'message': message
    }
    system_status['logs'].insert(0, log_entry)
    
    # Keep only last 100 log entries
    if len(system_status['logs']) > 100:
        system_status['logs'] = system_status['logs'][:100]


def check_service_status() -> Dict[str, Any]:
    """Check the status of all system services."""
    status = {
        'square_payments': {'status': 'unknown', 'details': ''},
        'gemini_ai': {'status': 'unknown', 'details': ''},
        'migration_service': {'status': 'unknown', 'details': ''},
        'clubos_auth': {'status': 'unknown', 'details': ''}
    }
    
    if not gym_bot_available:
        # Demo mode status
        status['square_payments'] = {'status': 'healthy', 'details': 'Demo mode - Square API simulated'}
        status['gemini_ai'] = {'status': 'healthy', 'details': 'Demo mode - AI responses simulated'}
        status['migration_service'] = {'status': 'healthy', 'details': 'Demo mode - Migration service simulated'}
        status['clubos_auth'] = {'status': 'healthy', 'details': 'Demo mode - Authentication simulated'}
        
        # Add new services status
        if social_media_available:
            status['social_media'] = {'status': 'healthy', 'details': 'Social media management active'}
        if analytics_available:
            status['analytics'] = {'status': 'healthy', 'details': 'Analytics engine running'}
        
        return status
    
    # Check Square payments
    try:
        if test_square_connection():
            status['square_payments'] = {'status': 'healthy', 'details': 'Connection successful'}
        else:
            status['square_payments'] = {'status': 'error', 'details': 'Connection failed'}
    except Exception as e:
        status['square_payments'] = {'status': 'error', 'details': str(e)}
    
    # Check Gemini AI
    try:
        ai_client = get_gemini_client()
        test_response = ai_client.generate_response("Hello")
        if test_response:
            status['gemini_ai'] = {'status': 'healthy', 'details': 'AI response generated'}
        else:
            status['gemini_ai'] = {'status': 'error', 'details': 'No response generated'}
    except Exception as e:
        status['gemini_ai'] = {'status': 'error', 'details': str(e)}
    
    # Check Migration Service
    try:
        migration_mode = get_migration_mode()
        migration_service = get_migration_service(migration_mode)
        stats = migration_service.get_migration_stats()
        status['migration_service'] = {
            'status': 'healthy', 
            'details': f"Mode: {migration_mode}, API calls: {stats.get('api_attempts', 0)}"
        }
    except Exception as e:
        status['migration_service'] = {'status': 'error', 'details': str(e)}
    
    # Check ClubOS authentication
    try:
        driver = get_driver(headless=True)
        status['clubos_auth'] = {'status': 'healthy', 'details': 'WebDriver initialized'}
        close_driver()
    except Exception as e:
        status['clubos_auth'] = {'status': 'error', 'details': str(e)}
    
    return status


def update_system_status():
    """Background task to update system status."""
    global status_update_running
    status_update_running = True
    
    while status_update_running:
        try:
            system_status['services'] = check_service_status()
            system_status['last_update'] = datetime.now().isoformat()
            log_message('INFO', 'System status updated', 'StatusUpdater')
        except Exception as e:
            log_message('ERROR', f'Status update failed: {e}', 'StatusUpdater')
        
        time.sleep(30)  # Update every 30 seconds


@app.route('/')
def dashboard_home():
    """Main dashboard page."""
    return render_template('dashboard.html', 
                         status=system_status,
                         project_id=GCP_PROJECT_ID)


@app.route('/api/status')
def api_status():
    """API endpoint for system status."""
    return jsonify(system_status)


@app.route('/api/refresh-status')
def api_refresh_status():
    """Force refresh system status."""
    try:
        system_status['services'] = check_service_status()
        system_status['last_update'] = datetime.now().isoformat()
        log_message('INFO', 'Status manually refreshed', 'API')
        return jsonify({'success': True, 'status': system_status})
    except Exception as e:
        log_message('ERROR', f'Manual status refresh failed: {e}', 'API')
        return jsonify({'success': False, 'error': str(e)})


@app.route('/workflows')
def workflows_page():
    """Workflows management page."""
    workflows = {
        'message_processing': {
            'name': 'Message Processing',
            'description': 'Process member messages and generate AI responses',
            'status': 'available'
        },
        'payment_processing': {
            'name': 'Payment Processing', 
            'description': 'Process overdue payments and send invoices',
            'status': 'available'
        },
        'api_testing': {
            'name': 'API Testing',
            'description': 'Run API vs Selenium testing suite',
            'status': 'available'
        },
        'api_discovery': {
            'name': 'API Discovery',
            'description': 'Discover ClubOS API endpoints',
            'status': 'available'
        }
    }
    
    return render_template('workflows.html', workflows=workflows)


@app.route('/api/run-workflow', methods=['POST'])
def api_run_workflow():
    """API endpoint to run a workflow."""
    try:
        workflow_name = request.json.get('workflow')
        migration_mode = request.json.get('migration_mode', 'hybrid')
        
        if not workflow_name:
            return jsonify({'success': False, 'error': 'No workflow specified'})
        
        log_message('INFO', f'Starting workflow: {workflow_name}', 'WorkflowRunner')
        
        # Start workflow in background thread
        def run_workflow():
            try:
                if not gym_bot_available:
                    # Demo mode
                    log_message('INFO', f'Demo mode: Simulating workflow {workflow_name}', 'WorkflowRunner')
                    time.sleep(2)  # Simulate work
                    log_message('INFO', f'Demo workflow completed: {workflow_name}', 'WorkflowRunner')
                    return
                
                if workflow_name == 'message_processing':
                    from main_enhanced import run_message_processing_enhanced
                    run_message_processing_enhanced(migration_mode)
                    
                elif workflow_name == 'payment_processing':
                    from main_enhanced import run_payment_workflow_enhanced
                    run_payment_workflow_enhanced(migration_mode)
                    
                elif workflow_name == 'api_testing':
                    from main_enhanced import run_api_testing
                    run_api_testing()
                    
                elif workflow_name == 'api_discovery':
                    from main_enhanced import run_api_discovery
                    run_api_discovery()
                
                log_message('INFO', f'Workflow completed: {workflow_name}', 'WorkflowRunner')
                
            except Exception as e:
                log_message('ERROR', f'Workflow failed: {workflow_name} - {e}', 'WorkflowRunner')
        
        # Run in background thread
        thread = threading.Thread(target=run_workflow)
        thread.daemon = True
        thread.start()
        
        return jsonify({'success': True, 'message': f'Workflow {workflow_name} started'})
        
    except Exception as e:
        log_message('ERROR', f'Failed to start workflow: {e}', 'API')
        return jsonify({'success': False, 'error': str(e)})


@app.route('/logs')
def logs_page():
    """System logs page."""
    return render_template('logs.html', logs=system_status['logs'])


@app.route('/api/logs')
def api_logs():
    """API endpoint for system logs."""
    return jsonify({'logs': system_status['logs']})


@app.route('/settings')
def settings_page():
    """Settings and configuration page."""
    settings = {
        'gcp_project': GCP_PROJECT_ID,
        'migration_mode': get_migration_mode(),
        'environment': os.environ.get('ENVIRONMENT', 'sandbox')
    }
    return render_template('settings.html', settings=settings)


# New routes for enhanced features
@app.route('/social-media')
def social_media_page():
    """Social Media Management page."""
    if not social_media_available:
        return render_template('feature_unavailable.html', feature='Social Media Management')
    
    sm_manager = get_social_media_manager()
    data = {
        'accounts': sm_manager.get_connected_accounts(),
        'scheduled_posts': sm_manager.get_scheduled_posts(),
        'engagement_overview': sm_manager.get_engagement_overview(),
        'content_recommendations': sm_manager.get_content_recommendations()
    }
    return render_template('social_media.html', **data)


@app.route('/analytics')
def analytics_page():
    """Analytics & Advice page."""
    if not analytics_available:
        return render_template('feature_unavailable.html', feature='Analytics & Advice')
    
    analytics_manager = get_analytics_manager()
    data = {
        'kpis': analytics_manager.get_kpis(),
        'dashboard_summary': analytics_manager.get_dashboard_summary(),
        'revenue_analytics': analytics_manager.get_revenue_analytics(),
        'membership_analytics': analytics_manager.get_membership_analytics(),
        'operational_analytics': analytics_manager.get_operational_analytics(),
        'insights': analytics_manager.get_insights()
    }
    return render_template('analytics.html', **data)


# API endpoints for new features
@app.route('/api/social-media/accounts')
def api_social_media_accounts():
    """API endpoint for social media accounts."""
    if not social_media_available:
        return jsonify({'error': 'Social media service not available'})
    
    sm_manager = get_social_media_manager()
    return jsonify({'accounts': sm_manager.get_connected_accounts()})


@app.route('/api/social-media/schedule-post', methods=['POST'])
def api_schedule_post():
    """API endpoint to schedule a social media post."""
    if not social_media_available:
        return jsonify({'success': False, 'error': 'Social media service not available'})
    
    try:
        sm_manager = get_social_media_manager()
        post_id = sm_manager.schedule_post(request.json)
        return jsonify({'success': True, 'post_id': post_id})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/analytics/dashboard')
def api_analytics_dashboard():
    """API endpoint for analytics dashboard data."""
    if not analytics_available:
        return jsonify({'error': 'Analytics service not available'})
    
    analytics_manager = get_analytics_manager()
    return jsonify(analytics_manager.get_dashboard_summary())


def create_templates():
    """Create HTML templates if they don't exist."""
    templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
    os.makedirs(templates_dir, exist_ok=True)
    
    # Enhanced Base template with modern sidebar navigation
    base_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Gym Bot Dashboard{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/chart.js@4.2.1/dist/chart.min.css" rel="stylesheet">
    <style>
        :root {
            --sidebar-width: 280px;
            --primary-color: #6366f1;
            --secondary-color: #f8fafc;
            --accent-color: #10b981;
            --danger-color: #ef4444;
            --warning-color: #f59e0b;
        }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background-color: #f8fafc;
            margin: 0;
        }
        
        .sidebar {
            position: fixed;
            top: 0;
            left: 0;
            height: 100vh;
            width: var(--sidebar-width);
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            z-index: 1000;
            overflow-y: auto;
            box-shadow: 4px 0 15px rgba(0,0,0,0.1);
        }
        
        .sidebar-header {
            padding: 1.5rem;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        
        .sidebar-brand {
            font-size: 1.5rem;
            font-weight: 700;
            color: white;
            text-decoration: none;
        }
        
        .sidebar-nav {
            padding: 1rem 0;
        }
        
        .nav-item {
            margin: 0.25rem 1rem;
        }
        
        .nav-link {
            display: flex;
            align-items: center;
            padding: 0.875rem 1rem;
            color: rgba(255,255,255,0.8);
            text-decoration: none;
            border-radius: 0.5rem;
            transition: all 0.2s;
            font-weight: 500;
        }
        
        .nav-link:hover, .nav-link.active {
            background-color: rgba(255,255,255,0.15);
            color: white;
            transform: translateX(4px);
        }
        
        .nav-link i {
            width: 20px;
            margin-right: 0.75rem;
        }
        
        .main-content {
            margin-left: var(--sidebar-width);
            min-height: 100vh;
        }
        
        .top-bar {
            background: white;
            border-bottom: 1px solid #e5e7eb;
            padding: 1rem 2rem;
            display: flex;
            justify-content: between;
            align-items: center;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        
        .content-area {
            padding: 2rem;
        }
        
        .card {
            border: none;
            border-radius: 1rem;
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        .card:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
        }
        
        .card-header {
            background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
            border-bottom: 1px solid #e2e8f0;
            border-radius: 1rem 1rem 0 0 !important;
            padding: 1.25rem;
        }
        
        .btn-primary {
            background: var(--primary-color);
            border-color: var(--primary-color);
            border-radius: 0.5rem;
            font-weight: 600;
            padding: 0.5rem 1rem;
        }
        
        .btn-primary:hover {
            background: #5856f5;
            border-color: #5856f5;
            transform: translateY(-1px);
        }
        
        .status-indicator {
            display: inline-flex;
            align-items: center;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.875rem;
            font-weight: 500;
        }
        
        .status-healthy {
            background-color: #dcfce7;
            color: #166534;
        }
        
        .status-warning {
            background-color: #fef3c7;
            color: #92400e;
        }
        
        .status-error {
            background-color: #fee2e2;
            color: #991b1b;
        }
        
        .metric-card {
            text-align: center;
            padding: 1.5rem;
        }
        
        .metric-value {
            font-size: 2.5rem;
            font-weight: 700;
            line-height: 1;
        }
        
        .metric-label {
            color: #6b7280;
            font-size: 0.875rem;
            margin-top: 0.5rem;
        }
        
        .chart-container {
            position: relative;
            height: 300px;
            margin: 1rem 0;
        }
        
        @media (max-width: 768px) {
            .sidebar {
                transform: translateX(-100%);
                transition: transform 0.3s;
            }
            
            .sidebar.show {
                transform: translateX(0);
            }
            
            .main-content {
                margin-left: 0;
            }
        }
    </style>
    {% block extra_css %}{% endblock %}
</head>
<body>
    <!-- Sidebar -->
    <nav class="sidebar">
        <div class="sidebar-header">
            <a href="{{ url_for('dashboard_home') }}" class="sidebar-brand">
                <i class="fas fa-dumbbell me-2"></i>Gym Bot Pro
            </a>
        </div>
        <ul class="sidebar-nav">
            <li class="nav-item">
                <a class="nav-link {% if request.endpoint == 'dashboard_home' %}active{% endif %}" 
                   href="{{ url_for('dashboard_home') }}">
                    <i class="fas fa-chart-line"></i>Dashboard
                </a>
            </li>
            <li class="nav-item">
                <a class="nav-link {% if request.endpoint == 'workflows_page' %}active{% endif %}" 
                   href="{{ url_for('workflows_page') }}">
                    <i class="fas fa-cogs"></i>Bot Controls
                </a>
            </li>
            <li class="nav-item">
                <a class="nav-link" href="#payments">
                    <i class="fas fa-credit-card"></i>Payments
                </a>
            </li>
            <li class="nav-item">
                <a class="nav-link" href="#messaging">
                    <i class="fas fa-comments"></i>Messaging
                </a>
            </li>
            <li class="nav-item">
                <a class="nav-link" href="#calendar">
                    <i class="fas fa-calendar-alt"></i>Calendar
                </a>
            </li>
            <li class="nav-item">
                <a class="nav-link {% if request.endpoint == 'analytics_page' %}active{% endif %}" 
                   href="{{ url_for('analytics_page') }}">
                    <i class="fas fa-chart-bar"></i>Analytics
                </a>
            </li>
            <li class="nav-item">
                <a class="nav-link {% if request.endpoint == 'social_media_page' %}active{% endif %}" 
                   href="{{ url_for('social_media_page') }}">
                    <i class="fab fa-instagram"></i>Social Media
                </a>
            </li>
            <li class="nav-item">
                <a class="nav-link {% if request.endpoint == 'settings_page' %}active{% endif %}" 
                   href="{{ url_for('settings_page') }}">
                    <i class="fas fa-cog"></i>Settings
                </a>
            </li>
            <li class="nav-item">
                <a class="nav-link {% if request.endpoint == 'logs_page' %}active{% endif %}" 
                   href="{{ url_for('logs_page') }}">
                    <i class="fas fa-file-alt"></i>Logs
                </a>
            </li>
        </ul>
    </nav>

    <!-- Main Content -->
    <div class="main-content">
        <!-- Top Bar -->
        <div class="top-bar">
            <div class="d-flex align-items-center">
                <button class="btn btn-link d-md-none me-3" onclick="toggleSidebar()">
                    <i class="fas fa-bars"></i>
                </button>
                <h4 class="mb-0">{% block page_title %}{% endblock %}</h4>
            </div>
            <div class="d-flex align-items-center">
                <span class="status-indicator status-healthy me-3">
                    <i class="fas fa-circle me-1"></i>System Online
                </span>
                <button class="btn btn-outline-primary btn-sm" onclick="refreshStatus()">
                    <i class="fas fa-sync-alt"></i>
                </button>
            </div>
        </div>

        <!-- Content Area -->
        <div class="content-area">
            {% with messages = get_flashed_messages() %}
                {% if messages %}
                    {% for message in messages %}
                        <div class="alert alert-info alert-dismissible fade show" role="alert">
                            {{ message }}
                            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                        </div>
                    {% endfor %}
                {% endif %}
            {% endwith %}
            
            {% block content %}{% endblock %}
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.2.1/dist/chart.min.js"></script>
    <script>
        function toggleSidebar() {
            document.querySelector('.sidebar').classList.toggle('show');
        }
        
        function refreshStatus() {
            fetch('/api/refresh-status')
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        location.reload();
                    } else {
                        showAlert('Failed to refresh status: ' + data.error, 'danger');
                    }
                })
                .catch(error => {
                    showAlert('Error refreshing status: ' + error, 'danger');
                });
        }
        
        function showAlert(message, type = 'info') {
            const alertDiv = document.createElement('div');
            alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
            alertDiv.innerHTML = `
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            `;
            document.querySelector('.content-area').prepend(alertDiv);
        }
        
        // Auto-refresh every 60 seconds
        setInterval(() => {
            refreshStatus();
        }, 60000);
    </script>
    {% block scripts %}{% endblock %}
</body>
</html>'''
    
    # Enhanced Dashboard template
    dashboard_template = '''{% extends "base.html" %}

{% block title %}Dashboard - Gym Bot Pro{% endblock %}
{% block page_title %}Dashboard Overview{% endblock %}

{% block content %}
<!-- Quick Stats Row -->
<div class="row mb-4">
    <div class="col-md-3">
        <div class="card metric-card">
            <div class="metric-value text-primary">{{ status.services|length }}</div>
            <div class="metric-label">Active Services</div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card metric-card">
            <div class="metric-value text-success">847</div>
            <div class="metric-label">Active Members</div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card metric-card">
            <div class="metric-value text-info">${{ '89,420' }}</div>
            <div class="metric-label">Monthly Revenue</div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card metric-card">
            <div class="metric-value text-warning">{{ status.logs|length }}</div>
            <div class="metric-label">Recent Logs</div>
        </div>
    </div>
</div>

<!-- System Status Row -->
<div class="row mb-4">
    <div class="col-lg-8">
        <div class="card">
            <div class="card-header">
                <h5><i class="fas fa-heartbeat me-2"></i>System Health</h5>
            </div>
            <div class="card-body">
                {% if status.services %}
                    <div class="row">
                        {% for service, info in status.services.items() %}
                        <div class="col-md-6 mb-3">
                            <div class="d-flex align-items-center">
                                {% if info.status == 'healthy' %}
                                    <div class="status-indicator status-healthy me-3">
                                        <i class="fas fa-check-circle"></i>
                                    </div>
                                {% elif info.status == 'error' %}
                                    <div class="status-indicator status-error me-3">
                                        <i class="fas fa-times-circle"></i>
                                    </div>
                                {% else %}
                                    <div class="status-indicator status-warning me-3">
                                        <i class="fas fa-question-circle"></i>
                                    </div>
                                {% endif %}
                                <div>
                                    <strong>{{ service.replace('_', ' ').title() }}</strong><br>
                                    <small class="text-muted">{{ info.details }}</small>
                                </div>
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                {% else %}
                    <p class="text-muted">No service status available. Click refresh to check services.</p>
                {% endif %}
            </div>
        </div>
    </div>
    
    <div class="col-lg-4">
        <div class="card">
            <div class="card-header">
                <h5><i class="fas fa-info-circle me-2"></i>System Information</h5>
            </div>
            <div class="card-body">
                <p><strong>GCP Project:</strong><br>{{ project_id }}</p>
                <p><strong>Last Update:</strong><br>{{ status.last_update or 'Never' }}</p>
                <p><strong>Environment:</strong><br>Production</p>
                <button class="btn btn-primary w-100" onclick="refreshStatus()">
                    <i class="fas fa-sync-alt me-1"></i> Refresh Status
                </button>
            </div>
        </div>
    </div>
</div>

<!-- Quick Actions & Recent Activity -->
<div class="row">
    <div class="col-lg-6">
        <div class="card">
            <div class="card-header">
                <h5><i class="fas fa-bolt me-2"></i>Quick Actions</h5>
            </div>
            <div class="card-body">
                <div class="d-grid gap-2">
                    <a href="{{ url_for('workflows_page') }}" class="btn btn-outline-primary">
                        <i class="fas fa-play me-2"></i>Run Workflow
                    </a>
                    <a href="{{ url_for('social_media_page') }}" class="btn btn-outline-success">
                        <i class="fab fa-instagram me-2"></i>Schedule Social Post
                    </a>
                    <a href="{{ url_for('analytics_page') }}" class="btn btn-outline-info">
                        <i class="fas fa-chart-bar me-2"></i>View Analytics
                    </a>
                </div>
            </div>
        </div>
    </div>
    
    <div class="col-lg-6">
        <div class="card">
            <div class="card-header">
                <h5><i class="fas fa-clock me-2"></i>Recent Activity</h5>
            </div>
            <div class="card-body">
                {% if status.logs %}
                    <div class="list-group list-group-flush">
                        {% for log in status.logs[:5] %}
                        <div class="list-group-item border-0 px-0">
                            <div class="d-flex justify-content-between align-items-start">
                                <div>
                                    <span class="badge bg-{% if log.level == 'ERROR' %}danger{% elif log.level == 'WARNING' %}warning{% else %}info{% endif %} me-2">
                                        {{ log.level }}
                                    </span>
                                    {{ log.message|truncate(50) }}
                                </div>
                                <small class="text-muted">{{ log.component }}</small>
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                    <div class="text-center mt-3">
                        <a href="{{ url_for('logs_page') }}" class="btn btn-outline-secondary btn-sm">
                            View All Logs
                        </a>
                    </div>
                {% else %}
                    <p class="text-muted text-center">No recent activity.</p>
                {% endif %}
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script>
// Auto-refresh dashboard data every 30 seconds
setInterval(() => {
    fetch('/api/status')
        .then(response => response.json())
        .then(data => {
            // Update status indicators without full page reload
            console.log('Status updated:', data);
        })
        .catch(error => console.error('Status update failed:', error));
}, 30000);
</script>
{% endblock %}'''
    
    # Social Media Management template
    social_media_template = '''{% extends "base.html" %}

{% block title %}Social Media - Gym Bot Pro{% endblock %}
{% block page_title %}Social Media Management{% endblock %}

{% block content %}
<!-- Social Media Overview -->
<div class="row mb-4">
    <div class="col-md-3">
        <div class="card metric-card">
            <div class="metric-value text-primary">{{ engagement_overview.total_followers }}</div>
            <div class="metric-label">Total Followers</div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card metric-card">
            <div class="metric-value text-success">{{ engagement_overview.connected_platforms }}</div>
            <div class="metric-label">Connected Platforms</div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card metric-card">
            <div class="metric-value text-info">{{ engagement_overview.scheduled_posts }}</div>
            <div class="metric-label">Scheduled Posts</div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card metric-card">
            <div class="metric-value text-warning">{{ engagement_overview.recent_engagement.engagement_rate }}%</div>
            <div class="metric-label">Engagement Rate</div>
        </div>
    </div>
</div>

<!-- Connected Accounts & Quick Post -->
<div class="row mb-4">
    <div class="col-lg-6">
        <div class="card">
            <div class="card-header">
                <h5><i class="fab fa-instagram me-2"></i>Connected Accounts</h5>
            </div>
            <div class="card-body">
                {% for account in accounts %}
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <div class="d-flex align-items-center">
                        <div class="status-indicator {% if account.is_connected %}status-healthy{% else %}status-error{% endif %} me-3">
                            {% if account.platform == 'facebook' %}
                                <i class="fab fa-facebook"></i>
                            {% elif account.platform == 'instagram' %}
                                <i class="fab fa-instagram"></i>
                            {% elif account.platform == 'twitter' %}
                                <i class="fab fa-twitter"></i>
                            {% endif %}
                        </div>
                        <div>
                            <strong>{{ account.account_name }}</strong><br>
                            <small class="text-muted">{{ account.followers_count }} followers</small>
                        </div>
                    </div>
                    {% if account.is_connected %}
                        <span class="badge bg-success">Connected</span>
                    {% else %}
                        <button class="btn btn-outline-primary btn-sm">Connect</button>
                    {% endif %}
                </div>
                {% endfor %}
                <button class="btn btn-primary w-100 mt-3">
                    <i class="fas fa-plus me-1"></i> Add Account
                </button>
            </div>
        </div>
    </div>
    
    <div class="col-lg-6">
        <div class="card">
            <div class="card-header">
                <h5><i class="fas fa-edit me-2"></i>Quick Post</h5>
            </div>
            <div class="card-body">
                <form id="quickPostForm">
                    <div class="mb-3">
                        <select class="form-select" name="platform" required>
                            <option value="">Select Platform</option>
                            {% for account in accounts %}
                                {% if account.is_connected %}
                                <option value="{{ account.platform }}">{{ account.account_name }}</option>
                                {% endif %}
                            {% endfor %}
                        </select>
                    </div>
                    <div class="mb-3">
                        <textarea class="form-control" name="content" rows="4" 
                                  placeholder="What's happening at the gym today?" required></textarea>
                    </div>
                    <div class="mb-3">
                        <input type="datetime-local" class="form-control" name="scheduled_time" required>
                    </div>
                    <button type="submit" class="btn btn-success w-100">
                        <i class="fas fa-clock me-1"></i> Schedule Post
                    </button>
                </form>
            </div>
        </div>
    </div>
</div>

<!-- Scheduled Posts & Content Recommendations -->
<div class="row">
    <div class="col-lg-8">
        <div class="card">
            <div class="card-header">
                <h5><i class="fas fa-calendar-alt me-2"></i>Scheduled Posts</h5>
            </div>
            <div class="card-body">
                {% if scheduled_posts %}
                    {% for post in scheduled_posts %}
                    <div class="border rounded p-3 mb-3">
                        <div class="d-flex justify-content-between align-items-start">
                            <div class="flex-grow-1">
                                <div class="d-flex align-items-center mb-2">
                                    {% if post.platform == 'facebook' %}
                                        <i class="fab fa-facebook text-primary me-2"></i>
                                    {% elif post.platform == 'instagram' %}
                                        <i class="fab fa-instagram text-danger me-2"></i>
                                    {% endif %}
                                    <strong>{{ post.platform.title() }}</strong>
                                    <span class="badge bg-info ms-2">{{ post.status.title() }}</span>
                                </div>
                                <p class="mb-2">{{ post.content }}</p>
                                <small class="text-muted">
                                    <i class="fas fa-clock me-1"></i>{{ post.scheduled_time }}
                                </small>
                            </div>
                            <div class="ms-3">
                                <button class="btn btn-outline-primary btn-sm me-1">
                                    <i class="fas fa-edit"></i>
                                </button>
                                <button class="btn btn-outline-danger btn-sm">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                    {% endfor %}
                {% else %}
                    <p class="text-muted text-center">No scheduled posts yet.</p>
                {% endif %}
            </div>
        </div>
    </div>
    
    <div class="col-lg-4">
        <div class="card">
            <div class="card-header">
                <h5><i class="fas fa-lightbulb me-2"></i>AI Recommendations</h5>
            </div>
            <div class="card-body">
                {% for rec in content_recommendations %}
                <div class="border rounded p-3 mb-3">
                    <h6>{{ rec.title }}</h6>
                    <p class="small text-muted mb-2">{{ rec.description }}</p>
                    <div class="small mb-2">
                        <strong>Best time:</strong> {{ rec.suggested_time }}<br>
                        <strong>Expected:</strong> {{ rec.expected_engagement }} engagement
                    </div>
                    <button class="btn btn-outline-success btn-sm w-100">
                        <i class="fas fa-plus me-1"></i> Use Template
                    </button>
                </div>
                {% endfor %}
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script>
document.getElementById('quickPostForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const postData = {
        platform: formData.get('platform'),
        content: formData.get('content'),
        scheduled_time: formData.get('scheduled_time'),
        media_urls: [],
        tags: []
    };
    
    fetch('/api/social-media/schedule-post', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(postData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert('Post scheduled successfully!', 'success');
            e.target.reset();
            setTimeout(() => location.reload(), 1500);
        } else {
            showAlert('Failed to schedule post: ' + data.error, 'danger');
        }
    })
    .catch(error => {
        showAlert('Error scheduling post: ' + error, 'danger');
    });
});
</script>
{% endblock %}'''
    
    # Analytics template
    analytics_template = '''{% extends "base.html" %}

{% block title %}Analytics - Gym Bot Pro{% endblock %}
{% block page_title %}Analytics & Business Insights{% endblock %}

{% block content %}
<!-- KPI Overview -->
<div class="row mb-4">
    {% for kpi in kpis[:6] %}
    <div class="col-md-2">
        <div class="card metric-card">
            <div class="metric-value {% if kpi.trend == 'up' %}text-success{% elif kpi.trend == 'down' %}text-danger{% else %}text-info{% endif %}">
                {% if kpi.unit == 'USD' %}${% endif %}{{ "{:,.0f}".format(kpi.current_value) }}{% if kpi.unit == '%' %}%{% elif kpi.unit != 'USD' %} {{ kpi.unit.split('/')[0] if '/' in kpi.unit else kpi.unit }}{% endif %}
            </div>
            <div class="metric-label">{{ kpi.name }}</div>
            <small class="{% if kpi.trend == 'up' %}text-success{% elif kpi.trend == 'down' %}text-danger{% else %}text-muted{% endif %}">
                <i class="fas fa-arrow-{% if kpi.trend == 'up' %}up{% elif kpi.trend == 'down' %}down{% else %}right{% endif %} me-1"></i>
                {{ kpi.trend.title() }}
            </small>
        </div>
    </div>
    {% endfor %}
</div>

<!-- Revenue & Membership Analytics -->
<div class="row mb-4">
    <div class="col-lg-8">
        <div class="card">
            <div class="card-header">
                <h5><i class="fas fa-chart-line me-2"></i>Revenue Trends</h5>
            </div>
            <div class="card-body">
                <canvas id="revenueChart" class="chart-container"></canvas>
            </div>
        </div>
    </div>
    
    <div class="col-lg-4">
        <div class="card">
            <div class="card-header">
                <h5><i class="fas fa-pie-chart me-2"></i>Revenue Breakdown</h5>
            </div>
            <div class="card-body">
                <canvas id="revenueBreakdownChart" style="height: 250px;"></canvas>
                <div class="mt-3">
                    {% for source, data in revenue_analytics.revenue_breakdown.items() %}
                    <div class="d-flex justify-content-between mb-1">
                        <span>{{ source.replace('_', ' ').title() }}</span>
                        <span class="fw-bold">${{ "{:,.0f}".format(data.amount) }}</span>
                    </div>
                    {% endfor %}
                </div>
            </div>
        </div>
    </div>
</div>

<!-- Membership Analytics -->
<div class="row mb-4">
    <div class="col-lg-6">
        <div class="card">
            <div class="card-header">
                <h5><i class="fas fa-users me-2"></i>Membership Growth</h5>
            </div>
            <div class="card-body">
                <canvas id="membershipChart" style="height: 250px;"></canvas>
            </div>
        </div>
    </div>
    
    <div class="col-lg-6">
        <div class="card">
            <div class="card-header">
                <h5><i class="fas fa-clock me-2"></i>Peak Hours Analysis</h5>
            </div>
            <div class="card-body">
                <canvas id="peakHoursChart" style="height: 250px;"></canvas>
            </div>
        </div>
    </div>
</div>

<!-- AI Insights -->
<div class="row">
    <div class="col-12">
        <div class="card">
            <div class="card-header">
                <h5><i class="fas fa-brain me-2"></i>AI-Powered Business Insights</h5>
            </div>
            <div class="card-body">
                <div class="row">
                    {% for insight in insights %}
                    <div class="col-lg-4 mb-3">
                        <div class="border rounded p-3 h-100">
                            <div class="d-flex justify-content-between align-items-start mb-2">
                                <h6 class="mb-0">{{ insight.title }}</h6>
                                <span class="badge bg-{% if insight.priority == 'high' %}danger{% elif insight.priority == 'medium' %}warning{% else %}info{% endif %}">
                                    {{ insight.priority.title() }}
                                </span>
                            </div>
                            <p class="small text-muted mb-2">{{ insight.description }}</p>
                            <p class="small mb-2"><strong>Recommendation:</strong> {{ insight.recommendation }}</p>
                            <p class="small text-success mb-0"><strong>Impact:</strong> {{ insight.impact }}</p>
                        </div>
                    </div>
                    {% endfor %}
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script>
// Revenue Trend Chart
const revenueCtx = document.getElementById('revenueChart').getContext('2d');
new Chart(revenueCtx, {
    type: 'line',
    data: {
        labels: {{ revenue_analytics.monthly_trend | map(attribute='month') | list | tojson }},
        datasets: [{
            label: 'Revenue',
            data: {{ revenue_analytics.monthly_trend | map(attribute='revenue') | list | tojson }},
            borderColor: 'rgb(99, 102, 241)',
            backgroundColor: 'rgba(99, 102, 241, 0.1)',
            tension: 0.4
        }, {
            label: 'Target',
            data: {{ revenue_analytics.monthly_trend | map(attribute='target') | list | tojson }},
            borderColor: 'rgb(16, 185, 129)',
            borderDash: [5, 5],
            fill: false
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            y: {
                beginAtZero: true,
                ticks: {
                    callback: function(value) {
                        return '$' + value.toLocaleString();
                    }
                }
            }
        }
    }
});

// Revenue Breakdown Chart
const breakdownCtx = document.getElementById('revenueBreakdownChart').getContext('2d');
new Chart(breakdownCtx, {
    type: 'doughnut',
    data: {
        labels: {{ revenue_analytics.revenue_breakdown.keys() | list | map('replace', '_', ' ') | map('title') | list | tojson }},
        datasets: [{
            data: {{ revenue_analytics.revenue_breakdown.values() | map(attribute='amount') | list | tojson }},
            backgroundColor: [
                'rgb(99, 102, 241)',
                'rgb(16, 185, 129)',
                'rgb(245, 158, 11)',
                'rgb(239, 68, 68)'
            ]
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false
    }
});

// Membership Chart
const membershipCtx = document.getElementById('membershipChart').getContext('2d');
new Chart(membershipCtx, {
    type: 'bar',
    data: {
        labels: {{ membership_analytics.membership_trends | map(attribute='month') | list | tojson }},
        datasets: [{
            label: 'New Members',
            data: {{ membership_analytics.membership_trends | map(attribute='new') | list | tojson }},
            backgroundColor: 'rgba(16, 185, 129, 0.8)'
        }, {
            label: 'Cancelled',
            data: {{ membership_analytics.membership_trends | map(attribute='cancelled') | list | tojson }},
            backgroundColor: 'rgba(239, 68, 68, 0.8)'
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            y: {
                beginAtZero: true
            }
        }
    }
});

// Peak Hours Chart
const peakHoursCtx = document.getElementById('peakHoursChart').getContext('2d');
new Chart(peakHoursCtx, {
    type: 'bar',
    data: {
        labels: {{ operational_analytics.peak_hours | map(attribute='hour') | list | tojson }},
        datasets: [{
            label: 'Utilization %',
            data: {{ operational_analytics.peak_hours | map(attribute='utilization') | list | tojson }},
            backgroundColor: 'rgba(99, 102, 241, 0.8)'
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            y: {
                beginAtZero: true,
                max: 100,
                ticks: {
                    callback: function(value) {
                        return value + '%';
                    }
                }
            }
        }
    }
});
</script>
{% endblock %}'''
    
    # Feature unavailable template
    feature_unavailable_template = '''{% extends "base.html" %}

{% block title %}Feature Unavailable - Gym Bot Pro{% endblock %}
{% block page_title %}Feature Unavailable{% endblock %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-md-6">
        <div class="card text-center">
            <div class="card-body">
                <i class="fas fa-exclamation-triangle text-warning mb-3" style="font-size: 3rem;"></i>
                <h4>{{ feature }} Unavailable</h4>
                <p class="text-muted">This feature is not currently available. Please check your configuration.</p>
                <a href="{{ url_for('dashboard_home') }}" class="btn btn-primary">
                    <i class="fas fa-arrow-left me-1"></i> Back to Dashboard
                </a>
            </div>
        </div>
    </div>
</div>
{% endblock %}'''
    
    # Create template files
    template_files = {
        'base.html': base_template,
        'dashboard.html': dashboard_template,
        'social_media.html': social_media_template,
        'analytics.html': analytics_template,
        'feature_unavailable.html': feature_unavailable_template
    }
    
    for filename, content in template_files.items():
        filepath = os.path.join(templates_dir, filename)
        if not os.path.exists(filepath):
            with open(filepath, 'w') as f:
                f.write(content)


def initialize_dashboard():
    """Initialize the dashboard application."""
    log_message('INFO', 'Gym Bot Dashboard starting up', 'Dashboard')
    
    # Create templates
    create_templates()
    
    # Start background status updater
    status_thread = threading.Thread(target=update_system_status)
    status_thread.daemon = True
    status_thread.start()
    
    log_message('INFO', 'Dashboard initialization complete', 'Dashboard')


if __name__ == '__main__':
    # Initialize dashboard
    initialize_dashboard()
    
    # Get configuration
    host = os.environ.get('DASHBOARD_HOST', '127.0.0.1')
    port = int(os.environ.get('DASHBOARD_PORT', 5000))
    debug = os.environ.get('DASHBOARD_DEBUG', 'False').lower() == 'true'
    
    log_message('INFO', f'Starting Flask server on {host}:{port}', 'Flask')
    
    try:
        app.run(host=host, port=port, debug=debug)
    except KeyboardInterrupt:
        log_message('INFO', 'Dashboard shutdown requested', 'Flask')
        status_update_running = False
    except Exception as e:
        log_message('ERROR', f'Dashboard startup failed: {e}', 'Flask')
        raise