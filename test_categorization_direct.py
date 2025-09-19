#!/usr/bin/env python3

import sqlite3
import logging
from datetime import datetime

def test_categorization_directly():
    """Test categorization logic directly on SQLite database"""
    
    db_path = "gym_bot.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("=== TESTING CATEGORIZATION LOGIC DIRECTLY ===")
        
        # Get some sample members to test categorization
        cursor.execute("""
            SELECT id, full_name, agreement_type, amount_past_due, status_message, status, agreement_id
            FROM members 
            WHERE full_name IN ('ANTHONY JORDAN', 'Miguel Belmontes', 'JOSEPH JONES', 'CHRIS BENNETT', 'WHITTNEY PULTZ')
            ORDER BY full_name
        """)
        
        test_members = cursor.fetchall()
        
        print(f"Found {len(test_members)} test members:")
        for member in test_members:
            id, full_name, agreement_type, amount_past_due, status_message, status, agreement_id = member
            print(f"  {full_name}: {agreement_type}, ${amount_past_due}, {status_message}, agreement_id: {agreement_id}")
        
        print(f"\n=== APPLYING NEW CATEGORIZATION LOGIC ===")
        
        # Apply the categorization logic directly
        for member in test_members:
            id, full_name, agreement_type, amount_past_due, status_message, status, agreement_id = member
            
            # Apply the same logic from the updated DatabaseManager
            status_message_lower = str(status_message or '').lower()
            status_lower = str(status or '').lower()
            past_due_amount = float(amount_past_due or 0)
            agreement_type_lower = str(agreement_type or '').lower()
            
            # Default category and status message
            category = 'green'
            updated_status_message = status_message
            
            # Collections members - Check for Collections agreement type or sent to collections status
            if (agreement_type_lower == 'collections' or 
                'sent to collections' in status_message_lower or
                'collections' in status_message_lower or
                (agreement_id is None and past_due_amount > 0 and 'good standing' not in status_message_lower)):
                category = 'collections'
                updated_status_message = status_message or 'Collections'
            
            # Past due members - ONLY if they have specific ClubHub status messages
            elif ('past due more than 30 days' in status_message_lower):
                category = 'past_due'
                updated_status_message = 'Past Due more than 30 days'
            elif ('past due 6-30 days' in status_message_lower):
                category = 'past_due'
                updated_status_message = 'Past Due 6-30 days'
            
            # Staff members
            elif ('staff' in status_message_lower or 'staff' in status_lower):
                category = 'staff'
            
            # Comp members
            elif ('comp' in status_message_lower or 'comp' in status_lower or 'free' in status_message_lower):
                category = 'comp'
            
            # Pay per visit members
            elif ('pay per visit' in status_message_lower or 'ppv' in status_message_lower):
                category = 'ppv'
            
            # Inactive members
            elif (any(inactive in status_message_lower for inactive in ['cancelled', 'cancel', 'expire', 'pending', 'suspended']) or
                  status_lower in ['inactive', 'suspended', 'cancelled']):
                category = 'inactive'
            
            # Green members (in good standing) - default for active members
            elif ('good standing' in status_message_lower or 'active' in status_lower or status_lower == 'active'):
                category = 'green'
            
            print(f"\n{full_name}:")
            print(f"  Agreement Type: {agreement_type}")
            print(f"  Agreement ID: {agreement_id}")
            print(f"  Past Due: ${amount_past_due}")
            print(f"  Status Message: {status_message}")
            print(f"  → NEW CATEGORY: {category}")
            
            # Update the category in the database
            current_time = datetime.now().isoformat()
            
            # Check if category exists
            cursor.execute("SELECT category FROM member_categories WHERE member_id = ?", (str(id),))
            existing = cursor.fetchone()
            
            if existing:
                old_category = existing[0]
                cursor.execute("""
                    UPDATE member_categories SET 
                        category = ?, status_message = ?, full_name = ?, classified_at = ?
                    WHERE member_id = ?
                """, (category, updated_status_message, full_name, current_time, str(id)))
                
                if old_category != category:
                    print(f"  ✅ UPDATED: {old_category} → {category}")
                else:
                    print(f"  ✓ UNCHANGED: {category}")
            else:
                cursor.execute("""
                    INSERT INTO member_categories (member_id, category, status_message, full_name, classified_at, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (str(id), category, updated_status_message, full_name, current_time, current_time))
                print(f"  ✅ NEW CATEGORY: {category}")
        
        # Commit changes
        conn.commit()
        
        # Show updated category counts
        print(f"\n=== UPDATED CATEGORY COUNTS ===")
        cursor.execute("""
            SELECT category, COUNT(*) as count
            FROM member_categories 
            GROUP BY category 
            ORDER BY count DESC
        """)
        
        categories = cursor.fetchall()
        total = sum(count for _, count in categories)
        
        for category, count in categories:
            print(f"  {category}: {count}")
        
        print(f"Total: {total}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error testing categorization: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_categorization_directly()