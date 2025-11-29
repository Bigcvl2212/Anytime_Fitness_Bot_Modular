#!/usr/bin/env python3
"""
Clean Anytime Fitness Dashboard - Working Version
"""

import os
import sqlite3
import pandas as pd
import re
import random
import glob
import uuid
from difflib import SequenceMatcher
from flask import Flask, render_template, jsonify, request, redirect, url_for, session, flash
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import logging
import json
import sys
import requests
import threading
import time
from clubos_fresh_data_api import ClubOSFreshDataAPI
from clubos_training_api import ClubOSTrainingPackageAPI
from clubos_training_clients_api import ClubOSTrainingClientsAPI
from clubos_real_calendar_api import ClubOSRealCalendarAPI
from ical_calendar_parser import iCalClubOSParser
from gym_bot_clean import ClubOSEventDeletion

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'anytime-fitness-dashboard-secret-key-2025'

# Create templates directory if it doesn't exist
templates_dir = 'templates'
if not os.path.exists(templates_dir):
    os.makedirs(templates_dir)

# Import Square invoice functionality with proper secrets management
try:
    from config.secrets_local import get_secret
    
    # Get Square credentials from secrets (production by default)
    access_token = get_secret("square-production-access-token")
    location_id = get_secret("square-production-location-id")
    
    # Set environment variables for the Square client
    os.environ['SQUARE_PRODUCTION_ACCESS_TOKEN'] = access_token
    os.environ['SQUARE_LOCATION_ID'] = location_id
    os.environ['SQUARE_ENVIRONMENT'] = 'production'
    
    # Now import the Square function
    from services.payments.square_client_simple import create_square_invoice
    
    SQUARE_AVAILABLE = True
    logger.info("🔑 Using Square credentials from secrets_local.py")
    logger.info("✅ Square client loaded successfully in PRODUCTION mode")
    
except ImportError as e:
    logger.warning(f"Square client not available: {e}")
    SQUARE_AVAILABLE = False
    
    # Create a fallback function
    def create_square_invoice(member_name, amount, description="Overdue Payment"):
        """Fallback Square invoice function when service is unavailable"""
        logger.error("Square service unavailable - cannot create invoice")
        return None

# Global background refresh status tracking
data_refresh_status = {
    'is_running': False,
    'started_at': None,
    'completed_at': None,
    'progress': 0,
    'status': 'idle',
    'message': 'No refresh in progress',
    'error': None
}

# Global bulk check-in status tracking
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

# Global instances
clubos_training_api = ClubOSTrainingPackageAPI()
clubos_fresh_data_api = ClubOSFreshDataAPI()

class TrainingPackageCache:
    """Enhanced cache for training package data with database storage and daily updates"""
    
    def __init__(self, cache_expiry_hours: int = 24):
        # Default cache expiry to 24 hours for background refreshes
        self.cache_expiry_hours = cache_expiry_hours
        # Use the globally initialized ClubOS training API client
        self.api = clubos_training_api
        
    def lookup_participant_funding(self, participant_name: str, participant_email: str = None, participant_phone: str = None) -> dict:
        """Look up funding status - LIVE ONLY (no cache fallback for card display)."""
        try:
            logger.info(f"🔍 Looking up funding for: {participant_name}")

            # LIVE lookup only for the most accurate status
            member_id = self._get_member_id_from_database(participant_name, participant_email, participant_phone)
            if member_id:
                logger.info(f"📦 Fetching fresh funding data for member ID: {member_id}")
                fresh_data = self._fetch_fresh_funding_data(member_id, participant_name)
                if fresh_data:
                    # Cache the fresh data then return
                    self._cache_funding_data(fresh_data)
                    return self._format_funding_response(fresh_data, is_stale=False, is_cached=False)
            
            # No data available
            logger.warning(f"❌ No LIVE funding data available for {participant_name}")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error looking up funding for {participant_name}: {e}")
            return None
    
    def _get_cached_funding(self, participant_name: str) -> dict:
        """Get cached funding data from database"""
        try:
            conn = sqlite3.connect(db_manager.db_path)
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
        """Check if cached data is stale (older than cache_expiry_hours)"""
        try:
            if not cached_data or not cached_data.get('last_updated'):
                return True
            
            last_updated = datetime.fromisoformat(cached_data['last_updated'])
            age_hours = (datetime.now() - last_updated).total_seconds() / 3600
            
            return age_hours > self.cache_expiry_hours
            
        except Exception as e:
            logger.error(f"❌ Error checking cache staleness: {e}")
            return True
    
    def _fetch_fresh_funding_data(self, member_id: str, member_name: str) -> dict:
        """Fetch fresh funding data from ClubOS API"""
        try:
            # Use the working training package API
            payment_status = self.api.get_member_payment_status(member_id)
            
            if payment_status:
                # The API returns a simple string: "Current", "Past Due", etc.
                funding_data = {
                    'member_id': None,  # We'll get this from training_clients
                    'member_name': member_name,
                    'clubos_member_id': member_id,
                    'package_name': 'Training Package',  # Generic name since API doesn't return specifics
                    'sessions_remaining': 0,  # API doesn't return this info
                    'sessions_purchased': 0,  # API doesn't return this info
                    'package_amount': None,  # API doesn't return this info
                    'amount_paid': None,  # API doesn't return this info
                    'amount_remaining': None,  # API doesn't return this info
                    'payment_status': payment_status,  # Simple string: "Current" or "Past Due"
                    'payment_method': None,  # API doesn't return this info
                    'last_payment_date': None,  # API doesn't return this info
                    'next_payment_date': None,  # API doesn't return this info
                    'raw_clubos_data': payment_status,  # Store the simple string response
                    'data_source': 'clubos_api',
                    'last_updated': datetime.now().isoformat()
                }
                
                # Determine funding status classification
                funding_data.update(self._classify_funding_status(payment_status))
                
                logger.info(f"✅ Fetched fresh funding data for {member_name}: {payment_status}")
                return funding_data
            else:
                logger.warning(f"❌ No payment status returned for member {member_id}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error fetching fresh funding data: {e}")
            return None
    
    def _classify_funding_status(self, payment_status) -> dict:
        """Classify payment data into funding status categories"""
        try:
            # Handle both string and dict payment status
            if isinstance(payment_status, str):
                status_str = payment_status.lower()
                
                if status_str == 'current':
                    return {
                        'funding_status': 'funded',
                        'funding_status_text': 'Current',
                        'funding_status_class': 'success',
                        'funding_status_icon': 'fas fa-check-circle'
                    }
                elif status_str == 'past due':
                    return {
                        'funding_status': 'unfunded',
                        'funding_status_text': 'Past Due',
                        'funding_status_class': 'danger',
                        'funding_status_icon': 'fas fa-exclamation-triangle'
                    }
                else:
                    return {
                        'funding_status': 'unknown',
                        'funding_status_text': status_str.title(),
                        'funding_status_class': 'secondary',
                        'funding_status_icon': 'fas fa-question-circle'
                    }
            
            elif isinstance(payment_status, dict):
                status_str = payment_status.get('payment_status', '').lower()
                sessions_remaining = payment_status.get('sessions_remaining', 0)
                
                if status_str in ['past_due', 'overdue', 'cancelled']:
                    return {
                        'funding_status': 'unfunded',
                        'funding_status_text': 'Past Due',
                        'funding_status_class': 'danger',
                        'funding_status_icon': 'fas fa-exclamation-triangle'
                    }
                elif status_str in ['current', 'paid', 'active'] and sessions_remaining > 0:
                    return {
                        'funding_status': 'funded',
                        'funding_status_text': f'Funded ({sessions_remaining} sessions)',
                        'funding_status_class': 'success',
                        'funding_status_icon': 'fas fa-check-circle'
                    }
                elif status_str in ['current', 'paid', 'active'] and sessions_remaining == 0:
                    return {
                        'funding_status': 'partial',
                        'funding_status_text': 'No Sessions Left',
                        'funding_status_class': 'warning',
                        'funding_status_icon': 'fas fa-clock'
                    }
                elif status_str in ['pending', 'processing']:
                    return {
                        'funding_status': 'partial',
                        'funding_status_text': 'Payment Pending',
                        'funding_status_class': 'warning',
                        'funding_status_icon': 'fas fa-hourglass-half'
                    }
                else:
                    return {
                        'funding_status': 'unknown',
                        'funding_status_text': 'Status Unknown',
                        'funding_status_class': 'secondary',
                        'funding_status_icon': 'fas fa-question-circle'
                    }
            
            else:
                return {
                    'funding_status': 'unknown',
                    'funding_status_text': 'Status Unknown',
                    'funding_status_class': 'secondary',
                    'funding_status_icon': 'fas fa-question-circle'
                }
                
        except Exception as e:
            logger.error(f"❌ Error classifying funding status: {e}")
            return {
                'funding_status': 'unknown',
                'funding_status_text': 'Error',
                'funding_status_class': 'danger',
                'funding_status_icon': 'fas fa-exclamation-triangle'
            }
    
    def _cache_funding_data(self, funding_data: dict):
        """Save funding data to database cache"""
        try:
            conn = sqlite3.connect(db_manager.db_path)
            cursor = conn.cursor()
            
            # Get member_id from training_clients table
            cursor.execute("""
                SELECT id FROM training_clients 
                WHERE clubos_member_id = ? OR LOWER(member_name) LIKE LOWER(?)
                LIMIT 1
            """, (funding_data['clubos_member_id'], f"%{funding_data['member_name']}%"))
            
            result = cursor.fetchone()
            if result:
                funding_data['member_id'] = result[0]
            
            # Insert or replace the funding data
            columns = ', '.join(funding_data.keys())
            placeholders = ', '.join(['?' for _ in funding_data.values()])
            
            cursor.execute(f"""
                INSERT OR REPLACE INTO funding_status_cache ({columns})
                VALUES ({placeholders})
            """, list(funding_data.values()))
            
            conn.commit()
            conn.close()
            
            logger.info(f"💾 Cached funding data for {funding_data['member_name']}")
            
        except Exception as e:
            logger.error(f"❌ Error caching funding data: {e}")
    
    def _format_funding_response(self, cached_data: dict, is_stale: bool = False, is_cached: bool = True) -> dict:
        """Format cached data for API response"""
        try:
            response = {
                'status_text': cached_data.get('funding_status_text', 'Unknown'),
                'status_class': cached_data.get('funding_status_class', 'secondary'),
                'status_icon': cached_data.get('funding_status_icon', 'fas fa-question-circle'),
                'funding_status': cached_data.get('funding_status', 'unknown'),
                'sessions_remaining': cached_data.get('sessions_remaining', 0),
                'package_name': cached_data.get('package_name'),
                'last_updated': cached_data.get('last_updated'),
                'is_cached': is_cached,
                'is_stale': is_stale
            }
            
            if is_stale:
                response['status_text'] += ' (Cached)'
            else:
                # Heuristic: if data source is direct ClubOS API and we have raw data, treat as fresh
                if cached_data.get('data_source') == 'clubos_api' and cached_data.get('raw_clubos_data') is not None:
                    response['is_cached'] = False
                
            return response
            
        except Exception as e:
            logger.error(f"❌ Error formatting funding response: {e}")
            return None
    
    def refresh_all_funding_cache(self) -> dict:
        """Refresh funding cache for all training clients - run daily"""
        try:
            logger.info("🔄 Starting daily funding cache refresh...")
            
            conn = sqlite3.connect(db_manager.db_path)
            cursor = conn.cursor()
            
            # Get all training clients
            cursor.execute("""
                SELECT id, clubos_member_id, member_name 
                FROM training_clients 
                WHERE clubos_member_id IS NOT NULL
            """)
            
            training_clients = cursor.fetchall()
            conn.close()
            
            success_count = 0
            error_count = 0
            
            for client_id, clubos_id, member_name in training_clients:
                try:
                    logger.info(f"🔄 Refreshing funding for {member_name} (ID: {clubos_id})")
                    
                    fresh_data = self._fetch_fresh_funding_data(str(clubos_id), member_name)
                    if fresh_data:
                        fresh_data['member_id'] = client_id
                        self._cache_funding_data(fresh_data)
                        success_count += 1
                    else:
                        error_count += 1
                        
                except Exception as e:
                    logger.error(f"❌ Error refreshing funding for {member_name}: {e}")
                    error_count += 1
            
            logger.info(f"✅ Funding cache refresh complete: {success_count} success, {error_count} errors")
            
            return {
                'success': True,
                'total_clients': len(training_clients),
                'success_count': success_count,
                'error_count': error_count,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error in daily funding refresh: {e}")
            return {'success': False, 'error': str(e)}
    
    def _get_member_id_from_database(self, participant_name: str, participant_email: str = None, participant_phone: str = None) -> str:
        """Get member ID from local database - now using real database with imported data"""
        try:
            conn = sqlite3.connect(db_manager.db_path)
            cursor = conn.cursor()
            
            # Search in training_clients table first (most specific)
            cursor.execute("""
                SELECT clubos_member_id FROM training_clients 
                WHERE LOWER(member_name) LIKE LOWER(?)
                LIMIT 1
            """, (f"%{participant_name.strip()}%",))
            
            result = cursor.fetchone()
            if result and result[0]:
                conn.close()
                logger.info(f"✅ Found ClubOS ID in training clients: {result[0]} for {participant_name}")
                return str(result[0])
            

            # Assignees fast-path: use ClubOS Assignees page as the authoritative list we can modify
            try:
                idx = self.api.get_assignee_index(force_refresh=False)
                if idx:
                    if participant_email and participant_email.lower() in idx.get('by_email', {}):
                        clubos_id = idx['by_email'][participant_email.lower()]
                        conn.close()
                        logger.info(f"✅ Found ClubOS ID via Assignees (email): {clubos_id} for {participant_name}")
                        return str(clubos_id)
                    # Phone-based lookup via Assignees index
                    if participant_phone:
                        try:
                            norm_ph = self.api._normalize_phone(participant_phone)
                        except Exception:
                            norm_ph = None
                        if norm_ph and norm_ph in idx.get('by_phone', {}):
                            clubos_id = idx['by_phone'][norm_ph]
                            conn.close()
                            logger.info(f"✅ Found ClubOS ID via Assignees (phone): {clubos_id} for {participant_name}")
                            return str(clubos_id)
                    # Name-based fallback using normalized name
                    norm = self.api._normalize_name(participant_name)
                    if norm and norm in idx.get('by_name', {}):
                        clubos_id = idx['by_name'][norm]
                        conn.close()
                        logger.info(f"✅ Found ClubOS ID via Assignees (name): {clubos_id} for {participant_name}")
                        return str(clubos_id)
            except Exception as e:
                logger.debug(f"Assignees index lookup skipped/failed: {e}")
                idx = None
            # If not found via initial Assignees cache, try a forced refresh and retry matches once
            if not result or not (result and result[0]):
                try:
                    if not idx:
                        idx = self.api.get_assignee_index(force_refresh=True)
                    if idx:
                        if participant_email and participant_email.lower() in idx.get('by_email', {}):
                            clubos_id = idx['by_email'][participant_email.lower()]
                            conn.close()
                            logger.info(f"✅ Found ClubOS ID via Assignees REFRESH (email): {clubos_id} for {participant_name}")
                            return str(clubos_id)
                        if participant_phone:
                            try:
                                norm_ph = self.api._normalize_phone(participant_phone)
                            except Exception:
                                norm_ph = None
                            if norm_ph and norm_ph in idx.get('by_phone', {}):
                                clubos_id = idx['by_phone'][norm_ph]
                                conn.close()
                                logger.info(f"✅ Found ClubOS ID via Assignees REFRESH (phone): {clubos_id} for {participant_name}")
                                return str(clubos_id)
                        norm = self.api._normalize_name(participant_name)
                        if norm and norm in idx.get('by_name', {}):
                            clubos_id = idx['by_name'][norm]
                            conn.close()
                            logger.info(f"✅ Found ClubOS ID via Assignees REFRESH (name): {clubos_id} for {participant_name}")
                            return str(clubos_id)
                except Exception as e:
                    logger.debug(f"Forced Assignees refresh failed: {e}")
            
            # Fallback to members table (ClubHub IDs) — do NOT treat as ClubOS IDs
            search_conditions = ["LOWER(first_name) LIKE LOWER(?) OR LOWER(last_name) LIKE LOWER(?) OR LOWER(full_name) LIKE LOWER(?)"]
            params = [f"%{participant_name}%", f"%{participant_name}%", f"%{participant_name}%"]
            
            if participant_email:
                search_conditions.append("LOWER(email) = LOWER(?)")
                params.append(participant_email)
            # Add phone search as a hint to derive email/name for live lookup
            phone_digits = None
            if participant_phone:
                try:
                    phone_digits = self.api._normalize_phone(participant_phone)
                except Exception:
                    phone_digits = None
            
            query = f"""
                SELECT id FROM members 
                WHERE {' OR '.join(search_conditions)}
                LIMIT 1
            """
            
            cursor.execute(query, params)
            result = cursor.fetchone()
            # If no direct name/email match and we have a phone, try to locate a member row by phone to obtain a better email/name for live lookup
            candidate_email = participant_email
            candidate_name = participant_name
            if (not result or not result[0]) and phone_digits:
                try:
                    cursor.execute(
                        """
                        SELECT id, full_name, email, mobile_phone, home_phone, work_phone
                        FROM members
                        WHERE REPLACE(REPLACE(REPLACE(REPLACE(COALESCE(mobile_phone,''), '-', ''), '(', ''), ')', ''), ' ', '') LIKE ?
                           OR REPLACE(REPLACE(REPLACE(REPLACE(COALESCE(home_phone,''), '-', ''), '(', ''), ')', ''), ' ', '') LIKE ?
                           OR REPLACE(REPLACE(REPLACE(REPLACE(COALESCE(work_phone,''), '-', ''), '(', ''), ')', ''), ' ', '') LIKE ?
                        LIMIT 1
                        """,
                        [f"%{phone_digits}%", f"%{phone_digits}%", f"%{phone_digits}%"]
                    )
                    phone_row = cursor.fetchone()
                    if phone_row:
                        candidate_name = phone_row[1] or candidate_name
                        candidate_email = (phone_row[2] or candidate_email)
                        logger.info(f"ℹ️ Found member by phone for {participant_name}; using name/email for live ClubOS search")
                except Exception as e:
                    logger.debug(f"Phone-based members lookup failed: {e}")

            conn.close()
            
            if result and result[0]:
                logger.info(f"ℹ️ Members table has local ID {result[0]} for {participant_name} (ClubHub ID) — performing live ClubOS lookup...")
            else:
                logger.warning(f"❌ No local match for {participant_name} — performing live ClubOS lookup...")

            # Live lookup via ClubOS search endpoints (Charles-captured)
            try:
                # Prefer the best candidate email/name we have at this point; try a couple of attempts
                live_member_id = None
                attempts = [
                    (candidate_name, candidate_email),
                    (participant_name, participant_email),
                    (participant_name, None)
                ]
                for nm, em in attempts:
                    if nm:
                        try:
                            mid = self.api.search_member_id(nm, em, participant_phone)
                            if mid:
                                live_member_id = mid
                                break
                        except Exception:
                            continue
                if live_member_id:
                    logger.info(f"🌐 Live lookup found ClubOS ID {live_member_id} for {participant_name}")
                    return str(live_member_id)
            except Exception as e:
                logger.warning(f"⚠️ Live member lookup failed for {participant_name}: {e}")
            return None
            
        except Exception as e:
            logger.error(f"❌ Database error looking up member ID: {e}")
            return None

    def _resolve_member_id_live(self, participant_name: str, participant_email: str = None) -> str:
        """Resolve ClubOS memberId by scraping the Personal Training dashboard and fuzzy-matching names."""
        try:
            api = ClubOSTrainingClientsAPI()
            if not api.authenticate():
                logger.warning("⚠️ TrainingClients API auth failed for live ID resolution")
                return None

            candidates = []
            # Prefer JSON list if available
            try:
                data = api.get_training_clients()
                if isinstance(data, list):
                    for item in data:
                        name = (item.get('name') or item.get('memberName') or '').strip()
                        mid = item.get('memberId') or item.get('clubos_member_id')
                        if name and mid:
                            candidates.append((name, str(mid)))
                elif isinstance(data, dict):
                    arr = data.get('clients') or data.get('data') or []
                    for item in arr:
                        name = (item.get('name') or item.get('memberName') or '').strip()
                        mid = item.get('memberId') or item.get('clubos_member_id')
                        if name and mid:
                            candidates.append((name, str(mid)))
            except Exception:
                pass

            # Fallback to HTML scraping
            if not candidates:
                html = api.get_personal_training_dashboard()
                if html:
                    soup = BeautifulSoup(html, 'html.parser')
                    for a in soup.find_all('a', href=True):
                        href = a['href']
                        m = re.search(r"memberId=(\d+)", href)
                        if m:
                            name = a.get_text(strip=True)
                            if name:
                                candidates.append((name, m.group(1)))

            if not candidates:
                logger.warning("⚠️ No candidates discovered for live ID resolution")
                return None

            target = participant_name.strip().lower()
            best_mid = None
            best_score = 0.0
            for name, mid in candidates:
                nm = name.strip().lower()
                score = SequenceMatcher(None, target, nm).ratio()
                if score > best_score:
                    best_score = score
                    best_mid = mid

            if best_mid and best_score >= 0.6:
                # Persist mapping for future
                try:
                    conn = sqlite3.connect(db_manager.db_path)
                    cursor = conn.cursor()
                    cursor.execute(
                        """
                        INSERT OR IGNORE INTO training_clients (member_id, clubos_member_id, member_name)
                        VALUES (?, ?, ?)
                        """,
                        (int(best_mid), int(best_mid), participant_name.strip())
                    )
                    conn.commit()
                    conn.close()
                except Exception:
                    pass
                return str(best_mid)

            logger.warning(f"⚠️ Live ID resolution score too low ({best_score:.2f}) for {participant_name}")
            return None
        except Exception as e:
            logger.error(f"❌ Live ID resolution error: {e}")
            return None

# Initialize training package cache
training_package_cache = TrainingPackageCache()

class DatabaseManager:
    """Enhanced Database Manager to handle comprehensive gym data with auto-refresh"""
    
    def __init__(self, db_path='gym_bot.db'):
        self.db_path = db_path
        self.last_refresh = None
        self.refresh_interval = 3600  # 1 hour in seconds
        self.init_database()
        
    def needs_refresh(self):
        """Check if database needs refreshing based on time interval"""
        if self.last_refresh is None:
            return True
        return (datetime.now() - self.last_refresh).total_seconds() > self.refresh_interval
    
    def get_fresh_data_from_clubos(self):
        """Get fresh data from ClubOS APIs"""
        try:
            logger.info("🔄 Fetching fresh data from ClubOS...")
            
            # Use the fresh data API to get real-time data
            fresh_members = clubos_fresh_data_api.get_fresh_members()
            fresh_prospects = clubos_fresh_data_api.get_fresh_prospects()
            summary = clubos_fresh_data_api.get_fresh_data_summary()
            
            fresh_data = {
                'members': fresh_members,
                'prospects': fresh_prospects,
                'summary': summary,
                'updated_at': datetime.now().isoformat()
            }
            
            logger.info("📊 Fresh data fetched successfully")
            return fresh_data
            
        except Exception as e:
            logger.error(f"❌ Error fetching fresh data: {e}")
            return None
    
    def refresh_database(self, force=False):
        """Refresh the database with latest data from ClubOS"""
        if not force and not self.needs_refresh():
            logger.info("⏭️ Database is fresh, skipping refresh")
            return False
            
        logger.info("🔄 Starting database refresh...")
        
        try:
            # Get fresh data from ClubOS
            fresh_data = self.get_fresh_data_from_clubos()
            
            if fresh_data:
                # Update database with fresh data
                self._update_database_with_fresh_data(fresh_data)
                self.last_refresh = datetime.now()
                logger.info("✅ Database refreshed successfully")
                return True
            else:
                # Fallback to existing CSV data but update the timestamp
                logger.warning("⚠️ Using existing CSV data as fallback")
                self.last_refresh = datetime.now()
                return False
                
        except Exception as e:
            logger.error(f"❌ Database refresh failed: {e}")
            return False
    
    def _update_database_with_fresh_data(self, fresh_data):
        """Update database tables with fresh data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Update members with fresh data
            # This would process the fresh_data and update the database
            # For now, we'll update the last_refresh timestamp
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS data_refresh_log (
                    id INTEGER PRIMARY KEY,
                    table_name TEXT,
                    last_refresh TIMESTAMP,
                    record_count INTEGER
                )
            """)
            
            # Log the refresh
            cursor.execute("""
                INSERT OR REPLACE INTO data_refresh_log (id, table_name, last_refresh, record_count)
                VALUES (1, 'members', ?, (SELECT COUNT(*) FROM members))
            """, (datetime.now(),))
            
            cursor.execute("""
                INSERT OR REPLACE INTO data_refresh_log (id, table_name, last_refresh, record_count)
                VALUES (2, 'prospects', ?, (SELECT COUNT(*) FROM prospects))
            """, (datetime.now(),))
            
            conn.commit()
            
        except Exception as e:
            logger.error(f"❌ Error updating database: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def get_refresh_status(self):
        """Get the last refresh status for each table"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT table_name, last_refresh, record_count 
                FROM data_refresh_log 
                ORDER BY table_name
            """)
            
            refresh_status = {}
            for row in cursor.fetchall():
                refresh_status[row[0]] = {
                    'last_refresh': row[1],
                    'record_count': row[2],
                    'age_minutes': (datetime.now() - datetime.fromisoformat(row[1])).total_seconds() / 60 if row[1] else None
                }
            
            conn.close()
            return refresh_status
            
        except Exception as e:
            logger.error(f"❌ Error getting refresh status: {e}")
            return {}
        
    def init_database(self):
        """Initialize the database with proper schema matching CSV data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Drop existing tables to recreate with new schema
        cursor.execute('DROP TABLE IF EXISTS members')
        cursor.execute('DROP TABLE IF EXISTS prospects')
        cursor.execute('DROP TABLE IF EXISTS training_clients')
        
        # Enhanced members table matching CSV structure
        cursor.execute('''
            CREATE TABLE members (
                id INTEGER PRIMARY KEY,
                guid TEXT,
                club_id INTEGER,
                first_name TEXT,
                last_name TEXT,
                full_name TEXT,
                email TEXT,
                mobile_phone TEXT,
                home_phone TEXT,
                work_phone TEXT,
                address1 TEXT,
                address2 TEXT,
                city TEXT,
                state TEXT,
                zip_code TEXT,
                country TEXT,
                date_of_birth TEXT,
                gender TEXT,
                membership_start TEXT,
                membership_end TEXT,
                last_visit TEXT,
                status TEXT,
                status_message TEXT,
                user_type TEXT,
                key_fob TEXT,
                photo_url TEXT,
                
                -- Home Club Information
                home_club_name TEXT,
                home_club_address TEXT,
                home_club_city TEXT,
                home_club_state TEXT,
                home_club_zip TEXT,
                home_club_af_number TEXT,
                
                -- Agreement Information (from CSV)
                agreement_id TEXT,
                agreement_guid TEXT,
                agreement_status TEXT,
                agreement_start_date TEXT,
                agreement_end_date TEXT,
                agreement_type TEXT,
                agreement_rate REAL,
                payment_amount REAL,  -- Add missing payment_amount column
                amount_past_due REAL,
                amount_of_next_payment REAL,
                date_of_next_payment TEXT,
                
                -- Payment Information (from CSV)
                payment_token TEXT,
                card_type TEXT,
                card_last4 TEXT,
                expiration_month TEXT,
                expiration_year TEXT,
                billing_name TEXT,
                billing_address TEXT,
                billing_city TEXT,
                billing_state TEXT,
                billing_zip TEXT,
                account_type TEXT,
                routing_number TEXT,
                
                -- Additional Fields from CSV
                emergency_contact TEXT,
                emergency_phone TEXT,
                employer TEXT,
                occupation TEXT,
                has_app BOOLEAN DEFAULT 0,
                last_activity_timestamp TEXT,
                contract_types TEXT,
                bucket INTEGER,
                color INTEGER,
                rating INTEGER,
                source TEXT,
                trial BOOLEAN DEFAULT 0,
                originated_from TEXT,
                female BOOLEAN,
                contact_type TEXT,
                biller_message TEXT,
                
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Enhanced prospects table
        cursor.execute('''
            CREATE TABLE prospects (
                id INTEGER PRIMARY KEY,
                guid TEXT,
                club_id INTEGER,
                first_name TEXT,
                last_name TEXT,
                full_name TEXT,
                email TEXT,
                mobile_phone TEXT,
                home_phone TEXT,
                work_phone TEXT,
                address1 TEXT,
                address2 TEXT,
                city TEXT,
                state TEXT,
                zip_code TEXT,
                country TEXT,
                date_of_birth TEXT,
                gender TEXT,
                status TEXT,
                status_message TEXT,
                user_type TEXT,  -- Add missing user_type column
                key_fob TEXT,    -- Add missing key_fob column
                photo_url TEXT,  -- Add missing photo_url column
                
                -- Additional fields that prospects can have
                emergency_contact TEXT,
                emergency_phone TEXT,
                employer TEXT,
                occupation TEXT,
                has_app BOOLEAN DEFAULT 0,
                last_activity_timestamp TEXT,
                contract_types TEXT,
                membership_start TEXT,
                membership_end TEXT,
                last_visit TEXT,
                
                -- Prospect-specific fields
                lead_source TEXT,
                interest_level INTEGER,
                follow_up_date TEXT,
                notes TEXT,
                trial_session_date TEXT,
                tour_completed BOOLEAN DEFAULT 0,
                
                -- Contact preferences
                preferred_contact_method TEXT,
                best_time_to_call TEXT,
                
                -- Additional tracking from CSV
                bucket INTEGER,
                color INTEGER,
                rating INTEGER,
                source TEXT,
                trial BOOLEAN DEFAULT 1,
                originated_from TEXT,
                female BOOLEAN,
                contact_type TEXT,
                
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Training clients table matching CSV structure
        cursor.execute('''
            CREATE TABLE training_clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id TEXT,  -- ID from CSV (e.g., "1707989-175560157")
                member_id INTEGER,  -- ClubOS member ID (e.g., 175560157)
                clubos_member_id INTEGER,  -- Same as member_id but with more explicit name
                member_name TEXT,  -- Add missing member_name column
                profile_url TEXT,
                member_location TEXT,
                agreement_location TEXT,
                agreement_name TEXT,
                next_invoice_subtotal REAL,
                member_services TEXT,
                renew_type TEXT,
                bill_cycle TEXT,
                agreement_expiration_date TEXT,
                assigned_trainers TEXT,
                trainer_name TEXT,  -- Primary trainer
                session_type TEXT,
                sessions_remaining INTEGER DEFAULT 0,
                last_session TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (member_id) REFERENCES members (id)
            )
        ''')
        
        # Funding status cache table - stores real funding data from ClubOS
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS funding_status_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                member_id INTEGER,
                member_name TEXT,
                clubos_member_id INTEGER,
                
                -- Training package details
                package_name TEXT,
                sessions_remaining INTEGER DEFAULT 0,
                sessions_purchased INTEGER DEFAULT 0,
                package_amount REAL,
                amount_paid REAL,
                amount_remaining REAL,
                
                -- Payment status
                payment_status TEXT,  -- 'current', 'past_due', 'pending', 'cancelled'
                payment_method TEXT,
                last_payment_date TEXT,
                next_payment_date TEXT,
                
                -- Funding status classification
                funding_status TEXT,  -- 'funded', 'unfunded', 'partial', 'unknown'
                funding_status_text TEXT,  -- Human readable status
                funding_status_class TEXT,  -- CSS class (success, warning, danger, secondary)
                funding_status_icon TEXT,  -- FontAwesome icon class
                
                -- Cache metadata
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data_source TEXT DEFAULT 'clubos_api',  -- Track where data came from
                is_stale BOOLEAN DEFAULT 0,  -- Flag for stale data
                
                -- Raw ClubOS data (JSON)
                raw_clubos_data TEXT,  -- Store full API response as JSON
                
                UNIQUE(member_id, clubos_member_id),
                FOREIGN KEY (member_id) REFERENCES training_clients (member_id)
            )
        ''')
        
        # Member transactions table for invoice and payment tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS member_transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                member_id INTEGER,
                clubos_member_id INTEGER,
                member_name TEXT,
                type TEXT,  -- 'invoice', 'payment', 'refund', 'fee'
                amount REAL,
                invoice_id TEXT,  -- Square invoice ID or external reference
                status TEXT,  -- 'pending', 'sent', 'paid', 'failed', 'cancelled'
                description TEXT,
                payment_method TEXT,  -- 'square', 'cash', 'check', 'other'
                square_data TEXT,  -- JSON data from Square API
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                meta_json TEXT,  -- Additional metadata as JSON
                
                FOREIGN KEY (member_id) REFERENCES members (id)
            )
        ''')
        
        # Message threads table for organizing conversations
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS message_threads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                member_id INTEGER,
                clubos_member_id INTEGER,
                member_name TEXT,
                thread_type TEXT,  -- 'clubos', 'sms', 'email', 'bot'
                thread_subject TEXT,
                external_thread_id TEXT,  -- ID from external system (ClubOS, SMS service, etc.)
                status TEXT,  -- 'active', 'archived', 'closed'
                last_message_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                FOREIGN KEY (member_id) REFERENCES members (id)
            )
        ''')
        
        # Messages table for individual messages within threads
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                thread_id INTEGER,
                member_id INTEGER,
                sender_type TEXT,  -- 'member', 'staff', 'system', 'bot'
                sender_name TEXT,
                sender_email TEXT,
                message_content TEXT,
                message_type TEXT,  -- 'text', 'image', 'file', 'system'
                external_message_id TEXT,  -- ID from external system
                direction TEXT,  -- 'inbound', 'outbound'
                status TEXT,  -- 'sent', 'delivered', 'read', 'failed'
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                read_at TIMESTAMP,
                metadata_json TEXT,  -- Additional metadata as JSON
                
                FOREIGN KEY (thread_id) REFERENCES message_threads (id),
                FOREIGN KEY (member_id) REFERENCES members (id)
            )
        ''')
        
        # Bulk check-in tracking table for resume on restart functionality
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bulk_checkin_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT UNIQUE,  -- UUID for tracking specific runs
                status TEXT,  -- 'running', 'completed', 'failed', 'paused'
                total_members INTEGER DEFAULT 0,
                processed_members INTEGER DEFAULT 0,
                successful_checkins INTEGER DEFAULT 0,
                failed_checkins INTEGER DEFAULT 0,
                excluded_ppv INTEGER DEFAULT 0,
                excluded_other INTEGER DEFAULT 0,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                error_message TEXT,
                resume_data_json TEXT  -- JSON data for resuming interrupted runs
            )
        ''')
        
        # Daily report cache table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                report_date DATE UNIQUE,
                bulk_checkins_count INTEGER DEFAULT 0,
                campaigns_sent INTEGER DEFAULT 0,
                replies_received INTEGER DEFAULT 0,
                invoices_created INTEGER DEFAULT 0,
                invoices_paid INTEGER DEFAULT 0,
                appointments_completed INTEGER DEFAULT 0,
                appointments_rescheduled INTEGER DEFAULT 0,
                new_members INTEGER DEFAULT 0,
                member_visits INTEGER DEFAULT 0,
                revenue_collected REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data_json TEXT  -- Additional metrics as JSON
            )
        ''')
        
        # Create indexes for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_funding_cache_member_id ON funding_status_cache(member_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_funding_cache_clubos_id ON funding_status_cache(clubos_member_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_funding_cache_updated ON funding_status_cache(last_updated)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_funding_cache_stale ON funding_status_cache(is_stale)')
        
        # Indexes for new tables
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_member_transactions_member_id ON member_transactions(member_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_member_transactions_type ON member_transactions(type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_member_transactions_status ON member_transactions(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_member_transactions_created ON member_transactions(created_at)')
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_message_threads_member_id ON message_threads(member_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_message_threads_type ON message_threads(thread_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_message_threads_status ON message_threads(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_message_threads_last_message ON message_threads(last_message_at)')
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_thread_id ON messages(thread_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_member_id ON messages(member_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_created ON messages(created_at)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_direction ON messages(direction)')
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_bulk_checkin_runs_status ON bulk_checkin_runs(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_bulk_checkin_runs_started ON bulk_checkin_runs(started_at)')
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_daily_reports_date ON daily_reports(report_date)')
        
        conn.commit()
        conn.close()
        
    def import_master_contact_list(self, csv_path):
        """Import master contact list from CSV with comprehensive data"""
        if not os.path.exists(csv_path):
            logger.warning(f"📋 Master contact list not found: {csv_path}")
            return 0, 0
            
        logger.info(f"📊 Importing master contact list from: {csv_path}")
        
        try:
            df = pd.read_csv(csv_path)
            logger.info(f"📋 Found {len(df)} records in CSV")
        except Exception as e:
            logger.error(f"❌ Error reading CSV: {e}")
            return 0, 0
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Clear existing data
        cursor.execute('DELETE FROM members')
        cursor.execute('DELETE FROM prospects')
        
        members_count = 0
        prospects_count = 0
        
        for _, row in df.iterrows():
            try:
                # Determine if this is a member or prospect
                is_prospect = str(row.get('prospect', 'False')).lower() == 'true'
                
                # Common fields - map CSV columns to database fields
                common_data = {
                    'id': row.get('id'),
                    'guid': row.get('guid'),
                    'club_id': row.get('clubId'),
                    'first_name': row.get('firstName'),
                    'last_name': row.get('lastName'),
                    'full_name': f"{row.get('firstName', '')} {row.get('lastName', '')}".strip(),
                    'email': row.get('email'),
                    'mobile_phone': row.get('mobilePhone'),
                    'home_phone': row.get('homePhone'),
                    'work_phone': row.get('workPhone'),
                    'address1': row.get('address1'),
                    'address2': row.get('address2'),
                    'city': row.get('city'),
                    'state': row.get('state'),
                    'zip_code': row.get('zip'),
                    'country': row.get('country'),
                    'date_of_birth': row.get('dateOfBirth'),
                    'gender': row.get('gender'),
                    'status': row.get('status'),
                    'status_message': row.get('statusMessage'),
                    'bucket': row.get('bucket'),
                    'color': row.get('color'),
                    'rating': row.get('rating'),
                    'source': row.get('source'),
                    'trial': str(row.get('trial', 'False')).lower() == 'true',
                    'originated_from': row.get('originatedFrom'),
                    'female': str(row.get('female', 'False')).lower() == 'true',
                    'contact_type': row.get('contact_type'),
                    'user_type': row.get('userType'),
                    'key_fob': row.get('keyFob'),
                    'photo_url': row.get('photoUrl'),
                    'emergency_contact': row.get('emergencyContact'),
                    'emergency_phone': row.get('emergencyPhone'),
                    'employer': row.get('employer'),
                    'occupation': row.get('occupation'),
                    'has_app': str(row.get('hasApp', 'False')).lower() == 'true',
                    'last_activity_timestamp': row.get('lastActivityTimestamp'),
                    'contract_types': row.get('contractTypes'),
                    'membership_start': row.get('membershipStart'),
                    'membership_end': row.get('membershipEnd'),
                    'last_visit': row.get('lastVisit')
                }
                
                if is_prospect:
                    # Insert as prospect
                    prospect_data = {
                        **common_data,
                        'lead_source': row.get('source'),
                        'interest_level': row.get('rating', 0),
                        'notes': row.get('statusMessage', ''),
                    }
                    
                    # Remove None values and prepare for insert
                    prospect_data = {k: v for k, v in prospect_data.items() if v is not None}
                    columns = ', '.join(prospect_data.keys())
                    placeholders = ', '.join(['?' for _ in prospect_data.values()])
                    
                    cursor.execute(f'''
                        INSERT OR REPLACE INTO prospects ({columns})
                        VALUES ({placeholders})
                    ''', list(prospect_data.values()))
                    
                    prospects_count += 1
                    
                else:
                    # Insert as member with agreement data
                    member_data = {
                        **common_data,
                        # Agreement fields
                        'agreement_id': row.get('agreement_agreementID'),
                        'agreement_guid': row.get('agreement_agreementGuid'),
                        'agreement_type': row.get('agreement_agreementType'),
                        'payment_amount': self._extract_payment_amount(row.get('agreement_recurringCost')),
                        'amount_past_due': row.get('agreement_amountPastDue'),
                        'amount_of_next_payment': row.get('agreement_amountOfNextPayment'),
                        'date_of_next_payment': row.get('agreement_dateOfNextPayment'),
                        
                        # Payment token fields
                        'payment_token': row.get('agreementTokenQuery_paymentToken'),
                        'card_type': row.get('agreementTokenQuery_cardType'),
                        'account_type': row.get('agreementTokenQuery_accountType'),
                        'billing_name': row.get('agreementTokenQuery_holderName'),
                        'billing_address': row.get('agreementTokenQuery_holderStreet'),
                        'billing_city': row.get('agreementTokenQuery_holderCity'),
                        'billing_state': row.get('agreementTokenQuery_holderState'),
                        'billing_zip': row.get('agreementTokenQuery_holderZip'),
                        'routing_number': row.get('agreementTokenQuery_routingNumber'),
                        'expiration_month': row.get('agreementTokenQuery_expirationMonth'),
                        'expiration_year': row.get('agreementTokenQuery_expirationYear'),
                        
                        # Home club info
                        'home_club_name': row.get('homeClub_name'),
                        'home_club_address': row.get('homeClub_address1'),
                        'home_club_city': row.get('homeClub_city'),
                        'home_club_state': row.get('homeClub_state'),
                        'home_club_zip': row.get('homeClub_zip'),
                        'home_club_af_number': row.get('homeClub_afNumber'),
                        
                        'biller_message': row.get('billerMessage')
                    }
                    
                    # Remove None values and prepare for insert
                    member_data = {k: v for k, v in member_data.items() if v is not None}
                    columns = ', '.join(member_data.keys())
                    placeholders = ', '.join(['?' for _ in member_data.values()])
                    
                    cursor.execute(f'''
                        INSERT OR REPLACE INTO members ({columns})
                        VALUES ({placeholders})
                    ''', list(member_data.values()))
                    
                    members_count += 1
                    
            except Exception as e:
                logger.error(f"❌ Error importing row {row.get('id', 'unknown')}: {e}")
                continue
        
        conn.commit()
        conn.close()
        
        logger.info(f"✅ Import complete: {members_count} members, {prospects_count} prospects")
        return members_count, prospects_count
    
    def _extract_payment_amount(self, recurring_cost_str):
        """Extract payment amount from recurring cost string/dict"""
        try:
            if isinstance(recurring_cost_str, str):
                # Try to parse JSON-like string
                import json
                if recurring_cost_str.startswith('{'):
                    cost_dict = json.loads(recurring_cost_str.replace("'", '"'))
                    return cost_dict.get('total', 0.0)
            elif isinstance(recurring_cost_str, dict):
                return recurring_cost_str.get('total', 0.0)
            elif isinstance(recurring_cost_str, (int, float)):
                return float(recurring_cost_str)
        except:
            pass
        return None
    
    def import_training_clients(self, csv_path):
        """Import training clients from CSV"""
        if not os.path.exists(csv_path):
            logger.warning(f"🏋️ Training clients CSV not found: {csv_path}")
            return 0
            
        logger.info(f"🏋️ Importing training clients from: {csv_path}")
        
        try:
            df = pd.read_csv(csv_path)
            logger.info(f"🏋️ Found {len(df)} training clients in CSV")
        except Exception as e:
            logger.error(f"❌ Error reading training clients CSV: {e}")
            return 0
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Clear existing training clients
        cursor.execute('DELETE FROM training_clients')
        
        clients_count = 0
        
        for _, row in df.iterrows():
            try:
                # Extract member ID from the compound ID (e.g., "1707989-175560157" -> 175560157)
                client_id = row.get('ID', '')
                member_id = None
                if '-' in client_id:
                    try:
                        member_id = int(client_id.split('-')[1])
                    except (ValueError, IndexError):
                        pass
                
                # Parse trainers
                trainers = row.get('Assigned Trainers', '')
                primary_trainer = trainers.split(',')[0].strip() if trainers else 'Jeremy Mayo'
                
                client_data = {
                    'client_id': client_id,
                    'member_id': member_id,
                    'clubos_member_id': member_id,  # Same value for lookups
                    'member_name': row.get('Member Name'),
                    'profile_url': row.get('Profile'),
                    'member_location': row.get('Member Location'),
                    'agreement_location': row.get('Agreement Location'),
                    'agreement_name': row.get('Agreement Name'),
                    'next_invoice_subtotal': row.get('Next Invoice Subtotal'),
                    'member_services': row.get('Member Services'),
                    'renew_type': row.get('Renew Type'),
                    'bill_cycle': row.get('Bill Cycle'),
                    'agreement_expiration_date': row.get('Agreement Expiration Date'),
                    'assigned_trainers': trainers,
                    'trainer_name': primary_trainer,
                    'session_type': row.get('Agreement Name'),  # Use agreement name as session type
                    'sessions_remaining': 0  # We'll need to get this from ClubOS API
                }
                
                # Remove None values
                client_data = {k: v for k, v in client_data.items() if v is not None}
                columns = ', '.join(client_data.keys())
                placeholders = ', '.join(['?' for _ in client_data.values()])
                
                cursor.execute(f'''
                    INSERT OR REPLACE INTO training_clients ({columns})
                    VALUES ({placeholders})
                ''', list(client_data.values()))
                
                clients_count += 1
                
            except Exception as e:
                logger.error(f"❌ Error importing training client {row.get('Member Name', 'unknown')}: {e}")
                continue
        
        conn.commit()
        conn.close()
        
        logger.info(f"✅ Training clients import complete: {clients_count} clients")
        return clients_count

# Initialize database manager and import data
db_manager = DatabaseManager()

# Only import CSV data if database is empty (first time setup)
conn = sqlite3.connect(db_manager.db_path)
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM members")
existing_members = cursor.fetchone()[0]
conn.close()

# Always import fresh data from ClubHub API instead of old CSV files
print("🔄 Loading fresh data from ClubHub API...")

def import_fresh_clubhub_data():
    """Import fresh data from ClubHub API on startup"""
    try:
        # Import ClubHub API client
        sys.path.append(os.path.join(os.path.dirname(__file__), 'services'))
        from api.clubhub_api_client import ClubHubAPIClient
        from config.clubhub_credentials import CLUBHUB_EMAIL, CLUBHUB_PASSWORD
        
        # Initialize and authenticate
        client = ClubHubAPIClient()
        if not client.authenticate(CLUBHUB_EMAIL, CLUBHUB_PASSWORD):
            print("❌ ClubHub authentication failed - using existing database")
            return
        
        print("✅ ClubHub authenticated - importing fresh member data...")
        
        # Get all members from ClubHub
        all_members = []
        page = 1
        page_size = 100
        
        while True:
            members_response = client.get_all_members(page=page, page_size=page_size)
            
            if not members_response or not isinstance(members_response, list):
                break
                
            all_members.extend(members_response)
            page += 1
            
            # If we got less than page_size, we've reached the end
            if len(members_response) < page_size:
                break
        
        print(f"📥 Retrieved {len(all_members)} members from ClubHub")
        
        # Clear existing data and import fresh data
        conn = sqlite3.connect(db_manager.db_path)
        cursor = conn.cursor()
        
        # Clear old data
        cursor.execute("DELETE FROM members")
        cursor.execute("DELETE FROM training_clients")
        print("�️ Cleared old data")
        
        # Import fresh member data
        members_added = 0
        training_clients_added = 0
        
        for member in all_members:
            # Add to members table using correct column names
            cursor.execute("""
                INSERT OR REPLACE INTO members (
                    id, guid, first_name, last_name, full_name, email, mobile_phone, 
                    status, status_message, membership_start, membership_end, last_visit
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                member.get('id'),
                member.get('guid'),
                member.get('firstName', ''),
                member.get('lastName', ''),
                f"{member.get('firstName', '')} {member.get('lastName', '')}".strip(),
                member.get('email', ''),
                member.get('mobilePhone', ''),
                member.get('status', ''),
                member.get('statusMessage', ''),
                member.get('membershipStart', ''),
                member.get('membershipEnd', ''),
                member.get('lastVisit', '')
            ))
            members_added += 1
            
            # For now, don't auto-detect training clients from ClubHub
            # Training clients need to come from ClubOS, not ClubHub
            # ClubHub only has membership data, not training package data
        
        conn.commit()
        conn.close()
        
        print(f"✅ Fresh data imported: {members_added} members, {training_clients_added} training clients")
        
    except Exception as e:
        print(f"❌ Error importing fresh data: {e}")
        print("📊 Continuing with existing database...")

# Call the import function to load fresh data on startup
import_fresh_clubhub_data()

class ClubOSIntegration:
    """Integration class to connect dashboard with working ClubOS API"""
    
    def __init__(self):
        from config.clubhub_credentials_clean import CLUBOS_USERNAME, CLUBOS_PASSWORD
        self.api = ClubOSRealCalendarAPI(CLUBOS_USERNAME, CLUBOS_PASSWORD)
        self.training_api = ClubOSTrainingPackageAPI()  # No parameters needed
        self.event_manager = ClubOSEventDeletion()
        self.authenticated = False
        
    def authenticate(self):
        """Authenticate with ClubOS"""
        try:
            # Authenticate both calendar and training APIs
            calendar_auth = self.api.authenticate()
            training_auth = self.training_api.authenticate()
            
            self.authenticated = calendar_auth and training_auth
            
            if self.authenticated:
                # Also authenticate the event manager
                self.event_manager.authenticated = True
                logger.info("✅ ClubOS authentication successful")
            else:
                logger.warning("⚠️ ClubOS authentication partially failed")
                
            return self.authenticated
        except Exception as e:
            logger.error(f"❌ ClubOS authentication failed: {e}")
            return False
    
    def get_live_events(self):
        """Get live calendar events with REAL dates, times, and participant names using iCal"""
        try:
            print("🌟 USING iCAL METHOD FOR REAL EVENT DATA...")
            
            # Use the iCal calendar sync URL found in ClubOS
            calendar_sync_url = "https://anytime.club-os.com/CalendarSync/4984a5b2aac135a95b6bc173054e95716b27e6b9"
            ical_parser = iCalClubOSParser(calendar_sync_url)
            
            # Get real events from iCal feed
            real_events = ical_parser.get_real_events()
            
            formatted_events = []
            for event in real_events:
                # Format the real event data for display
                attendee_names = [attendee['name'] for attendee in event.attendees if attendee['name']]
                attendee_emails = [attendee['email'] for attendee in event.attendees if attendee['email']]
                
                # Check if this event contains training clients (not just appointments)
                is_training_session = self._is_training_session(attendee_names)
                
                # Get training package status ONLY for training sessions, not appointments
                participant_funding_status = []
                for i, name in enumerate(attendee_names):
                    email = attendee_emails[i] if i < len(attendee_emails) else None
                    
                    if is_training_session:
                        # This is a training session - check funding status
                        try:
                            funding_data = training_package_cache.lookup_participant_funding(name, email)
                            if funding_data:  # Only add if we have REAL data
                                participant_funding_status.append({
                                    'name': name,
                                    'email': email,
                                    'status': funding_data.get('status'),
                                    'status_text': funding_data.get('status_text'),
                                    'status_class': funding_data.get('status_class'),
                                    'status_icon': funding_data.get('status_icon'),
                                    'is_training_client': True
                                })
                            else:
                                # No real data available for training client
                                participant_funding_status.append({
                                    'name': name,
                                    'email': email,
                                    'status': None,
                                    'status_text': 'Unknown',
                                    'status_class': 'secondary',
                                    'status_icon': 'fas fa-question-circle',
                                    'is_training_client': True
                                })
                        except Exception as e:
                            logger.warning(f"❌ Could not get funding status for training client {name}: {e}")
                            participant_funding_status.append({
                                'name': name,
                                'email': email,
                                'status': None,
                                'status_text': 'Error',
                                'status_class': 'danger',
                                'status_icon': 'fas fa-exclamation-triangle',
                                'is_training_client': True
                            })
                    else:
                        # This is an appointment - don't check funding status
                        participant_funding_status.append({
                            'name': name,
                            'email': email,
                            'status': None,
                            'status_text': None,
                            'status_class': None,
                            'status_icon': None,
                            'is_training_client': False
                        })
                
                formatted_event = {
                    'id': event.uid,
                    'title': event.summary or 'Training Session',
                    'start_time': event.start_time.strftime('%B %d, %Y at %I:%M %p'),
                    'end_time': event.end_time.strftime('%I:%M %p'),
                    'participants': ', '.join(attendee_names) if attendee_names else 'No participants listed',
                    'participant_emails': ', '.join(attendee_emails) if attendee_emails else '',
                    'participant_funding': participant_funding_status,  # Add funding status data
                    'status': 'Scheduled',
                    'service_type': 'Personal Training',
                    'trainer': 'Jeremy Mayo',
                    'raw_start': event.start_time,
                    'raw_end': event.end_time
                }
                formatted_events.append(formatted_event)
            
            logger.info(f"✅ Successfully extracted {len(formatted_events)} REAL events with actual times and names!")
            
            # Sort events by start time
            formatted_events.sort(key=lambda x: x['raw_start'])
            
            return formatted_events
            
        except Exception as e:
            logger.error(f"❌ Error getting live events via iCal: {e}")
            return []
    
    def get_todays_events_lightweight(self):
        """Get only today's calendar events WITHOUT funding status checks for fast dashboard loading"""
        try:
            print("🌟 GETTING TODAY'S EVENTS ONLY (LIGHTWEIGHT)...")
            
            # Use the iCal calendar sync URL
            calendar_sync_url = "https://anytime.club-os.com/CalendarSync/4984a5b2aac135a95b6bc173054e95716b27e6b9"
            ical_parser = iCalClubOSParser(calendar_sync_url)
            
            # Get real events from iCal feed
            real_events = ical_parser.get_real_events()
            
            # Filter for TODAY ONLY
            today_date = datetime.now().date()
            today_events = []
            
            for event in real_events:
                if event.start_time.date() == today_date:
                    # Get attendee names and convert emails to proper names
                    attendee_names = []
                    for attendee in event.attendees:
                        if attendee['name']:
                            # Check if it's an email address
                            if '@' in attendee['name']:
                                # Look up proper name from database
                                proper_name = self._lookup_member_name_by_email(attendee['name'])
                                if proper_name:
                                    attendee_names.append(proper_name)
                                else:
                                    # Fallback: extract name from email
                                    email_name = attendee['name'].split('@')[0].replace('.', ' ').title()
                                    attendee_names.append(email_name)
                            else:
                                attendee_names.append(attendee['name'])
                    
                    formatted_event = {
                        'id': event.uid,
                        'title': event.summary or 'Training Session',
                        'start_time': event.start_time.strftime('%B %d, %Y at %I:%M %p'),
                        'end_time': event.end_time.strftime('%I:%M %p'),
                        'participants': ', '.join(attendee_names) if attendee_names else 'No participants listed',
                        'status': 'Scheduled',
                        'service_type': 'Personal Training',
                        'trainer': 'Jeremy Mayo',
                        'raw_start': event.start_time,
                        'raw_end': event.end_time,
                        'funding_loaded': False  # Flag to indicate funding not yet loaded
                    }
                    today_events.append(formatted_event)
            
            # Sort by start time
            today_events.sort(key=lambda x: x['raw_start'])
            
            logger.info(f"✅ Got {len(today_events)} events for today (lightweight)")
            return today_events
            
        except Exception as e:
            logger.error(f"❌ Error getting today's events: {e}")
            return []
    
    def _lookup_member_name_by_email(self, email: str) -> str:
        """Look up proper member name (first + last) from database using email"""
        try:
            conn = sqlite3.connect(db_manager.db_path)
            cursor = conn.cursor()
            
            # First check members table
            cursor.execute("""
                SELECT first_name, last_name, full_name FROM members 
                WHERE LOWER(email) = LOWER(?)
                LIMIT 1
            """, (email.strip(),))
            
            result = cursor.fetchone()
            if result:
                first_name, last_name, full_name = result
                conn.close()
                
                # Return the best available name format
                if first_name and last_name:
                    return f"{first_name} {last_name}".strip()
                elif full_name:
                    return full_name.strip()
                elif first_name:
                    return first_name.strip()
                elif last_name:
                    return last_name.strip()
            
            # Then check training_clients table
            cursor.execute("""
                SELECT member_name FROM training_clients 
                WHERE LOWER(email) = LOWER(?) OR LOWER(member_name) LIKE LOWER(?)
                LIMIT 1
            """, (email.strip(), f"%{email.split('@')[0]}%"))
            
            result = cursor.fetchone()
            conn.close()
            
            if result and result[0]:
                return result[0].strip()
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error looking up member name by email {email}: {e}")
            return None
    
    def _is_training_session(self, attendee_names):
        """Check if event attendees include training clients from our database"""
        if not attendee_names:
            return False
        
        try:
            conn = sqlite3.connect(db_manager.db_path)
            cursor = conn.cursor()
            
            for name in attendee_names:
                # Check if this person is in our training_clients table
                cursor.execute("""
                    SELECT COUNT(*) FROM training_clients 
                    WHERE LOWER(member_name) LIKE LOWER(?)
                """, (f"%{name.strip()}%",))
                
                result = cursor.fetchone()
                if result and result[0] > 0:
                    conn.close()
                    return True
            
            conn.close()
            return False
            
        except Exception as e:
            logger.error(f"Error checking if training session: {e}")
            return False
    
    def get_member_payment_status(self, member_id):
        """Get payment status for a member using the training API"""
        try:
            return self.training_api.get_member_payment_status(member_id)
        except Exception as e:
            logger.error(f"❌ Error getting payment status for member {member_id}: {e}")
            return None

# Initialize ClubOS integration
clubos = ClubOSIntegration()

@app.route('/')
def dashboard():
    """Main dashboard with overview."""
    print("=== DASHBOARD ROUTE TRIGGERED ===")
    
    # Check if we need to refresh data (but don't block the dashboard load)
    if db_manager.needs_refresh():
        logger.info("⚠️ Database data is stale, consider refreshing")
    
    # Get real data from database
    conn = sqlite3.connect(db_manager.db_path)
    cursor = conn.cursor()
    
    # Get actual counts from database
    cursor.execute("SELECT COUNT(*) FROM members")
    total_members = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM prospects")
    total_prospects = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM training_clients")
    total_training_clients = cursor.fetchone()[0]
    
    # Get recent data for display
    cursor.execute("SELECT first_name, last_name, email, status FROM members ORDER BY created_at DESC LIMIT 5")
    recent_members_data = cursor.fetchall()
    recent_members = [{'first_name': row[0], 'last_name': row[1], 'email': row[2], 'status': row[3]} for row in recent_members_data]
    
    cursor.execute("SELECT first_name, last_name, email, status FROM prospects ORDER BY created_at DESC LIMIT 5")
    recent_prospects_data = cursor.fetchall()
    recent_prospects = [{'first_name': row[0], 'last_name': row[1], 'email': row[2], 'status': row[3]} for row in recent_prospects_data]
    
    conn.close()
    
    print(f"📊 Database Stats: {total_members} members, {total_prospects} prospects, {total_training_clients} training clients")
    
    # Get live data from ClubOS - ONLY TODAY'S EVENTS (LIGHTWEIGHT)
    print("=== STARTING CLUBOS INTEGRATION (LIGHTWEIGHT) ===")
    today_events = []
    clubos_status = "Disconnected"
    
    try:
        print("=== GETTING TODAY'S EVENTS WITHOUT FUNDING CHECKS ===")
        
        # Get today's events lightweight (no authentication needed for iCal)
        today_events = clubos.get_todays_events_lightweight()
        print(f"=== GOT {len(today_events)} TODAY'S EVENTS (LIGHTWEIGHT) ===")
                        
        clubos_status = "Connected" if today_events else "No events today"
    except Exception as e:
        print(f"=== CLUBOS ERROR: {e} ===")
        logger.error(f"ClubOS connection error: {e}")
        clubos_status = f"Error: {str(e)[:50]}..."
    
    # Get current sync time
    sync_time = datetime.now()
    
    # Categorize events for new metrics
    training_sessions_count = 0
    appointments_count = 0
    
    appointment_keywords = ['consult', 'meeting', 'appointment', 'tour', 'assessment', 'savannah']
    
    for event in today_events:
        title = event.get('title', '').lower()
        participants = event.get('participants', [])
        participant_name = participants[0].lower() if participants and participants[0] else ''
        
        # Check if it's an appointment based on multiple criteria
        is_appointment = (
            any(keyword in title for keyword in appointment_keywords) or
            'savannah' in participant_name or
            'savannah' in title or
            not participants or participants[0] == ''
        )
        
        if is_appointment:
            appointments_count += 1
        else:
            training_sessions_count += 1
    
    # Mock bot activity data (placeholder until real bot integration)
    bot_activities = [
        {
            'id': 1,
            'action': 'Sent Welcome Message',
            'recipient': 'Sarah Johnson',
            'preview': 'Welcome to Anytime Fitness! Ready to start your journey?',
            'time': '2 minutes ago',
            'icon': 'paper-plane',
            'color': 'success',
            'status': 'Delivered',
            'status_color': 'success'
        },
        {
            'id': 2,
            'action': 'Payment Reminder',
            'recipient': 'Mike Chen',
            'preview': 'Your payment for this month is due tomorrow. Click here to pay...',
            'time': '15 minutes ago',
            'icon': 'credit-card',
            'color': 'warning',
            'status': 'Pending',
            'status_color': 'warning'
        }
    ]
    
    # Mock conversation data (placeholder until real bot integration)
    bot_conversations = [
        {
            'id': 'conv_001',
            'contact_name': 'Jessica Williams',
            'last_message': 'Yes, I would like to schedule a session for tomorrow',
            'last_time': '5 min ago',
            'last_sender': 'user',
            'unread': True,
            'status': 'Hot Lead',
            'status_color': 'success',
            'needs_attention': False
        },
        {
            'id': 'conv_002',
            'contact_name': 'David Thompson',
            'last_message': 'Can you help me with my payment plan?',
            'last_time': '1 hour ago',
            'last_sender': 'user',
            'unread': True,
            'status': 'Support',
            'status_color': 'warning',
            'needs_attention': True
        }
    ]
    
    # Create bot_stats dictionary for template
    bot_stats = {
        'messages_sent': len(bot_activities),
        'last_activity': f"2 minutes ago: Sent welcome message"
    }
    
    # Create stats dictionary for dashboard metrics
    stats = {
        'todays_events': len(today_events),
        'next_session_time': today_events[0].get('start_time', 'None scheduled') if today_events else 'None scheduled',
        'revenue': f"$1,247"
    }
    
    return render_template('dashboard.html', 
                         total_members=total_members,
                         total_prospects=total_prospects,
                         total_training_clients=total_training_clients,
                         total_live_events=len(today_events),
                         today_events_count=len(today_events),
                         training_sessions_count=training_sessions_count,
                         appointments_count=appointments_count,
                         bot_messages_today=len(bot_activities),
                         active_conversations=len([c for c in bot_conversations if c['unread']]),
                         bot_activities=bot_activities,
                         bot_conversations=bot_conversations,
                         bot_stats=bot_stats,
                         stats=stats,
                         recent_members=[],  # Empty for now - can be populated later
                         recent_prospects=[], # Empty for now - can be populated later
                         recent_events=today_events,
                         clubos_status=clubos_status,
                         clubos_connected=clubos.authenticated,
                         sync_time=sync_time)

@app.route('/api/clubos/status')
def api_clubos_status():
    """Diagnostic: report ClubOS auth/session status without exposing secrets."""
    try:
        # Ensure we have a client instance
        api = clubos_training_api
        # Attempt to ensure session is alive but do not force credentials into response
        try:
            alive = api._ensure_session_alive() if hasattr(api, '_ensure_session_alive') else api.authenticate()
        except Exception:
            alive = False
        # Try to get assignees count
        assignees_count = None
        try:
            idx = api.get_assignee_index(force_refresh=False)
            assignees_count = sum(len(v) for v in (idx or {}).values()) if idx else 0
        except Exception:
            assignees_count = 0
        return jsonify({
            'success': True,
            'authenticated': bool(getattr(api, 'authenticated', False)),
            'session_alive': bool(alive),
            'has_access_token': bool(getattr(api, 'access_token', None)),
            'assignees_index_size': assignees_count
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/check-funding', methods=['POST'])
def check_funding():
    """API endpoint to check real funding status for participants"""
    try:
        data = request.get_json() if request.is_json else {}
        participant_name = (data.get('participant') or data.get('participant_name') or '').strip()
        # Optional email for improved matching
        participant_email = (data.get('participant_email') or data.get('email') or '').strip() or None
        # Optional phone for improved matching
        participant_phone = (data.get('participant_phone') or data.get('phone') or '').strip() or None
        time = data.get('time', '')

        logger.info(f"🔍 API request to check funding for: {participant_name}")

        # Use the training package cache to get real funding data
        funding_data = training_package_cache.lookup_participant_funding(
            participant_name, participant_email, participant_phone
        )

        if funding_data:
            logger.info(f"✅ API returning funding data for {participant_name}: {funding_data}")
            return jsonify({'success': True, 'funding': funding_data})
        else:
            logger.warning(f"⚠️ No funding data found for {participant_name}")
            return jsonify({
                'success': True,
                'funding': {
                    'status_text': 'No Data',
                    'status_class': 'secondary',
                    'status_icon': 'fas fa-question-circle',
                    'is_cached': False,
                    'is_stale': False,
                    'message': 'No live funding data available'
                }
            })
    except Exception as e:
        logger.error(f"❌ Error in funding API: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/check-funding-by-id', methods=['POST'])
def check_funding_by_id():
    """API endpoint to check funding by known ClubOS member ID (bypasses name search)."""
    try:
        data = request.get_json() if request.is_json else {}
        clubos_member_id = str(data.get('clubos_member_id') or data.get('member_id') or '').strip()
        member_name = (data.get('member_name') or data.get('name') or f"Member {clubos_member_id}").strip()

        if not clubos_member_id:
            return jsonify({'success': False, 'error': 'clubos_member_id is required'}), 400

        logger.info(f"🔎 Direct funding check for ClubOS ID: {clubos_member_id} ({member_name})")

        # Fetch fresh funding directly, bypassing name->ID search
        fresh_data = training_package_cache._fetch_fresh_funding_data(clubos_member_id, member_name)
        if fresh_data:
            training_package_cache._cache_funding_data(fresh_data)
            response = training_package_cache._format_funding_response(fresh_data, is_stale=False, is_cached=False)
            return jsonify({'success': True, 'funding': response})

        logger.warning(f"❌ No LIVE funding data available for ClubOS ID {clubos_member_id}")
        return jsonify({
            'success': True,
            'funding': {
                'status_text': 'No Data',
                'status_class': 'secondary',
                'status_icon': 'fas fa-question-circle',
                'is_cached': False,
                'is_stale': False,
                'message': 'No live funding data available'
            }
        })

    except Exception as e:
        logger.error(f"❌ Error in direct funding API: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/refresh-funding', methods=['POST'])
def refresh_funding_cache():
    """API endpoint to manually refresh funding cache for all training clients"""
    try:
        force = request.json.get('force', False) if request.is_json else False
        
        logger.info("🔄 Manual funding cache refresh requested")
        
        # Refresh funding cache for all training clients
        result = training_package_cache.refresh_all_funding_cache()
        
        return jsonify({
            'success': result.get('success', False),
            'total_clients': result.get('total_clients', 0),
            'success_count': result.get('success_count', 0),
            'error_count': result.get('error_count', 0),
            'timestamp': result.get('timestamp'),
            'message': f"Updated {result.get('success_count', 0)} of {result.get('total_clients', 0)} training clients"
        })
        
    except Exception as e:
        logger.error(f"❌ Error in funding refresh API: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

def save_bulk_checkin_run(run_id: str, status: str, status_data: dict, error_message: str = None):
    """Save bulk check-in run status to database for resume capability"""
    try:
        conn = sqlite3.connect(db_manager.db_path)
        cursor = conn.cursor()
        
        # Insert or update run record
        cursor.execute('''
            INSERT OR REPLACE INTO bulk_checkin_runs 
            (run_id, status, total_members, processed_members, successful_checkins, 
             failed_checkins, excluded_ppv, excluded_other, started_at, completed_at, 
             error_message, resume_data_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            run_id,
            status,
            status_data.get('total_members', 0),
            status_data.get('processed_members', 0),
            status_data.get('total_checkins', 0),
            len(status_data.get('errors', [])),
            status_data.get('ppv_excluded', 0),
            status_data.get('comp_excluded', 0) + status_data.get('frozen_excluded', 0),
            status_data.get('started_at'),
            status_data.get('completed_at'),
            error_message,
            json.dumps(status_data)
        ))
        
        conn.commit()
        conn.close()
        
    except Exception as e:
        logger.error(f"❌ Error saving bulk check-in run: {e}")

def load_bulk_checkin_resume_data(run_id: str) -> dict:
    """Load bulk check-in run data for resuming"""
    try:
        conn = sqlite3.connect(db_manager.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM bulk_checkin_runs WHERE run_id = ?', (run_id,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'status': json.loads(result['resume_data_json']) if result['resume_data_json'] else {},
                'processed_members': result['processed_members'],
                'total_members': result['total_members']
            }
        
        return None
        
    except Exception as e:
        logger.error(f"❌ Error loading bulk check-in resume data: {e}")
        return None

@app.route('/api/bulk-checkin-resume/<run_id>', methods=['POST'])
def api_bulk_checkin_resume(run_id):
    """API endpoint to resume a paused or failed bulk check-in run"""
    global bulk_checkin_status
    
    # Check if already running
    if bulk_checkin_status['is_running']:
        return jsonify({
            'success': False,
            'error': 'Bulk check-in already in progress',
            'status': bulk_checkin_status
        }), 400
    
    # Start background process with resume
    thread = threading.Thread(target=perform_bulk_checkin_background, args=(run_id,))
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'success': True,
        'message': f'Bulk check-in resumed for run: {run_id}',
        'status': bulk_checkin_status
    })

@app.route('/api/bulk-checkin-runs')
def api_bulk_checkin_runs():
    """API endpoint to get list of bulk check-in runs"""
    try:
        conn = sqlite3.connect(db_manager.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM bulk_checkin_runs 
            ORDER BY started_at DESC 
            LIMIT 50
        ''')
        
        runs = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return jsonify({
            'success': True,
            'runs': runs
        })
        
    except Exception as e:
        logger.error(f"❌ Error fetching bulk check-in runs: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/bulk-checkin', methods=['POST'])
def api_bulk_checkin():
    """API endpoint to start bulk member check-ins in background - EXCLUDES PPV/COMP/FROZEN MEMBERS"""
    global bulk_checkin_status
    
    # Check if already running
    if bulk_checkin_status['is_running']:
        return jsonify({
            'success': False,
            'error': 'Bulk check-in already in progress',
            'status': bulk_checkin_status
        }), 400
    
    # Start background process
    thread = threading.Thread(target=perform_bulk_checkin_background)
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'success': True,
        'message': 'Bulk check-in started in background',
        'status': bulk_checkin_status
    })

def perform_bulk_checkin_background(resume_run_id=None):
    """Background function to perform bulk member check-ins with progress tracking and resume capability"""
    global bulk_checkin_status
    
    run_id = resume_run_id or str(uuid.uuid4())
    
    try:
        # Initialize or resume status
        if resume_run_id:
            # Load resume data from database
            resume_data = load_bulk_checkin_resume_data(resume_run_id)
            if resume_data:
                logger.info(f"🔄 Resuming bulk check-in run: {resume_run_id}")
                bulk_checkin_status.update(resume_data.get('status', {}))
                bulk_checkin_status['is_running'] = True
                bulk_checkin_status['status'] = 'resuming'
                bulk_checkin_status['message'] = f'Resuming from {resume_data.get("processed_members", 0)} processed members...'
            else:
                logger.warning(f"❌ Could not find resume data for run: {resume_run_id}")
                resume_run_id = None
        
        if not resume_run_id:
            # Initialize new run
            bulk_checkin_status.update({
                'is_running': True,
                'run_id': run_id,
                'started_at': datetime.now().isoformat(),
                'completed_at': None,
                'progress': 0,
                'total_members': 0,
                'processed_members': 0,
                'ppv_excluded': 0,
                'comp_excluded': 0,
                'frozen_excluded': 0,
                'total_checkins': 0,
                'current_member': '',
                'status': 'starting',
                'message': 'Initializing bulk check-in process...',
                'error': None,
                'errors': []
            })
            
            # Create database tracking record
            save_bulk_checkin_run(run_id, 'running', bulk_checkin_status)
        
        logger.info(f"🏋️ Starting background bulk member check-in process (run: {run_id})...")
        
        # Import and initialize the ClubHub API client
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), 'services'))
        
        try:
            from api.clubhub_api_client import ClubHubAPIClient
            from config.clubhub_credentials import CLUBHUB_EMAIL, CLUBHUB_PASSWORD
        except ImportError as e:
            logger.error(f"❌ Failed to import ClubHub modules: {e}")
            bulk_checkin_status.update({
                'is_running': False,
                'status': 'error',
                'error': f'Import error: {e}',
                'message': 'Failed to import required modules'
            })
            save_bulk_checkin_run(run_id, 'failed', bulk_checkin_status, error_message=str(e))
            return
        
        bulk_checkin_status['message'] = 'Authenticating with ClubHub...'
        bulk_checkin_status['status'] = 'authenticating'
        save_bulk_checkin_run(run_id, 'running', bulk_checkin_status)
        
        # Initialize and authenticate
        client = ClubHubAPIClient()
        if not client.authenticate(CLUBHUB_EMAIL, CLUBHUB_PASSWORD):
            error_msg = 'ClubHub authentication failed'
            bulk_checkin_status.update({
                'is_running': False,
                'status': 'error',
                'error': error_msg,
                'message': 'Authentication failed'
            })
            save_bulk_checkin_run(run_id, 'failed', bulk_checkin_status, error_message=error_msg)
            return
        
        bulk_checkin_status['message'] = 'Fetching member list...'
        bulk_checkin_status['status'] = 'fetching'
        save_bulk_checkin_run(run_id, 'running', bulk_checkin_status)
        
        # Get ALL members from ClubHub (paginate through all pages)
        all_members = []
        page = 1
        page_size = 50  # Smaller page size to reduce memory usage
        
        while True:
            try:
                members_response = client.get_all_members(page=page, page_size=page_size)
                
                if not members_response or not isinstance(members_response, list):
                    break
                    
                all_members.extend(members_response)
                
                # Update progress
                bulk_checkin_status['message'] = f'Fetched page {page}, total members: {len(all_members)}'
                
                # If we got less than page_size, we've reached the end
                if len(members_response) < page_size:
                    break
                    
                page += 1
                
                # Add small delay to prevent overwhelming the API
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Error fetching page {page}: {e}")
                break
        
        logger.info(f"📋 Retrieved {len(all_members)} total members from ClubHub")
        bulk_checkin_status.update({
            'total_members': len(all_members),
            'message': f'Found {len(all_members)} total members, filtering excluded members...',
            'status': 'filtering'
        })
        save_bulk_checkin_run(run_id, 'running', bulk_checkin_status)
        
        # Enhanced member filtering with categorization
        regular_members = []
        ppv_members = []
        comp_members = []
        frozen_members = []
        
        for i, member in enumerate(all_members):
            # Update progress for filtering
            if i % 50 == 0:  # Update every 50 members
                bulk_checkin_status['message'] = f'Filtering members... {i}/{len(all_members)}'
                bulk_checkin_status['progress'] = int((i / len(all_members)) * 20)  # 20% for filtering
            
            # Extract member data for categorization
            contract_types = member.get('contractTypes', [])
            member_status = member.get('status', 0)
            user_type = member.get('userType', 0)
            status_message = member.get('statusMessage', '').lower()
            
            # Categorize members
            is_ppv = False
            is_comp = False
            is_frozen = False
            
            # PPV Check (Pay Per Visit)
            if contract_types and any(ct in [2, 3, 4] for ct in contract_types):
                is_ppv = True
            elif user_type in [18, 19, 20]:
                is_ppv = True
            elif member.get('trial', False):
                is_ppv = True
            elif any(keyword in status_message for keyword in ['pay per visit', 'ppv', 'day pass', 'guest pass']):
                is_ppv = True
            
            # Comp Check (Complimentary memberships)
            if not is_ppv:
                if any(keyword in status_message for keyword in ['comp', 'complimentary', 'free', 'staff']):
                    is_comp = True
                elif user_type in [99, 100]:  # Adjust based on your system's comp user types
                    is_comp = True
            
            # Frozen Check (Frozen/Hold memberships)
            if not is_ppv and not is_comp:
                if member_status in [2, 3]:  # Common frozen status codes
                    is_frozen = True
                elif any(keyword in status_message for keyword in ['frozen', 'hold', 'suspend', 'pause']):
                    is_frozen = True
            
            # Categorize member
            if is_ppv:
                ppv_members.append(member)
            elif is_comp:
                comp_members.append(member)
            elif is_frozen:
                frozen_members.append(member)
            else:
                regular_members.append(member)
        
        logger.info(f"✅ Member categorization: {len(regular_members)} regular, {len(ppv_members)} PPV, {len(comp_members)} comp, {len(frozen_members)} frozen")
        bulk_checkin_status.update({
            'ppv_excluded': len(ppv_members),
            'comp_excluded': len(comp_members),
            'frozen_excluded': len(frozen_members),
            'total_members': len(regular_members),
            'message': f'Processing {len(regular_members)} regular members (excluded {len(ppv_members)} PPV, {len(comp_members)} comp, {len(frozen_members)} frozen)',
            'status': 'processing',
            'progress': 25
        })
        save_bulk_checkin_run(run_id, 'running', bulk_checkin_status)
        
        # Process members in smaller batches to prevent crashes
        batch_size = 10  # Process 10 members at a time
        total_checkins = 0
        members_processed = 0
        errors = []
        
        for batch_start in range(0, len(regular_members), batch_size):
            batch_end = min(batch_start + batch_size, len(regular_members))
            batch = regular_members[batch_start:batch_end]
            
            for member in batch:
                try:
                    member_id = member.get('id')
                    member_name = f"{member.get('firstName', '')} {member.get('lastName', '')}".strip()
                    
                    if not member_id:
                        continue
                    
                    # Update current status
                    bulk_checkin_status.update({
                        'current_member': member_name,
                        'processed_members': members_processed,
                        'message': f'Checking in {member_name} ({members_processed + 1}/{len(regular_members)})',
                        'progress': 25 + int(((members_processed / len(regular_members)) * 70))  # 25-95% for processing
                    })
                    
                    # First check-in (now)
                    checkin_data_1 = {
                        "date": datetime.now().strftime("%Y-%m-%dT%H:%M:%S-05:00"),
                        "door": {"id": 772},
                        "club": {"id": 1156},
                        "manual": True
                    }
                    
                    result_1 = client.post_member_usage(str(member_id), checkin_data_1)
                    if result_1:
                        total_checkins += 1
                        bulk_checkin_status['total_checkins'] = total_checkins
                        logger.info(f"✅ Check-in 1 successful for {member_name} (ID: {member_id})")
                    
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
                        bulk_checkin_status['total_checkins'] = total_checkins
                        logger.info(f"✅ Check-in 2 successful for {member_name} (ID: {member_id})")
                    
                    members_processed += 1
                    bulk_checkin_status['processed_members'] = members_processed
                    
                    # Small delay between members
                    time.sleep(0.1)
                    
                except Exception as member_error:
                    error_msg = f"Error checking in {member_name}: {str(member_error)}"
                    logger.error(error_msg)
                    errors.append(error_msg)
                    bulk_checkin_status['errors'] = errors
            
            # Longer delay between batches to prevent overwhelming the system
            time.sleep(1)
            logger.info(f"Completed batch {batch_start//batch_size + 1}/{(len(regular_members) + batch_size - 1)//batch_size}")
        
        # Complete the process
        bulk_checkin_status.update({
            'is_running': False,
            'completed_at': datetime.now().isoformat(),
            'status': 'completed',
            'message': f'Completed! {total_checkins} total check-ins for {members_processed} members',
            'progress': 100,
            'current_member': ''
        })
        
        logger.info(f"🎉 Bulk check-in completed: {total_checkins} total check-ins for {members_processed} regular members")
        logger.info(f"🚫 Excluded {len(ppv_members)} PPV members from check-in process")
        
    except Exception as e:
        logger.error(f"❌ Error in background bulk check-in: {e}")
        bulk_checkin_status.update({
            'is_running': False,
            'status': 'error',
            'error': str(e),
            'message': f'Error: {str(e)}',
            'completed_at': datetime.now().isoformat()
        })

@app.route('/api/bulk-checkin-status')
def api_bulk_checkin_status():
    """API endpoint to get current bulk check-in status"""
    return jsonify({
        'success': True,
        'status': bulk_checkin_status
    })

@app.route('/api/funding-cache-status')
def funding_cache_status():
    """API endpoint to check current funding cache status"""
    try:
        conn = sqlite3.connect(db_manager.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get cache statistics
        cursor.execute("SELECT COUNT(*) as total FROM funding_status_cache")
        total_cached = cursor.fetchone()['total']
        
        cursor.execute("""
            SELECT COUNT(*) as fresh FROM funding_status_cache 
            WHERE datetime(last_updated) > datetime('now', '-24 hours')
        """)
        fresh_count = cursor.fetchone()['fresh']
        
        cursor.execute("""
            SELECT COUNT(*) as stale FROM funding_status_cache 
            WHERE datetime(last_updated) <= datetime('now', '-24 hours')
        """)
        stale_count = cursor.fetchone()['stale']
        
        # Get funding status breakdown
        cursor.execute("""
            SELECT funding_status, COUNT(*) as count 
            FROM funding_status_cache 
            GROUP BY funding_status
        """)
        
        status_breakdown = {}
        for row in cursor.fetchall():
            status_breakdown[row['funding_status']] = row['count']
        
        # Get last update info
        cursor.execute("""
            SELECT member_name, last_updated 
            FROM funding_status_cache 
            ORDER BY datetime(last_updated) DESC 
            LIMIT 1
        """)
        
        last_update = cursor.fetchone()
        
        conn.close()
        
        return jsonify({
            'success': True,
            'cache_stats': {
                'total_cached': total_cached,
                'fresh_count': fresh_count,
                'stale_count': stale_count,
                'last_update': {
                    'member_name': last_update['member_name'] if last_update else None,
                    'timestamp': last_update['last_updated'] if last_update else None
                }
            },
            'status_breakdown': status_breakdown,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Error getting funding cache status: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/refresh-data', methods=['POST', 'GET'])
def refresh_data():
    """API endpoint to manually refresh database with latest ClubOS data"""
    try:
        # Handle both JSON and form data, with safe defaults
        force = False
        background = False
        
        if request.method == 'POST':
            if request.is_json and request.json:
                force = request.json.get('force', False)
                background = request.json.get('background', False)
            elif request.form:
                force = request.form.get('force', 'false').lower() == 'true'
                background = request.form.get('background', 'false').lower() == 'true'
        
        logger.info(f"🔄 Manual data refresh requested (force={force}, background={background})")
        
        if background:
            # Start background refresh process
            import threading
            
            def background_refresh():
                global data_refresh_status
                try:
                    # Update status to running
                    data_refresh_status.update({
                        'is_running': True,
                        'started_at': datetime.now().isoformat(),
                        'completed_at': None,
                        'progress': 0,
                        'status': 'running',
                        'message': 'Starting background data refresh...',
                        'error': None
                    })
                    
                    logger.info("🔄 Starting background data refresh...")
                    
                    # Update progress
                    data_refresh_status['progress'] = 25
                    data_refresh_status['message'] = 'Refreshing database...'
                    
                    success = db_manager.refresh_database(force=force)
                    
                    # Update progress
                    data_refresh_status['progress'] = 75
                    data_refresh_status['message'] = 'Updating CSV data...'
                    
                    # Complete the refresh
                    data_refresh_status.update({
                        'is_running': False,
                        'completed_at': datetime.now().isoformat(),
                        'progress': 100,
                        'status': 'completed',
                        'message': f'Background refresh completed successfully: {success}',
                        'error': None
                    })
                    
                    logger.info(f"✅ Background refresh completed: {success}")
                    
                except Exception as e:
                    # Update status with error
                    data_refresh_status.update({
                        'is_running': False,
                        'completed_at': datetime.now().isoformat(),
                        'progress': 0,
                        'status': 'error',
                        'message': f'Background refresh failed: {str(e)}',
                        'error': str(e)
                    })
                    logger.error(f"❌ Background refresh failed: {e}")
            
            # Start background thread
            thread = threading.Thread(target=background_refresh, daemon=True)
            thread.start()
            
            return jsonify({
                'success': True,
                'background': True,
                'message': 'Background refresh started. Check /api/data-status for progress.',
                'timestamp': datetime.now().isoformat()
            })
        else:
            # Synchronous refresh
            success = db_manager.refresh_database(force=force)
            
            # Get updated counts
            conn = sqlite3.connect(db_manager.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM members")
            members_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM prospects")
            prospects_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM training_clients")
            training_clients_count = cursor.fetchone()[0]
            
            conn.close()
            
            # Get refresh status
            refresh_status = db_manager.get_refresh_status()
            
            return jsonify({
                'success': True,
                'refreshed': success,
                'counts': {
                    'members': members_count,
                    'prospects': prospects_count,
                    'training_clients': training_clients_count
                },
                'refresh_status': refresh_status,
                'timestamp': datetime.now().isoformat()
            })
        
    except Exception as e:
        logger.error(f"❌ Error in data refresh API: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/refresh-clubhub-members', methods=['POST', 'GET'])
def refresh_clubhub_members():
    """API endpoint to refresh member data directly from ClubHub"""
    try:
        logger.info("🔄 Refreshing member data from ClubHub...")
        
        # Import ClubHub API client
        sys.path.append(os.path.join(os.path.dirname(__file__), 'services'))
        from api.clubhub_api_client import ClubHubAPIClient
        from config.clubhub_credentials import CLUBHUB_EMAIL, CLUBHUB_PASSWORD
        
        # Initialize and authenticate
        client = ClubHubAPIClient()
        if not client.authenticate(CLUBHUB_EMAIL, CLUBHUB_PASSWORD):
            return jsonify({
                'success': False,
                'error': 'ClubHub authentication failed'
            })
        
        # Get fresh member data from ClubHub
        fresh_members = []
        page = 1
        page_size = 100
        
        logger.info("📥 Fetching members from ClubHub...")
        
        while True:
            members_response = client.get_all_members(page=page, page_size=page_size)
            
            if not members_response or not isinstance(members_response, list):
                break
                
            fresh_members.extend(members_response)
            logger.info(f"📄 Retrieved page {page}, total members so far: {len(fresh_members)}")
            
            # If we got less than page_size, we've reached the end
            if len(members_response) < page_size:
                break
                
            page += 1
        
        logger.info(f"📋 Retrieved {len(fresh_members)} total members from ClubHub")
        
        # Search for Dennis Rost specifically
        dennis_found = None
        for member in fresh_members:
            first_name = member.get('firstName', '').lower()
            last_name = member.get('lastName', '').lower()
            
            if 'dennis' in first_name and 'rost' in last_name:
                dennis_found = member
                logger.info(f"🎯 FOUND Dennis Rost in ClubHub: ID {member.get('id')}, Name: {first_name.title()} {last_name.title()}")
                break
        
        # Update database with fresh members
        conn = sqlite3.connect(db_manager.db_path)
        cursor = conn.cursor()
        
        # Clear and repopulate members table with fresh data
        cursor.execute('DELETE FROM members')
        
        members_added = 0
        for member in fresh_members:
            try:
                # Map ClubHub member data to our database schema
                member_data = {
                    'id': member.get('id'),
                    'first_name': member.get('firstName'),
                    'last_name': member.get('lastName'),
                    'full_name': f"{member.get('firstName', '')} {member.get('lastName', '')}".strip(),
                    'email': member.get('email'),
                    'mobile_phone': member.get('mobilePhone'),
                    'status': member.get('status'),
                    'user_type': member.get('userType'),
                    'membership_start': member.get('membershipStart'),
                    'membership_end': member.get('membershipEnd'),
                    'last_visit': member.get('lastVisit'),
                    'trial': member.get('trial', False),
                    'contract_types': str(member.get('contractTypes', [])),
                    'status_message': member.get('statusMessage')
                }
                
                # Remove None values
                member_data = {k: v for k, v in member_data.items() if v is not None}
                columns = ', '.join(member_data.keys())
                placeholders = ', '.join(['?' for _ in member_data.values()])
                
                cursor.execute(f'''
                    INSERT OR REPLACE INTO members ({columns})
                    VALUES ({placeholders})
                ''', list(member_data.values()))
                
                members_added += 1
                
            except Exception as e:
                logger.error(f"❌ Error adding member {member.get('firstName')} {member.get('lastName')}: {e}")
        
        conn.commit()
        conn.close()
        
        logger.info(f"✅ ClubHub member refresh complete: {members_added} members added")
        
        return jsonify({
            'success': True,
            'members_fetched': len(fresh_members),
            'members_added': members_added,
            'dennis_found': dennis_found is not None,
            'dennis_data': dennis_found if dennis_found else None,
            'message': f'Successfully refreshed {members_added} members from ClubHub'
        })
        
    except Exception as e:
        logger.error(f"❌ Error refreshing ClubHub members: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/data-status')
def data_status():
    """API endpoint to check current data status and freshness"""
    try:
        # Get database counts
        conn = sqlite3.connect(db_manager.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM members")
        members_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM prospects")
        prospects_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM training_clients")
        training_clients_count = cursor.fetchone()[0]
        
        # Get members with past due amounts
        cursor.execute("SELECT COUNT(*) FROM members WHERE amount_past_due > 0")
        red_list_count = cursor.fetchone()[0]
        
        # Get members with payments due soon
        cursor.execute("""
            SELECT COUNT(*) FROM members 
            WHERE date_of_next_payment <= date('now', '+7 days') 
            AND amount_past_due = 0
        """)
        yellow_list_count = cursor.fetchone()[0]
        
        conn.close()
        
        # Get refresh status
        refresh_status = db_manager.get_refresh_status()
        
        # Check CSV files for past due counts
        csv_files = [
            'data/exports/master_contact_list_20250715_181954.csv',
            'data/csv_exports/master_contact_list_with_agreements_20250802_123437.csv',
            'data/exports/master_contact_list_latest.csv'
        ]
        
        csv_past_due_counts = {'red': 0, 'yellow': 0, 'total': 0}
        active_csv = None;
        
        for file_path in csv_files:
            if os.path.exists(file_path):
                active_csv = file_path
                try:
                    df = pd.read_csv(file_path)
                    if 'StatusMessage' in df.columns:
                        red_count = len(df[df['StatusMessage'].str.contains('Past Due more than 30 days', na=False)])
                        yellow_count = len(df[df['StatusMessage'].str.contains('Past Due 6-30 days', na=False)])
                        csv_past_due_counts = {
                            'red': red_count,
                            'yellow': yellow_count,
                            'total': red_count + yellow_count
                        }
                        break
                except Exception as e:
                    pass
        
        return jsonify({
            'success': True,
            'counts': {
                'members': members_count,
                'prospects': prospects_count,
                'training_clients': training_clients_count,
                'red_list': red_list_count,
                'yellow_list': yellow_list_count
            },
            'csv_past_due_counts': csv_past_due_counts,
            'active_csv_file': active_csv,
            'refresh_status': refresh_status,
            'background_refresh_status': data_refresh_status,
            'needs_refresh': db_manager.needs_refresh(),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Error in data status API: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/members')
def members_page():
    """Display members page with automatic database refresh to get latest member data."""
    
    logger.info("🔄 Members page loaded - refreshing database with latest member data...")
    
    # Automatically refresh database with latest member data when members page loads
    try:
        # Import ClubHub API client for fresh data
        sys.path.append(os.path.join(os.path.dirname(__file__), 'services'))
        from api.clubhub_api_client import ClubHubAPIClient
        from config.clubhub_credentials import CLUBHUB_EMAIL, CLUBHUB_PASSWORD
        
        # Initialize and authenticate with ClubHub
        client = ClubHubAPIClient()
        if client.authenticate(CLUBHUB_EMAIL, CLUBHUB_PASSWORD):
            logger.info("✅ ClubHub authentication successful - fetching fresh member data...")
            
            # Get fresh member data from ClubHub
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
            
            logger.info(f"📋 Retrieved {len(fresh_members)} members from ClubHub - updating database...")
            
            # Update database with fresh member data
            conn = sqlite3.connect(db_manager.db_path)
            cursor = conn.cursor()
            
            # Clear existing members and insert fresh data
            cursor.execute('DELETE FROM members')
            
            updated_count = 0
            for member in fresh_members:
                try:
                    member_data = {
                        'id': member.get('id'),
                        'first_name': member.get('firstName'),
                        'last_name': member.get('lastName'),
                        'full_name': f"{member.get('firstName', '')} {member.get('lastName', '')}".strip(),
                        'email': member.get('email'),
                        'mobile_phone': member.get('mobilePhone'),
                        'home_phone': member.get('homePhone'),
                        'status': member.get('status'),
                        'status_message': member.get('statusMessage'),
                        'user_type': member.get('userType'),
                        'membership_start': member.get('membershipStart'),
                        'membership_end': member.get('membershipEnd'),
                        'last_visit': member.get('lastVisit'),
                        'contract_types': str(member.get('contractTypes', [])),
                        'trial': member.get('trial', False),
                        'created_at': datetime.now().isoformat(),
                        'updated_at': datetime.now().isoformat()
                    }
                    
                    # Remove None values
                    member_data = {k: v for k, v in member_data.items() if v is not None}
                    columns = ', '.join(member_data.keys())
                    placeholders = ', '.join(['?' for _ in member_data.values()])
                    
                    cursor.execute(f'''
                        INSERT OR REPLACE INTO members ({columns})
                        VALUES ({placeholders})
                    ''', list(member_data.values()))
                    
                    updated_count += 1
                    
                except Exception as e:
                    logger.error(f"❌ Error updating member {member.get('firstName', '')} {member.get('lastName', '')}: {e}")
                    continue
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Database updated with {updated_count} fresh members from ClubHub")
            
            # Also refresh training clients data
            try:
                logger.info("🏋️ Refreshing training clients data...")
                
                # Get training clients from ClubHub API if available
                training_clients_response = client.get_training_clients() if hasattr(client, 'get_training_clients') else []
                
                if training_clients_response:
                    conn = sqlite3.connect(db_manager.db_path)
                    cursor = conn.cursor()
                    
                    # Update training clients with fresh data
                    training_updated = 0
                    for training_client in training_clients_response:
                        try:
                            # Extract member ID and update training client data
                            client_data = {
                                'member_id': training_client.get('memberId'),
                                'clubos_member_id': training_client.get('memberId'),
                                'member_name': training_client.get('memberName'),
                                'trainer_name': training_client.get('trainerName', 'Jeremy Mayo'),
                                'sessions_remaining': training_client.get('sessionsRemaining', 0),
                                'updated_at': datetime.now().isoformat()
                            }
                            
                            # Remove None values
                            client_data = {k: v for k, v in client_data.items() if v is not None}
                            
                            # Update or insert training client
                            if client_data.get('clubos_member_id'):
                                columns = ', '.join(client_data.keys())
                                placeholders = ', '.join(['?' for _ in client_data.values()])
                                
                                cursor.execute(f'''
                                    INSERT OR REPLACE INTO training_clients ({columns})
                                    VALUES ({placeholders})
                                ''', list(client_data.values()))
                                
                                training_updated += 1
                                
                        except Exception as e:
                            logger.error(f"❌ Error updating training client: {e}")
                            continue
                    
                    conn.commit()
                    conn.close()
                    
                    logger.info(f"✅ Updated {training_updated} training clients")
                    
            except Exception as e:
                logger.error(f"❌ Error refreshing training clients: {e}")
            
        else:
            logger.warning("⚠️ ClubHub authentication failed - using existing database data")
            
    except Exception as e:
        logger.error(f"❌ Error refreshing member database: {e}")
        logger.info("⚠️ Using existing database data as fallback")
    
    # Get current database counts for display
    conn = sqlite3.connect(db_manager.db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM members")
    total_members = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM members WHERE amount_past_due > 0")
    red_list_count = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT COUNT(*) FROM members 
        WHERE date_of_next_payment <= date('now', '+7 days') 
        AND amount_past_due = 0
    """)
    yellow_list_count = cursor.fetchone()[0]
    
    conn.close()
    
    # Fast page load - render template with refreshed data counts
    # JavaScript will load the actual member data asynchronously
    return render_template('members.html',
                         members=[],  # Empty initially, loaded via JavaScript
                         total_members=total_members,  # Updated count from fresh data
                         statuses=[],
                         search='',
                         status_filter='',
                         page=1,
                         total_pages=1,
                         per_page=50,
                         red_list_count=red_list_count,
                         yellow_list_count=yellow_list_count,
                         past_due_count=red_list_count)

@app.route('/api/members/all')
def get_all_members():
    """API endpoint to get all members - called asynchronously after page load."""
    conn = None
    try:
        # Get search and filter parameters
        search = request.args.get('search', '')
        status_filter = request.args.get('status', '')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))

        # Use cached database data for speed (instead of ClubHub API every time)
        conn = sqlite3.connect(db_manager.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Build query with search and filters
        where_conditions = []
        params = []

        if search:
            where_conditions.append("(first_name LIKE ? OR last_name LIKE ? OR email LIKE ?)")
            search_term = f"%{search}%"
            params.extend([search_term, search_term, search_term])

        if status_filter:
            where_conditions.append("status = ?")
            params.append(status_filter)

        where_clause = ""
        if where_conditions:
            where_clause = "WHERE " + " AND ".join(where_conditions)

        # Get total count for pagination
        count_query = f"SELECT COUNT(*) FROM members {where_clause}"
        cursor.execute(count_query, params)
        total_members = cursor.fetchone()[0]

        # Calculate pagination
        total_pages = (total_members + per_page - 1) // per_page
        offset = (page - 1) * per_page

        # Get members for current page
        query = f"""
            SELECT id, first_name, last_name, full_name, email, mobile_phone, status,
                   status_message, membership_start, membership_end, payment_amount, user_type, created_at,
                   agreement_rate, amount_past_due, amount_of_next_payment, date_of_next_payment, trial
            FROM members {where_clause}
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """
        cursor.execute(query, params + [per_page, offset])
        members_data = cursor.fetchall()

        # Process members for display
        members = []
        for member in members_data:
            member_dict = dict(member)

            # Generate full_name if missing - CRITICAL FIX
            first_name = member_dict.get('first_name', '') or ''
            last_name = member_dict.get('last_name', '') or ''
            if not member_dict.get('full_name'):
                member_dict['full_name'] = f"{first_name} {last_name}".strip()

            # Ensure we have a display name - FALLBACK FIX
            if not member_dict['full_name']:
                member_dict['full_name'] = member_dict.get('email', 'Unknown Member')

            # Ensure first_name and last_name are not None
            member_dict['first_name'] = first_name or 'Unknown'
            member_dict['last_name'] = last_name or 'Member'

            # Classify priority/outlook and badge for UI
            status_message = (member_dict.get('status_message') or '').lower()
            user_type = str(member_dict.get('user_type') or '').lower()
            trial = bool(member_dict.get('trial')) if member_dict.get('trial') is not None else False
            amount_past_due = float(member_dict.get('amount_past_due') or 0)
            next_due = member_dict.get('date_of_next_payment') or ''
            priority = ''
            status_text = member_dict.get('status') or 'Active'
            badge_class = 'primary'

            # Determine PPV
            is_ppv = False
            if 'pay per visit' in status_message or 'ppv' in status_message:
                is_ppv = True
            if user_type in ('17', 'ppv'):
                is_ppv = True
            if trial:
                is_ppv = True

            # Determine red/yellow
            if amount_past_due > 0:
                priority = 'red'
                status_text = 'Past Due'
                badge_class = 'danger'
            else:
                # due within 7 days
                try:
                    if next_due:
                        due_dt = datetime.fromisoformat(str(next_due).replace('Z','').split('T')[0])
                        if (due_dt - datetime.now()).days <= 7:
                            priority = 'yellow'
                            status_text = 'Due Soon'
                            badge_class = 'warning'
                except Exception:
                    pass

            if not priority and is_ppv:
                priority = 'ppv'
                status_text = 'PPV'
                badge_class = 'info'

            member_dict['priority_status'] = priority
            member_dict['status_text'] = status_text
            member_dict['payment_status_class'] = badge_class

            # Add member ID for invoice functionality
            member_dict['member_id'] = member_dict.get('id', '')

            members.append(member_dict)

        # Get unique statuses for filter dropdown
        cursor.execute("SELECT DISTINCT status FROM members WHERE status IS NOT NULL AND status != ''")
        statuses = [row[0] for row in cursor.fetchall()]

        return jsonify({
            'success': True,
            'members': members,
            'total_members': total_members,
            'statuses': statuses,
            'page': page,
            'total_pages': total_pages,
            'per_page': per_page
        })

    except Exception as e:
        logger.error(f"❌ Error getting members: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        try:
            if conn:
                conn.close()
        except Exception:
            pass

@app.route('/api/members/past-due')
def get_past_due_members():
    """Return red/yellow members from the local database (fast, reliable)."""
    try:
        conn = sqlite3.connect(db_manager.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, first_name, last_name, full_name, email, mobile_phone, status,
                   status_message, amount_past_due, amount_of_next_payment, date_of_next_payment
            FROM members
            WHERE (amount_past_due IS NOT NULL AND amount_past_due > 0)
               OR (
                    (date_of_next_payment IS NOT NULL AND date(date_of_next_payment) <= date('now', '+7 days'))
                    AND (amount_past_due IS NULL OR amount_past_due <= 0)
                  )
            ORDER BY COALESCE(amount_past_due, 0) DESC
            """
        )
        rows = cursor.fetchall()
        conn.close()

        members = []
        for r in rows:
            m = dict(r)
            first = m.get('first_name') or ''
            last = m.get('last_name') or ''
            if not (m.get('full_name') or '').strip():
                m['full_name'] = f"{first} {last}".strip() or (m.get('email') or 'Unknown Member')

            apd = float(m.get('amount_past_due') or 0)
            priority = 'red' if apd > 0 else 'yellow'
            m['priority_status'] = priority
            m['status_text'] = 'Past Due' if priority == 'red' else 'Due Soon'
            members.append(m)

        return jsonify({'success': True, 'past_due_members': members})
    except Exception as e:
        logger.error(f"❌ Error getting past due members: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/member/<member_id>')
def get_member_profile(member_id):
    """Get detailed member profile information from the local database (used by modal)."""
    try:
        conn = sqlite3.connect(db_manager.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM members WHERE id = ? LIMIT 1", (member_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return jsonify({'success': False, 'error': 'Member not found'}), 404

        member = dict(row)

        # Compute payment status
        amount_past_due = float(member.get('amount_past_due') or 0)
        next_amount = member.get('amount_of_next_payment')
        next_date = member.get('date_of_next_payment')

        pay_status = {'text': 'Current', 'class': 'success'}
        if amount_past_due > 0:
            pay_status = {'text': f"Past Due (${amount_past_due:.2f})", 'class': 'danger'}
        else:
            try:
                if next_date:
                    due_dt = datetime.fromisoformat(str(next_date).replace('Z','').split('T')[0])
                    if (due_dt - datetime.now()).days <= 7:
                        pay_status = {'text': 'Due Soon', 'class': 'warning'}
            except Exception:
                pass

        # Build agreements summary from flat columns (best-effort)
        agreements = []
        if member.get('agreement_id') or member.get('agreement_type') or member.get('agreement_start_date'):
            agreements.append({
                'agreement_id': member.get('agreement_id'),
                'agreement_type': member.get('agreement_type') or 'Membership',
                'start_date': member.get('agreement_start_date'),
                'end_date': member.get('agreement_end_date'),
                'rate': member.get('agreement_rate') or member.get('payment_amount'),
                'status': member.get('agreement_status') or member.get('status'),
            })

        # Payments history not stored; include next payment as a single entry if available
        payments = []
        if next_date or next_amount:
            payments.append({
                'payment_date': next_date,
                'amount': next_amount or member.get('payment_amount'),
                'payment_type': 'Scheduled',
                'status': 'pending' if amount_past_due == 0 else 'due'
            })

        return jsonify({
            'success': True,
            'member': member,
            'payment_status': pay_status,
            'agreements': agreements,
            'payments': payments
        })
    except Exception as e:
        logger.error(f"❌ Error getting member profile: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/prospects')
def prospects_page():
    """Display prospects page with fast loading - data loads asynchronously via JavaScript."""
    
    # Fast page load - render template immediately with minimal data
    return render_template('prospects.html',
                         prospects=[],  # Empty initially, loaded via JavaScript
                         total_prospects=0,  # Will be updated via API
                         statuses=[],
                         search='',
                         page=1,
                         total_pages=1,
                         per_page=50)

@app.route('/api/prospects/all')
def get_all_prospects():
    """API endpoint to get all prospects from ClubHub API."""
    try:
        # Get fresh prospects from ClubHub API instead of stale database
        from config.clubhub_credentials_clean import CLUBHUB_EMAIL, CLUBHUB_PASSWORD
        
        CLUBHUB_LOGIN_URL = "https://clubhub-ios-api.anytimefitness.com/api/login"
        USERNAME = CLUBHUB_EMAIL
        PASSWORD = CLUBHUB_PASSWORD
        
        headers = {
            "Content-Type": "application/json",
            "API-version": "1",
            "Accept": "application/json",
            "User-Agent": "ClubHub Store/2.15.1 (com.anytimefitness.Club-Hub; build:1007; iOS 18.5.0) Alamofire/5.6.4",
        }
        
        session = requests.Session()
        session.headers.update(headers)
        
        # Login to get bearer token
        login_data = {"username": USERNAME, "password": PASSWORD}
        login_response = session.post(CLUBHUB_LOGIN_URL, json=login_data)
        
        if login_response.status_code != 200:
            return jsonify({'success': False, 'error': 'Failed to authenticate with ClubHub API'}), 500
            
        login_result = login_response.json()
        bearer_token = login_result.get('accessToken')
        
        if not bearer_token:
            return jsonify({'success': False, 'error': 'No access token received'}), 500
            
        session.headers.update({"Authorization": f"Bearer {bearer_token}"})
        
        # Get prospects from ClubHub API
        club_id = "1156"
        all_prospects = []
        page = 1
        
        while True:
            prospects_url = f"https://clubhub-ios-api.anytimefitness.com/api/clubs/{club_id}/prospects?page={page}&pageSize=100"
            prospects_response = session.get(prospects_url)
            
            if prospects_response.status_code != 200:
                break
                
            prospects_data = prospects_response.json()
            
            if len(prospects_data) == 0:
                break
            
            # Process prospects data
            for prospect in prospects_data:
                prospect['full_name'] = f"{prospect.get('firstName', '')} {prospect.get('lastName', '')}".strip()
                
            all_prospects.extend(prospects_data)
            page += 1
            
            # Limit to prevent infinite loops
            if page > 50:
                break
        
        return jsonify({
            'success': True,
            'prospects': all_prospects,
            'total_prospects': len(all_prospects),
            'page': 1,
            'total_pages': 1,
            'per_page': len(all_prospects)
        })
        
    except Exception as e:
        logger.error(f"❌ Error getting prospects: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/training-clients')
def training_clients_page():
    """Display training clients page with fast loading - data loads asynchronously via JavaScript."""
    
    # Fast page load - render template immediately with minimal data
    # JavaScript will load the actual training client data asynchronously from ClubOS API
    return render_template('training_clients.html',
                         training_clients=[],  # Empty initially, loaded via JavaScript
                         total_training_clients=0,  # Will be updated via API
                         search='',
                         page=1,
                         total_pages=1,
                         per_page=50)

@app.route('/api/training-clients/all')
def get_all_training_clients():
    """API endpoint to get all training clients from local database - called asynchronously after page load."""
    try:
        logger.info("🏋️ Loading training clients from local database...")
        
        conn = sqlite3.connect(db_manager.db_path)
        cursor = conn.cursor()
        
        # Get all training clients with their details including past due amounts
        cursor.execute("""
            SELECT 
                member_name,
                clubos_member_id,
                package_summary,
                trainer_name,
                created_at,
                sessions_remaining,
                total_past_due,
                payment_status,
                package_details,
                member_id
            FROM training_clients 
            ORDER BY total_past_due DESC, member_name
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        # Format training clients data
        training_clients = []
        import json
        for row in rows:
            member_name, clubos_id, package_summary, trainer_name, created_at, sessions_remaining, total_past_due, payment_status, package_details, member_id = row
            
            # Parse package_details if it's stored as JSON string
            parsed_package_details = []
            if package_details:
                try:
                    parsed_package_details = json.loads(package_details) if isinstance(package_details, str) else package_details
                except:
                    pass
            
            training_clients.append({
                'member_name': member_name,
                'email': 'N/A',
                'clubos_member_id': clubos_id,
                'member_id': member_id or clubos_id,
                'package_name': package_summary or 'Training Package',
                'package_summary': package_summary or 'Training Package',
                'trainer_name': trainer_name or 'Jeremy Mayo',
                'created_at': created_at,
                'last_updated': created_at,
                'status': 'Active',
                'sessions_remaining': sessions_remaining or 0,
                'total_past_due': float(total_past_due or 0),
                'past_due_amount': float(total_past_due or 0),
                'payment_status': payment_status or ('Past Due' if (total_past_due or 0) > 0 else 'Current'),
                'package_details': parsed_package_details
            })
        
        logger.info(f"✅ Returning {len(training_clients)} training clients from database")
        
        return jsonify({
            'success': True,
            'training_clients': training_clients,
            'total_training_clients': len(training_clients),
            'page': 1,
            'total_pages': 1,
            'per_page': len(training_clients),
            'source': 'local_database'
        })
        
    except Exception as e:
        logger.error(f"❌ Error getting training clients from database: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/create-invoice', methods=['POST'])
def api_create_invoice():
    """API endpoint to create a Square invoice."""
    data = request.get_json()
    member_name = data.get('member_name')
    amount = data.get('amount')
    description = data.get('description', 'Overdue Payment')

    if not all([member_name, amount]):
        return jsonify({'success': False, 'error': 'Missing required invoice data (member_name and amount).'}), 400

    if not SQUARE_AVAILABLE:
        return jsonify({'success': False, 'error': 'Square payment service is not available.'}), 503

    try:
        # Convert amount to float if it's a string
        amount = float(amount)
        
        # Create the invoice using the working Square client
        invoice_url = create_square_invoice(member_name, amount, description)
        
        if invoice_url:
            return jsonify({
                'success': True, 
                'invoice_url': invoice_url,
                'message': f'Invoice created successfully for {member_name}'
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to create invoice.'}), 500
            
    except ValueError as e:
        return jsonify({'success': False, 'error': f'Invalid amount value: {amount}'}), 400
    except Exception as e:
        logger.error(f"Error creating Square invoice: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/calculate-invoice-amount', methods=['POST'])
def api_calculate_invoice_amount():
    """API endpoint to calculate invoice amount with late fees for a member."""
    data = request.get_json()
    member_id = data.get('member_id')
    
    if not member_id:
        return jsonify({'success': False, 'error': 'Missing member_id'}), 400
    
    try:
        # Get member data from database first
        conn = sqlite3.connect(db_manager.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT first_name, last_name, amount_past_due, amount_of_next_payment, 
                   payment_amount, agreement_rate 
            FROM members 
            WHERE id = ?
        """, (member_id,))
        
        member = cursor.fetchone()
        conn.close()
        
        if not member:
            return jsonify({'success': False, 'error': 'Member not found'}), 404
        
        # Calculate amounts
        past_due = float(member['amount_past_due'] or 0)
        next_payment = float(member['amount_of_next_payment'] or 0)
        monthly_rate = float(member['agreement_rate'] or member['payment_amount'] or 0)
        
        # Apply late fee if past due (using a standard $25 late fee)
        late_fee = 25.0 if past_due > 0 else 0.0
        
        # Calculate total invoice amount
        total_amount = past_due + late_fee
        
        # If no past due amount, use next payment amount
        if total_amount <= 0 and next_payment > 0:
            total_amount = next_payment
        
        # If still no amount, use monthly rate
        if total_amount <= 0 and monthly_rate > 0:
            total_amount = monthly_rate
        
        return jsonify({
            'success': True,
            'member_name': f"{member['first_name']} {member['last_name']}",
            'past_due_amount': past_due,
            'late_fee': late_fee,
            'total_amount': total_amount,
            'description': f"Payment for {member['first_name']} {member['last_name']}" + 
                          (f" - Past Due: ${past_due:.2f}" if past_due > 0 else "") +
                          (f" + Late Fee: ${late_fee:.2f}" if late_fee > 0 else "")
        })
        
    except Exception as e:
        logger.error(f"Error calculating invoice amount: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/refresh-members', methods=['POST'])
def api_refresh_members():
    """API endpoint to manually refresh member database with latest ClubHub data"""
    try:
        logger.info("🔄 Manual member refresh requested...")
        
        # Import ClubHub API client
        sys.path.append(os.path.join(os.path.dirname(__file__), 'services'))
        from api.clubhub_api_client import ClubHubAPIClient
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
        
        # Update database
        conn = sqlite3.connect(db_manager.db_path)
        cursor = conn.cursor()
        
        # Clear and repopulate members table
        cursor.execute('DELETE FROM members')
        
        updated_count = 0
        for member in fresh_members:
            try:
                member_data = {
                    'id': member.get('id'),
                    'first_name': member.get('firstName'),
                    'last_name': member.get('lastName'),
                    'full_name': f"{member.get('firstName', '')} {member.get('lastName', '')}".strip(),
                    'email': member.get('email'),
                    'mobile_phone': member.get('mobilePhone'),
                    'status': member.get('status'),
                    'status_message': member.get('statusMessage'),
                    'user_type': member.get('userType'),
                    'contract_types': str(member.get('contractTypes', [])),
                    'trial': member.get('trial', False),
                    'updated_at': datetime.now().isoformat()
                }
                
                # Remove None values
                member_data = {k: v for k, v in member_data.items() if v is not None}
                columns = ', '.join(member_data.keys())
                placeholders = ', '.join(['?' for _ in member_data.values()])
                
                cursor.execute(f'''
                    INSERT OR REPLACE INTO members ({columns})
                    VALUES ({placeholders})
                ''', list(member_data.values()))
                
                updated_count += 1
                
            except Exception as e:
                logger.error(f"❌ Error updating member: {e}")
                continue
        
        conn.commit()
        conn.close()
        
        logger.info(f"✅ Manual refresh complete: {updated_count} members updated")
        
        return jsonify({
            'success': True,
            'members_updated': updated_count,
            'total_members_found': len(fresh_members),
            'timestamp': datetime.now().isoformat(),
            'message': f'Successfully refreshed {updated_count} members from ClubHub'
        })
        
    except Exception as e:
        logger.error(f"❌ Error in manual member refresh: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/refresh-training-clients', methods=['POST', 'GET'])
def refresh_training_clients():
    """API endpoint to refresh training clients from ClubHub"""
    try:
        logger.info("🏋️ Refreshing training clients from ClubHub...")
        
        # Import ClubHub API client
        sys.path.append(os.path.join(os.path.dirname(__file__), 'services'))
        from api.clubhub_api_client import ClubHubAPIClient
        from config.clubhub_credentials import CLUBHUB_EMAIL, CLUBHUB_PASSWORD
        
        # Initialize and authenticate
        client = ClubHubAPIClient()
        if not client.authenticate(CLUBHUB_EMAIL, CLUBHUB_PASSWORD):
            return jsonify({
                'success': False,
                'error': 'ClubHub authentication failed'
            })
        
        # Get all members and check for training indicators
        members_response = client.get_all_members(page=1, page_size=1000)
        training_members = []
        dennis_training_info = None
        
        if members_response:
            for member in members_response:
                first_name = member.get('firstName', '').lower()
                last_name = member.get('lastName', '').lower()
                
                # Check if this member has training indicators
                has_training = False
                training_indicators = [
                    'training' in member.get('statusMessage', '').lower(),
                    'personal' in member.get('statusMessage', '').lower(),
                    member.get('agreementId'),  # Has an agreement
                    member.get('nextInvoiceSubtotal', 0) > 0  # Has invoice amount
                ]
                
                if any(training_indicators):
                    has_training = True
                
                # Special check for Dennis Rost
                if 'dennis' in first_name and 'rost' in last_name:
                    dennis_training_info = {
                        'member': member,
                        'has_training_indicators': has_training,
                        'indicators_found': [i for i, indicator in enumerate(training_indicators) if indicator]
                    }
                    logger.info(f"🎯 Found Dennis Rost - Training indicators: {has_training}")
                    logger.info(f"   Status: {member.get('statusMessage')}")
                    logger.info(f"   Agreement ID: {member.get('agreementId')}")
                    logger.info(f"   Invoice Subtotal: {member.get('nextInvoiceSubtotal')}")
                
                if has_training:
                    training_members.append(member)
        
        # Update training_clients table
        conn = sqlite3.connect(db_manager.db_path)
        cursor = conn.cursor()
        
        # Add new training clients found
        clients_added = 0
        for member in training_members:
            try:
                # Check if already exists
                cursor.execute("""
                    SELECT COUNT(*) FROM training_clients 
                    WHERE clubos_member_id = ?
                """, (member.get('id'),))
                
                if cursor.fetchone()[0] == 0:
                    # Add new training client
                    client_data = {
                        'clubos_member_id': member.get('id'),
                        'member_name': f"{member.get('firstName', '')} {member.get('lastName', '')}".strip(),
                        'agreement_name': 'Personal Training',  # Default
                        'trainer_name': 'Jeremy Mayo',  # Default
                        'next_invoice_subtotal': member.get('nextInvoiceSubtotal', 0),
                        'sessions_remaining': 0,  # Will need to be updated separately
                        'member_services': 'Personal Training'
                    }
                    
                    # Remove None values
                    client_data = {k: v for k, v in client_data.items() if v is not None}
                    columns = ', '.join(client_data.keys())
                    placeholders = ', '.join(['?' for _ in client_data.values()])
                    
                    cursor.execute(f'''
                        INSERT INTO training_clients ({columns})
                        VALUES ({placeholders})
                    ''', list(client_data.values()))
                    
                    clients_added += 1
                    logger.info(f"➕ Added training client: {client_data['member_name']}")
                    
            except Exception as e:
                logger.error(f"❌ Error adding training client {member.get('firstName')} {member.get('lastName')}: {e}")
        
        conn.commit()
        conn.close()
        
        logger.info(f"✅ Training clients refresh complete: {clients_added} new clients added")
        
        return jsonify({
            'success': True,
            'training_members_found': len(training_members),
            'clients_added': clients_added,
            'dennis_found': dennis_training_info is not None,
            'dennis_training_info': dennis_training_info,
            'message': f'Successfully refreshed training clients: {clients_added} new clients added'
        })
        
    except Exception as e:
        logger.error(f"❌ Error refreshing training clients: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

# --- New: Refresh training clients mapping directly from ClubOS PT dashboard ---
def refresh_training_clients_from_clubos() -> dict:
    """
    Scrape ClubOS Personal Training dashboard to map member names -> ClubOS member IDs,
    and upsert into training_clients table. This enables live funding lookups to resolve IDs.
    """
    try:
        api = ClubOSTrainingClientsAPI()
        if not api.authenticate():
            return {"success": False, "error": "ClubOS auth failed"}

        html = api.get_personal_training_dashboard()
        if not html:
            return {"success": False, "error": "Failed to load PT dashboard"}

        soup = BeautifulSoup(html, 'html.parser')
        import re

        mappings = []
        anchor_patterns = [
            re.compile(r"/action/Member(?:Profile)?/(\d+)")
        ]

        # Extract from <a href>
        for a in soup.find_all('a', href=True):
            href = a['href']
            text = (a.get_text() or '').strip()
            clubos_id = None
            for pat in anchor_patterns:
                m = pat.search(href)
                if m:
                    clubos_id = m.group(1)
                    break
            if not clubos_id:
                m2 = re.search(r"memberId=(\d+)", href)
                if m2:
                    clubos_id = m2.group(1)
            if clubos_id and text:
                mappings.append((int(clubos_id), text))

        # Extract from data attributes if present
        for el in soup.find_all(attrs={'data-member-id': True}):
            try:
                cid = int(el.get('data-member-id'))
                name = (el.get('data-member-name') or el.get_text() or '').strip()
                if cid and name:
                    mappings.append((cid, name))
            except Exception:
                pass

        # Deduplicate by clubos_id
        unique = {}
        for cid, name in mappings:
            unique.setdefault(cid, name)

        if not unique:
            logger.warning("⚠️ No member mappings discovered on PT dashboard")
            return {"success": False, "error": "No member mappings discovered"}

        conn = sqlite3.connect(db_manager.db_path)
        cursor = conn.cursor()
        added = 0
        updated = 0

        for cid, name in unique.items():
            try:
                cursor.execute("SELECT id, member_name FROM training_clients WHERE clubos_member_id = ?", (cid,))
                row = cursor.fetchone()
                if row:
                    if row[1] != name:
                        cursor.execute("UPDATE training_clients SET member_name = ? WHERE id = ?", (name, row[0]))
                        updated += 1
                else:
                    cursor.execute(
                        """
                        INSERT INTO training_clients (member_id, clubos_member_id, member_name)
                        VALUES (?, ?, ?)
                        """,
                        (cid, cid, name)
                    )
                    added += 1
            except Exception as e:
                logger.error(f"❌ Error upserting training client {cid} - {name}: {e}")

        conn.commit()
        conn.close()

        total = len(unique)
        logger.info(f"✅ ClubOS training clients refreshed. discovered={total}, added={added}, updated={updated}")
        return {"success": True, "discovered": total, "added": added, "updated": updated}

    except Exception as e:
        logger.error(f"❌ Error refreshing training clients from ClubOS: {e}")
        return {"success": False, "error": str(e)}

@app.route('/api/refresh-training-clients-clubos', methods=['POST', 'GET'])
def api_refresh_training_clients_clubos():
    """Refresh training clients with LIVE invoice data from ClubOS V2 API"""
    try:
        logger.info("🔄 Starting full training clients refresh with live invoice data...")
        
        # Use ClubOSIntegration to get fresh data with invoices
        from services.clubos_integration import ClubOSIntegration
        integration = ClubOSIntegration()
        
        # This fetches fresh data from ClubOS including invoices and billing
        training_clients = integration.get_training_clients()
        
        if not training_clients:
            return jsonify({
                'success': False,
                'error': 'No training clients returned from ClubOS'
            }), 500
        
        # Update the database with the fresh data
        conn = sqlite3.connect(db_manager.db_path)
        cursor = conn.cursor()
        
        updated = 0
        added = 0
        
        for client in training_clients:
            clubos_id = client.get('clubos_member_id') or client.get('member_id')
            member_name = client.get('member_name') or client.get('full_name')
            
            if not clubos_id or not member_name:
                continue
            
            # Prepare data for storage
            past_due = client.get('past_due_amount', 0) or client.get('total_past_due', 0)
            payment_status = client.get('payment_status', 'Current')
            package_summary = client.get('package_summary', '')
            trainer_name = client.get('trainer_name', 'Jeremy Mayo')
            agreement_count = client.get('agreement_count', 0)
            
            # Serialize package_details as JSON
            import json
            package_details_json = json.dumps(client.get('package_details', []))
            
            # Check if client exists
            cursor.execute(
                "SELECT id FROM training_clients WHERE clubos_member_id = ?",
                (clubos_id,)
            )
            row = cursor.fetchone()
            
            if row:
                # Update existing
                cursor.execute("""
                    UPDATE training_clients SET
                        member_name = ?,
                        total_past_due = ?,
                        past_due_amount = ?,
                        payment_status = ?,
                        package_summary = ?,
                        trainer_name = ?,
                        package_details = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE clubos_member_id = ?
                """, (member_name, past_due, past_due, payment_status, package_summary, trainer_name, package_details_json, clubos_id))
                updated += 1
            else:
                # Insert new
                cursor.execute("""
                    INSERT INTO training_clients (
                        member_id, clubos_member_id, member_name, total_past_due, past_due_amount,
                        payment_status, package_summary, trainer_name, package_details
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (clubos_id, clubos_id, member_name, past_due, past_due, payment_status, package_summary, trainer_name, package_details_json))
                added += 1
        
        conn.commit()
        conn.close()
        
        # Count how many have past due amounts
        past_due_count = sum(1 for c in training_clients if (c.get('past_due_amount', 0) or c.get('total_past_due', 0)) > 0)
        total_past_due = sum(c.get('past_due_amount', 0) or c.get('total_past_due', 0) for c in training_clients)
        
        logger.info(f"✅ Training clients refresh complete: {len(training_clients)} total, {updated} updated, {added} added, {past_due_count} past due (${total_past_due:.2f})")
        
        return jsonify({
            'success': True,
            'message': f'Refreshed {len(training_clients)} clients ({past_due_count} with past due amounts)',
            'total': len(training_clients),
            'updated': updated,
            'added': added,
            'past_due_count': past_due_count,
            'total_past_due': round(total_past_due, 2)
        })
        
    except Exception as e:
        logger.error(f"❌ Error refreshing training clients: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

# Dashboard Beta API Endpoints

@app.route('/api/members/list')
def api_members_list():
    """Get filtered list of members with pagination"""
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 50, type=int), 100)
        search = request.args.get('search', '', type=str)
        status_filter = request.args.get('status', '', type=str)  # ppv, comp, frozen, active
        
        conn = sqlite3.connect(db_manager.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Build query with filters
        where_conditions = []
        params = []
        
        if search:
            where_conditions.append('(full_name LIKE ? OR email LIKE ? OR mobile_phone LIKE ?)')
            search_term = f'%{search}%'
            params.extend([search_term, search_term, search_term])
        
        if status_filter:
            if status_filter == 'ppv':
                where_conditions.append('(trial = 1 OR status_message LIKE "%ppv%" OR status_message LIKE "%day pass%")')
            elif status_filter == 'comp':
                where_conditions.append('status_message LIKE "%comp%" OR status_message LIKE "%staff%"')
            elif status_filter == 'frozen':
                where_conditions.append('(status IN (2, 3) OR status_message LIKE "%frozen%" OR status_message LIKE "%hold%")')
            elif status_filter == 'active':
                where_conditions.append('status = 1 AND trial = 0')
        
        where_clause = ' AND '.join(where_conditions) if where_conditions else '1=1'
        
        # Get total count
        cursor.execute(f'SELECT COUNT(*) FROM members WHERE {where_clause}', params)
        total_count = cursor.fetchone()[0]
        
        # Get paginated results
        offset = (page - 1) * per_page
        cursor.execute(f'''
            SELECT id, full_name, email, mobile_phone, status, status_message, 
                   trial, user_type, last_activity_timestamp, created_at
            FROM members 
            WHERE {where_clause}
            ORDER BY full_name
            LIMIT ? OFFSET ?
        ''', params + [per_page, offset])
        
        members = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return jsonify({
            'success': True,
            'members': members,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total_count,
                'pages': (total_count + per_page - 1) // per_page
            }
        })
        
    except Exception as e:
        logger.error(f"❌ Error fetching members list: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/members/<int:member_id>')
def api_member_details(member_id):
    """Get full member details with funding, transactions, and messaging history"""
    try:
        conn = sqlite3.connect(db_manager.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get member basic info
        cursor.execute('SELECT * FROM members WHERE id = ?', (member_id,))
        member = cursor.fetchone()
        
        if not member:
            return jsonify({
                'success': False,
                'error': 'Member not found'
            }), 404
        
        member_data = dict(member)
        
        # Get funding status
        cursor.execute('SELECT * FROM funding_status_cache WHERE member_id = ? ORDER BY last_updated DESC LIMIT 1', (member_id,))
        funding = cursor.fetchone()
        member_data['funding_status'] = dict(funding) if funding else None
        
        # Get transaction history
        cursor.execute('''
            SELECT * FROM member_transactions 
            WHERE member_id = ? 
            ORDER BY created_at DESC 
            LIMIT 50
        ''', (member_id,))
        member_data['transactions'] = [dict(row) for row in cursor.fetchall()]
        
        # Get message threads
        cursor.execute('''
            SELECT * FROM message_threads 
            WHERE member_id = ? 
            ORDER BY last_message_at DESC 
            LIMIT 20
        ''', (member_id,))
        threads = [dict(row) for row in cursor.fetchall()]
        
        # Get recent messages for each thread
        for thread in threads:
            cursor.execute('''
                SELECT * FROM messages 
                WHERE thread_id = ? 
                ORDER BY created_at DESC 
                LIMIT 10
            ''', (thread['id'],))
            thread['recent_messages'] = [dict(row) for row in cursor.fetchall()]
        
        member_data['message_threads'] = threads
        
        conn.close()
        
        return jsonify({
            'success': True,
            'member': member_data
        })
        
    except Exception as e:
        logger.error(f"❌ Error fetching member details: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/training/clients')
def api_training_clients():
    """Get training clients list with agreement data"""
    try:
        # Use existing ClubOS training API to get authoritative list
        assignees = clubos_training_api.fetch_assignees()
        
        if not assignees:
            return jsonify({
                'success': False,
                'error': 'Failed to fetch training clients from ClubOS'
            }), 500
        
        # Enhance with agreement data
        enhanced_clients = []
        
        for client in assignees:
            client_data = dict(client)
            
            # Get agreements summary for this client
            try:
                member_id = client.get('member_id') or client.get('clubos_member_id')
                if member_id:
                    # Get payment status and agreements
                    payment_status = clubos_training_api.get_member_payment_status(member_id)
                    client_data['payment_status'] = payment_status
                    
                    # Get cached funding data
                    conn = sqlite3.connect(db_manager.db_path)
                    conn.row_factory = sqlite3.Row
                    cursor = conn.cursor()
                    cursor.execute('SELECT * FROM funding_status_cache WHERE clubos_member_id = ? ORDER BY last_updated DESC LIMIT 1', (member_id,))
                    funding = cursor.fetchone()
                    client_data['funding_cache'] = dict(funding) if funding else None
                    conn.close()
                
            except Exception as e:
                logger.warning(f"Could not get agreement data for client {client.get('member_name', 'Unknown')}: {e}")
                client_data['payment_status'] = 'Unknown'
                client_data['funding_cache'] = None
            
            enhanced_clients.append(client_data)
        
        return jsonify({
            'success': True,
            'clients': enhanced_clients
        })
        
    except Exception as e:
        logger.error(f"❌ Error fetching training clients: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/invoices/create', methods=['POST'])
def api_create_invoice():
    """Create single Square invoice for a member"""
    try:
        data = request.get_json()
        member_id = data.get('member_id')
        amount = data.get('amount')
        description = data.get('description', 'Training Package Payment')
        
        if not member_id or not amount:
            return jsonify({
                'success': False,
                'error': 'member_id and amount are required'
            }), 400
        
        # Get member details
        conn = sqlite3.connect(db_manager.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM members WHERE id = ?', (member_id,))
        member = cursor.fetchone()
        
        if not member:
            return jsonify({
                'success': False,
                'error': 'Member not found'
            }), 404
        
        # Import Square client
        from services.payments.square_client_simple import create_square_invoice
        
        # Create invoice
        result = create_square_invoice(
            member_name=member['full_name'],
            member_email=member['email'],
            amount=float(amount),
            description=description
        )
        
        if result and result.get('success'):
            # Log transaction
            cursor.execute('''
                INSERT INTO member_transactions 
                (member_id, clubos_member_id, member_name, type, amount, invoice_id, 
                 status, description, payment_method, square_data, meta_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                member_id,
                member.get('clubos_member_id'),
                member['full_name'],
                'invoice',
                amount,
                result.get('invoice_id'),
                'sent',
                description,
                'square',
                json.dumps(result.get('square_data', {})),
                json.dumps({'created_via': 'dashboard_api'})
            ))
            conn.commit()
        
        conn.close()
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"❌ Error creating invoice: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/invoices/batch', methods=['POST'])
def api_create_batch_invoices():
    """Create batch Square invoices for multiple members/clients"""
    try:
        data = request.get_json()
        target_type = data.get('type', 'members')  # 'members' or 'training_clients'
        filter_criteria = data.get('filter', 'past_due')  # 'past_due', 'all'
        
        # Import Square client
        from services.payments.square_client_simple import create_square_invoice
        
        results = []
        
        if target_type == 'training_clients':
            # Get training clients with past due status
            clients = clubos_training_api.fetch_assignees()
            for client in clients:
                try:
                    member_id = client.get('member_id') or client.get('clubos_member_id')
                    if member_id:
                        payment_status = clubos_training_api.get_member_payment_status(member_id)
                        if filter_criteria == 'all' or (filter_criteria == 'past_due' and payment_status == 'Past Due'):
                            # Create invoice for this client
                            result = create_square_invoice(
                                member_name=client.get('member_name', 'Unknown'),
                                member_email=client.get('email', ''),
                                amount=50.0,  # Default amount - should be configurable
                                description='Training Package Payment - Past Due'
                            )
                            results.append({
                                'member_name': client.get('member_name'),
                                'result': result
                            })
                except Exception as e:
                    logger.error(f"Error creating invoice for training client {client.get('member_name')}: {e}")
                    results.append({
                        'member_name': client.get('member_name'),
                        'result': {'success': False, 'error': str(e)}
                    })
        
        else:
            # Handle members batch invoicing
            return jsonify({
                'success': False,
                'error': 'Members batch invoicing not yet implemented'
            }), 501
        
        return jsonify({
            'success': True,
            'results': results,
            'summary': {
                'total_processed': len(results),
                'successful': len([r for r in results if r['result'].get('success')]),
                'failed': len([r for r in results if not r['result'].get('success')])
            }
        })
        
    except Exception as e:
        logger.error(f"❌ Error creating batch invoices: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/messaging/inbox/recent')
def api_messaging_inbox():
    """Get recent messaging inbox with aggregated threads"""
    try:
        conn = sqlite3.connect(db_manager.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get recent message threads
        cursor.execute('''
            SELECT mt.*, m.full_name as member_full_name, m.email as member_email
            FROM message_threads mt
            LEFT JOIN members m ON mt.member_id = m.id
            ORDER BY mt.last_message_at DESC
            LIMIT 50
        ''')
        
        threads = []
        for row in cursor.fetchall():
            thread_data = dict(row)
            
            # Get latest message for preview
            cursor.execute('''
                SELECT * FROM messages 
                WHERE thread_id = ? 
                ORDER BY created_at DESC 
                LIMIT 1
            ''', (thread_data['id'],))
            
            latest_message = cursor.fetchone()
            thread_data['latest_message'] = dict(latest_message) if latest_message else None
            
            threads.append(thread_data)
        
        conn.close()
        
        return jsonify({
            'success': True,
            'threads': threads
        })
        
    except Exception as e:
        logger.error(f"❌ Error fetching messaging inbox: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/messaging/thread')
def api_messaging_thread():
    """Get full messaging thread history for a member"""
    try:
        member_id = request.args.get('memberId', type=int)
        
        if not member_id:
            return jsonify({
                'success': False,
                'error': 'memberId parameter required'
            }), 400
        
        conn = sqlite3.connect(db_manager.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get all threads for this member
        cursor.execute('''
            SELECT * FROM message_threads 
            WHERE member_id = ? 
            ORDER BY created_at DESC
        ''', (member_id,))
        
        threads = []
        for thread_row in cursor.fetchall():
            thread_data = dict(thread_row)
            
            # Get all messages for this thread
            cursor.execute('''
                SELECT * FROM messages 
                WHERE thread_id = ? 
                ORDER BY created_at ASC
            ''', (thread_data['id'],))
            
            thread_data['messages'] = [dict(row) for row in cursor.fetchall()]
            threads.append(thread_data)
        
        conn.close()
        
        return jsonify({
            'success': True,
            'threads': threads
        })
        
    except Exception as e:
        logger.error(f"❌ Error fetching messaging thread: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/daily-report')
def api_daily_report():
    """Get daily report with aggregated metrics"""
    try:
        report_date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
        
        conn = sqlite3.connect(db_manager.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get or create daily report
        cursor.execute('SELECT * FROM daily_reports WHERE report_date = ?', (report_date,))
        report = cursor.fetchone()
        
        if not report:
            # Generate report for the requested date
            report_data = generate_daily_report(report_date)
            cursor.execute('''
                INSERT INTO daily_reports 
                (report_date, bulk_checkins_count, campaigns_sent, replies_received,
                 invoices_created, invoices_paid, appointments_completed, 
                 appointments_rescheduled, new_members, member_visits, revenue_collected, data_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                report_date,
                report_data.get('bulk_checkins_count', 0),
                report_data.get('campaigns_sent', 0),
                report_data.get('replies_received', 0),
                report_data.get('invoices_created', 0),
                report_data.get('invoices_paid', 0),
                report_data.get('appointments_completed', 0),
                report_data.get('appointments_rescheduled', 0),
                report_data.get('new_members', 0),
                report_data.get('member_visits', 0),
                report_data.get('revenue_collected', 0.0),
                json.dumps(report_data)
            ))
            conn.commit()
            
            # Fetch the newly created report
            cursor.execute('SELECT * FROM daily_reports WHERE report_date = ?', (report_date,))
            report = cursor.fetchone()
        
        conn.close()
        
        return jsonify({
            'success': True,
            'report': dict(report) if report else None
        })
        
    except Exception as e:
        logger.error(f"❌ Error fetching daily report: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Calendar Two-Way API Endpoints

@app.route('/api/calendar/events')
def api_calendar_events():
    """Get calendar events using iCal parser"""
    try:
        from ical_calendar_parser import iCalClubOSParser
        
        start_date = request.args.get('start', datetime.now().strftime('%Y-%m-%d'))
        end_date = request.args.get('end', (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'))
        
        # Use existing iCal parser
        parser = iCalClubOSParser()
        events = parser.get_events_for_date_range(start_date, end_date)
        
        return jsonify({
            'success': True,
            'events': events
        })
        
    except Exception as e:
        logger.error(f"❌ Error fetching calendar events: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/calendar/events', methods=['POST'])
def api_calendar_create_event():
    """Create new calendar event via ClubOS API"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['title', 'start_time', 'end_time']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Use ClubOS real calendar API
        calendar_api = ClubOSRealCalendarAPI()
        
        # Create event
        result = calendar_api.create_event(
            title=data['title'],
            start_time=data['start_time'],
            end_time=data['end_time'],
            description=data.get('description', ''),
            trainer_id=data.get('trainer_id'),
            client_id=data.get('client_id'),
            service_id=data.get('service_id')
        )
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"❌ Error creating calendar event: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/calendar/events/<int:event_id>', methods=['PUT'])
def api_calendar_update_event(event_id):
    """Update existing calendar event"""
    try:
        data = request.get_json()
        
        # Use ClubOS real calendar API
        calendar_api = ClubOSRealCalendarAPI()
        
        # Update event
        result = calendar_api.update_event(
            event_id=event_id,
            title=data.get('title'),
            start_time=data.get('start_time'),
            end_time=data.get('end_time'),
            description=data.get('description'),
            trainer_id=data.get('trainer_id'),
            client_id=data.get('client_id')
        )
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"❌ Error updating calendar event: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/calendar/events/<int:event_id>', methods=['DELETE'])
def api_calendar_delete_event(event_id):
    """Delete calendar event with confirmation requirement"""
    try:
        data = request.get_json() or {}
        confirmed = data.get('confirmed', False)
        
        if not confirmed:
            return jsonify({
                'success': False,
                'error': 'Deletion requires confirmed: true',
                'requires_confirmation': True
            }), 400
        
        # Use gym_bot_clean ClubOSEventDeletion
        event_deletion = ClubOSEventDeletion()
        
        # Delete event
        result = event_deletion.delete_event(event_id)
        
        # Log the deletion
        logger.info(f"📅 Calendar event deleted: {event_id} (confirmed deletion)")
        
        return jsonify({
            'success': True,
            'message': f'Event {event_id} deleted successfully',
            'deletion_result': result
        })
        
    except Exception as e:
        logger.error(f"❌ Error deleting calendar event: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def generate_daily_report(report_date: str) -> dict:
    """Generate daily report metrics for a specific date"""
    try:
        conn = sqlite3.connect(db_manager.db_path)
        cursor = conn.cursor()
        
        # Count bulk check-in runs for the date
        cursor.execute('''
            SELECT COUNT(*) FROM bulk_checkin_runs 
            WHERE DATE(started_at) = ?
        ''', (report_date,))
        bulk_checkins = cursor.fetchone()[0]
        
        # Count transactions/invoices created on the date
        cursor.execute('''
            SELECT COUNT(*) FROM member_transactions 
            WHERE type = 'invoice' AND DATE(created_at) = ?
        ''', (report_date,))
        invoices_created = cursor.fetchone()[0]
        
        # Count paid invoices
        cursor.execute('''
            SELECT COUNT(*) FROM member_transactions 
            WHERE type = 'invoice' AND status = 'paid' AND DATE(updated_at) = ?
        ''', (report_date,))
        invoices_paid = cursor.fetchone()[0]
        
        # Calculate revenue collected
        cursor.execute('''
            SELECT COALESCE(SUM(amount), 0) FROM member_transactions 
            WHERE type = 'invoice' AND status = 'paid' AND DATE(updated_at) = ?
        ''', (report_date,))
        revenue_collected = cursor.fetchone()[0]
        
        # Count new members (if we track join dates)
        cursor.execute('''
            SELECT COUNT(*) FROM members 
            WHERE DATE(created_at) = ?
        ''', (report_date,))
        new_members = cursor.fetchone()[0]
        
        # Count messages received
        cursor.execute('''
            SELECT COUNT(*) FROM messages 
            WHERE direction = 'inbound' AND DATE(created_at) = ?
        ''', (report_date,))
        replies_received = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'bulk_checkins_count': bulk_checkins,
            'campaigns_sent': 0,  # Placeholder - implement based on actual campaign system
            'replies_received': replies_received,
            'invoices_created': invoices_created,
            'invoices_paid': invoices_paid,
            'appointments_completed': 0,  # Placeholder - implement based on calendar system
            'appointments_rescheduled': 0,  # Placeholder
            'new_members': new_members,
            'member_visits': 0,  # Placeholder - would need check-in data
            'revenue_collected': float(revenue_collected)
        }
        
    except Exception as e:
        logger.error(f"❌ Error generating daily report: {e}")
        return {}

@app.route('/calendar')
def calendar_page():
    """Display calendar page."""
    return render_template('calendar.html')


# ============================================
# AI SETTINGS & WORKFLOWS INTEGRATION
# ============================================

# Initialize AI modules
_ai_workflow_manager = None
_ai_knowledge_base = None

def init_ai_modules():
    """Initialize AI workflow manager and knowledge base"""
    global _ai_workflow_manager, _ai_knowledge_base
    
    try:
        from src.services.ai.knowledge_base import AIKnowledgeBase
        from src.services.ai.unified_workflow_manager import UnifiedWorkflowManager
        
        _ai_knowledge_base = AIKnowledgeBase(db_manager)
        _ai_workflow_manager = UnifiedWorkflowManager(db_manager, _ai_knowledge_base)
        
        logger.info("✅ AI modules initialized (Knowledge Base + Workflow Manager)")
    except Exception as e:
        logger.warning(f"⚠️ AI modules not fully available: {e}")


@app.route('/ai-settings')
def ai_settings_page():
    """Display AI settings and workflow management page."""
    return render_template('ai_settings.html')


@app.route('/api/ai/workflows', methods=['GET'])
def api_get_workflows():
    """Get all registered workflows with their status."""
    try:
        if not _ai_workflow_manager:
            init_ai_modules()
        
        if not _ai_workflow_manager:
            return jsonify({"success": False, "error": "Workflow manager not available"}), 503
        
        workflows = _ai_workflow_manager.get_all_workflow_statuses()
        
        return jsonify({
            "success": True,
            "workflows": workflows,
            "background_worker_running": _ai_workflow_manager.is_running
        })
    except Exception as e:
        logger.error(f"Error getting workflows: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/ai/workflows/<workflow_name>/enable', methods=['POST'])
def api_enable_workflow(workflow_name):
    """Enable a workflow."""
    try:
        if not _ai_workflow_manager:
            init_ai_modules()
        
        success = _ai_workflow_manager.enable_workflow(workflow_name)
        return jsonify({
            "success": success,
            "workflow_name": workflow_name,
            "enabled": True,
            "message": f"Workflow '{workflow_name}' enabled"
        })
    except Exception as e:
        logger.error(f"Error enabling workflow: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/ai/workflows/<workflow_name>/disable', methods=['POST'])
def api_disable_workflow(workflow_name):
    """Disable a workflow."""
    try:
        if not _ai_workflow_manager:
            init_ai_modules()
        
        success = _ai_workflow_manager.disable_workflow(workflow_name)
        return jsonify({
            "success": success,
            "workflow_name": workflow_name,
            "enabled": False,
            "message": f"Workflow '{workflow_name}' disabled"
        })
    except Exception as e:
        logger.error(f"Error disabling workflow: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/ai/workflows/<workflow_name>/run', methods=['POST'])
def api_run_workflow(workflow_name):
    """Manually trigger a workflow to run."""
    try:
        if not _ai_workflow_manager:
            init_ai_modules()
        
        data = request.get_json() or {}
        force = data.get('force', False)
        
        result = _ai_workflow_manager.run_workflow(workflow_name, force=force)
        
        return jsonify({
            "success": result.get("success", False),
            "workflow_name": workflow_name,
            "result": result
        })
    except Exception as e:
        logger.error(f"Error running workflow: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/ai/sync-clubos-leads', methods=['POST'])
def api_sync_clubos_leads():
    """Fetch and sync leads from ClubOS to the prospects table in real-time."""
    try:
        from clubos_leads_api import ClubOSLeadsAPI
        
        leads_api = ClubOSLeadsAPI()
        if not leads_api.authenticate():
            return jsonify({"success": False, "error": "ClubOS authentication failed"}), 401
        
        # Fetch leads
        clubos_leads = leads_api.get_leads(limit=100)
        
        synced = 0
        skipped = 0
        errors = []
        
        for lead in clubos_leads:
            formatted = leads_api.format_lead_for_outreach(lead)
            prospect_id = str(formatted.get('id', ''))
            
            if not prospect_id:
                continue
            
            try:
                # Check if already exists
                existing = db_manager.execute_query(
                    "SELECT prospect_id FROM prospects WHERE prospect_id = ?",
                    (prospect_id,),
                    fetch_one=True
                )
                
                if not existing:
                    # Insert new prospect from ClubOS lead
                    db_manager.execute_query(
                        """
                        INSERT INTO prospects (
                            prospect_id, first_name, last_name, full_name,
                            email, mobile_phone, source, status, created_date
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, 'New Lead', ?)
                        """,
                        (
                            prospect_id,
                            formatted.get('first_name', ''),
                            formatted.get('last_name', ''),
                            formatted.get('full_name', ''),
                            formatted.get('email', ''),
                            formatted.get('phone', ''),
                            formatted.get('source', 'ClubOS'),
                            formatted.get('created_date', datetime.now().isoformat())
                        )
                    )
                    synced += 1
                else:
                    skipped += 1
            except Exception as e:
                errors.append(f"{formatted.get('full_name')}: {str(e)}")
        
        return jsonify({
            "success": True,
            "leads_fetched": len(clubos_leads),
            "synced": synced,
            "skipped_existing": skipped,
            "errors": errors if errors else None
        })
    except ImportError:
        return jsonify({"success": False, "error": "ClubOS leads API not available"}), 503
    except Exception as e:
        logger.error(f"Error syncing ClubOS leads: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/ai/knowledge-base', methods=['GET'])
def api_get_knowledge_base():
    """Get all knowledge base documents grouped by category."""
    try:
        if not _ai_knowledge_base:
            init_ai_modules()
        
        if not _ai_knowledge_base:
            return jsonify({"success": False, "error": "Knowledge base not available"}), 503
        
        all_docs = _ai_knowledge_base.get_all_documents()
        categories = _ai_knowledge_base.CATEGORIES
        
        return jsonify({
            "success": True,
            "documents": all_docs,
            "categories": categories,
            "total_count": sum(len(docs) for docs in all_docs.values())
        })
    except Exception as e:
        logger.error(f"Error getting knowledge base: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/ai/knowledge-base', methods=['POST'])
def api_add_kb_document():
    """Add a new document to the knowledge base."""
    try:
        if not _ai_knowledge_base:
            init_ai_modules()
        
        data = request.get_json()
        
        required = ['category', 'title', 'content']
        for field in required:
            if field not in data:
                return jsonify({"success": False, "error": f"Missing required field: {field}"}), 400
        
        success = _ai_knowledge_base.add_document(
            category=data['category'],
            title=data['title'],
            content=data['content'],
            priority=data.get('priority', 1)
        )
        
        return jsonify({
            "success": success,
            "message": f"Document '{data['title']}' added to {data['category']}"
        })
    except Exception as e:
        logger.error(f"Error adding KB document: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/ai/knowledge-base/<category>/<title>', methods=['DELETE'])
def api_delete_kb_document(category, title):
    """Delete a knowledge base document."""
    try:
        if not _ai_knowledge_base:
            init_ai_modules()
        
        success = _ai_knowledge_base.delete_document(category, title)
        
        return jsonify({
            "success": success,
            "message": f"Document '{title}' deleted from {category}"
        })
    except Exception as e:
        logger.error(f"Error deleting KB document: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/ai/payment-plan-exemptions', methods=['GET'])
def api_get_payment_exemptions():
    """Get all members with payment plan exemptions."""
    try:
        rows = db_manager.execute_query(
            """
            SELECT member_id, name, email, phone, payment_plan_exempt, past_due_amount, past_due_days
            FROM members 
            WHERE payment_plan_exempt = 1
            ORDER BY name
            """,
            fetch_all=True
        )
        
        exempt_members = []
        for row in (rows or []):
            exempt_members.append({
                "member_id": row[0],
                "name": row[1],
                "email": row[2],
                "phone": row[3],
                "exempt": bool(row[4]) if row[4] else False,
                "past_due_amount": row[5],
                "past_due_days": row[6]
            })
        
        return jsonify({
            "success": True,
            "exempt_members": exempt_members,
            "count": len(exempt_members)
        })
    except Exception as e:
        logger.error(f"Error getting payment exemptions: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/ai/payment-plan-exemptions/<member_id>', methods=['POST'])
def api_add_payment_exemption(member_id):
    """Add payment plan exemption for a member."""
    try:
        db_manager.execute_query(
            "UPDATE members SET payment_plan_exempt = 1 WHERE member_id = ?",
            (member_id,)
        )
        
        logger.info(f"Added payment plan exemption for member {member_id}")
        
        return jsonify({
            "success": True,
            "member_id": member_id,
            "exempt": True,
            "message": f"Payment plan exemption added for member {member_id}"
        })
    except Exception as e:
        logger.error(f"Error adding payment exemption: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/ai/payment-plan-exemptions/<member_id>', methods=['DELETE'])
def api_remove_payment_exemption(member_id):
    """Remove payment plan exemption for a member."""
    try:
        db_manager.execute_query(
            "UPDATE members SET payment_plan_exempt = 0 WHERE member_id = ?",
            (member_id,)
        )
        
        logger.info(f"Removed payment plan exemption for member {member_id}")
        
        return jsonify({
            "success": True,
            "member_id": member_id,
            "exempt": False,
            "message": f"Payment plan exemption removed for member {member_id}"
        })
    except Exception as e:
        logger.error(f"Error removing payment exemption: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/ai/worker/status', methods=['GET'])
def api_get_worker_status():
    """Get background worker status."""
    try:
        if not _ai_workflow_manager:
            init_ai_modules()
        
        return jsonify({
            "success": True,
            "running": _ai_workflow_manager.is_running if _ai_workflow_manager else False
        })
    except Exception as e:
        logger.error(f"Error getting worker status: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/ai/worker/start', methods=['POST'])
def api_start_worker():
    """Start the background workflow worker."""
    try:
        if not _ai_workflow_manager:
            init_ai_modules()
        
        data = request.get_json() or {}
        interval = data.get('check_interval_seconds', 60)
        
        _ai_workflow_manager.start_background_worker(interval)
        
        return jsonify({
            "success": True,
            "message": f"Background worker started (checking every {interval}s)",
            "running": True
        })
    except Exception as e:
        logger.error(f"Error starting background worker: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/ai/worker/stop', methods=['POST'])
def api_stop_worker():
    """Stop the background workflow worker."""
    try:
        if not _ai_workflow_manager:
            return jsonify({"success": True, "running": False})
        
        _ai_workflow_manager.stop_background_worker()
        
        return jsonify({
            "success": True,
            "message": "Background worker stopped",
            "running": False
        })
    except Exception as e:
        logger.error(f"Error stopping background worker: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# Initialize AI modules on startup
try:
    init_ai_modules()
except Exception as e:
    logger.warning(f"⚠️ AI modules initialization deferred: {e}")


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
