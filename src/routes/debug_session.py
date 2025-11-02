#!/usr/bin/env python3
"""
Debug Session Route - Shows exactly what's in the session
"""

import logging
from flask import Blueprint, request, session, jsonify, current_app
from datetime import datetime

logger = logging.getLogger(__name__)

# Create debug blueprint
debug_bp = Blueprint('debug', __name__, url_prefix='/debug')

@debug_bp.route('/session')
def debug_session():
    """Show complete session data"""
    try:
        session_data = {
            'session_keys': list(session.keys()),
            'session_data': dict(session),
            'session_permanent': session.permanent,
            'session_modified': session.modified,
            'request_cookies': dict(request.cookies),
            'request_headers': dict(request.headers),
            'current_time': datetime.now().isoformat(),
            'flask_config': {
                'SESSION_COOKIE_NAME': current_app.config.get('SESSION_COOKIE_NAME'),
                'SESSION_COOKIE_SECURE': current_app.config.get('SESSION_COOKIE_SECURE'),
                'SESSION_COOKIE_HTTPONLY': current_app.config.get('SESSION_COOKIE_HTTPONLY'),
                'SESSION_COOKIE_SAMESITE': current_app.config.get('SESSION_COOKIE_SAMESITE'),
                'SECRET_KEY_SET': bool(current_app.config.get('SECRET_KEY')),
            }
        }

        return jsonify(session_data)

    except Exception as e:
        logger.error(f"Error getting session data: {e}")
        return jsonify({'error': str(e)}), 500

@debug_bp.route('/clear-session')
def clear_session():
    """Clear the session for testing"""
    try:
        session.clear()
        return jsonify({'message': 'Session cleared'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@debug_bp.route('/set-test-session')
def set_test_session():
    """Set a test session for debugging"""
    try:
        session.clear()
        session.permanent = True
        session['authenticated'] = True
        session['manager_id'] = 'test_manager_debug'
        session['selected_clubs'] = ['test_club_123']
        session['login_time'] = datetime.now().isoformat()
        session['last_activity'] = datetime.now().isoformat()
        session.modified = True

        return jsonify({
            'message': 'Test session set',
            'session_data': dict(session)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@debug_bp.route('/test-dashboard')
def test_dashboard():
    """Test dashboard access without auth - shows what auth decorator sees"""
    try:
        from flask import session as flask_session

        # Show what the auth decorator would see
        auth_data = {
            'session_exists': bool(flask_session),
            'session_keys': list(flask_session.keys()) if flask_session else [],
            'authenticated': flask_session.get('authenticated') if flask_session else None,
            'manager_id': flask_session.get('manager_id') if flask_session else None,
            'selected_clubs': flask_session.get('selected_clubs') if flask_session else None,
            'session_permanent': flask_session.permanent if flask_session else None,
            'cookies': dict(request.cookies),
            'would_pass_auth': bool(
                flask_session and
                flask_session.get('authenticated') and
                flask_session.get('manager_id')
            )
        }

        return jsonify(auth_data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500