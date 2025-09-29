#!/usr/bin/env python3
"""
Dashboard Routes - Fixed Version
Main dashboard page with working events display
"""

from flask import Blueprint, render_template, current_app, session, redirect, url_for, flash
from datetime import datetime, timedelta
import logging
import hashlib

logger = logging.getLogger(__name__)

dashboard_bp = Blueprint('dashboard', __name__)

# Import the authentication decorator
from .auth import require_auth

@dashboard_bp.route('/')
@dashboard_bp.route('/<int:day_offset>')
@require_auth
def dashboard(day_offset=0):
    """Dashboard route with working events display"""
    try:
        # DEBUGGING: Log that we made it past the auth decorator
        logger.info(f"🎉 DASHBOARD ROUTE REACHED - Auth decorator passed!")
        logger.info(f"🔍 Dashboard session check - authenticated: {session.get('authenticated')}")
        logger.info(f"🔍 Dashboard session check - manager_id: {session.get('manager_id')}")
        logger.info(f"🔍 Dashboard session check - selected_clubs: {session.get('selected_clubs')}")

        # Ensure session persistence
        session.permanent = True
        session.modified = True

        logger.info(f"🔍 Dashboard accessed - Session state: authenticated={session.get('authenticated')}")

        # Calculate target date
        target_date = datetime.now().date() + timedelta(days=day_offset)
        
        # Load events for display
        day_events = []

        try:
            # Get events using ClubOS integration
            from src.services.clubos_integration import ClubOSIntegration
            clubos_integration = ClubOSIntegration()

            # Get today's events only
            day_events = clubos_integration.get_todays_events_lightweight()

            logger.info(f"📅 Loaded {len(day_events)} events for today")
            
        except Exception as e:
            logger.error(f"❌ Error loading events: {e}")
            day_events = []

        # Process events for display
        processed_day_events = []
        for event in day_events:
            try:
                # Parse times
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

                # Process participants
                participants = event.get('participants', [])
                if isinstance(participants, str):
                    participants = [p.strip() for p in participants.split(',') if p.strip()]

                processed_day_events.append({
                    'id': event.get('id'),
                    'title': event.get('title', ''),
                    'participants': [{'name': p} for p in participants],
                    'start_time': start_time,
                    'end_time': end_time,
                    'trainer': event.get('trainer', ''),
                    'location': event.get('location', ''),
                })
            except Exception as e:
                logger.error(f"Error processing event: {e}")
                continue

        # Update day_events with processed data
        day_events = processed_day_events
        
        # Get basic counts from database (optimized with caching)
        db_manager = current_app.db_manager
        manager_id = session.get('manager_id', 'default')
        cache_key = f"dashboard_counts_{manager_id}"

        # Try to get cached counts first (cache for 5 minutes)
        cached_counts = current_app.data_cache.get(cache_key)
        cache_age = current_app.data_cache.get(f"{cache_key}_timestamp", 0)
        current_time = datetime.now().timestamp()

        if cached_counts and (current_time - cache_age) < 300:  # 5 minutes
            total_members = cached_counts.get('member_count', 0)
            total_prospects = cached_counts.get('prospect_count', 0)
            total_training_clients = cached_counts.get('training_client_count', 0)
            logger.debug("📊 Using cached dashboard counts")
        else:
            try:
                # Use a single query to get all counts at once
                counts_query = """
                    SELECT
                        (SELECT COUNT(*) FROM members) as member_count,
                        (SELECT COUNT(*) FROM prospects) as prospect_count,
                        (SELECT COUNT(*) FROM training_clients) as training_client_count
                """
                counts = db_manager.execute_query(counts_query, fetch_one=True)

                if counts:
                    total_members = counts['member_count'] if counts['member_count'] else 0
                    total_prospects = counts['prospect_count'] if counts['prospect_count'] else 0
                    total_training_clients = counts['training_client_count'] if counts['training_client_count'] else 0

                    # Cache the results
                    count_data = {
                        'member_count': total_members,
                        'prospect_count': total_prospects,
                        'training_client_count': total_training_clients
                    }
                    current_app.data_cache[cache_key] = count_data
                    current_app.data_cache[f"{cache_key}_timestamp"] = current_time
                    logger.debug("📊 Cached fresh dashboard counts")
                else:
                    total_members = total_prospects = total_training_clients = 0
            except Exception as e:
                logger.error(f"Error getting counts: {e}")
                total_members = 0
                total_prospects = 0
                total_training_clients = 0
        
        # Calculate next session time
        next_session_time = None
        if day_events:
            try:
                # Find next session from today's events
                today_events = [e for e in day_events if e.get('start_time') != 'N/A']
                if today_events:
                    # Sort by start time and get the next one
                    sorted_events = sorted(today_events, key=lambda x: x.get('start_time', ''))
                    next_session_time = sorted_events[0].get('start_time')
            except Exception as e:
                logger.error(f"Error calculating next session: {e}")
        
        # Create bot stats
        bot_stats = {
            'messages_sent': 0,
            'unread_conversations': 0,
            'response_rate': 0,
            'last_activity': 'No recent activity'
        }
        
        try:
            # Get bot activity stats from database (optimized single query)
            today = datetime.now().date()
            manager_id = session.get('manager_id', 'default')

            # Single query to get all bot stats at once
            bot_stats_query = """
                SELECT
                    (SELECT COUNT(*) FROM messages
                     WHERE DATE(created_at) = ? AND owner_id = ?) as messages_today,
                    (SELECT COUNT(DISTINCT conversation_id) FROM messages
                     WHERE delivery_status = 'received' AND owner_id = ?) as unread_conversations,
                    (SELECT COUNT(*) FROM messages WHERE owner_id = ?) as total_messages,
                    (SELECT created_at FROM messages
                     WHERE owner_id = ? ORDER BY created_at DESC LIMIT 1) as last_message_time
            """
            bot_data = db_manager.execute_query(
                bot_stats_query,
                (today, manager_id, manager_id, manager_id, manager_id),
                fetch_one=True
            )

            if bot_data:
                bot_stats['messages_sent'] = bot_data['messages_today'] if bot_data['messages_today'] else 0
                bot_stats['unread_conversations'] = bot_data['unread_conversations'] if bot_data['unread_conversations'] else 0

                # Calculate response rate
                total_msg_count = bot_data['total_messages'] if bot_data['total_messages'] else 0
                if total_msg_count > 0:
                    response_rate = min(95, max(0, 100 - (bot_stats['unread_conversations'] * 10)))
                    bot_stats['response_rate'] = response_rate

                # Process last activity time
                last_message_time = bot_data['last_message_time'] if 'last_message_time' in bot_data else None
                if last_message_time:
                    try:
                        last_activity_dt = datetime.fromisoformat(last_message_time.replace('Z', '+00:00'))
                        time_diff = datetime.now() - last_activity_dt.replace(tzinfo=None)
                        if time_diff.days > 0:
                            bot_stats['last_activity'] = f"{time_diff.days} days ago"
                        elif time_diff.seconds > 3600:
                            hours = time_diff.seconds // 3600
                            bot_stats['last_activity'] = f"{hours} hours ago"
                        else:
                            minutes = time_diff.seconds // 60
                            bot_stats['last_activity'] = f"{minutes} minutes ago"
                    except:
                        bot_stats['last_activity'] = 'Recently active'
            
        except Exception as e:
            logger.error(f"Error getting bot stats: {e}")
            # Keep default values
        
        # Create date formatting
        day_name = target_date.strftime('%A')
        date_formatted = target_date.strftime('%B %d, %Y')
        
        # Create bot conversations (empty for now)
        bot_conversations = []
        
        # Create stats
        stats = {
            'total_members': total_members,
            'total_prospects': total_prospects,
            'total_training_clients': total_training_clients,
            'todays_events': len(day_events),
            'next_session_time': next_session_time,
        }
        
        # Create dashboard context
        context = {
            'target_date': target_date,
            'day_offset': day_offset,
            'day_events': day_events,
            'stats': stats,
            'bot_stats': bot_stats,
            'day_name': day_name,
            'date_formatted': date_formatted,
            'bot_conversations': bot_conversations,
            'club_summary': {
                'selected_clubs': session.get('selected_clubs', []),
                'club_names': [],
                'is_multi_club': False,
                'user_info': session.get('user_info', {})
            }
        }

        logger.info(f"✅ Dashboard loaded successfully with {len(day_events)} events")
        return render_template('dashboard.html', **context)
        
    except Exception as e:
        logger.error(f"❌ Error in dashboard route: {e}")
        return render_template('error.html', error=str(e))
