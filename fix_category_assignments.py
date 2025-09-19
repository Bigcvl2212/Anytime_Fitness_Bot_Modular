import sqlite3
import os

# Database path
db_path = os.path.join(os.path.dirname(__file__), 'gym_bot.db')

def fix_category_assignments():
    """Fix the category assignments for members based on their agreement types and past due amounts"""
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        cursor = conn.cursor()
        
        print("=" * 80)
        print("FIXING MEMBER CATEGORY ASSIGNMENTS")
        print("=" * 80)
        
        # First, get all members who should have categories but don't
        cursor.execute("""
            SELECT m.id, m.prospect_id, m.guid, m.full_name, m.agreement_type, 
                   m.amount_past_due, m.late_fees, m.missed_payments, m.status_message
            FROM members m
            LEFT JOIN member_categories mc ON m.id = mc.member_id
            WHERE mc.member_id IS NULL
            ORDER BY m.amount_past_due DESC
        """)
        missing_categories = cursor.fetchall()
        
        print(f"Found {len(missing_categories)} members without category assignments")
        
        if missing_categories:
            print("\nTop 10 members missing categories:")
            for i, member in enumerate(missing_categories[:10]):
                total_owed = (member['amount_past_due'] or 0) + (member['late_fees'] or 0)
                print(f"  {i+1}. {member['full_name']}: ${total_owed:.2f} (Agreement: {member['agreement_type']})")
        
        # Apply categorization logic for missing members
        fixed_count = 0
        collections_count = 0
        past_due_count = 0
        
        for member in missing_categories:
            member_id = str(member['id'])  # Use database ID as member_id
            prospect_id = member['prospect_id'] or member['guid']  # Fallback
            full_name = member['full_name']
            agreement_type = str(member['agreement_type'] or '').lower()
            status_message = str(member['status_message'] or '').lower()
            amount_past_due = float(member['amount_past_due'] or 0)
            late_fees = float(member['late_fees'] or 0)
            total_owed = amount_past_due + late_fees
            
            # Determine category based on agreement type and amounts
            category = 'green'  # default
            classification_reason = 'Default - good standing'
            
            # Collections takes priority
            if agreement_type == 'collections' or total_owed > 200:
                category = 'collections'  # New category for collections
                classification_reason = f'Collections (Agreement: {agreement_type}, Owed: ${total_owed:.2f})'
                collections_count += 1
            
            # Past due (but not collections level)
            elif total_owed > 0:
                category = 'past_due'
                classification_reason = f'Past Due (${total_owed:.2f})'
                past_due_count += 1
            
            # Status message based categorization
            elif 'past due more than 30 days' in status_message:
                category = 'past_due'
                classification_reason = 'Status: Past Due >30 days'
                past_due_count += 1
            elif 'past due 6-30 days' in status_message:
                category = 'past_due'
                classification_reason = 'Status: Past Due 6-30 days'
                past_due_count += 1
            elif 'staff' in status_message:
                category = 'staff'
                classification_reason = 'Status: Staff member'
            elif any(word in status_message for word in ['comp', 'free']):
                category = 'comp'
                classification_reason = 'Status: Comp member'
            elif 'pay per visit' in status_message or 'ppv' in status_message:
                category = 'ppv'
                classification_reason = 'Status: Pay per visit'
            elif any(word in status_message for word in ['cancelled', 'cancel', 'expire', 'pending', 'suspended']):
                category = 'inactive'
                classification_reason = 'Status: Inactive'
            
            # Insert the category assignment
            try:
                cursor.execute("""
                    INSERT INTO member_categories (member_id, category, status_message, full_name, created_at, updated_at, classified_at)
                    VALUES (?, ?, ?, ?, datetime('now'), datetime('now'), datetime('now'))
                """, (member_id, category, classification_reason, full_name))
                
                fixed_count += 1
                
                # Print important ones
                if category in ['collections', 'past_due'] or total_owed > 100:
                    print(f"  ✅ {full_name}: {category} - {classification_reason}")
                    
            except sqlite3.Error as e:
                print(f"  ❌ Error categorizing {full_name}: {e}")
        
        # Also fix existing wrong categorizations
        print(f"\nChecking existing category assignments...")
        
        # Find members in past_due category who should be in collections
        cursor.execute("""
            SELECT m.id, m.full_name, m.agreement_type, m.amount_past_due, m.late_fees, mc.category
            FROM members m
            JOIN member_categories mc ON m.id = mc.member_id
            WHERE mc.category = 'past_due' 
            AND (m.agreement_type = 'Collections' OR (m.amount_past_due + COALESCE(m.late_fees, 0)) > 200)
        """)
        should_be_collections = cursor.fetchall()
        
        print(f"Found {len(should_be_collections)} members in past_due who should be collections")
        
        for member in should_be_collections:
            total_owed = (member['amount_past_due'] or 0) + (member['late_fees'] or 0)
            print(f"  Moving {member['full_name']} to collections (${total_owed:.2f})")
            
            cursor.execute("""
                UPDATE member_categories 
                SET category = 'collections', 
                    status_message = ?, 
                    updated_at = datetime('now'),
                    classified_at = datetime('now')
                WHERE member_id = ?
            """, (f"Collections - ${total_owed:.2f} owed", str(member['id'])))
        
        # Commit all changes
        conn.commit()
        
        print(f"\n✅ CATEGORIZATION COMPLETE:")
        print(f"  - Fixed {fixed_count} missing category assignments")
        print(f"  - Created {collections_count} collections categories")
        print(f"  - Created {past_due_count} past_due categories")
        print(f"  - Moved {len(should_be_collections)} members from past_due to collections")
        
        # Show final category breakdown
        cursor.execute("""
            SELECT category, COUNT(*) as count 
            FROM member_categories 
            GROUP BY category 
            ORDER BY count DESC
        """)
        final_categories = cursor.fetchall()
        
        print(f"\nFINAL CATEGORY BREAKDOWN:")
        for cat in final_categories:
            print(f"  {cat['category']}: {cat['count']} members")
        
        # Check Anthony Jordan specifically
        print(f"\nANTHONY JORDAN UPDATE:")
        cursor.execute("""
            SELECT m.full_name, m.agreement_type, m.amount_past_due, m.late_fees, mc.category, mc.status_message
            FROM members m
            LEFT JOIN member_categories mc ON m.id = mc.member_id
            WHERE m.full_name LIKE '%Anthony%Jordan%'
        """)
        anthony_after = cursor.fetchone()
        
        if anthony_after:
            total_owed = (anthony_after['amount_past_due'] or 0) + (anthony_after['late_fees'] or 0)
            print(f"  Name: {anthony_after['full_name']}")
            print(f"  Agreement Type: {anthony_after['agreement_type']}")
            print(f"  Total Owed: ${total_owed:.2f}")
            print(f"  Category: {anthony_after['category']}")
            print(f"  Status: {anthony_after['status_message']}")
        else:
            print("  Anthony Jordan not found")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error fixing categories: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    fix_category_assignments()