#!/usr/bin/env python3
"""
Members Routes
Member management, profiles, and related functionality
"""

from flask import Blueprint, render_template, jsonify, request, current_app
import logging
import json
from datetime import datetime
import datetime as dt

logger = logging.getLogger(__name__)

members_bp = Blueprint('members', __name__)

# Import the authentication decorator
from .auth import require_auth

@members_bp.route('/test-collections')
def test_collections_page():
    """Test page for collections without any authentication"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Collections Test</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container mt-5">
            <h1>Collections Management Test</h1>
            <button class="btn btn-danger" onclick="openCollectionsModal()">
                <i class="fas fa-gavel me-1"></i>
                Test Collections Modal
            </button>
        </div>
        
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            function openCollectionsModal() {
                fetch('/api/collections/past-due')
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            alert('Collections API working! Found ' + data.total_count + ' past due accounts');
                            console.log('Past due data:', data.past_due_data);
                        } else {
                            alert('Error: ' + data.error);
                        }
                    })
                    .catch(error => {
                        alert('Network error: ' + error);
                    });
            }
        </script>
    </body>
    </html>
    """

@members_bp.route('/members')
@require_auth
def members_page():
    """OPTIMIZED: Members page loads instantly with progressive data loading."""
    try:
        # Get only fast category counts (using indexes)
        category_counts = current_app.db_manager.get_category_counts()
        
        # PERFORMANCE: Don't load recent members during route - load via AJAX
        # This makes the page load instantly
        recent_members = []  # Will be loaded via JavaScript
        
        return render_template('members.html', 
                            category_counts=category_counts,
                            recent_members=recent_members,
                            loading_members=True)  # Flag for progressive loading
                            
    except Exception as e:
        logger.error(f"❌ Error loading members page: {e}")
        # Even on error, return fast
        return render_template('members.html',
                            category_counts={'ppv': 0, 'comp': 0, 'frozen': 0, 'active': 0, 'past_due': 0},
                            recent_members=[],
                            loading_members=True,
                            error=str(e))

@members_bp.route('/api/members/all')
def get_all_members():
    """Get all members from database with optional category filtering"""
    try:
        category = request.args.get('category')
        limit = request.args.get('limit', type=int)

        # Map category to status_message values
        category_mapping = {
            'good_standing': ['Member is in good standing', 'In good standing'],
            'pay_per_visit': ['Pay Per Visit Member'],
            'past_due_6_30': ['Past Due 6-30 days'],
            'past_due_30_plus': ['Past Due more than 30 days.'],
            'expiring_soon': ['Member is pending cancel', 'Expiring Soon'],
            'past_due_training': [],  # Special handling below
            'other_statuses': []  # Special handling below
        }

        if category:
            # Special handling for past_due_training
            if category == 'past_due_training':
                query = """
                    SELECT clubos_member_id as prospect_id, clubos_member_id as id,
                           first_name, last_name, member_name as full_name, email, mobile_phone,
                           payment_status as status, total_past_due as amount_past_due,
                           payment_status as status_message
                    FROM training_clients
                    WHERE total_past_due > 0
                    ORDER BY full_name
                """
                if limit:
                    query += f" LIMIT {limit}"
                result = current_app.db_manager.execute_query(query, fetch_all=True)
                members = [dict(row) for row in result] if result else []
                logger.info(f"✅ Retrieved {len(members)} training members (past due)")
                return jsonify({'success': True, 'members': members, 'source': 'database'})

            # Special handling for other_statuses
            elif category == 'other_statuses':
                excluded_statuses = [
                    'Member is in good standing', 'In good standing',
                    'Pay Per Visit Member', 'Past Due 6-30 days',
                    'Past Due more than 30 days.', 'Member is pending cancel', 'Expiring Soon'
                ]
                placeholders = ','.join(['?' for _ in excluded_statuses])
                query = f"""
                    SELECT prospect_id, id, first_name, last_name, full_name, email,
                           mobile_phone, status, amount_past_due, status_message
                    FROM members
                    WHERE status_message IS NOT NULL
                      AND status_message NOT IN ({placeholders})
                      AND status_message NOT LIKE '%good standing%'
                      AND status_message NOT LIKE '%expir%'
                    ORDER BY full_name
                """
                if limit:
                    query += f" LIMIT {limit}"
                result = current_app.db_manager.execute_query(query, tuple(excluded_statuses), fetch_all=True)
                members = [dict(row) for row in result] if result else []
                logger.info(f"✅ Retrieved {len(members)} members (other statuses)")
                return jsonify({'success': True, 'members': members, 'source': 'database'})

            # Regular category filtering
            else:
                status_messages = category_mapping.get(category, [])
                if status_messages:
                    placeholders = ','.join(['?' for _ in status_messages])
                    query = f"""
                        SELECT prospect_id, id, first_name, last_name, full_name, email,
                               mobile_phone, status, amount_past_due, status_message
                        FROM members
                        WHERE status_message IN ({placeholders})
                        ORDER BY full_name
                    """
                    if limit:
                        query += f" LIMIT {limit}"
                    result = current_app.db_manager.execute_query(query, tuple(status_messages), fetch_all=True)
                    members = [dict(row) for row in result] if result else []
                    logger.info(f"✅ Retrieved {len(members)} members for category {category}")
                    return jsonify({'success': True, 'members': members, 'source': 'database'})
                else:
                    # Unknown category
                    logger.warning(f"⚠️ Unknown category: {category}")
                    return jsonify({'success': True, 'members': [], 'source': 'database'})

        # No category filter - return all members
        # First try cache
        if hasattr(current_app, 'data_cache') and current_app.data_cache.get('members'):
            cached_members = current_app.data_cache['members']
            logger.info(f"✅ Retrieved {len(cached_members)} members from cache")
            return jsonify({'success': True, 'members': cached_members, 'source': 'cache'})

        # Fallback to database
        query = """
            SELECT prospect_id, id, first_name, last_name, full_name, email,
                   mobile_phone, status, amount_past_due, status_message
            FROM members
            ORDER BY full_name
        """
        if limit:
            query += f" LIMIT {limit}"

        result = current_app.db_manager.execute_query(query, fetch_all=True)
        members = [dict(row) for row in result] if result else []

        # Log categorization debug info
        status_counts = {}
        for member in members:
            status_msg = member.get('status_message', 'None')
            status_counts[status_msg] = status_counts.get(status_msg, 0) + 1

        logger.info(f"✅ Retrieved {len(members)} members from database")
        logger.info(f"📊 Status message distribution: {dict(list(status_counts.items())[:10])}")

        return jsonify({'success': True, 'members': members, 'source': 'database'})

    except Exception as e:
        logger.error(f"❌ Error getting all members: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@members_bp.route('/api/member/<member_id>')
def get_member_profile(member_id):
    """Get comprehensive member profile data."""
    try:
        profile_bundle = current_app.db_manager.get_member_profile_context(member_id)
        if not profile_bundle:
            return jsonify({'success': False, 'error': 'Member not found'}), 404

        member_data = profile_bundle.get('member', {})
        member_key = member_data.get('guid') or member_data.get('prospect_id') or member_id

        category_result = current_app.db_manager.execute_query(
            "SELECT category FROM member_categories WHERE member_id = ?",
            (str(member_key),),
            fetch_one=True
        )
        if category_result:
            member_data['category'] = category_result['category']

        response_payload = {'success': True}
        response_payload.update(profile_bundle)

        logger.info(f"✅ Retrieved profile bundle for member {member_id}")
        return jsonify(response_payload)

    except Exception as e:
        logger.error(f"❌ Error getting member profile {member_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@members_bp.route('/api/members/<member_id>/payment-plan', methods=['GET'])
@require_auth
def api_get_payment_plan(member_id):
    """Return the current payment plan for a member."""
    try:
        plan = current_app.db_manager.get_payment_plan(member_id)
        return jsonify({'success': True, 'payment_plan': plan})
    except Exception as e:
        logger.error(f"❌ Error retrieving payment plan for {member_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@members_bp.route('/api/members/<member_id>/payment-plan', methods=['POST'])
@require_auth
def api_save_payment_plan(member_id):
    """Create or replace a manual payment plan for a member."""
    try:
        payload = request.get_json() or {}
        plan = current_app.db_manager.save_payment_plan(member_id, payload)
        return jsonify({'success': True, 'payment_plan': plan})
    except ValueError as ve:
        logger.warning(f"⚠️ Invalid payment plan payload for {member_id}: {ve}")
        return jsonify({'success': False, 'error': str(ve)}), 400
    except Exception as e:
        logger.error(f"❌ Error saving payment plan for {member_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@members_bp.route('/api/members/<member_id>/payment-plan/installments/<int:installment_id>', methods=['PATCH'])
@require_auth
def api_mark_installment_paid(member_id, installment_id):
    """Mark a specific payment plan installment as paid."""
    try:
        payload = request.get_json() or {}
        paid_amount = payload.get('amount_paid')
        paid_date = payload.get('paid_date')
        plan = current_app.db_manager.mark_payment_plan_installment_paid(
            member_id,
            installment_id,
            paid_amount=paid_amount,
            paid_date=paid_date
        )
        return jsonify({'success': True, 'payment_plan': plan})
    except ValueError as ve:
        logger.warning(f"⚠️ Could not update installment {installment_id} for {member_id}: {ve}")
        return jsonify({'success': False, 'error': str(ve)}), 400
    except Exception as e:
        logger.error(f"❌ Error updating installment {installment_id} for {member_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@members_bp.route('/api/members/past-due')
def get_past_due_members():
    """Get members with past due payments."""
    try:
        with current_app.db_manager.get_cursor() as cursor:
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
                    phone,
                    address,
                    city,
                    state,
                    zip_code,
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

            past_due_data = cursor.fetchall()
            past_due_members = [dict(row) for row in past_due_data] if past_due_data else []

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
                cur = current_app.db_manager.get_cursor(conn)
                cur.execute('SELECT COUNT(*) as c FROM members')
                db_count = cur.fetchone()['c']
                conn.close()
            except Exception:
                db_count = -1
            logger.info(f"ℹ️ Category '{category}' returned 0; cache={cache_len}, db_count={db_count}")
        
        # Convert SQLite Row objects to dictionaries for JSON serialization
        members_list = [dict(member) for member in members] if members else []

        logger.info(f"✅ Retrieved {len(members)} members in category '{category}'")
        return jsonify({'success': True, 'members': members_list, 'category': category})
        
    except Exception as e:
        logger.error(f"❌ Error getting members by category '{category}': {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@members_bp.route('/api/members/search')
def search_members():
    """Search for members by name."""
    try:
        # Accept both 'q' and 'name' parameters for flexibility
        query = request.args.get('name', request.args.get('q', '')).strip()
        if not query:
            return jsonify({'success': False, 'error': 'Search query required'}), 400

        # More aggressive search - try multiple variations
        search_variations = [
            query,  # Exact search
            query.replace(' ', ''),  # No spaces
            query.replace('_', ' '),  # Replace underscores with spaces
            query.split()[0] if ' ' in query else query,  # First name only
            query.split()[-1] if ' ' in query else query,  # Last name only
        ]

        members = None
        for search_name in search_variations:
            if not search_name:
                continue

            members = current_app.db_manager.execute_query("""
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
                WHERE LOWER(first_name) LIKE LOWER(?)
                   OR LOWER(last_name) LIKE LOWER(?)
                   OR LOWER(full_name) LIKE LOWER(?)
                   OR LOWER(first_name || ' ' || last_name) LIKE LOWER(?)
                   OR LOWER(full_name) = LOWER(?)
                   OR LOWER(first_name || ' ' || last_name) = LOWER(?)
                ORDER BY
                    CASE WHEN LOWER(full_name) = LOWER(?) THEN 1
                         WHEN LOWER(first_name || ' ' || last_name) = LOWER(?) THEN 2
                         ELSE 3 END,
                    full_name
                LIMIT 10
            """, (f'%{search_name}%', f'%{search_name}%', f'%{search_name}%', f'%{search_name}%',
                  search_name, search_name, search_name, search_name), fetch_all=True)

            if members and len(members) > 0:
                logger.info(f"🎯 Found members with variation '{search_name}': {len(members)}")
                break

        # Convert to list of dicts if not already
        members = [dict(row) for row in members] if members else []

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
                        
                        # Extract agreement ID and GUID for collections tracking
                        member_data['agreement_id'] = agreement_data.get('agreementID')
                        member_data['agreement_guid'] = agreement_data.get('agreementGuid')
                        
                    else:
                        # No agreement data
                        member_data['amount_past_due'] = 0.0
                        member_data['base_amount_past_due'] = 0.0
                        member_data['late_fees'] = 0.0
                        member_data['missed_payments'] = 0
                        member_data['agreement_recurring_cost'] = 0.0
                        member_data['agreement_status'] = 'No Agreement'
                        member_data['agreement_id'] = None
                        member_data['agreement_guid'] = None
                
                return member_data
            except Exception as e:
                logger.warning(f"⚠️ Could not get agreement data for member {member_data.get('firstName', 'Unknown')}: {e}")
                member_data['amount_past_due'] = 0.0
                member_data['base_amount_past_due'] = 0.0
                member_data['late_fees'] = 0.0
                member_data['missed_payments'] = 0
                member_data['agreement_recurring_cost'] = 0.0
                member_data['agreement_id'] = None
                member_data['agreement_guid'] = None
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
    """Refresh billing data from ClubHub using the WORKING sync method that includes agreement data."""
    try:
        logger.info("🔄 Starting billing data refresh using multi_club_startup_sync...")
        
        # Use the WORKING sync method from multi_club_startup_sync
        from src.services.multi_club_startup_sync import sync_members_for_club
        
        # Run the sync that we KNOW works (includes agreement data AND preserves addresses)
        members_with_billing = sync_members_for_club(app=current_app)
        
        if not members_with_billing:
            return jsonify({
                'success': False,
                'error': 'No members returned from sync'
            }), 500
        
        # CRITICAL: Save to database (preserves existing addresses via REPLACE INTO)
        logger.info(f"💾 Saving {len(members_with_billing)} members with billing data to database...")
        save_success = current_app.db_manager.save_members_to_db(members_with_billing)
        
        if not save_success:
            logger.error("❌ Failed to save members to database")
            return jsonify({
                'success': False,
                'error': 'Failed to save billing data to database'
            }), 500
        
        logger.info("✅ Billing data saved to database successfully!")
        
        # Calculate summary stats
        past_due_members = [m for m in members_with_billing if m.get('amount_past_due', 0) > 0]
        total_past_due_amount = sum(m.get('amount_past_due', 0) for m in past_due_members)
        total_base_amount = sum(m.get('base_amount_past_due', 0) for m in past_due_members)
        total_late_fees = sum(m.get('late_fees', 0) for m in past_due_members)
        total_missed_payments = sum(m.get('missed_payments', 0) for m in past_due_members)
        
        logger.info(f"✅ Billing refresh complete: {len(members_with_billing)} members synced, {len(past_due_members)} past due, ${total_past_due_amount:.2f} total")
        
        return jsonify({
            'success': True,
            'message': 'Billing data refreshed successfully from ClubHub with agreement data',
            'total_processed': len(members_with_billing),
            'updated_members': len(members_with_billing),
            'past_due_members': len(past_due_members),
            'total_past_due_amount': round(total_past_due_amount, 2),
            'total_base_amount': round(total_base_amount, 2),
            'total_late_fees': round(total_late_fees, 2),
            'total_missed_payments': total_missed_payments,
            'past_due_details': [
                {
                    'member_id': m.get('prospect_id'),
                    'name': m.get('full_name'),
                    'amoualso nt_past_due': m.get('amount_past_due', 0),
                    'base_amount': m.get('base_amount_past_due', 0),
                    'late_fees': m.get('late_fees', 0),
                    'missed_payments': m.get('missed_payments', 0)
                }
                for m in past_due_members[:10]
            ],
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
    """Get total monthly revenue calculation for dashboard (members + training)."""
    try:
        revenue_data = current_app.db_manager.get_monthly_revenue_calculation()
        
        logger.info(f"✅ Monthly revenue calculation: ${revenue_data['total_monthly_revenue']:.2f}")
        return jsonify({
            'success': True,
            'revenue_data': revenue_data,
            'breakdown': {
                'member_revenue': revenue_data['total_monthly_revenue'],  # Use total as member revenue
                'training_revenue': 0.0,  # Training revenue not calculated yet
                'total_monthly_revenue': revenue_data['total_monthly_revenue'],
                'revenue_members_count': revenue_data['active_members'],
                'training_clients_count': 0  # Training clients count not calculated yet
            }
        })
        
    except Exception as e:
        logger.error(f"❌ Error getting monthly revenue: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@members_bp.route('/api/members/membership-revenue')
def get_membership_revenue():
    """Get membership-only revenue calculation (excludes training)."""
    try:
        revenue_data = current_app.db_manager.get_monthly_revenue_calculation()
        
        # Return only membership revenue
        membership_revenue = revenue_data.get('total_monthly_revenue', 0)
        membership_count = revenue_data.get('active_members', 0)
        
        logger.info(f"✅ Membership revenue calculation: ${membership_revenue:.2f}")
        
        return jsonify({
            'success': True,
            'revenue_data': {
                'membership_revenue': membership_revenue,
                'membership_count': membership_count
            }
        })
        
    except Exception as e:
        logger.error(f"❌ Error getting membership revenue: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'revenue_data': {
                'membership_revenue': 0,
                'membership_count': 0
            }
        })

@members_bp.route('/api/training/training-revenue')
def get_training_revenue():
    """Get training-only revenue calculation (excludes memberships)."""
    try:
        revenue_data = current_app.db_manager.get_monthly_revenue_calculation()
        
        # Return only training revenue
        training_revenue = revenue_data.get('training_revenue', 0)
        training_count = revenue_data.get('training_clients_count', 0)
        
        logger.info(f"✅ Training revenue calculation: ${training_revenue:.2f}")
        
        return jsonify({
            'success': True,
            'revenue_data': {
                'training_revenue': training_revenue,
                'training_count': training_count
            }
        })
        
    except Exception as e:
        logger.error(f"❌ Error getting training revenue: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'revenue_data': {
                'training_revenue': 0,
                'training_count': 0
            }
        })

@members_bp.route('/member/<member_id>')
def member_profile(member_id):
    """Member profile page - searches both members and prospects."""
    try:
        # Handle null/empty member_id
        if not member_id or member_id == 'null' or member_id == 'undefined':
            logger.warning(f"❌ Invalid member_id provided: {member_id}")
            return render_template('error.html', error='No member ID provided')
        profile_bundle = current_app.db_manager.get_member_profile_context(member_id)

        if profile_bundle:
            member = profile_bundle['member']
            member['is_prospect'] = False
            member_guid = member.get('guid') or member.get('prospect_id') or member_id

            category_result = current_app.db_manager.execute_query(
                "SELECT category FROM member_categories WHERE member_id = ?",
                (str(member_guid),),
                fetch_one=True
            )
            if category_result:
                member['category'] = category_result['category']

            # Normalize datetime objects for template rendering
            for key, value in list(member.items()):
                if isinstance(value, (dt.datetime, dt.date)):
                    member[key] = value.isoformat()

            return render_template(
                'member_profile.html',
                member=member,
                member_id=member_id,
                payment_status=profile_bundle.get('payment_status'),
                agreements=profile_bundle.get('agreements') or [],
                payments=profile_bundle.get('payments') or [],
                training_packages=profile_bundle.get('training_packages') or [],
                membership_summary=profile_bundle.get('membership_summary') or {},
                payment_plan=profile_bundle.get('payment_plan'),
                invoices=profile_bundle.get('invoices') or []
            )

        # Fallback to legacy member/prospect lookup when database bundle is unavailable
        member = None
        is_prospect = False

        member = current_app.db_manager.execute_query(
            "SELECT * FROM members WHERE guid = ? OR prospect_id = ?",
            (member_id, member_id),
            fetch_one=True
        )

        if not member:
            logger.info(f"🔍 Not found in members, trying prospects table for: {member_id}")
            member = current_app.db_manager.execute_query(
                "SELECT * FROM prospects WHERE full_name = ? COLLATE NOCASE",
                (member_id,),
                fetch_one=True
            )
            if member:
                is_prospect = True
                logger.info(f"✅ Found prospect by exact name match: {member_id}")

        if not member and ' ' in member_id:
            logger.info(f"🔍 Trying name search in members for: {member_id}")
            name_parts = member_id.rsplit(' ', 1)
            if len(name_parts) == 2:
                first_name, last_name = name_parts
                member = current_app.db_manager.execute_query(
                    """
                    SELECT * FROM members
                    WHERE LOWER(first_name) = LOWER(?) AND LOWER(last_name) = LOWER(?)
                    LIMIT 1
                    """,
                    (first_name, last_name),
                    fetch_one=True
                )

                if not member:
                    logger.info(f"🔍 Trying exact name search in prospects for: {member_id}")
                    member = current_app.db_manager.execute_query(
                        """
                        SELECT * FROM prospects
                        WHERE LOWER(first_name) = LOWER(?) AND LOWER(last_name) = LOWER(?)
                        LIMIT 1
                        """,
                        (first_name, last_name),
                        fetch_one=True
                    )
                    if member:
                        is_prospect = True
                        logger.info(f"✅ Found prospect by name parts: {first_name} {last_name}")

        if not member:
            logger.warning(f"❌ Member/Prospect not found: {member_id}")
            return render_template('error.html', error=f'Member or prospect not found: {member_id}')

        member_data = dict(member)
        member_data['is_prospect'] = is_prospect

        if is_prospect:
            member_data['name'] = member_data.get('full_name') or f"{member_data.get('first_name', '')} {member_data.get('last_name', '')}".strip() or 'Unknown'

        for key, value in member_data.items():
            if isinstance(value, (dt.datetime, dt.date)):
                member_data[key] = value.isoformat()

        member_guid = member_data.get('guid') or member_data.get('prospect_id') or member_id
        category_result = current_app.db_manager.execute_query(
            "SELECT category FROM member_categories WHERE member_id = ?",
            (str(member_guid),),
            fetch_one=True
        )

        if category_result:
            member_data['category'] = category_result['category'] if category_result['category'] else 'Unknown'
        else:
            member_data['category'] = 'Prospect' if is_prospect else 'Unknown'

        if is_prospect:
            return render_template('prospect_profile.html', member=member_data, prospect=member_data)

        return render_template(
            'member_profile.html',
            member=member_data,
            member_id=member_id,
            payment_status=None,
            agreements=[],
            payments=[],
            training_packages=[],
            membership_summary={},
            payment_plan=None,
            invoices=[]
        )
        
    except Exception as e:
        logger.error(f"❌ Error loading member profile {member_id}: {e}")
        logger.error(f"❌ Exception type: {type(e).__name__}")
        logger.error(f"❌ Full error details: {str(e)}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        return render_template('error.html', error=str(e))

@members_bp.route('/api/collections/past-due')
# @require_auth  # Temporarily disabled for testing
def get_past_due_collections():
    """Get all past due members and training clients for collections management using database manager"""
    try:
        # Get past due members using database manager for cross-platform compatibility
        past_due_members_data = current_app.db_manager.execute_query("""
            SELECT
                full_name as name,
                first_name,
                last_name,
                email,
                mobile_phone as phone,
                phone as home_phone,
                address,
                city,
                state,
                zip_code,
                amount_past_due as past_due_amount,
                status,
                join_date,
                'member' as type,
                status_message,
                agreement_recurring_cost,
                agreement_id,
                agreement_guid,
                agreement_type,
                prospect_id,
                guid
            FROM members
            WHERE status_message LIKE '%Past Due 6-30 days%'
               OR status_message LIKE '%Past Due more than 30 days%'
            ORDER BY amount_past_due DESC
        """, fetch_all=True)

        # Convert SQLite Row objects to dictionaries for JSON serialization
        past_due_members = [dict(row) for row in past_due_members_data] if past_due_members_data else []
        
        if not past_due_members:
            past_due_members = []
        
        # Get past due training clients WITH address/contact data from members table
        # NOTE: Training clients use ClubOS member IDs which don't match ClubHub prospect_ids
        # We match by name since the IDs are from different systems
        past_due_training_data = current_app.db_manager.execute_query("""
            SELECT
                tc.member_name as name,
                COALESCE(m.first_name, tc.first_name) as first_name,
                COALESCE(m.last_name, tc.last_name) as last_name,
                COALESCE(m.email, tc.email) as email,
                COALESCE(m.mobile_phone, m.phone, tc.phone, tc.mobile_phone) as phone,
                m.phone as home_phone,
                COALESCE(m.address, tc.address) as address,
                COALESCE(m.city, tc.city) as city,
                COALESCE(m.state, tc.state) as state,
                COALESCE(m.zip_code, tc.zip_code) as zip_code,
                tc.total_past_due as past_due_amount,
                tc.payment_status as status,
                tc.last_updated,
                'training_client' as type,
                tc.package_details,
                tc.active_packages,
                COALESCE(m.prospect_id, tc.prospect_id) as prospect_id,
                tc.clubos_member_id,
                tc.agreement_id,
                m.guid
            FROM training_clients tc
            LEFT JOIN members m ON (
                LOWER(TRIM(tc.member_name)) = LOWER(TRIM(m.full_name))
                OR LOWER(TRIM(tc.member_name)) = LOWER(TRIM(m.first_name || ' ' || m.last_name))
            )
            WHERE tc.total_past_due > 0 OR tc.past_due_amount > 0
            ORDER BY COALESCE(tc.total_past_due, tc.past_due_amount) DESC
        """, fetch_all=True)

        # Convert SQLite Row objects to dictionaries for JSON serialization
        past_due_training = [dict(row) for row in past_due_training_data] if past_due_training_data else []
        
        if not past_due_training:
            past_due_training = []
        
        # Process training clients to extract agreement info
        processed_training = []
        for client in past_due_training:
            # Convert to dict if not already
            if not isinstance(client, dict):
                client_dict = dict(client)
            else:
                client_dict = client
            
            # Extract agreement info from package_details
            agreement_id = None
            agreement_type = None
            if client_dict.get('package_details'):
                try:
                    import json
                    details = json.loads(client_dict['package_details'])
                    if details and len(details) > 0:
                        agreement_id = details[0].get('agreement_id')
                        agreement_type = details[0].get('package_name', 'Training Package')
                except:
                    pass
            
            client_dict['agreement_id'] = agreement_id
            client_dict['agreement_type'] = agreement_type
            processed_training.append(client_dict)
        
        # Combine all past due data
        all_past_due = []
        
        # Add members - convert to dict if needed
        for member in past_due_members:
            if not isinstance(member, dict):
                member_dict = dict(member)
            else:
                member_dict = member
            
            # Ensure agreement_type has a default value
            if not member_dict.get('agreement_type'):
                member_dict['agreement_type'] = 'Membership'
            
            all_past_due.append(member_dict)
        
        # Add training clients
        all_past_due.extend(processed_training)
        
        # Get count of members already sent to collections using database manager
        collections_sent_data = current_app.db_manager.execute_query("""
            SELECT COUNT(*) as count, COALESCE(SUM(amount_past_due), 0) as total_amount
            FROM members
            WHERE status_message = 'Sent to Collections'
        """, fetch_one=True)
        
        if collections_sent_data:
            # Convert SQLite Row to dictionary for consistent access
            sent_data_dict = dict(collections_sent_data)
            sent_count = sent_data_dict.get('count', 0)
            sent_amount = sent_data_dict.get('total_amount', 0)
        else:
            sent_count = 0
            sent_amount = 0
        
        logger.info(f"✅ Collections data: {len(past_due_members)} active members, {len(processed_training)} training clients, {sent_count} already sent")
        
        return jsonify({
            'success': True,
            'past_due_data': all_past_due,
            'total_count': len(all_past_due),
            'already_sent_count': sent_count,
            'already_sent_amount': sent_amount
        })
        
    except Exception as e:
        logger.error(f"❌ Error getting past due collections data: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return jsonify({'success': False, 'error': str(e)})

@members_bp.route('/api/collections/send-email', methods=['POST'])
# @require_auth  # Temporarily disabled for testing
def send_collections_email():
    """Send selected past due accounts to collections email"""
    try:
        data = request.get_json()
        selected_accounts = data.get('selected_accounts', [])
        
        if not selected_accounts:
            return jsonify({'success': False, 'error': 'No accounts selected'})
        
        # Generate email content
        email_content = generate_collections_email(selected_accounts)
        
        # Send email (you'll need to implement this based on your email service)
        success = send_email_to_club(email_content)
        
        if success:
            return jsonify({'success': True, 'message': f'Collections email sent for {len(selected_accounts)} accounts'})
        else:
            return jsonify({'success': False, 'error': 'Failed to send email'})
            
    except Exception as e:
        logger.error(f"❌ Error sending collections email: {e}")
        return jsonify({'success': False, 'error': str(e)})

def generate_collections_email(selected_accounts):
    """Generate email content for collections list"""
    from datetime import datetime
    
    email_content = f"""
COLLECTIONS REFERRAL - {datetime.now().strftime('%Y-%m-%d')}

The following accounts have been selected for collections referral:

"""
    
    total_amount = 0
    for i, account in enumerate(selected_accounts, 1):
        name = account.get('name', 'Unknown')
        amount = account.get('past_due_amount', 0)
        email = account.get('email', 'No email')
        phone = account.get('phone', 'No phone')
        home_phone = account.get('home_phone', '')
        address = account.get('address', 'No address')
        city = account.get('city', '')
        state = account.get('state', '')
        zip_code = account.get('zip_code', '')
        account_type = account.get('type', 'Unknown')
        agreement_id = account.get('agreement_id', 'N/A')
        agreement_type = account.get('agreement_type', 'N/A')
        prospect_id = account.get('prospect_id', 'N/A')
        guid = account.get('guid', 'N/A')
        
        # Format full address (handle None values)
        full_address = address or 'No address'
        if city or state or zip_code:
            if address:  # Only add comma if we have a base address
                full_address += f", {city}" if city else ""
                full_address += f", {state}" if state else ""
                full_address += f" {zip_code}" if zip_code else ""
            else:
                # Build address from just city/state/zip
                parts = [p for p in [city, state, zip_code] if p]
                full_address = ', '.join(parts) if parts else 'No address'

        # Format phone numbers (handle None values)
        phone_display = phone or 'No phone'
        if home_phone and home_phone != phone and home_phone != 'No phone':
            phone_display += f" / {home_phone}"
        
        total_amount += amount
        
        email_content += f"""
{i}. {name}
   Amount Past Due: ${amount:.2f}
   Type: {account_type.title()}
   Agreement ID: {agreement_id}
   Agreement Type: {agreement_type}
   
   CONTACT INFORMATION:
   Email: {email}
   Phone: {phone_display}
   Address: {full_address}
   
   ACCOUNT IDENTIFIERS:
   Prospect ID: {prospect_id}
   GUID: {guid}
   ---
"""
    
    email_content += f"""

TOTAL AMOUNT: ${total_amount:.2f}
TOTAL ACCOUNTS: {len(selected_accounts)}

Please process these accounts for collections referral.

Generated by Gym Bot Collections Manager
"""
    
    return email_content

def send_email_to_club(email_content):
    """Send email to club collections email using Gmail API with robust token refresh"""
    try:
        from datetime import datetime
        import base64
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        sender_email = "fdl.gym.bot@gmail.com"
        recipient_email = "FondDuLacWI@anytimefitness.com"
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = f"Collections Referral - {datetime.now().strftime('%Y-%m-%d')}"
        
        # Add body to email
        msg.attach(MIMEText(email_content, 'plain'))
        
        # Send email using Gmail API with OAuth2
        try:
            from googleapiclient.discovery import build
            from google.oauth2.credentials import Credentials
            from google.auth.transport.requests import Request
            from google_auth_oauthlib.flow import InstalledAppFlow
            import json
            import os
            
            # Gmail API scopes
            SCOPES = ['https://www.googleapis.com/auth/gmail.send']
            
            # Get credentials from your existing Google Cloud app
            creds = None
            token_file = 'gmail_token.json'
            
            # Load existing token if available
            if os.path.exists(token_file):
                logger.info("🔐 Loading existing Gmail token...")
                creds = Credentials.from_authorized_user_file(token_file, SCOPES)
                logger.info(f"📅 Token expiry: {creds.expiry}")
            
            # If no valid credentials, get new ones or refresh
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    logger.info("🔄 Refreshing expired Gmail token...")
                    try:
                        creds.refresh(Request())
                        logger.info("✅ Gmail token refreshed successfully!")
                        
                        # Save refreshed credentials
                        with open(token_file, 'w') as token:
                            token.write(creds.to_json())
                            logger.info("💾 Saved refreshed token")
                            
                    except Exception as refresh_error:
                        logger.error(f"❌ Token refresh failed: {refresh_error}")
                        logger.info("🔄 Will try to get new authorization...")
                        creds = None
                
                if not creds or not creds.valid:
                    logger.info("🔐 Getting new Gmail authorization...")
                    # Use your existing Google Cloud app credentials
                    credentials_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'google_oauth_credentials.json')
                    if not os.path.exists(credentials_path):
                        logger.error("❌ google_oauth_credentials.json not found")
                        logger.error("Path checked: " + credentials_path)
                        logger.error("Download OAuth2 credentials from Google Cloud Console")
                        return False
                    
                    flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
                    # Use console flow instead of local server for better compatibility
                    creds = flow.run_console()
                    
                    # Save credentials for next time
                    with open(token_file, 'w') as token:
                        token.write(creds.to_json())
                        logger.info("💾 Saved new Gmail token")
            
            # Create Gmail API service
            logger.info("📧 Creating Gmail API service...")
            service = build('gmail', 'v1', credentials=creds)
            
            # Encode message
            raw_message = base64.urlsafe_b64encode(msg.as_bytes()).decode()
            
            # Send email
            logger.info(f"📤 Sending email to {recipient_email}...")
            service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            logger.info(f"✅ Collections email sent successfully to {recipient_email}")
            return True
            
        except FileNotFoundError:
            logger.error("❌ credentials.json not found")
            logger.error("Download OAuth2 credentials from Google Cloud Console")
            logger.error("Place credentials.json in the project root")
            return False
        except Exception as e:
            logger.error(f"❌ Error sending email via Gmail API: {e}")
            return False
            
    except ImportError:
        logger.error("❌ Required email modules not available")
        return False
    except Exception as e:
        logger.error(f"❌ Error in send_email_to_club: {e}")
        return False

@members_bp.route('/invoices')
@require_auth
def invoices_page():
    """Invoices management page"""
    try:
        return render_template('invoices.html')
    except Exception as e:
        logger.error(f"❌ Error rendering invoices page: {e}")
        return f"Error loading invoices page: {str(e)}", 500

@members_bp.route('/api/prospects/all')
def get_all_prospects():
    """Get all prospects from database for messaging page - FIXED: Filter out duplicates"""
    try:
        # CRITICAL FIX: Filter out 57,372 rows with NULL prospect_ids
        # Use DISTINCT on prospect_id to get only unique prospects
        query = """
            SELECT
                prospect_id,
                id,
                first_name,
                last_name,
                full_name,
                email,
                phone as mobile_phone,
                status
            FROM prospects
            WHERE prospect_id IS NOT NULL
            GROUP BY prospect_id
            ORDER BY full_name
        """
        
        result = current_app.db_manager.execute_query(query, fetch_all=True)
        prospects = [dict(row) for row in result] if result else []
        
        logger.info(f"✅ Retrieved {len(prospects)} unique prospects from database (filtered out NULL prospect_ids)")
        logger.info(f"📊 Sample prospect: {prospects[0] if prospects else 'No prospects'}")
        return jsonify({'success': True, 'prospects': prospects})
        
    except Exception as e:
        logger.error(f"❌ Error getting prospects: {e}")
        import traceback
        logger.error(f"🔍 Traceback: {traceback.format_exc()}")
        return jsonify({'success': False, 'error': str(e)}), 500

@members_bp.route('/api/training/clients')
def get_all_training_clients():
    """Get all training clients from database for messaging page - FIXED: use payment_status"""
    try:
        query = """
            SELECT
                clubos_member_id,
                member_name as full_name,
                email,
                phone as mobile_phone,
                payment_status,
                total_past_due as past_due_amount,
                payment_status as status_message
            FROM training_clients
            ORDER BY member_name
        """
        
        result = current_app.db_manager.execute_query(query, fetch_all=True)
        training_clients = [dict(row) for row in result] if result else []
        
        logger.info(f"✅ Retrieved {len(training_clients)} training clients from database")
        logger.info(f"📊 Sample training client: {training_clients[0] if training_clients else 'No training clients'}")
        
        # Log past due count
        past_due_count = len([tc for tc in training_clients if tc.get('past_due_amount', 0) > 0])
        logger.info(f"💰 Training clients with past due: {past_due_count}")
        
        return jsonify({'success': True, 'training_clients': training_clients})
        
    except Exception as e:
        logger.error(f"❌ Error getting training clients: {e}")
        import traceback
        logger.error(f"🔍 Traceback: {traceback.format_exc()}")
        return jsonify({'success': False, 'error': str(e)}), 500
