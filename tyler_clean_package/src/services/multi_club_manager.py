#!/usr/bin/env python3
"""
Multi-Club Manager - Handle multi-club authentication and data synchronization
"""

import json
import base64
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

logger = logging.getLogger(__name__)

class MultiClubManager:
    """Manages multi-club access and data synchronization"""
    
    def __init__(self):
        self.available_clubs = []
        self.selected_clubs = []
        self.club_names_cache = {}
        self.user_info = {}
        
    def parse_jwt_token(self, jwt_token: str) -> Optional[Dict[str, Any]]:
        """Parse JWT token to extract club access information"""
        try:
            # JWT tokens have 3 parts separated by dots
            parts = jwt_token.split('.')
            if len(parts) != 3:
                logger.error("Invalid JWT token format")
                return None
            
            # Decode the payload (middle part)
            payload = parts[1]
            # Add padding if needed
            payload += '=' * (-len(payload) % 4)
            
            decoded = base64.b64decode(payload)
            token_data = json.loads(decoded)
            
            logger.info(f"✅ JWT token parsed successfully")
            logger.info(f"👤 User authenticated: {token_data.get('given_name', 'Unknown')}")
            logger.info(f"🏢 Available clubs: {len(token_data.get('club_ids', []))} clubs")
            logger.info(f"🔑 Role: {token_data.get('role', 'Unknown')}")
            
            return token_data
            
        except Exception as e:
            logger.error(f"❌ Error parsing JWT token: {e}")
            return None
    
    def extract_club_access(self, jwt_token: str) -> Tuple[List[str], Dict[str, Any]]:
        """Extract club IDs and user info from JWT token"""
        token_data = self.parse_jwt_token(jwt_token)
        if not token_data:
            return [], {}
        
        club_ids = token_data.get('club_ids', [])
        user_info = {
            'name': token_data.get('given_name', 'Unknown'),
            'email': token_data.get('email', 'No email'),
            'role': token_data.get('role', 'Unknown'),
            'user_type': token_data.get('user_type', 'Unknown'),
            'af_api_token': token_data.get('af_api_token', ''),
            'application_ids': token_data.get('application_ids', [])
        }
        
        self.available_clubs = club_ids
        self.user_info = user_info
        
        return club_ids, user_info
    
    def get_club_name(self, club_id: str) -> str:
        """Get human-readable club name (with caching)"""
        if club_id in self.club_names_cache:
            return self.club_names_cache[club_id]
        
        # Known club mappings (can be expanded from environment or config)
        import os
        club_names = {
            os.getenv('DEFAULT_CLUB_ID', '1156'): "Fond du Lac, WI",
            "1657": "Green Bay East, WI", 
            "1234": "Milwaukee Downtown, WI",
            "1111": "Madison West, WI"
        }
        
        name = club_names.get(club_id, f"Club {club_id}")
        self.club_names_cache[club_id] = name
        return name
    
    def get_available_clubs_for_selection(self) -> List[Dict[str, Any]]:
        """Get formatted list of clubs for selection screen"""
        clubs = []
        for club_id in self.available_clubs:
            clubs.append({
                'id': club_id,
                'name': self.get_club_name(club_id),
                'display_name': f"{self.get_club_name(club_id)} (#{club_id})"
            })
        return clubs
    
    def set_selected_clubs(self, club_ids: List[str]):
        """Set which clubs to sync data from"""
        # Validate that selected clubs are available
        valid_clubs = [club_id for club_id in club_ids if club_id in self.available_clubs]
        self.selected_clubs = valid_clubs
        
        logger.info(f"🎯 Selected clubs for sync: {[self.get_club_name(club_id) for club_id in valid_clubs]}")
        return valid_clubs
    
    def get_selected_clubs(self) -> List[str]:
        """Get currently selected club IDs"""
        return self.selected_clubs
    
    def sync_multi_club_data(self, clubhub_client, sync_functions: Dict[str, callable], app=None) -> Dict[str, Any]:
        """Synchronize data from multiple clubs in parallel
        
        Args:
            clubhub_client: ClubHubAPIClient instance
            sync_functions: Dict mapping data type to sync function
            app: Flask application instance (optional, for shared database access)
            
        Returns:
            Dict with combined data from all clubs
        """
        if not self.selected_clubs:
            logger.warning("⚠️ No clubs selected for sync")
            return {}
        
        logger.info(f"🔄 Starting multi-club sync for {len(self.selected_clubs)} clubs...")
        
        combined_data = {
            'members': [],
            'prospects': [], 
            'training_clients': [],
            'club_metadata': {}
        }
        
        def sync_club_data(club_id: str) -> Tuple[str, Dict[str, Any]]:
            """Sync data for a single club"""
            logger.info(f"🏢 Syncing {self.get_club_name(club_id)} (#{club_id})...")
            
            # Temporarily set the club_id on the client
            original_club_id = clubhub_client.club_id
            clubhub_client.club_id = club_id
            
            club_data = {
                'members': [],
                'prospects': [],
                'training_clients': [],
                'club_info': {'id': club_id, 'name': self.get_club_name(club_id)}
            }
            
            try:
                # Execute each sync function for this club
                for data_type, sync_func in sync_functions.items():
                    try:
                        logger.info(f"  📊 Syncing {data_type} for {self.get_club_name(club_id)}...")
                        # Pass both club_id and app parameters to sync functions
                        data = sync_func(club_id=club_id, app=app)
                        
                        if data:
                            club_data[data_type] = data
                            logger.info(f"  ✅ {data_type}: {len(data) if isinstance(data, list) else 'OK'}")
                        else:
                            logger.warning(f"  ⚠️ No {data_type} data for {self.get_club_name(club_id)}")
                            
                    except Exception as e:
                        logger.error(f"  ❌ Error syncing {data_type} for {self.get_club_name(club_id)}: {e}")
                        club_data[data_type] = []
                
                logger.info(f"✅ Completed sync for {self.get_club_name(club_id)}")
                
            except Exception as e:
                logger.error(f"❌ Error syncing {self.get_club_name(club_id)}: {e}")
                
            finally:
                # Restore original club_id
                clubhub_client.club_id = original_club_id
            
            return club_id, club_data
        
        # Execute syncing in parallel using ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=min(len(self.selected_clubs), 5)) as executor:
            # Submit all club sync tasks
            future_to_club = {executor.submit(sync_club_data, club_id): club_id for club_id in self.selected_clubs}
            
            # Process completed tasks
            for future in as_completed(future_to_club):
                club_id = future_to_club[future]
                try:
                    club_id, club_data = future.result()
                    
                    # Merge club data into combined results
                    for data_type in ['members', 'prospects', 'training_clients']:
                        if data_type in club_data and club_data[data_type]:
                            # Add club_id to each record for tracking
                            if isinstance(club_data[data_type], list):
                                for record in club_data[data_type]:
                                    if isinstance(record, dict):
                                        record['source_club_id'] = club_id
                                        record['source_club_name'] = self.get_club_name(club_id)
                                
                                combined_data[data_type].extend(club_data[data_type])
                    
                    # Store club metadata
                    combined_data['club_metadata'][club_id] = club_data['club_info']
                    
                except Exception as e:
                    logger.error(f"❌ Error processing sync results for {self.get_club_name(club_id)}: {e}")
        
        # Summary
        logger.info(f"🎉 Multi-club sync complete!")
        logger.info(f"📊 Combined results:")
        for data_type in ['members', 'prospects', 'training_clients']:
            count = len(combined_data[data_type])
            logger.info(f"  • {data_type}: {count}")
        
        return combined_data
    
    def get_club_breakdown(self, data: List[Dict[str, Any]]) -> Dict[str, int]:
        """Get count breakdown by club from combined data"""
        breakdown = {}
        for record in data:
            if isinstance(record, dict) and 'source_club_id' in record:
                club_id = record['source_club_id']
                club_name = record.get('source_club_name', self.get_club_name(club_id))
                breakdown[club_name] = breakdown.get(club_name, 0) + 1
        return breakdown
    
    def is_multi_club_user(self) -> bool:
        """Check if user has access to multiple clubs"""
        return len(self.available_clubs) > 1
    
    def get_user_summary(self) -> Dict[str, Any]:
        """Get summary of user's multi-club access"""
        return {
            'user_info': self.user_info,
            'available_clubs': self.get_available_clubs_for_selection(),
            'selected_clubs': self.selected_clubs,
            'is_multi_club': self.is_multi_club_user(),
            'total_available': len(self.available_clubs),
            'total_selected': len(self.selected_clubs)
        }

# Global instance
multi_club_manager = MultiClubManager()
