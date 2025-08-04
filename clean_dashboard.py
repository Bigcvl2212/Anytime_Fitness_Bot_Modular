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
from flask import Flask, render_template, jsonify, request, redirect, url_for, session, flash
from datetime import datetime, timedelta
from typing import Dict, Any
import logging
import json
import sys
import requests
import time
from bs4 import BeautifulSoup

# Import our working ClubOS API
from clubos_training_api import ClubOSTrainingPackageAPI
from clubos_real_calendar_api import ClubOSRealCalendarAPI
from ical_calendar_parser import iCalClubOSParser
from gym_bot_clean import ClubOSEventDeletion
from clubos_fresh_data_api import ClubOSFreshDataAPI

app = Flask(__name__)
app.secret_key = 'anytime-fitness-dashboard-secret-key-2025'

# Create templates directory if it doesn't exist
templates_dir = 'templates'
if not os.path.exists(templates_dir):
    os.makedirs(templates_dir)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# Global instances
clubos_training_api = ClubOSTrainingPackageAPI()
clubos_fresh_data_api = ClubOSFreshDataAPI()

class TrainingPackageCache:
    """Enhanced cache for training package data with database storage and daily updates"""
    
    def __init__(self):
        self.cache_expiry_hours = 24  # Cache expires after 24 hours
        self.api = ClubOSTrainingPackageAPI()
        
    def lookup_participant_funding(self, participant_name: str, participant_email: str = None) -> dict:
        """Look up funding status - first from cache, then from ClubOS API if needed"""
        try:
            logger.info(f"🔍 Looking up funding for: {participant_name}")
            
            # First, check if we have cached data that's still fresh
            cached_data = self._get_cached_funding(participant_name)
            if cached_data and not self._is_cache_stale(cached_data):
                logger.info(f"✅ Using cached funding data for {participant_name}")
                return self._format_funding_response(cached_data)
            
            # If no fresh cache, get member ID and try to fetch fresh data
            member_id = self._get_member_id_from_database(participant_name, participant_email)
            if member_id:
                logger.info(f"📦 Fetching fresh funding data for member ID: {member_id}")
                fresh_data = self._fetch_fresh_funding_data(member_id, participant_name)
                if fresh_data:
                    # Cache the fresh data
                    self._cache_funding_data(fresh_data)
                    return self._format_funding_response(fresh_data)
            
            # If we have stale cached data, use it as fallback
            if cached_data:
                logger.info(f"⚠️ Using stale cached data for {participant_name}")
                return self._format_funding_response(cached_data, is_stale=True)
            
            # No data available
            logger.warning(f"❌ No funding data available for {participant_name}")
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
    
    def _format_funding_response(self, cached_data: dict, is_stale: bool = False) -> dict:
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
                'is_cached': True,
                'is_stale': is_stale
            }
            
            if is_stale:
                response['status_text'] += ' (Cached)'
                
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
            
            logger.warning(f"❌ No member ID found for participant: {participant_name}")
            return None
            
        except Exception as e:
            logger.error(f"❌ Database error looking up member ID: {e}")
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

# Import the master contact list with agreements
master_csv = "data/csv_exports/master_contact_list_with_agreements_20250802_123437.csv"
if os.path.exists(master_csv):
    members_count, prospects_count = db_manager.import_master_contact_list(master_csv)
    print(f"📊 Imported {members_count} members and {prospects_count} prospects")

# Import training clients
training_csv = "data/csv_exports/Clients_1753310478191.csv" 
if os.path.exists(training_csv):
    clients_count = db_manager.import_training_clients(training_csv)
    print(f"🏋️ Imported {clients_count} training clients")

class ClubOSIntegration:
    """Integration class to connect dashboard with working ClubOS API"""
    
    def __init__(self):
        self.api = ClubOSRealCalendarAPI("j.mayo", "j@SD4fjhANK5WNA")
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
                    # Format without funding status for speed
                    attendee_names = [attendee['name'] for attendee in event.attendees if attendee['name']]
                    
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

@app.route('/api/check-funding', methods=['POST'])
def check_funding():
    """API endpoint to check real funding status for participants"""
    try:
        data = request.get_json()
        participant_name = data.get('participant', '')
        time = data.get('time', '')
        
        logger.info(f"🔍 API request to check funding for: {participant_name}")
        
        # Use the training package cache to get real funding data
        funding_data = training_package_cache.lookup_participant_funding(participant_name)
        
        if funding_data:
            logger.info(f"✅ API returning funding data for {participant_name}: {funding_data}")
            return jsonify({
                'success': True,
                'funding': funding_data
            })
        else:
            logger.warning(f"⚠️ No funding data found for {participant_name}")
            return jsonify({
                'success': True,
                'funding': {
                    'status_text': 'No Data',
                    'status_class': 'secondary',
                    'status_icon': 'fas fa-question-circle',
                    'is_cached': False,
                    'message': 'No funding data available - please refresh cache'
                }
            })
    
    except Exception as e:
        logger.error(f"❌ Error in funding API: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

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

@app.route('/api/refresh-data', methods=['POST'])
def refresh_data():
    """API endpoint to manually refresh database with latest ClubOS data"""
    try:
        force = request.json.get('force', False) if request.is_json else False
        background = request.json.get('background', False) if request.is_json else False
        
        logger.info("🔄 Manual data refresh requested")
        
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
        active_csv = None
        
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
    """Display all members with search and filtering using FRESH ClubHub data."""
    
    # Get fresh member count from ClubHub API instead of stale database
    try:
        # Use ClubHub credentials to get ALL members directly (matching past-due API)
        CLUBHUB_LOGIN_URL = "https://clubhub-ios-api.anytimefitness.com/api/login"
        USERNAME = "mayo.jeremy2212@gmail.com"
        PASSWORD = "SruLEqp464_GLrF"
        
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
        
        fresh_total_members = 528  # fallback to old count if API fails
        
        if login_response.status_code == 200:
            login_result = login_response.json()
            bearer_token = login_result.get('accessToken')
            
            if bearer_token:
                session.headers.update({"Authorization": f"Bearer {bearer_token}"})
                
                # Get ALL members count from ClubHub API
                club_id = "1156"
                all_members = []
                page = 1
                
                while True:
                    members_url = f"https://clubhub-ios-api.anytimefitness.com/api/clubs/{club_id}/members?page={page}&pageSize=100"
                    members_response = session.get(members_url)
                    
                    if members_response.status_code != 200:
                        break
                        
                    members_data = members_response.json()
                    
                    # Create a 'full_name' field for easier display
                    for member in members_data:
                        member['full_name'] = f"{member.get('firstName', '')} {member.get('lastName', '')}".strip()

                    logger.info(f"📊 Found {len(members_data)} members on page {page}")
                    
                    # If we got no members, stop paginating to avoid unnecessary API calls
                    if len(members_data) == 0:
                        logger.info(f"🛑 No more members found, stopping pagination")
                        break
                    
                    all_members.extend(members_data)
                    page += 1
                
                fresh_total_members = len(all_members)
                logger.info(f"✅ Got {fresh_total_members} total fresh members from ClubHub API")
                
                # Use the fresh data directly instead of old database data
                return render_template('members.html',
                                     members=all_members,
                                     total_members=fresh_total_members,
                                     statuses=[m.get('status') for m in all_members if m.get('status')],
                                     search='',
                                     status_filter='',
                                     page=1,
                                     total_pages=1,
                                     per_page=fresh_total_members,
                                     red_list_count=0,
                                     yellow_list_count=0,
                                     past_due_count=0)
    
    except Exception as e:
        logger.error(f"❌ Error getting fresh member count: {e}")
        fresh_total_members = 528  # fallback
    
    # Fall back to database only if API fails
    conn = sqlite3.connect(db_manager.db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get search and filter parameters
    search = request.args.get('search', '')
    status_filter = request.args.get('status', '')
    page = int(request.args.get('page', 1))
    per_page = 50  # Show 50 members per page
    
    # Build query with search and filters
    where_conditions = []
    params = []
    
    # IMPORTANT: Exclude past due members from "All Members" tab
    # Past due members should only appear in the "Past Due" tab
    where_conditions.append("(amount_past_due IS NULL OR amount_past_due <= 0)")
    where_conditions.append("(date_of_next_payment IS NULL OR date_of_next_payment > date('now', '+7 days'))")
    
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
    
    # Get local database count (just for pagination)
    count_query = f"SELECT COUNT(*) FROM members {where_clause}"
    cursor.execute(count_query, params)
    local_members_count = cursor.fetchone()[0]
    
    # Calculate pagination
    total_pages = (local_members_count + per_page - 1) // per_page
    offset = (page - 1) * per_page
    
    # Get members for current page
    query = f"""
        SELECT id, first_name, last_name, full_name, email, mobile_phone, status, 
               membership_start, membership_end, payment_amount, user_type, created_at, 
               agreement_rate, amount_past_due, amount_of_next_payment, date_of_next_payment
        FROM members {where_clause}
        ORDER BY 
            CASE 
                WHEN amount_past_due > 0 THEN 1  -- Red list (past due) first
                WHEN date_of_next_payment <= date('now', '+7 days') THEN 2  -- Yellow list (due soon) second
                ELSE 3  -- Everyone else
            END,
            amount_past_due DESC,  -- Within red list, highest amounts first
            created_at DESC
        LIMIT ? OFFSET ?
    """
    cursor.execute(query, params + [per_page, offset])
    members_data = cursor.fetchall()
    
    # Process members to add payment status flags
    members = []
    for member in members_data:
        member_dict = dict(member)
        
        # Always generate full_name regardless of database content
        first_name = member_dict.get('first_name', '')
        last_name = member_dict.get('last_name', '')
        member_dict['full_name'] = f"{first_name} {last_name}".strip()
        
        # Make sure we have at least something for display
        if not member_dict['full_name']:
            # Try to extract name from email
            email = member_dict.get('email', '')
            if email and '@' in email:
                username = email.split('@')[0]
                # Clean up username (remove numbers, dots, etc.)
                cleaned_name = ''.join([c for c in username if c.isalpha() or c == ' ']).title()
                if cleaned_name:
                    member_dict['full_name'] = f"{cleaned_name} (from email)"
        
        # Determine payment status category
        amount_past_due = member['amount_past_due'] if member['amount_past_due'] else 0
        date_of_next_payment = member['date_of_next_payment']
        
        if amount_past_due > 0:
            # Red list - past due
            member_dict['payment_status'] = 'red'
            member_dict['payment_status_text'] = f'Past Due: ${amount_past_due:.2f}'
            member_dict['payment_status_class'] = 'danger'
            member_dict['payment_priority'] = 1
        elif date_of_next_payment:
            # Check if payment is due soon (within 7 days)
            try:
                next_payment_date = datetime.strptime(date_of_next_payment, '%Y-%m-%d').date()
                days_until_payment = (next_payment_date - datetime.now().date()).days
                
                if 0 <= days_until_payment <= 7:
                    # Yellow list - due soon
                    member_dict['payment_status'] = 'yellow'
                    if days_until_payment == 0:
                        member_dict['payment_status_text'] = f'Due Today: ${member["amount_of_next_payment"] if member["amount_of_next_payment"] else 0:.2f}'
                    else:
                        member_dict['payment_status_text'] = f'Due in {days_until_payment} days: ${member["amount_of_next_payment"] if member["amount_of_next_payment"] else 0:.2f}'
                    member_dict['payment_status_class'] = 'warning'
                    member_dict['payment_priority'] = 2
                else:
                    # Green list - current
                    member_dict['payment_status'] = 'green'
                    member_dict['payment_status_text'] = 'Current'
                    member_dict['payment_status_class'] = 'success'
                    member_dict['payment_priority'] = 3
            except (ValueError, TypeError):
                # Can't parse date - assume current
                member_dict['payment_status'] = 'green'
                member_dict['payment_status_text'] = 'Current'
                member_dict['payment_status_class'] = 'success'
                member_dict['payment_priority'] = 3
        else:
            # No payment data - assume current
            member_dict['payment_status'] = 'green'
            member_dict['payment_status_text'] = 'Current'
            member_dict['payment_status_class'] = 'success'
            member_dict['payment_priority'] = 3
        
        members.append(member_dict)
    
    # Get unique statuses for filter dropdown
    cursor.execute("SELECT DISTINCT status FROM members WHERE status IS NOT NULL AND status != ''")
    statuses = [row[0] for row in cursor.fetchall()]
    
    # Get counts for red and yellow lists (for the tab badges)
    cursor.execute("SELECT COUNT(*) FROM members WHERE amount_past_due > 0")
    red_list_count = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT COUNT(*) FROM members 
        WHERE date_of_next_payment <= date('now', '+7 days') 
        AND amount_past_due = 0
    """)
    yellow_list_count = cursor.fetchone()[0]
    
    conn.close()
    
    return render_template('members.html',
                         members=members,
                         total_members=fresh_total_members,  # Use fresh ClubHub count
                         statuses=statuses,
                         search=search,
                         status_filter=status_filter,
                         page=page,
                         total_pages=total_pages,
                         per_page=per_page,
                         red_list_count=red_list_count,
                         yellow_list_count=yellow_list_count,
                         past_due_count=red_list_count + yellow_list_count)

@app.route('/api/member/<member_id>')
def get_member_profile(member_id):
    """Get detailed member profile information from fresh ClubHub data."""
    try:
        # Use ClubHub credentials to get fresh member data directly 
        CLUBHUB_LOGIN_URL = "https://clubhub-ios-api.anytimefitness.com/api/login"
        USERNAME = "mayo.jeremy2212@gmail.com"
        PASSWORD = "SruLEqp464_GLrF"
        
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
            return jsonify({'success': False, 'error': 'No bearer token received from ClubHub login'}), 500
        
        session.headers.update({"Authorization": f"Bearer {bearer_token}"})
        
        # Get member details from ClubHub API
        member_url = f"https://clubhub-ios-api.anytimefitness.com/api/members/{member_id}/profile"
        member_response = session.get(member_url)
        
        if member_response.status_code != 200:
            # Fall back to database if API fails
            conn = sqlite3.connect(db_manager.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Try to find member in database as fallback
            cursor.execute("SELECT * FROM members WHERE id = ? OR guid = ?", (member_id, member_id))
            member = cursor.fetchone()
            
            if not member:
                return jsonify({'success': False, 'error': f'Member not found with ID: {member_id}'}), 404
            
            member_dict = dict(member)
            member_dict['data_source'] = 'database'
        else:
            # Use fresh data from ClubHub API
            member_dict = member_response.json()
            member_dict['data_source'] = 'clubhub_api'
            member_dict['full_name'] = f"{member_dict.get('firstName', '')} {member_dict.get('lastName', '')}".strip()
        
        # Get member agreements if available
        agreements = []
        if member_dict.get('data_source') == 'database':
            conn = sqlite3.connect(db_manager.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    SELECT * FROM member_agreements WHERE member_id = ?
                """, (member_id,))
                agreements = [dict(row) for row in cursor.fetchall()]
            except sqlite3.OperationalError:
                # Table doesn't exist yet
                pass
        elif member_dict.get('agreements'):
            # If agreements are in ClubHub response
            agreements = member_dict.get('agreements', [])
        
        # Get payment info
        payments = []
        if member_dict.get('data_source') == 'database':
            try:
                cursor.execute("""
                    SELECT * FROM member_payments WHERE member_id = ? ORDER BY payment_date DESC LIMIT 10
                """, (member_id,))
                payments = [dict(row) for row in cursor.fetchall()]
            except sqlite3.OperationalError:
                # Table doesn't exist yet
                pass
        elif member_dict.get('payments'):
            # If payments are in ClubHub response
            payments = member_dict.get('payments', [])
            
        # Get billing info if available in ClubHub data
        if member_dict.get('data_source') == 'clubhub_api' and member_dict.get('billingInfo'):
            billing_info = member_dict.get('billingInfo', {})
            member_dict['payment_token'] = billing_info.get('paymentToken')
            member_dict['card_type'] = billing_info.get('cardType')
            member_dict['card_last4'] = billing_info.get('lastFour')
            member_dict['expiration_month'] = billing_info.get('expirationMonth')
            member_dict['expiration_year'] = billing_info.get('expirationYear')
        
        # Calculate payment status - use ClubHub data if available
        amount_past_due = member_dict.get('amountPastDue', member_dict.get('amount_past_due', 0)) or 0
        date_of_next_payment = member_dict.get('dateOfNextPayment', member_dict.get('date_of_next_payment'))
        
        payment_status = {
            'status': 'current',
            'class': 'success',
            'text': 'Current',
            'amount_past_due': amount_past_due,
            'next_payment_amount': member['amount_of_next_payment'],
            'next_payment_date': date_of_next_payment
        }
        
        if amount_past_due > 0:
            payment_status.update({
                'status': 'past_due',
                'class': 'danger', 
                'text': f'Past Due: ${amount_past_due:.2f}'
            })
        elif date_of_next_payment:
            try:
                next_payment_date = datetime.strptime(date_of_next_payment, '%Y-%m-%d').date()
                days_until_payment = (next_payment_date - datetime.now().date()).days
                
                if 0 <= days_until_payment <= 7:
                    payment_status.update({
                        'status': 'due_soon',
                        'class': 'warning',
                        'text': f'Due in {days_until_payment} days' if days_until_payment > 0 else 'Due Today'
                    })
            except (ValueError, TypeError):
                pass
        
        conn.close()
        
        # Now try to get real-time member details from ClubHub API
        try:
            # ClubHub API configuration
            CLUBHUB_LOGIN_URL = "https://clubhub-ios-api.anytimefitness.com/api/login"
            USERNAME = "mayo.jeremy2212@gmail.com"
            PASSWORD = "SruLEqp464_GLrF"
            
            # Set up session with headers
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
            
            fresh_member_details = None
            
            if login_response.status_code == 200:
                login_result = login_response.json()
                bearer_token = login_result.get('accessToken')
                
                if bearer_token:
                    session.headers.update({"Authorization": f"Bearer {bearer_token}"})
                    
                    # Try to get fresh member details from ClubHub API
                    club_id = "1156"
                    
                    # Try to use any ID we have - clubos_member_id, id, or the member_id from the route
                    member_lookup_id = member_dict.get('clubos_member_id') or member_dict.get('id') or member_id
                    
                    if member_lookup_id:
                        logger.info(f"🔍 Fetching fresh data for member ID: {member_lookup_id}")
                        member_details_url = f"https://clubhub-ios-api.anytimefitness.com/api/clubs/{club_id}/members/{member_lookup_id}"
                        member_details_response = session.get(member_details_url)
                        
                        if member_details_response.status_code == 200:
                            fresh_member_details = member_details_response.json()
                            
                            # Create a proper full name from the API response
                            fresh_member_details['full_name'] = f"{fresh_member_details.get('firstName', '')} {fresh_member_details.get('lastName', '')}".strip()
                            
                            # Add the fresh data to our response
                            member_dict['fresh_data'] = True
                            
                            # Add additional meaningful fields
                            member_dict.update({
                                'first_name': fresh_member_details.get('firstName', member_dict.get('first_name')),
                                'last_name': fresh_member_details.get('lastName', member_dict.get('last_name')),
                                'full_name': fresh_member_details.get('full_name', member_dict.get('full_name')),
                                'email': fresh_member_details.get('email', member_dict.get('email')),
                                'mobile_phone': fresh_member_details.get('mobilePhone', member_dict.get('mobile_phone')),
                                'status': fresh_member_details.get('status', member_dict.get('status')),
                                'last_visit': fresh_member_details.get('lastVisit', member_dict.get('last_visit')),
                                'membership_start': fresh_member_details.get('membershipStart', member_dict.get('membership_start')),
                                'membership_end': fresh_member_details.get('membershipEnd', member_dict.get('membership_end')),
                                'clubos_member_id': fresh_member_details.get('memberId', member_dict.get('clubos_member_id')),
                                'user_type': fresh_member_details.get('memberType', member_dict.get('user_type')),
                                'club_hub_data': fresh_member_details  # Store the full response for reference
                            })
        except Exception as e:
            logger.error(f"❌ Error getting fresh member details: {str(e)}")
            # Add a flag to indicate we couldn't get fresh data
            member_dict['fresh_data'] = False
            member_dict['fresh_data_error'] = str(e)
            # Continue with database info if fresh API call fails
        
        return jsonify({
            'success': True,
            'member': member_dict,
            'agreements': agreements,
            'payments': payments,
            'payment_status': payment_status
        })
        
    except Exception as e:
        logger.error(f"❌ Error getting member profile: {str(e)}")
        return jsonify({
            'success': False, 
            'error': str(e),
            'message': 'Failed to retrieve member profile data. Please try again or contact support.'
        }), 500

@app.route('/api/members/past-due')
def get_past_due_members():
    """Get members who are past due on payments using FRESH ClubHub API data"""
    try:
        import datetime
        logger.info("🔍 Getting past due members from FRESH ClubHub API...")
        
        # Use ClubHub credentials to get ALL members directly (matching HAR analysis)
        import requests
        
        # ClubHub API configuration (from working HAR analysis)
        CLUBHUB_LOGIN_URL = "https://clubhub-ios-api.anytimefitness.com/api/login"
        CLUBHUB_API_BASE = "https://clubhub-ios-api.anytimefitness.com/api/v1.0"
        
        # Working credentials from HAR
        # Note: These credentials might need updating if they expire
        USERNAME = "mayo.jeremy2212@gmail.com"
        PASSWORD = "SruLEqp464_GLrF"
        
        # Check for environment variables that might override the hardcoded credentials
        import os
        env_username = os.environ.get('CLUBHUB_USERNAME')
        env_password = os.environ.get('CLUBHUB_PASSWORD')
        
        if env_username and env_password:
            logger.info("🔑 Using credentials from environment variables")
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
        
        logger.info("🔑 Authenticating with ClubHub...")
        try:
            login_response = session.post(CLUBHUB_LOGIN_URL, json=login_data)
            logger.info(f"🔑 ClubHub login response status: {login_response.status_code}")
            
            if login_response.status_code == 200:
                login_result = login_response.json()
                logger.info(f"🔑 ClubHub login response keys: {list(login_result.keys())}")
                bearer_token = login_result.get('accessToken')  # Fixed: was 'token', should be 'accessToken'
            else:
                logger.error(f"🔑 ClubHub authentication failed with status {login_response.status_code}")
                try:
                    error_data = login_response.json()
                    logger.error(f"🔑 ClubHub error response: {error_data}")
                except:
                    logger.error(f"🔑 ClubHub error text: {login_response.text}")
        except Exception as e:
            logger.error(f"❌ Exception during ClubHub authentication: {e}")
            raise
            
        login_response = None  # Initialize outside the try block for the else clause
        bearer_token = None  # Initialize outside the try block
        try:
            login_response = session.post(CLUBHUB_LOGIN_URL, json=login_data)
            logger.info(f"🔑 ClubHub login response status: {login_response.status_code}")
            
            if login_response.status_code == 200:
                login_result = login_response.json()
                logger.info(f"🔑 ClubHub login response keys: {list(login_result.keys())}")
                bearer_token = login_result.get('accessToken')  # Fixed: was 'token', should be 'accessToken'
            else:
                logger.error(f"🔑 ClubHub authentication failed with status {login_response.status_code}")
                try:
                    error_data = login_response.json()
                    logger.error(f"🔑 ClubHub error response: {error_data}")
                except:
                    logger.error(f"🔑 ClubHub error text: {login_response.text}")
                    
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
                    logger.info(f"📄 Fetching page {page}...")
                    
                    members_response = session.get(members_url)
                    
                    if members_response.status_code != 200:
                        logger.error(f"❌ Failed to fetch page {page}: {members_response.status_code}")
                        break
                        
                    members_data = members_response.json()
                    
                    # Create a 'full_name' field for easier display
                    for member in members_data:
                        member['full_name'] = f"{member.get('firstName', '')} {member.get('lastName', '')}".strip()

                    logger.info(f"📊 Found {len(members_data)} members on page {page}")
                    
                    # If we got no members, stop paginating to avoid unnecessary API calls
                    if len(members_data) == 0:
                        logger.info(f"🛑 No more members found, stopping pagination")
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
                    logger.error(f"❌ Failed to cache data: {cache_error}")
                
                return jsonify(response_data)
            else:
                logger.error("❌ No bearer token received from ClubHub login")
                return jsonify({
                    'red_count': 0,
                    'yellow_count': 0,
                    'total_count': 0,
                    'past_due_members': [],
                    'error': 'No bearer token received from ClubHub'
                }), 500
                
        except Exception as e:
            logger.error(f"❌ ClubHub API access error: {e}")
            # Try to use cached data if available
            try:
                import json
                import os
                cache_path = os.path.join(os.path.dirname(__file__), 'cache', 'past_due_members_cache.json')
                
                if os.path.exists(cache_path):
                    logger.info("🔍 ClubHub API failed, using cached past due data")
                    with open(cache_path, 'r') as cache_file:
                        cached_data = json.load(cache_file)
                        cached_data['message'] = 'Using cached data (ClubHub API is unavailable)'
                        cached_data['data_source'] = 'cache'
                        return jsonify(cached_data)
            except Exception as cache_error:
                logger.error(f"❌ Failed to read cache: {cache_error}")
                
            # If no cache or cache failed, return error
            return jsonify({
                'red_count': 0,
                'yellow_count': 0,
                'total_count': 0,
                'past_due_members': [],
                'error': f'ClubHub API error: {e}'
            }), 500
            
    except Exception as e:
        logger.error(f"❌ Error getting fresh ClubHub data: {e}")
        return jsonify({
            'red_count': 0,
            'yellow_count': 0,
            'total_count': 0,
            'past_due_members': [],
            'error': str(e)
        }), 500

@app.route('/prospects')
def prospects_page():
    """Display all prospects with search and filtering."""
    conn = sqlite3.connect(db_manager.db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get search and filter parameters
    search = request.args.get('search', '')
    status_filter = request.args.get('status', '')
    page = int(request.args.get('page', 1))
    per_page = 50
    
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
    count_query = f"SELECT COUNT(*) FROM prospects {where_clause}"
    cursor.execute(count_query, params)
    total_prospects = cursor.fetchone()[0]
    
    # Calculate pagination
    total_pages = (total_prospects + per_page - 1) // per_page
    offset = (page - 1) * per_page
    
    # Get prospects for current page
    query = f"""
        SELECT id, first_name, last_name, full_name, email, mobile_phone, status, 
               user_type, created_at, key_fob, photo_url
        FROM prospects {where_clause}
        ORDER BY created_at DESC 
        LIMIT ? OFFSET ?
    """
    cursor.execute(query, params + [per_page, offset])
    prospects = cursor.fetchall()
    
    # Get unique statuses for filter dropdown
    cursor.execute("SELECT DISTINCT status FROM prospects WHERE status IS NOT NULL AND status != ''")
    statuses = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    
    return render_template('prospects.html',
                         prospects=prospects,
                         total_prospects=total_prospects,
                         statuses=statuses,
                         search=search,
                         status_filter=status_filter,
                         page=page,
                         total_pages=total_pages,
                         per_page=per_page)

@app.route('/training-clients')
def training_clients_page():
    """Display all training clients with search and filtering."""
    conn = sqlite3.connect(db_manager.db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get search and filter parameters
    search = request.args.get('search', '')
    page = int(request.args.get('page', 1))
    per_page = 50
    
    # Build query with search
    where_conditions = []
    params = []
    
    if search:
        where_conditions.append("(member_name LIKE ? OR trainer_name LIKE ?)")
        search_term = f"%{search}%"
        params.extend([search_term, search_term])
    
    where_clause = ""
    if where_conditions:
        where_clause = "WHERE " + " AND ".join(where_conditions)
    
    # Get total count for pagination
    count_query = f"SELECT COUNT(*) FROM training_clients {where_clause}"
    cursor.execute(count_query, params)
    total_training_clients = cursor.fetchone()[0]
    
    # Calculate pagination
    total_pages = (total_training_clients + per_page - 1) // per_page
    offset = (page - 1) * per_page
    
    # Get training clients for current page
    query = f"""
        SELECT id, client_id, member_id, clubos_member_id, member_name, 
               trainer_name, session_type, sessions_remaining, last_session,
               agreement_name, agreement_expiration_date, created_at
        FROM training_clients {where_clause}
        ORDER BY created_at DESC 
        LIMIT ? OFFSET ?
    """
    cursor.execute(query, params + [per_page, offset])
    training_clients_data = cursor.fetchall()
    
    # Add funding status for each training client
    training_clients = []
    for client in training_clients_data:
        client_dict = dict(client)
        
        # Get funding status using the training package cache
        member_name = client['member_name']
        try:
            # Look up funding status for this training client
            funding_data = training_package_cache.lookup_participant_funding(member_name)
            if funding_data:
                client_dict['funding_status'] = funding_data.get('status_text', 'Unknown')
                client_dict['funding_status_class'] = funding_data.get('status_class', 'secondary')
                client_dict['funding_status_icon'] = funding_data.get('status_icon', 'fas fa-question-circle')
            else:
                # Also check if they're in the members table for payment status
                conn_member = sqlite3.connect(db_manager.db_path)
                cursor_member = conn_member.cursor()
                
                # Try to find them in members table by name
                name_parts = member_name.split()
                if len(name_parts) >= 2:
                    first_name = name_parts[0]
                    last_name = ' '.join(name_parts[1:])
                    
                    cursor_member.execute("""
                        SELECT amount_past_due, amount_of_next_payment, date_of_next_payment 
                        FROM members 
                        WHERE LOWER(first_name) = LOWER(?) AND LOWER(last_name) = LOWER(?)
                        LIMIT 1
                    """, (first_name, last_name))
                    
                    member_payment = cursor_member.fetchone()
                    if member_payment:
                        amount_past_due = member_payment[0] or 0
                        amount_next = member_payment[1] or 0
                        date_next = member_payment[2]
                        
                        if amount_past_due > 0:
                            client_dict['funding_status'] = f'Past Due: ${amount_past_due:.2f}'
                            client_dict['funding_status_class'] = 'danger'
                            client_dict['funding_status_icon'] = 'fas fa-exclamation-triangle'
                        elif date_next:
                            try:
                                next_payment_date = datetime.strptime(date_next, '%Y-%m-%d').date()
                                days_until = (next_payment_date - datetime.now().date()).days
                                if 0 <= days_until <= 7:
                                    client_dict['funding_status'] = f'Due in {days_until} days: ${amount_next:.2f}'
                                    client_dict['funding_status_class'] = 'warning'
                                    client_dict['funding_status_icon'] = 'fas fa-clock'
                                else:
                                    client_dict['funding_status'] = 'Current'
                                    client_dict['funding_status_class'] = 'success'
                                    client_dict['funding_status_icon'] = 'fas fa-check-circle'
                            except:
                                client_dict['funding_status'] = 'Current'
                                client_dict['funding_status_class'] = 'success'
                                client_dict['funding_status_icon'] = 'fas fa-check-circle'
                        else:
                            client_dict['funding_status'] = 'Current'
                            client_dict['funding_status_class'] = 'success'
                            client_dict['funding_status_icon'] = 'fas fa-check-circle'
                    else:
                        client_dict['funding_status'] = 'Unknown'
                        client_dict['funding_status_class'] = 'secondary'
                        client_dict['funding_status_icon'] = 'fas fa-question-circle'
                
                conn_member.close()
                
        except Exception as e:
            logger.warning(f"❌ Could not get funding status for {member_name}: {e}")
            client_dict['funding_status'] = 'Error'
            client_dict['funding_status_class'] = 'danger'
            client_dict['funding_status_icon'] = 'fas fa-exclamation-triangle'
        
        training_clients.append(client_dict)
    
    conn.close()
    
    return render_template('training_clients.html',
                         training_clients=training_clients,
                         total_training_clients=total_training_clients,
                         search=search,
                         page=page,
                         total_pages=total_pages,
                         per_page=per_page)

if __name__ == "__main__":
    print("🚀 Starting Clean Anytime Fitness Dashboard...")
    app.run(debug=True, host='0.0.0.0', port=5001)
