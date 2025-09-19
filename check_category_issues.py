import sqlite3
import os
from collections import defaultdict

# Database path
db_path = os.path.join(os.path.dirname(__file__), 'gym_bot.db')

def check_database_categories():
    """Check current database categories and identify issues"""
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        cursor = conn.cursor()
        
        print("=" * 80)
        print("DATABASE CATEGORY ANALYSIS")
        print("=" * 80)
        
        # Check members table structure
        cursor.execute("PRAGMA table_info(members)")
        columns = cursor.fetchall()
        print("\nMEMBERS TABLE STRUCTURE:")
        for col in columns:
            print(f"  {col['name']} ({col['type']})")
        
        # Check prospects table structure  
        cursor.execute("PRAGMA table_info(prospects)")
        columns = cursor.fetchall()
        print("\nPROSPECTS TABLE STRUCTURE:")
        for col in columns:
            print(f"  {col['name']} ({col['type']})")
        
        # Get all members with their categories
        cursor.execute("""
            SELECT full_name, category, past_due, collections, phone, email, last_visit
            FROM members 
            ORDER BY category, full_name
        """)
        members = cursor.fetchall()
        
        # Get all prospects with their categories
        cursor.execute("""
            SELECT full_name, category, phone, email, last_visit  
            FROM prospects 
            ORDER BY category, full_name
        """)
        prospects = cursor.fetchall()
        
        print(f"\nTOTAL MEMBERS: {len(members)}")
        print(f"TOTAL PROSPECTS: {len(prospects)}")
        
        # Analyze member categories
        member_categories = defaultdict(list)
        past_due_members = []
        collections_members = []
        
        for member in members:
            category = member['category'] or 'No Category'
            member_categories[category].append(member)
            
            if member['past_due']:
                past_due_members.append(member)
            if member['collections']:
                collections_members.append(member)
        
        print("\nMEMBER CATEGORY BREAKDOWN:")
        for category, member_list in member_categories.items():
            print(f"  {category}: {len(member_list)} members")
        
        # Analyze prospect categories
        prospect_categories = defaultdict(list)
        for prospect in prospects:
            category = prospect['category'] or 'No Category'
            prospect_categories[category].append(prospect)
        
        print("\nPROSPECT CATEGORY BREAKDOWN:")
        for category, prospect_list in prospect_categories.items():
            print(f"  {category}: {len(prospect_list)} prospects")
        
        print(f"\nPAST DUE FLAGS: {len(past_due_members)} members")
        print(f"COLLECTIONS FLAGS: {len(collections_members)} members")
        
        # Check for overlapping past due and collections
        print("\n" + "=" * 80)
        print("CATEGORY CONFLICT ANALYSIS")
        print("=" * 80)
        
        overlapping_members = []
        for member in members:
            if member['past_due'] and member['collections']:
                overlapping_members.append(member)
        
        print(f"\nMEMBERS WITH BOTH PAST_DUE AND COLLECTIONS FLAGS: {len(overlapping_members)}")
        if overlapping_members:
            for member in overlapping_members:
                print(f"  - {member['full_name']} (Category: {member['category']})")
        
        # Look specifically for Anthony Jordan
        print("\nANTHONY JORDAN ANALYSIS:")
        cursor.execute("""
            SELECT * FROM members 
            WHERE full_name LIKE '%Anthony%' AND full_name LIKE '%Jordan%'
        """)
        anthony_records = cursor.fetchall()
        
        if anthony_records:
            for record in anthony_records:
                print(f"  Name: {record['full_name']}")
                print(f"  Category: {record['category']}")
                print(f"  Past Due: {record['past_due']}")
                print(f"  Collections: {record['collections']}")
                print(f"  Phone: {record['phone']}")
                print(f"  Last Visit: {record['last_visit']}")
        else:
            print("  No records found for Anthony Jordan")
        
        # Check for members in past due category but not flagged as past due
        print("\nCATEGORY VS FLAG MISMATCHES:")
        
        past_due_category_members = [m for m in members if m['category'] == 'Past Due']
        past_due_flagged_members = [m for m in members if m['past_due']]
        
        print(f"Members in 'Past Due' category: {len(past_due_category_members)}")
        print(f"Members with past_due flag: {len(past_due_flagged_members)}")
        
        # Members in past due category but not flagged
        category_not_flagged = []
        for member in past_due_category_members:
            if not member['past_due']:
                category_not_flagged.append(member)
        
        if category_not_flagged:
            print(f"\nMembers in 'Past Due' category but NOT flagged as past_due ({len(category_not_flagged)}):")
            for member in category_not_flagged:
                print(f"  - {member['full_name']}")
        
        # Members flagged as past due but not in category
        flagged_not_category = []
        for member in past_due_flagged_members:
            if member['category'] != 'Past Due':
                flagged_not_category.append(member)
        
        if flagged_not_category:
            print(f"\nMembers flagged as past_due but NOT in 'Past Due' category ({len(flagged_not_category)}):")
            for member in flagged_not_category:
                print(f"  - {member['full_name']} (Category: {member['category']})")
        
        # Similar analysis for collections
        collections_category_members = [m for m in members if m['category'] == 'Collections']
        collections_flagged_members = [m for m in members if m['collections']]
        
        print(f"\nMembers in 'Collections' category: {len(collections_category_members)}")
        print(f"Members with collections flag: {len(collections_flagged_members)}")
        
        # Show recent updates
        print("\n" + "=" * 80)
        print("RECENT DATABASE ACTIVITY")
        print("=" * 80)
        
        # Check if there's a last_updated column
        try:
            cursor.execute("""
                SELECT full_name, category, last_updated
                FROM members 
                WHERE last_updated IS NOT NULL
                ORDER BY last_updated DESC
                LIMIT 10
            """)
            recent_updates = cursor.fetchall()
            
            if recent_updates:
                print("\nRECENT MEMBER UPDATES:")
                for update in recent_updates:
                    print(f"  {update['full_name']} - {update['category']} - {update['last_updated']}")
            else:
                print("\nNo recent update timestamps found")
                
        except sqlite3.OperationalError as e:
            print(f"\nNo last_updated column found: {e}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error checking database categories: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_database_categories()