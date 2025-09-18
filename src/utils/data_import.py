#!/usr/bin/env python3
"""
Data Import Utilities
Handles ClubHub data import, member classification, and data processing
"""

import os
import sys
import logging
import json
import sqlite3
from datetime import datetime
from typing import Dict, Any, List, Optional
from flask import current_app

logger = logging.getLogger(__name__)

def classify_member_status(member_data: Dict[str, Any]) -> str:
    """Classify member status into categories based on status message and status."""
    try:
        # Ensure status_message and status are strings, handle None/NoneType values
        status_message = str(member_data.get('statusMessage', '')).lower()
        status = str(member_data.get('status', '')).lower()
        
        # Green members - active, good standing
        if any(green in status_message for green in ['active', 'good', 'current', 'active member']):
            return 'green'
        
        # Comp members - complimentary
        if any(comp in status_message for comp in ['comp', 'complimentary', 'free', 'no charge']):
            return 'comp'
        
        # PPV members - pay per visit
        if any(ppv in status_message for ppv in ['ppv', 'pay per visit', 'per visit', 'visit based']):
            return 'ppv'
        
        # Staff members
        if any(staff in status_message for staff in ['staff', 'employee', 'team member', 'coach']):
            return 'staff'
        
        # Past due members
        if any(past_due in status_message for past_due in ['past due', 'overdue', 'late', 'delinquent']):
            return 'past_due'
        
        # Inactive members
        if any(inactive in status_message for inactive in ['cancelled', 'cancel', 'expire', 'pending']):
            return 'inactive'
        
        # Default to green if no specific classification
        return 'green'
        
    except Exception as e:
        logger.error(f"❌ Error classifying member status: {e}")
        return 'unknown'

def import_fresh_clubhub_data():
    """Import fresh data from ClubHub API and classify members."""
    try:
        logger.info("🔄 Starting fresh ClubHub data import")
        
        # Import ClubHub API
        from src.services.api.clubhub_api_client import ClubHubAPIClient
        
        # Initialize API
        clubhub_api = ClubHubAPIClient()
        
        # Get fresh member data
        logger.info("📥 Fetching fresh member data from ClubHub")
        members_data = clubhub_api.get_all_members()
        
        if not members_data:
            logger.error("❌ No member data received from ClubHub")
            return False
        
        logger.info(f"📊 Received {len(members_data)} members from ClubHub")
        
        # Get database connection
        db_path = current_app.db_manager.db_path if current_app else 'gym_bot.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        try:
            # Clear existing member data
            cursor.execute("DELETE FROM members")
            cursor.execute("DELETE FROM member_categories")
            
            # Process and insert members
            member_count = 0
            category_counts = {
                'green': 0,
                'comp': 0,
                'ppv': 0,
                'staff': 0,
                'past_due': 0,
                'inactive': 0
            }
            
            for member_data in members_data:
                try:
                    # Extract member information
                    prospect_id = member_data.get('prospectID')
                    first_name = member_data.get('firstName', '')
                    last_name = member_data.get('lastName', '')
                    full_name = member_data.get('fullName', '') or f"{first_name} {last_name}".strip()
                    email = member_data.get('email', '')
                    phone = member_data.get('phone', '')
                    status = member_data.get('status', '')
                    status_message = member_data.get('statusMessage', '')
                    member_type = member_data.get('memberType', '')
                    join_date = member_data.get('joinDate', '')
                    amount_past_due = member_data.get('amountPastDue', 0)
                    date_of_next_payment = member_data.get('dateOfNextPayment', '')
                    
                    # Insert member
                    cursor.execute("""
                        INSERT INTO members (
                            prospect_id, first_name, last_name, full_name, email, phone,
                            status, status_message, member_type, join_date,
                            amount_past_due, date_of_next_payment, created_at, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        prospect_id, first_name, last_name, full_name, email, phone,
                        status, status_message, member_type, join_date,
                        amount_past_due, date_of_next_payment, datetime.now(), datetime.now()
                    ))
                    
                    # Classify member status
                    category = classify_member_status(member_data)
                    category_counts[category] = category_counts.get(category, 0) + 1
                    
                    # Insert category classification
                    cursor.execute("""
                        INSERT INTO member_categories (
                            member_id, category, status_message, status, created_at, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        prospect_id, category, status_message, status, datetime.now(), datetime.now()
                    ))
                    
                    member_count += 1
                    
                except Exception as e:
                    logger.error(f"❌ Error processing member {member_data.get('prospectID', 'Unknown')}: {e}")
                    continue
            
            # Create data_refresh_log table if it doesn't exist
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
                logger.info("🔧 Added missing category_breakdown column to data_refresh_log table")
            
            # Log the refresh with category breakdown
            category_breakdown = json.dumps(category_counts)
            cursor.execute("""
                INSERT INTO data_refresh_log 
                (id, table_name, last_refresh, record_count, category_breakdown)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    last_refresh = EXCLUDED.last_refresh,
                    record_count = EXCLUDED.record_count,
                    category_breakdown = EXCLUDED.category_breakdown
            """, (1, 'members', datetime.now(), member_count, category_breakdown))
            
            # Commit changes
            conn.commit()
            
            logger.info(f"✅ Fresh data imported: {member_count} members")
            logger.info(f"📊 Category breakdown: {category_counts}")
            
            # Apply staff designations after import to preserve staff status
            try:
                from src.utils.staff_designations import apply_staff_designations
                staff_success, staff_count, staff_message = apply_staff_designations(db_path)
                logger.info(f"🔄 Staff designation restoration: {staff_message}")
                category_counts['staff'] = staff_count  # Update staff count after restoration
            except Exception as e:
                logger.warning(f"⚠️ Failed to restore staff designations: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error during data import: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
            
    except Exception as e:
        logger.error(f"❌ Error importing fresh data: {e}")
        return False

def update_new_members_only():
    """Update database with only new members (incremental update)."""
    try:
        logger.info("🔄 Starting incremental member update")
        
        # Import ClubHub API
        from src.services.api.clubhub_api_client import ClubHubAPIClient
        
        # Initialize API
        clubhub_api = ClubHubAPIClient()
        
        # Get fresh member data
        members_data = clubhub_api.get_all_members()
        
        if not members_data:
            logger.warning("⚠️ No member data received from ClubHub")
            return False
        
        # Get database connection
        db_path = current_app.db_manager.db_path if current_app else 'gym_bot.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        try:
            new_members = 0
            updated_members = 0
            
            for member_data in members_data:
                try:
                    prospect_id = member_data.get('prospectID')
                    
                    # Check if member already exists
                    cursor.execute("SELECT prospect_id FROM members WHERE prospect_id = ?", (prospect_id,))
                    existing = cursor.fetchone()
                    
                    if existing:
                        # Update existing member
                        cursor.execute("""
                            UPDATE members SET
                                first_name = ?, last_name = ?, full_name = ?, email = ?, phone = ?,
                                status = ?, status_message = ?, member_type = ?, join_date = ?,
                                amount_past_due = ?, date_of_next_payment = ?, updated_at = ?
                            WHERE prospect_id = ?
                        """, (
                            member_data.get('firstName', ''),
                            member_data.get('lastName', ''),
                            member_data.get('fullName', '') or f"{member_data.get('firstName', '')} {member_data.get('lastName', '')}".strip(),
                            member_data.get('email', ''),
                            member_data.get('phone', ''),
                            member_data.get('status', ''),
                            member_data.get('statusMessage', ''),
                            member_data.get('memberType', ''),
                            member_data.get('joinDate', ''),
                            member_data.get('amountPastDue', 0),
                            member_data.get('dateOfNextPayment', ''),
                            datetime.now(),
                            prospect_id
                        ))
                        updated_members += 1
                    else:
                        # Insert new member
                        cursor.execute("""
                            INSERT INTO members (
                                prospect_id, first_name, last_name, full_name, email, phone,
                                status, status_message, member_type, join_date,
                                amount_past_due, date_of_next_payment, created_at, updated_at
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            prospect_id,
                            member_data.get('firstName', ''),
                            member_data.get('lastName', ''),
                            member_data.get('fullName', '') or f"{member_data.get('firstName', '')} {member_data.get('lastName', '')}".strip(),
                            member_data.get('email', ''),
                            member_data.get('phone', ''),
                            member_data.get('status', ''),
                            member_data.get('statusMessage', ''),
                            member_data.get('memberType', ''),
                            member_data.get('joinDate', ''),
                            member_data.get('amountPastDue', 0),
                            member_data.get('dateOfNextPayment', ''),
                            datetime.now(),
                            datetime.now()
                        ))
                        new_members += 1
                        
                        # Classify and insert category for new member
                        category = classify_member_status(member_data)
                        cursor.execute("""
                            INSERT INTO member_categories (
                                member_id, category, status_message, status, created_at, updated_at
                            ) VALUES (?, ?, ?, ?, ?, ?)
                        """, (
                            prospect_id, category, member_data.get('statusMessage', ''), 
                            member_data.get('status', ''), datetime.now(), datetime.now()
                        ))
                    
                except Exception as e:
                    logger.error(f"❌ Error processing member {member_data.get('prospectID', 'Unknown')}: {e}")
                    continue
            
            # Commit changes
            conn.commit()
            
            logger.info(f"✅ Incremental update completed: {new_members} new members, {updated_members} updated")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error during incremental update: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
            
    except Exception as e:
        logger.error(f"❌ Error during incremental member update: {e}")
        return False

def start_periodic_updates():
    """Start periodic background updates for new members."""
    try:
        import threading
        import time
        
        def periodic_update_worker():
            while True:
                try:
                    logger.info("🔄 Running periodic member update")
                    update_new_members_only()
                    
                    # Wait 6 hours before next update
                    time.sleep(21600)  # 6 hours in seconds
                    
                except Exception as e:
                    logger.error(f"❌ Periodic update failed: {e}")
                    # Wait 1 hour before retrying on error
                    time.sleep(3600)
        
        # Start background thread
        update_thread = threading.Thread(target=periodic_update_worker, daemon=True)
        update_thread.start()
        
        logger.info("✅ Periodic member updates started")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error starting periodic updates: {e}")
        return False
