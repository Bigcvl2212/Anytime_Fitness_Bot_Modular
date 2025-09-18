#!/usr/bin/env python3
"""
Check Unclassified Members
Find members without clear status classification in the database
"""

import sqlite3
import sys
import os

def check_unclassified_members():
    """Find members without clear status classification"""
    print("🔍 Checking Unclassified Members")
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
        
        # 1. Find members with NULL or empty status_message
        print("\n1. Members with NULL or empty status_message:")
        cursor.execute("""
            SELECT id, prospect_id, full_name, status_message, status, member_type
            FROM members 
            WHERE status_message IS NULL OR status_message = ''
            ORDER BY full_name
        """)
        
        null_members = cursor.fetchall()
        print(f"   Count: {len(null_members)}")
        
        if null_members:
            print("   Names:")
            for member in null_members[:20]:  # Show first 20
                name = member['full_name'] or 'No Name'
                status = member['status'] or 'No Status'
                member_type = member['member_type'] or 'No Type'
                print(f"   • {name} (Status: {status}, Type: {member_type})")
            
            if len(null_members) > 20:
                print(f"   ... and {len(null_members) - 20} more")
        
        # 2. Find members with unusual status messages (not the common ones)
        print("\n2. Members with unusual/unclear status messages:")
        
        # First get common status messages
        cursor.execute("""
            SELECT status_message, COUNT(*) as count
            FROM members 
            WHERE status_message IS NOT NULL AND status_message != ''
            GROUP BY status_message
            ORDER BY count DESC
        """)
        
        status_counts = cursor.fetchall()
        common_statuses = [row['status_message'] for row in status_counts if row['count'] >= 5]
        
        print(f"   Common status messages (5+ members): {len(common_statuses)}")
        for status in common_statuses:
            count = next(row['count'] for row in status_counts if row['status_message'] == status)
            print(f"   • '{status}' -> {count} members")
        
        # Now find members with uncommon status messages
        uncommon_placeholders = ', '.join(['?' for _ in common_statuses])
        if common_statuses:
            cursor.execute(f"""
                SELECT id, prospect_id, full_name, status_message, status
                FROM members 
                WHERE status_message IS NOT NULL 
                AND status_message != ''
                AND status_message NOT IN ({uncommon_placeholders})
                ORDER BY full_name
            """, common_statuses)
        else:
            cursor.execute("""
                SELECT id, prospect_id, full_name, status_message, status
                FROM members 
                WHERE status_message IS NOT NULL 
                AND status_message != ''
                ORDER BY full_name
            """)
        
        uncommon_members = cursor.fetchall()
        print(f"\n   Members with uncommon status messages: {len(uncommon_members)}")
        
        if uncommon_members:
            print("   Names and their status messages:")
            for member in uncommon_members:
                name = member['full_name'] or 'No Name'
                status_msg = member['status_message']
                status = member['status'] or 'No Status'
                print(f"   • {name} -> '{status_msg}' (Status: {status})")
        
        # 3. Summary of all unclassified members
        total_unclassified = len(null_members) + len(uncommon_members)
        print(f"\n3. Summary:")
        print(f"   • NULL/empty status_message: {len(null_members)}")
        print(f"   • Uncommon status messages: {len(uncommon_members)}")
        print(f"   • Total unclassified: {total_unclassified}")
        
        # 4. Check if any of these might be PPV members
        print(f"\n4. Checking if unclassified members might be PPV:")
        
        # Check member_type for PPV indicators
        all_unclassified_ids = [m['id'] for m in null_members] + [m['id'] for m in uncommon_members]
        
        if all_unclassified_ids:
            id_placeholders = ', '.join(['?' for _ in all_unclassified_ids])
            cursor.execute(f"""
                SELECT full_name, member_type, status, status_message
                FROM members 
                WHERE id IN ({id_placeholders})
                AND (member_type LIKE '%ppv%' OR member_type LIKE '%pay%' OR member_type LIKE '%visit%')
                ORDER BY full_name
            """, all_unclassified_ids)
            
            potential_ppv = cursor.fetchall()
            if potential_ppv:
                print(f"   Found {len(potential_ppv)} potentially PPV members:")
                for member in potential_ppv:
                    name = member['full_name'] or 'No Name'
                    member_type = member['member_type'] or 'No Type'
                    print(f"   • {name} (Type: {member_type})")
            else:
                print("   No obvious PPV indicators in member_type")
        
        conn.close()
        
        print(f"\n" + "=" * 50)
        print("📊 FINAL SUMMARY:")
        print(f"   • Total members without clear classification: {total_unclassified}")
        print(f"   • These might be additional PPV members or other categories")
        print(f"   • Current PPV detection finds 97 members")
        print(f"   • ClubHub reports 117 PPV members")
        print(f"   • Missing: {117 - 97} = 20 PPV members")
        
        if total_unclassified >= 20:
            print(f"   • ✅ We have {total_unclassified} unclassified members (>= 20 missing PPV)")
        else:
            print(f"   • ⚠️ Only {total_unclassified} unclassified members (< 20 missing PPV)")
        
    except Exception as e:
        print(f"❌ Error checking unclassified members: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_unclassified_members()