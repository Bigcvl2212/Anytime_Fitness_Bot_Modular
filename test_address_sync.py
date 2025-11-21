"""
Quick test to see ClubHub address fields and trigger a fresh sync
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.services.api.clubhub_api_client import ClubHubAPIClient
from src.services.database_manager import DatabaseManager

# Direct credentials
clubhub_email = "mayo.jeremy2212@gmail.com"
clubhub_password = "SruLEqp464_GLrF"

print("=" * 80)
print("CLUBHUB ADDRESS FIELD TEST & SYNC")
print("=" * 80)

# Initialize and authenticate
client = ClubHubAPIClient()
print("\n🔐 Authenticating with ClubHub...")

if client.authenticate(clubhub_email, clubhub_password):
    print("✅ Authenticated successfully!\n")
    
    # Get first 5 members to check address fields
    print("📡 Fetching members from ClubHub API...")
    members = client.get_all_members_paginated()
    
    if members:
        print(f"✅ Got {len(members)} total members\n")
        print("=" * 80)
        print("CHECKING FIRST 5 MEMBERS FOR ADDRESS DATA")
        print("=" * 80)
        
        address_count = 0
        for i, member in enumerate(members[:5], 1):
            name = f"{member.get('firstName', '')} {member.get('lastName', '')}".strip()
            address1 = member.get('address1')
            city = member.get('city')
            state = member.get('state')
            zip_code = member.get('zip')
            
            print(f"\n{i}. {name}")
            print(f"   address1: {address1 or 'None'}")
            print(f"   city:     {city or 'None'}")
            print(f"   state:    {state or 'None'}")
            print(f"   zip:      {zip_code or 'None'}")
            
            if address1:
                address_count += 1
        
        print("\n" + "=" * 80)
        print(f"ADDRESS SUMMARY: {address_count}/5 members have street addresses")
        print("=" * 80)
        
        # Now save these members to database
        print("\n💾 Saving members to database...")
        db = DatabaseManager()
        
        # Process members to add required fields
        for member in members:
            member['full_name'] = f"{member.get('firstName', '')} {member.get('lastName', '')}".strip()
            member['first_name'] = member.get('firstName')
            member['last_name'] = member.get('lastName')
            member['address'] = member.get('address1') or member.get('address')
            member['city'] = member.get('city')
            member['state'] = member.get('state')
            member['zip_code'] = member.get('zip') or member.get('zipCode')
            member['phone'] = member.get('homePhone') or member.get('phone')
            member['mobile_phone'] = member.get('mobilePhone')
            member['email'] = member.get('email')
            member['prospect_id'] = str(member.get('id'))
            
            # Add default billing fields if missing
            if 'amount_past_due' not in member:
                member['amount_past_due'] = 0.0
            if 'agreement_recurring_cost' not in member:
                member['agreement_recurring_cost'] = 0.0
        
        success = db.save_members_to_db(members)
        
        if success:
            print(f"✅ Successfully saved {len(members)} members to database!")
            
            # Verify addresses were saved
            print("\n🔍 Verifying addresses in database...")
            import sqlite3
            conn = sqlite3.connect('gym_bot.db')
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN address IS NOT NULL AND address != '' THEN 1 ELSE 0 END) as with_address
                FROM members
            """)
            stats = cursor.fetchone()
            conn.close()
            
            print(f"   Total members: {stats[0]}")
            print(f"   With addresses: {stats[1]} ({stats[1]/stats[0]*100:.1f}%)")
            
            if stats[1] > 0:
                print("\n🎉 SUCCESS! Addresses are now in the database!")
            else:
                print("\n❌ WARNING: No addresses saved to database")
        else:
            print("❌ Failed to save members to database")
    else:
        print("❌ No members returned from API")
else:
    print("❌ Authentication failed")
