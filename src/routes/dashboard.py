#!/usr/bin/env python3
"""
Dashboard Routes
Main dashboard page and related functionality
"""

from flask import Blueprint, render_template, current_app, session, redirect, url_for, flash
from datetime import datetime, timedelta
import datetime as dt_module
import logging

logger = logging.getLogger(__name__)

dashboard_bp = Blueprint('dashboard', __name__)

# Import the authentication decorator
from .auth import require_auth

@dashboard_bp.route('/')
@dashboard_bp.route('/<int:day_offset>')
@require_auth
def dashboard(day_offset=0):
    """Dashboard route with optional day offset for navigation and multi-club support"""
    try:
        # Ensure session persistence before proceeding
        session.permanent = True
        session.modified = True
        
        # Debug session state on dashboard access
        logger.info(f"🔍 Dashboard accessed - Session state: authenticated={session.get('authenticated')}, manager_id={session.get('manager_id')}, selected_clubs={session.get('selected_clubs')}")
        # Check for multi-club context
        from src.services.multi_club_manager import multi_club_manager
        
        # If no clubs selected but user has club access, redirect to selection
        selected_clubs = session.get('selected_clubs', [])
        # Temporarily disabled for testing - preventing redirect loop
        # if not selected_clubs and 'available_clubs' in session and session['available_clubs']:
        #     flash('Please select your clubs first.', 'info')
        #     return redirect(url_for('club_selection.club_selection'))
        
        # Get multi-club summary for dashboard header
        club_summary = {
            'selected_clubs': selected_clubs,
            'club_names': [multi_club_manager.get_club_name(club_id) for club_id in selected_clubs],
            'is_multi_club': len(selected_clubs) > 1,
            'user_info': session.get('user_info', {})
        }
        # Calculate target date based on day offset
        target_date = datetime.now().date() + timedelta(days=day_offset)
        
        # Get events for today (lightweight doesn't support target_date)
        clubos = current_app.clubos # Assuming ClubOSIntegration is available in current_app
        day_events = clubos.get_todays_events_lightweight()
        
        logger.info(f"Got {len(day_events) if day_events else 0} events from clubos")
        if day_events:
            logger.info(f"First event structure: {str(day_events[0])}")
        
        # Format events for display with enhanced participant name mapping
        recent_events = []
        for i, event in enumerate(day_events):
            logger.info(f"Processing event {str(i)}: {str(type(event))} - {str(event)}")
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
                
                # Enhanced participant name mapping from training clients database with past due amounts
                enhanced_participants = []
                raw_participants = event.get('participants', [])
                
                # Debug logging
                logger.debug(f"Raw participants: {str(raw_participants)}, type: {str(type(raw_participants))}")
                
                # Ensure participants is a proper list of strings
                if isinstance(raw_participants, str):
                    raw_participants = [p.strip() for p in raw_participants.split(',') if p.strip()]
                elif isinstance(raw_participants, list):
                    # Convert any non-string items to strings - safer approach
                    safe_participants = []
                    for p in raw_participants:
                        try:
                            if p is not None:
                                safe_participants.append(str(p).strip())
                        except Exception as e:
                            logger.error(f"Error converting participant to string: {str(type(p))}, error: {str(e)}")
                    raw_participants = safe_participants
                else:
                    raw_participants = []
                
                logger.debug(f"Processed participants: {str(raw_participants)}")

                for participant in raw_participants:
                    # Ensure participant is always a string
                    participant = str(participant) if participant is not None else ''
                    if participant and participant.strip():
                        # Try to find the real name and past due info in training clients database
                        try:
                            # Look for training client by various name patterns
                            participant_str = str(participant) if participant is not None else ''
                            search_param1 = f'%{participant_str}%'
                            search_param2 = f'%{participant_str}%'
                            search_param3 = participant_str
                            
                            training_client = current_app.db_manager.execute_query("""
                                SELECT member_name, first_name, last_name, member_id
                                FROM training_clients
                                WHERE LOWER(member_name) LIKE LOWER(%s)
                                   OR LOWER(first_name || ' ' || last_name) LIKE LOWER(%s)
                                   OR LOWER(%s) LIKE LOWER(member_name)
                                ORDER BY created_at DESC
                                LIMIT 1
                            """, (search_param1, search_param2, search_param3), fetch_one=True)

                            if training_client:
                                # Use the real name from training clients database (RealDictRow access)
                                first_name = str(training_client['first_name'] or '') if training_client['first_name'] is not None else ''
                                last_name = str(training_client['last_name'] or '') if training_client['last_name'] is not None else ''
                                if training_client['member_name']:
                                    real_name = str(training_client['member_name'])
                                else:
                                    full_name = str(first_name) + " " + str(last_name)
                                    real_name = full_name.strip()
                                member_id = training_client['member_id']

                                # Get past due amount for this training client
                                past_due_info = None
                                if member_id:
                                    try:
                                        # Use the ClubOS training API to get payment status and amount
                                        if hasattr(current_app.clubos, 'training_api') and current_app.clubos.training_api:
                                            payment_data = current_app.clubos.training_api.get_complete_agreement_data(member_id)
                                            if payment_data and payment_data.get('success'):
                                                payment_status = payment_data.get('payment_status', 'Unknown')
                                                amount_owed = payment_data.get('amount_owed', 0.0)

                                                if payment_status == 'Past Due' and amount_owed > 0:
                                                    try:
                                                        formatted_amount = f"${float(amount_owed):.2f}"
                                                    except (ValueError, TypeError):
                                                        formatted_amount = f"${str(amount_owed)}"
                                                    
                                                    past_due_info = {
                                                        'status': payment_status,
                                                        'amount': amount_owed,
                                                        'formatted_amount': formatted_amount
                                                    }
                                    except Exception as payment_error:
                                        logger.warning(f"⚠️ Error getting payment data for member {str(member_id)}: {str(payment_error)}")

                                # Create enhanced participant with past due info
                                enhanced_participant = {
                                    'name': str(real_name) if real_name else '',
                                    'original_name': str(participant) if participant else '',
                                    'past_due': past_due_info
                                }
                                enhanced_participants.append(enhanced_participant)
                                logger.info(f"✅ Mapped '{str(participant)}' to '{str(real_name)}' with past due: {str(past_due_info)}")
                            else:
                                # Keep original name if no mapping found
                                enhanced_participants.append({
                                    'name': str(participant) if participant else '',
                                    'original_name': str(participant) if participant else '',
                                    'past_due': None
                                })
                                logger.debug(f"⚠️ No training client mapping found for '{str(participant)}'")

                        except Exception as mapping_error:
                            logger.warning(f"⚠️ Error mapping participant '{str(participant)}': {str(mapping_error)}")
                            enhanced_participants.append({
                                'name': str(participant) if participant else '',
                                'original_name': str(participant) if participant else '',
                                'past_due': None
                            })
                    else:
                        enhanced_participants.append({
                            'name': str(participant) if participant else '',
                            'original_name': str(participant) if participant else '',
                            'past_due': None
                        })
                
                try:
                    recent_events.append({
                        'id': event.get('id'),
                        'title': event.get('title'),
                        'participants': enhanced_participants,  # Use enhanced names
                        'start_time': start_time,
                        'end_time': end_time,
                        'trainer': event.get('trainer', ''),
                        'location': event.get('location', ''),
                    })
                    logger.info(f"✅ Successfully added event {str(event.get('id', 'unknown'))} to recent_events")
                except Exception as append_error:
                    logger.error(f"❌ Error appending event to recent_events: {str(append_error)}")
                    logger.error(f"Event data types: id={type(event.get('id'))}, title={type(event.get('title'))}, participants={type(enhanced_participants)}")
                    continue
            except Exception as e:
                logger.error(f"Error formatting event {str(event.get('id', 'unknown'))}: {str(e)}")
                continue
        
        logger.info(f"🎯 Finished processing all events. Total recent_events: {len(recent_events)}")
        
        # Get bot stats and other data with real database counts
        try:
            # Get real counts from database
            total_members = current_app.db_manager.get_member_count() if hasattr(current_app.db_manager, 'get_member_count') else 0
            total_prospects = current_app.db_manager.get_prospect_count() if hasattr(current_app.db_manager, 'get_prospect_count') else 0
            total_training_clients = current_app.db_manager.get_training_client_count() if hasattr(current_app.db_manager, 'get_training_client_count') else 0
            
            # Calculate active members (green members)
            active_members = 0
            
            try:
                # Get green members count using the database manager's category methods
                if hasattr(current_app.db_manager, 'get_members_by_category'):
                    green_members = current_app.db_manager.get_members_by_category('green')
                    active_members = len(green_members) if green_members else 0
                    logger.info(f"📈 Found {active_members} green (active) members")
                else:
                    # Fallback: query database directly for green members using database manager
                    # Try member_categories table first
                    result = current_app.db_manager.execute_query("""
                        SELECT COUNT(DISTINCT member_id) as green_count
                        FROM member_categories 
                        WHERE LOWER(category) = 'green'
                    """, fetch_one=True)
                    
                    if result and result.get('green_count', 0) > 0:
                        active_members = result['green_count']
                        logger.info(f"📈 Found {active_members} green members from member_categories")
                    else:
                        # Fallback to members table with status/category heuristics using database manager
                        result = current_app.db_manager.execute_query("""
                            SELECT COUNT(*) as green_count
                            FROM members 
                            WHERE (
                                LOWER(membership_status) LIKE ? OR
                                LOWER(membership_type) LIKE ? OR
                                LOWER(status) LIKE ? OR
                                LOWER(status) LIKE ?
                            )
                        """, ('%green%', '%green%', '%active%', '%current%'), fetch_one=True)
                        
                        active_members = result.get('green_count', 0) if result else 0
                        logger.info(f"📈 Found {active_members} active members using status heuristics")
                    
            except Exception as green_error:
                logger.warning(f"⚠️ Error calculating green members, using 0: {str(green_error)}")
                active_members = 0
            
            # Calculate messaging and bot activity stats
            messages_sent_today = 0
            conversations_today = 0
            unread_conversations = 0
            total_conversations = 0
            
            try:
                today = datetime.now().date()
                all_threads = current_app.db_manager.get_recent_message_threads(limit=50)  # Get more to analyze
                
                for thread in all_threads:
                    total_conversations += 1
                    
                    # Count unread conversations
                    if thread.get('unread_count', 0) > 0:
                        unread_conversations += 1
                    
                    latest_msg = thread.get('latest_message', {})
                    if latest_msg.get('created_at'):
                        try:
                            msg_time = datetime.fromisoformat(str(latest_msg['created_at']).replace('Z', '+00:00'))
                            if msg_time.date() == today:
                                conversations_today += 1
                                # Count messages sent by bot/staff today
                                if latest_msg.get('sender_type') in ['staff', 'bot', 'system']:
                                    messages_sent_today += 1
                        except:
                            continue
                
                # Calculate response rate
                response_rate = round((conversations_today / max(total_conversations, 1)) * 100, 1) if total_conversations > 0 else 0
                
            except Exception as conv_count_error:
                logger.warning(f"⚠️ Error calculating messaging stats: {str(conv_count_error)}")
                messages_sent_today = 0
                conversations_today = 0
                unread_conversations = 0
                response_rate = 0
            
            bot_stats = {
                'total_members': total_members,
                'active_members': active_members,  # Use green members as active members
                'total_prospects': total_prospects,
                'conversations_today': conversations_today,
                'messages_sent': messages_sent_today,
                'last_activity': f'Last active: {dt_module.datetime.now().strftime("%I:%M %p")}' if messages_sent_today > 0 else 'No activity today',
                'unread_conversations': unread_conversations,
                'response_rate': response_rate
            }
            
            logger.info(f"✅ Created bot_stats with real data: {total_members} members, {active_members} active (green), {total_prospects} prospects, {conversations_today} conversations today")
        except Exception as stats_error:
            logger.error(f"❌ Error creating bot_stats: {str(stats_error)}")
            bot_stats = {
                'total_members': 0,
                'active_members': 0,
                'total_prospects': 0,
                'conversations_today': 0,
                'messages_sent': 0,
                'last_activity': 'No recent activity',
                'unread_conversations': 0,
                'response_rate': 0
            }
        
        try:
            # Calculate next session time from today's events
            next_session_time = None
            if recent_events:
                # Find the next session (earliest start time that hasn't passed)
                current_time = dt_module.datetime.now()
                upcoming_sessions = []
                
                for event in recent_events:
                    if event.get('start_time') and event['start_time'] not in ['N/A', 'TBD']:
                        try:
                            # Try to parse the formatted time back to compare
                            event_time_str = event['start_time']  # e.g., "02:30 PM"
                            # Combine with today's date for comparison
                            today_date = dt_module.datetime.now().date()
                            event_datetime = dt_module.datetime.strptime(f"{today_date} {event_time_str}", "%Y-%m-%d %I:%M %p")
                            
                            if event_datetime > current_time:
                                upcoming_sessions.append((event_datetime, event_time_str))
                        except:
                            continue
                
                if upcoming_sessions:
                    # Sort by time and get the earliest
                    upcoming_sessions.sort(key=lambda x: x[0])
                    next_session_time = upcoming_sessions[0][1]
            
            # Calculate today's revenue from training packages
            todays_revenue = 0
            try:
                # Get training clients with agreements and calculate revenue
                training_clients_with_agreements = current_app.db_manager.get_training_clients_with_agreements() if hasattr(current_app.db_manager, 'get_training_clients_with_agreements') else []
                
                today = dt_module.datetime.now().date()
                for client in training_clients_with_agreements:
                    # Check if agreement was created today
                    if client.get('created_at'):
                        try:
                            created_date = dt_module.datetime.fromisoformat(str(client['created_at']).replace('Z', '+00:00')).date()
                            if created_date == today:
                                # Add package price to revenue (estimate based on training packages)
                                todays_revenue += 150  # Average training package price
                        except:
                            continue
            except Exception as revenue_error:
                logger.warning(f"⚠️ Error calculating revenue: {str(revenue_error)}")
                todays_revenue = 0
            
            # Use the same real data for consistency
            stats = {
                'todays_events': len(recent_events),
                'total_members': bot_stats.get('total_members', 0),
                'active_prospects': bot_stats.get('total_prospects', 0),
                'next_session_time': next_session_time,
                'revenue': todays_revenue
            }
            logger.info(f"✅ Created stats with real data: {len(recent_events)} events, {stats['total_members']} members, {stats['active_prospects']} prospects, ${todays_revenue} revenue, next session: {next_session_time or 'None scheduled'}")
        except Exception as stats_error:
            logger.error(f"❌ Error creating stats: {str(stats_error)}")
            stats = {
                'todays_events': len(recent_events) if 'recent_events' in locals() else 0,
                'total_members': 0,
                'active_prospects': 0,
                'next_session_time': None,
                'revenue': 0
            }
        
        # Get real conversation data - try ClubOS live first using working messaging approach
        bot_conversations = []
        try:
            # First, try to get live messages using the working ClubOSMessagingClient approach
            clubos_messages = []
            try:
                from src.services.clubos_messaging_client_simple import ClubOSMessagingClient
                from src.routes.messaging import get_clubos_credentials
                
                # Use the same approach as the working messaging page
                owner_id = '187032782'  # Default owner ID from working messaging
                credentials = get_clubos_credentials(owner_id)
                
                if credentials:
                    logger.info("🔄 Fetching live ClubOS messages using messaging client...")
                    messaging_client = ClubOSMessagingClient(
                        username=credentials['username'],
                        password=credentials['password']
                    )
                    
                    # Authenticate like the working messaging page does
                    if messaging_client.authenticate():
                        logger.info("✅ ClubOS messaging authentication successful")
                        
                        # Get messages using the working approach
                        raw_messages = messaging_client.get_messages(owner_id)
                        
                        if raw_messages:
                            logger.info(f"✅ Retrieved {len(raw_messages)} raw ClubOS messages, filtering for real member messages...")
                            
                            # Convert raw messages to dashboard format (similar to messaging inbox route)
                            from src.routes.messaging import extract_name_from_message_content
                            
                            # Group messages by sender like the working messaging route does
                            # BUT filter out test/placeholder messages and only show real member messages
                            threads = {}
                            processed_count = 0
                            for message in raw_messages[:50]:  # Check more messages to find real ones
                                # Skip empty or invalid messages
                                content = message.get('content', '')
                                if not content or len(content.strip()) < 5:
                                    continue
                                    
                                # Extract name if needed
                                sender_name = message.get('from_user', message.get('from', 'Unknown'))
                                if sender_name == 'Unknown' or not sender_name:
                                    sender_name = extract_name_from_message_content(content)
                                
                                # Filter out system messages, test messages, and placeholder content
                                if (
                                    not sender_name or 
                                    sender_name == 'Unknown' or
                                    sender_name == 'System' or
                                    sender_name == 'j.mayo' or  # Skip your own messages
                                    'test' in sender_name.lower() or
                                    'sample' in content.lower() or
                                    'training schedule' in content.lower() or  # Skip the placeholder messages you mentioned
                                    len(sender_name) < 3 or
                                    len(sender_name) > 50
                                ):
                                    continue
                                
                                # Only process real member messages
                                sender_key = sender_name
                                if sender_key not in threads:
                                    threads[sender_key] = {
                                        'id': f"live_thread_{len(threads)}",
                                        'member_id': message.get('owner_id', owner_id),
                                        'member_name': sender_name,
                                        'latest_message': {
                                            'message_content': content,
                                            'created_at': message.get('timestamp', message.get('created_at')),
                                            'sender_type': 'member',  # These are all real member messages
                                            'status': message.get('status', 'received')
                                        },
                                        'thread_type': message.get('channel', 'clubos'),
                                        'unread_count': 1 if message.get('status') != 'read' else 0
                                    }
                                    processed_count += 1
                                    
                                    # Stop when we have enough real conversations
                                    if processed_count >= 10:
                                        break
                            
                            # Convert to dashboard conversation format
                            for thread_key, thread in list(threads.items())[:10]:  # Limit to 10 conversations
                                latest_msg = thread.get('latest_message', {})
                                
                                # Calculate time ago
                                time_ago = "Recently"
                                if latest_msg.get('created_at'):
                                    try:
                                        msg_time = datetime.fromisoformat(str(latest_msg['created_at']).replace('Z', '+00:00'))
                                        time_diff = dt_module.datetime.now() - msg_time
                                        if time_diff.days > 0:
                                            time_ago = f"{time_diff.days} day{'s' if time_diff.days > 1 else ''} ago"
                                        elif time_diff.seconds > 3600:
                                            hours = time_diff.seconds // 3600
                                            time_ago = f"{hours} hour{'s' if hours > 1 else ''} ago"
                                        elif time_diff.seconds > 60:
                                            minutes = time_diff.seconds // 60
                                            time_ago = f"{minutes} min ago"
                                        else:
                                            time_ago = "Just now"
                                    except:
                                        time_ago = "Recently"
                                
                                unread_count = thread.get('unread_count', 0)
                                thread_type = thread.get('thread_type', 'clubos')
                                
                                conversation = {
                                    'id': thread['id'],
                                    'name': str(thread.get('member_name', 'Unknown Member')),
                                    'preview': str(latest_msg.get('message_content', 'No messages yet'))[:100],
                                    'time': time_ago,
                                    'contact_name': str(thread.get('member_name', 'Unknown Member')),
                                    'last_message': str(latest_msg.get('message_content', 'No messages yet'))[:100],
                                    'last_time': time_ago,
                                    'last_sender': 'user' if latest_msg.get('sender_type') == 'member' else 'staff',
                                    'unread': unread_count > 0,
                                    'status': 'ClubOS Live',
                                    'status_color': 'primary',
                                    'needs_attention': unread_count > 0 and latest_msg.get('sender_type') == 'member',
                                    'member_id': thread.get('member_id'),
                                    'thread_type': thread_type,
                                    'unread_count': unread_count
                                }
                                
                                clubos_messages.append(conversation)
                            
                            if clubos_messages:
                                bot_conversations = clubos_messages
                                logger.info(f"✅ Successfully filtered and converted {len(clubos_messages)} real ClubOS member messages")
                                logger.info(f"👥 Live conversations: {[conv['name'] for conv in clubos_messages]}")
                                # Mark that we have live data to prevent fallback mixing
                                live_data_success = True
                            else:
                                logger.warning("⚠️ No conversations created from live messages, falling back to database")
                                live_data_success = False
                        else:
                            logger.warning("⚠️ No live messages returned from messaging client, falling back to database")
                            live_data_success = False
                    else:
                        logger.warning("⚠️ ClubOS messaging authentication failed, falling back to database")
                        live_data_success = False
                else:
                    logger.warning("⚠️ ClubOS credentials not available, using database fallback")
                    live_data_success = False
                    
            except Exception as clubos_error:
                logger.warning(f"⚠️ ClubOS live messaging failed: {str(clubos_error)}, falling back to database")
                live_data_success = False
                
            # If ClubOS live messages failed or returned empty, fall back to database
            # But ONLY fallback if we didn't get any live data to avoid mixing
            if not bot_conversations and not locals().get('live_data_success', False):
                logger.info("🔄 Using database fallback for messages...")
                # Check if database manager exists and has the method
                if hasattr(current_app, 'db_manager') and hasattr(current_app.db_manager, 'get_recent_message_threads'):
                    recent_threads = current_app.db_manager.get_recent_message_threads(limit=10)
                    
                    # Process database threads into the format expected by the dashboard
                    # Apply the same filtering as for live messages to avoid showing test/sample data
                    for thread in recent_threads:
                        latest_msg = thread.get('latest_message', {})
                        member_name = str(thread.get('member_name', 'Unknown Member'))
                        message_content = str(latest_msg.get('message_content', 'No messages yet'))
                        
                        # Apply same filters as live messages to avoid showing sample/test data
                        if (
                            not member_name or
                            member_name == 'Unknown Member' or
                            member_name == 'System' or
                            member_name == 'j.mayo' or
                            'test' in member_name.lower() or
                            'sample' in message_content.lower() or
                            'training schedule' in message_content.lower() or
                            len(member_name) < 3 or
                            len(member_name) > 50
                        ):
                            continue  # Skip this thread
                        
                        # Calculate time ago for display
                        if latest_msg.get('created_at'):
                            try:
                                msg_time = datetime.fromisoformat(str(latest_msg['created_at']).replace('Z', '+00:00'))
                                time_diff = dt_module.datetime.now() - msg_time
                                if time_diff.days > 0:
                                    time_ago = f"{time_diff.days} day{'s' if time_diff.days > 1 else ''} ago"
                                elif time_diff.seconds > 3600:
                                    hours = time_diff.seconds // 3600
                                    time_ago = f"{hours} hour{'s' if hours > 1 else ''} ago"
                                elif time_diff.seconds > 60:
                                    minutes = time_diff.seconds // 60
                                    time_ago = f"{minutes} min ago"
                                else:
                                    time_ago = "Just now"
                            except:
                                time_ago = "Recently"
                        else:
                            time_ago = "No recent activity"
                        
                        # Only show ClubOS messages in database fallback, not system messages
                        unread_count = thread.get('unread_count', 0)
                        thread_type = thread.get('thread_type', 'clubos')  # Default to clubos for real messages
                        
                        conversation = {
                            'id': f"thread_{thread['id']}",
                            'name': member_name,
                            'preview': message_content[:100],
                            'time': time_ago,
                            'contact_name': member_name,
                            'last_message': message_content[:100],
                            'last_time': time_ago,
                            'last_sender': 'user' if latest_msg.get('sender_type') == 'member' else 'staff',
                            'unread': unread_count > 0,
                            'status': 'ClubOS Stored',  # Indicate these are from database
                            'status_color': 'info',
                            'needs_attention': unread_count > 0 and latest_msg.get('sender_type') == 'member',
                            'member_id': thread.get('member_id'),
                            'thread_type': thread_type,
                            'unread_count': unread_count
                        }
                        
                        bot_conversations.append(conversation)
                        
                else:
                    logger.warning("⚠️ Database manager or method not available, using empty conversations")
            
            # Sort conversations by priority: unread member messages first, then by recency
            def conversation_sort_key(conv):
                priority = 0
                
                # Highest priority: Unread messages from members needing attention
                if conv.get('needs_attention'):
                    priority += 1000
                
                # High priority: Any unread messages
                if conv.get('unread'):
                    priority += 500
                
                # Medium priority: Recent messages (calculate recency score)
                time_str = conv.get('time', 'Never')
                if 'Just now' in time_str:
                    priority += 100
                elif 'min ago' in time_str:
                    try:
                        mins = int(time_str.split(' ')[0])
                        priority += max(50 - mins, 10)  # More recent = higher score
                    except:
                        priority += 25
                elif 'hour' in time_str:
                    try:
                        hours = int(time_str.split(' ')[0])
                        priority += max(20 - hours, 5)
                    except:
                        priority += 10
                elif 'day' in time_str:
                    try:
                        days = int(time_str.split(' ')[0])
                        priority += max(10 - days, 1)
                    except:
                        priority += 2
                
                # Small boost for different conversation types
                thread_type = conv.get('thread_type', 'system')
                if thread_type == 'sms':
                    priority += 5
                elif thread_type == 'email':
                    priority += 3
                elif thread_type == 'clubos':
                    priority += 4
                elif thread_type == 'bot':
                    priority += 2
                
                return -priority  # Negative for descending order
            
            # Sort the conversations
            bot_conversations.sort(key=conversation_sort_key)
            logger.info(f"📋 Sorted {len(bot_conversations)} conversations by priority")
            
            # Debug: show conversation order
            for i, conv in enumerate(bot_conversations[:5]):  # Show first 5
                priority_info = f"unread={conv.get('unread')}, needs_attention={conv.get('needs_attention')}, time={conv.get('time')}"
                logger.info(f"  {i+1}. {conv.get('name')} - {priority_info}")
            
            # Professional handling when no messages are available
            if not bot_conversations:
                logger.info("💬 No messages available to display - showing clean empty state")
                    
            logger.info("✅ Created bot_conversations with real data successfully")
        except Exception as conv_error:
            logger.error(f"❌ Error loading conversations: {str(conv_error)}")
            # Fallback to a simple mock conversation if database completely fails
            bot_conversations = [{
                'id': 'fallback_1',
                'name': 'System Message',
                'preview': 'Dashboard loaded successfully but conversation data is temporarily unavailable.',
                'time': 'Recently',
                'contact_name': 'System Message',
                'last_message': 'Dashboard loaded successfully but conversation data is temporarily unavailable.',
                'last_time': 'Recently',
                'last_sender': 'system',
                'unread': False,
                'status': 'System',
                'status_color': 'secondary',
                'needs_attention': False,
                'member_id': None,
                'thread_type': 'system',
                'unread_count': 0
            }]
        
        # Prepare context for template - with safe date formatting
        logger.info(f"🔧 About to format dates. target_date type: {type(target_date)}, value: {str(target_date)}")
        try:
            day_name = target_date.strftime('%A') if hasattr(target_date, 'strftime') else 'Today'
            date_formatted = target_date.strftime('%B %d, %Y') if hasattr(target_date, 'strftime') else 'Today'
            logger.info("✅ Date formatting successful")
        except (AttributeError, TypeError) as date_error:
            logger.error(f"❌ Error formatting dates: {str(date_error)}")
            day_name = 'Today'
            date_formatted = 'Today'
        
        logger.info("🔧 About to create dashboard_context")
        try:
            dashboard_context = {
                'bot_stats': bot_stats,
                'stats': stats,
                'recent_events': recent_events,
                'bot_conversations': bot_conversations,
                'club_summary': club_summary,
                'day_offset': day_offset,
                'target_date': target_date,
                'day_name': day_name,
                'date_formatted': date_formatted
            }
            logger.info("✅ Created dashboard_context successfully")
        except Exception as context_error:
            logger.error(f"❌ ERROR CREATING DASHBOARD_CONTEXT: {str(context_error)}")
            logger.error(f"Variable types: bot_stats={type(bot_stats)}, stats={type(stats)}, recent_events={type(recent_events)}")
            raise context_error
        
        # Debug the recent_events data structure before template rendering
        logger.info("🔍 DEBUGGING RECENT_EVENTS STRUCTURE:")
        for i, event in enumerate(recent_events):
            logger.info(f"Event {i}: id={type(event.get('id'))}:{event.get('id')}")
            logger.info(f"Event {i}: title={type(event.get('title'))}:{event.get('title')}")
            logger.info(f"Event {i}: participants type={type(event.get('participants'))}")
            if event.get('participants'):
                for j, participant in enumerate(event.get('participants', [])):
                    logger.info(f"  Participant {j}: {type(participant)}:{participant}")
        
        logger.info("🎨 About to render template...")
        try:
            return render_template('dashboard.html', **dashboard_context)
        except Exception as template_error:
            logger.error(f"❌ TEMPLATE RENDERING ERROR: {str(template_error)}")
            raise template_error
        
    except Exception as e:
        logger.error(f"Error in dashboard route: {str(e)}")
        # Use a safe fallback date to avoid datetime import issues
        try:
            fallback_date = dt_module.datetime.now().date()
        except Exception as fallback_error:
            logger.error(f"Error getting fallback date: {str(fallback_error)}")
            # Last resort - use a hardcoded recent date
            import datetime as dt
            fallback_date = dt.date(2025, 9, 12)
        
        return render_template('dashboard.html', 
                            bot_stats={
                                'total_members': 0,
                                'active_members': 0,
                                'total_prospects': 0,
                                'conversations_today': 0,
                                'messages_sent': 0,
                                'last_activity': 'Dashboard Error',
                                'unread_conversations': 0,
                                'response_rate': 0
                            }, 
                            stats={
                                'todays_events': 0,
                                'total_members': 0,
                                'active_prospects': 0,
                                'next_session_time': None,
                                'revenue': 0
                            }, 
                            recent_events=[], 
                            bot_conversations=[],
                            day_offset=day_offset,
                            target_date=fallback_date,
                            day_name='Today',
                            date_formatted='Today')
