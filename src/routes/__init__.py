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
from .admin import admin_bp
from .admin_ai import admin_ai_bp
from .club_selection import club_selection_bp
from .debug_session import debug_bp
from .ai_settings import ai_settings_bp, init_ai_settings_routes
from ..services.progressive_loading import progressive_bp

# Import Phase 3 AI routes
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from routes.ai_workflows import blueprint as ai_workflows_bp
from routes.ai_conversation import blueprint as ai_conversation_bp
from routes.settings import blueprint as settings_bp

def register_blueprints(app):
    """Register all route blueprints with the Flask app"""
    from flask import redirect, url_for, session, render_template
    from .auth import require_auth

    # Register template context processor for safe admin access
    @app.context_processor
    def inject_admin_context():
        """Safely inject admin context into templates"""
        admin_context = {
            'is_admin': False,
            'admin_permissions': [],
            'admin_user': None
        }

        try:
            # Only check admin status if user is authenticated and admin service exists
            if (session.get('authenticated') and
                session.get('manager_id') and
                hasattr(app, 'admin_service') and
                app.admin_service is not None):

                manager_id = session.get('manager_id')
                admin_context['is_admin'] = app.admin_service.is_admin(manager_id)

                if admin_context['is_admin']:
                    admin_context['admin_permissions'] = app.admin_service.get_admin_permissions(manager_id)
                    admin_context['admin_user'] = app.admin_service.admin_schema.get_admin_user(manager_id)

        except Exception as e:
            # Silently fail - don't break template rendering
            app.logger.debug(f"Admin context injection error: {e}")

        return admin_context

    # Register blueprints
    app.register_blueprint(auth_bp)  # Register auth blueprint first
    app.register_blueprint(club_selection_bp)  # Register club selection blueprint
    app.register_blueprint(admin_bp)  # Register admin blueprint
    app.register_blueprint(admin_ai_bp)  # Register admin AI blueprint
    app.register_blueprint(debug_bp)  # Register debug blueprint
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(members_bp)
    app.register_blueprint(prospects_bp)
    app.register_blueprint(training_bp)
    app.register_blueprint(calendar_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(progressive_bp, url_prefix='/api')  # Progressive loading API
    app.register_blueprint(messaging_bp)
    
    # Register Phase 3 AI routes
    app.register_blueprint(ai_workflows_bp)  # /api/ai/workflows/*
    app.register_blueprint(ai_conversation_bp)  # /api/ai/conversation/*
    app.register_blueprint(settings_bp)  # /api/settings/*
    app.register_blueprint(ai_settings_bp)  # /ai-settings page + /api/ai/* endpoints
    app.logger.info("✅ Phase 3 AI routes registered")
    app.logger.info("✅ AI Settings routes registered")
    app.logger.info("✅ Settings API registered")
    
    # Root route is handled directly by dashboard blueprint - no redirect needed
    
    # Add a simple health check route
    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'timestamp': '2025-01-27T00:00:00Z'}
    
    # Add performance demo route
    @app.route('/performance-demo')
    def performance_demo():
        """Performance optimization demo page"""
        return render_template('performance_demo.html')
    
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