#!/usr/bin/env python3
"""
Check for campaign and messaging related tables in the gym_bot.db database
"""

import sqlite3
import json
from datetime import datetime, timedelta

def check_campaign_tables():
    """Check what campaign/messaging tables exist and their contents"""
    
    try:
        conn = sqlite3.connect('gym_bot.db')
        cursor = conn.cursor()
        
        # Get all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        print("📋 All tables in gym_bot.db:")
        for table in sorted(tables):
            print(f"   - {table}")
        
        # Look for campaign/message related tables
        campaign_tables = [t for t in tables if any(keyword in t.lower() for keyword in 
                          ['campaign', 'message', 'sms', 'email', 'notification', 'bulk', 'checkin'])]
        
        print(f"\n🎯 Campaign/Message related tables ({len(campaign_tables)}):")
        for table in campaign_tables:
            print(f"   - {table}")
            
            # Get table schema
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()
            print(f"     Columns: {', '.join([col[1] for col in columns])}")
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"     Records: {count}")
            
            if count > 0 and count < 20:
                # Show sample data for small tables
                cursor.execute(f"SELECT * FROM {table} LIMIT 5")
                rows = cursor.fetchall()
                print(f"     Sample data:")
                for row in rows[:3]:
                    print(f"       {row}")
        
        # Check for any records from yesterday specifically
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        print(f"\n📅 Checking for records from {yesterday}...")
        
        for table in campaign_tables:
            cursor.execute(f"PRAGMA table_info({table})")
            columns = [col[1] for col in cursor.fetchall()]
            
            # Look for date/timestamp columns
            date_columns = [col for col in columns if any(keyword in col.lower() 
                          for keyword in ['date', 'time', 'created', 'updated', 'sent'])]
            
            if date_columns:
                for date_col in date_columns:
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE {date_col} LIKE ?", (f'%{yesterday}%',))
                        count = cursor.fetchone()[0]
                        if count > 0:
                            print(f"   ✅ {table}.{date_col}: {count} records from {yesterday}")
                            
                            # Show sample records from yesterday
                            cursor.execute(f"SELECT * FROM {table} WHERE {date_col} LIKE ? LIMIT 3", (f'%{yesterday}%',))
                            rows = cursor.fetchall()
                            for row in rows:
                                print(f"      {row}")
                    except Exception as e:
                        print(f"   ⚠️ Error checking {table}.{date_col}: {e}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error checking campaign tables: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Checking for campaign history in gym_bot.db...")
    check_campaign_tables()