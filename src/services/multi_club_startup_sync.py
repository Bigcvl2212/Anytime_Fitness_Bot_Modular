#!/usr/bin/env python3
"""
Multi-Club Startup Sync - Enhanced startup synchronization with multi-club support
"""

import logging
import time
from typing import Dict, List, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)

def enhanced_startup_sync(app, selected_clubs_override: List[str] = None, multi_club_enabled: bool = True) -> Dict[str, Any]:
    """
    Enhanced startup sync with multi-club support
    
    Args:
        app: Flask application instance
        multi_club_enabled: Whether to use multi-club synchronization
        
    Returns:
        Dict with sync results and statistics
    """
    logger.info("🚀 ENHANCED STARTUP SYNC INITIATED!")
    start_time = time.time()
    sync_results = {
        'success': False,
        'total_time': 0,
        'club_results': {},
        'combined_totals': {
            'members': 0,
            'prospects': 0,
            'training_clients': 0
        },
        'errors': []
    }
    
    try:
        # Initialize variables to avoid UnboundLocalError
        members = []
        prospects = []
        training_clients = []

        if multi_club_enabled:
            # Multi-club sync
            from src.services.multi_club_manager import multi_club_manager
            
            # Use override clubs if provided, otherwise get from manager
            if selected_clubs_override:
                logger.info(f"🎯 Using clubs from override: {selected_clubs_override}")
                multi_club_manager.set_selected_clubs(selected_clubs_override)
                selected_clubs = selected_clubs_override
            else:
                selected_clubs = multi_club_manager.get_selected_clubs()
            
            logger.info(f"🎯 Selected clubs for sync: {selected_clubs}")
            
            if not selected_clubs:
                # Auto-select default club for single-club mode
                logger.info("🔄 No clubs selected, attempting to auto-select default club...")
                try:
                    # Try to get the default club from ClubHub client
                    if hasattr(app, 'clubhub_client') and app.clubhub_client:
                        # Get available clubs from ClubHub
                        available_clubs = app.clubhub_client.get_clubs()
                        if available_clubs:
                            # Select the first available club
                            default_club = available_clubs[0]
                            club_id = default_club.get('id')
                            if club_id:
                                multi_club_manager.set_selected_clubs([club_id])
                                selected_clubs = multi_club_manager.get_selected_clubs()
                                logger.info(f"✅ Auto-selected default club: {club_id}")
                            else:
                                logger.warning("⚠️ No valid club ID found in available clubs")
                        else:
                            logger.warning("⚠️ No clubs available from ClubHub")
                    else:
                        logger.warning("⚠️ No ClubHub client available for auto-selection")
                except Exception as e:
                    logger.warning(f"⚠️ Auto-selection failed: {e}")
                
                if not selected_clubs:
                    # Fallback: Use default club ID for single-club mode
                    logger.info("🔄 Using fallback: default club ID for single-club mode")
                    try:
                        from src.services.authentication.secure_secrets_manager import SecureSecretsManager
                        secrets_manager = SecureSecretsManager()
                        # Try to get club ID from secrets or use a default
                        default_club_id = secrets_manager.get_secret('default-club-id') or '1'
                        multi_club_manager.set_selected_clubs([default_club_id])
                        selected_clubs = multi_club_manager.get_selected_clubs()
                        logger.info(f"✅ Fallback: Using default club ID: {default_club_id}")
                    except Exception as fallback_e:
                        logger.error(f"❌ Fallback auto-selection also failed: {fallback_e}")
                        return sync_results
            
            logger.info(f"🔄 Starting multi-club startup sync for {len(selected_clubs)} clubs...")
            
            # Define sync functions for each data type
            sync_functions = {
                'members': sync_members_for_club,
                'prospects': sync_prospects_for_club,
                'training_clients': sync_training_clients_for_club
            }
            
            # Get ClubHub client
            clubhub_client = app.clubhub_client
            
            # Perform multi-club sync
            combined_data = multi_club_manager.sync_multi_club_data(
                clubhub_client, sync_functions, app=app
            )
            
            # Update sync results
            sync_results['success'] = True
            sync_results['combined_totals']['members'] = len(combined_data.get('members', []))
            sync_results['combined_totals']['prospects'] = len(combined_data.get('prospects', []))
            sync_results['combined_totals']['training_clients'] = len(combined_data.get('training_clients', []))
            sync_results['club_results'] = combined_data.get('club_metadata', {})
            
            # CRITICAL FIX: Save fresh multi-club data to database
            try:
                if app and hasattr(app, 'db_manager'):
                    members_data = combined_data.get('members', [])
                    prospects_data = combined_data.get('prospects', [])
                    training_data = combined_data.get('training_clients', [])
                    
                    # Save members to database with agreement data
                    if members_data:
                        success = app.db_manager.save_members_to_db(members_data)
                        if success:
                            logger.info(f"💾 Successfully saved {len(members_data)} members with agreement data to database")
                        else:
                            logger.error(f"❌ Failed to save members to database")
                    
                    # Save prospects to database  
                    if prospects_data:
                        success = app.db_manager.save_prospects_to_db(prospects_data)
                        if success:
                            logger.info(f"💾 Successfully saved {len(prospects_data)} prospects to database")
                        else:
                            logger.error(f"❌ Failed to save prospects to database")
                    
                    # Save training clients to database
                    if training_data:
                        success = app.db_manager.save_training_clients_to_db(training_data)
                        if success:
                            logger.info(f"💾 Successfully saved {len(training_data)} training clients to database")
                        else:
                            logger.error(f"❌ Failed to save training clients to database")
                    
                    logger.info("✅ Fresh multi-club data saved to database successfully!")
                else:
                    logger.warning("⚠️ No database manager available, skipping database save")
                    
            except Exception as db_e:
                logger.error(f"❌ Multi-club database save error: {db_e}")
            
            # Cache combined data in app
            app.cached_members = combined_data.get('members', [])
            app.cached_prospects = combined_data.get('prospects', [])
            app.cached_training_clients = combined_data.get('training_clients', [])

            # Set variables for unified processing below
            members = combined_data.get('members', [])
            prospects = combined_data.get('prospects', [])
            training_clients = combined_data.get('training_clients', [])

            logger.info(f"🎉 Multi-club sync complete! Members: {len(members)}, "
                       f"Prospects: {len(prospects)}, Training Clients: {len(training_clients)}")
            
        else:
            # Single club sync (existing functionality)
            logger.info("🔄 Starting single-club startup sync...")
            
            # Use existing sync methods
            members = sync_members_for_club(app=app)
            prospects = sync_prospects_for_club(app=app)
            training_clients = sync_training_clients_for_club(app=app)
            
        sync_results['success'] = True
        sync_results['combined_totals']['members'] = len(members) if members else 0
        sync_results['combined_totals']['prospects'] = len(prospects) if prospects else 0
        sync_results['combined_totals']['training_clients'] = len(training_clients) if training_clients else 0
        
        # CRITICAL FIX: Save fresh data to database (single-club mode)
        try:
            if app and hasattr(app, 'db_manager'):
                # Save members to database with agreement data
                if members:
                    success = app.db_manager.save_members_to_db(members)
                    if success:
                        logger.info(f"💾 Successfully saved {len(members)} members with agreement data to database")
                    else:
                        logger.error(f"❌ Failed to save members to database")
                
                # Save prospects to database  
                if prospects:
                    success = app.db_manager.save_prospects_to_db(prospects)
                    if success:
                        logger.info(f"💾 Successfully saved {len(prospects)} prospects to database")
                    else:
                        logger.error(f"❌ Failed to save prospects to database")
                
                # Save training clients to database (already handled in individual sync)
                if training_clients:
                    success = app.db_manager.save_training_clients_to_db(training_clients)
                    if success:
                        logger.info(f"💾 Successfully saved {len(training_clients)} training clients to database")
                    else:
                        logger.error(f"❌ Failed to save training clients to database")
                
                logger.info("✅ Fresh data saved to database successfully!")
            else:
                logger.warning("⚠️ No database manager available, skipping database save")
                
        except Exception as db_e:
            logger.error(f"❌ Database save error: {db_e}")
        
        # Cache data in app
        app.cached_members = members or []
        app.cached_prospects = prospects or []
        app.cached_training_clients = training_clients or []

        sync_results['total_time'] = time.time() - start_time
        logger.info(f"✅ Startup sync completed in {sync_results['total_time']:.2f} seconds")
        
    except Exception as e:
        error_msg = f"Startup sync error: {e}"
        logger.error(f"❌ {error_msg}")
        sync_results['errors'].append(error_msg)
        sync_results['total_time'] = time.time() - start_time
    
    return sync_results

def sync_members_for_club(club_id: str = None, app=None) -> List[Dict[str, Any]]:
    """
    Sync members for a specific club with comprehensive agreement processing
    
    Args:
        club_id: Club ID to sync (optional for backward compatibility)
        app: Flask application instance (for accessing shared db_manager)
        
    Returns:
        List of member data with billing information
    """
    try:
        logger.info(f"📊 Syncing members for club {club_id or 'default'}...")
        
        # Import the ClubHub API client
        from src.services.api.clubhub_api_client import ClubHubAPIClient
        from src.services.authentication.secure_secrets_manager import SecureSecretsManager
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        # Get credentials from SecureSecretsManager
        secrets_manager = SecureSecretsManager()
        clubhub_email = secrets_manager.get_secret('clubhub-email')
        clubhub_password = secrets_manager.get_secret('clubhub-password')
        
        if not clubhub_email or not clubhub_password:
            logger.error(f"❌ ClubHub credentials not found in SecureSecretsManager for club {club_id}")
            return []
        
        # Create and authenticate client
        clubhub_client = ClubHubAPIClient()
        if not clubhub_client.authenticate(clubhub_email, clubhub_password):
            logger.error(f"❌ ClubHub authentication failed for club {club_id}")
            return []
        
        # Get ALL members for this specific club using pagination
        members = clubhub_client.get_all_members_paginated()
        if not members:
            logger.warning(f"⚠️ No members found for club {club_id}")
            return []
        
        logger.info(f"📊 Processing {len(members)} members with comprehensive agreement data...")
        
        def get_member_agreement_data(member_data):
            """Get agreement data for a single member (same logic as main startup sync)"""
            try:
                member_data['full_name'] = f"{member_data.get('firstName', '')} {member_data.get('lastName', '')}".strip()
                member_data['source_club_id'] = club_id
                
                member_id = member_data.get('id') or member_data.get('prospectId')
                if member_id:
                    agreement_data = clubhub_client.get_member_agreement(member_id)
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
                        elif 'agreement' in agreement_data and isinstance(agreement_data['agreement'], dict):
                            agreement = agreement_data['agreement']
                            if 'recurringCost' in agreement and isinstance(agreement['recurringCost'], dict):
                                recurring_cost = float(agreement['recurringCost'].get('total', 0)) or 0.0
                        
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
                        member_data['agreement_type'] = agreement_data.get('agreementType', 'Unknown')
                        member_data['agreement_id'] = agreement_data.get('agreementID')  # This is the key field!
                        member_data['agreement_guid'] = agreement_data.get('agreementGuid')
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
            future_to_member = {executor.submit(get_member_agreement_data, member): member for member in members}
            
            completed_count = 0
            for future in as_completed(future_to_member):
                completed_count += 1
                if completed_count % 100 == 0:
                    logger.info(f"📊 Members: {completed_count}/{len(members)} processed with agreement data...")
        
        # Log billing summary
        total_past_due = sum(m.get('amount_past_due', 0) for m in members)
        members_with_past_due = len([m for m in members if m.get('amount_past_due', 0) > 0])
        
        logger.info(f"✅ Synced {len(members)} members for club {club_id} with billing data")
        logger.info(f"💰 Billing Summary: {members_with_past_due} members with past due amounts, total: ${total_past_due:.2f}")
        
        return members
        
    except Exception as e:
        logger.error(f"❌ Error syncing members for club {club_id}: {e}")
        return []

def sync_prospects_for_club(club_id: str = None, app=None) -> List[Dict[str, Any]]:
    """
    Sync prospects for a specific club
    
    Args:
        club_id: Club ID to sync (optional for backward compatibility)
        app: Flask application instance (for accessing shared db_manager)
        
    Returns:
        List of prospect data
    """
    try:
        logger.info(f"📊 Syncing prospects for club {club_id or 'default'}...")
        
        # Import the ClubHub API client
        from src.services.api.clubhub_api_client import ClubHubAPIClient
        from src.services.authentication.secure_secrets_manager import SecureSecretsManager
        
        # Get credentials from SecureSecretsManager
        secrets_manager = SecureSecretsManager()
        clubhub_email = secrets_manager.get_secret('clubhub-email')
        clubhub_password = secrets_manager.get_secret('clubhub-password')
        
        if not clubhub_email or not clubhub_password:
            logger.error(f"❌ ClubHub credentials not found in SecureSecretsManager for club {club_id}")
            return []
        
        # Create and authenticate client
        clubhub_client = ClubHubAPIClient()
        if not clubhub_client.authenticate(clubhub_email, clubhub_password):
            logger.error(f"❌ ClubHub authentication failed for club {club_id}")
            return []
        
        # Get ALL prospects for this specific club using pagination
        prospects = clubhub_client.get_all_prospects_paginated()
        if not prospects:
            logger.warning(f"⚠️ No prospects found for club {club_id}")
            return []
        
        # Process prospects to add full_name and club context
        for prospect in prospects:
            prospect['full_name'] = f"{prospect.get('firstName', '')} {prospect.get('lastName', '')}".strip()
            prospect['source_club_id'] = club_id
            
        logger.info(f"✅ Synced {len(prospects)} prospects for club {club_id}")
        return prospects
        
    except Exception as e:
        logger.error(f"❌ Error syncing prospects for club {club_id}: {e}")
        return []

def sync_training_clients_for_club(club_id: str = None, app=None) -> List[Dict[str, Any]]:
    """
    Sync training clients for a specific club
    
    Args:
        club_id: Club ID to sync (optional for backward compatibility)
        app: Flask application instance (for accessing shared db_manager)
        
    Returns:
        List of training client data
    """
    try:
        logger.info(f"📊 Syncing training clients for club {club_id or 'default'}...")
        
        # For training clients, we'll use ClubOS integration since it's specific to training
        # This would need to be adapted based on how training clients are accessed per club
        
        # Import ClubOS integration (this might need club-specific configuration)
        try:
            import sys, os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            from src.services.clubos_integration import ClubOSIntegration
            
            clubos = ClubOSIntegration()
            training_clients = clubos.get_training_clients()
            
            if training_clients:
                # Add club context to training clients
                for client in training_clients:
                    if 'source_club_id' not in client:
                        client['source_club_id'] = club_id
                        client['source_club_name'] = f'Club {club_id}'
                
                # CRITICAL FIX: Save training clients to database using shared app.db_manager
                try:
                    if app and hasattr(app, 'db_manager'):
                        # Use the shared database manager from the app (configured for PostgreSQL)
                        success = app.db_manager.save_training_clients_to_db(training_clients)
                        
                        if success:
                            logger.info(f"💾 Successfully saved {len(training_clients)} training clients to PostgreSQL database")
                        else:
                            logger.error(f"❌ Failed to save training clients to database")
                    else:
                        # Fallback to local database manager if app not provided (backward compatibility)
                        logger.warning("⚠️ No shared db_manager available, using local DatabaseManager")
                        from src.services.database_manager import DatabaseManager
                        db_manager = DatabaseManager()
                        success = db_manager.save_training_clients_to_db(training_clients)
                        
                        if success:
                            logger.info(f"💾 Successfully saved {len(training_clients)} training clients with local db manager")
                        else:
                            logger.error(f"❌ Failed to save training clients to database")
                        
                except Exception as db_e:
                    logger.error(f"❌ Database save error for training clients: {db_e}")
                
                logger.info(f"✅ Synced {len(training_clients)} training clients for club {club_id}")
                return training_clients
            else:
                logger.warning(f"⚠️ No training clients found for club {club_id}")
                return []
                
        except Exception as e:
            logger.warning(f"⚠️ ClubOS integration not available for club {club_id}: {e}")
            return []
        
    except Exception as e:
        logger.error(f"❌ Error syncing training clients for club {club_id}: {e}")
        return []

def get_multi_club_summary(app) -> Dict[str, Any]:
    """
    Get summary statistics across all clubs
    
    Args:
        app: Flask application instance
        
    Returns:
        Dict with multi-club summary statistics
    """
    try:
        from src.services.multi_club_manager import multi_club_manager
        
        # Get cached data
        members = getattr(app, 'cached_members', [])
        prospects = getattr(app, 'cached_prospects', [])
        training_clients = getattr(app, 'cached_training_clients', [])
        
        # Calculate breakdowns by club
        member_breakdown = multi_club_manager.get_club_breakdown(members)
        prospect_breakdown = multi_club_manager.get_club_breakdown(prospects)
        training_breakdown = multi_club_manager.get_club_breakdown(training_clients)
        
        return {
            'total_members': len(members),
            'total_prospects': len(prospects),
            'total_training_clients': len(training_clients),
            'member_breakdown': member_breakdown,
            'prospect_breakdown': prospect_breakdown,
            'training_breakdown': training_breakdown,
            'selected_clubs': multi_club_manager.get_selected_clubs(),
            'club_names': [multi_club_manager.get_club_name(club_id) 
                          for club_id in multi_club_manager.get_selected_clubs()]
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting multi-club summary: {e}")
        return {
            'total_members': 0,
            'total_prospects': 0,
            'total_training_clients': 0,
            'member_breakdown': {},
            'prospect_breakdown': {},
            'training_breakdown': {},
            'selected_clubs': [],
            'club_names': []
        }
