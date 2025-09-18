#!/usr/bin/env python3
"""
Fix Bulk Check-in Member Categories
Update the bulk check-in to match the exact ClubHub categories and fix PPV exclusion
"""

import sqlite3
import os

def analyze_member_categories():
    """Analyze current database vs ClubHub categories"""
    db_path = os.path.join(os.getcwd(), 'gym_bot.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        print("🔍 Analyzing member categories vs ClubHub data...")
        print("\n📊 ClubHub Target Categories:")
        print("   304 green (active)")
        print("   27 yellow (multiple status types)")
        print("   13 red (multiple status types)")
        print("   3 frozen")
        print("   31 complimentary")
        print("   117 PPV (Pay Per Visit) ← EXCLUDE from bulk check-in")
        print("   5 staff")
        print("   Total: 500 members")
        
        # Check current database categories
        cursor.execute("""
            SELECT status_message, COUNT(*) as count 
            FROM members 
            WHERE status_message IS NOT NULL AND status_message != ''
            GROUP BY status_message 
            ORDER BY count DESC
        """)
        
        db_categories = cursor.fetchall()
        print(f"\n📋 Current Database Categories:")
        
        total_in_db = 0
        ppv_count = 0
        good_standing = 0
        comp_count = 0
        staff_count = 0
        
        for cat in db_categories:
            status = cat['status_message']
            count = cat['count']
            total_in_db += count
            
            if 'Pay Per Visit' in status:
                ppv_count += count
                print(f"   🚫 PPV: '{status}' = {count} members")
            elif 'Member is in good standing' == status:
                good_standing += count
                print(f"   ✅ Active: '{status}' = {count} members")
            elif 'Comp Member' in status:
                comp_count += count
                print(f"   🎁 Comp: '{status}' = {count} members")
            elif 'Staff Member' in status:
                staff_count += count
                print(f"   👨‍💼 Staff: '{status}' = {count} members")
            else:
                print(f"   ❓ Other: '{status}' = {count} members")
        
        print(f"\n🎯 Analysis:")
        print(f"Database total with status: {total_in_db}")
        print(f"ClubHub target total: 500")
        print(f"Difference: {total_in_db - 500} (likely inactive/cancelled members)")
        
        print(f"\n📊 Key Categories Comparison:")
        print(f"PPV Members - DB: {ppv_count}, ClubHub: 117, Match: {'✅' if ppv_count == 117 else '❌'}")
        print(f"Good Standing - DB: {good_standing}, ClubHub: 304, Match: {'✅' if good_standing == 304 else '❌'}")
        print(f"Comp Members - DB: {comp_count}, ClubHub: 31, Match: {'✅' if comp_count == 31 else '❌'}")
        print(f"Staff Members - DB: {staff_count}, ClubHub: 5, Match: {'✅' if staff_count == 5 else '❌'}")
        
        # Calculate bulk check-in eligible members
        eligible_for_checkin = total_in_db - ppv_count
        print(f"\n🎯 Bulk Check-in Calculation:")
        print(f"Total members with status: {total_in_db}")
        print(f"PPV to exclude: {ppv_count}")
        print(f"Eligible for check-in: {eligible_for_checkin}")
        print(f"Expected ClubHub eligible: {500 - 117} = 383")
        
        if eligible_for_checkin > 383:
            excess = eligible_for_checkin - 383
            print(f"⚠️  Database has {excess} extra members (likely inactive/cancelled)")
            print("💡 Solution: Update query to match only active ClubHub members")
        
        # Check for members without status_message
        cursor.execute("SELECT COUNT(*) as null_count FROM members WHERE status_message IS NULL OR status_message = ''")
        null_count = cursor.fetchone()['null_count']
        
        if null_count > 0:
            print(f"\n📝 Additional Info:")
            print(f"Members with NULL/empty status: {null_count}")
            if null_count == 20:  # 117 - 97 = 20
                print("💡 These might be additional PPV members")
        
        conn.close()
        return {
            'db_total': total_in_db,
            'ppv_count': ppv_count,
            'eligible_count': eligible_for_checkin,
            'target_eligible': 383
        }
        
    except Exception as e:
        print(f"❌ Error analyzing categories: {e}")
        return None

def suggest_bulk_checkin_fix():
    """Suggest the correct bulk check-in query"""
    print(f"\n🔧 Recommended Bulk Check-in Query Update:")
    print(f"Current query selects ALL members except PPV, but includes inactive members.")
    print(f"Updated query should match ClubHub's 500 active members exactly.")
    
    print(f"\n📝 Updated Query Options:")
    print(f"Option 1: Exclude specific inactive statuses:")
    print(f"   AND status_message NOT LIKE '%cancelled%'")
    print(f"   AND status_message NOT LIKE '%expired%'")
    print(f"   AND status_message NOT LIKE '%inactive%'")
    
    print(f"\nOption 2: Include only known active statuses:")
    print(f"   WHERE status_message IN (")
    print(f"     'Member is in good standing',")
    print(f"     'Comp Member',")
    print(f"     'Staff Member',")
    print(f"     'Past Due more than 30 days.',")
    print(f"     'Past Due 6-30 days',")
    print(f"     'Member will expire within 30 days.',")
    print(f"     'Member is pending cancel',")
    print(f"     'Invalid/Bad Address information.',")
    print(f"     'Invalid Billing Information.'")
    print(f"   )")

if __name__ == "__main__":
    result = analyze_member_categories()
    if result:
        suggest_bulk_checkin_fix()