#!/usr/bin/env python3
"""
Test ClubHub API for member search functionality
"""

from src.services.data.clubhub_api import EnhancedClubHubAPIService
from config.constants import CLUBHUB_API_URL_MEMBERS

def test_clubhub_member_search():
    """Test ClubHub API for member search"""
    print("🔍 Testing ClubHub API for member search...")
    
    try:
        # Initialize ClubHub API service
        clubhub_service = EnhancedClubHubAPIService()
        
        # Test parameters for member search
        params = {
            "recent": "true",
            "pageSize": "10",
            "page": "1"
        }
        
        print(f"📡 Fetching members from ClubHub API...")
        print(f"   URL: {CLUBHUB_API_URL_MEMBERS}")
        print(f"   Params: {params}")
        
        # Fetch members
        members = clubhub_service.fetch_clubhub_data(
            CLUBHUB_API_URL_MEMBERS,
            params,
            "members"
        )
        
        if members:
            print(f"✅ Successfully fetched {len(members)} members from ClubHub API")
            
            # Show first few members
            for i, member in enumerate(members[:3]):
                print(f"   Member {i+1}:")
                print(f"      Name: {member.get('firstName', 'N/A')} {member.get('lastName', 'N/A')}")
                print(f"      Email: {member.get('email', 'N/A')}")
                print(f"      Phone: {member.get('phone', 'N/A')}")
                print(f"      ID: {member.get('id', 'N/A')}")
                print()
            
            # Test searching for a specific member
            search_name = "Jeremy"
            print(f"🔍 Searching for members with name containing '{search_name}'...")
            
            matching_members = []
            for member in members:
                first_name = member.get('firstName', '').lower()
                last_name = member.get('lastName', '').lower()
                if search_name.lower() in first_name or search_name.lower() in last_name:
                    matching_members.append(member)
            
            if matching_members:
                print(f"✅ Found {len(matching_members)} matching members:")
                for member in matching_members:
                    print(f"   - {member.get('firstName', '')} {member.get('lastName', '')} (ID: {member.get('id', 'N/A')})")
            else:
                print(f"❌ No members found matching '{search_name}'")
            
            return True
        else:
            print("❌ No members returned from ClubHub API")
            return False
            
    except Exception as e:
        print(f"❌ Error testing ClubHub API: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_clubhub_member_search() 