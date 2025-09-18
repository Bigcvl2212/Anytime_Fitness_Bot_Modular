import sys
sys.path.append('.')
from src.services.database_manager import DatabaseManager

def check_agreement_data():
    """Check where the hell the agreement IDs are stored"""
    db = DatabaseManager()
    
    print('🔍 DEBUGGING AGREEMENT ID STORAGE...')
    
    # Check members table structure
    try:
        result = db.execute_query("SELECT sql FROM sqlite_master WHERE type='table' AND name='members'")
        if result:
            print('\n📋 MEMBERS TABLE SCHEMA:')
            print(result[0]['sql'])
    except:
        pass
    
    # Get a specific past due member we know exists
    result = db.execute_query("""
        SELECT * FROM members 
        WHERE full_name = 'WHITTNEY PULTZ' OR full_name = 'DALE ROEN'
        LIMIT 2
    """)
    
    print(f'\n📋 CHECKING SPECIFIC MEMBERS:')
    for member in result:
        print(f"\nMember: {member.get('full_name', 'Unknown')}")
        print(f"Amount Past Due: ${member.get('amount_past_due', 0)}")
        # Print ALL columns to see what we have
        for key, value in member.items():
            if 'agreement' in key.lower() or 'id' in key.lower():
                print(f"  {key}: {value}")
    
    # Check if there's a separate agreements table
    try:
        tables = db.execute_query("SELECT name FROM sqlite_master WHERE type='table'")
        agreement_tables = [t['name'] for t in tables if 'agreement' in t['name'].lower()]
        print(f'\n📊 AGREEMENT-RELATED TABLES: {agreement_tables}')
        
        for table in agreement_tables:
            try:
                sample = db.execute_query(f"SELECT * FROM {table} LIMIT 3")
                print(f'\n📋 {table.upper()} TABLE SAMPLE:')
                for row in sample:
                    print(f"  {dict(row)}")
            except Exception as e:
                print(f"  Error reading {table}: {e}")
                
    except Exception as e:
        print(f"Error checking tables: {e}")

if __name__ == "__main__":
    check_agreement_data()