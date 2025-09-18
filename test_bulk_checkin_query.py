#!/usr/bin/env python3
"""
Test Bulk Check-in Member Selection
Verify the updated query selects the right members and excludes PPV correctly
"""

import sqlite3
import os

def test_bulk_checkin_query():
    """Test the bulk check-in member selection query"""
    db_path = os.path.join(os.getcwd(), 'gym_bot.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        print("🔍 Testing bulk check-in member selection query...")
        
        # Current bulk check-in query - ALL members except PPV
        query = """
            SELECT prospect_id, first_name, last_name, full_name, status_message, 
                   user_type, member_type, agreement_type, status
            FROM members 
            WHERE status_message IS NOT NULL 
            AND status_message != ''
            AND status_message NOT LIKE 'Pay Per Visit%'
        """
        
        cursor.execute(query)
        selected_members = cursor.fetchall()
        
        print(f"\n📊 Bulk Check-in Query Results:")
        print(f"Total members selected for check-in: {len(selected_members)}")
        
        # Count by status for verification
        status_counts = {}
        ppv_found = 0
        
        for member in selected_members:
            status = member['status_message'] or 'Unknown'
            status_counts[status] = status_counts.get(status, 0) + 1
            
            # Check if any PPV members accidentally included
            if 'Pay Per Visit' in status or 'PPV' in status.upper():
                ppv_found += 1
                print(f"⚠️ PPV member found in selection: {member['full_name']} - Status: {status}")
        
        print(f"\n📋 Status Distribution of Selected Members:")
        for status, count in sorted(status_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {status}: {count} members")
        
        # Verify PPV exclusion
        print(f"\n🛡️ PPV Exclusion Check:")
        if ppv_found == 0:
            print("✅ No PPV members found in selection - fraud prevention working correctly")
        else:
            print(f"❌ {ppv_found} PPV members found in selection - query needs adjustment")
        
        # Check excluded PPV members
        ppv_query = """
            SELECT COUNT(*) as ppv_count
            FROM members 
            WHERE status_message LIKE 'Pay Per Visit%'
        """
        cursor.execute(ppv_query)
        ppv_excluded = cursor.fetchone()['ppv_count']
        
        print(f"🚫 PPV members excluded (fraud prevention): {ppv_excluded}")
        
        # Overall summary
        cursor.execute("SELECT COUNT(*) as total FROM members")
        total_members = cursor.fetchone()['total']
        
        print(f"\n🎯 Summary:")
        print(f"Total members in database: {total_members}")
        print(f"Members selected for check-in: {len(selected_members)}")
        print(f"PPV members excluded: {ppv_excluded}")
        print(f"Coverage: {len(selected_members)}/{total_members - ppv_excluded} eligible members")
        
        # Estimate check-ins (2 per member)
        estimated_checkins = len(selected_members) * 2
        print(f"Estimated total check-ins: {estimated_checkins}")
        
        return {
            'selected_count': len(selected_members),
            'ppv_excluded': ppv_excluded,
            'total_members': total_members,
            'estimated_checkins': estimated_checkins,
            'status_distribution': status_counts
        }
        
    except Exception as e:
        print(f"❌ Error testing query: {e}")
        return None
    
    finally:
        conn.close()

if __name__ == "__main__":
    test_bulk_checkin_query()