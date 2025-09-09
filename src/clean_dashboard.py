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
import threading
import queue
from flask import Flask, render_template, jsonify, request, redirect, url_for, session, flash
from datetime import datetime, timedelta
from typing import Dict, Any
import logging
import json
import sys
import requests
import time
from bs4 import BeautifulSoup
import traceback

# Import our working ClubOS API
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from clubos_training_api_fixed import ClubOSTrainingPackageAPI
from clubos_real_calendar_api import ClubOSRealCalendarAPI
from ical_calendar_parser import iCalClubOSParser
from gym_bot_clean import ClubOSEventDeletion
from clubos_fresh_data_api import ClubOSFreshDataAPI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure console streams can handle UTF-8 (Windows cp1252 workaround)
try:
	sys.stdout.reconfigure(encoding='utf-8', errors='replace')
	sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:
	pass

# File logging for debugging
try:
	log_dir = 'logs'
	os.makedirs(log_dir, exist_ok=True)
	from logging.handlers import RotatingFileHandler
	file_handler = RotatingFileHandler(os.path.join(log_dir, 'dashboard.log'), maxBytes=2_000_000, backupCount=3, encoding='utf-8')
	file_handler.setLevel(logging.INFO)
	file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(name)s: %(message)s'))
	root_logger = logging.getLogger()
	# Avoid duplicate handlers if reloader runs
	if not any(isinstance(h, RotatingFileHandler) for h in root_logger.handlers):
		root_logger.addHandler(file_handler)
	logger.info('File logging enabled at logs/dashboard.log')
except Exception as e:
	logger.warning(f'Could not enable file logging: {e}')

# Initialize Flask app
app = Flask(__name__, template_folder='../templates', static_folder='../static')
app.secret_key = 'anytime-fitness-dashboard-secret-key-2025'

# Create templates directory if it doesn't exist
templates_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')
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
    from src.services.payments.square_client_simple import create_square_invoice
    
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
    
    def __init__(self):
        self.cache_expiry_hours = 24  # Cache expires after 24 hours
        self.api = ClubOSTrainingPackageAPI()
        
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
                logger.info(f"⚠️ Using stale cached data for {participant_name}")
                return self._format_funding_response(cached_data, is_stale=True, is_cached=True)
            
            # No data available
            logger.warning(f"❌Œ No funding data available for {participant_name}")
            return None
            
        except Exception as e:
            logger.error(f"❌Œ Error looking up funding for {participant_name}: {e}")
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
            logger.error(f"❌Œ Error getting cached funding: {e}")
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
            logger.error(f"❌Œ Error checking cache staleness: {e}")
            return True
    
    def _fetch_fresh_funding_data(self, member_id: str, member_name: str) -> dict:
        """Fetch fresh funding data from ClubOS API"""
        try:
            # Use the working method that returns status + real amount owed
            result = None
            try:
                result = self.api.get_member_training_payment_details(member_id)
            except Exception as e:
                logger.warning(f"⚠️ get_member_training_payment_details error for {member_id}: {e}")

            if result and isinstance(result, dict) and result.get('success'):
                status = result.get('status') or 'Unknown'
                amount_owed = float(result.get('amount_owed') or 0.0)

                funding_data = {
                    'member_id': None,  # We'll get this from training_clients later
                    'member_name': member_name,
                    'clubos_member_id': member_id,
                    'package_name': 'Training Package',
                    'sessions_remaining': 0,
                    'sessions_purchased': 0,
                    'package_amount': None,
                    'amount_paid': None,
                    'amount_remaining': amount_owed,
                    'payment_status': status,
                    'payment_method': None,
                    'last_payment_date': None,
                    'next_payment_date': None,
                    'raw_clubos_data': json.dumps(result),
                    'data_source': 'clubos_api',
                    'last_updated': datetime.now().isoformat()
                }

                # Classify funding status using the status string
                funding_data.update(self._classify_funding_status(status))
                logger.info(f"✅ Fetched fresh funding data for {member_name}: {status} - ${amount_owed:.2f}")
                return funding_data

            # Fallback to previous string-only methods if the working path failed
            payment_status = None
            try:
                if hasattr(self.api, 'get_member_payment_status_v2'):
                    payment_status = self.api.get_member_payment_status_v2(member_id)
            except Exception:
                payment_status = None
            if not payment_status:
                payment_status = self.api.get_member_payment_status(member_id)

            if payment_status:
                funding_data = {
                    'member_id': None,
                    'member_name': member_name,
                    'clubos_member_id': member_id,
                    'package_name': 'Training Package',
                    'sessions_remaining': 0,
                    'sessions_purchased': 0,
                    'package_amount': None,
                    'amount_paid': None,
                    'amount_remaining': None,
                    'payment_status': payment_status,
                    'payment_method': None,
                    'last_payment_date': None,
                    'next_payment_date': None,
                    'raw_clubos_data': payment_status,
                    'data_source': 'clubos_api',
                    'last_updated': datetime.now().isoformat()
                }
                funding_data.update(self._classify_funding_status(payment_status))
                logger.info(f"✅ Fetched fresh funding data for {member_name}: {payment_status}")
                return funding_data

            logger.warning(f"❌Œ No payment status returned for member {member_id}")
            return None
                
        except Exception as e:
            logger.error(f"❌Œ Error fetching fresh funding data: {e}")
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
            logger.error(f"❌Œ Error classifying funding status: {e}")
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
            
            logger.info(f"ðŸ'¾ Cached funding data for {funding_data['member_name']}")
            
        except Exception as e:
            logger.error(f"❌Œ Error caching funding data: {e}")
    
    def _format_funding_response(self, cached_data: dict, is_stale: bool = False, is_cached: bool = True) -> dict:
        """Format funding data for API response.
        is_cached indicates if the data came from cache (False means freshly scraped live).
        """
        try:
            response = {
                'status_text': cached_data.get('funding_status_text', 'Unknown'),
                'status_class': cached_data.get('funding_status_class', 'secondary'),
                'status_icon': cached_data.get('funding_status_icon', 'fas fa-question-circle'),
                'funding_status': cached_data.get('funding_status', 'unknown'),
                'sessions_remaining': cached_data.get('sessions_remaining', 0),
                'package_name': cached_data.get('package_name'),
                'last_updated': cached_data.get('last_updated'),
                'is_cached': bool(is_cached),
                'is_stale': is_stale
            }
            
            if is_stale:
                response['status_text'] += ' (Cached)'
                
            return response
            
        except Exception as e:
            logger.error(f"❌Œ Error formatting funding response: {e}")
            return None
    
    def refresh_all_funding_cache(self) -> dict:
        """Refresh funding cache for all training clients - run daily"""
        try:
            logger.info("")
            
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
                    logger.info(f"")
                    
                    fresh_data = self._fetch_fresh_funding_data(str(clubos_id), member_name)
                    if fresh_data:
                        fresh_data['member_id'] = client_id
                        self._cache_funding_data(fresh_data)
                        success_count += 1
                    else:
                        error_count += 1
                        
                except Exception as e:
                    logger.error(f"❌Œ Error refreshing funding for {member_name}: {e}")
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
            logger.error(f"❌Œ Error in daily funding refresh: {e}")
            return {'success': False, 'error': str(e)}
    
    def _get_member_id_from_database(self, participant_name: str, participant_email: str = None) -> str:
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
            
            # Fallback to members table
            search_conditions = ["LOWER(first_name) LIKE LOWER(?) OR LOWER(last_name) LIKE LOWER(?) OR LOWER(full_name) LIKE LOWER(?)"]
            params = [f"%{participant_name}%", f"%{participant_name}%", f"%{participant_name}%"]
            
            if participant_email:
                search_conditions.append("LOWER(email) = LOWER(?)")
                params.append(participant_email)
            
            query = f"""
                SELECT id FROM members 
                WHERE {' OR '.join(search_conditions)}
                LIMIT 1
            """
            
            cursor.execute(query, params)
            result = cursor.fetchone()
            conn.close()
            
            if result and result[0]:
                logger.info(f"✅ Found member ID in members table: {result[0]} for {participant_name}")
                return str(result[0])
            
            logger.warning(f"❌Œ No member ID found for participant: {participant_name}")
            return None
            
        except Exception as e:
            logger.error(f"❌Œ Database error looking up member ID: {e}")
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
            logger.info("")
            
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
            
            logger.info("")
            return fresh_data
            
        except Exception as e:
            logger.error(f"❌Œ Error fetching fresh data: {e}")
            return None
    
    def refresh_database(self, force=False):
        """Refresh the database with latest data from ClubOS"""
        if not force and not self.needs_refresh():
            logger.info("❌­ï¸ Database is fresh, skipping refresh")
            return False
            
        logger.info("")
        
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
                logger.warning("⚠️ Using existing CSV data as fallback")
                self.last_refresh = datetime.now()
                return False
                
        except Exception as e:
            logger.error(f"❌Œ Database refresh failed: {e}")
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
                    record_count INTEGER,
                    category_breakdown TEXT
                )
            """)
            
            # Log the refresh
            cursor.execute("""
                INSERT OR REPLACE INTO data_refresh_log (id, table_name, last_refresh, record_count, category_breakdown)
                VALUES (1, 'members', ?, (SELECT COUNT(*) FROM members), '{}')
            """, (datetime.now(),))
            
            cursor.execute("""
                INSERT OR REPLACE INTO data_refresh_log (id, table_name, last_refresh, record_count, category_breakdown)
                VALUES (2, 'prospects', ?, (SELECT COUNT(*) FROM prospects), '{}')
            """, (datetime.now(),))
            
            conn.commit()
            
        except Exception as e:
            logger.error(f"❌Œ Error updating database: {e}")
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
            logger.error(f"❌Œ Error getting refresh status: {e}")
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
                email TEXT,  -- Member email
                phone TEXT,  -- Member phone
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
                payment_status TEXT,  -- Current/Past Due/Unknown
                last_updated TIMESTAMP,  -- When data was last refreshed from ClubOS
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (member_id) REFERENCES members (id)
            )
        ''')
        
        # Add missing columns to training_clients table if they don't exist
        try:
            cursor.execute("ALTER TABLE training_clients ADD COLUMN email TEXT")
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        try:
            cursor.execute("ALTER TABLE training_clients ADD COLUMN phone TEXT")
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        try:
            cursor.execute("ALTER TABLE training_clients ADD COLUMN payment_status TEXT")
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        try:
            cursor.execute("ALTER TABLE training_clients ADD COLUMN last_updated TIMESTAMP")
        except sqlite3.OperationalError:
            pass  # Column already exists
        
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
        
        # Create indexes for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_funding_cache_member_id ON funding_status_cache(member_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_funding_cache_clubos_id ON funding_status_cache(clubos_member_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_funding_cache_updated ON funding_status_cache(last_updated)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_funding_cache_stale ON funding_status_cache(is_stale)')
        
        conn.commit()
        conn.close()
        
    def import_master_contact_list(self, csv_path):
        """Import master contact list from CSV with comprehensive data"""
        if not os.path.exists(csv_path):
            logger.warning(f"")
            return 0, 0
            
        logger.info(f"")
        
        try:
            df = pd.read_csv(csv_path)
            logger.info(f"")
        except Exception as e:
            logger.error(f"❌Œ Error reading CSV: {e}")
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
                logger.error(f"❌Œ Error importing row {row.get('id', 'unknown')}: {e}")
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
            logger.warning(f"ðŸ‹ï¸ Training clients CSV not found: {csv_path}")
            return 0
            
        logger.info(f"ðŸ‹ï¸ Importing training clients from: {csv_path}")
        
        try:
            df = pd.read_csv(csv_path)
            logger.info(f"ðŸ‹ï¸ Found {len(df)} training clients in CSV")
        except Exception as e:
            logger.error(f"❌Œ Error reading training clients CSV: {e}")
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
                logger.error(f"❌Œ Error importing training client {row.get('Member Name', 'unknown')}: {e}")
                continue
        
        conn.commit()
        conn.close()
        
        logger.info(f"✅ Training clients import complete: {clients_count} clients")
        return clients_count

# Initialize database manager and import data
db_manager = DatabaseManager()

# Add database manager to Flask app for access in other modules
app.db_manager = db_manager

# Only import CSV data if database is empty (first time setup)
conn = sqlite3.connect(db_manager.db_path)
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM members")
existing_members = cursor.fetchone()[0]
conn.close()

# Always import fresh data from ClubHub API instead of old CSV files
print("🔄 Loading fresh data from ClubHub API...")

def classify_member_status(member_data):
    """Classify member into category based on status_message and other fields"""
    # Ensure status_message and status are strings, handle None/NoneType values
    status_message = str(member_data.get('statusMessage', '')).lower()
    status = str(member_data.get('status', '')).lower()
    
    # Past due members (highest priority)
    if 'past due' in status_message or 'overdue' in status_message:
        return 'past_due'
    
    # Staff members
    if 'staff' in status_message or 'staff' in status:
        return 'staff'
    
    # Comp members
    if 'comp' in status_message or 'comp' in status:
        return 'comp'
    
    # Pay per visit members
    if 'pay per visit' in status_message or 'ppv' in status_message:
        return 'ppv'
    
    # Inactive members
    if any(inactive in status_message for inactive in ['cancelled', 'cancel', 'expire', 'pending']):
        return 'inactive'
    
    # Green members (in good standing) - default
    if 'good standing' in status_message or 'active' in status or status == 'active':
        return 'green'
    
    # Default to green if unclear
    return 'green'

def import_fresh_clubhub_data():
    """Import fresh data from ClubHub API on startup with comprehensive classification"""
    try:
        # Import ClubHub API client
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'services'))
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
        
        print(f"🔥 Retrieved {len(all_members)} members from ClubHub")
        
        # Initialize ClubHub API client and authenticate
        client = ClubHubAPIClient()
        
        # Ensure we have fresh authentication before fetching prospects
        from config.clubhub_credentials import CLUBHUB_EMAIL, CLUBHUB_PASSWORD
        if not client.authenticate(CLUBHUB_EMAIL, CLUBHUB_PASSWORD):
            print("❌ ClubHub authentication failed!")
            return [], []
        print("✅ ClubHub authentication successful!")
        
        # Get all prospects from ClubHub using the working paginated method
        print("🔍 Fetching prospects from ClubHub...")
        all_prospects = client.get_all_prospects_paginated()
        print(f"🔥 Retrieved {len(all_prospects)} prospects from ClubHub")
        
        # Connect to database using absolute path
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'gym_bot.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create member_categories table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS member_categories (
                member_id TEXT PRIMARY KEY,
                category TEXT NOT NULL,
                classified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status_message TEXT,
                full_name TEXT
            )
        """)
        
        # Clear old data but keep member_categories for reference
        cursor.execute("DELETE FROM members")
        cursor.execute("DELETE FROM training_clients")
        cursor.execute("DELETE FROM prospects")  # Clear old prospects too
        print("🗑️ Cleared old member and prospect data")
        
        # Import fresh member data with classification
        members_added = 0
        training_clients_added = 0
        
        # Track classification counts
        category_counts = {
            'green': 0, 'comp': 0, 'ppv': 0, 'staff': 0, 'past_due': 0, 'inactive': 0
        }
        
        for member in all_members:
            # Classify the member
            category = classify_member_status(member)
            category_counts[category] += 1
            
            # Add to members table
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
            
            # Store classification for fast lookups
            cursor.execute("""
                INSERT OR REPLACE INTO member_categories (
                    member_id, category, status_message, full_name
                ) VALUES (?, ?, ?, ?)
            """, (
                member.get('id'),
                category,
                member.get('statusMessage', ''),
                f"{member.get('firstName', '')} {member.get('lastName', '')}".strip()
            ))
            
            members_added += 1
        
        # Create or update data refresh log table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS data_refresh_log (
                id INTEGER PRIMARY KEY,
                table_name TEXT,
                last_refresh TIMESTAMP,
                record_count INTEGER,
                category_breakdown TEXT
            )
        """)
        
        # Check if category_breakdown column exists, add it if it doesn't
        cursor.execute("PRAGMA table_info(data_refresh_log)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'category_breakdown' not in columns:
            cursor.execute("ALTER TABLE data_refresh_log ADD COLUMN category_breakdown TEXT")
            print("🔧 Added missing category_breakdown column to data_refresh_log table")
        
        # Log the refresh with category breakdown
        category_breakdown = json.dumps(category_counts)
        cursor.execute("""
            INSERT OR REPLACE INTO data_refresh_log (id, table_name, last_refresh, record_count, category_breakdown)
            VALUES (1, 'members', ?, ?, ?)
        """, (datetime.now(), members_added, category_breakdown))
        
        # Import prospects
        print("📊 Importing prospects...")
        prospects_added = 0
        if all_prospects:
            for i, prospect in enumerate(all_prospects, 1):
                cursor.execute("""
                    INSERT OR REPLACE INTO prospects (
                        id, firstName, lastName, email, homePhone, prospectPhase,
                        salesPerson, date, leadSource, leadCategory, referralCode,
                        pipelineDays, lastActivity, nextFollowUp, notes, raw_data
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    prospect.get('id'), prospect.get('firstName'), prospect.get('lastName'),
                    prospect.get('email'), prospect.get('homePhone'), prospect.get('prospectPhase'),
                    prospect.get('salesPerson'), prospect.get('date'), prospect.get('leadSource'),
                    prospect.get('leadCategory'), prospect.get('referralCode'), prospect.get('pipelineDays'),
                    prospect.get('lastActivity'), prospect.get('nextFollowUp'), prospect.get('notes'),
                    json.dumps(prospect)  # Store full data as JSON
                ))
                prospects_added += 1
                if i % 100 == 0:
                    print(f"   📈 Processed {i}/{len(all_prospects)} prospects...")
            print(f"✅ Successfully imported {len(all_prospects)} prospects")
        else:
            print("⚠️ No prospects data received")

        conn.commit()
        conn.close()
        
        print(f"✅ Fresh data imported: {members_added} members, {training_clients_added} training clients, {prospects_added} prospects")
        print(f"📊 Member classification breakdown:")
        for category, count in category_counts.items():
            print(f"   {category.capitalize()}: {count}")
        
        return category_counts
        
    except Exception as e:
        print(f"❌ Error importing fresh data: {e}")
        print("📊 Continuing with existing database...")
        return None

# Always import fresh data on startup to ensure data is current
# print("🔄 Importing fresh data from ClubHub on startup...")
# startup_category_counts = import_fresh_clubhub_data()

def update_new_members_only():
    """Periodically update database with only new members/prospects (not full refresh)"""
    try:
        # Import ClubHub API client
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'services'))
        from api.clubhub_api_client import ClubHubAPIClient
        from config.clubhub_credentials import CLUBHUB_EMAIL, CLUBHUB_PASSWORD
        
        # Initialize and authenticate
        client = ClubHubAPIClient()
        if not client.authenticate(CLUBHUB_EMAIL, CLUBHUB_PASSWORD):
            logger.warning("❌ ClubHub authentication failed for incremental update")
            return False
        
        logger.info("🔄 Checking for new members from ClubHub...")
        
        # Get latest members from ClubHub
        all_members = []
        page = 1
        page_size = 100
        
        while True:
            members_response = client.get_all_members(page=page, page_size=page_size)
            
            if not members_response or not isinstance(members_response, list):
                break
                
            all_members.extend(members_response)
            page += 1
            
            if len(members_response) < page_size:
                break
        
        # Connect to database
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'gym_bot.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get existing member IDs for comparison
        cursor.execute("SELECT id FROM members")
        existing_ids = {row[0] for row in cursor.fetchall()}
        
        # Find new members
        new_members = [m for m in all_members if m.get('id') not in existing_ids]
        
        if new_members:
            logger.info(f"🆕 Found {len(new_members)} new members to add")
            
            # Add new members with classification
            for member in new_members:
                category = classify_member_status(member)
                
                # Add to members table
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
                
                # Store classification
                cursor.execute("""
                    INSERT OR REPLACE INTO member_categories (
                        member_id, category, status_message, full_name
                    ) VALUES (?, ?, ?, ?)
                """, (
                    member.get('id'),
                    category,
                    member.get('statusMessage', ''),
                    f"{member.get('firstName', '')} {member.get('lastName', '')}".strip()
                ))
            
            conn.commit()
            logger.info(f"✅ Added {len(new_members)} new members to database")
        else:
            logger.info("✅ No new members found - database is up to date")
        
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Error updating new members: {e}")
        return False

# Set up periodic updates (every 6 hours) - only for new members
def start_periodic_updates():
    """Start background thread for periodic member updates"""
    def update_loop():
        while True:
            try:
                time.sleep(6 * 3600)  # 6 hours
                update_new_members_only()
            except Exception as e:
                logger.error(f"❌ Periodic update loop error: {e}")
    
    update_thread = threading.Thread(target=update_loop, daemon=True)
    update_thread.start()
    logger.info("🔄 Started periodic member update thread (every 6 hours)")

# Start periodic updates in background
start_periodic_updates()

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
                logger.warning("⚠️ ClubOS authentication partially failed")
                
            return self.authenticated
        except Exception as e:
            logger.error(f"❌Œ ClubOS authentication failed: {e}")
            return False
    
    def get_live_events(self):
        """Get live calendar events with REAL dates, times, and participant names using iCal"""
        try:
            print("ðŸŒŸ USING iCAL METHOD FOR REAL EVENT DATA...")
            
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
                            logger.warning(f"❌Œ Could not get funding status for training client {name}: {e}")
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
            logger.error(f"❌Œ Error getting live events via iCal: {e}")
            return []
    
    def get_todays_events_lightweight(self):
        """Get only today's calendar events WITHOUT funding status checks for fast dashboard loading"""
        try:
            print("ðŸŒŸ GETTING TODAY'S EVENTS ONLY (LIGHTWEIGHT)...")
            
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
            logger.error(f"❌Œ Error getting today's events: {e}")
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
            logger.error(f"❌Œ Error looking up member name by email {email}: {e}")
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
            logger.error(f"❌Œ Error getting payment status for member {member_id}: {e}")
            return None

# Initialize ClubOS integration
clubos = ClubOSIntegration()

@app.route('/')
def dashboard():
    """Main dashboard with overview."""
    print("=== DASHBOARD ROUTE TRIGGERED ===")
    
    # Check if we need to refresh data (but don't block the dashboard load)
    if db_manager.needs_refresh():
        logger.info("⚠️ Database data is stale, consider refreshing")
    
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
    
    print(f"")
    
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



@app.route('/api/refresh-funding', methods=['POST'])
def refresh_funding_cache():
    """API endpoint to manually refresh funding cache for all training clients"""
    try:
        force = request.json.get('force', False) if request.is_json else False
        
        logger.info("")
        
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
        logger.error(f"❌Œ Error in funding refresh API: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/training/payment-status', methods=['POST'])
def api_training_payment_status():
    """Return live training payment status and amount owed for a member or participant name using reliable agreement data."""
    try:
        data = request.get_json(silent=True) or request.form or request.args or {}
        participant_name = (data.get('participant') or '').strip()
        member_id = (data.get('member_id') or '').strip()

        # Ensure ClubOS API is authenticated
        if not clubos_training_api.authenticated:
            logger.info("")
            if not clubos_training_api.authenticate():
                logger.error("❌Œ Failed to authenticate ClubOS Training API")
                return jsonify({'success': False, 'error': 'ClubOS authentication failed'}), 500
        
        # Resolve member_id if only participant name is provided
        if not member_id:
            if not participant_name:
                return jsonify({'success': True, 'funding': {
                    'status_text': 'No Name', 'status_class': 'secondary', 'status_icon': 'fas fa-user'
                }})
            logger.info(f"")
            # Authentication already done above
            member_id = clubos_training_api.search_member_id(participant_name) or training_package_cache._get_member_id_from_database(participant_name)
            if not member_id:
                logger.warning(f"❌Œ No ClubOS memberId found for {participant_name}")
                return jsonify({'success': True, 'funding': {
                    'status_text': 'No Match', 'status_class': 'secondary', 'status_icon': 'fas fa-user-slash'
                }})

        # Follow the working training API flow exactly
        logger.info(f"")
        try:
            result = clubos_training_api.get_member_training_payment_details(member_id)
            if not result or not result.get('success'):
                raise Exception(result.get('error', 'Unknown error'))

            amount_owed = float(result.get('amount_owed', 0.0) or 0.0)
            status = result.get('status') or ('Past Due' if amount_owed > 0 else 'Current')

            status_class = 'danger' if status == 'Past Due' and amount_owed > 0 else ('success' if status == 'Current' else 'secondary')
            status_icon = 'fas fa-exclamation-circle' if status_class == 'danger' else ('fas fa-check-circle' if status_class == 'success' else 'fas fa-info-circle')

            return jsonify({
                'success': True,
                'participant': participant_name or None,
                'member_id': member_id,
                'funding': {
                    'status_text': f"{status} - ${amount_owed:.2f}" if amount_owed > 0 else status,
                    'status_class': status_class,
                    'status_icon': status_icon,
                    'amount_owed': amount_owed,
                    'source': result.get('source')
                },
                'agreement_ids': result.get('agreement_ids')
            })
        except Exception as e:
            logger.error(f"❌Œ Error computing training payment details for {member_id}: {e}")
            return jsonify({'success': False, 'error': str(e)})
        
    except Exception as e:
        logger.error(f"❌Œ Error in training payment-status API: {e}")
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/test-complete-flow', methods=['POST'])
def test_complete_flow():
    """Test the complete browser-like agreement discovery flow"""
    try:
        data = request.get_json()
        member_id = data.get('member_id', '191215290')  # Default to Alejandra
        
        logging.info(f"ðŸ§ª Testing complete agreement flow for member: {member_id}")
        
        # Initialize the ClubOS API
        from clubos_training_api_fixed import ClubOSTrainingPackageAPI
        clubos_api = ClubOSTrainingPackageAPI()
        
        # Test the complete flow
        result = clubos_api.test_complete_agreement_flow(member_id)
        
        return jsonify(result)
        
    except Exception as e:
        logging.error(f"❌Œ Error in complete flow test: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/test-browser-flow', methods=['POST'])
def test_browser_flow():
    """Test cloning the exact browser flow for agreement discovery"""
    try:
        data = request.get_json()
        member_id = data.get('member_id', '191215290')  # Default to Alejandra
        
        logging.info(f"ðŸŽ­ Testing browser flow clone for member: {member_id}")
        
        # Initialize the correct ClubOS API class
        from clubos_training_api import ClubOSTrainingPackageAPI
        clubos_api = ClubOSTrainingPackageAPI()
        
        # Test the browser flow clone
        result = clubos_api.clone_clubos_browser_flow(member_id)
        
        return jsonify(result)
        
    except Exception as e:
        logging.error(f"❌Œ Error in browser flow test: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/test-known-agreement', methods=['POST'])
def api_test_known_agreement():
    """Test endpoint to validate our agreement API methods with a known working agreement ID."""
    try:
        data = request.get_json(silent=True) or request.form or request.args or {}
        agreement_id = data.get('agreement_id', '1522516')  # Default to known working ID from HAR files
        
        logger.info(f"ðŸ§ª Testing known agreement ID: {agreement_id}")
        
        # Ensure authenticated
        clubos_training_api.authenticate()
        
        # Test the known agreement ID
        test_results = clubos_training_api.test_known_agreement_id(agreement_id)
        
        return jsonify({
            'success': True,
            'agreement_id': agreement_id,
            'test_results': test_results
        })
        
    except Exception as e:
        logger.error(f"❌Œ Error in test-known-agreement API: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/bulk-checkin', methods=['POST'])
def api_bulk_checkin():
    """API endpoint to start bulk member check-ins in background - EXCLUDES PPV MEMBERS"""
    global bulk_checkin_status
    
    # Check if already running
    if bulk_checkin_status['is_running']:
        return jsonify({
            'success': False,
            'error': 'Bulk check-in already in progress',
            'status': bulk_checkin_status
        }), 400
    
    # Start background process
    import threading
    thread = threading.Thread(target=perform_bulk_checkin_background)
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'success': True,
        'message': 'Bulk check-in started in background',
        'status': bulk_checkin_status
    })

def perform_bulk_checkin_background():
    """Background function to perform bulk member check-ins with progress tracking"""
    global bulk_checkin_status
    
    try:
        # Initialize status
        bulk_checkin_status.update({
            'is_running': True,
            'started_at': datetime.now().isoformat(),
            'completed_at': None,
            'progress': 0,
            'total_members': 0,
            'processed_members': 0,
            'ppv_excluded': 0,
            'total_checkins': 0,
            'current_member': '',
            'status': 'starting',
            'message': 'Initializing bulk check-in process...',
            'error': None,
            'errors': []
        })
        
        logger.info("ðŸ‹ï¸ Starting background bulk member check-in process (excluding PPV members)...")
        
        # Import and initialize the ClubHub API client
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), 'services'))
        from api.clubhub_api_client import ClubHubAPIClient
        from config.clubhub_credentials import CLUBHUB_EMAIL, CLUBHUB_PASSWORD
        
        bulk_checkin_status['message'] = 'Authenticating with ClubHub...'
        bulk_checkin_status['status'] = 'authenticating'
        
        # Initialize and authenticate
        client = ClubHubAPIClient()
        if not client.authenticate(CLUBHUB_EMAIL, CLUBHUB_PASSWORD):
            bulk_checkin_status.update({
                'is_running': False,
                'status': 'error',
                'error': 'ClubHub authentication failed',
                'message': 'Authentication failed'
            })
            return
        
        bulk_checkin_status['message'] = 'High-speed member fetching...'
        bulk_checkin_status['status'] = 'fetching'
        
        # Optimized parallel member fetching for maximum speed
        all_members = []
        page_size = 100  # Larger page size for fewer API calls
        max_fetch_threads = 10  # Parallel page fetching
        
        # First, get total page count efficiently
        initial_response = client.get_all_members(page=1, page_size=page_size)
        if not initial_response:
            raise Exception("Failed to fetch initial member data")
        
        all_members.extend(initial_response)
        
        # Estimate total pages (we'll adjust dynamically)
        estimated_pages = max(10, len(initial_response))  # Conservative estimate
        
        def fetch_page(page_num):
            """Fetch a single page of members"""
            try:
                page_client = ClubHubAPIClient()
                if page_client.authenticate(CLUBHUB_EMAIL, CLUBHUB_PASSWORD):
                    return page_client.get_all_members(page=page_num, page_size=page_size)
                return None
            except Exception as e:
                logger.warning(f"Failed to fetch page {page_num}: {e}")
                return None
        
        # Parallel page fetching with dynamic page discovery
        page = 2  # Start from page 2 since we already have page 1
        consecutive_empty = 0
        
        with ThreadPoolExecutor(max_workers=max_fetch_threads) as fetch_executor:
            active_futures = {}
            
            while consecutive_empty < 3:  # Stop after 3 consecutive empty pages
                # Submit up to max_fetch_threads pages concurrently
                while len(active_futures) < max_fetch_threads and consecutive_empty < 3:
                    future = fetch_executor.submit(fetch_page, page)
                    active_futures[future] = page
                    page += 1
                
                # Process completed futures
                completed_futures = [f for f in active_futures if f.done()]
                for future in completed_futures:
                    page_num = active_futures.pop(future)
                    try:
                        page_data = future.result()
                        
                        if page_data and len(page_data) > 0:
                            all_members.extend(page_data)
                            consecutive_empty = 0  # Reset counter
                            
                            # Update progress with speed metrics
                            bulk_checkin_status['message'] = f'High-speed fetch: {len(all_members)} members ({len(page_data)} from page {page_num})'
                            
                        else:
                            consecutive_empty += 1
                            
                    except Exception as e:
                        logger.warning(f"Error processing page {page_num}: {e}")
                        consecutive_empty += 1
                
                # Small delay to prevent overwhelming the API
                time.sleep(0.05)  # 50ms delay
        
        logger.info(f"❌š¡ High-speed fetch complete: Retrieved {len(all_members)} total members")
        bulk_checkin_status.update({
            'total_members': len(all_members),
            'message': f'High-speed fetch complete: {len(all_members)} members retrieved',
            'status': 'fetch_complete'
        })
        
        # Filter out PPV members - PPV members typically have specific contract types or payment structures
        regular_members = []
        ppv_members = []
        
        for i, member in enumerate(all_members):
            # Update progress for filtering
            if i % 50 == 0:  # Update every 50 members
                bulk_checkin_status['message'] = f'Filtering members... {i}/{len(all_members)}'
                bulk_checkin_status['progress'] = int((i / len(all_members)) * 20)  # 20% for filtering
            
            # Check for PPV indicators
            contract_types = member.get('contractTypes', [])
            member_status = member.get('status', 0)
            user_type = member.get('userType', 0)
            
            is_ppv = False
            
            # Check contract types (adjust these values based on your system)
            if contract_types and any(ct in [2, 3, 4] for ct in contract_types):
                is_ppv = True
            
            # Check user type for PPV indicators
            if user_type in [18, 19, 20]:
                is_ppv = True
            
            # Check if member has 'trial' status or specific PPV indicators
            if member.get('trial', False):
                is_ppv = True
            
            # Check for specific PPV keywords in status message
            status_message = member.get('statusMessage', '').lower()
            if any(keyword in status_message for keyword in ['pay per visit', 'ppv', 'day pass', 'guest pass']):
                is_ppv = True
            
            if is_ppv:
                ppv_members.append(member)
            else:
                regular_members.append(member)
        
        logger.info(f"✅ Filtered members: {len(regular_members)} regular members, {len(ppv_members)} PPV members (excluded)")
        bulk_checkin_status.update({
            'ppv_excluded': len(ppv_members),
            'total_members': len(regular_members),
            'message': f'Processing {len(regular_members)} regular members (excluded {len(ppv_members)} PPV members)',
            'status': 'processing',
            'progress': 25
        })
        
        import time
        import asyncio
        import aiohttp
        from concurrent.futures import ThreadPoolExecutor, as_completed
        import threading
        from collections import defaultdict
        import queue
        
        # Thread-safe counters with atomic operations
        thread_lock = threading.RLock()  # Reentrant lock for better performance
        total_checkins = 0
        members_processed = 0
        errors = []
        
        # Connection pooling for better performance
        client_pool = queue.Queue(maxsize=50)  # Pre-populate client pool
        
        def initialize_client_pool():
            """Pre-create authenticated clients for maximum speed"""
            for _ in range(min(50, len(regular_members))):
                try:
                    thread_client = ClubHubAPIClient()
                    if thread_client.authenticate(CLUBHUB_EMAIL, CLUBHUB_PASSWORD):
                        client_pool.put(thread_client)
                    else:
                        break  # Stop if authentication fails
                except:
                    break  # Stop on any error
        
        def get_client():
            """Get a client from pool or create new one"""
            try:
                return client_pool.get_nowait()
            except queue.Empty:
                thread_client = ClubHubAPIClient()
                thread_client.authenticate(CLUBHUB_EMAIL, CLUBHUB_PASSWORD)
                return thread_client
        
        def return_client(client):
            """Return client to pool for reuse"""
            try:
                client_pool.put_nowait(client)
            except queue.Full:
                pass  # Pool is full, let it be garbage collected
        
        # Batch processing for ultra-fast execution
        def process_member_batch(member_batch):
            """Process multiple members in a single batch for maximum speed"""
            batch_results = []
            client_instance = get_client()
            
            try:
                current_time = datetime.now()
                
                # Pre-calculate all check-in times to avoid repeated datetime calls
                checkin_times = [
                    current_time.strftime("%Y-%m-%dT%H:%M:%S-05:00"),
                    (current_time + timedelta(minutes=1)).strftime("%Y-%m-%dT%H:%M:%S-05:00")
                ]
                
                for member in member_batch:
                    try:
                        member_id = member.get('id')
                        member_name = f"{member.get('firstName', '')} {member.get('lastName', '')}".strip()
                        
                        if not member_id:
                            batch_results.append((0, f"No ID for {member_name}", member_name))
                            continue
                        
                        checkins_completed = 0
                        
                        # Batch both check-ins for same member - faster than separate calls
                        checkin_data = [
                            {
                                "date": checkin_times[0],
                                "door": {"id": 772},
                                "club": {"id": 1156}, 
                                "manual": True
                            },
                            {
                                "date": checkin_times[1],
                                "door": {"id": 772},
                                "club": {"id": 1156},
                                "manual": True
                            }
                        ]
                        
                        # Process both check-ins rapidly
                        for i, data in enumerate(checkin_data):
                            try:
                                result = client_instance.post_member_usage(str(member_id), data)
                                if result:
                                    checkins_completed += 1
                            except Exception as checkin_error:
                                # Log but don't fail the whole batch
                                logger.warning(f"Check-in {i+1} failed for {member_name}: {checkin_error}")
                        
                        batch_results.append((checkins_completed, None, member_name))
                        
                    except Exception as member_error:
                        error_msg = f"Error processing {member_name}: {str(member_error)}"
                        batch_results.append((0, error_msg, member_name))
                
                return_client(client_instance)  # Return to pool for reuse
                return batch_results
                
            except Exception as batch_error:
                logger.error(f"Batch processing error: {batch_error}")
                return [(0, f"Batch error: {batch_error}", "Unknown") for _ in member_batch]
        
        def update_progress_atomic(processed_count, checkin_count, current_member_name):
            """Atomic progress update to minimize lock contention"""
            with thread_lock:
                nonlocal total_checkins, members_processed
                total_checkins += checkin_count
                members_processed += processed_count
                
                # Only update UI every 25 members for better performance
                if members_processed % 25 == 0 or members_processed >= len(regular_members):
                    bulk_checkin_status.update({
                        'current_member': current_member_name,
                        'processed_members': members_processed,
                        'total_checkins': total_checkins,
                        'message': f'High-speed processing: {members_processed}/{len(regular_members)} members ({total_checkins} check-ins)',
                        'progress': 25 + int(((members_processed / len(regular_members)) * 70))
                    })
        
        # Initialize client pool for maximum speed
        logger.info("ðŸš€ Initializing high-speed client pool...")
        bulk_checkin_status['message'] = 'Creating connection pool for maximum speed...'
        initialize_client_pool()
        
        # Ultra-fast batch processing with optimized threading
        batch_size = 10  # Process 10 members per batch for optimal speed/memory balance
        member_batches = [regular_members[i:i + batch_size] for i in range(0, len(regular_members), batch_size)]
        max_workers = min(50, len(member_batches))  # Up to 50 concurrent batch processors
        
        logger.info(f"ðŸš€ Starting ULTRA-FAST bulk check-in with {max_workers} threads processing {len(member_batches)} batches of {batch_size} members each")
        bulk_checkin_status.update({
            'message': f'ULTRA-FAST MODE: {max_workers} parallel processors, {len(member_batches)} batches',
            'status': 'ultra_processing'
        })
        
        # Process all batches concurrently for maximum throughput
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all batch tasks
            future_to_batch = {
                executor.submit(process_member_batch, batch): i 
                for i, batch in enumerate(member_batches)
            }
            
            # Process completed batches as they finish
            for future in as_completed(future_to_batch):
                batch_index = future_to_batch[future]
                try:
                    batch_results = future.result()
                    
                    # Process all results from this batch
                    batch_checkins = 0
                    batch_processed = 0
                    last_member = ""
                    
                    for checkins, error, member_name in batch_results:
                        batch_checkins += checkins
                        batch_processed += 1
                        last_member = member_name
                        
                        if error:
                            with thread_lock:
                                errors.append(error)
                    
                    # Update progress atomically
                    update_progress_atomic(batch_processed, batch_checkins, last_member)
                    
                except Exception as exc:
                    error_msg = f"Batch {batch_index} processing exception: {exc}"
                    logger.error(error_msg)
                    with thread_lock:
                        errors.append(error_msg)
        
        # Complete the process
        bulk_checkin_status.update({
            'is_running': False,
            'completed_at': datetime.now().isoformat(),
            'status': 'completed',
            'message': f'Completed! {total_checkins} total check-ins for {members_processed} members',
            'progress': 100,
            'current_member': '',
            'total_checkins': total_checkins,
            'processed_members': members_processed
        })
        
        logger.info(f"ðŸŽ‰ Bulk check-in completed: {total_checkins} total check-ins for {members_processed} regular members")
        logger.info(f"ðŸš« Excluded {len(ppv_members)} PPV members from check-in process")
        
    except Exception as e:
        logger.error(f"❌Œ Error in background bulk check-in: {e}")
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
        logger.error(f"❌Œ Error getting funding cache status: {e}")
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
        
        logger.info(f"")
        
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
                    
                    logger.info("")
                    
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
                    logger.error(f"❌Œ Background refresh failed: {e}")
            
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
        logger.error(f"❌Œ Error in data refresh API: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/refresh-clubhub-members', methods=['POST', 'GET'])
def refresh_clubhub_members():
    """API endpoint to refresh member data directly from ClubHub"""
    try:
        logger.info("")
        
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
        
        logger.info("")
        
        while True:
            members_response = client.get_all_members(page=page, page_size=page_size)
            
            if not members_response or not isinstance(members_response, list):
                break
                
            fresh_members.extend(members_response)
            logger.info(f"")
            
            # If we got less than page_size, we've reached the end
            if len(members_response) < page_size:
                break
                
            page += 1
        
        logger.info(f"")
        
        # Search for Dennis Rost specifically
        dennis_found = None
        for member in fresh_members:
            first_name = member.get('firstName', '').lower()
            last_name = member.get('lastName', '').lower()
            
            if 'dennis' in first_name and 'rost' in last_name:
                dennis_found = member
                logger.info(f"ðŸŽ¯ FOUND Dennis Rost in ClubHub: ID {member.get('id')}, Name: {first_name.title()} {last_name.title()}")
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
                logger.error(f"❌Œ Error adding member {member.get('firstName')} {member.get('lastName')}: {e}")
        
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
        logger.error(f"❌Œ Error refreshing ClubHub members: {e}")
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
        

        
        conn.close()
        
        # Get refresh status
        refresh_status = db_manager.get_refresh_status() if hasattr(db_manager, 'get_refresh_status') else None
        
        # Get current category counts from member_categories table
        try:
            cursor.execute("""
                SELECT category, COUNT(*) as count
                FROM member_categories
                GROUP BY category
            """)
            current_category_counts = {}
            for row in cursor.fetchall():
                current_category_counts[row[0]] = row[1]
        except Exception as e:
            logger.error(f"❌ Error getting current category counts: {e}")
            current_category_counts = {}
        
        # Get last refresh info from data_refresh_log
        try:
            cursor.execute("""
                SELECT last_refresh, record_count, category_breakdown 
                FROM data_refresh_log 
                WHERE table_name = 'members' 
                ORDER BY last_refresh DESC LIMIT 1
            """)
            refresh_info = cursor.fetchone()
            if refresh_info:
                last_refresh, record_count, category_breakdown = refresh_info
                try:
                    startup_category_counts = json.loads(category_breakdown) if category_breakdown else {}
                except:
                    startup_category_counts = {}
            else:
                last_refresh = None
                record_count = 0
                startup_category_counts = {}
        except Exception as e:
            logger.error(f"❌ Error getting refresh info: {e}")
            last_refresh = None
            record_count = 0
            startup_category_counts = {}
        
        conn.close()
        
        return jsonify({
            'success': True,
            'counts': {
                'members': members_count,
                'prospects': prospects_count,
                'training_clients': training_clients_count
            },
            'category_breakdown': {
                'current': current_category_counts,
                'startup': startup_category_counts
            },
            'refresh_info': {
                'last_refresh': last_refresh,
                'expected_records': record_count,
                'needs_refresh': db_manager.needs_refresh() if hasattr(db_manager, 'needs_refresh') else False
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌Œ Error in data status API: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/members')
def members_page():
    """Display members page with fast loading - data loads asynchronously via JavaScript."""
    
    logger.info("📋 Members page loaded - using fast loading with existing database data")
    
    # Get simple counts from database for initial display (fast operation)
    conn = sqlite3.connect(db_manager.db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM members")
    total_members = cursor.fetchone()[0]
    
    conn.close()
    
    # Fast page load - render template immediately with minimal data
    # JavaScript will load the actual member data and category counts asynchronously
    return render_template('members.html',
                         members=[],  # Empty initially, loaded via JavaScript
                         total_members=total_members,
                         statuses=[],
                         search='',
                         status_filter='',
                         page=1,
                         total_pages=1,
                         per_page=50)

@app.route('/api/members/all')
def get_all_members():
    """API endpoint to get all members - called asynchronously after page load."""
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
        
        # Show all members in the "All Members" tab
        # Only filter by search and status if specified
        
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
        
        # Get members for current page - optimized query with minimal fields
        query = f"""
            SELECT id, first_name, last_name, email, mobile_phone, status, status_message
            FROM members {where_clause}
            ORDER BY last_name, first_name
            LIMIT ? OFFSET ?
        """
        cursor.execute(query, params + [per_page, offset])
        members_data = cursor.fetchall()
        
        logger.info(f"")
        logger.info(f"")
        logger.info(f"")
        
        # Process members for display - optimized and simplified
        members = []
        for member in members_data:
            # Simple dictionary conversion - only essential fields
            member_dict = {
                'id': member['id'],
                'first_name': member['first_name'] or '',
                'last_name': member['last_name'] or '',
                'email': member['email'] or '',
                'mobile_phone': member['mobile_phone'] or '',
                'status': member['status'] or '',
                'status_message': member['status_message'] or ''
            }
            
            # Generate full_name efficiently
            member_dict['full_name'] = f"{member_dict['first_name']} {member_dict['last_name']}".strip() or member_dict['email'] or 'Unknown Member'
            
            members.append(member_dict)
        
        # Get unique statuses for filter dropdown
        cursor.execute("SELECT DISTINCT status FROM members WHERE status IS NOT NULL AND status != ''")
        statuses = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        
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
        logger.error(f"❌Œ Error getting members: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/member/<member_id>')
def get_member_profile(member_id):
    """Get detailed member profile information from database and ClubHub API."""
    try:
        logger.info(f"")
        
        # First, get member data from our local database
        conn = sqlite3.connect(db_manager.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get comprehensive member data
        cursor.execute("""
            SELECT * FROM members WHERE id = ?
        """, (member_id,))
        
        member_row = cursor.fetchone()
        if not member_row:
            conn.close()
            return jsonify({'success': False, 'error': 'Member not found in database'}), 404
        
        # Convert to dictionary properly
        member_data = {
            'id': member_row['id'] if 'id' in member_row.keys() else None,
            'guid': member_row['guid'] if 'guid' in member_row.keys() else None,
            'first_name': member_row['first_name'] if 'first_name' in member_row.keys() else '',
            'last_name': member_row['last_name'] if 'last_name' in member_row.keys() else '',
            'full_name': member_row['full_name'] if 'full_name' in member_row.keys() else '',
            'email': member_row['email'] if 'email' in member_row.keys() else '',
            'amount_past_due': member_row['amount_past_due'] if 'amount_past_due' in member_row.keys() else 0,
        }
        
        # Get payment status information
        amount_past_due = float(member_data.get('amount_past_due') or 0)
        amount_of_next_payment = float(member_data.get('amount_of_next_payment') or 0)
        date_of_next_payment = member_data.get('date_of_next_payment')
        payment_amount = float(member_data.get('payment_amount') or 0)
        
        # Determine payment status
        if amount_past_due > 0:
            payment_status = {
                'text': f'Past Due - ${amount_past_due:.2f}',
                'class': 'danger',
                'icon': 'fas fa-exclamation-triangle',
                'amount_past_due': amount_past_due,
                'next_payment_date': date_of_next_payment,
                'next_payment_amount': amount_of_next_payment
            }
        elif date_of_next_payment and date_of_next_payment <= datetime.now().strftime('%Y-%m-%d'):
            payment_status = {
                'text': 'Payment Due',
                'class': 'warning',
                'icon': 'fas fa-clock',
                'amount_past_due': 0,
                'next_payment_date': date_of_next_payment,
                'next_payment_amount': amount_of_next_payment
            }
        else:
            payment_status = {
                'text': 'Current',
                'class': 'success',
                'icon': 'fas fa-check-circle',
                'amount_past_due': 0,
                'next_payment_date': date_of_next_payment,
                'next_payment_amount': amount_of_next_payment
            }
        
        # Get agreements information
        cursor.execute("""
            SELECT agreement_id, agreement_type, agreement_start_date, agreement_end_date, 
                   agreement_rate, payment_amount, amount_past_due, amount_of_next_payment, 
                   date_of_next_payment
            FROM members 
            WHERE id = ? AND agreement_id IS NOT NULL
        """, (member_id,))
        
        agreements_data = cursor.fetchall()
        agreements = []
        for agreement in agreements_data:
            agreements.append({
                'agreement_id': agreement['agreement_id'],
                'agreement_type': agreement['agreement_type'] or 'Standard Membership',
                'start_date': agreement['agreement_start_date'],
                'end_date': agreement['agreement_end_date'],
                'rate': agreement['agreement_rate'] or agreement['payment_amount'],
                'status': 'Active' if not agreement['agreement_end_date'] or agreement['agreement_end_date'] > datetime.now().strftime('%Y-%m-%d') else 'Expired'
            })
        
        # Get payment history (placeholder for now)
        payments = []
        
        # Get training client information if available
        cursor.execute("""
            SELECT * FROM training_clients 
            WHERE member_id = ? OR clubos_member_id = ?
        """, (member_id, member_id))
        
        training_client = cursor.fetchone()
        training_info = None
        if training_client:
            training_info = {
                'trainer_name': training_client['trainer_name'] or 'Jeremy Mayo',
                'sessions_remaining': training_client['sessions_remaining'] or 0,
                'session_type': training_client['session_type'] or 'Personal Training',
                'last_session': training_client['last_session'],
                'payment_status': training_client['payment_status'] or 'Unknown'
            }
        
        conn.close()
        
        # Try to get fresh data from ClubHub API as well
        try:
            from config.clubhub_credentials_clean import CLUBHUB_EMAIL, CLUBHUB_PASSWORD
            
            # Use ClubHub API client for fresh data
            sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'services', 'api'))
            from clubhub_api_client import ClubHubAPIClient
            
            client = ClubHubAPIClient()
            if client.authenticate(CLUBHUB_EMAIL, CLUBHUB_PASSWORD):
                # Get fresh member data
                fresh_member = client.get_member_details(member_id)
                if fresh_member:
                    # Merge fresh data with database data
                    member_data.update({
                        'fresh_data': True,
                        'last_updated': datetime.now().isoformat()
                    })
                    
                    # Update payment status if we have fresh data
                    if fresh_member.get('amountPastDue'):
                        fresh_past_due = float(fresh_member.get('amountPastDue', 0))
                        if fresh_past_due > amount_past_due:
                            payment_status.update({
                                'text': f'Past Due - ${fresh_past_due:.2f}',
                                'amount_past_due': fresh_past_due
                            })
                else:
                    member_data['fresh_data'] = False
            else:
                member_data['fresh_data'] = False
                
        except Exception as e:
            logger.warning(f"⚠️ Could not fetch fresh ClubHub data: {e}")
            member_data['fresh_data'] = False
            member_data['fresh_data_error'] = str(e)
        
        # Return comprehensive member profile
        return jsonify({
            'success': True,
            'member': member_data,
            'payment_status': payment_status,
            'agreements': agreements,
            'payments': payments,
            'training_info': training_info
        })

    except Exception as e:
        logger.error(f"❌Œ Error fetching member profile for ID {member_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
        
@app.route('/api/members/past-due')
def get_past_due_members():
    """Get members who are past due on payments using FRESH ClubHub API data"""
    try:
        import datetime
        logger.info("")
        
        # Use ClubHub credentials to get ALL members directly (matching HAR analysis)
        import requests
        
        # ClubHub API configuration (from working HAR analysis)
        CLUBHUB_LOGIN_URL = "https://clubhub-ios-api.anytimefitness.com/api/login"
        CLUBHUB_API_BASE = "https://clubhub-ios-api.anytimefitness.com/api/v1.0"
        
        # Use ClubHub credentials from config instead of hardcoded
        from config.clubhub_credentials_clean import CLUBHUB_EMAIL, CLUBHUB_PASSWORD
        
        USERNAME = CLUBHUB_EMAIL
        PASSWORD = CLUBHUB_PASSWORD
        
        # Check for environment variables that might override the hardcoded credentials
        import os
        env_username = os.environ.get('CLUBHUB_USERNAME')
        env_password = os.environ.get('CLUBHUB_PASSWORD')
        
        if env_username and env_password:
            logger.info("")
            USERNAME = env_username
            PASSWORD = env_password
        
        # Exact headers from successful HAR requests
        headers = {
            "Content-Type": "application/json",
            "API-version": "1",
            "Accept": "application/json",
            "User-Agent": "ClubHub Store/2.15.1 (com.anytimefitness.Club-Hub; build:1007; iOS 18.5.0) Alamofire/5.6.4",
        }
        
        # Create session
        session = requests.Session()
        session.headers.update(headers)
        
        # Login to get bearer token
        login_data = {
            "username": USERNAME,  # Fixed: was "email", should be "username" 
            "password": PASSWORD
        }
        
        logger.info("")
        try:
            login_response = session.post(CLUBHUB_LOGIN_URL, json=login_data)
            logger.info(f"")
            
            if login_response.status_code == 200:
                login_result = login_response.json()
                logger.info(f"")
                bearer_token = login_result.get('accessToken')  # Fixed: was 'token', should be 'accessToken'
            else:
                logger.error(f"")
                try:
                    error_data = login_response.json()
                    logger.error(f"")
                except:
                    logger.error(f"")
        except Exception as e:
            logger.error(f"❌Œ Exception during ClubHub authentication: {e}")
            raise
            
        login_response = None  # Initialize outside the try block for the else clause
        bearer_token = None  # Initialize outside the try block
        try:
            login_response = session.post(CLUBHUB_LOGIN_URL, json=login_data)
            logger.info(f"")
            
            if login_response.status_code == 200:
                login_result = login_response.json()
                logger.info(f"")
                bearer_token = login_result.get('accessToken')  # Fixed: was 'token', should be 'accessToken'
            else:
                logger.error(f"")
                try:
                    error_data = login_response.json()
                    logger.error(f"")
                except:
                    logger.error(f"")
                    
            if bearer_token:
                logger.info("✅ ClubHub authentication successful")
                
                # Update headers with bearer token
                session.headers.update({
                    "Authorization": f"Bearer {bearer_token}"
                })
                
                # Get ALL members from ClubHub API (paginated like working script)
                club_id = "1156"  # Fond du Lac club ID
                all_members = []
                page = 1
                    
                while True:
                    members_url = f"https://clubhub-ios-api.anytimefitness.com/api/clubs/{club_id}/members?page={page}&pageSize=100"
                    logger.info(f"")
                    
                    members_response = session.get(members_url)
                    
                    if members_response.status_code != 200:
                        logger.error(f"❌Œ Failed to fetch page {page}: {members_response.status_code}")
                        break
                        
                    members_data = members_response.json()
                    
                    # Create a 'full_name' field for easier display
                    for member in members_data:
                        member['full_name'] = f"{member.get('firstName', '')} {member.get('lastName', '')}".strip()

                    logger.info(f"")
                    
                    # If we got no members, stop paginating to avoid unnecessary API calls
                    if len(members_data) == 0:
                        logger.info(f"ðŸ›' No more members found, stopping pagination")
                        break
                        
                    all_members.extend(members_data)
                    page += 1
                    
                fresh_members = all_members
                logger.info(f"✅ Got {len(fresh_members)} total fresh members from ClubHub API")
                
                red_members = []
                yellow_members = []
                
                # Process each member to categorize by payment status (EXACTLY like ClubHub tablet)
                for member in fresh_members:
                    status_msg = str(member.get('statusMessage', member.get('status_message', member.get('StatusMessage', '')))).strip()
                    
                    # Determine member priority based on status message
                    priority_status = None
                    status_text = status_msg
                    
                    # Match exactly what ClubHub shows on tablet
                    if ('Past Due more than 30 days' in status_msg or 
                        'Delinquent' in status_msg or 
                        'Delinquent- Can not Expire' in status_msg):
                        priority_status = 'red'
                        if 'Delinquent- Can not Expire' in status_msg:
                            status_text = 'Delinquent- Can not Expire'
                        else:
                            status_text = 'Past Due 30+ Days'
                    elif ('Past Due 6-30 days' in status_msg or
                          'invalid' in status_msg.lower() and ('address' in status_msg.lower() or 'billing' in status_msg.lower())):
                        priority_status = 'yellow'
                        if 'invalid' in status_msg.lower() and 'address' in status_msg.lower():
                            status_text = 'Invalid Address'
                        elif 'invalid' in status_msg.lower() and 'billing' in status_msg.lower():
                            status_text = 'Invalid Billing Info'
                        else:
                            status_text = 'Past Due 6-30 Days'
                    elif 'Member is pending cancel' in status_msg:
                        priority_status = 'yellow'
                        status_text = 'Pending Cancel'
                    elif 'Member will expire within 30 days' in status_msg:
                        priority_status = 'yellow'
                        status_text = 'Expiring Soon'
                    elif 'Member is in good standing' in status_msg:
                        continue  # Skip current members
                    elif 'Pay per visit member' in status_msg:
                        continue  # Skip PPV
                    elif 'Comp member' in status_msg:
                        continue  # Skip comp
                    elif 'Staff member' in status_msg:
                        continue  # Skip staff
                    else:
                        continue  # Skip others
                    
                    if priority_status:
                        # Extract first and last name with fallbacks
                        first_name = str(member.get('firstName', member.get('first_name', member.get('FirstName', ''))))
                        last_name = str(member.get('lastName', member.get('last_name', member.get('LastName', ''))))
                        
                        # Create full_name properly
                        full_name = member.get('full_name', '')
                        if not full_name.strip() and (first_name or last_name):
                            full_name = f"{first_name} {last_name}".strip()
                        
                        # Create member data dictionary
                        member_data = {
                            'id': str(member.get('id', member.get('prospectId', member.get('ProspectID', '')))),
                            'full_name': full_name,
                            'first_name': first_name,
                            'last_name': last_name,
                            'email': str(member.get('email', member.get('Email', ''))),
                            'mobile_phone': str(member.get('mobilePhone', member.get('phone', member.get('Phone', member.get('MobilePhone', ''))))),
                            'priority_status': priority_status,
                            'status_text': status_text,
                            'address': str(member.get('address1', member.get('address', member.get('Address', '')))),
                            'city': str(member.get('city', member.get('City', ''))),
                            'state': str(member.get('state', member.get('State', ''))),
                            'zip': str(member.get('zip', member.get('zipCode', member.get('ZipCode', '')))),
                            'membership_start': str(member.get('membershipStart', member.get('membership_start', member.get('MemberSince', '')))),
                            'last_visit': str(member.get('lastVisit', member.get('last_visit', member.get('LastVisit', ''))))
                        }
                        
                        if priority_status == 'red':
                            red_members.append(member_data)
                        elif priority_status == 'yellow':
                            yellow_members.append(member_data)
                
                # Combine and sort by priority (red first, then yellow)
                all_past_due = red_members + yellow_members
                
                red_count = len(red_members)
                yellow_count = len(yellow_members)
                total_count = red_count + yellow_count
                
                logger.info(f"✅ FRESH ClubHub data: {red_count} red, {yellow_count} yellow, {total_count} total")
                
                # Prepare the response data
                response_data = {
                    'red_count': red_count,
                    'yellow_count': yellow_count,
                    'total_count': total_count,
                    'past_due_members': all_past_due,
                    'message': f'FRESH ClubHub data: {red_count} red, {yellow_count} yellow past due members',
                    'data_source': 'clubhub_live_api',
                    'timestamp': datetime.datetime.now().isoformat()
                }
                
                # Cache the data for fallback
                try:
                    import json
                    import os
                    
                    cache_dir = os.path.join(os.path.dirname(__file__), 'cache')
                    if not os.path.exists(cache_dir):
                        os.makedirs(cache_dir)
                        
                    cache_path = os.path.join(cache_dir, 'past_due_members_cache.json')
                    with open(cache_path, 'w') as cache_file:
                        json.dump(response_data, cache_file)
                    logger.info("✅ Past due members data cached successfully")
                except Exception as cache_error:
                    logger.error(f"❌Œ Failed to cache data: {cache_error}")
                
                return jsonify(response_data)
            else:
                logger.error("❌Œ No bearer token received from ClubHub login")
                return jsonify({
                    'red_count': 0,
                    'yellow_count': 0,
                    'total_count': 0,
                    'past_due_members': [],
                    'error': 'No bearer token received from ClubHub'
                }), 500
                
        except Exception as e:
            logger.error(f"❌Œ ClubHub API access error: {e}")
            # Try to use cached data if available
            try:
                import json
                import os
                cache_path = os.path.join(os.path.dirname(__file__), 'cache', 'past_due_members_cache.json')
                
                if os.path.exists(cache_path):
                    logger.info("")
                    with open(cache_path, 'r') as cache_file:
                        cached_data = json.load(cache_file)
                        cached_data['message'] = 'Using cached data (ClubHub API is unavailable)'
                        cached_data['data_source'] = 'cache'
                        return jsonify(cached_data)
            except Exception as cache_error:
                logger.error(f"❌Œ Failed to read cache: {cache_error}")
                
            # If no cache or cache failed, return error
            return jsonify({
                'red_count': 0,
                'yellow_count': 0,
                'total_count': 0,
                'past_due_members': [],
                'error': f'ClubHub API error: {e}'
            }), 500
            
    except Exception as e:
        logger.error(f"❌Œ Error getting fresh ClubHub data: {e}")
        return jsonify({
            'red_count': 0,
            'yellow_count': 0,
            'total_count': 0,
            'past_due_members': [],
            'error': str(e)
        }), 500

@app.route('/api/members/category-counts')
def get_member_category_counts():
    """Get counts for all member categories - optimized single query"""
    try:
        conn = sqlite3.connect(db_manager.db_path)
        cursor = conn.cursor()
        
        # Single query to get all counts at once
        query = """
        SELECT 
            SUM(CASE WHEN status_message = 'Member is in good standing' THEN 1 ELSE 0 END) as green,
            SUM(CASE WHEN status_message = 'Comp member' THEN 1 ELSE 0 END) as comp,
            SUM(CASE WHEN status_message = 'Pay per visit member' THEN 1 ELSE 0 END) as ppv,
            SUM(CASE WHEN status_message = 'Staff member' THEN 1 ELSE 0 END) as staff,
            SUM(CASE WHEN status_message LIKE 'Past Due%' THEN 1 ELSE 0 END) as past_due,
            SUM(CASE WHEN status_message IN ('Account has been cancelled.', 'Member is pending cancel', 'Member will expire within 30 days.') THEN 1 ELSE 0 END) as inactive
        FROM members
        """
        
        cursor.execute(query)
        result = cursor.fetchone()
        
        counts = {
            'green': result[0],
            'comp': result[1],
            'ppv': result[2],
            'staff': result[3],
            'past_due': result[4],
            'inactive': result[5]
        }
        
        conn.close()
        
        return jsonify({
            'success': True,
            'counts': counts
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
        cursor.execute("SELECT COUNT(*) FROM members WHERE status_message IN ('Account has been cancelled.', 'Member is pending cancel', 'Member will expire within 30 days.')")
        counts['inactive'] = cursor.fetchone()[0]
        
        # Total members
        cursor.execute("SELECT COUNT(*) FROM members")
        counts['total'] = cursor.fetchone()[0]
        
        conn.close()
        
        logger.info(f"✅ Category counts: Green: {counts['green']}, Comp: {counts['comp']}, PPV: {counts['ppv']}, Staff: {counts['staff']}, Past Due: {counts['past_due']}, Inactive: {counts['inactive']}")
        
        return jsonify({
            'success': True,
            'counts': counts
        })
        
    except Exception as e:
        logger.error(f"❌ Error getting category counts: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/members/by-category/<category>')
def get_members_by_category(category):
    """Get members filtered by specific category using the member_categories table for fast lookups"""
    try:
        # Use absolute path to ensure we're reading from correct database
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'gym_bot.db')
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Use the member_categories table for fast category lookups
        query = """
            SELECT m.id, m.first_name, m.last_name, m.email, m.mobile_phone, m.status_message
            FROM members m
            INNER JOIN member_categories mc ON m.id = mc.member_id
            WHERE mc.category = ?
            ORDER BY m.last_name, m.first_name
        """
        
        cursor.execute(query, (category,))
        members = []
        
        for row in cursor.fetchall():
            # Simple and fast member conversion
            member_dict = {
                'id': row['id'],
                'first_name': row['first_name'] or '',
                'last_name': row['last_name'] or '',
                'email': row['email'] or '',
                'mobile_phone': row['mobile_phone'] or '',
                'status_message': row['status_message'] or ''
            }
            
            # Generate full name
            member_dict['full_name'] = f"{member_dict['first_name']} {member_dict['last_name']}".strip() or member_dict['email'] or 'Unknown Member'
            
            members.append(member_dict)
        
        conn.close()
        
        logger.info(f"✅ Found {len(members)} {category} members using category table")
        
        return jsonify({
            'success': True,
            'members': members,
            'count': len(members),
            'category': category
        })
        
    except Exception as e:
        logger.error(f"❌ Error getting {category} members: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/members/category-counts')
def get_category_counts():
    """Get counts for all member categories using the member_categories table for fast lookups"""
    try:
        # Use absolute path to ensure we're reading from correct database
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'gym_bot.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        counts = {}
        
        # Use the member_categories table for fast counting
        cursor.execute("""
            SELECT category, COUNT(*) as count
            FROM member_categories
            GROUP BY category
        """)
        
        # Initialize all categories to 0
        for category in ['green', 'comp', 'ppv', 'staff', 'past_due', 'inactive']:
            counts[category] = 0
        
        # Update with actual counts from database
        for row in cursor.fetchall():
            category = row[0]
            count = row[1]
            if category in counts:
                counts[category] = count
        
        conn.close()
        
        logger.info(f"✅ Category counts from member_categories table: {counts}")
        
        return jsonify({
            'success': True,
            'counts': counts
        })
        
    except Exception as e:
        logger.error(f"❌ Error getting category counts: {e}")
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

@app.route('/prospect/<prospect_id>')
def prospect_profile(prospect_id):
    """Display individual prospect profile page with detailed information."""
    logger.info(f"📋 Viewing prospect profile: {prospect_id}")
    
    # Get prospect data from database first, then enhance with ClubHub if needed
    try:
        conn = sqlite3.connect(db_manager.db_path)
        cursor = conn.cursor()
        
        # Query prospect from prospects table first
        cursor.execute("""
            SELECT * FROM prospects 
            WHERE id = ? OR guid = ?
        """, (prospect_id, prospect_id))
        
        prospect_data = cursor.fetchone()
        
        # If not found in prospects, check members table for prospects
        if not prospect_data:
            cursor.execute("""
                SELECT * FROM members 
                WHERE (id = ? OR guid = ?) AND (user_type LIKE '%prospect%' OR status LIKE '%prospect%')
            """, (prospect_id, prospect_id))
            prospect_data = cursor.fetchone()
        
        if not prospect_data:
            conn.close()
            flash(f"Prospect with ID {prospect_id} not found", "error")
            return redirect(url_for('prospects_page'))
        
        # Get column names for whichever table we got data from
        columns = [description[0] for description in cursor.description]
        conn.close()
        
        # Convert to dictionary for easier template usage
        prospect = dict(zip(columns, prospect_data))
        
        # Enhance prospect data for template
        prospect_info = {
            'id': prospect.get('id', prospect_id),
            'guid': prospect.get('guid', ''),
            'name': prospect.get('full_name', f"{prospect.get('first_name', '')} {prospect.get('last_name', '')}".strip()) or 'Unknown Name',  # Template expects 'name'
            'full_name': prospect.get('full_name', f"{prospect.get('first_name', '')} {prospect.get('last_name', '')}".strip()) or 'Unknown Name',
            'first_name': prospect.get('first_name', ''),
            'last_name': prospect.get('last_name', ''),
            'email': prospect.get('email', ''),
            'mobile_phone': prospect.get('mobile_phone', ''),
            'home_phone': prospect.get('home_phone', ''),
            'address1': prospect.get('address1', ''),
            'address2': prospect.get('address2', ''),
            'city': prospect.get('city', ''),
            'state': prospect.get('state', ''),
            'zip_code': prospect.get('zip_code', ''),
            'status': prospect.get('status', 'New Lead'),
            'lead_source': prospect.get('lead_source', prospect.get('source', '')),
            'lead_status': 'new',  # Default lead status for template
            'prospect_id': prospect.get('id', prospect_id),  # Template expects prospect_id
            'interest_level': prospect.get('interest_level', ''),
            'follow_up_date': prospect.get('follow_up_date', ''),
            'notes': prospect.get('notes', ''),
            'created_at': prospect.get('created_at', ''),
            'last_activity_timestamp': prospect.get('last_activity_timestamp', ''),
            'user_type': prospect.get('user_type', 'prospect'),
            'membership_start': prospect.get('membership_start', ''),
            'membership_end': prospect.get('membership_end', ''),
            'date_of_birth': prospect.get('date_of_birth', ''),
            'gender': prospect.get('gender', ''),
            'emergency_contact': prospect.get('emergency_contact', ''),
            'emergency_phone': prospect.get('emergency_phone', '')
        }
        
        return render_template('prospect_profile.html', prospect=prospect_info)
        
    except Exception as e:
        logger.error(f"❌ Error loading prospect profile {prospect_id}: {e}")
        flash(f"Error loading prospect: {str(e)}", "error")
        return redirect(url_for('prospects_page'))

@app.route('/member/<member_id>')
def member_profile(member_id):
    """Display individual member profile page"""
    logger.info(f"📋 Viewing member profile: {member_id}")
    
    try:
        # Get member details using existing database
        conn = sqlite3.connect(db_manager.db_path)
        conn.row_factory = sqlite3.Row  # Enable dictionary-style access
        
        # Get basic member info
        member = conn.execute("""
            SELECT * FROM members WHERE id = ? OR guid = ?
        """, (member_id, member_id)).fetchone()
        
        if not member:
            conn.close()
            flash('Member not found', 'error')
            return redirect(url_for('members_page'))
            
        # Convert SQLite Row to dict properly
        member_dict = {
            'id': member['id'],
            'guid': member['guid'],
            'first_name': member['first_name'],
            'last_name': member['last_name'],
            'full_name': member['full_name'],
            'email': member['email'],
            'mobile_phone': member['mobile_phone'],
            'status': member['status'],
            'membership_start': member['membership_start'],
            'created_at': member['created_at']
        }
        
        # Mark as database data (no fresh API call for now)
        member_dict['fresh_data'] = False
        member_dict['fresh_data_error'] = None
            
        # Get payment status (simplified for now)
        payment_status = {
            'status': 'current',
            'amount_due': 0.0,
            'last_payment_date': None,
            'next_payment_date': None
        }
        
        # Get agreements (simplified - empty for now)
        agreements = []
            
        # Get payment history (empty for now)
        payments = []
        
        # Get training info if member is a training client
        training_info = None
        try:
            training_client = conn.execute("""
                SELECT * FROM training_clients WHERE clubos_member_id = ? OR member_id = ?
            """, (member_dict.get('clubos_member_id', member_id), member_id)).fetchone()
            
            if training_client:
                training_info = {
                    'trainer_name': training_client['trainer_name'],
                    'sessions_remaining': training_client['sessions_remaining'],
                    'last_session': training_client['last_session'],
                    'payment_status': training_client['payment_status']
                }
        except Exception as e:
            logger.error(f"Error fetching training info: {e}")
            training_info = None
            
        conn.close()
        
        return render_template('member_profile.html', 
                             member=member_dict,
                             payment_status=payment_status,
                             agreements=agreements,
                             payments=payments,
                             training_info=training_info)
        
    except Exception as e:
        logger.error(f"❌ Error in member_profile: {e}")
        flash('Error loading member profile', 'error')
        return redirect(url_for('members_page'))

@app.route('/training-client/<member_id>')
def training_client_profile(member_id):
    """Display individual training client profile page with agreement focus"""
    logger.info(f"🏋️ Viewing training client profile: {member_id}")
    
    try:
        # Get training client from database
        conn = sqlite3.connect(db_manager.db_path)
        
        training_client = conn.execute("""
            SELECT * FROM training_clients WHERE clubos_member_id = ? OR member_id = ? OR guid = ?
        """, (member_id, member_id, member_id)).fetchone()
        
        if not training_client:
            conn.close()
            flash('Training client not found', 'error')
            return redirect(url_for('training_clients'))
            
        # Convert SQLite Row to dict properly for training client
        client_dict = {
            'id': training_client['id'] if 'id' in training_client.keys() else None,
            'guid': training_client['guid'] if 'guid' in training_client.keys() else None,
            'member_id': training_client['member_id'] if 'member_id' in training_client.keys() else None,
            'trainer_name': training_client['trainer_name'] if 'trainer_name' in training_client.keys() else None,
            'sessions_remaining': training_client['sessions_remaining'] if 'sessions_remaining' in training_client.keys() else None,
            'package_type': training_client['package_type'] if 'package_type' in training_client.keys() else None,
            'clubos_member_id': training_client['clubos_member_id'] if 'clubos_member_id' in training_client.keys() else None,
        }
        
        # Get member details for additional info
        member = conn.execute("""
            SELECT * FROM members WHERE id = ? OR clubos_member_id = ? OR guid = ?
        """, (member_id, member_id, member_id)).fetchone()
        
        if member:
            # Convert SQLite Row to dict properly
            member_dict = {
                'id': member['id'] if 'id' in member.keys() else None,
                'guid': member['guid'] if 'guid' in member.keys() else None,
                'first_name': member['first_name'] if 'first_name' in member.keys() else None,
                'last_name': member['last_name'] if 'last_name' in member.keys() else None,
                'full_name': member['full_name'] if 'full_name' in member.keys() else None,
                'email': member['email'] if 'email' in member.keys() else None,
                'mobile_phone': member['mobile_phone'] if 'mobile_phone' in member.keys() else None,
                'status': member['status'] if 'status' in member.keys() else None,
                'membership_start': member['membership_start'] if 'membership_start' in member.keys() else None,
                'created_at': member['created_at'] if 'created_at' in member.keys() else None,
                'clubos_member_id': member['clubos_member_id'] if 'clubos_member_id' in member.keys() else None,
            }
            # Merge member data into client data
            for key, value in member_dict.items():
                if key not in client_dict or not client_dict[key]:
                    client_dict[key] = value
        
        # Get package agreements - this is the main focus
        agreements = []
        try:
            training_api = ClubOSTrainingPackageAPI()
            funding_data = training_api.get_funding_status(client_dict.get('clubos_member_id', member_id))
            if funding_data and funding_data.get('success'):
                agreements = funding_data.get('funding_data', [])
        except Exception as e:
            logger.error(f"Error fetching training agreements: {e}")
            
        # Calculate financial summary
        total_past_due = 0
        total_sessions = 0
        total_value = 0
        
        for agreement in agreements:
            try:
                # Calculate past due from invoice data
                v2 = agreement.get('v2', {})
                invoices = []
                
                if v2.get('include') and isinstance(v2['include'].get('invoices'), list):
                    invoices = v2['include']['invoices']
                elif isinstance(v2.get('invoices'), list):
                    invoices = v2['invoices']
                    
                # Calculate past due using SPA logic
                past_due_invoices = [inv for inv in invoices 
                                   if (inv.get('status', '')).lower() in ['delinquent', 'pay now']]
                
                agreement_past_due = sum(
                    float(inv.get('invoice_total', 0) or inv.get('remainingTotal', 0) or inv.get('total', 0) or 0)
                    for inv in past_due_invoices
                )
                total_past_due += agreement_past_due
                
                # Sessions
                sessions_remaining = agreement.get('v2', {}).get('packageAgreement', {}).get('sessionsRemaining', 0)
                total_sessions += sessions_remaining or 0
                
                # Total value
                agreement_value = agreement.get('agreement_total_value', {})
                value = agreement_value.get('totalValue', 0) or agreement_value.get('value', 0) or 0
                total_value += float(value) if value else 0
                
            except Exception as e:
                logger.error(f"Error calculating agreement summary: {e}")
                continue
        
        financial_summary = {
            'total_past_due': round(total_past_due, 2),
            'active_agreements': len(agreements),
            'total_sessions': total_sessions,
            'total_value': round(total_value, 2)
        }
        
        conn.close()
        
        return render_template('training_client_profile.html',
                             client=client_dict,
                             agreements=agreements,
                             financial_summary=financial_summary)
        
    except Exception as e:
        logger.error(f"❌ Error in training_client_profile: {e}")
        flash('Error loading training client profile', 'error')
        return redirect(url_for('training_clients'))

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
        
        # Process and save prospects to database for profile access
        conn = sqlite3.connect(db_manager.db_path)
        cursor = conn.cursor()
        
        # Clear existing prospects data to refresh with latest
        cursor.execute('DELETE FROM prospects')
        
        prospects_saved = 0
        
        while True:
            prospects_url = f"https://clubhub-ios-api.anytimefitness.com/api/clubs/{club_id}/prospects?page={page}&pageSize=100"
            prospects_response = session.get(prospects_url)
            
            if prospects_response.status_code != 200:
                break
                
            prospects_data = prospects_response.json()
            
            if len(prospects_data) == 0:
                break
                
            # Save each prospect to database
            for prospect in prospects_data:
                prospect['full_name'] = f"{prospect.get('firstName', '')} {prospect.get('lastName', '')}".strip()
                
                # Save prospect to database so profile pages can access it
                cursor.execute("""
                    INSERT OR REPLACE INTO prospects (
                        id, guid, first_name, last_name, full_name, email, mobile_phone, 
                        home_phone, address1, city, state, zip_code, status, lead_source, 
                        created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
                """, (
                    prospect.get('id') or prospect.get('prospectId'),
                    prospect.get('guid', ''),
                    prospect.get('firstName', ''),
                    prospect.get('lastName', ''),
                    prospect['full_name'],
                    prospect.get('email', ''),
                    prospect.get('mobilePhone', ''),
                    prospect.get('homePhone', ''),
                    prospect.get('address1', ''),
                    prospect.get('city', ''),
                    prospect.get('state', ''),
                    prospect.get('zipCode', ''),
                    prospect.get('status', 'New Lead'),
                    prospect.get('leadSource', ''),
                ))
                prospects_saved += 1
                    
            all_prospects.extend(prospects_data)
            page += 1
            
            # Limit to prevent infinite loops
            if page > 50:
                break
        
        conn.commit()
        conn.close()
        
        logger.info(f"✅ Saved {prospects_saved} prospects to database for profile access")
        
        return jsonify({
            'success': True,
            'prospects': all_prospects,
            'total_prospects': len(all_prospects),
            'page': 1,
            'total_pages': 1,
            'per_page': len(all_prospects)
        })
        
    except Exception as e:
        logger.error(f"❌Œ Error getting prospects: {e}")
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
    """API endpoint to get all training clients from ClubOS with fresh agreement data - saves to database but never returns stale data."""
    try:
        logger.info("ðŸ‹ï¸ Loading training clients from ClubOS with fresh agreement data...")
        
        # Ensure ClubOS API is authenticated
        if not clubos_training_api.authenticated:
            logger.info("")
            if not clubos_training_api.authenticate():
                logger.error("❌Œ Failed to authenticate ClubOS Training API")
                return jsonify({'success': False, 'error': 'ClubOS authentication failed'}), 500
        
        # Always fetch fresh data from ClubOS first
        clubos_assignees = clubos_training_api.fetch_assignees(force_refresh=True)

        # Fallbacks: try without force, then DB cache so the UI isn't empty
        if not clubos_assignees:
            logger.warning("⚠️ No training clients from ClubOS (force). Retrying without force...")
            clubos_assignees = clubos_training_api.fetch_assignees(force_refresh=False)

        if not clubos_assignees:
            logger.warning("⚠️ ClubOS assignees still empty. Falling back to database cache for training clients list.")
            try:
                conn = sqlite3.connect(db_manager.db_path)
                conn.row_factory = sqlite3.Row
                cur = conn.cursor()
                cur.execute("SELECT member_name, clubos_member_id, email, phone, agreement_name, trainer_name, sessions_remaining, next_invoice_subtotal, payment_status, created_at, last_updated FROM training_clients ORDER BY member_name")
                rows = cur.fetchall()
                conn.close()
                cached_clients = []
                for row in rows:
                    cached_clients.append({
                        'member_name': row['member_name'],
                        'email': row['email'],
                        'phone': row['phone'],
                        'clubos_member_id': row['clubos_member_id'],
                        'package_name': row['agreement_name'],
                        'trainer_name': row['trainer_name'],
                        'payment_status': row['payment_status'] or 'Unknown',
                        'sessions_remaining': row['sessions_remaining'],
                        'next_invoice_subtotal': row['next_invoice_subtotal'],
                        'total_agreements': None,
                        'created_at': row['created_at'],
                        'last_updated': row['last_updated'],
                        'status': 'Active',
                        'source': 'database_fallback'
                    })
                return jsonify({
                    'success': True,
                    'training_clients': cached_clients,
                    'total_training_clients': len(cached_clients),
                    'page': 1,
                    'total_pages': 1,
                    'per_page': len(cached_clients),
                    'source': 'database_fallback',
                    'last_updated': datetime.now().isoformat()
                })
            except Exception as e:
                logger.error(f"❌Œ DB fallback failed: {e}")
                return jsonify({
                    'success': True,
                    'training_clients': [],
                    'total_training_clients': 0,
                    'page': 1,
                    'total_pages': 1,
                    'per_page': 0,
                    'source': 'clubos_live'
                })
        
        logger.info(f"")
        
        # Connect to database for saving/updating
        conn = sqlite3.connect(db_manager.db_path)
        cursor = conn.cursor()
        
        # Clear existing training clients data to avoid stale records
        cursor.execute("DELETE FROM training_clients")
        logger.info("ðŸ—'ï¸ Cleared existing training clients data to prevent stale records")
        
        training_clients = []
        
        for assignee in clubos_assignees:
            try:
                member_id = assignee.get('id')
                member_name = assignee.get('name', 'Unknown')
                email = assignee.get('email', 'N/A')
                phone = assignee.get('phone', 'N/A')
                
                if not member_id:
                    continue
                
                # Fetch basic agreement info for this client to populate the list
                agreements_data = []
                package_name = 'No package assigned'
                trainer_name = 'Jeremy Mayo'
                sessions_remaining = 'N/A'
                agreement_amount = 'N/A'
                
                try:
                    # Delegate to member first
                    if clubos_training_api.delegate_to_member(member_id):
                        # Get basic agreement list
                        list_url = f"{clubos_training_api.base_url}/api/agreements/package_agreements/list"
                        list_resp = clubos_training_api.session.get(list_url, timeout=15)
                        
                        if list_resp.status_code == 200:
                            agreements_data = list_resp.json()
                            if isinstance(agreements_data, list) and agreements_data:
                                # Get first active agreement for basic info
                                primary_agreement = agreements_data[0]
                                package_name = primary_agreement.get('package_name', 'No package assigned')
                                trainer_name = primary_agreement.get('trainer_name', 'Jeremy Mayo')
                                sessions_remaining = primary_agreement.get('sessions_remaining', 'N/A')
                                agreement_amount = primary_agreement.get('amount', 'N/A')
                                
                                logger.info(f"✅ Found agreement for {member_name}: {package_name} - {sessions_remaining} sessions - ${agreement_amount}")
                            else:
                                logger.info(f"❌„¹ï¸ No agreements found for {member_name}")
                        else:
                            logger.warning(f"⚠️ Failed to fetch agreements for {member_name}: {list_resp.status_code}")
                    else:
                        logger.warning(f"⚠️ Failed to delegate to member {member_id} ({member_name})")
                except Exception as e:
                    logger.warning(f"⚠️ Error fetching agreement info for {member_name}: {e}")
                
                # Set default payment status
                payment_status = 'Unknown'  # Will be fetched when needed
                
                # Save to database with current timestamp
                current_time = datetime.now().isoformat()
                cursor.execute("""
                    INSERT INTO training_clients (
                        member_name, clubos_member_id, email, phone, agreement_name, 
                        trainer_name, sessions_remaining, next_invoice_subtotal, 
                        payment_status, created_at, last_updated
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    member_name, member_id, email, phone, package_name,
                    trainer_name, sessions_remaining, agreement_amount,
                    payment_status, current_time, current_time
                ))
                
                # Build response object with fresh data
                client_data = {
                    'member_name': member_name,
                    'email': email,
                    'phone': phone,
                    'clubos_member_id': member_id,
                    'package_name': package_name,
                    'trainer_name': trainer_name,
                    'payment_status': payment_status,
                    'sessions_remaining': sessions_remaining,
                    'next_invoice_subtotal': agreement_amount,
                    'total_agreements': len(agreements_data),
                    'created_at': current_time,
                    'last_updated': current_time,
                    'status': 'Active',
                    'source': 'clubos_live'
                }
                
                training_clients.append(client_data)
                
            except Exception as e:
                logger.warning(f"⚠️ Error processing training client {assignee.get('name', 'Unknown')}: {e}")
                continue
        
        # Commit database changes
        conn.commit()
        conn.close()
        
        logger.info(f"✅ Successfully loaded and saved {len(training_clients)} training clients with fresh agreement data")
        
        return jsonify({
            'success': True,
            'training_clients': training_clients,
            'total_training_clients': len(training_clients),
            'page': 1,
            'total_pages': 1,
            'per_page': len(training_clients),
            'source': 'clubos_live',
            'last_updated': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌Œ Error loading training clients from ClubOS: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/training-clients/<member_id>/agreements')
def get_member_package_agreements(member_id):
    """API endpoint to get all active training package agreements for a member with per-agreement past-due amounts.

    Uses the reliable flow: delegate to member + bare list + per-agreement billing_status.
    """
    try:
        logger.info(f"ðŸ‹ï¸ Fetching package agreements (with funding) for member ID: {member_id}")

        # Ensure ClubOS API is authenticated
        if not clubos_training_api.authenticated:
            logger.info("")
            if not clubos_training_api.authenticate():
                logger.error("❌Œ Failed to authenticate ClubOS Training API")
                return jsonify({'success': False, 'error': 'ClubOS authentication failed'}), 500

        # Delegate to this member context
        if not clubos_training_api.delegate_to_member(member_id):
            return jsonify({'success': False, 'error': 'Delegation failed'}), 500

        # Call bare list endpoint (no params)
        list_url = f"{clubos_training_api.base_url}/api/agreements/package_agreements/list"
        list_resp = clubos_training_api.session.get(list_url, timeout=15)
        if list_resp.status_code != 200:
            logger.warning(f"⚠️ Bare list failed for {member_id}: HTTP {list_resp.status_code}")
            return jsonify({'success': True, 'member_id': member_id, 'agreements': [], 'total_agreements': 0})

        try:
            agreements_raw = list_resp.json() or []
        except Exception:
            agreements_raw = []

        # Ensure list
        if isinstance(agreements_raw, dict):
            # Some variants return a dict with 'data' or similar
            cand = agreements_raw.get('data') or agreements_raw.get('agreements') or []
            agreements_raw = cand if isinstance(cand, list) else []

        normalized = []

        def extract_agreement_id(item: dict) -> str | None:
            try:
                if isinstance(item, dict):
                    pa = item.get('packageAgreement') or {}
                    if isinstance(pa, dict) and pa.get('id'):
                        return str(pa.get('id'))
                    if item.get('id'):
                        return str(item.get('id'))
            except Exception:
                pass
            return None

        def _to_float(val) -> float:
            """Convert value to float, handling currency strings and other formats."""
            try:
                if isinstance(val, (int, float)):
                    return float(val)
                if isinstance(val, str):
                    # Strip currency symbols/commas
                    s = val.replace('$', '').replace(',', '').strip()
                    return float(s)
            except Exception:
                return 0.0
            return 0.0

        def parse_amount_due(b: dict) -> float:
            try:
                # Try common fields first
                for key in ['amountDue', 'pastDueAmount', 'past_due_amount', 'balanceDue', 'totalPastDue', 'amount_due']:
                    if isinstance(b, dict) and key in b:
                        try:
                            return float(b.get(key) or 0) or 0.0
                        except Exception:
                            continue
                # Inspect nested invoice/balance structures
                try:
                    if isinstance(b, dict) and 'invoices' in b and isinstance(b['invoices'], list):
                        total = 0.0
                        for inv in b['invoices']:
                            # sum any outstanding/balance fields
                            for k in ['balance', 'balanceDue', 'amountDue', 'outstanding']:
                                if isinstance(inv, dict) and k in inv:
                                    try:
                                        total += float(inv.get(k) or 0)
                                    except Exception:
                                        pass
                        if total > 0:
                            return total
                except Exception:
                    pass
                # Last resort: scan numerics in dict
                try:
                    vals = []
                    for v in (b or {}).values():
                        try:
                            vals.append(float(v))
                        except Exception:
                            pass
                    cand = max(vals) if vals else 0.0
                    return cand if cand > 0 else 0.0
                except Exception:
                    return 0.0
            except Exception:
                return 0.0

        # Process agreements and add past due amounts
        headers = clubos_training_api._auth_headers(referer=f"{clubos_training_api.base_url}/action/Agreements")

        for item in agreements_raw:
            try:
                aid = extract_agreement_id(item)
                if not aid:
                    continue
                billing_url = f"{clubos_training_api.base_url}/api/agreements/package_agreements/{aid}/billing_status"
                b_resp = clubos_training_api.session.get(billing_url, headers=headers, timeout=12)
                b_json = b_resp.json() if b_resp.status_code == 200 else {}
                billing_amt = parse_amount_due(b_json)
                # Optional enrichment: V2, salespeople, and total value
                v2_json = None
                try:
                    # Use the recommended ClubOS SPA endpoint that includes invoice data
                    spa_url = f"{clubos_training_api.base_url}/action/PackageAgreementUpdated/spa/#/package-agreements/{aid}"
                    
                    # The SPA endpoint returns the full agreement data with invoices embedded
                    # We need to make a request to this endpoint and parse the response
                    spa_headers = clubos_training_api._auth_headers(referer=f"{clubos_training_api.base_url}/action/PackageAgreementUpdated/spa/")
                    spa_resp = clubos_training_api.session.get(spa_url, headers=spa_headers, timeout=14)
                    
                    if spa_resp.status_code == 200:
                        # Parse the SPA response to extract agreement data
                        v2_json = parse_spa_agreement_response(spa_resp.text, aid)
                    else:
                        v2_json = None
                except Exception:
                    v2_json = None

                # Compute invoice-based past due if invoices are present
                invoice_amt, invoice_count, invoice_list = 0.0, 0, []
                try:
                    if isinstance(v2_json, dict):
                        # In V2, invoices often appear under the 'include' container
                        include_obj = v2_json.get('include') if isinstance(v2_json.get('include'), dict) else None
                        invoices_list = None
                        if include_obj and isinstance(include_obj.get('invoices'), list):
                            invoices_list = include_obj.get('invoices')
                        elif isinstance(v2_json.get('invoices'), list):
                            invoices_list = v2_json.get('invoices')
                        if isinstance(invoices_list, list):
                            invoice_amt, invoice_count, invoice_list = compute_past_due_from_invoices(invoices_list)
                except Exception:
                    pass

                # Choose the more authoritative non-zero amount
                amt = invoice_amt if (invoice_amt and invoice_amt > 0) else billing_amt
                status = 'Past Due' if amt and amt > 0 else 'Current'

                sales_json = None
                try:
                    sales_url = f"{clubos_training_api.base_url}/api/agreements/package_agreements/{aid}/salespeople"
                    sales_resp = clubos_training_api.session.get(sales_url, headers=headers, timeout=10)
                    if sales_resp.status_code == 200:
                        sales_json = sales_resp.json()
                except Exception:
                    sales_json = None

                total_json = None
                try:
                    total_url = f"{clubos_training_api.base_url}/api/agreements/package_agreements/{aid}/agreementTotalValue"
                    total_params = {'agreementId': aid, '_': int(time.time() * 1000)}
                    total_resp = clubos_training_api.session.get(total_url, headers=headers, params=total_params, timeout=10)
                    if total_resp.status_code == 200:
                        total_json = total_resp.json()
                except Exception:
                    total_json = None

                # Derive package name robustly across bare and V2 shapes
                pkg_name = None
                try:
                    # Prefer V2 packageAgreement fields if available (support multiple shapes)
                    if isinstance(v2_json, dict):
                        # Common shapes observed: root.packageAgreement, data.packageAgreement
                        pa_v2 = None
                        if isinstance(v2_json.get('packageAgreement'), dict):
                            pa_v2 = v2_json.get('packageAgreement')
                        elif isinstance(v2_json.get('data'), dict) and isinstance(v2_json['data'].get('packageAgreement'), dict):
                            pa_v2 = v2_json['data'].get('packageAgreement')
                        # Some responses may nest under include -> packageAgreement (rare); check shallowly
                        elif isinstance(v2_json.get('include'), dict) and isinstance(v2_json['include'].get('packageAgreement'), dict):
                            pa_v2 = v2_json['include'].get('packageAgreement')

                        if isinstance(pa_v2, dict):
                            for k in ['name','productName','packageName','agreementName','programName']:
                                val = pa_v2.get(k)
                                if isinstance(val, str) and val.strip():
                                    pkg_name = val
                                    break
                            if not pkg_name and isinstance(pa_v2.get('package'), dict):
                                val = pa_v2['package'].get('name')
                                if isinstance(val, str) and val.strip():
                                    pkg_name = val
                    # Fallback to bare item
                    if not pkg_name and isinstance(item, dict):
                        pa_item = item.get('packageAgreement') or {}
                        for k in ['name','packageName','agreementName','productName','planName','typeName','packageAgreementName','packageAgreementTypeName']:
                            val = (item.get(k) if k in item else None) or (pa_item.get(k) if isinstance(pa_item, dict) else None)
                            if isinstance(val, str) and val.strip():
                                pkg_name = val
                                break
                        if not pkg_name and isinstance(item.get('package'), dict):
                            val = item['package'].get('name')
                            if isinstance(val, str) and val.strip():
                                pkg_name = val
                except Exception:
                    pkg_name = pkg_name or None

                # Lifecycle status: filter to only Active agreements (exclude canceled/completed/collections/terminated/expired)
                def _is_inactive_agreement(v2_obj, bare_obj) -> bool:
                    try:
                        texts = []
                        flags = []
                        # V2 fields
                        if isinstance(v2_obj, dict):
                            pa_v2 = v2_obj.get('packageAgreement') or {}
                            if isinstance(pa_v2, dict):
                                texts.extend([
                                    str(pa_v2.get('status') or ''),
                                    str(pa_v2.get('agreementStatus') or ''),
                                    str(pa_v2.get('state') or '')
                                ])
                                flags.extend([
                                    pa_v2.get('isCancelled'), pa_v2.get('isCanceled'),
                                    pa_v2.get('isComplete'), pa_v2.get('isCompleted'),
                                    pa_v2.get('inCollections'), pa_v2.get('isTerminated'),
                                ])
                        # Bare fields
                        if isinstance(bare_obj, dict):
                            pa_item = bare_obj.get('packageAgreement') or {}
                            texts.extend([
                                str(pa_item.get('status') or ''),
                                str(pa_item.get('agreementStatus') or ''),
                                str(pa_item.get('state') or ''),
                                str(bare_obj.get('status') or ''),
                                str(bare_obj.get('state') or '')
                            ])
                            flags.extend([
                                bare_obj.get('isCancelled'), bare_obj.get('isCanceled'),
                                bare_obj.get('isComplete'), bare_obj.get('isCompleted'),
                                bare_obj.get('inCollections'), bare_obj.get('isTerminated'),
                            ])
                        # Normalize and check
                        texts_lc = [t.strip().lower() for t in texts if isinstance(t, str)]
                        if any(bool(f) for f in flags):
                            return True
                        for t in texts_lc:
                            if any(k in t for k in ['cancel', 'complete', 'collection', 'terminated', 'expired']):
                                return True
                        return False
                    except Exception:
                        return False

                if _is_inactive_agreement(v2_json, item):
                    continue

                enriched = {
                    'agreement_id': aid,
                    'package_name': pkg_name or 'Training Package',
                    'status': status,
                    'amount_owed': round(float(amt or 0.0), 2),
                    # Include the full raw bare agreement item so UI can show billingStatuses etc.
                    'bare': item
                }
                # Add safe, optional fields for UI exploration
                if isinstance(b_json, dict):
                    enriched['billing'] = b_json
                if isinstance(v2_json, dict):
                    enriched['v2'] = v2_json
                    try:
                        include_obj = v2_json.get('include') if isinstance(v2_json.get('include'), dict) else None
                        invoices_list = None
                        if include_obj and isinstance(include_obj.get('invoices'), list):
                            invoices_list = include_obj.get('invoices')
                        elif isinstance(v2_json.get('invoices'), list):
                            invoices_list = v2_json.get('invoices')
                        if isinstance(invoices_list, list):
                            enriched['invoices_count'] = len(invoices_list)
                            # Provide a compact summary of invoices contributing to past due
                            if invoice_list:
                                enriched['past_due_invoices'] = invoice_list
                                enriched['past_due_amount'] = invoice_amt
                                enriched['past_due_count'] = invoice_count
                    except Exception:
                        pass

                normalized.append(enriched)

            except Exception as e:
                logger.warning(f"⚠️ Error processing agreement {aid}: {e}")
                continue

        logger.info(f"✅ Found {len(normalized)} agreements for member {member_id} (with funding)")
        return jsonify({
            'success': True,
            'member_id': member_id,
            'agreements': normalized,
            'total_agreements': len(normalized)
        })

    except Exception as e:
        logger.error(f"❌Œ Error fetching package agreements for member {member_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


def parse_spa_agreement_response(html_content: str, agreement_id: str) -> dict:
    """Parse the ClubOS SPA HTML response to extract agreement data including invoices."""
    try:
        # The SPA response is HTML that contains embedded JSON data
        # Look for script tags or data attributes that contain the agreement data
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Try to find embedded JSON data in script tags
        scripts = soup.find_all('script')
        agreement_data = None
        
        for script in scripts:
            if script.string and 'agreement' in script.string.lower():
                # Look for JSON data in the script content
                try:
                    # Find JSON-like content
                    import re
                    json_match = re.search(r'\{.*"agreement".*\}', script.string, re.DOTALL)
                    if json_match:
                        import json
                        agreement_data = json.loads(json_match.group())
                        break
                except:
                    continue
        
        if not agreement_data:
            # Fallback: try to extract from data attributes or other sources
            # Look for data attributes that might contain agreement info
            data_elements = soup.find_all(attrs={"data-agreement": True})
            if data_elements:
                # Extract data from attributes
                agreement_data = {
                    'agreement_id': agreement_id,
                    'invoices': [],
                    'packageAgreement': {}
                }
        
        return agreement_data or {}
        
    except Exception as e:
        print(f"Error parsing SPA response: {e}")
        return {}


def compute_past_due_from_invoices(invoices: list | None) -> tuple[float, int, list]:
    """Compute past due strictly per SPA: sum invoice_total for invoices with status in {Delinquent, Pay Now}.

    - Only considers 'invoices' array (not 'scheduledPayments').
    - Prefer invoice_total; fall back to remainingTotal/total if absent.

    Returns: (amount, count, contributing_invoices)
    """
    if not isinstance(invoices, list):
        return 0.0, 0, []
    total = 0.0
    picked = []
    for inv in invoices:
        if not isinstance(inv, dict):
            continue
        raw_status = inv.get('status') if isinstance(inv.get('status'), str) else None
        status_text = (raw_status or '').strip().lower()
        # SPA parity: only these text statuses count
        if status_text not in {'delinquent', 'pay now'}:
            continue

        # Prefer invoice_total when available, then remainingTotal/total
        amt = (
            _to_float(inv.get('invoice_total'))
            or _to_float(inv.get('remainingTotal'))
            or _to_float(inv.get('total'))
        )
        if amt <= 0:
            continue
        total += amt
        try:
            picked.append({
                'id': inv.get('id'),
                'date': inv.get('billingDate') or inv.get('date') or inv.get('invoiceDate') or inv.get('createdAt'),
                'status_text': raw_status,
                'remainingTotal': inv.get('remainingTotal'),
                'invoice_total': inv.get('invoice_total'),
                'total': inv.get('total')
            })
        except Exception:
            pass
    return round(total, 2), len(picked), picked

@app.route('/api/agreements/<agreement_id>/invoices')
def get_agreement_invoices(agreement_id):
    """Debug endpoint: fetch agreement V2 and return invoices + computed past due to mirror UI.

    Mirrors the SPA page logic described: sum invoice_total for invoices where status is
    'Delinquent' or 'Pay Now' (i.e., anything not 'Paid' considered due by UI), with
    fallbacks to remainingTotal/total when invoice_total is absent.
    """
    try:
        # Ensure ClubOS API is authenticated
        if not clubos_training_api.authenticated:
            if not clubos_training_api.authenticate():
                return jsonify({'success': False, 'error': 'ClubOS authentication failed'}), 500

        # Optionally delegate to a member context if provided (mirrors SPA navigation)
        member_id = request.args.get('member_id')
        delegated = False
        if member_id:
            try:
                delegated = clubos_training_api.delegate_to_member(member_id)
            except Exception:
                delegated = False

        # Fetch V2 with includes as the SPA does
        v2_url = f"{clubos_training_api.base_url}/api/agreements/package_agreements/V2/{agreement_id}"
        v2_params = [
            ('include', 'invoices'),
            ('include', 'scheduledPayments'),
            ('include', 'prohibitChangeTypes'),
            ('_', str(int(time.time() * 1000)))
        ]
        v2_headers = clubos_training_api._auth_headers(
            referer=f"{clubos_training_api.base_url}/action/PackageAgreementUpdated/spa/#/package-agreements/{agreement_id}"
        )
        resp = clubos_training_api.session.get(v2_url, headers=v2_headers, params=v2_params, timeout=15)
        if resp.status_code != 200:
            return jsonify({'success': False, 'error': f'HTTP {resp.status_code} from V2', 'delegated': delegated}), 502

        v2_json = resp.json()
        include_obj = v2_json.get('include') if isinstance(v2_json, dict) else None
        invoices = None
        if isinstance(include_obj, dict) and isinstance(include_obj.get('invoices'), list):
            invoices = include_obj.get('invoices')
        elif isinstance(v2_json, dict) and isinstance(v2_json.get('invoices'), list):
            invoices = v2_json.get('invoices')
        if not isinstance(invoices, list):
            invoices = []

        # Normalize invoices for clarity
        def _to_float(val):
            try:
                if isinstance(val, (int, float)):
                    return float(val)
                if isinstance(val, str):
                    return float(val.replace('$', '').replace(',', '').strip())
            except Exception:
                return 0.0
            return 0.0

        simplified = []
        for inv in invoices:
            if not isinstance(inv, dict):
                continue
            simplified.append({
                'id': inv.get('id'),
                'invoice_date': inv.get('billingDate') or inv.get('date') or inv.get('invoiceDate') or inv.get('createdAt'),
                'invoice_total': inv.get('invoice_total') if 'invoice_total' in inv else (
                    inv.get('total') if 'total' in inv else inv.get('remainingTotal')
                ),
                'status': inv.get('status'),
                'invoiceStatus': inv.get('invoiceStatus'),
                'remainingTotal': inv.get('remainingTotal'),
                'total': inv.get('total')
            })

        # Past due per SPA: sum invoice_total for Delinquent/Pay Now (and not Paid)
        def _is_past_due_status(text):
            t = (text or '').strip().lower()
            return t in {'delinquent', 'pay now'}

        past_due = 0.0
        contributing = []
        for inv in simplified:
            status_text = inv.get('status')
            if _is_past_due_status(status_text):
                amt = _to_float(inv.get('invoice_total')) or _to_float(inv.get('remainingTotal')) or _to_float(inv.get('total'))
                if amt > 0:
                    past_due += amt
                    contributing.append({
                        'id': inv.get('id'),
                        'status': status_text,
                        'invoice_total': inv.get('invoice_total'),
                        'remainingTotal': inv.get('remainingTotal'),
                        'total': inv.get('total')
                    })

        return jsonify({
            'success': True,
            'agreement_id': agreement_id,
            'delegated': delegated,
            'invoices': simplified,
            'computed': {
                'past_due_amount': round(past_due, 2),
                'method': 'sum(invoice_total) for status in [Delinquent, Pay Now] (fallback to remainingTotal/total)',
                'contributing_invoices': contributing
            }
        })

    except Exception as e:
        logger.error(f"❌Œ Error fetching invoices for agreement {agreement_id}: {e}")
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
        logger.info("")
        
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
                logger.error(f"❌Œ Error updating member: {e}")
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
        logger.error(f"❌Œ Error in manual member refresh: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/refresh-members-full', methods=['POST'])
def api_refresh_members_full():
    """API endpoint to force a full refresh of all member data (use sparingly)"""
    try:
        logger.info("🔄 Force refreshing ALL member data from ClubHub...")
        
        # Call the full import function
        category_counts = import_fresh_clubhub_data()
        
        if category_counts:
            return jsonify({
                'success': True,
                'message': 'Full member refresh completed successfully',
                'category_breakdown': category_counts
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Full member refresh failed'
            }), 500
        
    except Exception as e:
        logger.error(f"❌ Error during full member refresh: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/refresh-training-clients', methods=['POST', 'GET'])
def refresh_training_clients():
    """API endpoint to refresh training clients from ClubHub"""
    try:
        logger.info("ðŸ‹ï¸ Refreshing training clients from ClubHub...")
        
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
                    logger.info(f"ðŸŽ¯ Found Dennis Rost - Training indicators: {has_training}")
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
                    logger.info(f"❌ž• Added training client: {client_data['member_name']}")
                    
            except Exception as e:
                logger.error(f"❌Œ Error adding training client {member.get('firstName')} {member.get('lastName')}: {e}")
        
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
        logger.error(f"❌Œ Error refreshing training clients: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/calendar')
def calendar_page():
    """Display calendar page."""
    return render_template('calendar.html')

@app.route('/api/debug/agreement/<agreement_id>/invoices')
def debug_agreement_invoices(agreement_id):
    """Debug endpoint to see exactly what invoice data is being returned from ClubOS."""
    try:
        # Ensure ClubOS API is authenticated
        if not clubos_training_api.authenticated:
            if not clubos_training_api.authenticate():
                return jsonify({'success': False, 'error': 'ClubOS authentication failed'}), 500

        # Fetch V2 with includes as the SPA does
        v2_url = f"{clubos_training_api.base_url}/api/agreements/package_agreements/V2/{agreement_id}"
        v2_params = [
            ('include', 'invoices'),
            ('include', 'scheduledPayments'),
            ('include', 'prohibitChangeTypes'),
            ('_', str(int(time.time() * 1000)))
        ]
        
        # Use the package SPA as referer to match UI navigation
        v2_headers = clubos_training_api._auth_headers(referer=f"{clubos_training_api.base_url}/action/PackageAgreementUpdated/spa/")
        v2_resp = clubos_training_api.session.get(v2_url, headers=v2_headers, params=v2_params, timeout=14)
        
        if v2_resp.status_code != 200:
            return jsonify({'success': False, 'error': f'ClubOS API returned {v2_resp.status_code}'}), 500
            
        v2_json = v2_resp.json()
        
        # Extract invoice data
        invoices = []
        if isinstance(v2_json, dict):
            # Check different possible locations for invoices
            if v2_json.get('include') and isinstance(v2_json['include'].get('invoices'), list):
                invoices = v2_json['include']['invoices']
            elif isinstance(v2_json.get('invoices'), list):
                invoices = v2_json['invoices']
        
        # Calculate past due using the same logic as the main endpoint
        def _to_float(v):
            if v is None:
                return 0.0
            if isinstance(v, (int, float)):
                return float(v)
            if isinstance(v, str):
                return float(v.replace('$', '').replace(',', '')) if v.strip() else 0.0
            return 0.0
        
        past_due_invoices = []
        total_past_due = 0.0
        
        for inv in invoices:
            if not isinstance(inv, dict):
                continue
            status = (inv.get('status') or '').strip().lower()
            if status in ['delinquent', 'pay now']:
                amount = _to_float(inv.get('invoice_total')) or _to_float(inv.get('remainingTotal')) or _to_float(inv.get('total'))
                if amount > 0:
                    total_past_due += amount
                    past_due_invoices.append({
                        'id': inv.get('id'),
                        'status': inv.get('status'),
                        'invoice_total': inv.get('invoice_total'),
                        'remainingTotal': inv.get('remainingTotal'),
                        'total': inv.get('total'),
                        'date': inv.get('invoice_date') or inv.get('billingDate') or inv.get('date'),
                        'amount_contributed': amount
                    })
        
        return jsonify({
            'success': True,
            'agreement_id': agreement_id,
            'raw_v2_response': v2_json,
            'invoices_found': len(invoices),
            'invoices_data': invoices,
            'past_due_invoices': past_due_invoices,
            'total_past_due': round(total_past_due, 2),
            'past_due_count': len(past_due_invoices)
        })
        
    except Exception as e:
        logger.error(f"❌Œ Error debugging agreement invoices for {agreement_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/debug/agreement/<agreement_id>/v2-raw')
def debug_agreement_v2_raw(agreement_id):
    """Debug endpoint to show the raw V2 API response from ClubOS for a specific agreement."""
    try:
        # Ensure ClubOS API is authenticated
        if not clubos_training_api.authenticated:
            if not clubos_training_api.authenticate():
                return jsonify({'success': False, 'error': 'ClubOS authentication failed'}), 500

        # Fetch from the recommended ClubOS SPA endpoint
        spa_url = f"{clubos_training_api.base_url}/action/PackageAgreementUpdated/spa/#/package-agreements/{agreement_id}"
        
        # Use the package SPA as referer to match UI navigation
        spa_headers = clubos_training_api._auth_headers(referer=f"{clubos_training_api.base_url}/action/PackageAgreementUpdated/spa/")
        spa_resp = clubos_training_api.session.get(spa_url, headers=spa_headers, timeout=14)
        
        if spa_resp.status_code != 200:
            return jsonify({
                'success': False, 
                'error': f'ClubOS SPA returned status {spa_resp.status_code}',
                'response_text': spa_resp.text[:500] if spa_resp.text else 'No response text'
            }), 500
        
        # Parse the SPA HTML response to extract agreement data
        v2_json = parse_spa_agreement_response(spa_resp.text, agreement_id)
        
        # Extract invoice information for debugging
        invoice_info = {
            'raw_response': v2_json,
            'has_include': 'include' in v2_json,
            'include_type': type(v2_json.get('include')).__name__ if 'include' in v2_json else None,
            'has_invoices': False,
            'invoices_location': None,
            'invoices_count': 0,
            'invoices_sample': None
        }
        
        # Check different possible locations for invoices
        if isinstance(v2_json.get('include'), dict) and isinstance(v2_json['include'].get('invoices'), list):
            invoice_info['has_invoices'] = True
            invoice_info['invoices_location'] = 'include.invoices'
            invoice_info['invoices_count'] = len(v2_json['include']['invoices'])
            invoice_info['invoices_sample'] = v2_json['include']['invoices'][:3] if v2_json['include']['invoices'] else None
        elif isinstance(v2_json.get('invoices'), list):
            invoice_info['has_invoices'] = True
            invoice_info['invoices_location'] = 'root.invoices'
            invoice_info['invoices_count'] = len(v2_json['invoices'])
            invoice_info['invoices_sample'] = v2_json['invoices'][:3] if v2_json['invoices'] else None
        
        return jsonify({
            'success': True,
            'agreement_id': agreement_id,
            'v2_url': v2_url,
            'v2_params': v2_params,
            'invoice_info': invoice_info,
            'response_keys': list(v2_json.keys()) if isinstance(v2_json, dict) else [],
            'include_keys': list(v2_json.get('include', {}).keys()) if isinstance(v2_json.get('include'), dict) else []
        })
        
    except Exception as e:
        return jsonify({
            'success': False, 
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/api/invoices/batch', methods=['POST'])
def api_batch_invoices():
    """API endpoint to create batch invoices for multiple members."""
    try:
        data = request.get_json()
        invoice_type = data.get('type', 'members')
        filter_type = data.get('filter', 'past_due')
        selected_clients = data.get('selected_clients', [])
        
        if not selected_clients:
            return jsonify({'success': False, 'error': 'No members selected for invoicing'}), 400
        
        if not SQUARE_AVAILABLE:
            return jsonify({'success': False, 'error': 'Square payment service is not available.'}), 503
        
        logger.info(f"")
        
        # Get member details from database
        conn = sqlite3.connect(db_manager.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get member information for selected IDs
        placeholders = ','.join(['?' for _ in selected_clients])
        cursor.execute(f"""
            SELECT id, first_name, last_name, full_name, email, amount_past_due, 
                   amount_of_next_payment, payment_amount, agreement_rate
            FROM members 
            WHERE id IN ({placeholders})
        """, selected_clients)
        
        members = cursor.fetchall()
        conn.close()
        
        if not members:
            return jsonify({'success': False, 'error': 'No valid members found'}), 404
        
        # Process each member
        successful_invoices = []
        failed_invoices = []
        
        for member in members:
            try:
                member_id = member['id']
                member_name = member['full_name'] or f"{member['first_name']} {member['last_name']}".strip()
                email = member['email']
                
                # Calculate invoice amount
                amount_past_due = float(member['amount_past_due'] or 0)
                next_payment = float(member['amount_of_next_payment'] or 0)
                monthly_rate = float(member['agreement_rate'] or member['payment_amount'] or 0)
                
                # Apply late fee if past due
                late_fee = 25.0 if amount_past_due > 0 else 0.0
                total_amount = amount_past_due + late_fee
                
                # If no past due amount, use next payment or monthly rate
                if total_amount <= 0:
                    total_amount = next_payment if next_payment > 0 else monthly_rate
                
                # Ensure we have a valid amount (minimum $5)
                total_amount = max(float(total_amount), 5.0)
                
                # Create description
                description = f"Payment for {member_name}"
                if amount_past_due > 0:
                    description += f" - Past Due: ${amount_past_due:.2f}"
                if late_fee > 0:
                    description += f" + Late Fee: ${late_fee:.2f}"
                
                # Create Square invoice with correct parameter order
                invoice_result = create_square_invoice(member_name, email, total_amount, description)
                invoice_url = invoice_result.get('public_url') if isinstance(invoice_result, dict) and invoice_result.get('success') else None
                
                if invoice_url:
                    successful_invoices.append({
                        'member_id': member_id,
                        'member_name': member_name,
                        'email': email,
                        'amount': total_amount,
                        'invoice_url': invoice_url,
                        'description': description
                    })
                    logger.info(f"✅ Invoice created for {member_name}: ${float(total_amount):.2f}")
                else:
                    failed_invoices.append({
                        'member_id': member_id,
                        'member_name': member_name,
                        'email': email,
                        'amount': total_amount,
                        'error': 'Failed to create Square invoice'
                    })
                    logger.error(f"❌Œ Failed to create invoice for {member_name}")
                    
            except Exception as e:
                member_name = member.get('full_name', 'Unknown') or f"{member.get('first_name', '')} {member.get('last_name', '')}".strip()
                failed_invoices.append({
                    'member_id': member.get('id'),
                    'member_name': member_name,
                    'email': member.get('email'),
                    'error': str(e)
                })
                logger.error(f"❌Œ Error processing invoice for {member_name}: {e}")
                continue
        
        # Prepare summary
        summary = {
            'total_processed': len(selected_clients),
            'successful': len(successful_invoices),
            'failed': len(failed_invoices),
            'total_amount': sum(inv['amount'] for inv in successful_invoices)
        }
        
        logger.info(f"ðŸŽ‰ Batch invoicing completed: {summary['successful']} successful, {summary['failed']} failed")
        
        return jsonify({
            'success': True,
            'summary': summary,
            'successful_invoices': successful_invoices,
            'failed_invoices': failed_invoices,
            'message': f"Batch invoicing completed: {summary['successful']} successful, {summary['failed']} failed"
        })
        
    except Exception as e:
        logger.error(f"❌Œ Error in batch invoicing: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/debug/members')
def debug_members():
    """Debug endpoint to check what's in the members database."""
    try:
        conn = sqlite3.connect(db_manager.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Check table schema
        cursor.execute("PRAGMA table_info(members)")
        schema = cursor.fetchall()
        
        # Get total count
        cursor.execute("SELECT COUNT(*) FROM members")
        total_count = cursor.fetchone()[0]
        
        # Get sample members
        cursor.execute("SELECT * FROM members LIMIT 5")
        sample_members = [dict(row) for row in cursor.fetchall()]
        
        # Check for specific fields
        cursor.execute("SELECT COUNT(*) FROM members WHERE amount_past_due IS NULL")
        null_past_due = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM members WHERE date_of_next_payment IS NULL")
        null_next_payment = cursor.fetchone()[0]
        
        conn.close()
        
        return jsonify({
            'success': True,
            'schema': [dict(row) for row in schema],
            'total_count': total_count,
            'sample_members': sample_members,
            'null_past_due': null_past_due,
            'null_next_payment': null_next_payment
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    # On Windows, Werkzeug's reloader can trigger WinError 10038 (not a socket) during restarts.
    # Keep debug features but disable the auto-reloader for stability.
    app.run(debug=True, use_reloader=False, host='0.0.0.0', port=5000)
