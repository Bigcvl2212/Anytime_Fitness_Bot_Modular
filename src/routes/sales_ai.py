#!/usr/bin/env python3
"""
Sales AI Routes
Routes for AI-powered sales automation and revenue generation
"""

import logging
import json
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, current_app, session, redirect
from typing import Dict, Any

from .auth import require_auth

logger = logging.getLogger(__name__)

# Create sales AI blueprint
sales_ai_bp = Blueprint('sales_ai', __name__, url_prefix='/sales-ai')

@sales_ai_bp.route('/dashboard')
@require_auth
def sales_ai_dashboard():
    """REDIRECT: Sales AI is now unified with Messaging Dashboard."""
    logger.info("🔀 Redirecting /sales-ai/dashboard to /messaging")
    return redirect('/messaging')

@sales_ai_bp.route('/unified')
@require_auth
def unified_sales_inbox():
    """REDIRECT: Unified dashboard is now at /messaging."""
    logger.info("🔀 Redirecting /sales-ai/unified to /messaging")
    return redirect('/messaging')

@sales_ai_bp.route('/command', methods=['POST'])
@require_auth
def api_process_sales_command():
    """Process natural language sales command"""
    try:
        data = request.get_json()
        command = data.get('command', '').strip()
        session_id = data.get('session_id')

        if not command:
            return jsonify({'success': False, 'error': 'Command is required'}), 400

        # Get current user info
        user_info = {
            'manager_id': session.get('manager_id', 'unknown'),
            'user_email': session.get('user_email', 'unknown'),
            'club_id': session.get('club_id')
        }

        # Get AI sales agent
        sales_ai_agent = getattr(current_app, 'sales_ai_agent', None)
        if not sales_ai_agent:
            return jsonify({'success': False, 'error': 'Sales AI agent not available'}), 503

        # Process command
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(sales_ai_agent.process_command(command, user_info, session_id))
        finally:
            loop.close()

        return jsonify(result)

    except Exception as e:
        logger.error(f"❌ Error processing sales AI command: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@sales_ai_bp.route('/collections')
@require_auth
def api_get_collections_data():
    """Get AI-enhanced collections data"""
    try:
        # Get filter parameters
        min_amount = request.args.get('min_amount', 0, type=float)
        filters = {'min_amount': min_amount} if min_amount > 0 else {}

        # Get current user info
        user_info = {
            'manager_id': session.get('manager_id', 'unknown'),
            'user_email': session.get('user_email', 'unknown')
        }

        # Get AI sales agent
        sales_ai_agent = getattr(current_app, 'sales_ai_agent', None)
        if not sales_ai_agent:
            return jsonify({'success': False, 'error': 'Sales AI agent not available'}), 503

        # Handle past due clients with AI
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(sales_ai_agent.handle_past_due_clients(filters))
        finally:
            loop.close()

        return jsonify(result)

    except Exception as e:
        logger.error(f"❌ Error getting collections data: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@sales_ai_bp.route('/collections/invoice', methods=['POST'])
@require_auth
def api_ai_create_invoice():
    """Create invoice with AI optimization"""
    try:
        data = request.get_json()
        member_id = data.get('member_id')
        amount = data.get('amount')

        if not member_id or not amount:
            return jsonify({'success': False, 'error': 'Member ID and amount are required'}), 400

        # Get member info
        db_manager = current_app.db_manager
        member_query = """
            SELECT prospect_id, first_name, last_name, email, mobile_phone, amount_past_due
            FROM members
            WHERE prospect_id = ? OR id = ?
        """
        member_result = db_manager.execute_query(member_query, (member_id, member_id), fetch_one=True)

        if not member_result:
            return jsonify({'success': False, 'error': 'Member not found'}), 404

        member = dict(member_result)
        member_name = f"{member.get('first_name', '')} {member.get('last_name', '')}".strip()
        email = member.get('email')
        mobile_phone = member.get('mobile_phone')

        # Use AI to optimize invoice details
        sales_ai_agent = getattr(current_app, 'sales_ai_agent', None)
        if sales_ai_agent:
            # Get AI recommendations for invoice
            ai_prompt = f"""Optimize invoice details for member {member_name} with past due amount ${amount}:
1. Suggest professional invoice description
2. Recommend payment terms
3. Suggest follow-up strategy"""

            try:
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    ai_response = loop.run_until_complete(sales_ai_agent.ai_service.simple_query(ai_prompt))
                    ai_recommendations = ai_response
                finally:
                    loop.close()
            except:
                ai_recommendations = "Standard payment terms recommended."
        else:
            ai_recommendations = "AI optimization not available."

        # Create invoice using existing Square integration
        from ..services.payments.square_client_simple import create_square_invoice

        # Determine delivery method and contact
        delivery_method = "email" if email else "sms"
        contact_info = email if email else mobile_phone

        description = f"Payment for {member_name} - Past Due Amount: ${amount}"

        result = create_square_invoice(
            member_name=member_name,
            contact_info=contact_info,
            amount=float(amount),
            description=description,
            delivery_method=delivery_method
        )

        if result.get('success'):
            return jsonify({
                'success': True,
                'invoice_url': result.get('invoice_url'),
                'member_name': member_name,
                'amount': amount,
                'delivery_method': delivery_method,
                'contact_info': contact_info,
                'ai_recommendations': ai_recommendations
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Failed to create invoice')
            }), 500

    except Exception as e:
        logger.error(f"❌ Error creating AI-optimized invoice: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@sales_ai_bp.route('/campaigns')
@require_auth
def api_get_campaign_data():
    """Get AI-enhanced campaign data"""
    try:
        # Get campaign service
        campaign_service = getattr(current_app, 'campaign_service', None)
        if not campaign_service:
            return jsonify({'success': False, 'error': 'Campaign service not available'}), 503

        # Get campaign status for different categories
        campaigns_data = []
        categories = ['good_standing', 'past_due_6_30', 'past_due_30_plus', 'expiring_soon']

        for category in categories:
            try:
                status = campaign_service.get_campaign_status(category)
                campaigns_data.append({
                    'category': category,
                    'status': status
                })
            except Exception as e:
                logger.warning(f"⚠️ Error getting campaign status for {category}: {e}")

        # Get AI recommendations for campaigns
        sales_ai_agent = getattr(current_app, 'sales_ai_agent', None)
        ai_recommendations = ""
        if sales_ai_agent:
            try:
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    ai_recommendations = loop.run_until_complete(sales_ai_agent.ai_service.simple_query(
                        "Provide campaign recommendations based on current gym member engagement trends."
                    ))
                finally:
                    loop.close()
            except:
                ai_recommendations = "AI recommendations not available."

        return jsonify({
            'success': True,
            'campaigns': campaigns_data,
            'ai_recommendations': ai_recommendations,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"❌ Error getting campaign data: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@sales_ai_bp.route('/campaigns/optimize', methods=['POST'])
@require_auth
def api_optimize_campaign():
    """Optimize campaign with AI"""
    try:
        data = request.get_json()
        campaign_category = data.get('category')
        message_content = data.get('message', '')

        if not campaign_category:
            return jsonify({'success': False, 'error': 'Campaign category is required'}), 400

        # Get AI sales agent
        sales_ai_agent = getattr(current_app, 'sales_ai_agent', None)
        if not sales_ai_agent:
            return jsonify({'success': False, 'error': 'Sales AI agent not available'}), 503

        # Use AI to optimize campaign
        optimization_prompt = f"""Optimize this marketing campaign:
Category: {campaign_category}
Current Message: {message_content}

Provide:
1. Improved message content
2. Optimal send timing
3. Expected engagement rate
4. A/B testing suggestions"""

        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            ai_response = loop.run_until_complete(sales_ai_agent.ai_service.simple_query(optimization_prompt))
        finally:
            loop.close()

        return jsonify({
            'success': True,
            'category': campaign_category,
            'original_message': message_content,
            'ai_optimization': ai_response,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"❌ Error optimizing campaign: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@sales_ai_bp.route('/analytics')
@require_auth
def api_get_sales_analytics():
    """Get AI-powered sales analytics"""
    try:
        # Get basic sales data
        db_manager = current_app.db_manager

        # Get past due analytics
        past_due_query = """
            SELECT
                COUNT(*) as total_past_due,
                SUM(amount_past_due) as total_amount,
                AVG(amount_past_due) as avg_amount
            FROM members
            WHERE amount_past_due > 0
        """
        past_due_result = db_manager.execute_query(past_due_query, fetch_one=True)

        # Get member analytics
        member_query = """
            SELECT
                COUNT(*) as total_members,
                COUNT(CASE WHEN status = 'Active' THEN 1 END) as active_members,
                COUNT(CASE WHEN amount_past_due > 0 THEN 1 END) as past_due_members
            FROM members
        """
        member_result = db_manager.execute_query(member_query, fetch_one=True)

        analytics_data = {
            'past_due_stats': dict(past_due_result) if past_due_result else {},
            'member_stats': dict(member_result) if member_result else {},
            'timestamp': datetime.now().isoformat()
        }

        # Get AI insights
        sales_ai_agent = getattr(current_app, 'sales_ai_agent', None)
        ai_insights = ""
        if sales_ai_agent:
            try:
                insights_prompt = f"""Analyze these gym sales metrics and provide insights:
{json.dumps(analytics_data, indent=2)}

Provide:
1. Key performance indicators
2. Revenue optimization opportunities
3. Collection strategy recommendations
4. Member retention insights"""

                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    ai_insights = loop.run_until_complete(sales_ai_agent.ai_service.simple_query(insights_prompt))
                finally:
                    loop.close()
            except:
                ai_insights = "AI insights not available."

        return jsonify({
            'success': True,
            'analytics_data': analytics_data,
            'ai_insights': ai_insights
        })

    except Exception as e:
        logger.error(f"❌ Error getting sales analytics: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@sales_ai_bp.route('/conversations')
@require_auth
def api_get_sales_conversations():
    """Get list of active sales AI conversations"""
    try:
        # Get AI context manager
        context_manager = getattr(current_app, 'ai_context_manager', None)
        if not context_manager:
            return jsonify({'success': False, 'error': 'AI context manager not available'}), 503

        # Get active sessions for current user
        manager_id = session.get('manager_id', 'unknown')
        all_sessions = context_manager.get_active_sessions()
        user_sessions = [s for s in all_sessions if s['user_id'] == manager_id and s['agent_type'] == 'sales']

        return jsonify({
            'success': True,
            'conversations': user_sessions,
            'total_count': len(user_sessions)
        })

    except Exception as e:
        logger.error(f"❌ Error getting sales conversations: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500