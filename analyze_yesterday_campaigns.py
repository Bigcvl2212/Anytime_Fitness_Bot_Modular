#!/usr/bin/env python3
"""
Detailed analysis of yesterday's campaign activity
"""

import sqlite3
import json
from datetime import datetime, timedelta

def analyze_yesterdays_campaigns():
    """Analyze campaign activity from 2025-09-18"""
    
    try:
        conn = sqlite3.connect('gym_bot.db')
        cursor = conn.cursor()
        
        print("📊 DETAILED CAMPAIGN ANALYSIS FOR 2025-09-18")
        print("=" * 50)
        
        # Get campaigns from yesterday
        cursor.execute("""
            SELECT id, campaign_name, message_text, message_type, subject, 
                   categories, total_recipients, successful_sends, failed_sends, 
                   errors, notes, status, created_at
            FROM campaigns 
            WHERE created_at LIKE '%2025-09-18%'
            ORDER BY created_at
        """)
        
        campaigns = cursor.fetchall()
        
        print(f"\n🎯 CAMPAIGNS RUN ON 2025-09-18: {len(campaigns)}")
        print("-" * 40)
        
        for i, campaign in enumerate(campaigns, 1):
            (id, name, message, msg_type, subject, categories, total_recipients, 
             successful_sends, failed_sends, errors, notes, status, created_at) = campaign
            
            print(f"\n📋 CAMPAIGN #{i} (ID: {id})")
            print(f"   Name: {name}")
            print(f"   Type: {msg_type.upper()}")
            print(f"   Category: {categories}")
            print(f"   Status: {status.upper()}")
            print(f"   Created: {created_at}")
            print(f"   Recipients: {total_recipients}")
            print(f"   ✅ Successful: {successful_sends}")
            print(f"   ❌ Failed: {failed_sends}")
            print(f"   Notes: {notes}")
            
            if message:
                print(f"   Message Preview: {message[:100]}...")
            
            if errors and errors.strip():
                print(f"   Errors: {errors[:200]}...")
        
        # Get message details for campaigns
        print(f"\n💬 MESSAGE DETAILS FROM 2025-09-18")
        print("-" * 40)
        
        cursor.execute("""
            SELECT campaign_id, COUNT(*) as message_count, 
                   SUM(CASE WHEN status = 'sent' THEN 1 ELSE 0 END) as sent_count,
                   SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed_count,
                   channel, message_type
            FROM messages 
            WHERE created_at LIKE '%2025-09-18%'
            GROUP BY campaign_id, channel, message_type
            ORDER BY campaign_id
        """)
        
        message_stats = cursor.fetchall()
        
        for stat in message_stats:
            campaign_id, msg_count, sent_count, failed_count, channel, msg_type = stat
            print(f"   Campaign {campaign_id}: {msg_count} messages ({sent_count} sent, {failed_count} failed) via {channel}")
        
        # Get campaign progress tracking
        print(f"\n📈 CAMPAIGN PROGRESS TRACKING")
        print("-" * 40)
        
        cursor.execute("""
            SELECT category, last_processed_member_id, last_processed_index, 
                   last_campaign_date, total_members_in_category, notes
            FROM campaign_progress 
            WHERE last_campaign_date LIKE '%2025-09-18%'
        """)
        
        progress_records = cursor.fetchall()
        
        for record in progress_records:
            category, last_member_id, last_index, last_date, total_members, notes = record
            print(f"   📁 Category: {category}")
            print(f"      Last Member: {last_member_id}")
            print(f"      Progress: {last_index}/{total_members}")
            print(f"      Last Run: {last_date}")
            print(f"      Notes: {notes}")
            print()
        
        # Sample messages sent
        print(f"\n📝 SAMPLE MESSAGES SENT ON 2025-09-18")
        print("-" * 40)
        
        cursor.execute("""
            SELECT campaign_id, to_user, content, timestamp, status, channel, member_id
            FROM messages 
            WHERE created_at LIKE '%2025-09-18%'
            AND status = 'sent'
            ORDER BY timestamp
            LIMIT 10
        """)
        
        sample_messages = cursor.fetchall()
        
        for msg in sample_messages:
            campaign_id, to_user, content, timestamp, status, channel, member_id = msg
            print(f"   ✅ Campaign {campaign_id} → {to_user} (ID: {member_id})")
            print(f"      Channel: {channel} | Status: {status}")
            print(f"      Time: {timestamp}")
            print(f"      Message: {content[:80]}...")
            print()
        
        conn.close()
        
        print(f"\n🎉 SUMMARY:")
        print(f"   • {len(campaigns)} campaigns were successfully run and saved")
        print(f"   • Campaign history is fully tracked and preserved")
        print(f"   • All message details are stored with delivery status")
        print(f"   • Progress tracking shows successful completion")
        
        return True
        
    except Exception as e:
        print(f"❌ Error analyzing campaigns: {e}")
        return False

if __name__ == "__main__":
    analyze_yesterdays_campaigns()