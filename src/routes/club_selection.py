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
        
        data = request.get_json()
        selected_club_ids = data.get('club_ids', [])
        
        if not selected_club_ids:
            return jsonify({'error': 'Please select at least one club'}), 400
        
        # Validate and set selected clubs
        valid_clubs = multi_club_manager.set_selected_clubs(selected_club_ids)
        
        if not valid_clubs:
            return jsonify({'error': 'No valid clubs selected'}), 400
        
        # Store in session and force persistence
        session['selected_clubs'] = valid_clubs
        session.modified = True  # Force Flask to save session
        
        # Ensure the session is committed immediately
        try:
            # Just mark session as modified - Flask will handle the saving
            session.permanent = True
            session.modified = True
            logger.info(f"🔍 Session marked for save with selected_clubs: {session.get('selected_clubs')}")
        except Exception as save_error:
            logger.warning(f"⚠️ Could not mark session for save: {save_error}")
        
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
            
            # Create and start sync thread
            sync_thread = threading.Thread(
                target=enhanced_startup_sync, 
                args=(current_app._get_current_object(),), 
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
        
        # Force session save before generating response
        import time
        time.sleep(0.5)  # Give session time to save
        
        # Debug the generated redirect URL
        redirect_url = url_for('dashboard.dashboard')
        logger.info(f"🔍 Generated redirect URL: {redirect_url}")
        
        # Verify session was saved correctly
        logger.info(f"🔍 Final session state: authenticated={session.get('authenticated')}, selected_clubs={session.get('selected_clubs')}")
        
        response_data = {
            'success': True,
            'selected_clubs': valid_clubs,
            'club_names': club_names,
            'redirect_url': redirect_url,
            'message': f'Successfully selected: {", ".join(club_names)}'
        }
        
        logger.info(f"🚀 Sending response: {response_data}")
        return jsonify(response_data)
        
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
