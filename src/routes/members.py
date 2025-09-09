#!/usr/bin/env python3
"""
Members Routes
Member management, profiles, and related functionality
"""

from flask import Blueprint, render_template, jsonify, request, current_app
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)

members_bp = Blueprint('members', __name__)

# Import the authentication decorator
from .auth import require_auth

@members_bp.route('/members')
@require_auth
def members_page():
    """Members page with categorized member lists."""
    try:
        # Get category counts for the tabs
        category_counts = current_app.db_manager.get_category_counts()
        
        # Get recent members for display
        recent_members = current_app.db_manager.get_recent_members(10)
        
        return render_template('members.html', 
                            category_counts=category_counts,
                            recent_members=recent_members)
                            
    except Exception as e:
        logger.error(f"❌ Error loading members page: {e}")
        return render_template('error.html', error=str(e))

@members_bp.route('/api/members/all')
def get_all_members():
    """Get all members from database or cache"""
    try:
        # First try to get from cache if available
        if hasattr(current_app, 'data_cache') and current_app.data_cache.get('members'):
            cached_members = current_app.data_cache['members']
            logger.info(f"✅ Retrieved {len(cached_members)} members from cache")
            return jsonify({'success': True, 'members': cached_members, 'source': 'cache'})

        # Fallback to database
        conn = current_app.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                prospect_id,
                id,
                guid,
                first_name,
                last_name,
                full_name,
                email,
                mobile_phone,
                status,
                status_message,
                amount_past_due,
                date_of_next_payment
            FROM members 
            ORDER BY full_name
        """)
        
        members = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        logger.info(f"✅ Retrieved {len(members)} members from database")
        return jsonify({'success': True, 'members': members, 'source': 'database'})
        
    except Exception as e:
        logger.error(f"❌ Error getting all members: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@members_bp.route('/api/member/<member_id>')
def get_member_profile(member_id):
    """Get comprehensive member profile data."""
    try:
        conn = current_app.db_manager.get_connection()
        cursor = conn.cursor()
        
        # Get basic member info
        cursor.execute("""
            SELECT * FROM members WHERE prospect_id = ?
        """, (member_id,))
        
        member = cursor.fetchone()
        if not member:
            return jsonify({'success': False, 'error': 'Member not found'}), 404
        
        member_data = dict(member)
        
        # Get category info
        cursor.execute("""
            SELECT category FROM member_categories WHERE member_id = ?
        """, (member_id,))
        
        category_result = cursor.fetchone()
        member_data['category'] = category_result[0] if category_result else 'Unknown'
        
        # Get training package info if available
        try:
            training_packages = current_app.clubos.get_member_agreements(member_id)
            member_data['training_packages'] = training_packages
        except Exception as e:
            logger.warning(f"⚠️ Could not get training packages for member {member_id}: {e}")
            member_data['training_packages'] = []
        
        # Get payment status
        member_data['payment_status'] = {
            'amount_past_due': member_data.get('amount_past_due', 0),
            'date_of_next_payment': member_data.get('date_of_next_payment'),
            'status': member_data.get('status'),
            'status_message': member_data.get('status_message')
        }
        
        conn.close()
        
        logger.info(f"✅ Retrieved profile for member {member_id}")
        return jsonify({'success': True, 'member': member_data})
        
    except Exception as e:
        logger.error(f"❌ Error getting member profile {member_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@members_bp.route('/api/members/past-due')
def get_past_due_members():
    """Get members with past due payments."""
    try:
        conn = current_app.db_manager.get_connection()
        cursor = conn.cursor()
        
        # Get members with past due amounts or past due status message
        cursor.execute("""
            SELECT 
                prospect_id,
                id,
                guid,
                first_name,
                last_name,
                full_name,
                email,
                mobile_phone,
                status,
                status_message,
                amount_past_due,
                base_amount_past_due,
                missed_payments,
                late_fees,
                date_of_next_payment,
                membership_start,
                last_visit,
                agreement_status,
                agreement_type,
                agreement_recurring_cost,
                agreement_name,
                agreement_billing_frequency
            FROM members 
            WHERE status_message LIKE '%Past Due 6-30 days%' 
               OR status_message LIKE '%Past Due more than 30 days%'
            ORDER BY amount_past_due DESC
        """)
        
        past_due_members = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        logger.info(f"✅ Retrieved {len(past_due_members)} past due members")
        return jsonify({'success': True, 'members': past_due_members})
        
    except Exception as e:
        logger.error(f"❌ Error getting past due members: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@members_bp.route('/api/members/category-counts')
def get_member_category_counts():
    """Get counts of members in each category."""
    try:
        category_counts = current_app.db_manager.get_category_counts()
        
        logger.info(f"✅ Retrieved category counts: {category_counts}")
        return jsonify({'success': True, 'counts': category_counts})
        
    except Exception as e:
        logger.error(f"❌ Error getting category counts: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@members_bp.route('/api/members/by-category/<category>')
def get_members_by_category(category):
    """Get members by specific category."""
    try:
        members = current_app.db_manager.get_members_by_category(category)
        if not members:
            # Emit a debug line to server logs with cache size and DB count
            try:
                cache_len = len(current_app.data_cache.get('members', [])) if hasattr(current_app, 'data_cache') else 0
            except Exception:
                cache_len = 0
            try:
                conn = current_app.db_manager.get_connection()
                cur = conn.cursor()
                cur.execute('SELECT COUNT(*) as c FROM members')
                db_count = cur.fetchone()['c']
                conn.close()
            except Exception:
                db_count = -1
            logger.info(f"ℹ️ Category '{category}' returned 0; cache={cache_len}, db_count={db_count}")
        
        logger.info(f"✅ Retrieved {len(members)} members in category '{category}'")
        return jsonify({'success': True, 'members': members, 'category': category})
        
    except Exception as e:
        logger.error(f"❌ Error getting members by category '{category}': {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@members_bp.route('/api/members/search')
def search_members():
    """Search for members by name."""
    try:
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify({'success': False, 'error': 'Search query required'}), 400
        
        conn = current_app.db_manager.get_connection()
        cursor = conn.cursor()
        
        # Search by first name, last name, or full name
        cursor.execute("""
            SELECT 
                prospect_id,
                id,
                guid,
                first_name,
                last_name,
                full_name,
                email,
                mobile_phone,
                status,
                status_message,
                amount_past_due,
                date_of_next_payment
            FROM members 
            WHERE first_name LIKE ? OR last_name LIKE ? OR full_name LIKE ?
            ORDER BY full_name
            LIMIT 10
        """, (f'%{query}%', f'%{query}%', f'%{query}%'))
        
        members = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        logger.info(f"✅ Search for '{query}' returned {len(members)} members")
        return jsonify({'success': True, 'members': members, 'query': query})
        
    except Exception as e:
        logger.error(f"❌ Error searching members for '{query}': {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@members_bp.route('/member/<member_id>')
def member_profile(member_id):
    """Member profile page."""
    try:
        # Get member data
        conn = current_app.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM members WHERE guid = ? OR prospect_id = ?
        """, (member_id, member_id))
        
        member = cursor.fetchone()
        if not member:
            return render_template('error.html', error='Member not found')
        
        member_data = dict(member)
        
        # Get category - use the actual guid from the member record
        member_guid = member['guid'] or member['prospect_id'] or member_id
        cursor.execute("""
            SELECT category FROM member_categories WHERE member_id = ?
        """, (member_guid,))
        
        category_result = cursor.fetchone()
        member_data['category'] = category_result[0] if category_result else 'Unknown'
        
        conn.close()
        
        return render_template('member_profile.html', member=member_data)
        
    except Exception as e:
        logger.error(f"❌ Error loading member profile {member_id}: {e}")
        return render_template('error.html', error=str(e))
