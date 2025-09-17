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
    
    # Add a test route for collections without any authentication
    @app.route('/test-collections-api')
    def test_collections_api():
        """Test collections API without authentication"""
        try:
            import sqlite3
            import json
            
            # Connect to local SQLite database
            conn = sqlite3.connect('gym_bot.db')
            cursor = conn.cursor()
            
            # Get past due members
            cursor.execute("""
                SELECT 
                    full_name as name,
                    email,
                    phone,
                    amount_past_due as past_due_amount,
                    'member' as type
                FROM members 
                WHERE amount_past_due > 0
                ORDER BY amount_past_due DESC
                LIMIT 5
            """)
            
            past_due_members = cursor.fetchall()
            
            # Get past due training clients
            cursor.execute("""
                SELECT 
                    member_name as name,
                    email,
                    phone,
                    past_due_amount,
                    'training_client' as type
                FROM training_clients 
                WHERE past_due_amount > 0
                ORDER BY past_due_amount DESC
                LIMIT 5
            """)
            
            past_due_training = cursor.fetchall()
            
            # Combine data
            all_past_due = []
            
            # Add members
            for member in past_due_members:
                all_past_due.append({
                    'name': member[0], 'email': member[1], 'phone': member[2],
                    'past_due_amount': member[3], 'type': member[4]
                })
            
            # Add training clients
            for client in past_due_training:
                all_past_due.append({
                    'name': client[0], 'email': client[1], 'phone': client[2],
                    'past_due_amount': client[3], 'type': client[4]
                })
            
            conn.close()
            
            return {
                'success': True,
                'past_due_data': all_past_due,
                'total_count': len(all_past_due)
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}