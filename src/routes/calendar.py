#!/usr/bin/env python3
"""
Calendar Routes
Calendar management, event operations, and related functionality
"""

from flask import Blueprint, render_template, jsonify, current_app, request
import logging

logger = logging.getLogger(__name__)

calendar_bp = Blueprint('calendar', __name__)

@calendar_bp.route('/calendar')
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
			logger.error(f"❌ Error getting events from ClubOS: {e}")
			events = []
		
		# Enhanced name lookup for attendees
		enhanced_events = []
		for event in events:
			enhanced_event = event.copy()
			
			# Process attendees with proper name lookup
			if 'attendees' in event and event['attendees']:
				enhanced_attendees = []
				for attendee in event['attendees']:
					if attendee.get('name'):
						# Check if it's an email address
						if '@' in attendee['name']:
							# Look up proper name from database
							proper_name = current_app.db_manager.lookup_member_name_by_email(attendee['name'])
							if proper_name:
								enhanced_attendees.append({
									'name': proper_name,
									'email': attendee['name'],
									'original_name': attendee['name']
								})
							else:
								# Fallback: extract name from email
								email_name = attendee['name'].split('@')[0].replace('.', ' ').title()
								enhanced_attendees.append({
									'name': email_name,
									'email': attendee['name'],
									'original_name': attendee['name']
								})
						else:
							enhanced_attendees.append({
								'name': attendee['name'],
								'email': attendee.get('email', ''),
								'original_name': attendee['name']
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
		logger.error(f"❌ Error getting calendar events: {e}")
		return jsonify({
			'success': False,
			'error': str(e),
			'events': []
		}), 500
		
		# Format events for FullCalendar
		formatted_events = []
		for event in events:
			formatted_events.append({
				'id': getattr(event, 'id', None) or getattr(event, 'uid', None),
				'title': getattr(event, 'title', '') or getattr(event, 'name', ''),
				'start': getattr(event, 'start_time', None),
				'end': getattr(event, 'end_time', None),
				'description': getattr(event, 'description', ''),
				'location': getattr(event, 'location', ''),
				'attendees': getattr(event, 'attendee_names', [])
			})
		
		logger.info(f"✅ Retrieved {len(formatted_events)} calendar events")
		return jsonify(formatted_events)
		
	except Exception as e:
		logger.error(f"❌ Error getting calendar events: {e}")
		return jsonify([]), 500

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
