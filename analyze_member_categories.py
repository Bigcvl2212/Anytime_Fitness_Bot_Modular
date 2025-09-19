import sqlite3
import os

# Database path
db_path = os.path.join(os.path.dirname(__file__), 'gym_bot.db')

def analyze_member_categories():
    """Analyze the member_categories table and category logic"""
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        cursor = conn.cursor()
        
        print("=" * 80)
        print("MEMBER CATEGORIES TABLE ANALYSIS")
        print("=" * 80)
        
        # Check member_categories table structure
        cursor.execute("PRAGMA table_info(member_categories)")
        columns = cursor.fetchall()
        
        print("MEMBER_CATEGORIES TABLE STRUCTURE:")
        for col in columns:
            print(f"  {col['name']} ({col['type']})")
        
        # Get all categories
        cursor.execute("SELECT COUNT(*) as count FROM member_categories")
        total_categories = cursor.fetchone()['count']
        print(f"\nTotal records in member_categories: {total_categories}")
        
        # Sample data
        cursor.execute("SELECT * FROM member_categories LIMIT 10")
        sample_categories = cursor.fetchall()
        
        if sample_categories:
            print("\nSample category data:")
            for cat in sample_categories:
                print(f"  Member ID: {cat['member_id']}")
                print(f"  Category: {cat['category']}")
                try:
                    print(f"  Updated At: {cat['updated_at']}")
                except (KeyError, IndexError):
                    print("  Updated At: N/A")
                print("  ---")
        
        # Get category breakdown
        cursor.execute("""
            SELECT category, COUNT(*) as count 
            FROM member_categories 
            GROUP BY category 
            ORDER BY count DESC
        """)
        category_breakdown = cursor.fetchall()
        
        print("\nCATEGORY BREAKDOWN:")
        for cat in category_breakdown:
            print(f"  {cat['category']}: {cat['count']} members")
        
        # Check Anthony Jordan in categories
        print("\nANTHONY JORDAN CATEGORY STATUS:")
        
        # First get Anthony's member ID
        cursor.execute("SELECT id FROM members WHERE full_name LIKE '%Anthony%Jordan%'")
        anthony_id = cursor.fetchone()
        
        if anthony_id:
            anthony_member_id = anthony_id['id']
            print(f"Anthony Jordan's member ID: {anthony_member_id}")
            
            # Check his category assignment
            cursor.execute("SELECT * FROM member_categories WHERE member_id = ?", (anthony_member_id,))
            anthony_category = cursor.fetchone()
            
            if anthony_category:
                print(f"Current category: {anthony_category['category']}")
                try:
                    print(f"Updated at: {anthony_category['updated_at']}")
                except (KeyError, IndexError):
                    print("Updated at: N/A")
            else:
                print("No category assignment found!")
        else:
            print("Anthony Jordan not found in members table")
        
        # Check for members who should be in different categories
        print("\nCATEGORY LOGIC ANALYSIS:")
        
        # Members with collections agreement type but not in collections category
        cursor.execute("""
            SELECT m.id, m.full_name, m.agreement_type, m.amount_past_due, mc.category
            FROM members m
            LEFT JOIN member_categories mc ON m.id = mc.member_id
            WHERE m.agreement_type = 'Collections'
        """)
        collections_members = cursor.fetchall()
        
        print(f"\nMembers with Collections agreement type: {len(collections_members)}")
        for member in collections_members:
            print(f"  {member['full_name']}: Category={member['category']}, Past Due=${member['amount_past_due']}")
        
        # Members with high past due but not in collections
        cursor.execute("""
            SELECT m.id, m.full_name, m.amount_past_due, m.late_fees, m.missed_payments, mc.category
            FROM members m
            LEFT JOIN member_categories mc ON m.id = mc.member_id
            WHERE m.amount_past_due > 200 AND (mc.category != 'Collections' OR mc.category IS NULL)
            ORDER BY m.amount_past_due DESC
        """)
        high_past_due_not_collections = cursor.fetchall()
        
        print(f"\nMembers with >$200 past due but NOT in Collections: {len(high_past_due_not_collections)}")
        for member in high_past_due_not_collections:
            total_owed = (member['amount_past_due'] or 0) + (member['late_fees'] or 0)
            print(f"  {member['full_name']}: ${total_owed:.2f}, Category={member['category']}")
        
        # Members in Past Due category
        cursor.execute("""
            SELECT m.id, m.full_name, m.amount_past_due, m.late_fees, mc.category
            FROM members m
            JOIN member_categories mc ON m.id = mc.member_id
            WHERE mc.category = 'Past Due'
            ORDER BY m.amount_past_due DESC
        """)
        past_due_category_members = cursor.fetchall()
        
        print(f"\nMembers in 'Past Due' category: {len(past_due_category_members)}")
        for member in past_due_category_members:
            total_owed = (member['amount_past_due'] or 0) + (member['late_fees'] or 0)
            print(f"  {member['full_name']}: ${total_owed:.2f}")
        
        # Check for members without category assignments
        cursor.execute("""
            SELECT m.id, m.full_name, m.amount_past_due
            FROM members m
            LEFT JOIN member_categories mc ON m.id = mc.member_id
            WHERE mc.member_id IS NULL
            ORDER BY m.amount_past_due DESC
            LIMIT 20
        """)
        no_category_members = cursor.fetchall()
        
        print(f"\nMembers without category assignment: {len(no_category_members)} (showing top 20)")
        for member in no_category_members:
            print(f"  {member['full_name']}: ${member['amount_past_due'] or 0}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error analyzing member categories: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_member_categories()