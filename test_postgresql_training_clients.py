#!/usr/bin/env python3
"""
Test PostgreSQL training clients lookup
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.database_manager import DatabaseManager

# Initialize database manager
db_manager = DatabaseManager()

print("🔍 Testing PostgreSQL training clients lookup...")

try:
    # Get PostgreSQL connection
    conn = db_manager.get_connection()
    cursor = conn.cursor()
    
    # Test the count
    cursor.execute("SELECT COUNT(*) FROM training_clients")
    total_count = cursor.fetchone()[0]
    print(f"📊 Total training clients in PostgreSQL: {total_count}")
    
    # Test specific name lookups that were failing
    test_names = ['David Berendt', 'Alejandra Espinoza', 'Grace Sphatt', 'Dennis Rost']
    print(f"\n🔍 Testing specific names:")
    
    for name in test_names:
        # Test exact match
        cursor.execute("""
            SELECT member_name, total_past_due, payment_status
            FROM training_clients 
            WHERE LOWER(member_name) = LOWER(%s)
            LIMIT 1
        """, (name,))
        
        exact_result = cursor.fetchone()
        
        if exact_result:
            print(f"  ✅ EXACT match for '{name}': {exact_result[0]} (${exact_result[1]}, {exact_result[2]})")
        else:
            # Test partial match
            cursor.execute("""
                SELECT member_name, total_past_due, payment_status
                FROM training_clients 
                WHERE LOWER(member_name) LIKE LOWER(%s)
                LIMIT 1
            """, (f'%{name}%',))
            
            partial_result = cursor.fetchone()
            if partial_result:
                print(f"  ✅ PARTIAL match for '{name}': {partial_result[0]} (${partial_result[1]}, {partial_result[2]})")
            else:
                print(f"  ❌ No match found for '{name}'")
    
    conn.close()
    print("\n🎉 PostgreSQL training clients test completed!")
    
except Exception as e:
    print(f"❌ Error testing PostgreSQL: {e}")
    import traceback
    traceback.print_exc()