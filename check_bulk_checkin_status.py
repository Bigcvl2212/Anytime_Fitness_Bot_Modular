#!/usr/bin/env python3
"""
Check bulk check-in status and analyze missing check-ins
"""

import sqlite3
import json
from datetime import datetime

def check_bulk_checkin_status():
    conn = sqlite3.connect('gym_bot.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    print('🔍 === Database Tables ===')
    cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
    tables = cursor.fetchall()
    for table in tables:
        print(f'  - {table["name"]}')

    print('\n📋 === bulk_checkin_runs schema ===')
    cursor.execute('PRAGMA table_info(bulk_checkin_runs)')
    columns = cursor.fetchall()
    for col in columns:
        print(f'  {col["name"]} ({col["type"]})')

    print('\n🎯 === Latest Bulk Check-in Run ===')
    cursor.execute('''
    SELECT * FROM bulk_checkin_runs 
    ORDER BY started_at DESC 
    LIMIT 1
    ''')
    run = cursor.fetchone()
    
    if run:
        print(f'Run ID: {run["run_id"]}')
        print(f'Total Members: {run["total_members"]}')
        print(f'Processed Members: {run["processed_members"]}')
        print(f'Successful Check-ins: {run["successful_checkins"]}')
        print(f'Failed Check-ins: {run["failed_checkins"]}')
        print(f'PPV Excluded: {run["excluded_ppv"]}')
        print(f'Comp Excluded: {run["excluded_comp"]}')
        print(f'Frozen Excluded: {run["excluded_frozen"]}')
        print(f'Started At: {run["started_at"]}')
        print(f'Completed At: {run["completed_at"]}')
        print(f'Status: {run["status"]}')
        print(f'Progress: {run["progress_percentage"]}%')
        print(f'Current Member: {run["current_member_name"]}')
        print(f'Status Message: {run["status_message"]}')
        
        run_id = run["run_id"]
        
        print('\n📊 === Check-in Details for Latest Run ===')
        cursor.execute('''
        SELECT status, COUNT(*) as count 
        FROM member_checkins 
        WHERE run_id = ? 
        GROUP BY status
        ''', (run_id,))
        
        status_counts = {}
        for status_row in cursor.fetchall():
            status = status_row["status"]
            count = status_row["count"]
            status_counts[status] = count
            print(f'  {status}: {count}')
            
        print('\n❌ === Sample Failed Check-ins ===')
        cursor.execute('''
        SELECT member_id, error_message 
        FROM member_checkins 
        WHERE run_id = ? AND status = "failed"
        LIMIT 10
        ''', (run_id,))
        
        failed_checkins = cursor.fetchall()
        if failed_checkins:
            for fail_row in failed_checkins:
                print(f'  Member {fail_row["member_id"]}: {fail_row["error_message"]}')
        else:
            print('  No failed check-ins found')
            
        print('\n✅ === Sample Successful Check-ins ===')
        cursor.execute('''
        SELECT member_id, checkin_timestamp 
        FROM member_checkins 
        WHERE run_id = ? AND status = "successful"
        LIMIT 5
        ''', (run_id,))
        
        success_checkins = cursor.fetchall()
        for success_row in success_checkins:
            print(f'  Member {success_row["member_id"]}: {success_row["checkin_timestamp"]}')
            
        print('\n🔢 === Summary ===')
        total_processed = sum(status_counts.values())
        successful = status_counts.get('completed', 0) + status_counts.get('successful', 0)
        failed = status_counts.get('failed', 0)
        skipped = status_counts.get('skipped', 0)
        ppv_excluded = status_counts.get('ppv_excluded', 0)
        
        print(f'  Total Processed: {total_processed}')
        print(f'  Successful Check-ins: {successful}')
        print(f'  Failed Check-ins: {failed}')
        print(f'  Skipped: {skipped}')
        print(f'  PPV Excluded: {ppv_excluded}')
        
        # Compare with total member counts
        print(f'\n🧮 === Member Analysis ===')
        cursor.execute('SELECT COUNT(*) as total FROM members')
        total_members_db = cursor.fetchone()['total']
        
        cursor.execute('SELECT COUNT(*) as ppv_count FROM members WHERE status_message LIKE "%Pay Per Visit%"')
        ppv_members_db = cursor.fetchone()['ppv_count'] 
        
        expected_eligible = total_members_db - ppv_members_db
        
        print(f'  Total Members in DB: {total_members_db}')
        print(f'  PPV Members in DB: {ppv_members_db}')
        print(f'  Expected Eligible: {expected_eligible}')
        print(f'  Actually Processed: {run["processed_members"]}')
        
        if run["processed_members"] < expected_eligible:
            missing = expected_eligible - run["processed_members"]
            print(f'\n⚠️  MISSING MEMBERS: {missing} members were NOT processed!')
            print(f'     Expected ~{expected_eligible}, but only got {run["processed_members"]}')
        else:
            print(f'\n✅ All eligible members were processed')
            
    else:
        print('No bulk check-in runs found')

    conn.close()

if __name__ == "__main__":
    check_bulk_checkin_status()