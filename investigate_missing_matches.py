#!/usr/bin/env python3
"""
Investigate why Rashida Hull and Mindy Feilbach aren't matching
"""

import sqlite3

def investigate_missing_matches():
    """Check why specific training clients aren't matching with members"""
    print("🔍 INVESTIGATING: Missing name matches")
    print("=" * 60)
    
    try:
        # Connect to database
        conn = sqlite3.connect('gym_bot.db')
        conn.row_factory = sqlite3.Row  # Enable dict-like access
        cursor = conn.cursor()
        
        # Get the two clients that didn't match
        missing_clients = ['Rashida Hull', 'Mindy Feilbach']
        
        for client_name in missing_clients:
            print(f"\n🔍 Investigating: {client_name}")
            print("-" * 40)
            
            # Get training client info
            cursor.execute("""
                SELECT member_name, first_name, last_name, full_name, clubos_member_id
                FROM training_clients 
                WHERE member_name = ?
            """, (client_name,))
            
            tc_result = cursor.fetchone()
            if tc_result:
                print(f"Training Client Data:")
                print(f"  member_name: '{tc_result['member_name']}'")
                print(f"  first_name: '{tc_result['first_name']}'")
                print(f"  last_name: '{tc_result['last_name']}'")
                print(f"  full_name: '{tc_result['full_name']}'")
                print(f"  clubos_member_id: '{tc_result['clubos_member_id']}'")
                
                # Search for similar names in members table
                print(f"\nSearching members table for variations:")
                
                # Exact matches
                cursor.execute("SELECT full_name, first_name, last_name, prospect_id FROM members WHERE LOWER(full_name) LIKE ?", (f"%{client_name.lower()}%",))
                exact_matches = cursor.fetchall()
                
                if exact_matches:
                    print(f"  📍 Found exact matches:")
                    for match in exact_matches:
                        print(f"    - full_name: '{match['full_name']}', first_name: '{match['first_name']}', last_name: '{match['last_name']}', prospect_id: {match['prospect_id']}")
                else:
                    print(f"  ❌ No exact matches found")
                
                # Search by first name only
                first_name = tc_result['first_name']
                if first_name:
                    cursor.execute("SELECT full_name, first_name, last_name, prospect_id FROM members WHERE LOWER(first_name) = ?", (first_name.lower(),))
                    first_name_matches = cursor.fetchall()
                    
                    if first_name_matches:
                        print(f"  📍 Found first name matches for '{first_name}':")
                        for match in first_name_matches:
                            print(f"    - full_name: '{match['full_name']}', first_name: '{match['first_name']}', last_name: '{match['last_name']}', prospect_id: {match['prospect_id']}")
                    else:
                        print(f"  ❌ No first name matches for '{first_name}'")
                
                # Search by last name only
                last_name = tc_result['last_name']
                if last_name:
                    cursor.execute("SELECT full_name, first_name, last_name, prospect_id FROM members WHERE LOWER(last_name) = ?", (last_name.lower(),))
                    last_name_matches = cursor.fetchall()
                    
                    if last_name_matches:
                        print(f"  📍 Found last name matches for '{last_name}':")
                        for match in last_name_matches:
                            print(f"    - full_name: '{match['full_name']}', first_name: '{match['first_name']}', last_name: '{match['last_name']}', prospect_id: {match['prospect_id']}")
                    else:
                        print(f"  ❌ No last name matches for '{last_name}'")
                
                # Search by ClubOS ID in case there's a different approach
                clubos_id = tc_result['clubos_member_id']
                if clubos_id:
                    cursor.execute("SELECT full_name, first_name, last_name, prospect_id, guid FROM members WHERE prospect_id = ? OR guid = ?", (clubos_id, clubos_id))
                    id_matches = cursor.fetchall()
                    
                    if id_matches:
                        print(f"  📍 Found ID matches for ClubOS ID '{clubos_id}':")
                        for match in id_matches:
                            print(f"    - full_name: '{match['full_name']}', prospect_id: {match['prospect_id']}, guid: '{match['guid']}'")
                    else:
                        print(f"  ❌ No ID matches for ClubOS ID '{clubos_id}'")
                
                # Fuzzy search - partial matches
                print(f"  🔍 Fuzzy search results:")
                words = client_name.split()
                for word in words:
                    if len(word) > 3:  # Only search meaningful words
                        cursor.execute("SELECT full_name, first_name, last_name, prospect_id FROM members WHERE LOWER(full_name) LIKE ?", (f"%{word.lower()}%",))
                        fuzzy_matches = cursor.fetchall()
                        
                        if fuzzy_matches:
                            print(f"    Contains '{word}':")
                            for match in fuzzy_matches[:3]:  # Limit to first 3
                                print(f"      - '{match['full_name']}'")
            else:
                print(f"  ❌ Training client '{client_name}' not found!")
        
        # Also check if there are any members with similar names that we might be missing
        print(f"\n🔍 Checking for potential name variations in members table:")
        cursor.execute("""
            SELECT DISTINCT full_name, first_name, last_name 
            FROM members 
            WHERE LOWER(full_name) LIKE '%rashida%' 
               OR LOWER(full_name) LIKE '%mindy%'
               OR LOWER(first_name) LIKE '%rashida%'
               OR LOWER(first_name) LIKE '%mindy%'
            ORDER BY full_name
        """)
        
        potential_matches = cursor.fetchall()
        if potential_matches:
            print("  📍 Found potential name variations:")
            for match in potential_matches:
                print(f"    - '{match['full_name']}' (first: '{match['first_name']}', last: '{match['last_name']}')")
        else:
            print("  ❌ No potential variations found")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error investigating matches: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    investigate_missing_matches()