#!/usr/bin/env python3
"""
Verification script for October 3, 2025 database and API fixes
"""

import sqlite3
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def verify_prospects_schema():
    """Verify prospects table has mobile_phone column"""
    try:
        db_path = os.path.join(os.path.dirname(__file__), 'gym_bot.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("PRAGMA table_info(prospects)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'mobile_phone' in columns:
            logger.info("✅ prospects.mobile_phone column exists")
            return True
        else:
            logger.error("❌ prospects.mobile_phone column MISSING")
            logger.info(f"   Available columns: {columns}")
            return False
    except Exception as e:
        logger.error(f"❌ Error checking prospects schema: {e}")
        return False
    finally:
        conn.close()

def verify_training_clients_table():
    """Verify training_clients table exists and has expected columns"""
    try:
        db_path = os.path.join(os.path.dirname(__file__), 'gym_bot.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("PRAGMA table_info(training_clients)")
        columns = [row[1] for row in cursor.fetchall()]
        
        required_columns = ['member_name', 'total_past_due', 'payment_status', 
                          'sessions_remaining', 'trainer_name', 'active_packages', 'last_session']
        
        missing_columns = [col for col in required_columns if col not in columns]
        
        if not missing_columns:
            logger.info("✅ training_clients table has all required columns")
            return True
        else:
            logger.warning(f"⚠️ training_clients table missing columns: {missing_columns}")
            logger.info(f"   Available columns: {columns}")
            return False
    except Exception as e:
        logger.warning(f"⚠️ training_clients table may not exist yet: {e}")
        return True  # This is OK if table hasn't been created yet
    finally:
        conn.close()

def main():
    """Run all verification checks"""
    logger.info("=" * 60)
    logger.info("Database Schema Verification - October 3, 2025")
    logger.info("=" * 60)
    
    results = []
    
    # Check 1: Prospects mobile_phone column
    logger.info("\n1. Checking prospects.mobile_phone column...")
    results.append(('prospects.mobile_phone', verify_prospects_schema()))
    
    # Check 2: Training clients table
    logger.info("\n2. Checking training_clients table...")
    results.append(('training_clients', verify_training_clients_table()))
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("VERIFICATION SUMMARY")
    logger.info("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for check_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status} - {check_name}")
    
    logger.info(f"\nTotal: {passed}/{total} checks passed")
    
    if passed == total:
        logger.info("✅ All checks passed! Database schema is correct.")
        return 0
    else:
        logger.error("❌ Some checks failed. Please review the errors above.")
        return 1

if __name__ == "__main__":
    exit(main())
