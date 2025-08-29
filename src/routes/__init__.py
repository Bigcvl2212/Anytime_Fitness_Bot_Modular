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

def register_blueprints(app):
    """Register all route blueprints with the Flask app"""
    
    # Register blueprints
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(members_bp)
    app.register_blueprint(prospects_bp)
    app.register_blueprint(training_bp)
    app.register_blueprint(calendar_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(messaging_bp)
    
    # Add a simple health check route
    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'timestamp': '2025-01-27T00:00:00Z'}
