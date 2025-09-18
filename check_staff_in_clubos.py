#!/usr/bin/env python3
"""
Check ClubOS for all people with "Staff Member" status to determine if they're active or inactive
"""

import sys
import os
import time

# Add the src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from services.api.clubhub_api_client import ClubHubAPIClient
from services.authentication.secure_secrets_manager import SecureSecretsManager
import sqlite3

def check_staff_members_in_clubos():
    """Check all Staff Member status people in ClubOS to categorize them properly"""
    print("🔍 Checking Staff Member status people in ClubOS...")
    print("=" * 60)
    
    # Get the list of people with Staff Member status from database
    conn = sqlite3.connect('gym_bot.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT first_name, last_name, prospect_id, email, status_message
        FROM members 
        WHERE status_message IN ('Staff Member', 'Staff member')
        AND prospect_id NOT IN ('64309309', '55867562', '50909888', '62716557', '52750389')
        ORDER BY first_name, last_name
    """)
    
    staff_status_people = cursor.fetchall()
    conn.close()
    
    print(f"Found {len(staff_status_people)} people with 'Staff Member' status (excluding real staff)")
    print("\nChecking each person in ClubOS...")
    
    # Initialize ClubHub API client
    try:
        secrets_manager = SecureSecretsManager()
        clubhub_email = secrets_manager.get_secret('clubhub-email')
        clubhub_password = secrets_manager.get_secret('clubhub-password')
        
        if not clubhub_email or not clubhub_password:
            print("❌ ClubHub credentials not found")
            return
        
        client = ClubHubAPIClient()
        if not client.authenticate(clubhub_email, clubhub_password):
            print("❌ ClubHub authentication failed")
            return
        
    except Exception as e:
        print(f"❌ Error setting up ClubOS client: {e}")
        return
    
    active_members = []
    inactive_members = []
    
    for i, person in enumerate(staff_status_people, 1):
        first_name, last_name, prospect_id, email, status_message = person
        full_name = f"{first_name} {last_name}"
        
        print(f"\n{i:2d}. Checking {full_name} (ID: {prospect_id})...")
        
        try:
            # Search for this person in ClubOS
            search_results = client.search_members_by_name(f"{first_name} {last_name}")
            
            # Also try searching by prospect_id if name search fails
            if not search_results and prospect_id:
                member_data = client.get_member_by_id(prospect_id)
                if member_data:
                    search_results = [member_data]
            
            if search_results and len(search_results) > 0:
                # Found in ClubOS - they're active
                member_info = search_results[0]
                clubos_status = member_info.get('status', 'Unknown')
                clubos_status_message = member_info.get('statusMessage', 'Unknown')
                
                print(f"    ✅ ACTIVE in ClubOS - Status: {clubos_status_message}")
                active_members.append({
                    'name': full_name,
                    'prospect_id': prospect_id,
                    'email': email,
                    'db_status': status_message,
                    'clubos_status': clubos_status_message
                })
            else:
                # Not found in ClubOS - they're inactive
                print(f"    ❌ INACTIVE (not found in ClubOS)")
                inactive_members.append({
                    'name': full_name,
                    'prospect_id': prospect_id,
                    'email': email,
                    'db_status': status_message
                })
                
            # Small delay to avoid rate limiting
            time.sleep(0.5)
            
        except Exception as e:
            print(f"    ⚠️ Error checking {full_name}: {e}")
            # If we can't check, assume inactive for safety
            inactive_members.append({
                'name': full_name,
                'prospect_id': prospect_id,
                'email': email,
                'db_status': status_message,
                'error': str(e)
            })
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 RESULTS SUMMARY:")
    print("=" * 60)
    
    print(f"\n✅ ACTIVE MEMBERS (should be GREEN): {len(active_members)}")
    for member in active_members:
        print(f"  • {member['name']} - ClubOS Status: {member['clubos_status']}")
    
    print(f"\n❌ INACTIVE MEMBERS (should be INACTIVE): {len(inactive_members)}")
    for member in inactive_members:
        error_info = f" (Error: {member.get('error', 'Not found')})" if member.get('error') else ""
        print(f"  • {member['name']}{error_info}")
    
    print(f"\n🎯 RECOMMENDATIONS:")
    print(f"   - Move {len(active_members)} people to GREEN category")
    print(f"   - Move {len(inactive_members)} people to INACTIVE category")
    print(f"   - Keep only 5 real staff in STAFF category")
    
    return active_members, inactive_members

if __name__ == '__main__':
    check_staff_members_in_clubos()