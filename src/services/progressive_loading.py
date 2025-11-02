#!/usr/bin/env python3
"""
Progressive Loading Framework
Enable fast initial page loads with progressive data loading
"""

from flask import Blueprint, jsonify, render_template, request, current_app
import logging
import json
from datetime import datetime
import time

from ..services.performance_cache import cache_medium, cache_short, performance_cache

logger = logging.getLogger(__name__)

progressive_bp = Blueprint('progressive', __name__)

class ProgressiveLoader:
    """Framework for progressive page loading"""
    
    @staticmethod
    def get_page_skeleton(page_type: str, **kwargs):
        """Return page skeleton for immediate rendering"""
        skeletons = {
            'dashboard': {
                'title': 'Dashboard',
                'cards': [
                    {'id': 'total-members', 'title': 'Total Members', 'loading': True},
                    {'id': 'total-prospects', 'title': 'Total Prospects', 'loading': True},
                    {'id': 'training-clients', 'title': 'Training Clients', 'loading': True},
                    {'id': 'monthly-revenue', 'title': 'Monthly Revenue', 'loading': True},
                ],
                'recent_members': [],
                'todays_events': []
            },
            'members': {
                'title': 'Members',
                'total_count': 0,
                'members': [],
                'loading': True,
                'filters': ['all', 'active', 'ppv', 'comp', 'frozen'],
                'page': 1,
                'total_pages': 1
            },
            'prospects': {
                'title': 'Prospects',
                'total_count': 0,
                'prospects': [],
                'loading': True,
                'page': 1,
                'total_pages': 1
            },
            'training_clients': {
                'title': 'Training Clients',
                'total_count': 0,
                'training_clients': [],
                'loading': True,
                'page': 1,
                'total_pages': 1
            }
        }
        
        return skeletons.get(page_type, {'title': page_type.title(), 'loading': True})
    
    @staticmethod
    def create_loading_response(message: str = "Loading..."):
        """Create standardized loading response"""
        return {
            'loading': True,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'data': None
        }

# API Routes for Progressive Loading

@progressive_bp.route('/api/progressive/dashboard-summary')
@cache_short
def get_dashboard_summary():
    """Get dashboard summary data (cached for 1 minute)"""
    try:
        logger.info("📊 Loading dashboard summary...")
        start_time = time.time()
        
        db_manager = current_app.db_manager
        
        # Get basic counts (fast queries with indexes)
        summary = {
            'total_members': db_manager.get_member_count(),
            'total_prospects': db_manager.get_prospect_count(), 
            'total_training_clients': db_manager.get_training_client_count(),
            'loading': False,
            'loaded_at': datetime.now().isoformat(),
            'load_time': 0
        }
        
        load_time = time.time() - start_time
        summary['load_time'] = round(load_time * 1000, 2)  # milliseconds
        
        logger.info(f"✅ Dashboard summary loaded in {load_time:.3f}s")
        
        return jsonify(summary)
        
    except Exception as e:
        logger.error(f"❌ Error loading dashboard summary: {e}")
        return jsonify({
            'error': str(e),
            'loading': False,
            'total_members': 0,
            'total_prospects': 0,
            'total_training_clients': 0
        }), 500

@progressive_bp.route('/api/progressive/members-summary')
@cache_short
def get_members_summary():
    """Get members page summary data"""
    try:
        logger.info("👥 Loading members summary...")
        start_time = time.time()
        
        db_manager = current_app.db_manager
        
        # Get category breakdown (fast with indexes)
        category_counts = db_manager.get_category_counts()
        
        summary = {
            'total_members': sum(category_counts.values()),
            'category_counts': category_counts,
            'loading': False,
            'loaded_at': datetime.now().isoformat(),
            'load_time': round((time.time() - start_time) * 1000, 2)
        }
        
        logger.info(f"✅ Members summary loaded in {summary['load_time']}ms")
        
        return jsonify(summary)
        
    except Exception as e:
        logger.error(f"❌ Error loading members summary: {e}")
        return jsonify({
            'error': str(e),
            'loading': False,
            'total_members': 0,
            'category_counts': {}
        }), 500

@progressive_bp.route('/api/progressive/members-list')
@cache_medium
def get_members_list():
    """Get paginated members list with search/filter"""
    try:
        # Get parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 25, type=int), 100)  # Smaller pages for faster loading
        search = request.args.get('search', '').strip()
        status_filter = request.args.get('status', '').strip()
        
        logger.info(f"👥 Loading members list (page {page}, {per_page}/page, search='{search}', status='{status_filter}')")
        start_time = time.time()
        
        db_manager = current_app.db_manager
        
        # Use optimized paginated query
        members_data = db_manager.get_members_paginated(
            page=page, 
            per_page=per_page,
            search=search,
            status_filter=status_filter
        )
        
        load_time = time.time() - start_time
        
        response = {
            'members': members_data['members'],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total_pages': members_data['total_pages'],
                'total_members': members_data['total_members'],
                'has_prev': page > 1,
                'has_next': page < members_data['total_pages']
            },
            'filters': {
                'search': search,
                'status': status_filter
            },
            'loading': False,
            'loaded_at': datetime.now().isoformat(),
            'load_time': round(load_time * 1000, 2)
        }
        
        logger.info(f"✅ Members list loaded in {load_time:.3f}s ({len(members_data['members'])} members)")
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"❌ Error loading members list: {e}")
        return jsonify({
            'error': str(e),
            'loading': False,
            'members': [],
            'pagination': {'page': 1, 'total_pages': 0, 'total_members': 0}
        }), 500

@progressive_bp.route('/api/progressive/training-clients-list')
@cache_medium
def get_training_clients_list():
    """Get training clients list with progressive loading"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 25, type=int), 100)
        
        logger.info(f"🏋️ Loading training clients list (page {page})")
        start_time = time.time()
        
        db_manager = current_app.db_manager
        training_clients_data = db_manager.get_training_clients_paginated(page=page, per_page=per_page)
        
        load_time = time.time() - start_time
        
        response = {
            'training_clients': training_clients_data['training_clients'],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total_pages': training_clients_data['total_pages'],
                'total_training_clients': training_clients_data['total_training_clients']
            },
            'loading': False,
            'loaded_at': datetime.now().isoformat(),
            'load_time': round(load_time * 1000, 2)
        }
        
        logger.info(f"✅ Training clients loaded in {load_time:.3f}s")
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"❌ Error loading training clients: {e}")
        return jsonify({
            'error': str(e),
            'loading': False,
            'training_clients': [],
            'pagination': {'page': 1, 'total_pages': 0}
        }), 500

@progressive_bp.route('/api/progressive/prospects-list')
def get_prospects_list():
    """Get prospects list with progressive loading"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 25, type=int), 100)
        
        logger.info(f"🎯 Loading prospects list (page {page})")
        start_time = time.time()
        
        db_manager = current_app.db_manager
        prospects_data = db_manager.get_prospects_paginated(page=page, per_page=per_page)
        
        load_time = time.time() - start_time
        
        response = {
            'prospects': prospects_data['prospects'],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total_pages': prospects_data['total_pages'],
                'total_prospects': prospects_data['total_prospects']
            },
            'loading': False,
            'loaded_at': datetime.now().isoformat(),
            'load_time': round(load_time * 1000, 2)
        }
        
        logger.info(f"✅ Prospects loaded in {load_time:.3f}s")
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"❌ Error loading prospects: {e}")
        return jsonify({
            'error': str(e),
            'loading': False,
            'prospects': [],
            'pagination': {'page': 1, 'total_pages': 0}
        }), 500

@progressive_bp.route('/api/progressive/cache-status')
def get_cache_status():
    """Get current cache performance statistics"""
    try:
        from ..services.performance_cache import get_cache_statistics
        
        stats = get_cache_statistics()
        
        return jsonify({
            'cache_stats': stats,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Error getting cache status: {e}")
        return jsonify({'error': str(e)}), 500

@progressive_bp.route('/api/progressive/calendar/events')
def get_calendar_events():
    """Get calendar events progressively"""
    try:
        start_time = time.time()
        
        # Get today's events
        today_events = []
        try:
            if hasattr(current_app, 'clubos') and current_app.clubos:
                today_events = current_app.clubos.get_todays_events_lightweight()
        except Exception as e:
            logger.warning(f"⚠️ Could not get today's events: {e}")
            
        # Get calendar summary
        calendar_summary = {
            'total_events': 0,
            'training_sessions': 0,
            'classes': 0,
            'updated_at': None
        }
        
        try:
            if hasattr(current_app, 'clubos') and current_app.clubos:
                calendar_summary = current_app.clubos.get_calendar_summary()
        except Exception as e:
            logger.warning(f"⚠️ Could not get calendar summary: {e}")
        
        # Calculate performance
        load_time = round((time.time() - start_time) * 1000, 2)
        
        return jsonify({
            'today_events': today_events,
            'calendar_summary': calendar_summary,
            'loading': False,
            'performance': {
                'load_time_ms': load_time,
                'cached': False,
                'event_count': len(today_events)
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Error loading calendar events: {e}")
        return jsonify({
            'error': str(e),
            'loading': False,
            'today_events': [],
            'calendar_summary': {
                'total_events': 0,
                'training_sessions': 0,
                'classes': 0,
                'updated_at': None
            }
        }), 500

@progressive_bp.route('/api/progressive/clear-cache', methods=['POST'])
def clear_cache():
    """Clear performance cache"""
    try:
        performance_cache.clear()
        
        return jsonify({
            'success': True,
            'message': 'Cache cleared successfully',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Error clearing cache: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500