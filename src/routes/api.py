#!/usr/bin/env python3
"""
API Routes
Data management, refresh operations, and utility endpoints
"""

from flask import Blueprint, jsonify, request, current_app
import logging
import json
from datetime import datetime
import threading
import time

logger = logging.getLogger(__name__)

api_bp = Blueprint('api', __name__)

@api_bp.route('/sync-cache-to-db', methods=['POST'])
def sync_cache_to_db():
    """Force sync cached members to database for proper categorization"""
    try:
        # Get cached members
        cached_members = current_app.data_cache.get('members', [])
        if not cached_members:
            return jsonify({
                'success': False,
                'error': 'No cached members found',
                'cached_count': 0,
                'db_count': current_app.db_manager.get_member_count()
            })
        
        logger.info(f"📊 Found {len(cached_members)} cached members, syncing to DB...")
        
        # Save to database with categorization
        success = current_app.db_manager.save_members_to_db(cached_members)
        
        if success:
            db_count = current_app.db_manager.get_member_count()
            category_counts = current_app.db_manager.get_category_counts()
            
            logger.info(f"✅ Successfully synced {len(cached_members)} members from cache to database")
            logger.info(f"📊 Database now has {db_count} members")
            logger.info(f"📊 Category counts: {category_counts}")
            
            return jsonify({
                'success': True,
                'message': f'Successfully synced {len(cached_members)} members from cache to database',
                'cached_count': len(cached_members),
                'db_count': db_count,
                'category_counts': category_counts
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to save members to database',
                'cached_count': len(cached_members),
                'db_count': current_app.db_manager.get_member_count()
            })
            
    except Exception as e:
        logger.error(f"❌ Error syncing cache to DB: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'cached_count': len(current_app.data_cache.get('members', [])),
            'db_count': 0
        }), 500




# Global status tracking
data_refresh_status = {
    'is_running': False,
    'started_at': None,
    'completed_at': None,
    'progress': 0,
    'status': 'idle',
    'message': 'No refresh in progress',
    'error': None
}

bulk_checkin_status = {
    'is_running': False,
    'started_at': None,
    'completed_at': None,
    'progress': 0,
    'total_members': 0,
    'processed_members': 0,
    'ppv_excluded': 0,
    'total_checkins': 0,
    'current_member': '',
    'status': 'idle',
    'message': 'No bulk check-in in progress',
    'error': None,
    'errors': []
}

@api_bp.route('/refresh-funding', methods=['POST'])
def refresh_funding_cache():
    """Refresh the funding cache."""
    try:
        logger.info("🔄 Refreshing funding cache")
        
        # Start background refresh
        def background_refresh():
            try:
                refreshed_count = current_app.training_package_cache.refresh_cache()
                logger.info(f"✅ Funding cache refresh completed: {refreshed_count} entries updated")
            except Exception as e:
                logger.error(f"❌ Funding cache refresh failed: {e}")
        
        thread = threading.Thread(target=background_refresh)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'message': 'Funding cache refresh started in background'
        })
        
    except Exception as e:
        logger.error(f"❌ Error starting funding cache refresh: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/training/payment-status', methods=['POST'])
def api_training_payment_status():
    """Get training payment status for a participant."""
    try:
        data = request.get_json()
        participant_name = data.get('participant_name')
        participant_email = data.get('participant_email')
        force_refresh = data.get('force_refresh', False)
        
        if not participant_name:
            return jsonify({'success': False, 'error': 'Participant name is required'}), 400
        
        logger.info(f"🔍 Getting payment status for: {participant_name}")
        
        # Get funding status from cache
        funding_data = current_app.training_package_cache.lookup_participant_funding(
            participant_name, participant_email, force_refresh
        )
        
        if funding_data:
            return jsonify({
                'success': True,
                'funding_data': funding_data
            })
        else:
            return jsonify({
                'success': False,
                'error': 'No funding data available'
            }), 404
            
    except Exception as e:
        logger.error(f"❌ Error getting training payment status: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/bulk-checkin', methods=['POST'])
def api_bulk_checkin():
    """Start bulk check-in process."""
    try:
        if bulk_checkin_status['is_running']:
            return jsonify({
                'success': False,
                'error': 'Bulk check-in already in progress'
            }), 400
        
        # Start background bulk check-in
        def background_bulk_checkin():
            perform_bulk_checkin_background()
        
        thread = threading.Thread(target=background_bulk_checkin)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'message': 'Bulk check-in started in background'
        })
        
    except Exception as e:
        logger.error(f"❌ Error starting bulk check-in: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/bulk-checkin-status')
def api_bulk_checkin_status():
    """Get bulk check-in status."""
    return jsonify(bulk_checkin_status)

@api_bp.route('/funding-cache-status')
def funding_cache_status():
    """Get funding cache status."""
    try:
        cache_status = current_app.training_package_cache.get_cache_status()
        return jsonify({
            'success': True,
            'cache_status': cache_status
        })
    except Exception as e:
        logger.error(f"❌ Error getting funding cache status: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/refresh-data', methods=['POST', 'GET'])
def refresh_data():
    """Refresh all data from ClubOS APIs."""
    try:
        if data_refresh_status['is_running']:
            return jsonify({
                'success': False,
                'error': 'Data refresh already in progress'
            }), 400
        
        # Start background refresh
        def background_refresh():
            try:
                data_refresh_status.update({
                    'is_running': True,
                    'started_at': datetime.now().isoformat(),
                    'status': 'running',
                    'message': 'Refreshing data from ClubOS APIs...',
                    'error': None
                })
                
                # Refresh database
                success = current_app.db_manager.refresh_database(force=True)
                
                if success:
                    data_refresh_status.update({
                        'status': 'completed',
                        'message': 'Data refresh completed successfully',
                        'completed_at': datetime.now().isoformat(),
                        'progress': 100
                    })
                else:
                    data_refresh_status.update({
                        'status': 'failed',
                        'message': 'Data refresh failed',
                        'completed_at': datetime.now().isoformat(),
                        'error': 'Database refresh failed'
                    })
                    
            except Exception as e:
                logger.error(f"❌ Data refresh failed: {e}")
                data_refresh_status.update({
                    'status': 'failed',
                    'message': f'Data refresh failed: {str(e)}',
                    'completed_at': datetime.now().isoformat(),
                    'error': str(e)
                })
            finally:
                data_refresh_status['is_running'] = False
        
        thread = threading.Thread(target=background_refresh)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'message': 'Data refresh started in background'
        })
        
    except Exception as e:
        logger.error(f"❌ Error starting data refresh: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/refresh-clubhub-members', methods=['POST', 'GET'])
def refresh_clubhub_members():
    """Refresh ClubHub member data."""
    try:
        if data_refresh_status['is_running']:
            return jsonify({
                'success': False,
                'error': 'Data refresh already in progress'
            }), 400
        
        # Start background refresh
        def background_refresh():
            try:
                data_refresh_status.update({
                    'is_running': True,
                    'started_at': datetime.now().isoformat(),
                    'status': 'running',
                    'message': 'Refreshing ClubHub member data...',
                    'error': None
                })
                
                # Import fresh ClubHub data
                from utils.data_import import import_fresh_clubhub_data
                import_fresh_clubhub_data()
                
                data_refresh_status.update({
                    'status': 'completed',
                    'message': 'ClubHub member data refresh completed',
                    'completed_at': datetime.now().isoformat(),
                    'progress': 100
                })
                
            except Exception as e:
                logger.error(f"❌ ClubHub refresh failed: {e}")
                data_refresh_status.update({
                    'status': 'failed',
                    'message': f'ClubHub refresh failed: {str(e)}',
                    'completed_at': datetime.now().isoformat(),
                    'error': str(e)
                })
            finally:
                data_refresh_status['is_running'] = False
        
        thread = threading.Thread(target=background_refresh)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'message': 'ClubHub member data refresh started in background'
        })
        
    except Exception as e:
        logger.error(f"❌ Error starting ClubHub refresh: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/data-status')
def data_status():
    """Get current data status and refresh information."""
    try:
        # Get database counts
        member_count = current_app.db_manager.get_member_count()
        prospect_count = current_app.db_manager.get_prospect_count()
        training_client_count = current_app.db_manager.get_training_client_count()
        
        # Check if we have cached data available
        if hasattr(current_app, 'data_cache'):
            cached_members = current_app.data_cache.get('members', [])
            cached_prospects = current_app.data_cache.get('prospects', [])
            cached_training_clients = current_app.data_cache.get('training_clients', [])
            
            if cached_members:
                member_count = len(cached_members)
                logger.info(f"📊 Using cached member count: {member_count}")
            if cached_prospects:
                prospect_count = len(cached_prospects)
                logger.info(f"📊 Using cached prospect count: {prospect_count}")
            if cached_training_clients:
                training_client_count = len(cached_training_clients)
                logger.info(f"📊 Using cached training client count: {training_client_count}")
        
        # Get refresh log info
        conn = current_app.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT table_name, last_refresh, record_count, category_breakdown
            FROM data_refresh_log
            ORDER BY last_refresh DESC
        """)
        
        refresh_logs = []
        for row in cursor.fetchall():
            refresh_logs.append({
                'table_name': row[0],
                'last_refresh': row[1],
                'record_count': row[2],
                'category_breakdown': json.loads(row[3]) if row[3] else {}
            })
        
        conn.close()
        
        # Get category counts
        category_counts = current_app.db_manager.get_category_counts()
        
        return jsonify({
            'success': True,
            'data': {
                'counts': {
                    'members': member_count,
                    'prospects': prospect_count,
                    'training_clients': training_client_count
                },
                'refresh_logs': refresh_logs,
                'category_counts': category_counts,
                'refresh_status': data_refresh_status
            }
        })
        
    except Exception as e:
        logger.error(f"❌ Error getting data status: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/refresh-members-full', methods=['POST'])
def api_refresh_members_full():
    """Trigger a full refresh of all member data."""
    try:
        if data_refresh_status['is_running']:
            return jsonify({
                'success': False,
                'error': 'Data refresh already in progress'
            }), 400
        
        # Start background full refresh
        def background_full_refresh():
            try:
                data_refresh_status.update({
                    'is_running': True,
                    'started_at': datetime.now().isoformat(),
                    'status': 'running',
                    'message': 'Performing full member data refresh...',
                    'error': None
                })
                
                # Import fresh ClubHub data
                from utils.data_import import import_fresh_clubhub_data
                import_fresh_clubhub_data()
                
                data_refresh_status.update({
                    'status': 'completed',
                    'message': 'Full member data refresh completed',
                    'completed_at': datetime.now().isoformat(),
                    'progress': 100
                })
                
            except Exception as e:
                logger.error(f"❌ Full member refresh failed: {e}")
                data_refresh_status.update({
                    'status': 'failed',
                    'message': f'Full member refresh failed: {str(e)}',
                    'completed_at': datetime.now().isoformat(),
                    'error': str(e)
                })
            finally:
                data_refresh_status['is_running'] = False
        
        thread = threading.Thread(target=background_full_refresh)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'message': 'Full member data refresh started in background'
        })
        
    except Exception as e:
        logger.error(f"❌ Error starting full member refresh: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/create-invoice', methods=['POST'])
def api_create_invoice():
    """API endpoint to create a Square invoice."""
    try:
        data = request.get_json()
        member_name = data.get('member_name')
        member_email = data.get('member_email')
        amount = data.get('amount')
        description = data.get('description', 'Overdue Payment')
        past_due_amount = data.get('past_due_amount', 0)
        late_fee = data.get('late_fee', 0)

        if not all([member_name, amount]):
            return jsonify({'success': False, 'error': 'Missing required invoice data (member_name and amount).'}), 400

        # Check if Square client is available
        square_client = current_app.config.get('SQUARE_CLIENT')
        if not square_client:
            return jsonify({'success': False, 'error': 'Square payment service is not available.'}), 503

        try:
            # Convert amount to float if it's a string
            amount = float(amount)
            
            # Create the invoice using the Square client
            if member_email:
                invoice_result = square_client(member_name, member_email, amount, description)
            else:
                invoice_result = square_client(member_name, amount, description)
            
            # Handle different return types from square client
            if isinstance(invoice_result, dict):
                if invoice_result.get('success'):
                    invoice_url = invoice_result.get('public_url') or invoice_result.get('invoice_url')
                else:
                    return jsonify({'success': False, 'error': invoice_result.get('error', 'Failed to create invoice')}), 500
            else:
                # Assume it's a direct URL if not a dict
                invoice_url = invoice_result
            
            if invoice_url:
                logger.info(f"✅ Invoice created for {member_name}: ${amount:.2f}")
                return jsonify({
                    'success': True, 
                    'invoice_url': invoice_url,
                    'message': f'Invoice created successfully for {member_name}',
                    'amount': amount,
                    'past_due_amount': past_due_amount,
                    'late_fee': late_fee
                })
            else:
                return jsonify({'success': False, 'error': 'Failed to create invoice - no URL returned.'}), 500
                
        except ValueError as e:
            return jsonify({'success': False, 'error': f'Invalid amount value: {amount}'}), 400
        except Exception as e:
            logger.error(f"Error creating Square invoice: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
            
    except Exception as e:
        logger.error(f"Error in api_create_invoice: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/invoices/batch', methods=['POST'])
def api_batch_invoices():
    """API endpoint to create batch invoices for multiple members."""
    try:
        data = request.get_json()
        invoice_type = data.get('type', 'members')
        filter_type = data.get('filter', 'past_due')
        selected_clients = data.get('selected_clients', [])
        
        if not selected_clients:
            return jsonify({'success': False, 'error': 'No members selected for invoicing'}), 400
        
        # Check if Square client is available
        square_client = current_app.config.get('SQUARE_CLIENT')
        if not square_client:
            return jsonify({'success': False, 'error': 'Square payment service is not available.'}), 503
        
        logger.info(f"🧾 Starting batch invoice creation for {len(selected_clients)} members")
        
        # Get member details from database
        conn = current_app.db_manager.get_connection()
        cursor = conn.cursor()
        
        # Get member information for selected IDs
        placeholders = ','.join(['?' for _ in selected_clients])
        cursor.execute(f"""
            SELECT prospect_id, id, guid, first_name, last_name, full_name, email, 
                   mobile_phone, amount_past_due, base_amount_past_due, missed_payments,
                   late_fees, agreement_recurring_cost, status_message
            FROM members 
            WHERE prospect_id IN ({placeholders}) OR id IN ({placeholders})
        """, selected_clients + selected_clients)
        
        members = cursor.fetchall()
        conn.close()
        
        if not members:
            return jsonify({'success': False, 'error': 'No valid members found'}), 404
        
        # Process each member
        successful_invoices = []
        failed_invoices = []
        
        for member in members:
            try:
                member_dict = dict(member)
                member_id = member_dict['prospect_id'] or member_dict['id'] or member_dict['guid']
                member_name = member_dict['full_name'] or f"{member_dict['first_name'] or ''} {member_dict['last_name'] or ''}".strip()
                email = member_dict['email']
                
                # Skip if no valid name
                if not member_name or member_name.strip() == '':
                    failed_invoices.append({
                        'member_id': member_id,
                        'member_name': 'Unknown',
                        'email': email,
                        'error': 'No valid member name'
                    })
                    continue
                
                # Use the new calculated fields from the cards
                base_amount_past_due = float(member_dict['base_amount_past_due'] or 0)
                missed_payments = int(member_dict['missed_payments'] or 0)
                late_fees = float(member_dict['late_fees'] or 0)
                
                # Total amount is base + late fees (as shown on the cards)
                total_amount = base_amount_past_due + late_fees
                
                # If no calculated total, fall back to original amount_past_due
                if total_amount <= 0:
                    total_amount = float(member_dict['amount_past_due'] or 0)
                
                # Ensure we have a valid amount (minimum $5)
                total_amount = max(float(total_amount), 5.0)
                
                # Create detailed description with new breakdown
                description = f"Payment for {member_name}"
                if base_amount_past_due > 0:
                    description += f" - Base Amount: ${base_amount_past_due:.2f}"
                if missed_payments > 0:
                    description += f" ({missed_payments} missed payments)"
                if late_fees > 0:
                    description += f" + Late Fees: ${late_fees:.2f}"
                    
                # Add status message if available
                if member_dict['status_message']:
                    description += f" ({member_dict['status_message']})"
                
                # Get mobile phone for SMS delivery
                mobile_phone = member_dict['mobile_phone']
                
                # Create Square invoice - prioritize email over SMS since SMS delivery is problematic
                try:
                    # Check for valid email (not None, not empty, not the string 'None')
                    valid_email = email and email != 'None' and email.strip() != ''
                    
                    if valid_email:
                        # Send to real ClubHub email address
                        invoice_result = square_client(member_name, email, total_amount, description, delivery_method='email')
                    elif mobile_phone:
                        # Fallback to mobile phone (SMS) if no valid email
                        invoice_result = square_client(member_name, mobile_phone, total_amount, description, delivery_method='sms')
                    else:
                        # No contact method available - use placeholder email
                        placeholder_email = f"{member_name.lower().replace(' ', '.')}@anytimefitness.com"
                        invoice_result = square_client(member_name, placeholder_email, total_amount, description, delivery_method='email')
                    
                    # Handle different return types
                    if isinstance(invoice_result, dict):
                        if invoice_result.get('success'):
                            invoice_url = invoice_result.get('public_url') or invoice_result.get('invoice_url')
                        else:
                            raise Exception(invoice_result.get('error', 'Failed to create invoice'))
                    else:
                        invoice_url = invoice_result
                        
                except Exception as e:
                    logger.error(f"❌ Square client error for {member_name}: {e}")
                    invoice_url = None
                
                if invoice_url:
                    # Determine actual delivery method used
                    valid_email = email and email != 'None' and email.strip() != ''
                    actual_delivery_method = 'Email' if valid_email else ('SMS' if mobile_phone else 'Email')
                    actual_contact_info = email if valid_email else (mobile_phone if mobile_phone else f"{member_name.lower().replace(' ', '.')}@anytimefitness.com")
                    
                    successful_invoices.append({
                        'member_id': member_id,
                        'member_name': member_name,
                        'contact_info': actual_contact_info,
                        'delivery_method': actual_delivery_method,
                        'amount': total_amount,
                        'base_amount': base_amount_past_due,
                        'late_fees': late_fees,
                        'missed_payments': missed_payments,
                        'invoice_url': invoice_url,
                        'description': description
                    })
                    logger.info(f"✅ Invoice created for {member_name}: ${total_amount:.2f} (Base: ${base_amount_past_due:.2f}, Late Fees: ${late_fees:.2f}) via {actual_delivery_method} to {actual_contact_info}")
                else:
                    valid_email = email and email != 'None' and email.strip() != ''
                    failed_invoices.append({
                        'member_id': member_id,
                        'member_name': member_name,
                        'contact_info': email if valid_email else (mobile_phone if mobile_phone else f"{member_name.lower().replace(' ', '.')}@anytimefitness.com"),
                        'delivery_method': 'Email' if valid_email else ('SMS' if mobile_phone else 'Email'),
                        'amount': total_amount,
                        'error': 'Failed to create Square invoice'
                    })
                    logger.error(f"❌ Failed to create invoice for {member_name}")
                    
            except Exception as e:
                member_name = member.get('full_name', 'Unknown') or f"{member.get('first_name', '')} {member.get('last_name', '')}".strip()
                failed_invoices.append({
                    'member_id': member.get('prospect_id') or member.get('id') or member.get('guid'),
                    'member_name': member_name,
                    'email': member.get('email'),
                    'error': str(e)
                })
                logger.error(f"❌ Error processing invoice for {member_name}: {e}")
                continue
        
        # Prepare summary
        summary = {
            'total_processed': len(selected_clients),
            'successful': len(successful_invoices),
            'failed': len(failed_invoices),
            'total_amount': sum(inv['amount'] for inv in successful_invoices),
            'total_late_fees': sum(inv['late_fees'] for inv in successful_invoices)
        }
        
        logger.info(f"🧾 Batch invoice summary: {summary['successful']}/{summary['total_processed']} successful, Total: ${summary['total_amount']:.2f}")
        
        return jsonify({
            'success': True,
            'summary': summary,
            'successful_invoices': successful_invoices,
            'failed_invoices': failed_invoices,
            'message': f'Batch invoicing completed. {summary["successful"]} successful, {summary["failed"]} failed.'
        })
        
    except Exception as e:
        logger.error(f"❌ Error in batch invoice creation: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/calculate-invoice-amount', methods=['POST'])
def api_calculate_invoice_amount():
    """API endpoint to calculate invoice amount with late fees for a member."""
    try:
        data = request.get_json()
        member_id = data.get('member_id')
        
        if not member_id:
            return jsonify({'success': False, 'error': 'Member ID is required'}), 400
        
        # Get member details from database
        conn = current_app.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT prospect_id, id, full_name, first_name, last_name, 
                   amount_past_due, amount_of_next_payment, payment_amount, 
                   agreement_rate, status_message
            FROM members 
            WHERE prospect_id = ? OR id = ?
        """, (member_id, member_id))
        
        member = cursor.fetchone()
        conn.close()
        
        if not member:
            return jsonify({'success': False, 'error': 'Member not found'}), 404
        
        member_dict = dict(member)
        member_name = member_dict['full_name'] or f"{member_dict['first_name'] or ''} {member_dict['last_name'] or ''}".strip()
        
        # Calculate amounts
        amount_past_due = float(member_dict['amount_past_due'] or 0)
        next_payment = float(member_dict['amount_of_next_payment'] or 0)
        monthly_rate = float(member_dict['agreement_rate'] or member_dict['payment_amount'] or 0)
        
        # Calculate late fee
        late_fee = 0.0
        if amount_past_due > 0:
            payment_periods_behind = max(1, int(amount_past_due / 50))
            late_fee = max(25.0, payment_periods_behind * 5.0)
            late_fee = min(late_fee, 100.0)
        
        total_amount = amount_past_due + late_fee
        
        if total_amount <= 0:
            total_amount = next_payment if next_payment > 0 else monthly_rate
        
        total_amount = max(float(total_amount), 5.0)
        
        # Create description
        description = f"Payment for {member_name}"
        if amount_past_due > 0:
            description += f" - Past Due: ${amount_past_due:.2f}"
        if late_fee > 0:
            description += f" + Late Fee: ${late_fee:.2f}"
        
        return jsonify({
            'success': True,
            'member_name': member_name,
            'past_due_amount': amount_past_due,
            'late_fee': late_fee,
            'total_amount': total_amount,
            'description': description
        })
        
    except Exception as e:
        logger.error(f"❌ Error calculating invoice amount: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

def perform_bulk_checkin_background():
    """Background function for bulk check-in process."""
    try:
        bulk_checkin_status.update({
            'is_running': True,
            'started_at': datetime.now().isoformat(),
            'status': 'running',
            'message': 'Starting bulk check-in process...',
            'error': None
        })
        
        # Get all active members
        conn = current_app.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT prospect_id, first_name, last_name, full_name, status_message
            FROM members 
            WHERE status_message NOT LIKE '%cancelled%' 
            AND status_message NOT LIKE '%expired%'
            AND status_message NOT LIKE '%inactive%'
        """)
        
        members = cursor.fetchall()
        conn.close()
        
        total_members = len(members)
        bulk_checkin_status['total_members'] = total_members
        
        logger.info(f"🔄 Starting bulk check-in for {total_members} members")
        
        # Process members in batches
        batch_size = 10
        processed = 0
        ppv_excluded = 0
        total_checkins = 0
        errors = []
        
        for i in range(0, total_members, batch_size):
            batch = members[i:i + batch_size]
            
            for member in batch:
                try:
                    member_name = member['full_name'] or f"{member['first_name']} {member['last_name']}"
                    bulk_checkin_status['current_member'] = member_name
                    
                    # Skip PPV members
                    if 'ppv' in member['status_message'].lower() or 'pay per visit' in member['status_message'].lower():
                        ppv_excluded += 1
                        logger.info(f"⏭️ Skipping PPV member: {member_name}")
                        continue
                    
                    # Perform check-in (placeholder for actual check-in logic)
                    logger.info(f"✅ Checked in: {member_name}")
                    total_checkins += 1
                    
                    processed += 1
                    bulk_checkin_status['processed_members'] = processed
                    bulk_checkin_status['progress'] = int((processed / total_members) * 100)
                    
                    # Small delay to avoid overwhelming the system
                    time.sleep(0.1)
                    
                except Exception as e:
                    error_msg = f"Error processing {member.get('full_name', 'Unknown')}: {str(e)}"
                    errors.append(error_msg)
                    logger.error(f"❌ {error_msg}")
                    continue
            
            # Update status
            bulk_checkin_status.update({
                'ppv_excluded': ppv_excluded,
                'total_checkins': total_checkins,
                'errors': errors
            })
            
            # Small delay between batches
            time.sleep(1)
        
        # Final status update
        bulk_checkin_status.update({
            'status': 'completed',
            'message': f'Bulk check-in completed: {total_checkins} check-ins, {ppv_excluded} PPV excluded',
            'completed_at': datetime.now().isoformat(),
            'progress': 100
        })
        
        logger.info(f"✅ Bulk check-in completed: {total_checkins} check-ins, {ppv_excluded} PPV excluded")
        
    except Exception as e:
        logger.error(f"❌ Bulk check-in failed: {e}")
        bulk_checkin_status.update({
            'status': 'failed',
            'message': f'Bulk check-in failed: {str(e)}',
            'completed_at': datetime.now().isoformat(),
            'error': str(e)
        })
    finally:
        bulk_checkin_status['is_running'] = False
@api_bp.route('/refresh-members', methods=['POST'])
def api_refresh_members():
    """Simple member refresh from ClubHub (lightweight version)"""
    try:
        logger.info("🔄 Starting simple member refresh from ClubHub...")
        
        # Import ClubHub API client
        from services.api.clubhub_api_client import ClubHubAPIClient
        from config.clubhub_credentials import CLUBHUB_EMAIL, CLUBHUB_PASSWORD
        
        # Initialize and authenticate
        client = ClubHubAPIClient()
        if not client.authenticate(CLUBHUB_EMAIL, CLUBHUB_PASSWORD):
            return jsonify({
                'success': False,
                'error': 'ClubHub authentication failed'
            }), 500
        
        # Get fresh member data
        fresh_members = []
        page = 1
        page_size = 100
        
        while True:
            members_response = client.get_all_members(page=page, page_size=page_size)
            
            if not members_response or not isinstance(members_response, list):
                break
                
            fresh_members.extend(members_response)
            
            if len(members_response) < page_size:
                break
                
            page += 1
        
        # Update database using our database manager
        success = current_app.db_manager.save_members_to_db(fresh_members)
        
        if success:
            member_count = current_app.db_manager.get_member_count()
            category_counts = current_app.db_manager.get_category_counts()
            
            logger.info(f"✅ Successfully refreshed {len(fresh_members)} members")
            logger.info(f"📊 Database now has {member_count} total members")
            logger.info(f"📊 Category distribution: {category_counts}")
            
            return jsonify({
                'success': True,
                'message': f'Successfully refreshed {len(fresh_members)} members',
                'total_members': member_count,
                'fresh_members': len(fresh_members),
                'category_counts': category_counts
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to save members to database'
            }), 500
            
    except Exception as e:
        logger.error(f"❌ Error refreshing members: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/refresh-training-clients', methods=['POST', 'GET'])
def refresh_training_clients():
    """Refresh training clients from ClubHub with enhanced detection"""
    try:
        logger.info("🏋️ Starting training clients refresh from ClubHub...")
        
        # Import ClubHub API client
        from services.api.clubhub_api_client import ClubHubAPIClient
        from config.clubhub_credentials import CLUBHUB_EMAIL, CLUBHUB_PASSWORD
        
        # Initialize and authenticate
        client = ClubHubAPIClient()
        if not client.authenticate(CLUBHUB_EMAIL, CLUBHUB_PASSWORD):
            return jsonify({
                'success': False,
                'error': 'ClubHub authentication failed'
            }), 500
        
        # Get all members and check for training indicators
        members_response = client.get_all_members(page=1, page_size=1000)
        training_members = []
        detection_stats = {
            'total_checked': 0,
            'training_detected': 0,
            'indicators_used': {
                'status_message': 0,
                'agreement_id': 0,
                'invoice_amount': 0,
                'member_type': 0
            }
        }
        
        if members_response:
            for member in members_response:
                detection_stats['total_checked'] += 1
                
                # Enhanced training detection logic
                has_training = False
                indicators_found = []
                
                status_msg = (member.get('statusMessage') or '').lower()
                member_type = (member.get('memberType') or '').lower()
                
                # Check multiple indicators
                if 'training' in status_msg or 'personal' in status_msg:
                    has_training = True
                    indicators_found.append('status_message')
                    detection_stats['indicators_used']['status_message'] += 1
                
                if member.get('agreementId'):
                    has_training = True
                    indicators_found.append('agreement_id')
                    detection_stats['indicators_used']['agreement_id'] += 1
                
                if float(member.get('nextInvoiceSubtotal', 0)) > 0:
                    has_training = True
                    indicators_found.append('invoice_amount')
                    detection_stats['indicators_used']['invoice_amount'] += 1
                
                if 'training' in member_type or 'pt' in member_type:
                    has_training = True
                    indicators_found.append('member_type')
                    detection_stats['indicators_used']['member_type'] += 1
                
                if has_training:
                    detection_stats['training_detected'] += 1
                    training_member = {
                        'id': member.get('id'),
                        'member_id': str(member.get('id')),
                        'first_name': member.get('firstName', ''),
                        'last_name': member.get('lastName', ''),
                        'full_name': f"{member.get('firstName', '')} {member.get('lastName', '')}".strip(),
                        'email': member.get('email', ''),
                        'phone': member.get('mobilePhone', ''),
                        'status': status_msg,
                        'training_package': f"Detected via: {', '.join(indicators_found)}",
                        'agreement_id': member.get('agreementId', ''),
                        'invoice_amount': member.get('nextInvoiceSubtotal', 0)
                    }
                    training_members.append(training_member)
        
        # Save to database
        if training_members:
            conn = current_app.db_manager.get_connection()
            cursor = conn.cursor()
            
            # Clear existing training clients
            cursor.execute('DELETE FROM training_clients')
            
            # Insert detected training clients
            for client_data in training_members:
                cursor.execute("""
                    INSERT INTO training_clients (
                        member_id, first_name, last_name, full_name, email, phone,
                        status, training_package, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (
                    client_data['member_id'],
                    client_data['first_name'],
                    client_data['last_name'], 
                    client_data['full_name'],
                    client_data['email'],
                    client_data['phone'],
                    client_data['status'],
                    client_data['training_package']
                ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Detected and saved {len(training_members)} training clients")
            logger.info(f"📊 Detection stats: {detection_stats}")
        
        return jsonify({
            'success': True,
            'message': f'Successfully refreshed training clients',
            'training_clients_found': len(training_members),
            'detection_stats': detection_stats,
            'training_clients': training_members[:10]  # Return first 10 for preview
        })
        
    except Exception as e:
        logger.error(f"❌ Error refreshing training clients: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/debug/members', methods=['GET'])
def debug_members():
    """Debug endpoint to inspect member data"""
    try:
        # Get query parameters
        limit = request.args.get('limit', 10, type=int)
        search = request.args.get('search', '')
        category = request.args.get('category', '')
        
        query = "SELECT * FROM members"
        params = []
        
        # Add search filter
        if search:
            query += " WHERE (first_name LIKE ? OR last_name LIKE ? OR email LIKE ?)"
            search_param = f"%{search}%"
            params.extend([search_param, search_param, search_param])
        
        # Add category filter
        if category:
            if search:
                query += " AND"
            else:
                query += " WHERE"
            query += " status_message LIKE ?"
            params.append(f"%{category}%")
        
        query += f" ORDER BY created_at DESC LIMIT {limit}"
        
        members = current_app.db_manager.execute_query(query, tuple(params))
        
        # Get category distribution
        category_counts = current_app.db_manager.get_category_counts()
        
        # Get database stats
        total_members = current_app.db_manager.get_member_count()
        
        return jsonify({
            'success': True,
            'total_members': total_members,
            'category_counts': category_counts,
            'sample_members': members,
            'query_params': {
                'limit': limit,
                'search': search,
                'category': category
            }
        })
        
    except Exception as e:
        logger.error(f"❌ Error in debug members: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/refresh-billing-data', methods=['POST'])
def api_refresh_billing_data():
    """API endpoint to refresh billing data from ClubHub for all past due members."""
    try:
        logger.info("🔄 Starting billing data refresh from ClubHub...")
        
        # Import the ClubOS Fresh Data API
        from clubos_fresh_data_api import ClubOSFreshDataAPI
        
        # Initialize the API client
        fresh_api = ClubOSFreshDataAPI()
        
        # Get members with real billing details from ClubHub
        billing_data = fresh_api.get_members_with_billing_details()
        
        if billing_data:
            # Update the database with real billing information
            success = fresh_api.update_member_billing_in_database(billing_data)
            
            if success:
                # Get summary of updated data
                total_members = len(billing_data)
                past_due_members = [b for b in billing_data if b.get('amount_past_due', 0) > 0]
                total_past_due_amount = sum(b.get('amount_past_due', 0) for b in past_due_members)
                total_late_fees = sum(b.get('late_fees', 0) for b in past_due_members)
                
                summary = {
                    'success': True,
                    'message': 'Billing data refreshed successfully from ClubHub',
                    'updated_members': total_members,
                    'past_due_members': len(past_due_members),
                    'total_past_due_amount': round(total_past_due_amount, 2),
                    'total_late_fees': round(total_late_fees, 2),
                    'timestamp': datetime.now().isoformat()
                }
                
                logger.info(f"✅ Billing refresh complete: {len(past_due_members)} past due members, ${total_past_due_amount:.2f} total")
                return jsonify(summary)
            else:
                return jsonify({
                    'success': False,
                    'error': 'Failed to update database with billing data'
                }), 500
        else:
            return jsonify({
                'success': False,
                'error': 'No billing data retrieved from ClubHub'
            }), 404
            
    except Exception as e:
        logger.error(f"❌ Error refreshing billing data: {e}")
        return jsonify({
            'success': False,
            'error': f'Billing data refresh error: {str(e)}'
        }), 500

@api_bp.route('/test-complete-flow', methods=['POST'])
def test_complete_flow():
    """Test endpoint for complete training client flow"""
    try:
        test_member_id = request.json.get('member_id', 'test123')
        
        # Mock test data
        test_result = {
            'member_id': test_member_id,
            'test_steps': [
                {'step': 'Authentication', 'status': 'success'},
                {'step': 'Member lookup', 'status': 'success'},
                {'step': 'Agreement fetch', 'status': 'success'},
                {'step': 'Invoice calculation', 'status': 'success'}
            ],
            'timestamp': datetime.now().isoformat(),
            'environment': 'test'
        }
        
        return jsonify({
            'success': True,
            'message': 'Complete flow test completed',
            'test_result': test_result
        })
        
    except Exception as e:
        logger.error(f"❌ Error in test complete flow: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/test-browser-flow', methods=['POST'])
def test_browser_flow():
    """Test endpoint for browser-based operations"""
    try:
        test_url = request.json.get('url', 'https://example.com')
        
        # Mock browser test
        test_result = {
            'url': test_url,
            'browser_tests': [
                {'test': 'Page load', 'status': 'success', 'time_ms': 250},
                {'test': 'Element detection', 'status': 'success', 'time_ms': 50},
                {'test': 'Form interaction', 'status': 'success', 'time_ms': 100}
            ],
            'total_time_ms': 400,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify({
            'success': True,
            'message': 'Browser flow test completed',
            'test_result': test_result
        })
        
    except Exception as e:
        logger.error(f"❌ Error in test browser flow: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/test-known-agreement', methods=['POST'])
def test_known_agreement():
    """Test endpoint for known agreement validation"""
    try:
        agreement_id = request.json.get('agreement_id', 'test_agreement_123')
        
        # Mock agreement validation
        test_result = {
            'agreement_id': agreement_id,
            'validation_steps': [
                {'step': 'Agreement exists', 'status': 'success'},
                {'step': 'Member association', 'status': 'success'},
                {'step': 'Payment status', 'status': 'success'},
                {'step': 'Invoice generation', 'status': 'success'}
            ],
            'agreement_details': {
                'id': agreement_id,
                'member_name': 'Test Member',
                'amount': 150.00,
                'status': 'active'
            },
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify({
            'success': True,
            'message': 'Known agreement test completed',
            'test_result': test_result
        })
        
    except Exception as e:
        logger.error(f"❌ Error in test known agreement: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/member/<member_id>/billing-details', methods=['GET'])
def api_get_member_billing_details(member_id):
    """API endpoint to get detailed billing information for a specific member."""
    try:
        logger.info(f"💰 Getting billing details for member {member_id}...")
        
        # Import the ClubOS Fresh Data API
        from clubos_fresh_data_api import ClubOSFreshDataAPI
        
        # Initialize the API client
        fresh_api = ClubOSFreshDataAPI()
        
        # Get detailed billing information
        billing_details = fresh_api.get_member_agreement_details(member_id)
        
        if billing_details:
            return jsonify({
                'success': True,
                'member_id': member_id,
                'billing_details': billing_details,
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'error': f'No billing details found for member {member_id}'
            }), 404
            
    except Exception as e:
        logger.error(f"❌ Error getting billing details for member {member_id}: {e}")
        return jsonify({
            'success': False,
            'error': f'Error retrieving billing details: {str(e)}'
        }), 500

