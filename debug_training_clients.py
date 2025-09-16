#!/usr/bin/env python3
"""
Debug script to check training clients in database
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.database_manager import DatabaseManager

# Initialize database manager
db_manager = DatabaseManager()

print("🔍 Checking training clients in database...")

# Check if training_clients table exists and has data
try:
    # Get total count
    result = db_manager.execute_query("SELECT COUNT(*) as count FROM training_clients")
    if result:
        total_count = result[0]['count']
        print(f"📊 Total training clients in database: {total_count}")
    else:
        print("❌ No results from training_clients count query")
        
    # Get a few sample records
    sample_result = db_manager.execute_query("""
        SELECT member_name, first_name, last_name, member_id, created_at 
        FROM training_clients 
        ORDER BY created_at DESC 
        LIMIT 10
    """)
    
    if sample_result:
        print(f"\n📋 Sample training clients (showing {len(sample_result)}):")
        for i, client in enumerate(sample_result):
            print(f"  {i+1}. {client['member_name']} ({client['first_name']} {client['last_name']}) - ID: {client['member_id']}")
    else:
        print("❌ No sample training clients found")
        
    # Check for specific names from the error logs
    test_names = ['David Berendt', 'Alejandra Espinoza', 'Grace Sphatt', 'Dennis Rost']
    print(f"\n🔍 Checking for specific names that failed:")
    
    for name in test_names:
        result = db_manager.execute_query("""
            SELECT member_name, first_name, last_name 
            FROM training_clients 
            WHERE LOWER(member_name) LIKE LOWER(?) 
               OR LOWER(first_name || ' ' || last_name) LIKE LOWER(?)
            LIMIT 3
        """, (f'%{name}%', f'%{name}%'))
        
        if result:
            print(f"  ✅ Found matches for '{name}':")
            for match in result:
                print(f"    - {match['member_name']} ({match['first_name']} {match['last_name']})")
        else:
            print(f"  ❌ No matches found for '{name}'")

except Exception as e:
    print(f"❌ Error checking training clients: {e}")
    import traceback
    traceback.print_exc()