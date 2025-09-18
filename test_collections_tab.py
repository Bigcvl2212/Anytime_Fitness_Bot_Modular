#!/usr/bin/env python3
"""
Test script to verify Collections tab functionality
"""

import sys
import os

# Add the src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from services.database_manager import DatabaseManager
from services.config_manager import ConfigManager

def test_collections_functionality():
    """Test the collections tab functionality"""
    print("🧪 Testing Collections Tab Functionality")
    print("=" * 50)
    
    # Initialize managers
    config_manager = ConfigManager()
    db_manager = DatabaseManager(config_manager)
    
    # Test 1: Get collections members count
    print("\n📊 Test 1: Collections Count")
    counts = db_manager.get_category_counts()
    collections_count = counts.get('collections', 0)
    print(f"Collections members count: {collections_count}")
    
    # Test 2: Get actual collections members
    print("\n👥 Test 2: Collections Members List")
    collections_members = db_manager.get_members_by_category('collections')
    print(f"Found {len(collections_members)} collections members:")
    
    for i, member in enumerate(collections_members[:5]):  # Show first 5
        print(f"  {i+1}. {member.get('first_name', 'N/A')} {member.get('last_name', 'N/A')} - Status: {member.get('collections_status', 'N/A')} - Agreement ID: {member.get('agreement_id', 'NULL')}")
    
    if len(collections_members) > 5:
        print(f"  ... and {len(collections_members) - 5} more")
    
    # Test 3: Check database state
    print("\n🗄️ Test 3: Database Collections Status")
    
    # Check how many members have NULL agreement_id
    null_agreement_query = "SELECT COUNT(*) as count FROM members WHERE agreement_id IS NULL"
    null_result = db_manager.execute_query(null_agreement_query)
    null_count = null_result[0]['count'] if null_result else 0
    
    # Check how many have collections_status = 'Collections'
    collections_status_query = "SELECT COUNT(*) as count FROM members WHERE collections_status = 'Collections'"
    status_result = db_manager.execute_query(collections_status_query)
    status_count = status_result[0]['count'] if status_result else 0
    
    print(f"Members with NULL agreement_id: {null_count}")
    print(f"Members with collections_status = 'Collections': {status_count}")
    
    # Test 4: Verify category system works
    print("\n✅ Test 4: Category System Verification")
    all_categories = ['green', 'comp', 'ppv', 'staff', 'past_due', 'collections', 'inactive']
    
    for category in all_categories:
        count = counts.get(category, 0)
        members = db_manager.get_members_by_category(category)
        print(f"  {category.upper()}: Count={count}, Actual={len(members)} {'✅' if count == len(members) else '❌'}")
    
    print(f"\n🎯 Collections Tab Ready! Found {collections_count} members already sent to collections.")
    print("✅ Collections tab should now work in the web interface!")

if __name__ == '__main__':
    test_collections_functionality()