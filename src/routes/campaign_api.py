"""
Real-time Campaign Tracking API Endpoints
Provides REST and WebSocket endpoints for campaign monitoring and control
"""
import logging
import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from src.services.campaign_tracker import (
    get_campaign_tracker, CampaignMetadata, CampaignStatus, CampaignPriority
)

logger = logging.getLogger(__name__)

# Create blueprint
campaign_api = Blueprint('campaign_api', __name__, url_prefix='/api/campaigns')

@campaign_api.route('/create', methods=['POST'])
def create_campaign():
    """Create a new campaign with tracking"""
    try:
        data = request.json
        campaign_id = str(uuid.uuid4())
        
        # Validate required fields
        required_fields = ['name', 'message', 'categories']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400
        
        # Create campaign metadata
        metadata = CampaignMetadata(
            campaign_id=campaign_id,
            name=data['name'],
            message_text=data['message'],
            message_type=data.get('type', 'sms'),
            subject=data.get('subject'),
            categories=data['categories'] if isinstance(data['categories'], list) else [data['categories']],
            status=CampaignStatus.DRAFT,
            priority=CampaignPriority(data.get('priority', 'normal')),
            created_at=datetime.now(),
            created_by=data.get('created_by', 'system'),
            max_recipients=data.get('max_recipients', 999999),
            batch_size=data.get('batch_size', 50),
            delay_between_batches=data.get('delay_between_batches', 30),
            retry_attempts=data.get('retry_attempts', 3),
            notes=data.get('notes', '')
        )
        
        # Create campaign in tracker
        tracker = get_campaign_tracker(current_app.db_manager)
        campaign_id = tracker.create_campaign(metadata)
        
        return jsonify({
            'success': True,
            'campaign_id': campaign_id,
            'message': f'Campaign "{metadata.name}" created successfully'
        })
        
    except Exception as e:
        logger.error(f"❌ Error creating campaign: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@campaign_api.route('/<campaign_id>/start', methods=['POST'])
def start_campaign(campaign_id):
    """Start a campaign"""
    try:
        data = request.json or {}
        total_recipients = data.get('total_recipients', 0)
        
        if total_recipients <= 0:
            return jsonify({'success': False, 'error': 'Invalid total_recipients'}), 400
        
        tracker = get_campaign_tracker(current_app.db_manager)
        success = tracker.start_campaign(campaign_id, total_recipients)
        
        if success:
            # Log campaign start for tracking
            logger.info(f"📊 Campaign {campaign_id} started successfully with {total_recipients} recipients")
            
            return jsonify({
                'success': True,
                'message': f'Campaign {campaign_id} started with {total_recipients} recipients'
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to start campaign'}), 500
            
    except Exception as e:
        logger.error(f"❌ Error starting campaign {campaign_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@campaign_api.route('/<campaign_id>/pause', methods=['POST'])
def pause_campaign(campaign_id):
    """Pause a running campaign"""
    try:
        tracker = get_campaign_tracker(current_app.db_manager)
        success = tracker.pause_campaign(campaign_id)
        
        if success:
            # Log campaign pause for tracking
            logger.info(f"⏸️ Campaign {campaign_id} paused successfully")
            
            return jsonify({'success': True, 'message': f'Campaign {campaign_id} paused'})
        else:
            return jsonify({'success': False, 'error': 'Failed to pause campaign'}), 500
            
    except Exception as e:
        logger.error(f"❌ Error pausing campaign {campaign_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@campaign_api.route('/<campaign_id>/resume', methods=['POST'])
def resume_campaign(campaign_id):
    """Resume a paused campaign"""
    try:
        tracker = get_campaign_tracker(current_app.db_manager)
        success = tracker.resume_campaign(campaign_id)
        
        if success:
            # Log campaign resume for tracking
            logger.info(f"▶️ Campaign {campaign_id} resumed successfully")
            
            return jsonify({'success': True, 'message': f'Campaign {campaign_id} resumed'})
        else:
            return jsonify({'success': False, 'error': 'Failed to resume campaign'}), 500
            
    except Exception as e:
        logger.error(f"❌ Error resuming campaign {campaign_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@campaign_api.route('/<campaign_id>/cancel', methods=['POST'])
def cancel_campaign(campaign_id):
    """Cancel a campaign"""
    try:
        tracker = get_campaign_tracker(current_app.db_manager)
        success = tracker.cancel_campaign(campaign_id)
        
        if success:
            # Log campaign cancellation for tracking
            logger.info(f"🛑 Campaign {campaign_id} cancelled successfully")
            
            return jsonify({'success': True, 'message': f'Campaign {campaign_id} cancelled'})
        else:
            return jsonify({'success': False, 'error': 'Failed to cancel campaign'}), 500
            
    except Exception as e:
        logger.error(f"❌ Error cancelling campaign {campaign_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@campaign_api.route('/<campaign_id>/status', methods=['GET'])
def get_campaign_status(campaign_id):
    """Get detailed campaign status"""
    try:
        tracker = get_campaign_tracker(current_app.db_manager)
        status = tracker.get_campaign_status(campaign_id)
        
        if 'error' in status:
            return jsonify({'success': False, 'error': status['error']}), 404
        
        return jsonify({'success': True, 'campaign': status})
        
    except Exception as e:
        logger.error(f"❌ Error getting campaign status {campaign_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@campaign_api.route('/<campaign_id>/progress', methods=['GET'])
def get_campaign_progress(campaign_id):
    """Get real-time campaign progress"""
    try:
        tracker = get_campaign_tracker(current_app.db_manager)
        status = tracker.get_campaign_status(campaign_id)
        
        if 'error' in status:
            return jsonify({'success': False, 'error': status['error']}), 404
        
        # Extract progress-specific data
        progress = {
            'campaign_id': campaign_id,
            'total_recipients': status.get('total_recipients', 0),
            'processed': status.get('processed', 0),
            'successful': status.get('successful', 0),
            'failed': status.get('failed', 0),
            'skipped': status.get('skipped', 0),
            'percentage_complete': status.get('percentage_complete', 0),
            'success_rate': status.get('success_rate', 0),
            'current_member': status.get('current_member'),
            'last_update': status.get('last_update'),
            'estimated_completion': status.get('estimated_completion'),
            'status': status.get('status')
        }
        
        return jsonify({'success': True, 'progress': progress})
        
    except Exception as e:
        logger.error(f"❌ Error getting campaign progress {campaign_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@campaign_api.route('/active', methods=['GET'])
def get_active_campaigns():
    """Get all active campaigns"""
    try:
        tracker = get_campaign_tracker(current_app.db_manager)
        campaigns = tracker.get_all_active_campaigns()
        
        return jsonify({'success': True, 'campaigns': campaigns})
        
    except Exception as e:
        logger.error(f"❌ Error getting active campaigns: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@campaign_api.route('/<campaign_id>/update-progress', methods=['POST'])
def update_campaign_progress(campaign_id):
    """Update campaign progress (internal endpoint for campaign execution)"""
    try:
        data = request.json
        
        tracker = get_campaign_tracker(current_app.db_manager)
        success = tracker.update_progress(
            campaign_id=campaign_id,
            processed=data.get('processed', 0),
            successful=data.get('successful', 0),
            failed=data.get('failed', 0),
            skipped=data.get('skipped', 0),
            current_member=data.get('current_member'),
            error_message=data.get('error_message')
        )
        
        if success:
            # Log progress update for tracking
            logger.debug(f"📊 Campaign {campaign_id} progress updated")
            
            return jsonify({'success': True, 'message': 'Progress updated'})
        else:
            return jsonify({'success': False, 'error': 'Failed to update progress'}), 500
            
    except Exception as e:
        logger.error(f"❌ Error updating campaign progress {campaign_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@campaign_api.route('/<campaign_id>/logs', methods=['GET'])
def get_campaign_logs(campaign_id):
    """Get campaign message logs"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        offset = (page - 1) * per_page
        
        logs = current_app.db_manager.execute_query('''
            SELECT member_name, member_contact, status, error_message, sent_at, retry_count
            FROM campaign_message_logs 
            WHERE campaign_id = ?
            ORDER BY sent_at DESC
            LIMIT ? OFFSET ?
        ''', (campaign_id, per_page, offset))
        
        # Get total count
        count_result = current_app.db_manager.execute_query('''
            SELECT COUNT(*) as total FROM campaign_message_logs WHERE campaign_id = ?
        ''', (campaign_id,))
        
        total = count_result[0]['total'] if count_result else 0
        
        return jsonify({
            'success': True,
            'logs': logs,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page
            }
        })
        
    except Exception as e:
        logger.error(f"❌ Error getting campaign logs {campaign_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@campaign_api.route('/<campaign_id>/events', methods=['GET'])
def get_campaign_events(campaign_id):
    """Get campaign event history"""
    try:
        events = current_app.db_manager.execute_query('''
            SELECT event_type, event_message, event_data, timestamp
            FROM campaign_events 
            WHERE campaign_id = ?
            ORDER BY timestamp DESC
            LIMIT 50
        ''', (campaign_id,))
        
        return jsonify({'success': True, 'events': events})
        
    except Exception as e:
        logger.error(f"❌ Error getting campaign events {campaign_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Real-time tracking via REST API polling (WebSocket can be added later if needed)

# Function to register blueprint
def register_campaign_api(app):
    """Register the campaign API blueprint"""
    app.register_blueprint(campaign_api)
    logger.info("📊 Campaign tracking API registered")