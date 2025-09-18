#!/usr/bin/env python3
"""
Test script to verify expiring soon members are found correctly
"""

import sqlite3

def test_expiring_soon():
    """Test the expiring soon query logic"""
    print("🔍 Testing expiring soon members...")
    
    try:
        conn = sqlite3.connect('gym_bot.db')
        cursor = conn.cursor()
        
        # Test the exact query logic from the backend
        cursor.execute('''
            SELECT id, prospect_id, email, mobile_phone, full_name, status_message
            FROM members 
            WHERE status_message LIKE '%expire%' OR status_message = 'Expired'
            ORDER BY id
        ''')
        
        expiring_members = cursor.fetchall()
        print(f"📊 Found {len(expiring_members)} expiring members:")
        
        for member in expiring_members:
            print(f"  • ID: {member[0]} | Name: {member[4]} | Status: {member[5]}")
            print(f"    Email: {member[2] or 'None'} | Phone: {member[3] or 'None'}")
        
        # Also test what status messages we have that contain "expire"
        cursor.execute('''
            SELECT DISTINCT status_message, COUNT(*) 
            FROM members 
            WHERE status_message LIKE '%expire%' OR status_message = 'Expired'
            GROUP BY status_message
            ORDER BY COUNT(*) DESC
        ''')
        
        status_counts = cursor.fetchall()
        print(f"\n📋 Expiring status message patterns:")
        for status, count in status_counts:
            print(f"  • '{status}': {count} members")
        
        conn.close()
        return len(expiring_members)
        
    except Exception as e:
        print(f"❌ Error testing expiring soon members: {e}")
        return 0

if __name__ == "__main__":
    count = test_expiring_soon()
    print(f"\n✅ Total expiring members found: {count}")