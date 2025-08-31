#!/usr/bin/env python3
"""
Clean Anytime Fitness Dashboard - Main Application
Main entry point for the Flask application
"""

import os
import sys
import logging
import threading
import time
from flask import Flask

# Add src to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import database and ClubOS integration
from .services.database_manager import DatabaseManager
from .services.clubos_integration import ClubOSIntegration

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from flask import Flask
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Import configuration and services
from .config.settings import create_app_config
from .services.database_manager import DatabaseManager
from .services.training_package_cache import TrainingPackageCache
from .services.clubos_integration import ClubOSIntegration
from .routes import register_blueprints

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure console streams can handle UTF-8 (Windows cp1252 workaround)
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

# File logging for debugging - disabled to avoid Windows file locking issues
try:
    log_dir = 'logs'
    os.makedirs(log_dir, exist_ok=True)
    logger.info('Log directory created, but file logging disabled to avoid Windows lock issues')
except Exception as e:
    logger.warning(f'Could not create log directory: {e}')

def create_app():
    """Application factory pattern for creating Flask app"""
    app = Flask(__name__, 
                template_folder='../templates', 
                static_folder='../static')
    
    # Configure the app
    create_app_config(app)
    
    # Create templates directory if it doesn't exist
    templates_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')
    if not os.path.exists(templates_dir):
        os.makedirs(templates_dir)
    
    # Initialize services
    with app.app_context():
        # Initialize database manager
        app.db_manager = DatabaseManager()
        
        # Initialize training package cache
        app.training_package_cache = TrainingPackageCache()
        
        # Initialize ClubOS Integration
        app.clubos = ClubOSIntegration()
        
        # Initialize ClubOS Messaging Client
        try:
            from services.clubos_messaging_client import ClubOSMessagingClient
            from config.secrets_local import get_secret
            
            username = get_secret('clubos-username')
            password = get_secret('clubos-password')
            
            if username and password:
                app.messaging_client = ClubOSMessagingClient(username, password)
                logger.info("✅ ClubOS messaging client initialized")
            else:
                app.messaging_client = None
                logger.warning("⚠️ ClubOS messaging client not initialized - credentials missing")
        except Exception as e:
            app.messaging_client = None
            logger.warning(f"⚠️ ClubOS messaging client initialization failed: {e}")
        
        # Initialize global status tracking
        app.data_refresh_status = {
            'is_running': False,
            'started_at': None,
            'completed_at': None,
            'progress': 0,
            'status': 'idle',
            'message': 'No refresh in progress',
            'error': None
        }
        
        # Initialize data cache for persistence between page navigations
        app.data_cache = {
            'messages': [],
            'members': [],
            'prospects': [],
            'training_clients': [],
            'last_sync': {},
            'cache_timestamp': datetime.now().isoformat()
        }
        
        app.bulk_checkin_status = {
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
        
        logger.info("✅ All services initialized successfully")
        
        # Kick off startup sync in a background thread so app doesn't block
        try:
            threading.Thread(target=startup_sync, args=(app,), daemon=True).start()
            logger.info("🔄 Startup sync launched in background thread")
        except Exception as e:
            logger.warning(f"⚠️ Could not start background startup sync: {e}")
    
    # Register blueprints
    register_blueprints(app)
    
    return app

def startup_sync(app):
    """Perform initial data sync on startup - OPTIMIZED with parallel processing"""
    logger.info("🚀 Starting OPTIMIZED initial data sync on startup...")
    
    try:
        # Import all required modules once at the start
        from services.api.clubhub_api_client import ClubHubAPIClient
        from config.clubhub_credentials import CLUBHUB_EMAIL, CLUBHUB_PASSWORD
        from concurrent.futures import ThreadPoolExecutor, as_completed
        import threading
        
        # Initialize single ClubHub client and authenticate once
        logger.info("🔐 Authenticating with ClubHub API...")
        clubhub_client = ClubHubAPIClient()
        if not clubhub_client.authenticate(CLUBHUB_EMAIL, CLUBHUB_PASSWORD):
            logger.error("❌ ClubHub authentication failed - cannot proceed with sync")
            return
        logger.info("✅ ClubHub authentication successful")
        
        # PARALLEL SYNC: Start all major sync operations simultaneously
        logger.info("⚡ Starting parallel sync operations...")
        
        # 1. Messages sync (if available)
        messages = None
        if app.messaging_client:
            try:
                logger.info("📨 Syncing messages...")
                messages = app.messaging_client.sync_messages('187032782')
                if messages:
                    app.data_cache['messages'] = messages
                    app.data_cache['last_sync']['messages'] = datetime.now().isoformat()
                    logger.info(f"✅ Messages: {len(messages)} synced")
                else:
                    logger.warning("⚠️ No messages found")
            except Exception as e:
                logger.error(f"❌ Messages sync failed: {e}")
        
        # 2. Prospects sync (parallel with other operations)
        logger.info("🔍 Fetching prospects from ClubHub...")
        prospects = clubhub_client.get_all_prospects_paginated()
        if prospects:
            # Process prospects in parallel
            logger.info(f"📊 Processing {len(prospects)} prospects...")
            
            def process_prospect(prospect):
                prospect['full_name'] = f"{prospect.get('firstName', '')} {prospect.get('lastName', '')}".strip()
                return prospect
            
            with ThreadPoolExecutor(max_workers=20) as executor:
                prospects = list(executor.map(process_prospect, prospects))
            
            app.data_cache['prospects'] = prospects
            app.data_cache['last_sync']['prospects'] = datetime.now().isoformat()
            logger.info(f"✅ Prospects: {len(prospects)} processed and cached")
            
            # Save prospects to database
            try:
                app.db_manager.save_prospects_to_db(prospects)
                logger.info(f"✅ Prospects: {len(prospects)} saved to database")
            except Exception as db_e:
                logger.warning(f"⚠️ Could not save prospects to database: {db_e}")
        else:
            logger.warning("⚠️ No prospects returned from ClubHub API")
        
        # 3. Members sync with parallel agreement data processing
        logger.info("👥 Fetching members from ClubHub...")
        members = clubhub_client.get_all_members_paginated()
        logger.info(f"🔍 Members API response: {type(members)} - {len(members) if members else 'None'}")
        if members:
            logger.info(f"📊 Found {len(members)} members, processing agreement data in parallel...")
            
            def get_member_agreement_data(member_data):
                """Get agreement data for a single member (thread-safe)"""
                try:
                    member_data['full_name'] = f"{member_data.get('firstName', '')} {member_data.get('lastName', '')}".strip()
                    
                    member_id = member_data.get('id') or member_data.get('prospectId')
                    if member_id:
                        # Use shared authenticated client (thread-safe for read operations)
                        agreement_data = clubhub_client.get_member_agreement(member_id)
                        if agreement_data and isinstance(agreement_data, dict):
                            # DEBUG: Log the actual structure we're getting
                            if member_data.get('full_name') in ['Miguel Belmontes', 'DALE ROEN']:
                                logger.info(f"🔍 DEBUG - Agreement data structure for {member_data['full_name']}: {agreement_data}")
                                logger.info(f"🔍 DEBUG - Available keys: {list(agreement_data.keys())}")
                                if 'recurringCost' in agreement_data:
                                    logger.info(f"🔍 DEBUG - recurringCost: {agreement_data['recurringCost']}")
                                if 'agreement' in agreement_data:
                                    logger.info(f"🔍 DEBUG - agreement: {agreement_data['agreement']}")
                            
                            # Get the TOTAL past due amount from API (this includes late fees already)
                            total_amount_past_due = float(agreement_data.get('amountPastDue', 0))
                            
                            # Now we need to BREAK DOWN this total into base amount and late fees
                            late_fees = 0.0
                            missed_payments = 0
                            base_amount = 0.0
                            
                            # Get recurring cost from agreement data (regardless of base_amount)
                            recurring_cost = 0.0
                            
                            # Try the most common ClubHub field names first
                            if 'monthlyDues' in agreement_data and agreement_data['monthlyDues']:
                                recurring_cost = float(agreement_data['monthlyDues']) or 0.0
                                logger.info(f"💰 Found monthlyDues for {member_data['full_name']}: ${recurring_cost:.2f}")
                            elif 'amountOfNextPayment' in agreement_data and agreement_data['amountOfNextPayment']:
                                recurring_cost = float(agreement_data['amountOfNextPayment']) or 0.0
                                logger.info(f"💰 Found amountOfNextPayment for {member_data['full_name']}: ${recurring_cost:.2f}")
                            elif 'renewalRate' in agreement_data and agreement_data['renewalRate']:
                                recurring_cost = float(agreement_data['renewalRate']) or 0.0
                                logger.info(f"💰 Found renewalRate for {member_data['full_name']}: ${recurring_cost:.2f}")
                            elif 'monthlyRate' in agreement_data and agreement_data['monthlyRate']:
                                recurring_cost = float(agreement_data['monthlyRate']) or 0.0
                                logger.info(f"💰 Found monthlyRate for {member_data['full_name']}: ${recurring_cost:.2f}")
                            elif 'recurringCost' in agreement_data and isinstance(agreement_data['recurringCost'], dict):
                                recurring_cost = float(agreement_data['recurringCost'].get('total', 0)) or 0.0
                                logger.info(f"💰 Found recurringCost.total for {member_data['full_name']}: ${recurring_cost:.2f}")
                            elif 'agreement' in agreement_data and isinstance(agreement_data['agreement'], dict):
                                # Handle nested agreement structure
                                agreement = agreement_data['agreement']
                                if 'recurringCost' in agreement and isinstance(agreement['recurringCost'], dict):
                                    recurring_cost = float(agreement['recurringCost'].get('total', 0)) or 0.0
                                    if member_data.get('full_name') in ['Miguel Belmontes', 'DALE ROEN']:
                                        logger.info(f"🔍 DEBUG - Found recurringCost in nested agreement: {recurring_cost}")
                                elif 'recurring_cost' in agreement:
                                    recurring_cost = float(agreement['recurring_cost']) or 0.0
                                    if member_data.get('full_name') in ['Miguel Belmontes', 'DALE ROEN']:
                                        logger.info(f"🔍 DEBUG - Found recurring_cost in nested agreement: {recurring_cost}")
                                elif 'monthlyRate' in agreement:
                                    recurring_cost = float(agreement['monthlyRate']) or 0.0
                                    if member_data.get('full_name') in ['Miguel Belmontes', 'DALE ROEN']:
                                        logger.info(f"🔍 DEBUG - Found monthlyRate in nested agreement: {recurring_cost}")
                                elif 'monthly_rate' in agreement:
                                    recurring_cost = float(agreement['monthly_rate']) or 0.0
                                    if member_data.get('full_name') in ['Miguel Belmontes', 'DALE ROEN']:
                                        logger.info(f"🔍 DEBUG - Found monthly_rate in nested agreement: {recurring_cost}")
                            
                            # Check contracts array for recurring cost if main fields are 0.0
                            if recurring_cost == 0.0 and 'contracts' in agreement_data and isinstance(agreement_data['contracts'], list):
                                for contract in agreement_data['contracts']:
                                    if isinstance(contract, dict):
                                        # Check contract recurringCost
                                        if 'recurringCost' in contract and isinstance(contract['recurringCost'], dict):
                                            contract_recurring = float(contract['recurringCost'].get('total', 0)) or 0.0
                                            if contract_recurring > 0:
                                                recurring_cost = contract_recurring
                                                if member_data.get('full_name') in ['Miguel Belmontes', 'DALE ROEN']:
                                                    logger.info(f"🔍 DEBUG - Found recurringCost in contract: {recurring_cost}")
                                                break
                                        # Check contract monthlyDues
                                        elif 'monthlyDues' in contract and contract['monthlyDues'] > 0:
                                            recurring_cost = float(contract['monthlyDues'])
                                            if member_data.get('full_name') in ['Miguel Belmontes', 'DALE ROEN']:
                                                logger.info(f"🔍 DEBUG - Found monthlyDues in contract: {recurring_cost}")
                                            break
                            
                            # Check if this is a Comp Member BEFORE trying fallback recurring costs
                            is_comp_member = (
                                str(agreement_data.get('statusMessage', '')).lower().startswith('comp') or
                                str(agreement_data.get('status_message', '')).lower().startswith('comp') or
                                str(member_data.get('user_type', '')).lower() == 'comp' or
                                str(member_data.get('status', '')).lower() == 'comp' or
                                (agreement_data.get('contracts') and 
                                 any(str(contract.get('contractType', {}).get('name', '')).lower().startswith('complimentary') 
                                     for contract in agreement_data['contracts'] if isinstance(contract, dict)))
                            )
                            
                            # Only try fallback recurring costs if NOT a Comp Member
                            if recurring_cost == 0.0 and not is_comp_member:
                                # Try amountOfNextPayment first (often has the monthly rate)
                                if agreement_data.get('amountOfNextPayment') and agreement_data['amountOfNextPayment'] > 0:
                                    recurring_cost = float(agreement_data['amountOfNextPayment'])
                                    if member_data.get('full_name') in ['Miguel Belmontes', 'DALE ROEN']:
                                        logger.info(f"🔍 DEBUG - Using fallback amountOfNextPayment: {recurring_cost}")
                                # Try renewalRate as second fallback
                                elif agreement_data.get('renewalRate') and agreement_data['renewalRate'] > 0:
                                    recurring_cost = float(agreement_data['renewalRate'])
                                    if member_data.get('full_name') in ['Miguel Belmontes', 'DALE ROEN']:
                                        logger.info(f"🔍 DEBUG - Using fallback renewalRate: {recurring_cost}")
                                # Try existing agreement_rate field as last resort
                                elif member_data.get('agreement_rate'):
                                    recurring_cost = float(member_data['agreement_rate']) or 0.0
                                    if member_data.get('full_name') in ['Miguel Belmontes', 'DALE ROEN']:
                                        logger.info(f"🔍 DEBUG - Using fallback agreement_rate: {recurring_cost}")
                            elif is_comp_member:
                                # Force recurring_cost to 0 for Comp Members
                                recurring_cost = 0.0
                                if member_data.get('full_name') in ['Miguel Belmontes', 'DALE ROEN']:
                                    logger.info(f"🔍 DEBUG - Comp Member detected, forcing recurring_cost to 0.0")
                            

                            
                            # Since ClubHub isn't providing recurring costs, we need to work backwards
                            if total_amount_past_due > 0 and not is_comp_member:
                                # Use standard Anytime Fitness rate if no recurring cost available
                                if recurring_cost == 0:
                                    recurring_cost = 39.50  # Standard AF monthly rate
                                
                                # Work backwards: ClubHub amount is BASE amount (without late fees)
                                base_amount = total_amount_past_due
                                
                                # Calculate missed payments: base_amount / recurring_payment
                                missed_payments = max(1, int(base_amount / recurring_cost))
                                
                                # Calculate late fees: missed_payments × 19.50
                                late_fees = missed_payments * 19.50
                                
                                # Total = base_amount + late_fees
                                total_with_fees = base_amount + late_fees
                                
                                logger.info(f"💰 Member {member_data['full_name']}: Base: ${base_amount:.2f}, Missed: {missed_payments}, Late Fees: ${late_fees:.2f}, Total: ${total_with_fees:.2f}")
                                
                            elif total_amount_past_due > 0 and is_comp_member:
                                # Comp member - no late fees
                                base_amount = total_amount_past_due
                                missed_payments = 0
                                late_fees = 0.0
                                total_with_fees = base_amount
                                
                                logger.info(f"ℹ️ Member {member_data['full_name']}: Comp Member - Base: ${base_amount:.2f}, No late fees")
                                
                            else:
                                # No past due amount
                                base_amount = 0.0
                                missed_payments = 0
                                late_fees = 0.0
                                total_with_fees = 0.0
                            
                            member_data['base_amount_past_due'] = base_amount
                            member_data['missed_payments'] = missed_payments
                            member_data['late_fees'] = late_fees
                            member_data['amount_past_due'] = total_with_fees
                            
                            # Store additional agreement data for display
                            member_data['agreement_recurring_cost'] = recurring_cost
                            member_data['agreement_status'] = agreement_data.get('status', 'Unknown')
                            member_data['agreement_type'] = agreement_data.get('type', 'Unknown')
                            member_data['agreement_start_date'] = agreement_data.get('startDate', 'Unknown')
                            member_data['agreement_end_date'] = agreement_data.get('endDate', 'Unknown')
                            member_data['agreement_billing_frequency'] = agreement_data.get('billingFrequency', 'Unknown')
                            
                            # Store nested agreement data if available
                            if 'agreement' in agreement_data and isinstance(agreement_data['agreement'], dict):
                                nested_agreement = agreement_data['agreement']
                                member_data['agreement_name'] = nested_agreement.get('name', 'Unknown')
                                member_data['agreement_description'] = nested_agreement.get('description', 'Unknown')
                        else:
                            member_data['amount_past_due'] = 0.0
                            member_data['base_amount_past_due'] = 0.0
                            member_data['late_fees'] = 0.0
                            member_data['missed_payments'] = 0
                            member_data['agreement_recurring_cost'] = 0.0
                            member_data['agreement_status'] = 'No Agreement'
                            member_data['agreement_type'] = 'No Agreement'
                            member_data['agreement_start_date'] = 'No Agreement'
                            member_data['agreement_end_date'] = 'No Agreement'
                            member_data['agreement_billing_frequency'] = 'No Agreement'
                            member_data['agreement_name'] = 'No Agreement'
                            member_data['agreement_description'] = 'No Agreement'
                    else:
                        member_data['amount_past_due'] = 0.0
                        member_data['base_amount_past_due'] = 0.0
                        member_data['late_fees'] = 0.0
                        member_data['missed_payments'] = 0
                        member_data['agreement_recurring_cost'] = 0.0
                        member_data['agreement_status'] = 'No Agreement'
                        member_data['agreement_type'] = 'No Agreement'
                        member_data['agreement_start_date'] = 'No Agreement'
                        member_data['agreement_end_date'] = 'No Agreement'
                        member_data['agreement_billing_frequency'] = 'No Agreement'
                        member_data['agreement_name'] = 'No Agreement'
                        member_data['agreement_description'] = 'No Agreement'
                        
                    return member_data
                except Exception as e:
                    logger.warning(f"⚠️ Could not get agreement data for member {member_data.get('firstName', 'Unknown')}: {e}")
                    member_data['amount_past_due'] = 0.0
                    member_data['base_amount_past_due'] = 0.0
                    member_data['late_fees'] = 0.0
                    member_data['missed_payments'] = 0
                    member_data['agreement_recurring_cost'] = 0.0
                    member_data['agreement_status'] = 'No Agreement'
                    member_data['agreement_type'] = 'No Agreement'
                    member_data['agreement_start_date'] = 'No Agreement'
                    member_data['agreement_end_date'] = 'No Agreement'
                    member_data['agreement_billing_frequency'] = 'No Agreement'
                    member_data['agreement_name'] = 'No Agreement'
                    member_data['agreement_description'] = 'No Agreement'
                    return member_data
            
            # Process members in parallel with optimized thread count
            with ThreadPoolExecutor(max_workers=15) as executor:
                future_to_member = {executor.submit(get_member_agreement_data, member): member for member in members}
                
                # Process completed tasks and track progress
                completed_count = 0
                for future in as_completed(future_to_member):
                    completed_count += 1
                    if completed_count % 100 == 0:  # Log progress every 100 members
                        logger.info(f"📊 Members: {completed_count}/{len(members)} processed...")
            
            logger.info(f"✅ Members: {len(members)} processed with agreement data")
            
            # Log summary of late fee calculations
            total_base_amount = sum(m.get('base_amount_past_due', 0) for m in members)
            total_late_fees = sum(m.get('late_fees', 0) for m in members)
            total_amount_owed = sum(m.get('amount_past_due', 0) for m in members)
            members_with_late_fees = len([m for m in members if m.get('late_fees', 0) > 0])
            
            logger.info(f"💰 Late Fee Summary: {members_with_late_fees} members have late fees")
            logger.info(f"💰 Total Base Amount: ${total_base_amount:.2f}")
            logger.info(f"💰 Total Late Fees: ${total_late_fees:.2f}")
            logger.info(f"💰 Total Amount Owed: ${total_amount_owed:.2f}")
            
            app.data_cache['members'] = members
            app.data_cache['last_sync']['members'] = datetime.now().isoformat()
            
            # Save members to database
            try:
                app.db_manager.save_members_to_db(members)
                logger.info(f"✅ Members: {len(members)} saved to database with past due amounts")
            except Exception as db_e:
                logger.warning(f"⚠️ Could not save members to database: {db_e}")
        else:
            logger.warning("⚠️ No members found from ClubHub API")
        
        # 4. Training clients sync (if available)
        if app.clubos:
            logger.info("💪 Syncing training clients...")
            try:
                training_clients = app.clubos.get_training_clients()
                if training_clients:
                    app.data_cache['training_clients'] = training_clients
                    app.data_cache['last_sync']['training_clients'] = datetime.now().isoformat()
                    
                    try:
                        app.db_manager.save_training_clients_to_db(training_clients)
                        logger.info(f"✅ Training clients: {len(training_clients)} synced and saved")
                    except Exception as db_e:
                        logger.warning(f"⚠️ Could not save training clients to database: {db_e}")
                        logger.info(f"✅ Training clients: {len(training_clients)} synced (database save failed)")
                else:
                    logger.warning("⚠️ No training clients found")
            except Exception as e:
                logger.error(f"❌ Training clients sync failed: {e}")
        
        logger.info("🎉 OPTIMIZED startup sync completed successfully!")
        
        # Start periodic sync in background thread
        try:
            periodic_sync_thread = threading.Thread(target=periodic_sync, args=(app,), daemon=True)
            periodic_sync_thread.start()
            logger.info("✅ Periodic sync thread started")
        except Exception as e:
            logger.error(f"❌ Failed to start periodic sync thread: {e}")
        
    except Exception as e:
        logger.error(f"❌ OPTIMIZED startup sync failed: {e}")

def periodic_sync(app):
    """Periodically sync data in the background"""
    logger.info("🔄 Starting periodic sync thread...")
    
    while True:
        try:
            time.sleep(300)  # Sync every 5 minutes
            
            logger.info("🔄 Performing periodic data sync...")
            
            # Sync messages
            if app.messaging_client:
                try:
                    messages = app.messaging_client.sync_messages('187032782')
                    if messages:
                        # Update cache
                        app.data_cache['messages'] = messages
                        app.data_cache['last_sync']['messages'] = datetime.now().isoformat()
                        logger.info(f"✅ Periodic sync: {len(messages)} messages synced and cached")
                except Exception as e:
                    logger.error(f"❌ Periodic sync messages failed: {e}")
            
            # Sync prospects from ClubHub API
            try:
                # Import with fallback paths
                try:
                    from services.api.clubhub_api_client import ClubHubAPIClient
                    from config.clubhub_credentials import CLUBHUB_EMAIL, CLUBHUB_PASSWORD
                except ImportError:
                    # Fallback to root level imports
                    import sys
                    import os
                    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
                    from services.api.clubhub_api_client import ClubHubAPIClient
                    from config.clubhub_credentials import CLUBHUB_EMAIL, CLUBHUB_PASSWORD
                
                clubhub_client = ClubHubAPIClient()
                
                if clubhub_client.authenticate(CLUBHUB_EMAIL, CLUBHUB_PASSWORD):
                    prospects = clubhub_client.get_all_prospects_paginated()
                    if prospects:
                        # Process prospects to ensure full_name is set
                        for prospect in prospects:
                            prospect['full_name'] = f"{prospect.get('firstName', '')} {prospect.get('lastName', '')}".strip()
                        
                        app.data_cache['prospects'] = prospects
                        app.data_cache['last_sync']['prospects'] = datetime.now().isoformat()
                        logger.info(f"✅ Periodic sync: {len(prospects)} prospects synced and cached from ClubHub API")
                        
                        # Save prospects to database as well
                        try:
                            if hasattr(app, 'db_manager'):
                                app.db_manager.save_prospects_to_db(prospects)
                                logger.info(f"✅ Periodic sync: {len(prospects)} prospects saved to database")
                            else:
                                logger.warning("⚠️ No db_manager available, skipping database save")
                        except Exception as db_e:
                            logger.warning(f"⚠️ Could not save prospects to database: {db_e}")
                            
            except Exception as e:
                logger.error(f"❌ Periodic sync prospects failed: {e}")
            
            # Sync members from ClubHub API
            try:
                # Import with fallback paths
                try:
                    from services.api.clubhub_api_client import ClubHubAPIClient
                    from config.clubhub_credentials import CLUBHUB_EMAIL, CLUBHUB_PASSWORD
                except ImportError:
                    # Fallback to root level imports
                    import sys
                    import os
                    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
                    from services.api.clubhub_api_client import ClubHubAPIClient
                    from config.clubhub_credentials import CLUBHUB_EMAIL, CLUBHUB_PASSWORD
                
                clubhub_client = ClubHubAPIClient()
                
                if clubhub_client.authenticate(CLUBHUB_EMAIL, CLUBHUB_PASSWORD):
                    members = clubhub_client.get_all_members_paginated()
                    if members:
                        # Process members to ensure full_name is set
                        for member in members:
                            member['full_name'] = f"{member.get('firstName', '')} {member.get('lastName', '')}".strip()
                        
                        app.data_cache['members'] = members
                        app.data_cache['last_sync']['members'] = datetime.now().isoformat()
                        logger.info(f"✅ Periodic sync: {len(members)} members synced and cached from ClubHub API")
                        
                        # Save members to database as well
                        try:
                            if hasattr(app, 'db_manager'):
                                app.db_manager.save_members_to_db(members)
                                logger.info(f"✅ Periodic sync: {len(members)} members saved to database")
                            else:
                                logger.warning("⚠️ No db_manager available, skipping database save")
                        except Exception as db_e:
                            logger.warning(f"⚠️ Could not save members to database: {db_e}")
                            
            except Exception as e:
                logger.error(f"❌ Periodic sync members failed: {e}")
            
            # Sync training clients from ClubOS
            if app.clubos:
                try:
                    training_clients = app.clubos.get_training_clients()
                    if training_clients:
                        # Cache in memory
                        app.data_cache['training_clients'] = training_clients
                        app.data_cache['last_sync']['training_clients'] = datetime.now().isoformat()
                        
                        # Save to database for persistence
                        try:
                            if hasattr(app, 'db_manager'):
                                app.db_manager.save_training_clients_to_db(training_clients)
                                logger.info(f"✅ Periodic sync: {len(training_clients)} training clients synced, cached, and saved to database")
                            else:
                                logger.warning("⚠️ No db_manager available, skipping database save")
                                logger.info(f"✅ Periodic sync: {len(training_clients)} training clients synced and cached")
                        except Exception as db_e:
                            logger.warning(f"⚠️ Could not save training clients to database: {db_e}")
                            logger.info(f"✅ Periodic sync: {len(training_clients)} training clients synced and cached")
                except Exception as e:
                    logger.error(f"❌ Periodic sync training clients failed: {e}")
            
        except Exception as e:
            logger.error(f"❌ Periodic sync error: {e}")
            time.sleep(60)  # Wait 1 minute on error before retrying

# Create the app instance
app = create_app()

if __name__ == '__main__':
    # On Windows, Werkzeug's reloader can trigger WinError 10038 (not a socket) during restarts.
    # Keep debug features but disable the auto-reloader for stability.
    app.run(debug=True, use_reloader=False, host='0.0.0.0', port=5000)
