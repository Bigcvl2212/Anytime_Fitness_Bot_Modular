#!/usr/bin/env python3
"""
Club Selection Screen - Allow users to choose which clubs to sync data from
"""

from flask import render_template, request, redirect, url_for, session, jsonify, flash, current_app
from flask import Blueprint
import logging
from src.services.multi_club_manager import multi_club_manager

logger = logging.getLogger(__name__)

club_selection_bp = Blueprint('club_selection', __name__)

@club_selection_bp.route('/club-selection')
def club_selection():
    """Display club selection screen"""
    try:
        # Enhanced session debugging
        logger.info(f"🔍 Club selection - Full session object: {session}")
        logger.info(f"🔍 Club selection - Session authenticated: {session.get('authenticated')}")
        logger.info(f"🔍 Club selection - Session manager_id: {session.get('manager_id')}")
        logger.info(f"🔍 Club selection - Session keys: {list(session.keys())}")
        logger.info(f"🔍 Club selection - Session permanent: {session.permanent}")
        logger.info(f"🔍 Club selection - Session modified: {session.modified}")
        
        # Check Flask app session config
        logger.info(f"🔍 Flask session config - Cookie name: {current_app.config.get('SESSION_COOKIE_NAME')}")
        logger.info(f"🔍 Flask session config - Cookie secure: {current_app.config.get('SESSION_COOKIE_SECURE')}")
        logger.info(f"🔍 Flask session config - Cookie httponly: {current_app.config.get('SESSION_COOKIE_HTTPONLY')}")
        
        # Check if session exists at all
        if not session or 'authenticated' not in session:
            logger.warning("❌ No session data found in club selection")
            flash('Session expired. Please log in again.', 'error')
            return redirect(url_for('auth.login'))
        
        # Use proper session validation
        from src.services.authentication.secure_auth_service import SecureAuthService
        auth_service = SecureAuthService()
        is_valid, manager_id = auth_service.validate_session()
        
        logger.info(f"🔍 Session validation result: is_valid={is_valid}, manager_id={manager_id}")
        
        if not is_valid:
            logger.warning("❌ Session validation failed in club selection")
            flash('Session expired. Please log in again.', 'error')
            return redirect(url_for('auth.login'))
        
        # Get available clubs from multi_club_manager
        available_clubs = multi_club_manager.get_available_clubs_for_selection()
        user_summary = multi_club_manager.get_user_summary()
        
        if not available_clubs:
            flash('No clubs available. Please contact support.', 'error')
            return redirect(url_for('auth.login'))
        
        # If user only has one club, skip selection and redirect to dashboard
        if len(available_clubs) == 1:
            single_club = available_clubs[0]
            multi_club_manager.set_selected_clubs([single_club['id']])
            session['selected_clubs'] = [single_club['id']]
            flash(f'Welcome to {single_club["name"]}!', 'success')
            return redirect(url_for('dashboard.dashboard'))
        
        return render_template('club_selection.html', 
                             available_clubs=available_clubs,
                             user_summary=user_summary)
        
    except Exception as e:
        logger.error(f"❌ Error in club selection: {e}")
        flash('Error loading club selection. Please try again.', 'error')
        return redirect(url_for('auth.login'))

@club_selection_bp.route('/select-clubs', methods=['POST'])
def select_clubs():
    """Handle club selection submission"""
    try:
        # Use proper session validation
        from src.services.authentication.secure_auth_service import SecureAuthService
        auth_service = SecureAuthService()
        is_valid, manager_id = auth_service.validate_session()
        
        if not is_valid:
            return jsonify({'error': 'Not logged in'}), 401
        
        # Handle both JSON and form data
        selected_club_ids = []
        
        # Try to get JSON data first
        data = request.get_json()
        if data:
            selected_club_ids = data.get('club_ids', [])
            logger.info(f"📥 Received JSON data: {data}")
        else:
            # Fallback to form data
            selected_club_ids = request.form.getlist('clubs')
            logger.info(f"📥 Received form data: clubs={selected_club_ids}")
        
        logger.info(f"🔍 Selected clubs for sync: {selected_club_ids}")
        
        if not selected_club_ids:
            logger.warning(f"❌ No clubs selected. Request data: JSON={request.get_json()}, Form={dict(request.form)}, Args={dict(request.args)}")
            return jsonify({'error': 'Please select at least one club'}), 400
        
        # Validate and set selected clubs
        valid_clubs = multi_club_manager.set_selected_clubs(selected_club_ids)
        
        if not valid_clubs:
            return jsonify({'error': 'No valid clubs selected'}), 400
        
        # Store in session and secure storage for persistence
        session['selected_clubs'] = valid_clubs
        session.permanent = True
        session.modified = True

        # PERMANENT FIX: Store in secure storage using session token
        from src.services.authentication.secure_auth_service import SecureAuthService
        auth_service = SecureAuthService()
        session_token = session.get('session_token')

        if session_token:
            success = auth_service.store_selected_clubs(session_token, valid_clubs)
            if success:
                logger.info(f"✅ Stored selected clubs in secure storage: {valid_clubs}")
            else:
                logger.warning(f"⚠️ Failed to store clubs in secure storage, using session only")
        
        # Debug: Verify session data is set correctly
        logger.info(f"🔍 Session after setting selected_clubs: {dict(session)}")
        logger.info(f"🔍 Session selected_clubs specifically: {session.get('selected_clubs')}")
        logger.info(f"🔍 Session permanent: {session.permanent}, modified: {session.modified}")
        
        # Get club names for display
        club_names = [multi_club_manager.get_club_name(club_id) for club_id in valid_clubs]
        
        logger.info(f"✅ User selected clubs: {club_names}")
        
        # Debug session after modification
        logger.info(f"🔍 Session after club selection: authenticated={session.get('authenticated')}, selected_clubs={session.get('selected_clubs')}")
        
        # Trigger startup sync for selected clubs
        try:
            import threading
            import time
            from src.services.multi_club_startup_sync import enhanced_startup_sync
            
            logger.info(f"🔄 Attempting to start data sync for clubs: {club_names}")
            
            # Create and start sync thread with selected clubs
            sync_thread = threading.Thread(
                target=enhanced_startup_sync, 
                args=(current_app._get_current_object(), valid_clubs), 
                daemon=True,
                name=f"DataSync-{'-'.join(map(str, valid_clubs))}"
            )
            sync_thread.start()
            
            logger.info(f"✅ Successfully started sync thread '{sync_thread.name}' for clubs: {club_names}")
            
            # Longer pause to ensure session is saved before returning redirect
            time.sleep(0.3)
            
        except ImportError as import_error:
            logger.error(f"❌ Failed to import sync module: {import_error}")
        except Exception as sync_error:
            logger.error(f"❌ Failed to start post-selection sync: {sync_error}")
            import traceback
            logger.error(f"Sync error traceback: {traceback.format_exc()}")
        
        # CRITICAL: Force session save multiple ways before generating response
        session.permanent = True
        session.modified = True
        
        # Force session to be saved by accessing it
        _ = session.get('authenticated')  # Access session to trigger save
        
        import time
        time.sleep(0.5)  # Give session time to save to storage
        
        # Debug the generated redirect URL - use explicit root path
        redirect_url = '/'  # Direct to root which should now properly map to dashboard
        logger.info(f"🔍 Generated redirect URL: {redirect_url} (explicit root path)")
        
        # Comprehensive session verification before response
        logger.info(f"🔍 ====== CLUB SELECTION SESSION DEBUG ======")
        logger.info(f"🔍 Final session state: authenticated={session.get('authenticated')}, selected_clubs={session.get('selected_clubs')}")
        logger.info(f"🔍 Session manager_id: {session.get('manager_id')}")
        logger.info(f"🔍 Session permanent: {session.permanent}")
        logger.info(f"🔍 Session modified: {session.modified}")
        logger.info(f"🔍 All session keys: {list(session.keys())}")
        logger.info(f"🔍 Full session data: {dict(session)}")
        
        # Test session validation again before response
        from src.services.authentication.secure_auth_service import SecureAuthService
        auth_service = SecureAuthService()
        is_still_valid, still_manager_id = auth_service.validate_session()
        logger.info(f"🔍 Session validation before response: valid={is_still_valid}, manager_id={still_manager_id}")
        
        response_data = {
            'success': True,
            'selected_clubs': valid_clubs,
            'club_names': club_names,
            'redirect_url': redirect_url,
            'message': f'Successfully selected: {", ".join(club_names)}'
        }
        
        logger.info(f"🚀 Sending response: {response_data}")
        logger.info(f"🔍 ====== CLUB SELECTION RESPONSE SENT ======")
        
        # Create response and force session to save before return
        response = jsonify(response_data)
        
        # One final session modification to ensure it gets saved
        session['last_club_selection'] = time.time()
        session.modified = True
        
        return response
        
    except Exception as e:
        logger.error(f"❌ Error selecting clubs: {e}")
        return jsonify({'error': 'Error selecting clubs'}), 500

@club_selection_bp.route('/club-selection/api/clubs')
def api_get_clubs():
    """API endpoint to get available clubs"""
    try:
        # Use proper session validation
        from src.services.authentication.secure_auth_service import SecureAuthService
        auth_service = SecureAuthService()
        is_valid, manager_id = auth_service.validate_session()
        
        if not is_valid:
            return jsonify({'error': 'Not logged in'}), 401
        
        available_clubs = multi_club_manager.get_available_clubs_for_selection()
        user_summary = multi_club_manager.get_user_summary()
        
        return jsonify({
            'clubs': available_clubs,
            'user': user_summary['user_info'],
            'is_multi_club': user_summary['is_multi_club']
        })
        
    except Exception as e:
        logger.error(f"❌ Error getting clubs API: {e}")
        return jsonify({'error': 'Error loading clubs'}), 500

@club_selection_bp.route('/change-clubs')
def change_clubs():
    """Allow user to change club selection"""
    try:
        # Use proper session validation
        from src.services.authentication.secure_auth_service import SecureAuthService
        auth_service = SecureAuthService()
        is_valid, manager_id = auth_service.validate_session()
        
        if not is_valid:
            flash('Please log in first', 'error')
            return redirect(url_for('auth.login'))
        
        # Clear current selection
        if 'selected_clubs' in session:
            del session['selected_clubs']
        multi_club_manager.set_selected_clubs([])
        
        flash('Club selection cleared. Please select clubs again.', 'info')
        return redirect(url_for('club_selection.club_selection'))
        
    except Exception as e:
        logger.error(f"❌ Error changing clubs: {e}")
        flash('Error changing clubs. Please try again.', 'error')
        return redirect(url_for('dashboard.dashboard'))
