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
    """Decorator to require authentication for routes - SIMPLIFIED VERSION"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            route_name = request.endpoint or "unknown_route"

            # Debug: Log current session state
            logger.info(f"🔍 AUTH CHECK - Route: {route_name}")
            logger.info(f"🔍 AUTH CHECK - Session keys: {list(session.keys())}")
            logger.info(f"🔍 AUTH CHECK - Session authenticated: {session.get('authenticated')}")
            logger.info(f"🔍 AUTH CHECK - Session manager_id: {session.get('manager_id')}")
            logger.info(f"🔍 AUTH CHECK - Session selected_clubs: {session.get('selected_clubs')}")

            # SIMPLIFIED AUTH: Just check Flask session directly
            if not session.get('authenticated') or not session.get('manager_id'):
                logger.warning(f"❌ AUTH FAILED for route {route_name}")
                logger.warning(f"❌ authenticated: {session.get('authenticated')}")
                logger.warning(f"❌ manager_id: {session.get('manager_id')}")
                logger.warning(f"❌ REDIRECTING TO LOGIN")

                # IMPORTANT: Preserve club selection data before clearing
                # This prevents losing selected clubs if there's a temporary auth hiccup
                preserved_data = {
                    'selected_clubs': session.get('selected_clubs'),
                    'available_clubs': session.get('available_clubs'),
                    'user_info': session.get('user_info')
                }

                session.clear()

                # Restore preserved data if it existed
                if preserved_data.get('selected_clubs'):
                    session['selected_clubs'] = preserved_data['selected_clubs']
                    logger.info(f"🔄 Preserved selected_clubs: {preserved_data['selected_clubs']}")
                if preserved_data.get('available_clubs'):
                    session['available_clubs'] = preserved_data['available_clubs']
                if preserved_data.get('user_info'):
                    session['user_info'] = preserved_data['user_info']

                session.modified = True
                return redirect(url_for('auth.login'))

            # Check session timeout
            if 'login_time' in session:
                try:
                    from datetime import datetime, timedelta
                    login_time = datetime.fromisoformat(session['login_time'])
                    session_age = datetime.now() - login_time

                    # 8 hour timeout
                    if session_age > timedelta(hours=8):
                        logger.warning(f"⚠️ Session expired for {route_name}: age={session_age}")

                        # Preserve club selection data before clearing
                        preserved_data = {
                            'selected_clubs': session.get('selected_clubs'),
                            'available_clubs': session.get('available_clubs'),
                            'user_info': session.get('user_info')
                        }

                        session.clear()

                        # Restore preserved data
                        if preserved_data.get('selected_clubs'):
                            session['selected_clubs'] = preserved_data['selected_clubs']
                        if preserved_data.get('available_clubs'):
                            session['available_clubs'] = preserved_data['available_clubs']
                        if preserved_data.get('user_info'):
                            session['user_info'] = preserved_data['user_info']

                        session.modified = True
                        flash('Your session has expired. Please log in again.', 'info')
                        return redirect(url_for('auth.login'))
                except (ValueError, TypeError):
                    # Invalid time format, but don't fail - just update it
                    from datetime import datetime
                    session['login_time'] = datetime.now().isoformat()
                    session.modified = True

            # Update last activity
            try:
                from datetime import datetime
                session['last_activity'] = datetime.now().isoformat()
                session.modified = True
            except:
                pass  # Don't fail on activity update

            # Debug: Log successful validation
            logger.info(f"✅ AUTH DECORATOR SUCCESS - {route_name} - manager_id={session.get('manager_id')}")

            # Session is valid, proceed with the request
            return f(*args, **kwargs)

        except Exception as e:
            logger.error(f"❌ Authentication exception for {route_name}: {e}")
            import traceback
            logger.error(f"❌ Exception traceback: {traceback.format_exc()}")
            return redirect(url_for('auth.login'))

    return decorated_function

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login route - simple username/password"""
    if request.method == 'GET':
        success_msg = request.args.get('success')
        return render_template('login_new.html', success=success_msg)

    try:
        # Get form data
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        if not username or not password:
            return render_template('login_new.html', error='Username and password are required')

        # Get admin service
        admin_service = current_app.admin_service

        # Find user by username
        admin_user = admin_service.admin_schema.get_admin_user_by_username(username)

        if not admin_user:
            logger.warning(f"⚠️ Login attempt with non-existent username: {username}")
            return render_template('login_new.html', error='Invalid username or password')

        # Verify password
        from werkzeug.security import check_password_hash
        stored_password_hash = admin_user.get('password_hash')

        if not stored_password_hash:
            logger.error(f"❌ No password hash found for user: {username}")
            return render_template('login_new.html', error='Account not properly configured. Please contact support.')

        if not check_password_hash(stored_password_hash, password):
            logger.warning(f"⚠️ Failed login attempt for user: {username}")
            return render_template('login_new.html', error='Invalid username or password')

        # Successfully authenticated!
        manager_id = admin_user['manager_id']

        # Create session manually (don't use auth_service since we're not using ClubOS/ClubHub to login)
        session['authenticated'] = True
        session['manager_id'] = manager_id
        session['username'] = username
        session.permanent = True

        # Add timestamps expected by SecureAuthService.validate_session()
        # (club selection and other routes may rely on these keys).
        from datetime import datetime
        now_iso = datetime.now().isoformat()
        session['login_time'] = now_iso
        session['last_activity'] = now_iso

        logger.info(f"✅ Manager {username} ({manager_id}) logged in successfully from {request.remote_addr}")

        # DISABLED: Automated access monitoring (causing errors)
        # TODO: Re-enable after fixing ClubHub authentication and adding log_access_action to DatabaseManager
        # try:
        #     if hasattr(current_app, 'start_monitoring_after_auth'):
        #         current_app.start_monitoring_after_auth()
        #         logger.info("🔐 Automated access monitoring started after login")
        # except Exception as e:
        #     logger.warning(f"⚠️ Could not start automated access monitoring: {e}")

        # Get stored ClubHub credentials to check for multi-club access
        from ..services.authentication.secure_secrets_manager import SecureSecretsManager
        secrets_manager = SecureSecretsManager()

        logger.info(f"🔍 Attempting to retrieve credentials for manager_id: {manager_id}")
        credentials = secrets_manager.get_credentials(manager_id)
        logger.info(f"🔍 Credentials retrieved: {credentials is not None}")
        if credentials:
            logger.info(f"🔍 Has clubhub_email: {credentials.get('clubhub_email') is not None}")
            logger.info(f"🔍 Has clubhub_password: {credentials.get('clubhub_password') is not None}")

        # Fallback to environment variables if database credentials not available/decryptable
        import os
        clubhub_email = None
        clubhub_password = None
        if credentials and credentials.get('clubhub_email') and credentials.get('clubhub_password'):
            clubhub_email = credentials.get('clubhub_email')
            clubhub_password = credentials.get('clubhub_password')
            logger.info("🔍 Using database credentials for ClubHub")
        else:
            clubhub_email = os.getenv('CLUBHUB_EMAIL')
            clubhub_password = os.getenv('CLUBHUB_PASSWORD')
            if clubhub_email and clubhub_password:
                logger.info("🔍 Using environment variable credentials for ClubHub")
            else:
                logger.warning("⚠️ No ClubHub credentials found in database or environment")

        if clubhub_email and clubhub_password:
            # Try to authenticate with ClubHub to get club access
            from src.services.multi_club_manager import multi_club_manager

            try:
                # Import ClubHub auth
                from ..services.authentication.clubhub_auth import ClubHubAuth
                clubhub_auth = ClubHubAuth()

                clubhub_token = clubhub_auth.authenticate(
                    clubhub_email,
                    clubhub_password
                )

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

                        # ALWAYS redirect to club selection - let user confirm their club(s)
                        # even if they only have access to one club
                        flash(f'Welcome {user_info.get("name", "Manager")}! Please select your clubs.', 'success')
                        return redirect(url_for('club_selection.club_selection'))
                    else:
                        logger.warning("❌ No club access found in JWT token")
                        flash('No club access found. Please contact support.', 'error')
                        return redirect(url_for('auth.login'))
                else:
                    # ClubHub auth failed - redirect to club selection
                    logger.info(f"⚠️ ClubHub authentication failed for {username}, redirecting to club selection")
                    flash(f'Welcome {username}! Please select your clubs.', 'success')
                    return redirect(url_for('club_selection.club_selection'))

            except Exception as clubhub_error:
                logger.warning(f"⚠️ ClubHub authentication error: {clubhub_error}")
                # Redirect to club selection
                flash(f'Welcome {username}! Please select your clubs.', 'success')
                return redirect(url_for('club_selection.club_selection'))
        else:
            # No ClubHub credentials - redirect to club selection
            logger.info(f"ℹ️ No ClubHub credentials found for {username}, redirecting to club selection")
            flash(f'Welcome {username}! Please select your clubs.', 'success')
            return redirect(url_for('club_selection.club_selection'))
            
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
    """Registration route - create new manager account"""
    if request.method == 'GET':
        return render_template('register_new.html')

    try:
        # Get form data
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        email = request.form.get('email', '').strip()

        clubos_username = request.form.get('clubos_username', '').strip()
        clubos_password = request.form.get('clubos_password', '').strip()
        clubhub_email = request.form.get('clubhub_email', '').strip()
        clubhub_password = request.form.get('clubhub_password', '').strip()
        square_access_token = request.form.get('square_access_token', '').strip()
        square_location_id = request.form.get('square_location_id', '').strip()

        # Validate all fields are present
        if not all([username, password, confirm_password, email, clubos_username, clubos_password,
                    clubhub_email, clubhub_password, square_access_token, square_location_id]):
            return render_template('register_new.html', error='All fields are required')

        # Validate password match
        if password != confirm_password:
            return render_template('register_new.html', error='Passwords do not match')

        # Validate password length
        if len(password) < 8:
            return render_template('register_new.html', error='Password must be at least 8 characters')

        # Validate username length
        if len(username) < 3:
            return render_template('register_new.html', error='Username must be at least 3 characters')

        # Check if username already exists
        admin_service = current_app.admin_service
        existing_user = admin_service.admin_schema.get_admin_user_by_username(username)

        if existing_user:
            return render_template('register_new.html', error='Username already exists. Please choose another.')

        # Generate manager_id from username
        import hashlib
        manager_id = hashlib.sha256(username.lower().encode()).hexdigest()[:16]

        # Create admin user account
        success = admin_service.admin_schema.add_admin_user(
            manager_id=manager_id,
            username=username,
            email=email,
            is_super_admin=False
        )

        if not success:
            return render_template('register_new.html', error='Failed to create account. Please try again.')

        # Store password hash in admin system
        from werkzeug.security import generate_password_hash
        password_hash = generate_password_hash(password)
        admin_service.admin_schema.update_admin_user(
            manager_id=manager_id,
            updates={'password_hash': password_hash}
        )

        # Store API credentials
        from ..services.authentication.secure_secrets_manager import SecureSecretsManager
        secrets_manager = SecureSecretsManager()

        # Store ClubOS and ClubHub credentials
        creds_success = secrets_manager.store_credentials(
            manager_id=manager_id,
            clubos_username=clubos_username,
            clubos_password=clubos_password,
            clubhub_email=clubhub_email,
            clubhub_password=clubhub_password
        )

        if not creds_success:
            # Rollback: delete admin user
            admin_service.admin_schema.delete_admin_user(manager_id)
            return render_template('register_new.html', error='Failed to store credentials. Please try again.')

        # Store Square credentials
        secrets_manager.set_secret(f'square-access-token-{manager_id}', square_access_token)
        secrets_manager.set_secret(f'square-location-id-{manager_id}', square_location_id)

        logger.info(f"✅ New user registered: {username} ({manager_id})")

        # Redirect to login with success message
        return redirect(url_for('auth.login', success='Account created successfully! Please login.'))

    except Exception as e:
        logger.error(f"❌ Registration error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return render_template('register_new.html', error=f'Registration failed: {str(e)}')
