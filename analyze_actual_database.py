import sqlite3
import os

# Database path
db_path = os.path.join(os.path.dirname(__file__), 'gym_bot.db')

def analyze_actual_database():
    """Analyze the actual database structure and data"""
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        cursor = conn.cursor()
        
        print("=" * 80)
        print("ACTUAL DATABASE ANALYSIS")
        print("=" * 80)
        
        # Get all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print("AVAILABLE TABLES:")
        for table in tables:
            print(f"  - {table['name']}")
        
        # Check members table in detail
        print(f"\nMEMBERS TABLE ANALYSIS:")
        cursor.execute("SELECT COUNT(*) as count FROM members")
        member_count = cursor.fetchone()['count']
        print(f"Total members: {member_count}")
        
        # Look at sample member data
        cursor.execute("SELECT * FROM members LIMIT 5")
        sample_members = cursor.fetchall()
        
        if sample_members:
            print("\nSample member data:")
            for member in sample_members:
                print(f"  ID: {member['id']}")
                print(f"  Name: {member['full_name']}")
                print(f"  Email: {member['email']}")
                print(f"  Phone: {member['phone']}")
                print(f"  Status: {member['status']}")
                print(f"  Amount Past Due: {member['amount_past_due']}")
                print(f"  Next Payment: {member['date_of_next_payment']}")
                print(f"  Agreement Type: {member['agreement_type']}")
                print("  ---")
        
        # Check for Anthony Jordan specifically
        print("\nANTHONY JORDAN SEARCH:")
        cursor.execute("""
            SELECT * FROM members 
            WHERE full_name LIKE '%Anthony%' AND full_name LIKE '%Jordan%'
        """)
        anthony_records = cursor.fetchall()
        
        if anthony_records:
            for record in anthony_records:
                print(f"  Name: {record['full_name']}")
                print(f"  Email: {record['email']}")
                print(f"  Phone: {record['phone']}")
                print(f"  Status: {record['status']}")
                print(f"  Amount Past Due: ${record['amount_past_due'] or 0}")
                print(f"  Late Fees: ${record['late_fees'] or 0}")
                print(f"  Missed Payments: {record['missed_payments'] or 0}")
                print(f"  Agreement Type: {record['agreement_type']}")
                print(f"  Agreement ID: {record['agreement_id']}")
        else:
            print("  No records found for Anthony Jordan")
            
            # Try broader search
            cursor.execute("SELECT full_name FROM members WHERE full_name LIKE '%Anthony%' OR full_name LIKE '%Jordan%'")
            similar_names = cursor.fetchall()
            
            if similar_names:
                print("  Similar names found:")
                for name in similar_names:
                    print(f"    - {name['full_name']}")
        
        # Analyze past due amounts
        print("\nPAST DUE ANALYSIS:")
        cursor.execute("""
            SELECT 
                COUNT(*) as total_members,
                COUNT(CASE WHEN amount_past_due > 0 THEN 1 END) as past_due_count,
                COUNT(CASE WHEN amount_past_due > 100 THEN 1 END) as high_past_due,
                AVG(amount_past_due) as avg_past_due,
                MAX(amount_past_due) as max_past_due
            FROM members
        """)
        stats = cursor.fetchone()
        
        print(f"  Total members: {stats['total_members']}")
        print(f"  Members with past due amount > $0: {stats['past_due_count']}")
        print(f"  Members with past due amount > $100: {stats['high_past_due']}")
        print(f"  Average past due: ${stats['avg_past_due']:.2f}")
        print(f"  Maximum past due: ${stats['max_past_due']:.2f}")
        
        # Show top past due members
        cursor.execute("""
            SELECT full_name, amount_past_due, late_fees, missed_payments, status
            FROM members 
            WHERE amount_past_due > 0
            ORDER BY amount_past_due DESC
            LIMIT 10
        """)
        top_past_due = cursor.fetchall()
        
        if top_past_due:
            print("\nTOP PAST DUE MEMBERS:")
            for member in top_past_due:
                total_owed = (member['amount_past_due'] or 0) + (member['late_fees'] or 0)
                print(f"  {member['full_name']}: ${total_owed:.2f} (Base: ${member['amount_past_due'] or 0}, Fees: ${member['late_fees'] or 0}, Missed: {member['missed_payments'] or 0})")
        
        # Check prospects table
        print(f"\nPROSPECTS TABLE ANALYSIS:")
        cursor.execute("SELECT COUNT(*) as count FROM prospects")
        prospect_count = cursor.fetchone()['count']
        print(f"Total prospects: {prospect_count}")
        
        # Sample prospect data
        cursor.execute("SELECT * FROM prospects LIMIT 3")
        sample_prospects = cursor.fetchall()
        
        if sample_prospects:
            print("\nSample prospect data:")
            for prospect in sample_prospects:
                print(f"  ID: {prospect['id']}")
                print(f"  Name: {prospect['full_name']}")
                print(f"  Email: {prospect['email']}")
                print(f"  Phone: {prospect['phone']}")
                print(f"  Status: {prospect['status']}")
                print(f"  Type: {prospect['prospect_type']}")
                print("  ---")
        
        conn.close()
        
    except Exception as e:
        print(f"Error analyzing database: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_actual_database()