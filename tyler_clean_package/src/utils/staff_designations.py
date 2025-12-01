#!/usr/bin/env python3
"""
Staff Designation Utils
Utility functions for applying staff designations after ClubHub syncs
"""

import sqlite3
import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def apply_staff_designations(db_path=None):
    """
    Apply staff designations from staff_designations table to members table
    Call this function after ClubHub syncs to restore staff status
    
    Args:
        db_path (str): Optional database path. If None, uses default gym_bot.db
        
    Returns:
        tuple: (success: bool, applied_count: int, message: str)
    """
    
    if not db_path:
        # Navigate from src/utils/ back to project root (2 levels up)
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        db_path = os.path.join(project_root, 'gym_bot.db')
    
    if not os.path.exists(db_path):
        error_msg = f"Database not found at: {db_path}"
        logger.error(f"❌ {error_msg}")
        return False, 0, error_msg
    
    logger.info(f"🔄 Applying staff designations from staff_designations table...")
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Check if staff_designations table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='staff_designations'
        """)
        
        if not cursor.fetchone():
            logger.warning("⚠️ staff_designations table doesn't exist, skipping staff restoration")
            return True, 0, "staff_designations table not found"
        
        # Get active staff designations
        cursor.execute("""
            SELECT prospect_id, full_name, role
            FROM staff_designations 
            WHERE is_active = TRUE
        """)
        
        active_staff = cursor.fetchall()
        applied_count = 0
        
        logger.info(f"🔄 Applying staff status to {len(active_staff)} authorized members...")
        
        for staff in active_staff:
            prospect_id = staff['prospect_id']
            full_name = staff['full_name']
            
            # Check if member exists in members table
            cursor.execute("""
                SELECT full_name, status_message
                FROM members 
                WHERE prospect_id = ?
            """, (prospect_id,))
            
            member = cursor.fetchone()
            
            if member:
                current_status = member['status_message'] or ''
                
                # Determine new status based on current status
                if 'Staff Member' in current_status:
                    # Already has staff status, check if it needs member status too
                    if 'Member is in good standing' not in current_status:
                        new_status = 'Member is in good standing, Staff Member'
                    else:
                        new_status = current_status  # Already has both
                elif 'Member is in good standing' in current_status:
                    # Has member status, add staff
                    new_status = 'Member is in good standing, Staff Member'
                elif current_status and current_status.strip():
                    # Has other status, preserve and add staff
                    new_status = f'{current_status}, Staff Member'
                else:
                    # No status or empty, set to dual status
                    new_status = 'Member is in good standing, Staff Member'
                
                # Update member status if needed
                if new_status != current_status:
                    cursor.execute("""
                        UPDATE members 
                        SET status_message = ?,
                            updated_at = ?
                        WHERE prospect_id = ?
                    """, (new_status, datetime.now().isoformat(), prospect_id))
                    
                    if cursor.rowcount > 0:
                        logger.info(f"  ✅ Applied staff status to {full_name}: '{new_status}'")
                        applied_count += 1
                    else:
                        logger.warning(f"  ⚠️ Failed to update {full_name}")
                else:
                    logger.info(f"  ✅ {full_name} already has correct status: '{current_status}'")
                    applied_count += 1
            else:
                logger.warning(f"  ❌ Member {full_name} (ID: {prospect_id}) not found in members table")
        
        conn.commit()
        
        success_msg = f"Applied staff status to {applied_count}/{len(active_staff)} members"
        logger.info(f"✅ Staff designations applied successfully! {success_msg}")
        
        return True, applied_count, success_msg
        
    except Exception as e:
        error_msg = f"Error applying staff designations: {e}"
        logger.error(f"❌ {error_msg}")
        if 'conn' in locals():
            conn.rollback()
        return False, 0, error_msg
        
    finally:
        if 'conn' in locals():
            conn.close()

def get_staff_count():
    """
    Get current count of staff members
    
    Returns:
        int: Number of members with staff status
    """
    # Navigate from src/utils/ back to project root (2 levels up)
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    db_path = os.path.join(project_root, 'gym_bot.db')
    
    if not os.path.exists(db_path):
        return 0
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM members 
            WHERE status_message LIKE '%Staff%'
        """)
        
        result = cursor.fetchone()
        return result[0] if result else 0
        
    except Exception as e:
        logger.error(f"❌ Error getting staff count: {e}")
        return 0
        
    finally:
        if 'conn' in locals():
            conn.close()

def verify_staff_designations():
    """
    Verify that all authorized staff have correct dual status
    
    Returns:
        dict: Verification results with details
    """
    # Navigate from src/utils/ back to project root (2 levels up)
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    db_path = os.path.join(project_root, 'gym_bot.db')
    
    if not os.path.exists(db_path):
        return {'success': False, 'error': 'Database not found'}
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get authorized staff from staff_designations
        cursor.execute("""
            SELECT prospect_id, full_name, role
            FROM staff_designations 
            WHERE is_active = TRUE
        """)
        
        authorized_staff = cursor.fetchall()
        
        # Check their current status in members table
        verification_results = []
        all_correct = True
        
        for staff in authorized_staff:
            cursor.execute("""
                SELECT full_name, status_message
                FROM members 
                WHERE prospect_id = ?
            """, (staff['prospect_id'],))
            
            member = cursor.fetchone()
            
            if member:
                current_status = member['status_message'] or ''
                has_member_status = 'Member is in good standing' in current_status
                has_staff_status = 'Staff Member' in current_status
                is_correct = has_member_status and has_staff_status
                
                verification_results.append({
                    'name': staff['full_name'],
                    'prospect_id': staff['prospect_id'],
                    'current_status': current_status,
                    'has_member_status': has_member_status,
                    'has_staff_status': has_staff_status,
                    'is_correct': is_correct
                })
                
                if not is_correct:
                    all_correct = False
            else:
                verification_results.append({
                    'name': staff['full_name'],
                    'prospect_id': staff['prospect_id'],
                    'current_status': 'MEMBER NOT FOUND',
                    'has_member_status': False,
                    'has_staff_status': False,
                    'is_correct': False
                })
                all_correct = False
        
        return {
            'success': True,
            'all_correct': all_correct,
            'total_staff': len(authorized_staff),
            'results': verification_results
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e)}
        
    finally:
        if 'conn' in locals():
            conn.close()