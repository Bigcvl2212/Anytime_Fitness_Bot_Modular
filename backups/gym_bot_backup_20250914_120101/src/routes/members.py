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
                date_of_next_payment
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

@members_bp.route('/api/refresh-data', methods=['POST'])
def api_refresh_data():
    """Refresh all member data from ClubHub API with comprehensive agreement processing."""
    try:
        logger.info("🔄 Starting comprehensive member data refresh from ClubHub...")
        
        # Import required modules
        from src.services.api.clubhub_api_client import ClubHubAPIClient
        from src.services.authentication.secure_secrets_manager import SecureSecretsManager
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        # Get credentials from SecureSecretsManager
        secrets_manager = SecureSecretsManager()
        clubhub_email = secrets_manager.get_secret('clubhub-email')
        clubhub_password = secrets_manager.get_secret('clubhub-password')
        
        if not clubhub_email or not clubhub_password:
            return jsonify({
                'success': False,
                'error': 'ClubHub credentials not found in SecureSecretsManager'
            }), 500
        
        # Initialize and authenticate
        client = ClubHubAPIClient()
        if not client.authenticate(clubhub_email, clubhub_password):
            return jsonify({
                'success': False,
                'error': 'ClubHub authentication failed'
            }), 500
        
        # Get basic member and prospect data
        logger.info("👥 Fetching basic member data from ClubHub...")
        fresh_members = client.get_all_members_paginated()
        fresh_prospects = client.get_all_prospects_paginated()
        
        if not fresh_members:
            return jsonify({
                'success': False,
                'error': 'No member data returned from ClubHub'
            }), 500
            
        logger.info(f"📊 Processing {len(fresh_members)} members with agreement data...")
        
        def get_member_agreement_data(member_data):
            """Get agreement data for a single member (same logic as startup sync)"""
            try:
                member_data['full_name'] = f"{member_data.get('firstName', '')} {member_data.get('lastName', '')}".strip()
                
                member_id = member_data.get('id') or member_data.get('prospectId')
                if member_id:
                    agreement_data = client.get_member_agreement(member_id)
                    if agreement_data and isinstance(agreement_data, dict):
                        # Get the TOTAL past due amount from API
                        total_amount_past_due = float(agreement_data.get('amountPastDue', 0))
                        
                        # Initialize billing breakdown
                        late_fees = 0.0
                        missed_payments = 0
                        base_amount = 0.0
                        recurring_cost = 0.0
                        
                        # Extract recurring cost from various possible fields
                        if 'monthlyDues' in agreement_data and agreement_data['monthlyDues']:
                            recurring_cost = float(agreement_data['monthlyDues']) or 0.0
                        elif 'amountOfNextPayment' in agreement_data and agreement_data['amountOfNextPayment']:
                            recurring_cost = float(agreement_data['amountOfNextPayment']) or 0.0
                        elif 'recurringCost' in agreement_data and isinstance(agreement_data['recurringCost'], dict):
                            recurring_cost = float(agreement_data['recurringCost'].get('total', 0)) or 0.0
                        
                        # Check for comp member status
                        is_comp_member = (
                            str(agreement_data.get('statusMessage', '')).lower().startswith('comp') or
                            str(member_data.get('user_type', '')).lower() == 'comp'
                        )
                        
                        if total_amount_past_due > 0 and not is_comp_member:
                            if recurring_cost == 0:
                                recurring_cost = 39.50  # Standard AF monthly rate
                            
                            # Calculate billing breakdown
                            base_amount = total_amount_past_due
                            missed_payments = max(1, int(base_amount / recurring_cost))
                            late_fees = missed_payments * 19.50
                            total_with_fees = base_amount + late_fees
                            
                            member_data['amount_past_due'] = total_with_fees
                            member_data['base_amount_past_due'] = base_amount
                            member_data['late_fees'] = late_fees
                            member_data['missed_payments'] = missed_payments
                        else:
                            member_data['amount_past_due'] = total_amount_past_due
                            member_data['base_amount_past_due'] = total_amount_past_due
                            member_data['late_fees'] = 0.0
                            member_data['missed_payments'] = 0
                        
                        # Store additional agreement data
                        member_data['agreement_recurring_cost'] = recurring_cost
                        member_data['agreement_status'] = agreement_data.get('status', 'Unknown')
                        member_data['agreement_type'] = agreement_data.get('type', 'Unknown')
                        member_data['date_of_next_payment'] = agreement_data.get('dateOfNextPayment')
                        member_data['status_message'] = agreement_data.get('statusMessage', '')
                        
                    else:
                        # No agreement data
                        member_data['amount_past_due'] = 0.0
                        member_data['base_amount_past_due'] = 0.0
                        member_data['late_fees'] = 0.0
                        member_data['missed_payments'] = 0
                        member_data['agreement_recurring_cost'] = 0.0
                        member_data['agreement_status'] = 'No Agreement'
                
                return member_data
            except Exception as e:
                logger.warning(f"⚠️ Could not get agreement data for member {member_data.get('firstName', 'Unknown')}: {e}")
                member_data['amount_past_due'] = 0.0
                member_data['base_amount_past_due'] = 0.0
                member_data['late_fees'] = 0.0
                member_data['missed_payments'] = 0
                member_data['agreement_recurring_cost'] = 0.0
                return member_data
        
        # Process members with agreement data in parallel
        with ThreadPoolExecutor(max_workers=15) as executor:
            future_to_member = {executor.submit(get_member_agreement_data, member): member for member in fresh_members}
            
            completed_count = 0
            for future in as_completed(future_to_member):
                completed_count += 1
                if completed_count % 100 == 0:
                    logger.info(f"📊 Members: {completed_count}/{len(fresh_members)} processed...")
        
        logger.info(f"✅ Members: {len(fresh_members)} processed with agreement data")
        
        # Calculate billing summary
        total_past_due = sum(m.get('amount_past_due', 0) for m in fresh_members)
        members_with_past_due = len([m for m in fresh_members if m.get('amount_past_due', 0) > 0])
        
        logger.info(f"💰 Billing Summary: {members_with_past_due} members with past due amounts, total: ${total_past_due:.2f}")
        
        # Update database
        members_success = current_app.db_manager.save_members_to_db(fresh_members)
        prospects_success = current_app.db_manager.save_prospects_to_db(fresh_prospects) if fresh_prospects else True
        
        if members_success and prospects_success:
            member_count = current_app.db_manager.get_member_count()
            
            logger.info(f"✅ Successfully refreshed {len(fresh_members)} members with billing data")
            
            return jsonify({
                'success': True,
                'message': 'Data refreshed successfully from ClubHub with comprehensive agreement data',
                'counts': {
                    'members': len(fresh_members),
                    'prospects': len(fresh_prospects) if fresh_prospects else 0,
                    'total_db_members': member_count,
                    'members_with_past_due': members_with_past_due,
                    'total_past_due_amount': round(total_past_due, 2)
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to save data to database'
            }), 500
            
    except Exception as e:
        logger.error(f"❌ Error refreshing data: {e}")
        return jsonify({
            'success': False,
            'error': f'Data refresh error: {str(e)}'
        }), 500

@members_bp.route('/api/refresh-billing-data', methods=['POST'])
def api_refresh_billing_data():
    """Refresh billing data from ClubHub by pulling membership agreement data for all members."""
    try:
        logger.info("🔄 Starting billing data refresh from ClubHub API...")
        
        # Import ClubHub API client
        from src.services.api.clubhub_api_client import ClubHubAPIClient
        from src.services.authentication.secure_secrets_manager import SecureSecretsManager
        
        # Get credentials from SecureSecretsManager
        secrets_manager = SecureSecretsManager()
        clubhub_email = secrets_manager.get_secret('clubhub-email')
        clubhub_password = secrets_manager.get_secret('clubhub-password')
        
        if not clubhub_email or not clubhub_password:
            return jsonify({
                'success': False,
                'error': 'ClubHub credentials not found in SecureSecretsManager'
            }), 500
        
        # Initialize and authenticate
        client = ClubHubAPIClient()
        if not client.authenticate(clubhub_email, clubhub_password):
            return jsonify({
                'success': False,
                'error': 'ClubHub authentication failed'
            }), 500
        
        # Get all members from database to update their billing info
        conn = current_app.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT prospect_id, guid, first_name, last_name FROM members")
        member_records = cursor.fetchall()
        
        updated_members = []
        past_due_members = []
        total_past_due_amount = 0.0
        total_base_amount = 0.0
        total_late_fees = 0.0
        total_missed_payments = 0
        errors = []
        
        logger.info(f"🔄 Processing {len(member_records)} members for billing data...")
        
        for i, member_row in enumerate(member_records, 1):
            member_id = member_row['prospect_id'] or member_row['guid']
            if not member_id:
                continue
                
            try:
                # Get member agreement data from ClubHub
                agreement_data = client.get_member_agreement(member_id)
                
                if agreement_data and isinstance(agreement_data, dict):
                    # Extract billing information from agreement
                    amount_past_due = float(agreement_data.get('amount_past_due', 0))
                    base_amount_past_due = float(agreement_data.get('base_amount_past_due', 0))
                    late_fees = float(agreement_data.get('late_fees', 0))
                    missed_payments = int(agreement_data.get('missed_payments', 0))
                    date_of_next_payment = agreement_data.get('date_of_next_payment')
                    status = agreement_data.get('status', '')
                    status_message = agreement_data.get('status_message', '')
                    
                    # Update member billing info in database
                    billing_data = {
                        'amount_past_due': amount_past_due,
                        'base_amount_past_due': base_amount_past_due,
                        'late_fees': late_fees,
                        'missed_payments': missed_payments,
                        'date_of_next_payment': date_of_next_payment,
                        'status': status,
                        'status_message': status_message
                    }
                    
                    current_app.db_manager.update_member_billing_info(member_id, billing_data)
                    updated_members.append(member_id)
                    
                    # Track past due totals
                    if amount_past_due > 0:
                        past_due_members.append({
                            'member_id': member_id,
                            'name': f"{member_row['first_name']} {member_row['last_name']}",
                            'amount_past_due': amount_past_due,
                            'base_amount': base_amount_past_due,
                            'late_fees': late_fees,
                            'missed_payments': missed_payments
                        })
                        total_past_due_amount += amount_past_due
                        total_base_amount += base_amount_past_due
                        total_late_fees += late_fees
                        total_missed_payments += missed_payments
                
                # Progress logging every 50 members
                if i % 50 == 0:
                    logger.info(f"🔄 Processed {i}/{len(member_records)} members...")
                        
            except Exception as member_error:
                error_msg = f"Failed to update billing for member {member_id} ({member_row['first_name']} {member_row['last_name']}): {member_error}"
                logger.warning(f"⚠️ {error_msg}")
                errors.append(error_msg)
                continue
        
        conn.close()
        
        logger.info(f"✅ Billing refresh complete: {len(updated_members)} updated, {len(past_due_members)} past due, ${total_past_due_amount:.2f} total")
        
        return jsonify({
            'success': True,
            'message': 'Billing data refreshed successfully from ClubHub membership agreements',
            'total_processed': len(member_records),
            'updated_members': len(updated_members),
            'past_due_members': len(past_due_members),
            'total_past_due_amount': round(total_past_due_amount, 2),
            'total_base_amount': round(total_base_amount, 2),
            'total_late_fees': round(total_late_fees, 2),
            'total_missed_payments': total_missed_payments,
            'past_due_details': past_due_members[:10],  # First 10 for preview
            'errors': len(errors),
            'error_details': errors[:5] if errors else [],  # First 5 errors for debugging
            'timestamp': datetime.now().isoformat()
        })
            
    except Exception as e:
        logger.error(f"❌ Error refreshing billing data: {e}")
        return jsonify({
            'success': False,
            'error': f'Billing data refresh error: {str(e)}'
        }), 500

@members_bp.route('/api/members/monthly-revenue')
def get_monthly_revenue():
    """Get monthly revenue calculation from valid revenue-generating members only."""
    try:
        revenue_data = current_app.db_manager.get_monthly_revenue_calculation()
        
        logger.info(f"✅ Monthly revenue calculation: ${revenue_data['total_monthly_revenue']:.2f}")
        return jsonify({
            'success': True,
            'revenue_data': revenue_data,
            'breakdown': {
                'member_revenue': revenue_data['member_revenue'],
                'training_revenue': revenue_data['training_revenue'],
                'total_monthly_revenue': revenue_data['total_monthly_revenue'],
                'revenue_members_count': revenue_data['revenue_members_count'],
                'training_clients_count': revenue_data['training_clients_count']
            }
        })
        
    except Exception as e:
        logger.error(f"❌ Error getting monthly revenue: {e}")
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
