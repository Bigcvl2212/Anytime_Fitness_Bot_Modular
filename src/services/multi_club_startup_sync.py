#!/usr/bin/env python3
"""
Multi-Club Startup Sync - Enhanced startup synchronization with multi-club support
"""

import logging
import time
from typing import Dict, List, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)

def enhanced_startup_sync(app, multi_club_enabled: bool = True) -> Dict[str, Any]:
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
        if multi_club_enabled:
            # Multi-club sync
            from src.services.multi_club_manager import multi_club_manager
            
            selected_clubs = multi_club_manager.get_selected_clubs()
            
            if not selected_clubs:
                logger.warning("⚠️ No clubs selected for multi-club sync")
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
                clubhub_client, sync_functions
            )
            
            # Update sync results
            sync_results['success'] = True
            sync_results['combined_totals']['members'] = len(combined_data.get('members', []))
            sync_results['combined_totals']['prospects'] = len(combined_data.get('prospects', []))
            sync_results['combined_totals']['training_clients'] = len(combined_data.get('training_clients', []))
            sync_results['club_results'] = combined_data.get('club_metadata', {})
            
            # Cache combined data in app
            app.cached_members = combined_data.get('members', [])
            app.cached_prospects = combined_data.get('prospects', [])
            app.cached_training_clients = combined_data.get('training_clients', [])
            
            # **CRITICAL FIX: Actually save data to database!**
            logger.info("💾 Saving fresh data to database...")
            try:
                from src.services.database_manager import DatabaseManager
                db_manager = DatabaseManager()
                
                # Save members to database
                members_saved = db_manager.save_members_to_db(app.cached_members)
                logger.info(f"{'✅' if members_saved else '❌'} Members saved to database: {members_saved}")
                
                # Save prospects to database  
                prospects_saved = db_manager.save_prospects_to_db(app.cached_prospects)
                logger.info(f"{'✅' if prospects_saved else '❌'} Prospects saved to database: {prospects_saved}")
                
                # Save training clients to database
                training_saved = db_manager.save_training_clients_to_db(app.cached_training_clients)
                logger.info(f"{'✅' if training_saved else '❌'} Training clients saved to database: {training_saved}")
                
                # Log data refresh operations
                db_manager.log_data_refresh('members', len(app.cached_members))
                db_manager.log_data_refresh('prospects', len(app.cached_prospects))  
                db_manager.log_data_refresh('training_clients', len(app.cached_training_clients))
                
                logger.info("💾 Database save operations completed!")
                
            except Exception as db_error:
                logger.error(f"❌ Database save error: {db_error}")
                sync_results['errors'].append(f"Database save error: {db_error}")
            
            logger.info(f"🎉 Multi-club sync complete! Members: {sync_results['combined_totals']['members']}, "
                       f"Prospects: {sync_results['combined_totals']['prospects']}, "
                       f"Training Clients: {sync_results['combined_totals']['training_clients']}")
            
        else:
            # Single club sync (existing functionality)
            logger.info("🔄 Starting single-club startup sync...")
            
            # Use existing sync methods
            members = sync_members_for_club()
            prospects = sync_prospects_for_club()
            training_clients = sync_training_clients_for_club()
            
            sync_results['success'] = True
            sync_results['combined_totals']['members'] = len(members) if members else 0
            sync_results['combined_totals']['prospects'] = len(prospects) if prospects else 0
            sync_results['combined_totals']['training_clients'] = len(training_clients) if training_clients else 0
            
            # Cache data in app
            app.cached_members = members or []
            app.cached_prospects = prospects or []
            app.cached_training_clients = training_clients or []
            
            # **CRITICAL FIX: Actually save data to database for single-club mode too!**
            logger.info("💾 Saving fresh data to database (single-club mode)...")
            try:
                from src.services.database_manager import DatabaseManager
                db_manager = DatabaseManager()
                
                # Save members to database
                members_saved = db_manager.save_members_to_db(app.cached_members) if app.cached_members else True
                logger.info(f"{'✅' if members_saved else '❌'} Members saved to database: {members_saved}")
                
                # Save prospects to database  
                prospects_saved = db_manager.save_prospects_to_db(app.cached_prospects) if app.cached_prospects else True
                logger.info(f"{'✅' if prospects_saved else '❌'} Prospects saved to database: {prospects_saved}")
                
                # Save training clients to database
                training_saved = db_manager.save_training_clients_to_db(app.cached_training_clients) if app.cached_training_clients else True
                logger.info(f"{'✅' if training_saved else '❌'} Training clients saved to database: {training_saved}")
                
                # Log data refresh operations
                db_manager.log_data_refresh('members', len(app.cached_members))
                db_manager.log_data_refresh('prospects', len(app.cached_prospects))  
                db_manager.log_data_refresh('training_clients', len(app.cached_training_clients))
                
                logger.info("💾 Database save operations completed!")
                
            except Exception as db_error:
                logger.error(f"❌ Database save error: {db_error}")
                sync_results['errors'].append(f"Database save error: {db_error}")
        
        sync_results['total_time'] = time.time() - start_time
        logger.info(f"✅ Startup sync completed in {sync_results['total_time']:.2f} seconds")
        
    except Exception as e:
        error_msg = f"Startup sync error: {e}"
        logger.error(f"❌ {error_msg}")
        sync_results['errors'].append(error_msg)
        sync_results['total_time'] = time.time() - start_time
    
    return sync_results

def sync_members_for_club(club_id: str = None) -> List[Dict[str, Any]]:
    """
    Sync members for a specific club
    
    Args:
        club_id: Club ID to sync (optional for backward compatibility)
        
    Returns:
        List of member data
    """
    try:
        logger.info(f"📊 Syncing members for club {club_id or 'default'}...")
        
        # Import the ClubHub API client
        from src.services.api.clubhub_api_client import ClubHubAPIClient
        from config.clubhub_credentials import CLUBHUB_EMAIL, CLUBHUB_PASSWORD
        
        # Create and authenticate client
        clubhub_client = ClubHubAPIClient()
        if not clubhub_client.authenticate(CLUBHUB_EMAIL, CLUBHUB_PASSWORD):
            logger.error(f"❌ ClubHub authentication failed for club {club_id}")
            return []
        
        # Get ALL members for this specific club using pagination
        members = clubhub_client.get_all_members_paginated()
        if not members:
            logger.warning(f"⚠️ No members found for club {club_id}")
            return []
        
        # Process members to add full_name and club context
        for member in members:
            member['full_name'] = f"{member.get('firstName', '')} {member.get('lastName', '')}".strip()
            member['source_club_id'] = club_id
            
        logger.info(f"✅ Synced {len(members)} members for club {club_id}")
        return members
        
    except Exception as e:
        logger.error(f"❌ Error syncing members for club {club_id}: {e}")
        return []

def sync_prospects_for_club(club_id: str = None) -> List[Dict[str, Any]]:
    """
    Sync prospects for a specific club
    
    Args:
        club_id: Club ID to sync (optional for backward compatibility)
        
    Returns:
        List of prospect data
    """
    try:
        logger.info(f"📊 Syncing prospects for club {club_id or 'default'}...")
        
        # Import the ClubHub API client
        from src.services.api.clubhub_api_client import ClubHubAPIClient
        from config.clubhub_credentials import CLUBHUB_EMAIL, CLUBHUB_PASSWORD
        
        # Create and authenticate client
        clubhub_client = ClubHubAPIClient()
        if not clubhub_client.authenticate(CLUBHUB_EMAIL, CLUBHUB_PASSWORD):
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

def sync_training_clients_for_club(club_id: str = None) -> List[Dict[str, Any]]:
    """
    Sync training clients for a specific club
    
    Args:
        club_id: Club ID to sync (optional for backward compatibility)
        
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
