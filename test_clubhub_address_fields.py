"""
Test script to see what address fields ClubHub API returns
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.services.api.clubhub_api_client import ClubHubAPIClient
import json

# Use direct credentials
clubhub_email = "mayo.jeremy2212@gmail.com"
clubhub_password = "SruLEqp464_GLrF"

# Initialize and authenticate
client = ClubHubAPIClient()
if client.authenticate(clubhub_email, clubhub_password):
    print("[OK] Authenticated with ClubHub\n")

    # Get first 3 members
    members = client.get_all_members()

    if members:
        print(f"[OK] Got {len(members)} members\n")
        print("=" * 80)
        print("CHECKING ADDRESS FIELDS IN API RESPONSE")
        print("=" * 80)
        
        for i, member in enumerate(members[:5], 1):
            name = f"{member.get('firstName', '')} {member.get('lastName', '')}".strip()
            print(f"\n{i}. {name}")
            print("-" * 80)
            
            # Check ALL possible address field names
            address_fields = {
                'address': member.get('address'),
                'address1': member.get('address1'),
                'address2': member.get('address2'),
                'streetAddress': member.get('streetAddress'),
                'street': member.get('street'),
                'city': member.get('city'),
                'state': member.get('state'),
                'zip': member.get('zip'),
                'zipCode': member.get('zipCode'),
                'postalCode': member.get('postalCode'),
            }
            
            has_address = False
            for field, value in address_fields.items():
                if value:
                    print(f"   [+] {field:20s} = {value}")
                    has_address = True
                else:
                    print(f"   [-] {field:20s} = None")

            if not has_address:
                print("\n   [!] NO ADDRESS FIELDS FOUND IN API RESPONSE!")
                
                # Show ALL fields returned for this member
                print("\n   ALL FIELDS RETURNED BY API:")
                for key in sorted(member.keys()):
                    value = member[key]
                    if isinstance(value, str) and len(value) > 50:
                        value = value[:50] + "..."
                    print(f"      {key}: {value}")
    else:
        print("[ERROR] No members returned")
else:
    print("[ERROR] Authentication failed")
