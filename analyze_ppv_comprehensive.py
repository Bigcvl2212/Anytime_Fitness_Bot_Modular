#!/usr/bin/env python3
"""
Comprehensive PPV Member Analysis
Find all Pay Per Visit members with various status message patterns
"""

import sqlite3
import os

def analyze_ppv_patterns():
    """Comprehensive analysis of PPV member patterns"""
    db_path = os.path.join(os.getcwd(), 'gym_bot.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        print("🔍 Comprehensive PPV Member Analysis...")
        
        # Get all distinct status messages to find PPV patterns
        cursor.execute("""
            SELECT status_message, COUNT(*) as count 
            FROM members 
            WHERE status_message IS NOT NULL 
            AND status_message != ''
            GROUP BY status_message 
            ORDER BY count DESC
        """)
        
        all_statuses = cursor.fetchall()
        print(f"\n📊 All Status Messages ({len(all_statuses)} unique):")
        
        ppv_patterns = []
        total_ppv = 0
        
        for status in all_statuses:
            status_msg = status['status_message'].lower()
            count = status['count']
            
            # Check for various PPV patterns
            is_ppv = False
            if any(pattern in status_msg for pattern in [
                'pay per visit', 
                'ppv', 
                'day pass', 
                'guest pass', 
                'single visit',
                'one day',
                'daily pass',
                'visitor',
                'drop-in'
            ]):
                is_ppv = True
            
            if is_ppv:
                ppv_patterns.append((status['status_message'], count))
                total_ppv += count
                print(f"  🚫 PPV: '{status['status_message']}' = {count} members")
            else:
                print(f"  ✅ Non-PPV: '{status['status_message']}' = {count} members")
        
        print(f"\n🎯 PPV Pattern Summary:")
        print(f"Total PPV patterns found: {len(ppv_patterns)}")
        print(f"Total PPV members found: {total_ppv}")
        
        # If we don't have 117, let's look for other patterns
        if total_ppv != 117:
            print(f"\n🔍 Expected 117 PPV members, found {total_ppv}. Looking for additional patterns...")
            
            # Search for any status containing numbers or specific keywords that might indicate PPV
            cursor.execute("""
                SELECT status_message, COUNT(*) as count,
                       prospect_id, full_name, user_type, member_type, agreement_type
                FROM members 
                WHERE status_message IS NOT NULL 
                AND status_message != ''
                AND (
                    LOWER(status_message) LIKE '%visit%' OR
                    LOWER(status_message) LIKE '%day%' OR
                    LOWER(status_message) LIKE '%guest%' OR
                    LOWER(status_message) LIKE '%pass%' OR
                    LOWER(status_message) LIKE '%single%' OR
                    LOWER(status_message) LIKE '%drop%' OR
                    LOWER(status_message) LIKE '%temp%' OR
                    user_type = 3 OR
                    member_type LIKE '%PPV%' OR
                    agreement_type LIKE '%visit%'
                )
                GROUP BY status_message
                ORDER BY count DESC
            """)
            
            potential_ppv = cursor.fetchall()
            print(f"\n🔍 Potential PPV candidates ({len(potential_ppv)} patterns):")
            
            additional_ppv = 0
            for row in potential_ppv:
                if row['status_message'] not in [p[0] for p in ppv_patterns]:
                    print(f"  🤔 Potential: '{row['status_message']}' = {row['count']} members")
                    print(f"       user_type={row['user_type']}, member_type={row['member_type']}, agreement_type={row['agreement_type']}")
                    additional_ppv += row['count']
            
            print(f"\nAdditional potential PPV members: {additional_ppv}")
            print(f"Total potential PPV (original + additional): {total_ppv + additional_ppv}")
        
        # Check user_type column for PPV indicators
        print(f"\n🔍 Checking user_type patterns:")
        cursor.execute("""
            SELECT user_type, COUNT(*) as count 
            FROM members 
            WHERE user_type IS NOT NULL 
            GROUP BY user_type 
            ORDER BY count DESC
        """)
        
        user_types = cursor.fetchall()
        for ut in user_types:
            print(f"  user_type {ut['user_type']}: {ut['count']} members")
        
        # Check member_type and agreement_type columns
        print(f"\n🔍 Checking member_type patterns:")
        cursor.execute("""
            SELECT member_type, COUNT(*) as count 
            FROM members 
            WHERE member_type IS NOT NULL 
            GROUP BY member_type 
            ORDER BY count DESC
        """)
        
        member_types = cursor.fetchall()
        for mt in member_types:
            if mt['member_type']:
                print(f"  member_type '{mt['member_type']}': {mt['count']} members")
        
        print(f"\n🔍 Checking agreement_type patterns:")
        cursor.execute("""
            SELECT agreement_type, COUNT(*) as count 
            FROM members 
            WHERE agreement_type IS NOT NULL 
            GROUP BY agreement_type 
            ORDER BY count DESC
        """)
        
        agreement_types = cursor.fetchall()
        for at in agreement_types:
            if at['agreement_type']:
                print(f"  agreement_type '{at['agreement_type']}': {at['count']} members")
        
        # Final search: look for the exact count of 117 in any field
        print(f"\n🎯 Searching for field combinations that total 117...")
        
        # Check if user_type 3 gives us 117
        cursor.execute("SELECT COUNT(*) as count FROM members WHERE user_type = 3")
        ut3_count = cursor.fetchone()['count']
        print(f"user_type = 3: {ut3_count} members")
        
        if ut3_count == 117:
            print("🎯 FOUND IT! user_type = 3 gives exactly 117 members (PPV)")
        
        return {
            'ppv_patterns': ppv_patterns,
            'total_ppv': total_ppv,
            'user_type_3': ut3_count
        }
        
    except Exception as e:
        print(f"❌ Error analyzing PPV patterns: {e}")
        return None
    
    finally:
        conn.close()

if __name__ == "__main__":
    analyze_ppv_patterns()