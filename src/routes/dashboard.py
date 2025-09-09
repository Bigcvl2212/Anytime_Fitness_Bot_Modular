#!/usr/bin/env python3
"""
Dashboard Routes
Main dashboard page and related functionality
"""

from flask import Blueprint, render_template, current_app, session, redirect, url_for, flash
from datetime import datetime, timedelta
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
        # Check for multi-club context
        from src.services.multi_club_manager import multi_club_manager
        
        # If no clubs selected but user has club access, redirect to selection
        selected_clubs = session.get('selected_clubs', [])
        if not selected_clubs and 'available_clubs' in session and session['available_clubs']:
            flash('Please select your clubs first.', 'info')
            return redirect(url_for('club_selection.club_selection'))
        
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
        
        # Format events for display with enhanced participant name mapping
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
                
                # Enhanced participant name mapping from training clients database with past due amounts
                enhanced_participants = []
                raw_participants = event.get('participants', [])
                
                # Ensure participants is a proper list of strings
                if isinstance(raw_participants, str):
                    raw_participants = [p.strip() for p in raw_participants.split(',') if p.strip()]
                elif not isinstance(raw_participants, list):
                    raw_participants = []

                for participant in raw_participants:
                    if participant and isinstance(participant, str) and participant.strip():
                        # Try to find the real name and past due info in training clients database
                        try:
                            conn = current_app.db_manager.get_connection()
                            cursor = conn.cursor()

                            # Look for training client by various name patterns
                            cursor.execute("""
                                SELECT member_name, first_name, last_name, member_id
                                FROM training_clients
                                WHERE LOWER(member_name) LIKE LOWER(?)
                                   OR LOWER(first_name || ' ' || last_name) LIKE LOWER(?)
                                   OR LOWER(?) LIKE LOWER(member_name)
                                ORDER BY created_at DESC
                                LIMIT 1
                            """, (f'%{participant}%', f'%{participant}%', participant))

                            training_client = cursor.fetchone()
                            conn.close()

                            if training_client:
                                # Use the real name from training clients database
                                real_name = training_client[0] or f"{training_client[1]} {training_client[2]}".strip()
                                member_id = training_client[3]

                                # Get past due amount for this training client
                                past_due_info = None
                                if member_id:
                                    try:
                                        # Use the ClubOS training API to get payment status and amount
                                        payment_data = current_app.clubos.get_complete_agreement_data(member_id)
                                        if payment_data and payment_data.get('success'):
                                            payment_status = payment_data.get('payment_status', 'Unknown')
                                            amount_owed = payment_data.get('amount_owed', 0.0)

                                            if payment_status == 'Past Due' and amount_owed > 0:
                                                past_due_info = {
                                                    'status': payment_status,
                                                    'amount': amount_owed,
                                                    'formatted_amount': f"${amount_owed:.2f}"
                                                }
                                    except Exception as payment_error:
                                        logger.warning(f"⚠️ Error getting payment data for member {member_id}: {payment_error}")

                                # Create enhanced participant with past due info
                                enhanced_participant = {
                                    'name': real_name,
                                    'original_name': participant,
                                    'past_due': past_due_info
                                }
                                enhanced_participants.append(enhanced_participant)
                                logger.info(f"✅ Mapped '{participant}' to '{real_name}' with past due: {past_due_info}")
                            else:
                                # Keep original name if no mapping found
                                enhanced_participants.append({
                                    'name': participant,
                                    'original_name': participant,
                                    'past_due': None
                                })
                                logger.debug(f"⚠️ No training client mapping found for '{participant}'")

                        except Exception as mapping_error:
                            logger.warning(f"⚠️ Error mapping participant '{participant}': {mapping_error}")
                            enhanced_participants.append({
                                'name': participant,
                                'original_name': participant,
                                'past_due': None
                            })
                    else:
                        enhanced_participants.append({
                            'name': participant,
                            'original_name': participant,
                            'past_due': None
                        })
                
                recent_events.append({
                    'id': event.get('id'),
                    'title': event.get('title'),
                    'participants': enhanced_participants,  # Use enhanced names
                    'start_time': start_time,
                    'end_time': end_time,
                    'trainer': event.get('trainer', ''),
                    'location': event.get('location', ''),
                })
            except Exception as e:
                logger.error(f"Error formatting event {event.get('id', 'unknown')}: {str(e)}")
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
        logger.error(f"Error in dashboard route: {str(e)}")
        return render_template('dashboard.html', 
                            bot_stats={}, 
                            stats={}, 
                            recent_events=[], 
                            sample_conversations=[],
                            day_offset=day_offset,
                            target_date=datetime.now().date(),
                            day_name='Today',
                            date_formatted='Today')
