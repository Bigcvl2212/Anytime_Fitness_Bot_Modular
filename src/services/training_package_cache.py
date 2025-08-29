#!/usr/bin/env python3
"""
Training Package Cache Service
Handles caching of training package data and funding status lookups
"""

import os
import sqlite3
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from flask import current_app

logger = logging.getLogger(__name__)

class TrainingPackageCache:
    """Enhanced cache for training package data with database storage and daily updates"""
    
    def __init__(self):
        self.cache_expiry_hours = 24  # Cache expires after 24 hours
        self.api = None  # Will be initialized when needed
        
    def lookup_participant_funding(self, participant_name: str, participant_email: str = None, force: bool = False) -> dict:
        """Look up funding status.
        When force=True, bypass cache and fetch live from ClubOS, then update cache.
        When force=False, prefer fresh cache and fall back to live fetch if stale/missing.
        """
        try:
            logger.info(f"🔍 Looking up funding for: {participant_name}")
            
            # First, check if we have cached data that's still fresh (unless forced live)
            cached_data = self._get_cached_funding(participant_name)
            if not force and cached_data and not self._is_cache_stale(cached_data):
                logger.info(f"✅ Using cached funding data for {participant_name}")
                return self._format_funding_response(cached_data, is_stale=False, is_cached=True)
            
            # If no fresh cache, get member ID and try to fetch fresh data
            member_id = self._get_member_id_from_database(participant_name, participant_email)
            if member_id:
                logger.info(f"📊 Fetching fresh funding data for member ID: {member_id}")
                fresh_data = self._fetch_fresh_funding_data(member_id, participant_name)
                if fresh_data:
                    # Cache the fresh data
                    self._cache_funding_data(fresh_data)
                    return self._format_funding_response(fresh_data, is_stale=False, is_cached=False)
            
            # If we have stale cached data, use it as fallback
            if not force and cached_data:
                logger.info(f"⚠️ Using stale cached data for {participant_name}")
                return self._format_funding_response(cached_data, is_stale=True, is_cached=True)
            
            # No data available
            logger.warning(f"❌ No funding data available for {participant_name}")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error looking up funding for {participant_name}: {e}")
            return None
    
    def _get_cached_funding(self, participant_name: str) -> dict:
        """Get cached funding data from database"""
        try:
            # Get database path from current app context
            db_path = current_app.db_manager.db_path if current_app else 'gym_bot.db'
            
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Look up by member name (fuzzy match)
            cursor.execute("""
                SELECT * FROM funding_status_cache 
                WHERE LOWER(member_name) LIKE LOWER(?)
                ORDER BY last_updated DESC
                LIMIT 1
            """, (f"%{participant_name.strip()}%",))
            
            result = cursor.fetchone()
            conn.close()
            
            return dict(result) if result else None
            
        except Exception as e:
            logger.error(f"❌ Error getting cached funding: {e}")
            return None
    
    def _is_cache_stale(self, cached_data: dict) -> bool:
        """Check if cached data is stale"""
        try:
            last_updated = datetime.fromisoformat(cached_data.get('last_updated', ''))
            cache_expiry = datetime.fromisoformat(cached_data.get('cache_expiry', ''))
            return datetime.now() > cache_expiry
        except Exception as e:
            logger.warning(f"⚠️ Error checking cache staleness: {e}")
            return True  # Assume stale if we can't determine
    
    def _get_member_id_from_database(self, participant_name: str, participant_email: str = None) -> Optional[str]:
        """Get member ID from database by name or email"""
        try:
            db_path = current_app.db_manager.db_path if current_app else 'gym_bot.db'
            
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Try to find by name first
            cursor.execute("""
                SELECT prospect_id FROM members 
                WHERE LOWER(full_name) LIKE LOWER(?) OR 
                      (LOWER(first_name) || ' ' || LOWER(last_name)) LIKE LOWER(?)
                LIMIT 1
            """, (f"%{participant_name.strip()}%", f"%{participant_name.strip()}%"))
            
            result = cursor.fetchone()
            
            if not result and participant_email:
                # Try by email if name didn't work
                cursor.execute("""
                    SELECT prospect_id FROM members 
                    WHERE LOWER(email) = LOWER(?)
                    LIMIT 1
                """, (participant_email.strip(),))
                result = cursor.fetchone()
            
            conn.close()
            
            return result[0] if result else None
            
        except Exception as e:
            logger.error(f"❌ Error getting member ID from database: {e}")
            return None
    
    def _fetch_fresh_funding_data(self, member_id: str, participant_name: str) -> Optional[dict]:
        """Fetch fresh funding data from ClubOS API"""
        try:
            # Initialize API if not already done
            if not self.api:
                from clubos_training_api_fixed import ClubOSTrainingPackageAPI
                self.api = ClubOSTrainingPackageAPI()
                self.api.authenticate()
            
            # Get funding status from ClubOS
            funding_data = self.api.get_member_billing_status(member_id)
            
            if funding_data:
                return {
                    'member_name': participant_name,
                    'member_id': member_id,
                    'funding_status': funding_data.get('status', 'Unknown'),
                    'package_details': json.dumps(funding_data),
                    'last_updated': datetime.now().isoformat(),
                    'cache_expiry': (datetime.now() + timedelta(hours=self.cache_expiry_hours)).isoformat()
                }
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error fetching fresh funding data: {e}")
            return None
    
    def _cache_funding_data(self, funding_data: dict):
        """Cache funding data in database"""
        try:
            db_path = current_app.db_manager.db_path if current_app else 'gym_bot.db'
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO funding_status_cache 
                (member_name, member_email, member_id, funding_status, package_details, last_updated, cache_expiry)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                funding_data.get('member_name'),
                funding_data.get('member_email'),
                funding_data.get('member_id'),
                funding_data.get('funding_status'),
                funding_data.get('package_details'),
                funding_data.get('last_updated'),
                funding_data.get('cache_expiry')
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Cached funding data for {funding_data.get('member_name')}")
            
        except Exception as e:
            logger.error(f"❌ Error caching funding data: {e}")
    
    def _format_funding_response(self, data: dict, is_stale: bool = False, is_cached: bool = False) -> dict:
        """Format funding data for frontend consumption"""
        try:
            package_details = json.loads(data.get('package_details', '{}'))
            
            # Determine status and styling
            status = data.get('funding_status', 'Unknown')
            if is_stale:
                status_text = f"{status} (Cached - {self._get_cache_age(data)} old)"
                status_class = 'warning'
                status_icon = 'fas fa-clock'
            elif is_cached:
                status_text = f"{status} (Cached)"
                status_class = 'info'
                status_icon = 'fas fa-database'
            else:
                status_text = status
                status_class = 'success'
                status_icon = 'fas fa-check-circle'
            
            return {
                'status': status,
                'status_text': status_text,
                'status_class': status_class,
                'status_icon': status_icon,
                'package_details': package_details,
                'is_cached': is_cached,
                'is_stale': is_stale,
                'last_updated': data.get('last_updated'),
                'cache_age': self._get_cache_age(data) if is_cached else None
            }
            
        except Exception as e:
            logger.error(f"❌ Error formatting funding response: {e}")
            return {
                'status': 'Error',
                'status_text': 'Error formatting data',
                'status_class': 'danger',
                'status_icon': 'fas fa-exclamation-triangle',
                'is_cached': False,
                'is_stale': False
            }
    
    def _get_cache_age(self, data: dict) -> str:
        """Get human-readable cache age"""
        try:
            last_updated = datetime.fromisoformat(data.get('last_updated', ''))
            age = datetime.now() - last_updated
            
            if age.days > 0:
                return f"{age.days} day{'s' if age.days != 1 else ''}"
            elif age.seconds > 3600:
                hours = age.seconds // 3600
                return f"{hours} hour{'s' if hours != 1 else ''}"
            elif age.seconds > 60:
                minutes = age.seconds // 60
                return f"{minutes} minute{'s' if minutes != 1 else ''}"
            else:
                return "Just now"
                
        except Exception:
            return "Unknown"
    
    def refresh_cache(self):
        """Refresh all cached funding data"""
        try:
            logger.info("🔄 Refreshing funding cache")
            
            db_path = current_app.db_manager.db_path if current_app else 'gym_bot.db'
            
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get all cached entries
            cursor.execute("SELECT * FROM funding_status_cache")
            cached_entries = cursor.fetchall()
            
            conn.close()
            
            refreshed_count = 0
            for entry in cached_entries:
                entry_dict = dict(entry)
                member_id = entry_dict.get('member_id')
                member_name = entry_dict.get('member_name')
                
                if member_id and member_name:
                    # Fetch fresh data
                    fresh_data = self._fetch_fresh_funding_data(member_id, member_name)
                    if fresh_data:
                        self._cache_funding_data(fresh_data)
                        refreshed_count += 1
            
            logger.info(f"✅ Funding cache refreshed: {refreshed_count} entries updated")
            return refreshed_count
            
        except Exception as e:
            logger.error(f"❌ Error refreshing funding cache: {e}")
            return 0
    
    def clear_expired_cache(self):
        """Clear expired cache entries"""
        try:
            db_path = current_app.db_manager.db_path if current_app else 'gym_bot.db'
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Delete expired entries
            cursor.execute("""
                DELETE FROM funding_status_cache 
                WHERE cache_expiry < ?
            """, (datetime.now().isoformat(),))
            
            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()
            
            if deleted_count > 0:
                logger.info(f"🧹 Cleared {deleted_count} expired cache entries")
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"❌ Error clearing expired cache: {e}")
            return 0
    
    def get_cache_status(self) -> dict:
        """Get cache status information"""
        try:
            db_path = current_app.db_manager.db_path if current_app else 'gym_bot.db'
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get total cache entries
            cursor.execute("SELECT COUNT(*) FROM funding_status_cache")
            total_entries = cursor.fetchone()[0]
            
            # Get expired entries count
            cursor.execute("""
                SELECT COUNT(*) FROM funding_status_cache 
                WHERE cache_expiry < ?
            """, (datetime.now().isoformat(),))
            expired_entries = cursor.fetchone()[0]
            
            # Get cache size info
            cursor.execute("PRAGMA page_count")
            page_count = cursor.fetchone()[0]
            cursor.execute("PRAGMA page_size")
            page_size = cursor.fetchone()[0]
            cache_size_mb = (page_count * page_size) / (1024 * 1024)
            
            conn.close()
            
            return {
                'total_entries': total_entries,
                'expired_entries': expired_entries,
                'active_entries': total_entries - expired_entries,
                'cache_size_mb': round(cache_size_mb, 2),
                'last_refresh': self._get_last_cache_refresh()
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting cache status: {e}")
            return {
                'total_entries': 0,
                'expired_entries': 0,
                'active_entries': 0,
                'cache_size_mb': 0,
                'last_refresh': 'Unknown'
            }
    
    def _get_last_cache_refresh(self) -> str:
        """Get last cache refresh time"""
        try:
            db_path = current_app.db_manager.db_path if current_app else 'gym_bot.db'
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT MAX(last_updated) FROM funding_status_cache
            """)
            
            result = cursor.fetchone()
            conn.close()
            
            if result and result[0]:
                last_refresh = datetime.fromisoformat(result[0])
                return last_refresh.strftime("%Y-%m-%d %H:%M:%S")
            
            return "Never"
            
        except Exception:
            return "Unknown"
