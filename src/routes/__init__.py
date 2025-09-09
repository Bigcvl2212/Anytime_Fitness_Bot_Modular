#!/usr/bin/env python3
"""
Routes package for the Anytime Fitness Dashboard
"""

from .dashboard import dashboard_bp
from .members import members_bp
from .prospects import prospects_bp
from .training import training_bp
from .calendar import calendar_bp
from .api import api_bp
from .messaging import messaging_bp
from .auth import auth_bp
from .club_selection import club_selection_bp

def register_blueprints(app):
    """Register all route blueprints with the Flask app"""
    from flask import redirect, url_for, session
    from .auth import require_auth
    
    # Register blueprints
    app.register_blueprint(auth_bp)  # Register auth blueprint first
    app.register_blueprint(club_selection_bp)  # Register club selection blueprint
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(members_bp)
    app.register_blueprint(prospects_bp)
    app.register_blueprint(training_bp)
    app.register_blueprint(calendar_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(messaging_bp)
    
    # Add root route that requires authentication
    @app.route('/')
    @require_auth
    def root():
        """Root route - redirects authenticated users to dashboard"""
        return redirect(url_for('dashboard.dashboard'))
    
    # Add a simple health check route
    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'timestamp': '2025-01-27T00:00:00Z'}
