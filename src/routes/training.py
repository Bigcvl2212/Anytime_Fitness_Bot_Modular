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
    # Prefer app db_manager (has Row factory set)
    if hasattr(current_app, 'db_manager') and current_app.db_manager:
        return current_app.db_manager.get_connection()
    # Fallback to absolute path
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'gym_bot.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def get_active_packages_and_past_due(member_id):
    """
    Get active package names and REAL past due amount for a training client.
    
    Args:
        member_id (str): The clubos_member_id from training_clients table
        
    Returns:
        tuple: (list of package names, total past due amount)
    """
    try:
        logger.info(f"🔍 Getting training packages for member {member_id} from database")
        
        # Get package data from database
        conn = _get_db_connection()
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
