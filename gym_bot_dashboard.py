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


def create_templates():
    """Create HTML templates if they don't exist."""
    templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
    os.makedirs(templates_dir, exist_ok=True)
    
    # Base template
    base_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Gym Bot Dashboard{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="{{ url_for('dashboard_home') }}">
                <i class="fas fa-dumbbell"></i> Gym Bot Dashboard
            </a>
            <div class="navbar-nav">
                <a class="nav-link" href="{{ url_for('dashboard_home') }}">Dashboard</a>
                <a class="nav-link" href="{{ url_for('workflows_page') }}">Workflows</a>
                <a class="nav-link" href="{{ url_for('logs_page') }}">Logs</a>
                <a class="nav-link" href="{{ url_for('settings_page') }}">Settings</a>
            </div>
        </div>
    </nav>
    
    <div class="container mt-4">
        {% block content %}{% endblock %}
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    {% block scripts %}{% endblock %}
</body>
</html>'''
    
    # Dashboard template
    dashboard_template = '''{% extends "base.html" %}

{% block title %}Dashboard - Gym Bot{% endblock %}

{% block content %}
<div class="row">
    <div class="col-12">
        <h1>Gym Bot System Dashboard</h1>
        <p class="text-muted">Monitor and control your gym automation system</p>
    </div>
</div>

<div class="row mb-4">
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">
                <h5><i class="fas fa-info-circle"></i> System Information</h5>
            </div>
            <div class="card-body">
                <p><strong>GCP Project:</strong> {{ project_id }}</p>
                <p><strong>Last Update:</strong> {{ status.last_update or 'Never' }}</p>
                <button class="btn btn-primary btn-sm" onclick="refreshStatus()">
                    <i class="fas fa-refresh"></i> Refresh Status
                </button>
            </div>
        </div>
    </div>
    
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">
                <h5><i class="fas fa-chart-bar"></i> Quick Stats</h5>
            </div>
            <div class="card-body">
                <div class="row">
                    <div class="col-6">
                        <div class="text-center">
                            <h3 class="text-success">{{ status.services|length }}</h3>
                            <small class="text-muted">Services</small>
                        </div>
                    </div>
                    <div class="col-6">
                        <div class="text-center">
                            <h3 class="text-info">{{ status.logs|length }}</h3>
                            <small class="text-muted">Log Entries</small>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<div class="row">
    <div class="col-12">
        <div class="card">
            <div class="card-header">
                <h5><i class="fas fa-heartbeat"></i> Service Status</h5>
            </div>
            <div class="card-body">
                {% if status.services %}
                    <div class="row">
                        {% for service, info in status.services.items() %}
                        <div class="col-md-6 mb-3">
                            <div class="d-flex align-items-center">
                                {% if info.status == 'healthy' %}
                                    <i class="fas fa-check-circle text-success me-2"></i>
                                {% elif info.status == 'error' %}
                                    <i class="fas fa-times-circle text-danger me-2"></i>
                                {% else %}
                                    <i class="fas fa-question-circle text-warning me-2"></i>
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
</div>

<div class="row mt-4">
    <div class="col-12">
        <div class="card">
            <div class="card-header">
                <h5><i class="fas fa-clock"></i> Recent Logs</h5>
            </div>
            <div class="card-body">
                {% if status.logs %}
                    <div class="table-responsive">
                        <table class="table table-sm">
                            <thead>
                                <tr>
                                    <th>Time</th>
                                    <th>Level</th>
                                    <th>Component</th>
                                    <th>Message</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for log in status.logs[:10] %}
                                <tr>
                                    <td>{{ log.timestamp }}</td>
                                    <td>
                                        <span class="badge bg-{% if log.level == 'ERROR' %}danger{% elif log.level == 'WARNING' %}warning{% else %}info{% endif %}">
                                            {{ log.level }}
                                        </span>
                                    </td>
                                    <td>{{ log.component }}</td>
                                    <td>{{ log.message }}</td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                    <a href="{{ url_for('logs_page') }}" class="btn btn-outline-primary btn-sm">View All Logs</a>
                {% else %}
                    <p class="text-muted">No logs available.</p>
                {% endif %}
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script>
function refreshStatus() {
    fetch('/api/refresh-status')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                alert('Failed to refresh status: ' + data.error);
            }
        })
        .catch(error => {
            alert('Error refreshing status: ' + error);
        });
}

// Auto-refresh every 60 seconds
setInterval(() => {
    refreshStatus();
}, 60000);
</script>
{% endblock %}'''
    
    # Create template files
    template_files = {
        'base.html': base_template,
        'dashboard.html': dashboard_template
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