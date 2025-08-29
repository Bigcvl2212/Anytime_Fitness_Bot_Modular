#!/usr/bin/env python3
"""
Training Routes (minimal, DB-first)
- /training-clients page
- /api/training-clients/all returns training clients directly from SQLite
No cache lookups. Names/packages/past due come straight from DB.
"""

from flask import Blueprint, jsonify, render_template, current_app
import logging
import sqlite3
import os
import json

logger = logging.getLogger(__name__)

training_bp = Blueprint('training', __name__)


def _get_db_connection():
    """Get a database connection with proper error handling for application context"""
    from flask import current_app
    
    try:
        # First try to get from current application context
        if current_app and hasattr(current_app, 'db_manager') and current_app.db_manager:
            return current_app.db_manager.get_connection()
    except RuntimeError as e:
        # Handle "Working outside of application context" error
        logger.warning(f"⚠️ No Flask application context available, using direct database path: {e}")
    
    # Fallback to absolute path
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'gym_bot.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def get_active_packages_and_past_due(member_id):
    """
    Get active package names and REAL past due amount for a training client.
    First try to get fresh data from ClubOS API, then fall back to database if that fails.
    
    Args:
        member_id (str): The clubos_member_id from training_clients table
        
    Returns:
        tuple: (list of package names, total past due amount)
    """
    from flask import current_app, Flask
    
    try:
        logger.info(f"🔍 Getting training packages for member {member_id}")
        
        # Set application context if needed
        flask_app = None
        within_app_context = False
        
        try:
            # First check if we are already in an app context
            within_app_context = current_app._get_current_object() is not None
        except RuntimeError:
            # We're outside app context, create a temporary one if needed
            import os
            import sys
            sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
            from flask import Flask
            flask_app = Flask(__name__)
            # Set a dummy secret key
            flask_app.secret_key = 'anytime-fitness-dashboard-temporary'
            # Configure the app
            from src.config.settings import create_app_config
            create_app_config(flask_app)
            within_app_context = False
        
        # Use the app context manager if we're not already in a context
        app_context = flask_app.app_context() if flask_app else None
        
        if app_context and not within_app_context:
            app_context.push()
            logger.info(f"🔄 Created temporary application context for member {member_id}")
        
        try:
            # Now we should have access to current_app safely
            
            # First try to get FRESH data from ClubOS API
            if hasattr(current_app, 'clubos') and current_app.clubos:
                try:
                    # Get package details from API
                    logger.info(f"🔄 Calling ClubOS API for member {member_id} package details")
                    package_details = current_app.clubos.get_training_package_details(str(member_id))
                    
                    if package_details and package_details.get('success'):
                        # Extract package names from agreements
                        agreement_ids = package_details.get('agreement_ids', [])
                        
                        # If there are agreement IDs, get their details to extract package names
                        package_names = []
                        if agreement_ids and current_app.clubos.authenticated:
                            for agreement_id in agreement_ids[:3]:  # Limit to 3 to avoid too many API calls
                                try:
                                    # Get agreement details
                                    agreements = current_app.clubos.get_member_agreements(str(member_id))
                                    for agreement in agreements:
                                        # Extract package name
                                        package_name = agreement.get('packageName') or agreement.get('name')
                                        if package_name and package_name not in package_names:
                                            package_names.append(package_name)
                                except Exception as agreement_error:
                                    logger.warning(f"⚠️ Error getting agreement details for {agreement_id}: {agreement_error}")
                        
                        # If no package names found, use a default
                        if not package_names:
                            package_names = ['Training Package']
                        
                        # Get past due amount from package details
                        past_due_amount = float(package_details.get('amount_owed', 0.0))
                        
                        # Save to database for future use
                        try:
                            save_package_data_to_db(str(member_id), package_names, past_due_amount)
                        except Exception as db_error:
                            logger.warning(f"⚠️ Could not save package data to database: {db_error}")
                        
                        logger.info(f"✅ Retrieved from API: {len(package_names)} packages, ${past_due_amount} past due for member {member_id}")
                        return package_names, past_due_amount
                except Exception as api_error:
                    logger.warning(f"⚠️ Could not get package details from API: {api_error}")
            
            # Fall back to database if API call fails
            logger.info(f"🔍 Falling back to database for member {member_id}")
            
            # Safely use app context for database operations
            db_path = None
            
            # First try to get database path from app context
            try:
                if current_app and hasattr(current_app, 'db_manager'):
                    # Get connection directly from the app's database manager
                    conn = current_app.db_manager.get_connection()
                else:
                    # Fall back to direct path
                    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'gym_bot.db')
                    conn = sqlite3.connect(db_path)
                    conn.row_factory = sqlite3.Row
            except RuntimeError:
                # Handle "Working outside of application context" error
                logger.warning(f"⚠️ No Flask application context available for {member_id}, using direct database path")
                db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'gym_bot.db')
                conn = sqlite3.connect(db_path)
                conn.row_factory = sqlite3.Row
        finally:
            # Clean up the temporary app context if we created one
            if app_context and not within_app_context:
                app_context.pop()
                logger.info(f"🔄 Released temporary application context for member {member_id}")
        
        
        # Execute database query
        cur = conn.cursor()
        cur.execute(
            """
            SELECT active_packages, past_due_amount
            FROM training_clients
            WHERE clubos_member_id = ?
            """, 
            (str(member_id),)
        )
        row = cur.fetchone()
        conn.close()
        
        if not row:
            logger.info(f"ℹ️ No training data found in database for member {member_id}")
            return [], 0.0
        
        # Extract package names
        active_packages = row['active_packages']
        package_names = []
        
        if isinstance(active_packages, list):
            package_names = active_packages
        elif isinstance(active_packages, str):
            if active_packages:
                # Try to parse as JSON first
                try:
                    parsed = json.loads(active_packages)
                    if isinstance(parsed, list):
                        package_names = parsed
                    else:
                        package_names = [str(parsed)]
                except json.JSONDecodeError:
                    # Not JSON, treat as comma-separated
                    if ',' in active_packages:
                        package_names = [name.strip() for name in active_packages.split(',')]
                    else:
                        package_names = [active_packages.strip()]
        
        # Use default if no packages found
        if not package_names:
            package_names = ['Training Package']
        
        # Get past due amount
        past_due_amount = float(row['past_due_amount'] or 0.0)
        
        logger.info(f"✅ Retrieved from database: {len(package_names)} packages, ${past_due_amount} past due for member {member_id}")
        return package_names, past_due_amount
        
    except Exception as e:
        logger.error(f"❌ Error getting active packages and past due for {member_id}: {e}")
        return ['Training Package'], 0.0


def save_package_data_to_db(member_id, package_names, past_due_amount):
    """Save package data to database for future use"""
    try:
        conn = _get_db_connection()
        cursor = conn.cursor()
        
        # Convert package names to JSON string
        if isinstance(package_names, list):
            package_names_json = json.dumps(package_names)
        else:
            package_names_json = json.dumps([str(package_names)])
        
        # Update the training client record
        cursor.execute(
            """
            UPDATE training_clients
            SET active_packages = ?, past_due_amount = ?, payment_status = ?
            WHERE clubos_member_id = ?
            """,
            (
                package_names_json,
                past_due_amount,
                'Past Due' if past_due_amount > 0 else 'Current',
                str(member_id)
            )
        )
        conn.commit()
        conn.close()
        logger.info(f"✅ Saved package data to database for member {member_id}")
        return True
    except Exception as e:
        logger.error(f"❌ Error saving package data to database: {e}")
        return False


@training_bp.route('/training-clients')
def training_clients_page():
    """Render training clients UI page."""
    try:
        count = 0
        try:
            conn = _get_db_connection()
            cur = conn.cursor()
            cur.execute('SELECT COUNT(*) FROM training_clients')
            row = cur.fetchone()
            count = row[0] if row else 0
            conn.close()
        except Exception:
            count = 0
        return render_template('training_clients.html', training_client_count=count)
    except Exception as e:
        logger.error(f"Error loading training clients page: {e}")
        return render_template('error.html', error=str(e))


@training_bp.route('/api/training-clients/all')
def get_all_training_clients():
    """DB-only: return training clients as stored by the sync."""
    try:
        conn = _get_db_connection()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, clubos_member_id, member_name, active_packages, past_due_amount,
                   payment_status, trainer_name, sessions_remaining, last_session,
                   email, phone
            FROM training_clients
            ORDER BY member_name COLLATE NOCASE
            """
        )
        rows = cur.fetchall()
        conn.close()

        clients = []
        for r in rows:
            row = {k: r[k] for k in r.keys()}
            name = row.get('member_name') or f"Client #{str(row.get('clubos_member_id') or '')[-4:]}"

            # Normalize active_packages -> list[str]
            active = row.get('active_packages')
            if isinstance(active, list):
                active_list = active or ['Training Package']
            elif isinstance(active, str):
                active = active.strip()
                if not active:
                    active_list = ['Training Package']
                else:
                    # try JSON first
                    try:
                        parsed = json.loads(active)
                        active_list = parsed if isinstance(parsed, list) else [str(parsed)]
                    except Exception:
                        active_list = [s.strip() for s in active.split(',')] if ',' in active else [active]
            else:
                active_list = ['Training Package']

            clients.append({
                'id': row.get('id'),
                'member_id': row.get('clubos_member_id'),
                'prospect_id': row.get('clubos_member_id'),
                'member_name': name,
                'active_packages': active_list,
                'past_due_amount': float(row.get('past_due_amount') or 0.0),
                'payment_status': row.get('payment_status') or 'Current',
                'trainer_name': row.get('trainer_name') or 'Jeremy Mayo',
                'sessions_remaining': row.get('sessions_remaining') or 0,
                'last_session': row.get('last_session') or 'Never',
                'email': row.get('email'),
                'phone': row.get('phone')
            })

        return jsonify({'success': True, 'training_clients': clients, 'source': 'database'})
    except Exception as e:
        logger.error(f"Error in /api/training-clients/all: {e}")
        return jsonify({'success': True, 'training_clients': [], 'source': 'error_fallback', 'error': str(e)})


@training_bp.route('/api/training-clients/<member_id>/packages')
def get_member_packages(member_id):
    """Get active packages and past due amount for a specific training client."""
    try:
        if not member_id:
            return jsonify({'success': False, 'error': 'Member ID is required'}), 400
            
        # Get active packages and real past due amount
        active_packages, past_due_amount = get_active_packages_and_past_due(str(member_id))
        
        payment_status = 'Past Due' if past_due_amount > 0 else 'Current'
        
        return jsonify({
            'success': True,
            'member_id': member_id,
            'active_packages': active_packages,
            'past_due_amount': past_due_amount,
            'payment_status': payment_status,
            'debug_packages_count': len(active_packages)
        })
        
    except Exception as e:
        logger.error(f"❌ Error getting packages for member {member_id}: {e}")
        return jsonify({
            'success': False, 
            'error': str(e),
            'member_id': member_id,
            'active_packages': [],
            'past_due_amount': 0.0,
            'payment_status': 'Error'
        }), 500
