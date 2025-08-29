#!/usr/bin/env python3
"""
Dashboard Routes
Main dashboard page and related functionality
"""

from flask import Blueprint, render_template, current_app
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@dashboard_bp.route('/<int:day_offset>')
def dashboard(day_offset=0):
    """Dashboard route with optional day offset for navigation"""
    try:
        # Calculate target date based on day offset
        target_date = datetime.now().date() + timedelta(days=day_offset)
        
        # Get events for today (lightweight doesn't support target_date)
        clubos = current_app.clubos # Assuming ClubOSIntegration is available in current_app
        day_events = clubos.get_todays_events_lightweight()
        
        # Format events for display
        recent_events = []
        for event in day_events:
            try:
                # Parse ISO format times to readable format
                start_time = 'N/A'
                end_time = 'N/A'
                
                if event.get('start'):
                    try:
                        start_dt = datetime.fromisoformat(event['start'].replace('Z', '+00:00'))
                        start_time = start_dt.strftime('%I:%M %p')
                    except:
                        start_time = 'TBD'
                
                if event.get('end'):
                    try:
                        end_dt = datetime.fromisoformat(event['end'].replace('Z', '+00:00'))
                        end_time = end_dt.strftime('%I:%M %p')
                    except:
                        end_time = ''
                
                recent_events.append({
                    'id': event.get('id'),
                    'title': event.get('title'),
                    'participants': ', '.join(event.get('participants', [])),
                    'start_time': start_time,
                    'end_time': end_time,
                    'trainer': event.get('trainer', ''),
                    'location': event.get('location', ''),
                })
            except Exception as e:
                logger.error(f"Error formatting event {event}: {e}")
                continue
        
        # Get bot stats and other data
        bot_stats = {
            'total_members': 0,
            'active_members': 0,
            'total_prospects': 0,
            'conversations_today': 0
        }
        
        stats = {
            'todays_events': len(recent_events),
            'total_members': 0,
            'active_prospects': 0
        }
        
        sample_conversations = [
            "Member: Hi, I have a question about my membership",
            "Bot: Hello! I'd be happy to help with your membership. What would you like to know?",
            "Member: Can you tell me when my next payment is due?",
            "Bot: I'd be happy to check your payment schedule. Let me look that up for you."
        ]
        
        # Prepare context for template
        dashboard_context = {
            'bot_stats': bot_stats,
            'stats': stats,
            'recent_events': recent_events,
            'sample_conversations': sample_conversations,
            'day_offset': day_offset,
            'target_date': target_date,
            'day_name': target_date.strftime('%A'),
            'date_formatted': target_date.strftime('%B %d, %Y')
        }
        
        return render_template('dashboard.html', **dashboard_context)
        
    except Exception as e:
        logger.error(f"Error in dashboard route: {e}")
        return render_template('dashboard.html', 
                            bot_stats={}, 
                            stats={}, 
                            recent_events=[], 
                            sample_conversations=[],
                            day_offset=day_offset,
                            target_date=datetime.now().date(),
                            day_name='Today',
                            date_formatted='Today')

def dashboard():
    """Main dashboard with overview."""
    logger.info("=== DASHBOARD ROUTE TRIGGERED ===")
    
    # Check if we need to refresh data (but don't block the dashboard load)
    if current_app.db_manager.needs_refresh():
        logger.info("⚠️ Database data is stale, consider refreshing")
    
    # Get real data from database
    total_members = current_app.db_manager.get_member_count()
    total_prospects = current_app.db_manager.get_prospect_count()
    total_training_clients = current_app.db_manager.get_training_client_count()
    
    # Check if we have cached data available
    if hasattr(current_app, 'data_cache'):
        cached_members = current_app.data_cache.get('members', [])
        cached_prospects = current_app.data_cache.get('prospects', [])
        cached_training_clients = current_app.data_cache.get('training_clients', [])
        
        if cached_members:
            total_members = len(cached_members)
            logger.info(f"📊 Using cached member count: {total_members}")
        if cached_prospects:
            total_prospects = len(cached_prospects)
            logger.info(f"📊 Using cached prospect count: {total_prospects}")
        if cached_training_clients:
            total_training_clients = len(cached_training_clients)
            logger.info(f"📊 Using cached training client count: {total_training_clients}")
    
    # Get recent data for display
    recent_members = current_app.db_manager.get_recent_members(5)
    recent_prospects = current_app.db_manager.get_recent_prospects(5)
    
    logger.info(f"📊 Dashboard data: {total_members} members, {total_prospects} prospects, {total_training_clients} training clients")
    
    # Get live data from ClubOS - ONLY TODAY'S EVENTS (LIGHTWEIGHT)
    logger.info("=== STARTING CLUBOS INTEGRATION (LIGHTWEIGHT) ===")
    today_events = []
    clubos_status = "Disconnected"
    
    try:
        logger.info("=== GETTING TODAY'S EVENTS WITHOUT FUNDING CHECKS ===")
        
        # Get today's events lightweight (no authentication needed for iCal)
        today_events = current_app.clubos.get_todays_events_lightweight()
        logger.info(f"=== GOT {len(today_events)} TODAY'S EVENTS (LIGHTWEIGHT) ===")
                        
        clubos_status = "Connected" if today_events else "No events today"
    except Exception as e:
        logger.error(f"=== CLUBOS ERROR: {e} ===")
        clubos_status = f"Error: {str(e)[:50]}..."
    
    # Get current sync time
    sync_time = datetime.now()
    
    # Categorize events for new metrics
    training_sessions_count = 0
    appointments_count = 0
    
    appointment_keywords = ['consult', 'meeting', 'appointment', 'tour', 'assessment', 'savannah']
    
    for event in today_events:
        title = event.get('title', '').lower()
        participants = event.get('participants', [])
        participant_name = participants[0].lower() if participants and participants[0] else ''
        
        # Check if it's an appointment based on multiple criteria
        is_appointment = (
            any(keyword in title for keyword in appointment_keywords) or
            'savannah' in participant_name or
            'savannah' in title or
            not participants or participants[0] == ''
        )
        
        if is_appointment:
            appointments_count += 1
        else:
            training_sessions_count += 1
    
    # Mock bot activity data (placeholder until real bot integration)
    bot_activities = [
        {
            'id': 1,
            'action': 'Sent Welcome Message',
            'recipient': 'Sarah Johnson',
            'preview': 'Welcome to Anytime Fitness! Ready to start your journey?',
            'time': '2 minutes ago',
            'icon': 'paper-plane',
            'color': 'success',
            'status': 'Delivered',
            'status_color': 'success'
        },
        {
            'id': 2,
            'action': 'Payment Reminder',
            'recipient': 'Mike Chen',
            'preview': 'Your monthly payment is due in 3 days. Please update your payment method.',
            'time': '15 minutes ago',
            'icon': 'credit-card',
            'color': 'warning',
            'status': 'Sent',
            'status_color': 'warning'
        },
        {
            'id': 3,
            'action': 'Training Session Reminder',
            'recipient': 'Emily Rodriguez',
            'preview': 'Your training session with Coach Alex is tomorrow at 10:00 AM.',
            'time': '1 hour ago',
            'icon': 'dumbbell',
            'color': 'info',
            'status': 'Delivered',
            'status_color': 'info'
        }
    ]
    
    # Prepare dashboard context
    dashboard_context = {
        'total_members': total_members,
        'total_prospects': total_prospects,
        'total_training_clients': total_training_clients,
        'recent_members': recent_members,
        'recent_prospects': recent_prospects,
        'today_events': today_events,
        'clubos_status': clubos_status,
        'sync_time': sync_time,
        'training_sessions_count': training_sessions_count,
        'appointments_count': appointments_count,
        'bot_activities': bot_activities,
        'data_refresh_status': current_app.data_refresh_status,
        'bulk_checkin_status': current_app.bulk_checkin_status
    }
    
    return render_template('dashboard.html', **dashboard_context)
