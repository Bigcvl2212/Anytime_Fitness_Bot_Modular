#!/usr/bin/env python3
"""
Comprehensive PPV Member Analysis
Analyze all possible PPV status message variations to find all 117 PPV members
"""

import sqlite3
import sys
import os

def analyze_ppv_variations():
    """Analyze all PPV member status message variations"""
    print("🔍 Comprehensive PPV Member Analysis")
    print("=" * 50)
    
    # Connect to database
    db_path = os.path.join(os.getcwd(), 'gym_bot.db')
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return
        
    print(f"📂 Database: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 1. Find exact "Pay Per Visit Member" matches
        print("\n1. Exact 'Pay Per Visit Member' matches:")
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM members 
            WHERE status_message = 'Pay Per Visit Member'
        """)
        exact_count = cursor.fetchone()['count']
        print(f"   Exact matches: {exact_count}")
        
        # 2. Find all variations containing "pay per visit" (case insensitive)
        print("\n2. All 'pay per visit' variations (case insensitive):")
        cursor.execute("""
            SELECT DISTINCT status_message, COUNT(*) as count
            FROM members 
            WHERE LOWER(status_message) LIKE '%pay per visit%'
            GROUP BY status_message
            ORDER BY count DESC
        """)
        
        ppv_variations = cursor.fetchall()
        total_ppv_count = 0
        
        for row in ppv_variations:
            status = row['status_message']
            count = row['count']
            total_ppv_count += count
            print(f"   '{status}' -> {count} members")
        
        print(f"\n   Total PPV variations: {total_ppv_count}")
        
        # 3. Check for similar patterns that might be PPV
        print("\n3. Checking for similar PPV patterns:")
        ppv_patterns = [
            '%pay%per%visit%',
            '%ppv%',
            '%day pass%',
            '%daily%',
            '%visit%member%',
            '%per%visit%'
        ]
        
        all_similar = set()
        for pattern in ppv_patterns:
            cursor.execute("""
                SELECT DISTINCT status_message, COUNT(*) as count
                FROM members 
                WHERE LOWER(status_message) LIKE ?
                AND status_message IS NOT NULL
                GROUP BY status_message
            """, (pattern,))
            
            results = cursor.fetchall()
            for row in results:
                status = row['status_message']
                count = row['count']
                if status not in [r['status_message'] for r in ppv_variations]:
                    all_similar.add((status, count))
                    print(f"   Pattern '{pattern}': '{status}' -> {count}")
        
        # 4. Get all status_message values to check for missed patterns
        print("\n4. All unique status_message values (first 20):")
        cursor.execute("""
            SELECT status_message, COUNT(*) as count
            FROM members 
            WHERE status_message IS NOT NULL AND status_message != ''
            GROUP BY status_message
            ORDER BY count DESC
            LIMIT 20
        """)
        
        all_statuses = cursor.fetchall()
        print("   Top status messages:")
        for row in all_statuses:
            status = row['status_message']
            count = row['count']
            print(f"   '{status}' -> {count} members")
        
        # 5. Check if we have exactly 117 PPV members with exact match
        print(f"\n5. PPV Member Count Analysis:")
        print(f"   Target PPV count (from ClubHub): 117")
        print(f"   Found exact 'Pay Per Visit Member': {exact_count}")
        print(f"   Found all PPV variations: {total_ppv_count}")
        
        if exact_count == 117:
            print("   ✅ MATCH: Exact count matches target!")
        elif total_ppv_count == 117:
            print("   ✅ MATCH: Total variations match target!")
        else:
            print(f"   ❌ MISMATCH: Need to find {117 - total_ppv_count} more PPV members")
        
        # 6. Show sample PPV members for verification
        print(f"\n6. Sample PPV members (first 5):")
        cursor.execute("""
            SELECT id, prospect_id, full_name, status_message, status
            FROM members 
            WHERE LOWER(status_message) LIKE '%pay per visit%'
            LIMIT 5
        """)
        
        samples = cursor.fetchall()
        for row in samples:
            print(f"   ID: {row['id']}, Name: {row['full_name']}, Status: '{row['status_message']}'")
        
        # 7. Check member_type and other columns for PPV indicators
        print(f"\n7. Checking member_type column for PPV indicators:")
        cursor.execute("""
            SELECT DISTINCT member_type, COUNT(*) as count
            FROM members 
            WHERE member_type IS NOT NULL
            GROUP BY member_type
            ORDER BY count DESC
        """)
        
        member_types = cursor.fetchall()
        for row in member_types:
            mtype = row['member_type']
            count = row['count']
            if any(keyword in mtype.lower() for keyword in ['ppv', 'pay', 'visit', 'day'] if mtype):
                print(f"   '{mtype}' -> {count} members (potential PPV)")
            else:
                print(f"   '{mtype}' -> {count} members")
        
        conn.close()
        
        print(f"\n" + "=" * 50)
        print("📊 SUMMARY:")
        print(f"   • Exact 'Pay Per Visit Member': {exact_count}")
        print(f"   • All PPV variations: {total_ppv_count}")
        print(f"   • Target from ClubHub: 117")
        if exact_count == 117:
            print(f"   • ✅ Status: All PPV members found with exact match")
        else:
            print(f"   • ❌ Status: Missing {117 - exact_count} PPV members")
        
    except Exception as e:
        print(f"❌ Error analyzing PPV variations: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_ppv_variations()