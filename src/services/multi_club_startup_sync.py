#!/usr/bin/env python3
"""
Multi-Club Startup Sync - Enhanced startup synchronization with multi-club support
"""

import logging
import time
from typing import Dict, List, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)

def enhanced_startup_sync(app, selected_clubs_override: List[str] = None, multi_club_enabled: bool = True, manager_id: str = None) -> Dict[str, Any]:
    """
    Enhanced startup sync with multi-club support

    Args:
        app: Flask application instance
        selected_clubs_override: List of club IDs to sync
        multi_club_enabled: Whether to use multi-club synchronization
        manager_id: Manager ID for credential retrieval

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
            # Order: prospects FIRST (needed for member addresses), then members, then training clients
            sync_functions = {
                'prospects': sync_prospects_for_club,
                'members': sync_members_for_club,
                'training_clients': sync_training_clients_for_club,
                'messages': sync_messages_for_club,
                'sessions': sync_sessions_for_club
            }
            
            # Get ClubHub client
            clubhub_client = app.clubhub_client
            
            # Perform multi-club sync
            combined_data = multi_club_manager.sync_multi_club_data(
                clubhub_client, sync_functions, app=app, manager_id=manager_id
            )
            
            # Update sync results
            sync_results['success'] = True
            sync_results['combined_totals']['members'] = len(combined_data.get('members', []))
            sync_results['combined_totals']['prospects'] = len(combined_data.get('prospects', []))
            sync_results['combined_totals']['training_clients'] = len(combined_data.get('training_clients', []))
            sync_results['combined_totals']['messages'] = len(combined_data.get('messages', []))
            sync_results['combined_totals']['sessions'] = len(combined_data.get('sessions', []))
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

                    # Save messages to database
                    messages_data = combined_data.get('messages', [])
                    if messages_data:
                        # Use the store_messages_in_database function from messaging.py
                        from src.routes.messaging import store_messages_in_database
                        stored_count = store_messages_in_database(messages_data, owner_id='187032782')  # TODO: Make owner_id dynamic
                        if stored_count > 0:
                            logger.info(f"💾 Successfully saved {stored_count} messages to database")
                        else:
                            logger.error(f"❌ Failed to save messages to database")

                    # Cache calendar sessions in app
                    sessions_data = combined_data.get('sessions', [])
                    if sessions_data:
                        app.cached_calendar_events = sessions_data
                        logger.info(f"📅 Successfully cached {len(sessions_data)} calendar events")

                    logger.info("✅ Fresh multi-club data saved to database successfully!")
                else:
                    logger.warning("⚠️ No database manager available, skipping database save")
                    
            except Exception as db_e:
                logger.error(f"❌ Multi-club database save error: {db_e}")
            
            # Cache combined data in app
            app.cached_members = combined_data.get('members', [])
            app.cached_prospects = combined_data.get('prospects', [])
            app.cached_training_clients = combined_data.get('training_clients', [])
            app.cached_messages = combined_data.get('messages', [])
            if combined_data.get('sessions'):
                app.cached_calendar_events = combined_data.get('sessions', [])

            # Set variables for unified processing below
            members = combined_data.get('members', [])
            prospects = combined_data.get('prospects', [])
            training_clients = combined_data.get('training_clients', [])
            messages = combined_data.get('messages', [])
            sessions = combined_data.get('sessions', [])

            logger.info(f"🎉 Multi-club sync complete! Members: {len(members)}, "
                       f"Prospects: {len(prospects)}, Training Clients: {len(training_clients)}, "
                       f"Messages: {len(messages)}, Sessions: {len(sessions)}")
            
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

def sync_members_for_club(club_id: str = None, app=None, manager_id: str = None) -> List[Dict[str, Any]]:
    """
    Sync members for a specific club with comprehensive agreement processing

    Args:
        club_id: Club ID to sync (optional for backward compatibility)
        app: Flask application instance (for accessing shared db_manager)
        manager_id: Manager ID for credential retrieval

    Returns:
        List of member data with billing information
    """
    try:
        logger.info(f"📊 Syncing members for club {club_id or 'default'}...")

        # Import the ClubHub API client
        from src.services.api.clubhub_api_client import ClubHubAPIClient
        from src.services.authentication.secure_secrets_manager import SecureSecretsManager
        from concurrent.futures import ThreadPoolExecutor, as_completed
        import os

        # Get credentials from SecureSecretsManager using manager_id
        secrets_manager = SecureSecretsManager()
        clubhub_email = None
        clubhub_password = None

        # Get credentials using manager_id if provided
        if manager_id:
            credentials = secrets_manager.get_credentials(manager_id)
            if credentials and credentials.get('clubhub_email') and credentials.get('clubhub_password'):
                clubhub_email = credentials.get('clubhub_email')
                clubhub_password = credentials.get('clubhub_password')
                logger.info(f"✅ Using database credentials for ClubHub (manager: {manager_id})")
            else:
                logger.warning(f"⚠️ Database credentials not available for manager {manager_id}, trying env vars...")

        # Fallback to environment variables if database credentials not available
        if not clubhub_email or not clubhub_password:
            clubhub_email = os.getenv('CLUBHUB_EMAIL')
            clubhub_password = os.getenv('CLUBHUB_PASSWORD')
            if clubhub_email and clubhub_password:
                logger.info("✅ Using environment variable credentials for ClubHub")
            else:
                # Last resort: legacy secret retrieval
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

        # Get prospects for address data - check database first to avoid duplicate fetch
        logger.info(f"📍 Getting prospect address data...")

        # Try to read from database first (prospects might have been synced already)
        try:
            db_prospects = app.db_manager.execute_query(
                "SELECT prospect_id, address, city, state, zip_code, phone, mobile_phone, email FROM prospects",
                fetch_all=True
            )
            if db_prospects and len(db_prospects) > 0:
                logger.info(f"📊 Using {len(db_prospects)} prospects from database for address lookup")
                prospects = [dict(row) for row in db_prospects]
            else:
                logger.info(f"📍 No prospects in database yet, fetching from ClubHub API...")
                prospects = clubhub_client.get_all_prospects_paginated()
        except Exception as e:
            logger.warning(f"⚠️ Could not read prospects from database: {e}, fetching from API...")
            prospects = clubhub_client.get_all_prospects_paginated()

        # Create address lookup by prospect ID
        address_lookup = {}
        if prospects:
            for prospect in prospects:
                # Handle both API field names and database column names
                prospect_id = str(
                    prospect.get('id') or
                    prospect.get('prospectId') or
                    prospect.get('prospect_id')
                )
                if prospect_id:
                    address_lookup[prospect_id] = {
                        'address': (
                            prospect.get('address') or
                            prospect.get('address1') or
                            prospect.get('streetAddress')
                        ),
                        'city': prospect.get('city'),
                        'state': prospect.get('state'),
                        'zip_code': (
                            prospect.get('zip_code') or
                            prospect.get('zip') or
                            prospect.get('zipCode') or
                            prospect.get('postalCode')
                        ),
                        'phone': (
                            prospect.get('phone') or
                            prospect.get('homePhone') or
                            prospect.get('phoneNumber')
                        ),
                        'mobile_phone': (
                            prospect.get('mobile_phone') or
                            prospect.get('mobilePhone') or
                            prospect.get('mobile')
                        ),
                        'email': prospect.get('email')
                    }
            logger.info(f"📊 Built address lookup from {len(address_lookup)} prospects")

        logger.info(f"📊 Processing {len(members)} members with comprehensive agreement data...")
        
        def get_member_agreement_data(member_data):
            """Get agreement data for a single member (contact info already in member_data)"""
            try:
                member_data['full_name'] = f"{member_data.get('firstName', '')} {member_data.get('lastName', '')}".strip()
                member_data['source_club_id'] = club_id

                # Get prospect ID first
                member_data['prospect_id'] = str(member_data.get('id') or member_data.get('prospectId'))
                prospect_id = member_data['prospect_id']

                # Extract contact information from member data first
                member_data['first_name'] = member_data.get('firstName')
                member_data['last_name'] = member_data.get('lastName')
                member_data['address'] = member_data.get('address1') or member_data.get('address') or member_data.get('streetAddress')
                member_data['city'] = member_data.get('city')
                member_data['state'] = member_data.get('state')
                member_data['zip_code'] = member_data.get('zip') or member_data.get('zipCode') or member_data.get('postalCode')
                member_data['phone'] = member_data.get('homePhone') or member_data.get('phone') or member_data.get('phoneNumber')
                member_data['mobile_phone'] = member_data.get('mobilePhone') or member_data.get('mobile')
                member_data['email'] = member_data.get('email')

                # Enhance with prospect data if available (prospects have full address info)
                if prospect_id in address_lookup:
                    prospect_data = address_lookup[prospect_id]
                    # Only override if member data doesn't have it
                    if not member_data.get('address'):
                        member_data['address'] = prospect_data.get('address')
                    if not member_data.get('city'):
                        member_data['city'] = prospect_data.get('city')
                    if not member_data.get('state'):
                        member_data['state'] = prospect_data.get('state')
                    if not member_data.get('zip_code'):
                        member_data['zip_code'] = prospect_data.get('zip_code')
                    if not member_data.get('phone'):
                        member_data['phone'] = prospect_data.get('phone')
                    if not member_data.get('mobile_phone'):
                        member_data['mobile_phone'] = prospect_data.get('mobile_phone')
                    if not member_data.get('email'):
                        member_data['email'] = prospect_data.get('email')

                member_id = member_data.get('id') or member_data.get('prospectId')
                if member_id:
                    # Get agreement data for billing information
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

                            # Calculate billing breakdown - BREAK DOWN the total into base + fees
                            # The total_amount_past_due from API is what member owes (INCLUDING any late fees)
                            # We need to calculate: base amount, late fees, and missed payments

                            # Calculate missed payments from past due amount
                            missed_payments = max(1, int(total_amount_past_due / recurring_cost))

                            # Calculate late fees ($19.50 per missed payment)
                            late_fees = missed_payments * 19.50

                            # Base amount is total MINUS calculated late fees
                            base_amount = max(0, total_amount_past_due - late_fees)

                            # Store the breakdown
                            member_data['amount_past_due'] = total_amount_past_due  # Total owed (from API)
                            member_data['base_amount_past_due'] = base_amount  # Base dues owed
                            member_data['late_fees'] = late_fees  # Late fees portion
                            member_data['missed_payments'] = missed_payments  # Number of missed payments
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

def sync_prospects_for_club(club_id: str = None, app=None, manager_id: str = None) -> List[Dict[str, Any]]:
    """
    Sync prospects for a specific club

    Args:
        club_id: Club ID to sync (optional for backward compatibility)
        app: Flask application instance (for accessing shared db_manager)
        manager_id: Manager ID for credential retrieval

    Returns:
        List of prospect data
    """
    try:
        logger.info(f"📊 Syncing prospects for club {club_id or 'default'}...")

        # Import the ClubHub API client
        from src.services.api.clubhub_api_client import ClubHubAPIClient
        from src.services.authentication.secure_secrets_manager import SecureSecretsManager
        import os

        # Get credentials from SecureSecretsManager using manager_id
        secrets_manager = SecureSecretsManager()
        clubhub_email = None
        clubhub_password = None

        # Get credentials using manager_id if provided
        if manager_id:
            credentials = secrets_manager.get_credentials(manager_id)
            if credentials and credentials.get('clubhub_email') and credentials.get('clubhub_password'):
                clubhub_email = credentials.get('clubhub_email')
                clubhub_password = credentials.get('clubhub_password')
                logger.info(f"✅ Using database credentials for ClubHub prospects (manager: {manager_id})")
            else:
                logger.warning(f"⚠️ Database credentials not available for manager {manager_id}, trying env vars...")

        # Fallback to environment variables if database credentials not available
        if not clubhub_email or not clubhub_password:
            clubhub_email = os.getenv('CLUBHUB_EMAIL')
            clubhub_password = os.getenv('CLUBHUB_PASSWORD')
            if clubhub_email and clubhub_password:
                logger.info("✅ Using environment variable credentials for ClubHub prospects")
            else:
                # Last resort: legacy secret retrieval
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

def sync_training_clients_for_club(club_id: str = None, app=None, manager_id: str = None) -> List[Dict[str, Any]]:
    """
    Sync training clients for a specific club

    Args:
        club_id: Club ID to sync (optional for backward compatibility)
        app: Flask application instance (for accessing shared db_manager)
        manager_id: Manager ID for credential retrieval

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
            from src.services.api.clubhub_api_client import ClubHubAPIClient
            from src.services.authentication.secure_secrets_manager import SecureSecretsManager

            # CRITICAL FIX: Use app.clubos to avoid duplicate authentication
            if app and hasattr(app, 'clubos'):
                clubos = app.clubos
                logger.info("✅ Using shared ClubOS session from app (no duplicate auth)")
            else:
                clubos = ClubOSIntegration()
                logger.warning("⚠️ Creating new ClubOSIntegration instance (app.clubos not available)")

            training_clients = clubos.get_training_clients()

            if training_clients:
                # Enhance training clients with address data from members database
                logger.info(f"📍 Enhancing {len(training_clients)} training clients with address data from members database...")

                # Get database manager
                from src.services.database_manager import DatabaseManager
                db_manager = DatabaseManager()

                # Get all members with addresses from database
                members_query = """
                    SELECT prospect_id, address, city, state, zip_code, mobile_phone, email, phone
                    FROM members
                    WHERE prospect_id IS NOT NULL
                """
                members_rows = db_manager.execute_query(members_query, fetch_all=True)

                # Create lookup dictionary by prospect_id
                members_lookup = {}
                for row in members_rows:
                    member_dict = dict(row) if hasattr(row, 'keys') else row
                    prospect_id = str(member_dict.get('prospect_id', ''))
                    if prospect_id:
                        members_lookup[prospect_id] = member_dict

                logger.info(f"📊 Found {len(members_lookup)} members with IDs for matching")

                # Match training clients to members and copy address data
                matched_count = 0
                for client in training_clients:
                    try:
                        # Try multiple ID fields to match
                        member_id = client.get('clubos_member_id') or client.get('member_id') or client.get('prospect_id')
                        if member_id:
                            member_id = str(member_id)

                            # Look up member in our database
                            if member_id in members_lookup:
                                member_data = members_lookup[member_id]

                                # Copy address data from member to training client
                                client['address'] = member_data.get('address')
                                client['city'] = member_data.get('city')
                                client['state'] = member_data.get('state')
                                client['zip_code'] = member_data.get('zip_code')
                                client['mobile_phone'] = client.get('mobile_phone') or member_data.get('mobile_phone') or member_data.get('phone')
                                client['email'] = client.get('email') or member_data.get('email')

                                # Set prospect_id if not already set
                                if not client.get('prospect_id'):
                                    client['prospect_id'] = member_id

                                matched_count += 1
                    except Exception as e:
                        logger.debug(f"⚠️ Could not match training client {client.get('member_name')}: {e}")

                logger.info(f"✅ Enhanced {matched_count}/{len(training_clients)} training clients with address data from database")

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

def sync_messages_for_club(club_id: str = None, app=None, manager_id: str = None) -> List[Dict[str, Any]]:
    """
    Sync initial inbox messages (last 30 days) from ClubOS

    Args:
        club_id: Club ID to sync (optional for backward compatibility)
        app: Flask application instance (for accessing messaging_client)
        manager_id: Manager ID for credential retrieval

    Returns:
        List of message data
    """
    try:
        logger.info(f"💬 Syncing messages for club {club_id or 'default'}...")

        # Get ClubOS messaging client from app
        if not hasattr(app, 'messaging_client') or not app.messaging_client:
            logger.warning("⚠️ ClubOS messaging client not available - skipping message sync")
            return []

        messaging_client = app.messaging_client

        # Get logged in user's owner_id
        if not hasattr(messaging_client, 'logged_in_user_id') or not messaging_client.logged_in_user_id:
            logger.warning("⚠️ ClubOS messaging client not authenticated - skipping message sync")
            return []

        owner_id = messaging_client.logged_in_user_id

        # Get messages from ClubOS
        try:
            messages = messaging_client.get_messages(owner_id=owner_id)
            if not messages:
                logger.info("📭 No messages found in ClubOS inbox")
                return []
        except Exception as api_error:
            logger.error(f"❌ Error fetching messages from ClubOS: {api_error}")
            return []

        # Filter to last 30 days to avoid loading too much data
        from datetime import datetime, timedelta
        cutoff_date = datetime.now() - timedelta(days=30)

        recent_messages = []
        for msg in messages:
            try:
                # Parse timestamp
                msg_timestamp = msg.get('timestamp', '')
                if msg_timestamp:
                    # Try to parse various date formats
                    msg_date = None
                    for fmt in ['%m/%d/%Y %I:%M %p', '%Y-%m-%d %H:%M:%S', '%m/%d/%y %I:%M %p']:
                        try:
                            msg_date = datetime.strptime(msg_timestamp, fmt)
                            break
                        except:
                            continue

                    # Skip if message is older than 30 days
                    if msg_date and msg_date < cutoff_date:
                        continue

                recent_messages.append(msg)
            except Exception as filter_error:
                # Include message if we can't parse date (better to have extra than miss some)
                recent_messages.append(msg)
                logger.debug(f"⚠️ Could not filter message by date: {filter_error}")

        logger.info(f"✅ Synced {len(recent_messages)} messages from last 30 days (out of {len(messages)} total)")
        return recent_messages

    except Exception as e:
        logger.error(f"❌ Error syncing messages for club {club_id}: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return []

def sync_sessions_for_club(club_id: str = None, app=None, manager_id: str = None) -> List[Dict[str, Any]]:
    """
    Sync today's and upcoming PT sessions/calendar events

    Args:
        club_id: Club ID to sync (optional for backward compatibility)
        app: Flask application instance
        manager_id: Manager ID for credential retrieval

    Returns:
        List of calendar session data
    """
    try:
        logger.info(f"📅 Syncing calendar sessions for club {club_id or 'default'}...")

        # Import ClubOS integration
        try:
            from src.services.clubos_integration import ClubOSIntegration
        except ImportError:
            from services.clubos_integration import ClubOSIntegration

        # CRITICAL FIX: Use app.clubos to avoid duplicate authentication
        if app and hasattr(app, 'clubos'):
            clubos = app.clubos
            logger.info("✅ Using shared ClubOS session from app (no duplicate auth)")

            # Check if already authenticated
            if not clubos.authenticated:
                logger.warning("⚠️ ClubOS not authenticated - skipping session sync")
                return []
        else:
            # Fallback: Create new instance if app not available
            logger.warning("⚠️ Creating new ClubOSIntegration instance (app.clubos not available)")
            clubos = ClubOSIntegration()

            # Authenticate
            if not clubos.authenticate():
                logger.warning("⚠️ ClubOS authentication failed - skipping session sync")
                return []

        # Get calendar events for next 30 days
        try:
            sessions = clubos.api.get_current_calendar_events(limit=50)
            if not sessions:
                logger.info("📭 No calendar sessions found")
                return []

            logger.info(f"✅ Synced {len(sessions)} calendar sessions for next 30 days")
            return sessions

        except Exception as api_error:
            logger.error(f"❌ Error fetching calendar sessions from ClubOS: {api_error}")
            return []

    except Exception as e:
        logger.error(f"❌ Error syncing sessions for club {club_id}: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return []
