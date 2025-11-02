#!/usr/bin/env python3
"""
Admin AI Routes
Routes for AI-powered administrative assistance
"""

import logging
import json
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, current_app, session
from typing import Dict, Any

from ..services.admin_auth_service import require_admin, require_admin_api

logger = logging.getLogger(__name__)

# Create admin AI blueprint
admin_ai_bp = Blueprint('admin_ai', __name__, url_prefix='/admin/ai')

@admin_ai_bp.route('/dashboard')
@require_admin
def ai_dashboard():
    """AI-enhanced admin dashboard"""
    try:
        manager_id = session.get('manager_id')
        admin_service = current_app.admin_service

        # Get admin user info
        admin_user = admin_service.admin_schema.get_admin_user(manager_id)
        permissions = admin_service.get_admin_permissions(manager_id)

        # Get AI service availability
        ai_service = getattr(current_app, 'ai_service', None)
        ai_available = ai_service.is_available() if ai_service else False

        # Get AI usage stats
        ai_stats = ai_service.get_usage_stats() if ai_service else {}

        # Log dashboard access
        admin_service.log_admin_action(
            manager_id, 'ai_dashboard_access', 'Accessed AI admin dashboard'
        )

        return render_template('admin/ai_dashboard.html',
                             admin_user=admin_user,
                             permissions=permissions,
                             ai_available=ai_available,
                             ai_stats=ai_stats)

    except Exception as e:
        logger.error(f"❌ Error loading AI dashboard: {e}")
        return render_template('error.html', error='Failed to load AI dashboard')

@admin_ai_bp.route('/command', methods=['POST'])
@require_admin_api
def api_process_command():
    """Process natural language admin command"""
    try:
        data = request.get_json()
        command = data.get('command', '').strip()
        session_id = data.get('session_id')

        if not command:
            return jsonify({'success': False, 'error': 'Command is required'}), 400

        # Get current admin user
        manager_id = session.get('manager_id')
        admin_service = current_app.admin_service
        admin_user = admin_service.admin_schema.get_admin_user(manager_id)

        if not admin_user:
            return jsonify({'success': False, 'error': 'Admin user not found'}), 404

        # Get AI admin agent
        admin_ai_agent = getattr(current_app, 'admin_ai_agent', None)
        if not admin_ai_agent:
            return jsonify({'success': False, 'error': 'AI admin agent not available'}), 503

        # Process command (using asyncio to handle async function)
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(admin_ai_agent.process_command(command, admin_user, session_id))
        finally:
            loop.close()

        return jsonify(result)

    except Exception as e:
        logger.error(f"❌ Error processing admin AI command: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_ai_bp.route('/insights/<data_type>')
@require_admin_api
def api_generate_insights(data_type):
    """Generate AI insights for specific data types"""
    try:
        # Get current admin user
        manager_id = session.get('manager_id')
        admin_service = current_app.admin_service
        admin_user = admin_service.admin_schema.get_admin_user(manager_id)

        if not admin_user:
            return jsonify({'success': False, 'error': 'Admin user not found'}), 404

        # Get AI admin agent
        admin_ai_agent = getattr(current_app, 'admin_ai_agent', None)
        if not admin_ai_agent:
            return jsonify({'success': False, 'error': 'AI admin agent not available'}), 503

        # Generate insights
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(admin_ai_agent.generate_insights(data_type, admin_user))
        finally:
            loop.close()

        return jsonify({
            'success': True,
            'data_type': data_type,
            'insights': result,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"❌ Error generating AI insights: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_ai_bp.route('/suggestions', methods=['POST'])
@require_admin_api
def api_get_suggestions():
    """Get AI-powered action suggestions"""
    try:
        data = request.get_json()
        context = data.get('context', {})

        # Get AI admin agent
        admin_ai_agent = getattr(current_app, 'admin_ai_agent', None)
        if not admin_ai_agent:
            return jsonify({'success': False, 'error': 'AI admin agent not available'}), 503

        # Get suggestions
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            suggestions = loop.run_until_complete(admin_ai_agent.suggest_actions(context))
        finally:
            loop.close()

        return jsonify({
            'success': True,
            'suggestions': suggestions,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"❌ Error getting AI suggestions: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_ai_bp.route('/query', methods=['POST'])
@require_admin_api
def api_natural_query():
    """Process natural language database query"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()

        if not query:
            return jsonify({'success': False, 'error': 'Query is required'}), 400

        # Get current admin user for context
        manager_id = session.get('manager_id')
        admin_service = current_app.admin_service
        admin_user = admin_service.admin_schema.get_admin_user(manager_id)

        # Get database AI adapter
        db_adapter = getattr(current_app, 'db_ai_adapter', None)
        if not db_adapter:
            return jsonify({'success': False, 'error': 'Database AI adapter not available'}), 503

        # Process query
        context = {'current_user': admin_user} if admin_user else {}
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(db_adapter.process_natural_query(query, context))
        finally:
            loop.close()

        # Log the query
        if admin_user:
            admin_service.log_admin_action(
                manager_id, 'ai_database_query',
                f'AI Database Query: {query[:100]}',
                'ai_agent', 'database_query',
                success=result.get('success', False)
            )

        return jsonify(result)

    except Exception as e:
        logger.error(f"❌ Error processing natural query: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_ai_bp.route('/conversations')
@require_admin_api
def api_get_conversations():
    """Get list of active AI conversations"""
    try:
        # Get AI context manager
        context_manager = getattr(current_app, 'ai_context_manager', None)
        if not context_manager:
            return jsonify({'success': False, 'error': 'AI context manager not available'}), 503

        # Get active sessions for current user
        manager_id = session.get('manager_id')
        all_sessions = context_manager.get_active_sessions()
        user_sessions = [s for s in all_sessions if s['user_id'] == manager_id and s['agent_type'] == 'admin']

        return jsonify({
            'success': True,
            'conversations': user_sessions,
            'total_count': len(user_sessions)
        })

    except Exception as e:
        logger.error(f"❌ Error getting conversations: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_ai_bp.route('/conversations/<session_id>', methods=['DELETE'])
@require_admin_api
def api_close_conversation(session_id):
    """Close an AI conversation session"""
    try:
        # Get AI context manager
        context_manager = getattr(current_app, 'ai_context_manager', None)
        if not context_manager:
            return jsonify({'success': False, 'error': 'AI context manager not available'}), 503

        # Close session
        context_manager.close_session(session_id)

        return jsonify({
            'success': True,
            'message': f'Conversation {session_id} closed'
        })

    except Exception as e:
        logger.error(f"❌ Error closing conversation: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_ai_bp.route('/stats')
@require_admin_api
def api_get_ai_stats():
    """Get AI usage statistics"""
    try:
        # Get AI service
        ai_service = getattr(current_app, 'ai_service', None)
        if not ai_service:
            return jsonify({'success': False, 'error': 'AI service not available'}), 503

        # Get usage stats
        stats = ai_service.get_usage_stats()

        # Get context manager stats
        context_manager = getattr(current_app, 'ai_context_manager', None)
        if context_manager:
            context_stats = {
                'active_sessions': len(context_manager.get_active_sessions()),
                'admin_sessions': len([s for s in context_manager.get_active_sessions() if s['agent_type'] == 'admin'])
            }
            stats.update(context_stats)

        return jsonify({
            'success': True,
            'stats': stats,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"❌ Error getting AI stats: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500