#!/usr/bin/env python3
"""
Bulk Check-in Tracking Database Setup
Creates the necessary tables and functions for tracking bulk check-in operations
"""

import sqlite3
import json
import os
import sys
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def _get_db_path():
    """Get the correct database path - same logic as DatabaseManager"""
    if getattr(sys, 'frozen', False):
        # Running as compiled executable - use user's AppData
        db_dir = Path.home() / 'AppData' / 'Local' / 'GymBot' / 'data'
        db_dir.mkdir(parents=True, exist_ok=True)
        return str(db_dir / 'gym_bot.db')
    else:
        # Running as script - use project root
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        return os.path.join(project_root, 'gym_bot.db')


def _get_connection():
    """Get a database connection with proper settings"""
    db_path = _get_db_path()
    conn = sqlite3.connect(db_path, timeout=30.0)
    conn.row_factory = sqlite3.Row
    return conn


def setup_bulk_checkin_tracking_tables():
    """Create the necessary tables for bulk check-in tracking"""
    try:
        conn = _get_connection()
        cursor = conn.cursor()
        
        # Create bulk_checkin_runs table to track each bulk operation
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bulk_checkin_runs (
                run_id TEXT PRIMARY KEY,
                status TEXT NOT NULL, -- 'running', 'completed', 'failed', 'paused'
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP NULL,
                total_members INTEGER DEFAULT 0,
                processed_members INTEGER DEFAULT 0,
                successful_checkins INTEGER DEFAULT 0,
                failed_checkins INTEGER DEFAULT 0,
                excluded_ppv INTEGER DEFAULT 0,
                excluded_comp INTEGER DEFAULT 0,
                excluded_frozen INTEGER DEFAULT 0,
                current_member_name TEXT NULL,
                progress_percentage INTEGER DEFAULT 0,
                status_message TEXT NULL,
                error_message TEXT NULL,
                run_data TEXT NULL -- JSON data for additional tracking
            )
        ''')
        
        # Create member_checkins table to track individual check-ins
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS member_checkins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT NOT NULL,
                member_id TEXT NOT NULL,
                member_name TEXT NOT NULL,
                checkin_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                checkin_count INTEGER DEFAULT 1, -- How many check-ins (usually 2)
                success_count INTEGER DEFAULT 0, -- How many were successful
                status TEXT DEFAULT 'pending', -- 'pending', 'success', 'partial', 'failed'
                error_message TEXT NULL,
                FOREIGN KEY (run_id) REFERENCES bulk_checkin_runs(run_id)
            )
        ''')
        
        # Create index for faster queries
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_member_checkins_run_id ON member_checkins(run_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_member_checkins_member_id ON member_checkins(member_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_bulk_checkin_runs_status ON bulk_checkin_runs(status)')
        
        conn.commit()
        conn.close()
        
        print("✅ Bulk check-in tracking tables created successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error creating bulk check-in tracking tables: {e}")
        return False

def save_bulk_checkin_run(run_id, status, status_data, error_message=None):
    """Save or update a bulk check-in run record"""
    try:
        conn = _get_connection()
        cursor = conn.cursor()
        
        # Check if run already exists
        cursor.execute('SELECT run_id FROM bulk_checkin_runs WHERE run_id = ?', (run_id,))
        existing = cursor.fetchone()
        
        if existing:
            # Update existing run
            update_fields = []
            update_values = []
            
            # Always update status and timestamp
            update_fields.extend(['status = ?', 'completed_at = ?'])
            update_values.extend([status, datetime.now().isoformat() if status in ['completed', 'failed'] else None])
            
            # Update from status_data
            if 'total_members' in status_data:
                update_fields.append('total_members = ?')
                update_values.append(status_data['total_members'])
            if 'processed_members' in status_data:
                update_fields.append('processed_members = ?')
                update_values.append(status_data['processed_members'])
            if 'total_checkins' in status_data:
                update_fields.append('successful_checkins = ?')
                update_values.append(status_data['total_checkins'])
            if 'ppv_excluded' in status_data:
                update_fields.append('excluded_ppv = ?')
                update_values.append(status_data['ppv_excluded'])
            if 'comp_excluded' in status_data:
                update_fields.append('excluded_comp = ?')
                update_values.append(status_data['comp_excluded'])
            if 'frozen_excluded' in status_data:
                update_fields.append('excluded_frozen = ?')
                update_values.append(status_data['frozen_excluded'])
            if 'current_member' in status_data:
                update_fields.append('current_member_name = ?')
                update_values.append(status_data['current_member'])
            if 'progress' in status_data:
                update_fields.append('progress_percentage = ?')
                update_values.append(status_data['progress'])
            if 'message' in status_data:
                update_fields.append('status_message = ?')
                update_values.append(status_data['message'])
            
            if error_message:
                update_fields.append('error_message = ?')
                update_values.append(error_message)
                
            # Add run_data as JSON
            update_fields.append('run_data = ?')
            update_values.append(json.dumps(status_data))
            
            # Add run_id for WHERE clause
            update_values.append(run_id)
            
            sql = f"UPDATE bulk_checkin_runs SET {', '.join(update_fields)} WHERE run_id = ?"
            cursor.execute(sql, update_values)
            
        else:
            # Insert new run
            cursor.execute('''
                INSERT INTO bulk_checkin_runs (
                    run_id, status, started_at, total_members, processed_members, 
                    successful_checkins, excluded_ppv, excluded_comp, excluded_frozen,
                    current_member_name, progress_percentage, status_message, error_message, run_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                run_id,
                status,
                status_data.get('started_at', datetime.now().isoformat()),
                status_data.get('total_members', 0),
                status_data.get('processed_members', 0),
                status_data.get('total_checkins', 0),
                status_data.get('ppv_excluded', 0),
                status_data.get('comp_excluded', 0),
                status_data.get('frozen_excluded', 0),
                status_data.get('current_member', ''),
                status_data.get('progress', 0),
                status_data.get('message', ''),
                error_message,
                json.dumps(status_data)
            ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"✅ Saved bulk check-in run: {run_id} - {status}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error saving bulk check-in run {run_id}: {e}")
        return False

def load_bulk_checkin_resume_data(run_id):
    """Load resume data for a bulk check-in run"""
    try:
        conn = _get_connection()
        cursor = conn.cursor()
        
        # Get the run data
        cursor.execute('SELECT * FROM bulk_checkin_runs WHERE run_id = ?', (run_id,))
        run_data = cursor.fetchone()
        
        if not run_data:
            return None
            
        # Get processed members to know where to resume
        cursor.execute('''
            SELECT member_id, member_name, status 
            FROM member_checkins 
            WHERE run_id = ? AND status IN ('success', 'partial', 'failed')
            ORDER BY checkin_timestamp
        ''', (run_id,))
        
        processed_members = cursor.fetchall()
        conn.close()
        
        # Convert row to dict and add processed members
        resume_data = dict(run_data)
        resume_data['processed_members'] = len(processed_members)
        resume_data['processed_member_list'] = [dict(row) for row in processed_members]
        
        # Parse JSON data if available
        if run_data['run_data']:
            try:
                json_data = json.loads(run_data['run_data'])
                resume_data['status'] = json_data
            except:
                pass
        
        logger.info(f"✅ Loaded resume data for run {run_id}: {len(processed_members)} members processed")
        return resume_data
        
    except Exception as e:
        logger.error(f"❌ Error loading resume data for run {run_id}: {e}")
        return None

def log_member_checkin(run_id, member_id, member_name, checkin_count, success_count, status='pending', error_message=None):
    """Log an individual member check-in result"""
    try:
        conn = _get_connection()
        cursor = conn.cursor()
        
        # Check if this member already has a record for this run
        cursor.execute('''
            SELECT id FROM member_checkins 
            WHERE run_id = ? AND member_id = ?
        ''', (run_id, member_id))
        
        existing = cursor.fetchone()
        
        if existing:
            # Update existing record
            cursor.execute('''
                UPDATE member_checkins 
                SET checkin_count = ?, success_count = ?, status = ?, error_message = ?
                WHERE run_id = ? AND member_id = ?
            ''', (checkin_count, success_count, status, error_message, run_id, member_id))
        else:
            # Insert new record
            cursor.execute('''
                INSERT INTO member_checkins (
                    run_id, member_id, member_name, checkin_count, success_count, status, error_message
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (run_id, member_id, member_name, checkin_count, success_count, status, error_message))
        
        conn.commit()
        conn.close()
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error logging member check-in for {member_name}: {e}")
        return False

def get_bulk_checkin_history(limit=10):
    """Get bulk check-in run history"""
    try:
        conn = _get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM bulk_checkin_runs 
            ORDER BY started_at DESC 
            LIMIT ?
        ''', (limit,))
        
        runs = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in runs]
        
    except Exception as e:
        logger.error(f"❌ Error getting bulk check-in history: {e}")
        return []

def get_run_checkin_details(run_id):
    """Get detailed check-in results for a specific run"""
    try:
        conn = _get_connection()
        cursor = conn.cursor()
        
        # Get run info
        cursor.execute('SELECT * FROM bulk_checkin_runs WHERE run_id = ?', (run_id,))
        run_info = cursor.fetchone()
        
        # Get member check-ins - handle potential missing columns gracefully
        try:
            cursor.execute('''
                SELECT * FROM member_checkins 
                WHERE run_id = ? 
                ORDER BY id
            ''', (run_id,))
            checkins = cursor.fetchall()
        except Exception as db_error:
            logger.warning(f"⚠️ Error fetching member check-ins for run {run_id}: {db_error}")
            checkins = []
        
        conn.close()
        
        result = {
            'run_info': dict(run_info) if run_info else None,
            'member_checkins': [dict(row) for row in checkins] if checkins else []
        }
        
        logger.debug(f"📊 Retrieved details for run {run_id}: {len(checkins)} check-ins")
        return result
        
    except Exception as e:
        logger.error(f"❌ Error getting run check-in details: {e}")
        return None

def get_resumable_runs():
    """Get list of bulk check-in runs that can be resumed (interrupted or failed runs)."""
    try:
        conn = _get_connection()
        cursor = conn.cursor()
        
        # Get runs that were interrupted (not completed)
        cursor.execute("""
            SELECT run_id, started_at, total_members, processed_members, 
                   status, excluded_ppv, error_message, completed_at
            FROM bulk_checkin_runs 
            WHERE status IN ('running', 'processing', 'failed', 'resuming')
            ORDER BY started_at DESC
        """)
        
        resumable_runs = cursor.fetchall()
        
        result = []
        for run in resumable_runs:
            # Get check-in count for this run (sum of success_count from all members)
            cursor.execute("""
                SELECT COALESCE(SUM(success_count), 0) as total_successful
                FROM member_checkins 
                WHERE run_id = ?
            """, (run['run_id'],))
            checkin_result = cursor.fetchone()
            total_successful = checkin_result['total_successful'] if checkin_result else 0
            
            # Get processed member count for this run
            cursor.execute("""
                SELECT COUNT(DISTINCT member_id) as member_count
                FROM member_checkins 
                WHERE run_id = ?
            """, (run['run_id'],))
            member_result = cursor.fetchone()
            processed_member_count = member_result['member_count'] if member_result else 0
            
            result.append({
                'run_id': run['run_id'],
                'started_at': run['started_at'],
                'status': run['status'],
                'total_members': run['total_members'] or 0,
                'processed_members': processed_member_count,
                'successful_checkins': total_successful,
                'ppv_excluded': run['excluded_ppv'] or 0,
                'error': run['error_message'],
                'completed_at': run['completed_at'],
                'can_resume': run['status'] in ['running', 'processing', 'failed', 'resuming']
            })
        
        conn.close()
        
        logger.info(f"✅ Found {len(result)} resumable bulk check-in runs")
        return result
        
    except Exception as e:
        logger.error(f"❌ Error getting resumable runs: {e}")
        return []

if __name__ == "__main__":
    # Setup the tables when run directly
    setup_bulk_checkin_tracking_tables()