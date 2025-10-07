"""
Debug script to see what fields ClubHub actually returns for members
"""
import json
from src.services.api.clubhub_api_client import ClubHubAPIClient

# Initialize ClubHub client
client = ClubHubAPIClient()

# Get first 5 members
print("Fetching members from ClubHub API...")
all_members = client.get_all_members()
response = {'results': all_members[:5] if all_members else []}

if response and 'results' in response:
    members = response['results']
    print(f"\n✅ Got {len(members)} members\n")
    
    if members:
        # Show all fields from first member
        first_member = members[0]
        print("=" * 80)
        print(f"FIRST MEMBER: {first_member.get('firstName')} {first_member.get('lastName')}")
        print("=" * 80)
        print("\nALL AVAILABLE FIELDS:")
        print("-" * 80)
        
        for key in sorted(first_member.keys()):
            value = first_member[key]
            # Truncate long values
            if isinstance(value, str) and len(value) > 50:
                value = value[:50] + "..."
            print(f"{key:25s} = {value}")
        
        print("\n" + "=" * 80)
        print("ADDRESS-RELATED FIELDS:")
        print("=" * 80)
        
        address_fields = {
            'address': first_member.get('address'),
            'address1': first_member.get('address1'),
            'address2': first_member.get('address2'),
            'streetAddress': first_member.get('streetAddress'),
            'street': first_member.get('street'),
            'city': first_member.get('city'),
            'state': first_member.get('state'),
            'zip': first_member.get('zip'),
            'zipCode': first_member.get('zipCode'),
            'postalCode': first_member.get('postalCode'),
        }
        
        for field, value in address_fields.items():
            status = "✅" if value else "❌"
            print(f"{status} {field:20s} = {value}")
        
        # Check a few more members
        print("\n" + "=" * 80)
        print("ADDRESS DATA FOR ALL 5 MEMBERS:")
        print("=" * 80)
        
        for i, member in enumerate(members, 1):
            name = f"{member.get('firstName', 'Unknown')} {member.get('lastName', 'Unknown')}"
            addr = member.get('address1') or member.get('address') or member.get('streetAddress')
            city = member.get('city')
            state = member.get('state')
            zip_code = member.get('zip') or member.get('zipCode')
            
            print(f"\n{i}. {name}")
            print(f"   Address: {addr or 'NO ADDRESS'}")
            print(f"   City: {city or 'NO CITY'}, State: {state or 'NO STATE'}, Zip: {zip_code or 'NO ZIP'}")
else:
    print("❌ Failed to fetch members from ClubHub API")
    print(f"Response: {response}")
