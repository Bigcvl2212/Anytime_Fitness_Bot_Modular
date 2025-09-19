#!/usr/bin/env python3
"""
Authentication routes for the Anytime Fitness Dashboard
"""

import logging
from flask import Blueprint, request, render_template, redirect, url_for, flash, session, current_app
from functools import wraps

logger = logging.getLogger(__name__)

# Create authentication blueprint
auth_bp = Blueprint('auth', __name__)

def require_auth(f):
    """Decorator to require authentication for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # Import authentication service and datetime
            from src.services.authentication.secure_auth_service import SecureAuthService
            from datetime import datetime, timedelta
            auth_service = SecureAuthService()
            
            # Minimal logging for performance - only log failures
            route_name = request.endpoint or "unknown_route"
            
            # Ensure session persistence before validation
            if session:
                session.permanent = True
                session.modified = True
            
            # Quick session check - simplified validation
            if not session or not session.get('authenticated') or not session.get('manager_id'):
                logger.warning(f"❌ Fast auth check failed for {route_name} - missing session data")
                return redirect(url_for('auth.login'))
            
            # Check session timeout only (skip full validation for performance)
            if 'login_time' in session:
                try:
                    from datetime import datetime, timedelta
                    login_time = datetime.fromisoformat(session['login_time'])
                    session_age = datetime.now() - login_time
                    
                    # 8 hour timeout
                    if session_age > timedelta(hours=8):
                        logger.warning(f"⚠️ Session expired for {route_name}: age={session_age}")
                        session.clear()
                        return redirect(url_for('auth.login'))
                except (ValueError, TypeError):
                    # Invalid time format, but don't fail - just update it
                    session['login_time'] = datetime.now().isoformat()
                    session.modified = True
            
            # Update last activity silently
            try:
                session['last_activity'] = datetime.now().isoformat()
                session.modified = True
            except:
                pass  # Don't fail on activity update
            
            # Session is valid, proceed with the request
            return f(*args, **kwargs)
            
        except Exception as e:
            logger.error(f"❌ Authentication exception for {route_name}: {e}")
            return redirect(url_for('auth.login'))
    
    return decorated_function

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login route"""
    if request.method == 'GET':
        return render_template('login.html')
    
    try:
        # Import validation functions
        from src.utils.validation import FormValidator
        
        # Validate form data
        validation_result = FormValidator.validate_login_form(request.form)
        
        if not validation_result['is_valid']:
            for error in validation_result['errors']:
                flash(error, 'error')
            return render_template('login.html')
        
        # Use sanitized data
        form_data = validation_result['sanitized_data']
        clubos_username = form_data['clubos_username']
        clubos_password = form_data['clubos_password']
        clubhub_email = form_data['clubhub_email']
        clubhub_password = form_data['clubhub_password']
        
        # Import authentication service
        from src.services.authentication.secure_auth_service import SecureAuthService
        auth_service = SecureAuthService()
        
        # Authenticate
        success, manager_id, error_msg = auth_service.authenticate_manager(
            clubos_username, clubos_password, clubhub_email, clubhub_password
        )
        
        if success:
            # Create session
            session_token = auth_service.create_session(manager_id)
            
            # Debug: Check session immediately after creation
            logger.info(f"🔍 Session immediately after creation: authenticated={session.get('authenticated')}, manager_id={session.get('manager_id')}")
            
            logger.info(f"✅ Manager {manager_id} logged in successfully from {request.remote_addr}")
            
            # Get authentication tokens to check for multi-club access
            from src.services.multi_club_manager import multi_club_manager
            
            # Try to get JWT token from the auth service
            clubhub_token = getattr(auth_service, 'clubhub_token', None)
            
            if clubhub_token:
                # Parse JWT token to extract club access
                club_ids, user_info = multi_club_manager.extract_club_access(clubhub_token)
                
                if club_ids:
                    logger.info(f"🏢 User has access to {len(club_ids)} clubs: {club_ids}")
                    
                    # Store in session for persistence
                    session['user_info'] = user_info
                    session['available_clubs'] = club_ids
                    
                    # Force session to be saved after adding club data
                    session.modified = True
                    
                    # If multi-club user, redirect to club selection
                    if len(club_ids) > 1:
                        flash(f'Welcome {user_info.get("name", "Manager")}! Please select your clubs.', 'success')
                        return redirect(url_for('club_selection.club_selection'))
                    else:
                        # Single club - auto-select and go to dashboard
                        multi_club_manager.set_selected_clubs(club_ids)
                        session['selected_clubs'] = club_ids
                        
                        # Force session to be saved after setting selected clubs
                        session.modified = True
                        
                        club_name = multi_club_manager.get_club_name(club_ids[0])
                        
                        # Trigger startup sync for this club
                        try:
                            import threading
                            from src.services.multi_club_startup_sync import enhanced_startup_sync
                            
                            # Ensure the sync has the club context
                            def run_sync_with_context():
                                try:
                                    with current_app.app_context():
                                        logger.info(f"🔄 Starting data sync for club {club_ids[0]} after single-club authentication")
                                        result = enhanced_startup_sync(current_app._get_current_object())
                                        logger.info(f"✅ Sync completed: {result.get('success', False)}")
                                except Exception as sync_inner_error:
                                    logger.error(f"❌ Sync execution failed: {sync_inner_error}")
                            
                            sync_thread = threading.Thread(target=run_sync_with_context, daemon=True)
                            sync_thread.start()
                            logger.info(f"🔄 Started data sync thread for club {club_ids[0]} after authentication")
                            
                        except Exception as sync_error:
                            logger.warning(f"⚠️ Could not start post-auth sync: {sync_error}")
                            import traceback
                            logger.warning(f"⚠️ Sync error traceback: {traceback.format_exc()}")
                        
                        flash(f'Welcome {user_info.get("name", "Manager")} to {club_name}!', 'success')
                        return redirect(url_for('dashboard.dashboard'))
                else:
                    logger.warning("❌ No club access found in JWT token")
                    flash('No club access found. Please contact support.', 'error')
                    return redirect(url_for('auth.login'))
            else:
                # Fallback for single club (backward compatibility)
                flash(f'Welcome! Successfully authenticated as manager {manager_id}.', 'success')
                return redirect(url_for('dashboard.dashboard'))
        else:
            logger.warning(f"❌ Failed login attempt from {request.remote_addr}: {error_msg}")
            flash(f'Login failed: {error_msg}', 'error')
            return render_template('login.html', error=error_msg)
            
    except Exception as e:
        logger.error(f"❌ Login error: {e}")
        flash('An error occurred during login. Please try again.', 'error')
        return render_template('login.html')

@auth_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    """Logout route"""
    try:
        # Clear session
        session.clear()
        flash('You have been logged out successfully.', 'info')
        logger.info(f"✅ User logged out from {request.remote_addr}")
    except Exception as e:
        logger.error(f"❌ Logout error: {e}")
    
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Registration route - placeholder for future implementation"""
    if request.method == 'GET':
        return render_template('register.html')
    
    # For now, redirect to login
    flash('Registration is not yet implemented. Please contact your administrator.', 'info')
    return redirect(url_for('auth.login'))
