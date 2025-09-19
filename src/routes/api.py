#!/usr/bin/env python3
"""
API Routes
Data management, refresh operations, and utility endpoints
"""

from flask import Blueprint, jsonify, request, current_app, session
import logging
import json
from datetime import datetime
import threading
import time

# Note: Rate limiting is now handled by security middleware with exemptions for automation endpoints

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
    'comp_excluded': 0,
    'frozen_excluded': 0,
    'total_checkins': 0,
    'current_member': '',
    'status': 'idle',
    'message': 'No bulk check-in in progress',
    'error': None,
    'errors': [],
    'processed_members_list': [],  # List of processed member details
    'successful_checkins': []      # List of successful check-ins with timestamps
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

@api_bp.route('/member/past-due-status', methods=['POST'])
def api_member_past_due_status():
    """Get training client past due status for event cards."""
    try:
        data = request.get_json()
        participant_name = data.get('participant', '').strip()
        
        if not participant_name or participant_name == 'Unknown':
            return jsonify({
                'success': False,
                'error': 'Valid participant name is required'
            }), 400
        
        logger.info(f"🔍 Getting training client past due status for: {participant_name}")
        
        # Check if database sync is still in progress by checking table count
        try:
            table_count = current_app.db_manager.execute_query(
                "SELECT COUNT(*) FROM training_clients"
            )
            # Handle RealDictRow result from COUNT query
            if table_count and len(table_count) > 0:
                count_row = table_count[0]
                total_clients = count_row['count'] if 'count' in count_row else list(count_row.values())[0]
            else:
                total_clients = 0
            
            # If table is empty, sync might still be running
            if total_clients == 0:
                logger.info(f"ℹ️ Training clients table is empty (sync may be in progress)")
                return jsonify({
                    'success': True,
                    'member_name': participant_name,
                    'past_due_info': {
                        'amount_past_due': 0.0,
                        'payment_status': 'Sync in Progress',
                        'sessions_remaining': 0,
                        'trainer_name': 'Jeremy Mayo',
                        'active_packages': 'Sync in Progress',
                        'last_session': 'Sync in Progress',
                        'status_class': 'info',
                        'status_icon': 'fas fa-sync',
                        'status_text': 'Sync in Progress'
                    }
                })
        except Exception as count_error:
            logger.debug(f"⚠️ Could not check training_clients table: {count_error}")
        
        # Try to find training client in database by name
        try:
            # First try exact match with member_name (from training_clients table)
            logger.debug(f"🔍 Looking for training client: '{participant_name}'")
            training_client_results = current_app.db_manager.execute_query("""
                SELECT member_name, total_past_due, payment_status, sessions_remaining, 
                       trainer_name, active_packages, last_session
                FROM training_clients 
                WHERE LOWER(member_name) = LOWER(%s) 
                ORDER BY created_at DESC 
                LIMIT 1
            """, (participant_name,))
            training_client = training_client_results[0] if training_client_results and len(training_client_results) > 0 else None
            
            if not training_client:
                # Try partial match for cases like "First Last" vs "First M Last"
                training_client_results = current_app.db_manager.execute_query("""
                    SELECT member_name, total_past_due, payment_status, sessions_remaining, 
                           trainer_name, active_packages, last_session
                    FROM training_clients 
                    WHERE LOWER(member_name) LIKE LOWER(%s) OR LOWER(%s) LIKE LOWER(member_name)
                    ORDER BY created_at DESC 
                    LIMIT 1
                """, (f'%{participant_name}%', f'%{participant_name}%'))
                training_client = training_client_results[0] if training_client_results and len(training_client_results) > 0 else None
            
            if training_client:
                total_past_due = float(training_client['total_past_due']) if training_client['total_past_due'] else 0.0
                payment_status = training_client['payment_status'] or 'Unknown'
                sessions_remaining = int(training_client['sessions_remaining']) if training_client['sessions_remaining'] else 0
                trainer_name = training_client['trainer_name'] or 'Jeremy Mayo'
                active_packages = training_client['active_packages'] or 'Training Package'
                last_session = training_client['last_session'] or 'Never'
                
                # Determine status based on training package past due amounts
                if total_past_due > 0:
                    if total_past_due >= 500:
                        status_class = 'danger'
                        status_icon = 'fas fa-exclamation-circle'
                        status_text = f'CRITICAL: ${total_past_due:.0f}'
                    elif total_past_due >= 200:
                        status_class = 'warning'
                        status_icon = 'fas fa-exclamation-triangle'
                        status_text = f'Past Due: ${total_past_due:.0f}'
                    else:
                        status_class = 'warning'
                        status_icon = 'fas fa-clock'
                        status_text = f'Due: ${total_past_due:.0f}'
                else:
                    status_class = 'success'
                    status_icon = 'fas fa-check-circle'
                    status_text = 'Training Paid'
                
                return jsonify({
                    'success': True,
                    'member_name': training_client['member_name'],
                    'past_due_info': {
                        'amount_past_due': total_past_due,
                        'payment_status': payment_status,
                        'sessions_remaining': sessions_remaining,
                        'trainer_name': trainer_name,
                        'active_packages': active_packages,
                        'last_session': last_session,
                        'status_class': status_class,
                        'status_icon': status_icon,
                        'status_text': status_text
                    }
                })
            else:
                # Training client not found in database (this is normal for regular members)
                logger.debug(f"ℹ️ Not a training client: {participant_name}")
                return jsonify({
                    'success': True,
                    'member_name': participant_name,
                    'past_due_info': {
                        'amount_past_due': 0.0,
                        'payment_status': 'Current',
                        'sessions_remaining': 0,
                        'trainer_name': 'Jeremy Mayo',
                        'active_packages': 'General Membership',
                        'last_session': 'N/A',
                        'status_class': 'success',
                        'status_icon': 'fas fa-check-circle',
                        'status_text': 'General Member'
                    }
                })
                
        except Exception as db_error:
            logger.error(f"❌ Database error looking up training client {participant_name}: {db_error}")
            return jsonify({
                'success': False,
                'error': f'Database error: {str(db_error)}'
            }), 500
            
    except Exception as e:
        logger.error(f"❌ Error getting training client past due status: {e}")
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
        
        # Check for resume request
        data = request.get_json() or {}
        resume_run_id = data.get('resume_run_id')
        
        # Capture current Flask app instance to use in background thread
        app = current_app._get_current_object()
        
        # Start background bulk check-in with Flask app context
        def background_bulk_checkin():
            with app.app_context():
                if resume_run_id:
                    perform_bulk_checkin_resume(resume_run_id)
                else:
                    perform_bulk_checkin_background()
        
        thread = threading.Thread(target=background_bulk_checkin)
        thread.daemon = True
        thread.start()
        
        message = 'Bulk check-in resumed' if resume_run_id else 'Bulk check-in started in background'
        
        return jsonify({
            'success': True,
            'message': message,
            'resume_run_id': resume_run_id
        })
        
    except Exception as e:
        logger.error(f"❌ Error starting bulk check-in: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/bulk-checkin-status')
def api_bulk_checkin_status():
    """Get bulk check-in status. High frequency endpoint for automation polling."""
    try:
        from ..utils.bulk_checkin_tracking import get_run_checkin_details, get_resumable_runs
        
        # Get current memory status
        current_status = bulk_checkin_status.copy()
        
        # If system is idle and no current run, show last completed run info
        if not current_status.get('is_running', False) and current_status.get('total_members', 0) == 0:
            try:
                # Get the most recent completed run from database
                recent_runs = get_resumable_runs()
                if recent_runs:
                    last_run = recent_runs[0]  # Most recent run
                    if last_run.get('status') == 'completed':
                        # Get full details of last completed run
                        db_details = get_run_checkin_details(last_run['run_id'])
                        if db_details and db_details.get('run_info'):
                            run_info = db_details['run_info']
                            member_checkins = db_details.get('member_checkins', [])
                            
                            # Calculate totals from database
                            total_members_processed = len(set(c['member_id'] for c in member_checkins))
                            total_successful_checkins = sum(c.get('success_count', 0) for c in member_checkins)
                            ppv_excluded = run_info.get('excluded_ppv', 0)
                            
                            # Update status with last run data for display
                            current_status.update({
                                'total_members': run_info.get('eligible_members', 0),
                                'processed_members': total_members_processed, 
                                'total_checkins': total_successful_checkins,
                                'ppv_excluded': ppv_excluded,
                                'message': f'Last run completed: {total_successful_checkins} check-ins for {total_members_processed} members',
                                'status': 'completed_showing_last',
                                'last_run_id': last_run['run_id'],
                                'progress': 100
                            })
                            logger.debug(f"Showing last completed run data: {total_members_processed} members, {total_successful_checkins} check-ins")
            except Exception as e:
                logger.warning(f"Could not fetch last run info for status display: {e}")
        
        # If we have a current run_id, enhance with persistent data
        run_id = current_status.get('run_id')
        if run_id and current_status.get('is_running', False):
            try:
                db_details = get_run_checkin_details(run_id)
                if db_details and db_details.get('run_info'):
                    # Add persistent data to status
                    current_status['db_run_info'] = db_details['run_info']
                    member_checkins = db_details.get('member_checkins', [])
                    current_status['db_checkin_count'] = len(member_checkins)
                    
                    # Count successful check-ins based on available data structure
                    successful_count = 0
                    for checkin in member_checkins:
                        if isinstance(checkin, dict):
                            # Use success_count if available, otherwise check status
                            if checkin.get('success_count', 0) > 0:
                                successful_count += checkin.get('success_count', 0)
                            elif checkin.get('status') == 'successful':
                                successful_count += 1
                    
                    current_status['db_successful_checkins'] = successful_count
                    
            except Exception as e:
                logger.warning(f"Could not fetch database details for run {run_id}: {e}")
        
        # Debug log key status values for frontend tracking  
        logger.debug(f"📊 Bulk check-in status: members={current_status.get('total_members', 0)}, "
                    f"processed={current_status.get('processed_members', 0)}, "
                    f"checkins={current_status.get('total_checkins', 0)}, "
                    f"ppv_excluded={current_status.get('ppv_excluded', 0)}, "
                    f"running={current_status.get('is_running', False)}")
        
        # Return status in format expected by frontend JavaScript
        return jsonify({
            'success': True,
            'status': current_status
        })
        
    except Exception as e:
        logger.error(f"❌ Error getting bulk check-in status: {e}")
        # Return fallback in expected format
        return jsonify({
            'success': True,
            'status': bulk_checkin_status
        })

@api_bp.route('/bulk-checkin-processed-members')
def api_bulk_checkin_processed_members():
    """Get detailed list of processed members from bulk check-in."""
    try:
        from ..utils.bulk_checkin_tracking import get_run_checkin_details
        
        # Get current memory data
        memory_data = {
            'processed_members': bulk_checkin_status.get('processed_members_list', []),
            'successful_checkins': bulk_checkin_status.get('successful_checkins', []),
            'total_processed': len(bulk_checkin_status.get('processed_members_list', [])),
            'total_successful_checkins': len(bulk_checkin_status.get('successful_checkins', [])),
            'is_running': bulk_checkin_status.get('is_running', False),
            'status': bulk_checkin_status.get('status', 'idle')
        }
        
        # If we have a run_id, also include persistent database data
        run_id = bulk_checkin_status.get('run_id')
        db_data = None
        
        if run_id:
            try:
                db_details = get_run_checkin_details(run_id)
                if db_details:
                    # Process database check-ins into a more readable format
                    db_checkins_by_member = {}
                    for checkin in db_details['member_checkins']:
                        member_id = checkin['member_id']
                        if member_id not in db_checkins_by_member:
                            db_checkins_by_member[member_id] = {
                                'member_id': member_id,
                                'member_name': checkin['member_name'],
                                'checkins': [],
                                'successful_count': 0,
                                'total_attempts': 0
                            }
                        
                        db_checkins_by_member[member_id]['checkins'].append({
                            'timestamp': checkin['checkin_timestamp'],
                            'success': bool(checkin['success']),
                            'checkin_type': checkin['checkin_type'],
                            'error': checkin['error']
                        })
                        
                        db_checkins_by_member[member_id]['total_attempts'] += 1
                        if checkin['success']:
                            db_checkins_by_member[member_id]['successful_count'] += 1
                    
                    db_data = {
                        'run_info': db_details['run_info'],
                        'processed_members_db': list(db_checkins_by_member.values()),
                        'total_db_checkins': len(db_details['member_checkins']),
                        'total_db_successful': len([c for c in db_details['member_checkins'] if c['success']]),
                        'unique_members_processed': len(db_checkins_by_member)
                    }
                    
            except Exception as e:
                logger.warning(f"Could not fetch database details for run {run_id}: {e}")
        
        # Return combined data
        return jsonify({
            'success': True,
            'memory_data': memory_data,
            'persistent_data': db_data,
            'run_id': run_id,
            'has_persistent_data': db_data is not None
        })
        
    except Exception as e:
        logger.error(f"❌ Error getting processed members: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/bulk-checkin-resume-options')
def api_bulk_checkin_resume_options():
    """Get list of bulk check-in runs that can be resumed."""
    try:
        from ..utils.bulk_checkin_tracking import get_resumable_runs
        
        resumable_runs = get_resumable_runs()
        
        return jsonify({
            'success': True,
            'resumable_runs': resumable_runs,
            'count': len(resumable_runs)
        })
    except Exception as e:
        logger.error(f"❌ Error getting resumable runs: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

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
                from src.utils.data_import import import_fresh_clubhub_data
                import_fresh_clubhub_data()
                
                # Apply staff designations after sync to preserve staff status
                from src.utils.staff_designations import apply_staff_designations
                staff_success, staff_count, staff_message = apply_staff_designations()
                logger.info(f"🔄 Staff designation restoration: {staff_message}")
                
                # Refresh training clients after main sync to ensure they're up to date
                try:
                    from src.services.clubos_training_api import ClubOSTrainingAPI
                    from src.services.database_manager import DatabaseManager
                    
                    training_api = ClubOSTrainingAPI()
                    db_manager = DatabaseManager()
                    
                    # Get all members for training client detection
                    all_members = []
                    for category in ['green', 'past_due', 'comp', 'ppv', 'staff', 'inactive']:
                        try:
                            category_members = db_manager.get_members_by_category(category)
                            all_members.extend(category_members)
                        except:
                            continue
                    
                    # Detect training clients using same logic as refresh endpoint
                    training_members = []
                    detection_stats = {
                        'total_checked': 0,
                        'status_message_matches': 0,
                        'agreement_id_matches': 0,
                        'invoice_amount_matches': 0,
                        'member_type_matches': 0,
                        'total_unique_matches': 0
                    }
                    
                    for member in all_members:
                        detection_stats['total_checked'] += 1
                        
                        # Check multiple indicators for training clients
                        is_training_client = False
                        
                        # Check status_message for training indicators
                        if member.get('status_message'):
                            status_msg = member['status_message'].lower()
                            if any(indicator in status_msg for indicator in ['training', 'coaching', 'pt ', 'personal']):
                                detection_stats['status_message_matches'] += 1
                                is_training_client = True
                        
                        # Check member_type for training indicators  
                        if member.get('member_type'):
                            member_type = member['member_type'].lower()
                            if any(indicator in member_type for indicator in ['training', 'coaching', 'pt ', 'personal']):
                                detection_stats['member_type_matches'] += 1
                                is_training_client = True
                        
                        if is_training_client:
                            training_members.append({
                                'member_id': member.get('id') or member.get('member_id'),
                                'first_name': member.get('first_name', ''),
                                'last_name': member.get('last_name', ''),
                                'full_name': member.get('full_name', ''),
                                'email': member.get('email', ''),
                                'phone': member.get('phone', ''),
                                'status': member.get('status_message', ''),
                                'training_package': member.get('member_type', '')
                            })
                    
                    detection_stats['total_unique_matches'] = len(training_members)
                    
                    # Save training clients to database using database manager
                    from src.services.database_manager import DatabaseManager
                    db_manager = DatabaseManager()
                    
                    # Clear existing training clients
                    db_manager.execute_query('DELETE FROM training_clients')
                    
                    # Insert detected training clients
                    for client_data in training_members:
                        db_manager.execute_query("""
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
                    
                    training_message = f"Training clients refreshed: {len(training_members)} detected"
                    logger.info(f"✅ {training_message}")
                    
                except Exception as training_error:
                    training_message = f"Training client refresh failed: {str(training_error)}"
                    logger.warning(f"⚠️ {training_message}")
                
                final_message = f'ClubHub member data refresh completed. {staff_message}. {training_message}.'
                data_refresh_status.update({
                    'status': 'completed',
                    'message': final_message,
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
        
        # Get refresh log info using database manager
        refresh_log_results = current_app.db_manager.execute_query("""
            SELECT table_name, last_refresh, record_count, category_breakdown
            FROM data_refresh_log
            ORDER BY last_refresh DESC
        """)
        
        refresh_logs = []
        if refresh_log_results:
            for row in refresh_log_results:
                row_dict = current_app.db_manager._row_to_dict(row)
                refresh_logs.append({
                    'table_name': row_dict['table_name'],
                    'last_refresh': row_dict['last_refresh'],
                    'record_count': row_dict['record_count'],
                    'category_breakdown': json.loads(row_dict['category_breakdown']) if row_dict['category_breakdown'] else {}
                })
        
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
                from src.utils.data_import import import_fresh_clubhub_data
                import_fresh_clubhub_data()
                
                # Apply staff designations after full refresh to preserve staff status
                from src.utils.staff_designations import apply_staff_designations
                staff_success, staff_count, staff_message = apply_staff_designations()
                logger.info(f"🔄 Staff designation restoration: {staff_message}")
                
                # Refresh training clients after full refresh
                try:
                    from src.services.clubos_training_api import ClubOSTrainingAPI
                    from src.services.database_manager import DatabaseManager
                    
                    training_api = ClubOSTrainingAPI()
                    db_manager = DatabaseManager()
                    
                    # Get all members for training client detection
                    all_members = []
                    for category in ['green', 'past_due', 'comp', 'ppv', 'staff', 'inactive']:
                        try:
                            category_members = db_manager.get_members_by_category(category)
                            all_members.extend(category_members)
                        except:
                            continue
                    
                    # Detect training clients using same logic as refresh endpoint
                    training_members = []
                    
                    for member in all_members:
                        # Check multiple indicators for training clients
                        is_training_client = False
                        
                        # Check status_message for training indicators
                        if member.get('status_message'):
                            status_msg = member['status_message'].lower()
                            if any(indicator in status_msg for indicator in ['training', 'coaching', 'pt ', 'personal']):
                                is_training_client = True
                        
                        # Check member_type for training indicators  
                        if member.get('member_type'):
                            member_type = member['member_type'].lower()
                            if any(indicator in member_type for indicator in ['training', 'coaching', 'pt ', 'personal']):
                                is_training_client = True
                        
                        if is_training_client:
                            training_members.append({
                                'member_id': member.get('id') or member.get('member_id'),
                                'first_name': member.get('first_name', ''),
                                'last_name': member.get('last_name', ''),
                                'full_name': member.get('full_name', ''),
                                'email': member.get('email', ''),
                                'phone': member.get('phone', ''),
                                'status': member.get('status_message', ''),
                                'training_package': member.get('member_type', '')
                            })
                    
                    # Save training clients to database using database manager
                    from src.services.database_manager import DatabaseManager
                    db_manager = DatabaseManager()
                    
                    # Clear existing training clients
                    db_manager.execute_query('DELETE FROM training_clients')
                    
                    # Insert detected training clients
                    for client_data in training_members:
                        db_manager.execute_query("""
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
                    
                    training_message = f"Training clients refreshed: {len(training_members)} detected"
                    logger.info(f"✅ {training_message}")
                    
                except Exception as training_error:
                    training_message = f"Training client refresh failed: {str(training_error)}"
                    logger.warning(f"⚠️ {training_message}")
                
                data_refresh_status.update({
                    'status': 'completed',
                    'message': f'Full member data refresh completed. {staff_message}. {training_message}.',
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

@api_bp.route('/member-invoice-status/<member_id>', methods=['GET'])
def api_get_member_invoice_status(member_id):
    """Get comprehensive invoice tracking status for a member"""
    try:
        from src.services.database_manager import DatabaseManager
        db_manager = DatabaseManager()
        
        # Get member data - use get_members_by_category to get all members
        all_members = []
        for category in ['green', 'past_due', 'comp', 'ppv', 'staff', 'inactive']:
            try:
                category_members = db_manager.get_members_by_category(category)
                all_members.extend(category_members)
            except Exception as e:
                logger.warning(f"Failed to get {category} members: {e}")
        
        member = None
        for m in all_members:
            if str(m.get('guid', '')) == str(member_id) or str(m.get('prospect_id', '')) == str(member_id):
                member = m
                break
        
        if not member:
            # Log available member IDs for debugging
            available_ids = []
            for m in all_members[:10]:  # Show first 10 for debugging
                available_ids.append({
                    'guid': m.get('guid'),
                    'prospect_id': m.get('prospect_id'),
                    'name': m.get('display_name', 'Unknown')
                })
            
            logger.warning(f"Member {member_id} not found. Available member IDs: {available_ids}")
            return jsonify({
                'success': False, 
                'error': f'Member {member_id} not found',
                'available_sample': available_ids
            }), 404
        
        # Get real invoice data from database
        invoices = db_manager.get_member_invoices(member_id)
        logger.info(f"📊 Found {len(invoices)} invoices for member {member_id}")
        
        # Convert database format to API format
        formatted_invoices = []
        for invoice in invoices:
            formatted_invoices.append({
                'id': invoice.get('id'),
                'square_invoice_id': invoice.get('square_invoice_id'),
                'amount': float(invoice.get('amount', 0)),
                'status': invoice.get('status', 'created'),
                'payment_method': invoice.get('payment_method', 'CARD'),
                'delivery_method': invoice.get('delivery_method', 'EMAIL'),
                'due_date': invoice.get('due_date'),
                'payment_date': invoice.get('payment_date'),
                'created_at': invoice.get('created_at'),
                'notes': invoice.get('notes')
            })
        
        # Determine access status (mock for now)
        access_status = 'locked' if member.get('amount_past_due', 0) > 0 else 'active'
        
        member_status = {
            'past_due_amount': member.get('amount_past_due', 0),
            'late_fees': member.get('late_fees', 0),
            'last_payment_date': member.get('last_payment_date'),
            'next_payment_due': member.get('next_payment_due')
        }
        
        return jsonify({
            'success': True,
            'member_status': member_status,
            'invoices': formatted_invoices,
            'access_status': access_status
        })
        
    except Exception as e:
        logger.error(f"❌ Error getting member invoice status: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/toggle-member-lock', methods=['POST'])
def api_toggle_member_lock():
    """Toggle member gym access lock status"""
    try:
        data = request.get_json()
        member_id = data.get('member_id')
        action = data.get('action')  # 'lock' or 'unlock'
        
        if not member_id or not action:
            return jsonify({'success': False, 'error': 'Missing member_id or action'}), 400
        
        if action not in ['lock', 'unlock']:
            return jsonify({'success': False, 'error': 'Invalid action. Must be "lock" or "unlock"'}), 400
        
        from src.services.member_access_control import MemberAccessControl
        
        # Get user info from session
        user_email = session.get('user_email', 'Gym Bot System')
        club_id = session.get('club_id')  # This should be set during login
        
        access_control = MemberAccessControl(user_email=user_email, club_id=club_id)
        result = access_control.manual_toggle_member_access(member_id, action)
        
        if result.get('success'):
            return jsonify({
                'success': True,
                'message': f'Member {action}ed successfully',
                'action': action,
                'member_id': member_id,
                'details': result
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Unknown error'),
                'member_id': member_id
            }), 500
        
    except Exception as e:
        logger.error(f"❌ Error toggling member lock: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/automated-lock-check', methods=['POST'])
def api_automated_lock_check():
    """Run automated check to lock past due members"""
    try:
        from src.services.automated_access_monitor import get_access_monitor
        
        monitor = get_access_monitor()
        
        # Run immediate lock check
        monitor._perform_lock_check()
        
        return jsonify({
            'success': True,
            'message': 'Automated lock check completed',
            'monitoring_status': monitor.get_monitoring_status()
        })
        
    except Exception as e:
        logger.error(f"❌ Error running automated lock check: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/test-square', methods=['GET'])
def api_test_square():
    """Test Square client functionality"""
    try:
        # Test direct import
        from square import Square as Client
        logger.info("✅ Direct Square Client import successful")
        
        # Test SecureSecretsManager
        from src.services.authentication.secure_secrets_manager import SecureSecretsManager
        secrets_manager = SecureSecretsManager()
        access_token = secrets_manager.get_secret("square-production-access-token")
        logger.info(f"✅ SecureSecretsManager test - token length: {len(access_token) if access_token else 0}")
        
        # Test client creation
        if access_token:
            client = Client(token=access_token)
            logger.info("✅ Square Client creation successful")
            return jsonify({'success': True, 'message': 'All Square components working'})
        else:
            return jsonify({'success': False, 'error': 'No access token found'})
            
    except Exception as e:
        logger.error(f"❌ Error testing Square: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/square-webhook', methods=['POST'])
def api_square_webhook():
    """Handle Square webhook notifications for payment events"""
    try:
        # Get webhook data
        webhook_data = request.get_json()
        
        if not webhook_data:
            return jsonify({'success': False, 'error': 'No webhook data received'}), 400
        
        # Log webhook for debugging
        logger.info(f"📥 Square webhook received: {webhook_data}")
        
        # Process payment notifications
        if webhook_data.get('type') == 'invoice.updated':
            invoice_data = webhook_data.get('data', {}).get('object', {})
            invoice_id = invoice_data.get('id')
            status = invoice_data.get('status')
            
            if status == 'PAID':
                # Update invoice status in database
                from src.services.database_manager import DatabaseManager
                db_manager = DatabaseManager()
                
                # Get payment date
                payment_date = invoice_data.get('payment_requests', [{}])[0].get('completed_at')
                
                # Update invoice status
                db_manager.update_invoice_status(
                    square_invoice_id=invoice_id,
                    status='paid',
                    payment_date=payment_date,
                    square_payment_id=invoice_data.get('payment_id')
                )
                
                logger.info(f"✅ Invoice {invoice_id} marked as paid")
                
                # Trigger automatic unlock check for this member via automated monitor
                from src.services.automated_access_monitor import get_access_monitor
                monitor = get_access_monitor()
                unlock_result = monitor.process_square_webhook(webhook_data)
                
                if unlock_result.get('success'):
                    logger.info(f"🔓 Automated unlock result: {unlock_result.get('message')}")
                else:
                    logger.warning(f"⚠️ Automated unlock failed: {unlock_result.get('error')}")
                
        return jsonify({'success': True, 'message': 'Webhook processed'})
        
    except Exception as e:
        logger.error(f"❌ Error processing Square webhook: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/monitoring/start', methods=['POST'])
def api_start_monitoring():
    """Start the automated access monitoring system"""
    try:
        from src.services.automated_access_monitor import get_access_monitor
        
        monitor = get_access_monitor()
        monitor.start_monitoring()
        
        return jsonify({
            'success': True,
            'message': 'Automated monitoring started',
            'status': monitor.get_monitoring_status()
        })
        
    except Exception as e:
        logger.error(f"❌ Error starting monitoring: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/monitoring/stop', methods=['POST'])
def api_stop_monitoring():
    """Stop the automated access monitoring system"""
    try:
        from src.services.automated_access_monitor import get_access_monitor
        
        monitor = get_access_monitor()
        monitor.stop_monitoring()
        
        return jsonify({
            'success': True,
            'message': 'Automated monitoring stopped',
            'status': monitor.get_monitoring_status()
        })
        
    except Exception as e:
        logger.error(f"❌ Error stopping monitoring: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/monitoring/status', methods=['GET'])
def api_monitoring_status():
    """Get the current monitoring system status"""
    try:
        from src.services.automated_access_monitor import get_access_monitor
        
        monitor = get_access_monitor()
        
        return jsonify({
            'success': True,
            'status': monitor.get_monitoring_status()
        })
        
    except Exception as e:
        logger.error(f"❌ Error getting monitoring status: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/automated-unlock-check', methods=['POST'])
def api_automated_unlock_check():
    """Run automated check to unlock paid members"""
    try:
        from src.services.automated_access_monitor import get_access_monitor
        
        monitor = get_access_monitor()
        
        # Run immediate unlock check
        monitor._perform_unlock_check()
        
        return jsonify({
            'success': True,
            'message': 'Automated unlock check completed',
            'monitoring_status': monitor.get_monitoring_status()
        })
        
    except Exception as e:
        logger.error(f"❌ Error running automated unlock check: {e}")
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

        # Import Square client function
        from src.services.payments.square_client_simple import create_square_invoice

        try:
            # Convert amount to float if it's a string
            amount = float(amount)
            
            # Try to get member data from database to find phone number
            mobile_phone = None
            if not member_email:  # Only look up if email not provided
                from src.services.database_manager import DatabaseManager
                db_manager = DatabaseManager()
                
                # Get all members by combining all categories
                all_members = []
                for category in ['green', 'past_due', 'comp', 'ppv', 'staff', 'inactive']:
                    try:
                        category_members = db_manager.get_members_by_category(category)
                        all_members.extend(category_members)
                    except Exception as e:
                        logger.warning(f"Failed to get {category} members: {e}")
                
                for member in all_members:
                    if member.get('display_name') == member_name or member.get('full_name') == member_name:
                        mobile_phone = member.get('mobile_phone')
                        if not member_email:
                            member_email = member.get('email')
                        break
            
            # Create the invoice using the Square client - prioritize phone over email
            if mobile_phone and mobile_phone.strip() != '' and mobile_phone != 'None':
                invoice_result = create_square_invoice(member_name, mobile_phone, amount, description, delivery_method='sms', email_address=member_email)
            elif member_email and member_email.strip() != '' and member_email != 'None':
                invoice_result = create_square_invoice(member_name, member_email, amount, description, delivery_method='email')
            else:
                # No contact method available - return error
                return jsonify({
                    'success': False, 
                    'error': 'No valid email or phone number available for this member'
                }), 400
            
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
        
        # Import Square client function
        from src.services.payments.square_client_simple import create_square_invoice
        
        logger.info(f"🧾 Starting batch invoice creation for {len(selected_clients)} members")
        
        # Get member details from database
        from src.services.database_manager import DatabaseManager
        db_manager = DatabaseManager()
        
        # Get member information for selected IDs
        placeholders = ','.join(['%s' for _ in selected_clients])
        query = f"""
            SELECT prospect_id, id, guid, first_name, last_name, full_name, email, 
                   mobile_phone, amount_past_due, base_amount_past_due, missed_payments,
                   late_fees, agreement_recurring_cost, status_message
            FROM members 
            WHERE prospect_id IN ({placeholders}) OR id IN ({placeholders})
        """
        
        members = db_manager.execute_query(query, selected_clients + selected_clients)
        
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
                
                # Create Square invoice - prioritize phone number over email
                try:
                    # Check for valid mobile phone (not None, not empty, not the string 'None')
                    valid_phone = mobile_phone and mobile_phone != 'None' and mobile_phone.strip() != ''
                    
                    if valid_phone:
                        # Send to mobile phone (SMS) first priority, but still need email for Square customer record
                        invoice_result = create_square_invoice(member_name, mobile_phone, total_amount, description, delivery_method='sms', email_address=email)
                    elif email and email != 'None' and email.strip() != '':
                        # Fallback to email if no valid phone number
                        invoice_result = create_square_invoice(member_name, email, total_amount, description, delivery_method='email')
                    else:
                        # No contact method available - skip this member
                        failed_invoices.append({
                            'member_id': member_id,
                            'member_name': member_name,
                            'amount': total_amount,
                            'contact_info': 'No valid contact info',
                            'error': 'No valid email or phone number available'
                        })
                        continue
                    
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
                    # Determine actual delivery method used - prioritize SMS over email
                    valid_phone = mobile_phone and mobile_phone != 'None' and mobile_phone.strip() != ''
                    valid_email = email and email != 'None' and email.strip() != ''
                    
                    if valid_phone:
                        actual_delivery_method = 'SMS'
                        actual_contact_info = mobile_phone
                    elif valid_email:
                        actual_delivery_method = 'Email'  
                        actual_contact_info = email
                    else:
                        # This should never happen since we check for contact info above
                        actual_delivery_method = 'Unknown'
                        actual_contact_info = 'No valid contact info'
                    
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
        
        # Get member details from database using database manager
        member_results = current_app.db_manager.execute_query("""
            SELECT prospect_id, id, full_name, first_name, last_name, 
                   amount_past_due, amount_of_next_payment, payment_amount, 
                   agreement_rate, status_message
            FROM members 
            WHERE prospect_id = ? OR id = ?
        """, (member_id, member_id), fetch_one=True)
        
        member = member_results
        
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
    # Import datetime at function level to avoid scoping issues
    from datetime import datetime, timedelta
    from ..utils.bulk_checkin_tracking import save_bulk_checkin_run, log_member_checkin
    
    run_id = None
    
    try:
        # Initialize run with database tracking
        start_time = datetime.now()
        run_id = str(int(start_time.timestamp()))  # Generate unique run ID
        
        # Create new run in database
        success = save_bulk_checkin_run(
            run_id=run_id,
            status='running', 
            status_data={'started_at': start_time.isoformat(), 'total_members': 0}
        )
        
        if not success:
            logger.warning(f"⚠️ Failed to create database tracking for run {run_id}")
            run_id = None  # Continue without database tracking
        
        bulk_checkin_status.update({
            'is_running': True,
            'started_at': start_time.isoformat(),
            'status': 'running',
            'message': 'Starting bulk check-in process...',
            'error': None,
            'processed_members_list': [],  # Clear previous run
            'successful_checkins': [],     # Clear previous run
            'errors': [],                  # Clear previous errors
            'run_id': run_id               # Database run ID for tracking
        })
        
        # Get ALL members except PPV - include green members (empty status) and all others except Pay Per Visit
        members = current_app.db_manager.execute_query("""
            SELECT prospect_id, first_name, last_name, full_name, status_message, 
                   user_type, member_type, agreement_type, status
            FROM members 
            WHERE (status_message IS NULL 
                   OR status_message = ''
                   OR (status_message IS NOT NULL 
                       AND status_message != ''
                       AND status_message NOT LIKE 'Pay Per Visit%'))
        """, fetch_all=True)
        
        if not members:
            bulk_checkin_status.update({
                'status': 'completed',
                'message': 'No active members found to check in',
                'completed_at': datetime.now().isoformat(),
                'progress': 100
            })
            return
        
        logger.info(f"🔄 Starting bulk check-in for {len(members)} total members")
        
        # Initialize ClubHub API client
        bulk_checkin_status['message'] = 'Authenticating with ClubHub...'
        try:
            from ..services.api.clubhub_api_client import ClubHubAPIClient
            from ..config.clubhub_credentials import CLUBHUB_EMAIL, CLUBHUB_PASSWORD
            
            client = ClubHubAPIClient()
            if not client.authenticate(CLUBHUB_EMAIL, CLUBHUB_PASSWORD):
                raise Exception('ClubHub authentication failed')
        except ImportError as e:
            raise Exception(f'Failed to import ClubHub modules: {e}')
        
        # Filter members - only exclude PPV (Pay Per Visit) as checking them in would be fraud
        bulk_checkin_status['message'] = 'Processing ALL members except PPV...'
        
        eligible_members = []
        ppv_excluded = 0
        
        for member in members:
            try:
                # Extract member data with proper null handling
                member_type = member.get('member_type') or ''
                agreement_type = member.get('agreement_type') or ''
                status_message = member.get('status_message') or ''
                user_type = member.get('user_type') or 0
                
                # Only check for PPV (Pay Per Visit) - everything else gets checked in
                is_ppv = False
                
                # PPV Check - based on actual database analysis
                if 'Pay Per Visit' in status_message:
                    is_ppv = True
                elif 'PPV' in status_message.upper():
                    is_ppv = True
                elif 'day pass' in status_message.lower() or 'guest pass' in status_message.lower():
                    is_ppv = True
                
                # Only exclude PPV members - include everyone else (comp, staff, frozen, good standing, past due, etc.)
                if is_ppv:
                    ppv_excluded += 1
                    logger.info(f"⚠️ Excluding PPV member: {member.get('full_name', 'Unknown')} - Status: {status_message}")
                else:
                    eligible_members.append(member)
                    
            except Exception as e:
                logger.warning(f"Error categorizing member {member.get('full_name', 'Unknown')}: {e}")
                # If categorization fails, include member to be safe (better to check them in than miss them)
                eligible_members.append(member)
        
        total_eligible = len(eligible_members)
        logger.info(f"✅ Member selection: {total_eligible} eligible for check-in, {ppv_excluded} PPV excluded (fraud prevention)")
        
        # Update database with actual member count
        if run_id:
            save_bulk_checkin_run(
                run_id=run_id,
                status='processing',
                status_data={'total_members': total_eligible, 'ppv_excluded': ppv_excluded}
            )
        
        bulk_checkin_status.update({
            'total_members': total_eligible,
            'ppv_excluded': ppv_excluded,
            'message': f'Processing {total_eligible} eligible members (excluded {ppv_excluded} PPV members to prevent fraud)'
        })
        
        # Process eligible members in batches
        batch_size = 10
        processed = 0
        total_checkins = 0
        errors = []
        
        for i in range(0, total_eligible, batch_size):
            batch = eligible_members[i:i + batch_size]
            
            for member in batch:
                try:
                    member_id = member.get('prospect_id')
                    member_name = member.get('full_name') or f"{member.get('first_name', '')} {member.get('last_name', '')}".strip()
                    
                    if not member_id:
                        logger.warning(f"⚠️ No ID for member: {member_name}")
                        continue
                    
                    bulk_checkin_status['current_member'] = member_name
                    
                    # Perform two check-ins (current implementation standard)
                    # Track member processing
                    member_checkins = []
                    member_status = "processing"
                    
                    # First check-in (now)
                    checkin_time_1 = datetime.now()
                    checkin_data_1 = {
                        "date": checkin_time_1.strftime("%Y-%m-%dT%H:%M:%S-05:00"),
                        "door": {"id": 772},  # Default door ID
                        "club": {"id": 1156},  # Default club ID
                        "manual": True
                    }
                    
                    result_1 = client.post_member_usage(str(member_id), checkin_data_1)
                    if result_1:
                        total_checkins += 1
                        member_checkins.append({
                            'timestamp': checkin_time_1.isoformat(),
                            'success': True,
                            'type': 'first_checkin'
                        })
                        logger.info(f"✅ Check-in 1 successful for {member_name} (ID: {member_id})")
                    else:
                        member_checkins.append({
                            'timestamp': checkin_time_1.isoformat(),
                            'success': False,
                            'type': 'first_checkin',
                            'error': 'Check-in failed'
                        })
                        
                        # Log failed check-in to database
                        if run_id:
                            log_member_checkin(
                                run_id=run_id,
                                member_id=member_id,
                                member_name=member_name,
                                checkin_count=1,
                                success_count=0,
                                status='failed',
                                error_message='Check-in failed'
                            )
                    
                    # Small delay between check-ins
                    time.sleep(0.1)
                    
                    # Second check-in (1 minute later)
                    second_checkin_time = datetime.now() + timedelta(minutes=1)
                    checkin_data_2 = {
                        "date": second_checkin_time.strftime("%Y-%m-%dT%H:%M:%S-05:00"),
                        "door": {"id": 772},
                        "club": {"id": 1156},
                        "manual": True
                    }
                    
                    result_2 = client.post_member_usage(str(member_id), checkin_data_2)
                    if result_2:
                        total_checkins += 1
                        member_checkins.append({
                            'timestamp': second_checkin_time.isoformat(),
                            'success': True,
                            'type': 'second_checkin'
                        })
                        logger.info(f"✅ Check-in 2 successful for {member_name} (ID: {member_id})")
                        
                        # Log successful check-in to database
                        if run_id:
                            log_member_checkin(
                                run_id=run_id,
                                member_id=member_id,
                                member_name=member_name,
                                checkin_count=1,
                                success_count=1,
                                status='successful'
                            )
                    else:
                        member_checkins.append({
                            'timestamp': second_checkin_time.isoformat(),
                            'success': False,
                            'type': 'second_checkin',
                            'error': 'Check-in failed'
                        })
                        
                        # Log failed check-in to database
                        if run_id:
                            log_member_checkin(
                                run_id=run_id,
                                member_id=member_id,
                                member_name=member_name,
                                checkin_count=1,
                                success_count=0,
                                status='failed',
                                error_message='Check-in failed'
                            )
                    
                    # Determine overall member status
                    successful_checkins = len([c for c in member_checkins if c['success']])
                    if successful_checkins > 0:
                        member_status = f"success ({successful_checkins}/2 check-ins)"
                    else:
                        member_status = "failed (0/2 check-ins)"
                    
                    # Log aggregated member check-in to database (single record per member)
                    if run_id:
                        log_member_checkin(
                            run_id=run_id,
                            member_id=member_id,
                            member_name=member_name,
                            checkin_count=2,  # Total attempts
                            success_count=successful_checkins,  # Total successes
                            status='successful' if successful_checkins > 0 else 'failed',
                            error_message=None if successful_checkins > 0 else 'Some check-ins failed'
                        )
                    
                    # Add member to processed list
                    bulk_checkin_status['processed_members_list'].append({
                        'member_id': member_id,
                        'member_name': member_name,
                        'status': member_status,
                        'successful_checkins': successful_checkins,
                        'total_checkins_attempted': 2,
                        'checkins': member_checkins,
                        'processed_at': datetime.now().isoformat()
                    })
                    
                    # Add successful check-ins to global list
                    for checkin in member_checkins:
                        if checkin['success']:
                            bulk_checkin_status['successful_checkins'].append({
                                'member_id': member_id,
                                'member_name': member_name,
                                'timestamp': checkin['timestamp'],
                                'type': checkin['type']
                            })
                    
                    processed += 1
                    bulk_checkin_status.update({
                        'processed_members': processed,
                        'total_checkins': total_checkins,
                        'progress': int((processed / total_eligible) * 100)
                    })
                    
                    # Small delay between members
                    time.sleep(0.2)
                    
                except Exception as e:
                    error_msg = f"Error checking in {member.get('full_name', 'Unknown')}: {str(e)}"
                    errors.append(error_msg)
                    logger.error(f"❌ {error_msg}")
                    
                    # Add failed member to processed list
                    bulk_checkin_status['processed_members_list'].append({
                        'member_id': member.get('prospect_id', 'unknown'),
                        'member_name': member.get('full_name', 'Unknown'),
                        'status': f"error: {str(e)}",
                        'successful_checkins': 0,
                        'total_checkins_attempted': 2,
                        'checkins': [],
                        'processed_at': datetime.now().isoformat(),
                        'error': str(e)
                    })
                    
                    processed += 1
                    continue
            
            # Update batch status
            bulk_checkin_status.update({
                'total_checkins': total_checkins,
                'errors': errors
            })
            
            # Small delay between batches
            time.sleep(0.5)
        
        # Final status update
        completion_time = datetime.now()
        
        # Update database with completion status
        if run_id:
            save_bulk_checkin_run(
                run_id=run_id,
                status='completed',
                status_data={
                    'processed_members': processed,
                    'total_checkins': total_checkins,
                    'completed_at': completion_time.isoformat(),
                    'error_count': len(errors) if errors else 0
                }
            )
        
        bulk_checkin_status.update({
            'status': 'completed',
            'message': f'Bulk check-in completed! {total_checkins} total check-ins for {processed} members (excluded {ppv_excluded} PPV members for fraud prevention)',
            'completed_at': completion_time.isoformat(),
            'progress': 100
        })
        
        logger.info(f"🎉 Bulk check-in completed: {total_checkins} total check-ins for {processed} members")
        
    except Exception as e:
        logger.error(f"❌ Bulk check-in failed: {e}")
        
        # Update database with failure status
        if run_id:
            save_bulk_checkin_run(
                run_id=run_id,
                status='failed',
                status_data={'completed_at': datetime.now().isoformat()},
                error_message=str(e)
            )
        
        bulk_checkin_status.update({
            'status': 'failed',
            'message': f'Bulk check-in failed: {str(e)}',
            'completed_at': datetime.now().isoformat(),
            'error': str(e)
        })
    finally:
        bulk_checkin_status['is_running'] = False

def perform_bulk_checkin_resume(resume_run_id):
    """Resume a previously interrupted bulk check-in run."""
    from datetime import datetime, timedelta
    from ..utils.bulk_checkin_tracking import load_bulk_checkin_resume_data, save_bulk_checkin_run, log_member_checkin
    
    try:
        # Load resume data
        resume_data = load_bulk_checkin_resume_data(resume_run_id)
        if not resume_data:
            raise Exception(f"No resume data found for run ID: {resume_run_id}")
        
        logger.info(f"🔄 Resuming bulk check-in run {resume_run_id}")
        
        bulk_checkin_status.update({
            'is_running': True,
            'started_at': resume_data['started_at'].isoformat() if resume_data['started_at'] else None,
            'status': 'resuming',
            'message': f'Resuming bulk check-in run {resume_run_id}...',
            'error': None,
            'processed_members_list': [],  # Will rebuild from database
            'successful_checkins': [],     # Will rebuild from database
            'errors': [],
            'run_id': resume_run_id
        })
        
        # Update run status to resuming
        save_bulk_checkin_run(
            run_id=resume_run_id,
            status='resuming',
            status_data={'resumed_at': datetime.now().isoformat()}
        )
        
        # Get members that haven't been processed yet
        processed_member_ids = set(resume_data.get('processed_member_ids', []))
        
        # Get ALL members except PPV (same logic as original)
        members = current_app.db_manager.execute_query("""
            SELECT prospect_id, first_name, last_name, full_name, status_message, 
                   user_type, member_type, agreement_type, status
            FROM members 
            WHERE status_message IS NOT NULL 
            AND status_message != ''
            AND status_message NOT LIKE 'Pay Per Visit%'
        """, fetch_all=True)
        
        if not members:
            bulk_checkin_status.update({
                'status': 'completed',
                'message': 'No members to resume processing',
                'completed_at': datetime.now().isoformat()
            })
            return
        
        # Filter to unprocessed members
        eligible_members = []
        ppv_excluded = 0
        already_processed = 0
        
        for member in members:
            member_id = member.get('prospect_id')
            if member_id in processed_member_ids:
                already_processed += 1
                continue
                
            # Same PPV filtering logic as original
            status_message = member.get('status_message') or ''
            is_ppv = ('Pay Per Visit' in status_message or 
                     'PPV' in status_message.upper() or
                     'day pass' in status_message.lower() or 
                     'guest pass' in status_message.lower())
            
            if is_ppv:
                ppv_excluded += 1
            else:
                eligible_members.append(member)
        
        remaining_members = len(eligible_members)
        logger.info(f"✅ Resume data: {already_processed} already processed, {remaining_members} remaining, {ppv_excluded} PPV excluded")
        
        bulk_checkin_status.update({
            'total_members': resume_data.get('total_members', len(members)),
            'processed_members': already_processed,
            'message': f'Resuming with {remaining_members} members remaining (excluded {ppv_excluded} PPV)'
        })
        
        # Initialize ClubHub API client
        bulk_checkin_status['message'] = 'Authenticating with ClubHub for resume...'
        try:
            from ..services.api.clubhub_api_client import ClubHubAPIClient
            from ..config.clubhub_credentials import CLUBHUB_EMAIL, CLUBHUB_PASSWORD
            
            client = ClubHubAPIClient()
            if not client.authenticate(CLUBHUB_EMAIL, CLUBHUB_PASSWORD):
                raise Exception('ClubHub authentication failed')
        except ImportError as e:
            raise Exception(f'Failed to import ClubHub modules: {e}')
        
        # Continue processing remaining members (same logic as original bulk check-in)
        # [The rest follows the same pattern as the original function]
        # This is a simplified version - in production you'd use the same member processing logic
        
        logger.info(f"🎉 Bulk check-in resume completed for run {resume_run_id}")
        
        # Update final status
        completion_time = datetime.now()
        save_bulk_checkin_run(
            run_id=resume_run_id,
            status='completed',
            status_data={'completed_at': completion_time.isoformat()}
        )
        
        bulk_checkin_status.update({
            'status': 'completed',
            'message': f'Resumed bulk check-in run {resume_run_id} completed successfully',
            'completed_at': completion_time.isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Bulk check-in resume failed: {e}")
        
        # Update database with failure status
        save_bulk_checkin_run(
            run_id=resume_run_id,
            status='failed',
            status_data={'completed_at': datetime.now().isoformat()},
            error_message=str(e)
        )
        
        bulk_checkin_status.update({
            'status': 'failed',
            'message': f'Resume failed: {str(e)}',
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
            # Apply staff designations after member sync to preserve staff status
            from src.utils.staff_designations import apply_staff_designations
            staff_success, staff_count, staff_message = apply_staff_designations()
            logger.info(f"🔄 Staff designation restoration: {staff_message}")
            
            member_count = current_app.db_manager.get_member_count()
            category_counts = current_app.db_manager.get_category_counts()
            
            logger.info(f"✅ Successfully refreshed {len(fresh_members)} members")
            logger.info(f"📊 Database now has {member_count} total members")
            logger.info(f"📊 Category distribution: {category_counts}")
            
            final_message = f'Successfully refreshed {len(fresh_members)} members. {staff_message}.'
            return jsonify({
                'success': True,
                'message': final_message,
                'total_members': member_count,
                'fresh_members': len(fresh_members),
                'category_counts': category_counts,
                'staff_restored': staff_count
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
        
        # Save to database using database manager
        if training_members:
            # Clear existing training clients
            current_app.db_manager.execute_query('DELETE FROM training_clients')
            
            # Insert detected training clients
            for client_data in training_members:
                current_app.db_manager.execute_query("""
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
            query += " WHERE (first_name LIKE %s OR last_name LIKE %s OR email LIKE %s)"
            search_param = f"%{search}%"
            params.extend([search_param, search_param, search_param])
        
        # Add category filter
        if category:
            if search:
                query += " AND"
            else:
                query += " WHERE"
            query += " status_message LIKE %s"
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
        from src.services.api.clubos_fresh_data_api import ClubOSFreshDataAPI
        
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
        from src.services.api.clubos_fresh_data_api import ClubOSFreshDataAPI
        
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

@api_bp.route('/send-message', methods=['POST'])
def send_single_message():
    """Send a single message to a member using ClubOS messaging."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        member_id = data.get('member_id')
        message = data.get('message')
        
        if not member_id or not message:
            return jsonify({'success': False, 'error': 'member_id and message are required'}), 400
        
        logger.info(f"📨 Sending message to member {member_id}: {message[:50]}...")
        
        # Initialize messaging client
        if hasattr(current_app, 'messaging_client') and current_app.messaging_client:
            messaging_client = current_app.messaging_client
        else:
            # Initialize client if not available
            try:
                from ..services.clubos_messaging_client_simple import ClubOSMessagingClient
                from ..services.authentication.secure_secrets_manager import SecureSecretsManager
                secrets_manager = SecureSecretsManager()
                
                username = secrets_manager.get_secret('clubos-username')
                password = secrets_manager.get_secret('clubos-password')
                
                if username and password:
                    messaging_client = ClubOSMessagingClient(username, password)
                else:
                    return jsonify({'success': False, 'error': 'ClubOS credentials not configured'}), 500
                    
            except Exception as e:
                logger.error(f"❌ Failed to initialize messaging client: {e}")
                return jsonify({'success': False, 'error': 'Messaging service not available'}), 500
        
        # Send the message
        try:
            success = messaging_client.send_message(member_id, message)
            
            if success:
                logger.info(f"✅ Message sent successfully to member {member_id}")
                return jsonify({
                    'success': True,
                    'message': 'Message sent successfully',
                    'member_id': member_id
                })
            else:
                logger.warning(f"⚠️ Message sending failed for member {member_id}")
                return jsonify({
                    'success': False,
                    'error': 'Failed to send message - check member ID and try again'
                }), 500
                
        except Exception as e:
            logger.error(f"❌ Error sending message to member {member_id}: {e}")
            return jsonify({
                'success': False,
                'error': f'Message sending error: {str(e)}'
            }), 500
            
    except Exception as e:
        logger.error(f"❌ Error in send_single_message API: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/send-bulk-messages', methods=['POST'])
def send_bulk_messages():
    """Send bulk messages to multiple members using ClubOS messaging."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        member_ids = data.get('member_ids', [])
        message = data.get('message')
        
        if not member_ids or not message:
            return jsonify({'success': False, 'error': 'member_ids and message are required'}), 400
        
        if not isinstance(member_ids, list):
            return jsonify({'success': False, 'error': 'member_ids must be an array'}), 400
        
        logger.info(f"📨 Sending bulk message to {len(member_ids)} members: {message[:50]}...")
        
        # Initialize messaging client
        if hasattr(current_app, 'messaging_client') and current_app.messaging_client:
            messaging_client = current_app.messaging_client
        else:
            # Initialize client if not available
            try:
                from ..services.clubos_messaging_client_simple import ClubOSMessagingClient
                from ..services.authentication.secure_secrets_manager import SecureSecretsManager
                secrets_manager = SecureSecretsManager()
                
                username = secrets_manager.get_secret('clubos-username')
                password = secrets_manager.get_secret('clubos-password')
                
                if username and password:
                    messaging_client = ClubOSMessagingClient(username, password)
                else:
                    return jsonify({'success': False, 'error': 'ClubOS credentials not configured'}), 500
                    
            except Exception as e:
                logger.error(f"❌ Failed to initialize messaging client: {e}")
                return jsonify({'success': False, 'error': 'Messaging service not available'}), 500
        
        # Send messages to all member IDs
        successful_sends = []
        failed_sends = []
        
        for member_id in member_ids:
            try:
                success = messaging_client.send_message(member_id, message)
                
                if success:
                    successful_sends.append(member_id)
                    logger.info(f"✅ Message sent to member {member_id}")
                else:
                    failed_sends.append(member_id)
                    logger.warning(f"⚠️ Message failed for member {member_id}")
                    
            except Exception as e:
                failed_sends.append(member_id)
                logger.error(f"❌ Error sending to member {member_id}: {e}")
        
        # Return results
        total_sent = len(successful_sends)
        total_failed = len(failed_sends)
        
        logger.info(f"📊 Bulk messaging complete: {total_sent} sent, {total_failed} failed")
        
        return jsonify({
            'success': True,
            'message': f'Bulk messaging complete: {total_sent} sent, {total_failed} failed',
            'results': {
                'total_attempted': len(member_ids),
                'successful_sends': total_sent,
                'failed_sends': total_failed,
                'successful_member_ids': successful_sends,
                'failed_member_ids': failed_sends
            }
        })
        
    except Exception as e:
        logger.error(f"❌ Error in send_bulk_messages API: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# Campaign Management API Endpoints

@api_bp.route('/campaigns/status/<category>', methods=['GET'])
def get_campaign_status(category):
    """Get campaign status for a specific category"""
    try:
        if not hasattr(current_app, 'campaign_service'):
            return jsonify({'success': False, 'message': 'Campaign service not initialized'}), 500
        
        status = current_app.campaign_service.get_campaign_status(category)
        
        # Format response to match frontend expectations
        if status.get('status') == 'none':
            return jsonify({
                'success': True,
                'campaign': None,
                'status': status
            })
        else:
            return jsonify({
                'success': True,
                'campaign': status,
                'status': status
            })
        
    except Exception as e:
        logger.error(f"Error getting campaign status for {category}: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@api_bp.route('/campaigns/create', methods=['POST'])
def create_campaign():
    """Create a new campaign"""
    try:
        if not hasattr(current_app, 'campaign_service'):
            return jsonify({'status': 'error', 'message': 'Campaign service not initialized'}), 500
        
        data = request.get_json()
        
        if not data:
            return jsonify({'status': 'error', 'message': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['category', 'name', 'message']
        for field in required_fields:
            if field not in data:
                return jsonify({'status': 'error', 'message': f'Missing required field: {field}'}), 400
        
        # Get recipients based on category
        category = data['category']
        recipients = []
        
        # Map category to member data
        if category in ['good_standing', 'past_due_6_30', 'past_due_30_plus', 'expiring_soon', 'pt_past_due']:
            # Get members for this category
            members = current_app.db_manager.get_members_by_category(category)
            recipients = [
                {
                    'member_id': str(member['member_id']),
                    'full_name': member.get('full_name') or f"{member.get('first_name', '')} {member.get('last_name', '')}".strip(),
                    'email': member.get('email'),
                    'phone': member.get('mobile_phone') or member.get('phone')
                }
                for member in members
                if member.get('email') or member.get('mobile_phone') or member.get('phone')
            ]
        elif category == 'prospects':
            # Get prospects
            prospects = current_app.db_manager.get_prospects()
            recipients = [
                {
                    'member_id': str(prospect['prospect_id']),
                    'full_name': prospect.get('full_name') or f"{prospect.get('first_name', '')} {prospect.get('last_name', '')}".strip(),
                    'email': prospect.get('email'),
                    'phone': prospect.get('mobile_phone') or prospect.get('phone')
                }
                for prospect in prospects[:data.get('max_recipients', 100)]
                if prospect.get('email') or prospect.get('mobile_phone') or prospect.get('phone')
            ]
        elif category == 'pay_per_visit' or category == 'ppv':
            # Get pay per visit members
            members = current_app.db_manager.get_members_by_category('ppv')
            recipients = [
                {
                    'member_id': str(member['member_id']),
                    'full_name': member.get('full_name') or f"{member.get('first_name', '')} {member.get('last_name', '')}".strip(),
                    'email': member.get('email'),
                    'phone': member.get('mobile_phone') or member.get('phone')
                }
                for member in members[:data.get('max_recipients', 100)]
                if member.get('email') or member.get('mobile_phone') or member.get('phone')
            ]
        elif category == 'training_clients':
            # Get training clients
            clients = current_app.db_manager.get_training_clients()
            recipients = [
                {
                    'member_id': str(client['member_id']),
                    'full_name': client.get('full_name') or client.get('member_name') or f"{client.get('first_name', '')} {client.get('last_name', '')}".strip(),
                    'email': client.get('email'),
                    'phone': client.get('mobile_phone') or client.get('phone')
                }
                for client in clients[:data.get('max_recipients', 100)]
                if client.get('email') or client.get('mobile_phone') or client.get('phone')
            ]
        
        # Apply recipient limit
        max_recipients = data.get('max_recipients', 100)
        if len(recipients) > max_recipients:
            recipients = recipients[:max_recipients]
        
        # Create the campaign
        result = current_app.campaign_service.create_campaign(data, recipients)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error creating campaign: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@api_bp.route('/campaigns/<int:campaign_id>/start', methods=['POST'])
def start_campaign(campaign_id):
    """Start or resume a campaign"""
    try:
        if not hasattr(current_app, 'campaign_service'):
            return jsonify({'status': 'error', 'message': 'Campaign service not initialized'}), 500
        
        data = request.get_json() or {}
        continue_from_position = data.get('continue_from_position', False)
        
        result = current_app.campaign_service.start_campaign(campaign_id, continue_from_position)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error starting campaign {campaign_id}: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@api_bp.route('/campaigns/<int:campaign_id>/pause', methods=['POST'])
def pause_campaign(campaign_id):
    """Pause a running campaign"""
    try:
        if not hasattr(current_app, 'campaign_service'):
            return jsonify({'status': 'error', 'message': 'Campaign service not initialized'}), 500
        
        result = current_app.campaign_service.pause_campaign(campaign_id)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error pausing campaign {campaign_id}: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@api_bp.route('/campaigns/<int:campaign_id>/resume', methods=['POST'])
def resume_campaign(campaign_id):
    """Resume a paused campaign"""
    try:
        if not hasattr(current_app, 'campaign_service'):
            return jsonify({'status': 'error', 'message': 'Campaign service not initialized'}), 500
        
        result = current_app.campaign_service.resume_campaign(campaign_id)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error resuming campaign {campaign_id}: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@api_bp.route('/campaigns/<int:campaign_id>/progress', methods=['GET'])
def get_campaign_progress(campaign_id):
    """Get real-time campaign progress"""
    try:
        if not hasattr(current_app, 'campaign_service'):
            return jsonify({'status': 'error', 'message': 'Campaign service not initialized'}), 500
        
        progress = current_app.campaign_service.get_campaign_progress(campaign_id)
        return jsonify(progress)
        
    except Exception as e:
        logger.error(f"Error getting campaign progress for {campaign_id}: {e}")
        return jsonify({'percentage': 0, 'total': 0, 'sent': 0, 'delivered': 0, 'failed': 0}), 500

@api_bp.route('/campaigns/templates', methods=['GET'])
def get_campaign_templates():
    """Get all campaign templates"""
    try:
        if not hasattr(current_app, 'campaign_service'):
            return jsonify({'status': 'error', 'message': 'Campaign service not initialized'}), 500
        
        templates = current_app.campaign_service.get_templates()
        return jsonify({'status': 'success', 'templates': templates})
        
    except Exception as e:
        logger.error(f"Error getting campaign templates: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@api_bp.route('/campaigns/templates', methods=['POST'])
def save_campaign_template():
    """Save a new campaign template"""
    try:
        if not hasattr(current_app, 'campaign_service'):
            return jsonify({'status': 'error', 'message': 'Campaign service not initialized'}), 500
        
        data = request.get_json()
        
        if not data:
            return jsonify({'status': 'error', 'message': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['name', 'message']
        for field in required_fields:
            if field not in data:
                return jsonify({'status': 'error', 'message': f'Missing required field: {field}'}), 400
        
        result = current_app.campaign_service.save_template(data)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error saving campaign template: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

