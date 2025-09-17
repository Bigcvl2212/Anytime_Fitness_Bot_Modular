#!/usr/bin/env python3

"""
Test script to fetch and examine agreement data structure from ClubHub API
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from services.api.clubhub_api_client import ClubHubAPIClient
from services.authentication.secure_secrets_manager import SecureSecretsManager
import json

def test_agreement_data():
    """Test fetching agreement data to see what fields are available"""
    
    print("🔍 Testing ClubHub Agreement Data Structure")
    print("=" * 50)
    
    try:
        # Initialize ClubHub client and authenticate
        clubhub_client = ClubHubAPIClient()
        
        # Get credentials
        secrets_manager = SecureSecretsManager()
        clubhub_email = secrets_manager.get_secret("clubhub-email")
        clubhub_password = secrets_manager.get_secret("clubhub-password")
        
        if not clubhub_client.authenticate(clubhub_email, clubhub_password):
            print("❌ ClubHub authentication failed")
            return
        
        print("✅ ClubHub authenticated successfully")
        
        # Get a sample member ID from the database
        import sqlite3
        conn = sqlite3.connect('gym_bot.db')
        cursor = conn.cursor()
        
        # Get a member with past due amount
        cursor.execute("""
            SELECT prospect_id, full_name, amount_past_due 
            FROM members 
            WHERE status_message LIKE '%Past Due%' 
            LIMIT 1
        """)
        
        member = cursor.fetchone()
        if not member:
            print("❌ No past due members found in database")
            return
        
        member_id, member_name, past_due = member
        print(f"📋 Testing with member: {member_name} (ID: {member_id}, Past Due: ${past_due})")
        
        # Fetch agreement data
        print(f"\n🔍 Fetching agreement data for member {member_id}...")
        agreement_data = clubhub_client.get_member_agreement(member_id)
        
        if agreement_data:
            print("✅ Agreement data retrieved successfully!")
            print(f"📊 Agreement data structure:")
            print(json.dumps(agreement_data, indent=2, default=str))
            
            # Look for agreement ID fields
            print(f"\n🔍 Looking for agreement ID fields:")
            for key, value in agreement_data.items():
                if 'id' in key.lower() or 'agreement' in key.lower():
                    print(f"   {key}: {value}")
            
            # Check if there's an agreement object
            if 'agreement' in agreement_data and isinstance(agreement_data['agreement'], dict):
                print(f"\n🔍 Agreement object fields:")
                for key, value in agreement_data['agreement'].items():
                    if 'id' in key.lower() or 'agreement' in key.lower():
                        print(f"   agreement.{key}: {value}")
        else:
            print("❌ No agreement data returned")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error testing agreement data: {e}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    test_agreement_data()
