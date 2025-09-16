#!/usr/bin/env python3
"""
Calendar Routes
Calendar management, event operations, and related functionality
"""

from flask import Blueprint, render_template, jsonify, current_app, request
import logging

logger = logging.getLogger(__name__)

calendar_bp = Blueprint('calendar', __name__)

# Import the authentication decorator
from .auth import require_auth

@calendar_bp.route('/calendar')
@require_auth
def calendar_page():
	"""Calendar page."""
	try:
		# Get today's events for display
		try:
			today_events = current_app.clubos.get_todays_events_lightweight()
		except Exception:
			today_events = []
		
		# Get calendar summary
		try:
			calendar_summary = current_app.clubos.get_calendar_summary()
		except Exception:
			calendar_summary = {
				'total_events': 0,
				'training_sessions': 0,
				'classes': 0,
				'updated_at': None
			}
		
		return render_template('calendar.html', 
							today_events=today_events,
							calendar_summary=calendar_summary)
							
	except Exception as e:
		logger.error(f"❌ Error loading calendar page: {e}")
		return render_template('error.html', error=str(e))

@calendar_bp.route('/api/calendar/events')
def get_calendar_events():
	"""Get calendar events for the specified date range with enhanced name lookup."""
	try:
		start_date = request.args.get('start', '')
		end_date = request.args.get('end', '')
		
		# Get events from ClubOS
		try:
			if hasattr(current_app, 'clubos') and current_app.clubos:
				events = current_app.clubos.get_events_for_date_range(start_date, end_date)
			else:
				events = []
		except Exception as e:
			logger.error(f"❌ Error getting events from ClubOS: {str(e)}")
			events = []
		
		# Enhanced name lookup for attendees
		enhanced_events = []
		for event in events:
			enhanced_event = event.copy()
			
			# Process attendees with proper name lookup from training clients database
			if 'attendees' in event and event['attendees']:
				enhanced_attendees = []
				for attendee in event['attendees']:
					if attendee.get('name'):
						original_name = attendee['name']
						enhanced_name = original_name
						
						# Check if it's an email address
						if '@' in original_name:
							# Look up proper name from database
							proper_name = current_app.db_manager.lookup_member_name_by_email(original_name)
							if proper_name:
								enhanced_name = proper_name
							else:
								# Fallback: extract name from email
								enhanced_name = original_name.split('@')[0].replace('.', ' ').title()
						else:
								# Try to find the real name and past due info in training clients database
								past_due_info = None
								try:
									# Look for training client by various name patterns
									training_client = current_app.db_manager.execute_query("""
										SELECT member_name, first_name, last_name, full_name, member_id, prospect_id
										FROM training_clients
										WHERE LOWER(member_name) LIKE LOWER(?)
										   OR LOWER(first_name || ' ' || last_name) LIKE LOWER(?)
										   OR LOWER(full_name) LIKE LOWER(?)
										   OR LOWER(?) LIKE LOWER(member_name)
										ORDER BY created_at DESC
										LIMIT 1
									""", (f'%{original_name}%', f'%{original_name}%', f'%{original_name}%', original_name), fetch_one=True)

									if training_client:
										# Use the real name from training clients database
										enhanced_name = training_client[0] or training_client[3] or f"{training_client[1]} {training_client[2]}".strip()
										member_id = training_client[4]

										# Get past due amount for this training client
										if member_id:
											try:
												# Use the ClubOS training API to get payment status and amount
												payment_data = current_app.clubos.training_api.get_complete_agreement_data(member_id)
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
												logger.warning(f"⚠️ Calendar error getting payment data for member {member_id}: {payment_error}")

									logger.info(f"✅ Calendar mapped '{original_name}' to '{enhanced_name}' with past due: {past_due_info}")

								except Exception as mapping_error:
									logger.warning(f"⚠️ Calendar error mapping attendee '{original_name}': {mapping_error}")

						enhanced_attendees.append({
							'name': enhanced_name,
							'email': attendee.get('email', ''),
							'original_name': original_name,
							'past_due': past_due_info
						})
				
				enhanced_event['attendees'] = enhanced_attendees
				enhanced_event['participants'] = ', '.join([att['name'] for att in enhanced_attendees])
			
			# Add funding status if available
			enhanced_event['funding_loaded'] = False  # Default
			if 'attendees' in enhanced_event:
				for attendee in enhanced_event['attendees']:
					if attendee.get('email'):
						# Check if member has funding info
						try:
							funding_query = """
								SELECT funding_status FROM funding_status_cache 
								WHERE LOWER(member_email) = LOWER(?)
								LIMIT 1
							"""
							funding_results = current_app.db_manager.execute_query(funding_query, (attendee['email'],))
							if funding_results:
								enhanced_event['funding_loaded'] = True
								break
						except Exception:
							pass
			
			enhanced_events.append(enhanced_event)
		
		return jsonify({
			'success': True,
			'events': enhanced_events,
			'total_events': len(enhanced_events),
			'date_range': {
				'start': start_date,
				'end': end_date
			}
		})
		
	except Exception as e:
		logger.error(f"❌ Error getting calendar events: {str(e)}")
		return jsonify({
			'success': False,
			'error': str(e),
			'events': []
		}), 500

@calendar_bp.route('/api/debug/agreement/<agreement_id>/invoices')
def debug_agreement_invoices(agreement_id):
    """Debug endpoint to get invoices for a specific agreement."""
    try:
        # Get invoices from ClubOS
        invoices = current_app.clubos.get_agreement_invoices(agreement_id)
        
        if invoices:
            logger.info(f"✅ Retrieved {len(invoices)} invoices for agreement {agreement_id}")
            return jsonify({'success': True, 'invoices': invoices})
        else:
            logger.info(f"ℹ️ No invoices found for agreement {agreement_id}")
            return jsonify({'success': True, 'invoices': []})
            
    except Exception as e:
        logger.error(f"❌ Error getting invoices for agreement {agreement_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@calendar_bp.route('/api/debug/agreement/<agreement_id>/v2-raw')
def debug_agreement_v2_raw(agreement_id):
    """Debug endpoint to get raw agreement data."""
    try:
        # Get raw agreement data from ClubOS
        # This would be implemented based on the specific ClubOS API structure
        logger.info(f"🔍 Getting raw agreement data for {agreement_id}")
        
        # Placeholder for raw agreement data
        raw_data = {
            'agreement_id': agreement_id,
            'status': 'Not implemented',
            'message': 'Raw agreement data endpoint not yet implemented'
        }
        
        return jsonify({'success': True, 'raw_data': raw_data})
        
    except Exception as e:
        logger.error(f"❌ Error getting raw agreement data for {agreement_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
