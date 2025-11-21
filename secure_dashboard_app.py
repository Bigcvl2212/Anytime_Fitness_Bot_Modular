#!/usr/bin/env python3
"""
Secure Dashboard Application with Manager Authentication

This application provides secure login for managers and uses their credentials
to access ClubOS and ClubHub APIs safely through Google Secret Manager.
"""

import os
import secrets
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_session import Session
import logging
from datetime import datetime
from src.services.authentication.secure_auth_service import SecureAuthService
from src.services.authentication.secure_secrets_manager import SecureSecretsManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Security configuration
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', secrets.token_urlsafe(32))
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_KEY_PREFIX'] = 'anytime_fitness_'
app.config['SESSION_FILE_THRESHOLD'] = 100

# Initialize Flask-Session
Session(app)

# Initialize authentication service
auth_service = SecureAuthService()
secrets_manager = SecureSecretsManager()

# Security headers middleware
@app.after_request
def add_security_headers(response):
    """Add security headers to all responses"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
    return response

@app.route('/')
def index():
    """Home page - redirect to dashboard if authenticated, otherwise login"""
    is_valid, manager_id = auth_service.validate_session()
    
    if is_valid:
        return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Manager login page"""
    if request.method == 'GET':
        # Check if already authenticated
        is_valid, manager_id = auth_service.validate_session()
        if is_valid:
            return redirect(url_for('dashboard'))
        
        return render_template('login.html')
    
    elif request.method == 'POST':
        try:
            # Get credentials from form
            clubos_username = request.form.get('clubos_username', '').strip()
            clubos_password = request.form.get('clubos_password', '').strip()
            clubhub_email = request.form.get('clubhub_email', '').strip()
            clubhub_password = request.form.get('clubhub_password', '').strip()
            
            # Validate form data
            if not all([clubos_username, clubos_password, clubhub_email, clubhub_password]):
                flash('All credential fields are required.', 'error')
                return render_template('login.html', error='All credential fields are required.')
            
            # Attempt authentication
            success, manager_id, error_msg = auth_service.authenticate_manager(
                clubos_username, clubos_password, clubhub_email, clubhub_password
            )
            
            if success:
                # Create session
                session_token = auth_service.create_session(manager_id)
                
                logger.info(f"✅ Manager {manager_id} logged in successfully from {request.remote_addr}")
                flash(f'Welcome! Successfully authenticated as manager {manager_id}.', 'success')
                return redirect(url_for('dashboard'))
            else:
                logger.warning(f"❌ Failed login attempt from {request.remote_addr}: {error_msg}")
                flash(error_msg, 'error')
                return render_template('login.html', error=error_msg)
                
        except Exception as e:
            logger.error(f"❌ Login error: {e}")
            flash('An unexpected error occurred. Please try again.', 'error')
            return render_template('login.html', error='An unexpected error occurred. Please try again.')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Manager registration page"""
    if request.method == 'GET':
        return render_template('register.html')
    
    elif request.method == 'POST':
        try:
            # Get credentials from form
            clubos_username = request.form.get('clubos_username', '').strip()
            clubos_password = request.form.get('clubos_password', '').strip()
            clubhub_email = request.form.get('clubhub_email', '').strip()
            clubhub_password = request.form.get('clubhub_password', '').strip()
            
            # Validate form data
            if not all([clubos_username, clubos_password, clubhub_email, clubhub_password]):
                flash('All credential fields are required.', 'error')
                return render_template('register.html', error='All credential fields are required.')
            
            # Store credentials
            success, manager_id, error_msg = auth_service.store_manager_credentials(
                clubos_username, clubos_password, clubhub_email, clubhub_password
            )
            
            if success:
                logger.info(f"✅ Manager {manager_id} registered successfully from {request.remote_addr}")
                flash(f'Registration successful! Your manager ID is: {manager_id}. You can now login.', 'success')
                return redirect(url_for('login'))
            else:
                logger.warning(f"❌ Registration failed from {request.remote_addr}: {error_msg}")
                flash(error_msg, 'error')
                return render_template('register.html', error=error_msg)
                
        except Exception as e:
            logger.error(f"❌ Registration error: {e}")
            flash('An unexpected error occurred. Please try again.', 'error')
            return render_template('register.html', error='An unexpected error occurred. Please try again.')

@app.route('/logout')
def logout():
    """Logout and clear session"""
    manager_id = session.get('manager_id', 'unknown')
    auth_service.logout()
    
    logger.info(f"✅ Manager {manager_id} logged out")
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    """Main dashboard - requires authentication"""
    is_valid, manager_id = auth_service.validate_session()
    
    if not is_valid:
        flash('Please login to access the dashboard.', 'error')
        return redirect(url_for('login'))
    
    # Get session info
    session_info = auth_service.get_session_info()
    
    # Get credentials for API calls (without exposing passwords)
    credentials = auth_service.get_manager_credentials(manager_id)
    if credentials:
        clubos_username = credentials.get('clubos_username', 'Not available')
        clubhub_email = credentials.get('clubhub_email', 'Not available')
    else:
        clubos_username = 'Error retrieving credentials'
        clubhub_email = 'Error retrieving credentials'
    
    dashboard_data = {
        'manager_id': manager_id,
        'clubos_username': clubos_username,
        'clubhub_email': clubhub_email,
        'session_info': session_info,
        'login_time': session_info.get('login_time'),
        'last_activity': session_info.get('last_activity')
    }
    
    return render_template('secure_dashboard.html', **dashboard_data)

@app.route('/api/credentials/<manager_id>')
def api_get_credentials(manager_id):
    """API endpoint to get credentials for authenticated manager"""
    is_valid, session_manager_id = auth_service.validate_session()
    
    if not is_valid:
        return jsonify({'error': 'Not authenticated'}), 401
    
    if session_manager_id != manager_id:
        logger.warning(f"❌ Unauthorized credential access attempt: {session_manager_id} tried to access {manager_id}")
        return jsonify({'error': 'Unauthorized'}), 403
    
    credentials = auth_service.get_manager_credentials(manager_id)
    
    if credentials:
        # Return credentials without exposing them in logs
        return jsonify({
            'success': True,
            'clubos_username': credentials['clubos_username'],
            'clubos_password': credentials['clubos_password'],
            'clubhub_email': credentials['clubhub_email'],
            'clubhub_password': credentials['clubhub_password']
        })
    else:
        return jsonify({'error': 'Credentials not found'}), 404

@app.route('/api/session')
def api_session_info():
    """API endpoint to get session information"""
    session_info = auth_service.get_session_info()
    return jsonify(session_info)

@app.route('/settings')
def settings():
    """Settings page for updating credentials"""
    is_valid, manager_id = auth_service.validate_session()
    
    if not is_valid:
        flash('Please login to access settings.', 'error')
        return redirect(url_for('login'))
    
    # Get current credentials (without passwords for display)
    credentials = auth_service.get_manager_credentials(manager_id)
    if credentials:
        display_creds = {
            'clubos_username': credentials['clubos_username'],
            'clubhub_email': credentials['clubhub_email']
        }
    else:
        display_creds = {
            'clubos_username': 'Error retrieving',
            'clubhub_email': 'Error retrieving'
        }
    
    return render_template('settings.html', manager_id=manager_id, credentials=display_creds)

@app.route('/health')
def health_check():
    """Health check endpoint"""
    try:
        # Check secrets manager connectivity
        test_managers = secrets_manager.list_managers()
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'secrets_manager': 'connected',
            'registered_managers': len(test_managers)
        })
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'timestamp': datetime.now().isoformat(),
            'error': str(e)
        }), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return render_template('error.html', 
                         error_code=404, 
                         error_message="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"❌ Internal server error: {error}")
    return render_template('error.html', 
                         error_code=500, 
                         error_message="Internal server error"), 500

@app.errorhandler(403)
def forbidden(error):
    """Handle 403 errors"""
    return render_template('error.html', 
                         error_code=403, 
                         error_message="Access forbidden"), 403

if __name__ == '__main__':
    # Set up logging
    if not app.debug:
        logging.basicConfig(level=logging.INFO)
    
    logger.info("🚀 Starting Secure Dashboard Application")
    logger.info(f"🔐 Secret Manager Project: {secrets_manager.project_id}")
    
    # Run the app
    port = int(os.getenv('PORT', 5000))
    debug_mode = os.getenv('FLASK_ENV') == 'development'
    
    app.run(host='0.0.0.0', port=port, debug=debug_mode)