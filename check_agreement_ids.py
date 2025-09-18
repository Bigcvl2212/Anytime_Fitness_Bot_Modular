import sys
sys.path.append('.')
from src.services.database_manager import DatabaseManager

def check_agreement_ids():
    """Check if agreement_id field is populated in database"""
    db = DatabaseManager()
    
    print("🔍 Checking agreement_id field population...")
    
    # Check if past due members have agreement_id populated
    result = db.execute_query('''
        SELECT id, full_name, agreement_id, amount_past_due 
        FROM members 
        WHERE amount_past_due > 0 
        LIMIT 5
    ''')
    
    print('\n📋 Past Due Members with Agreement IDs:')
    for row in result:
        print(f'  {row["full_name"]} (ID: {row["id"]}) - Agreement ID: {row["agreement_id"]} - Past Due: ${row["amount_past_due"]}')
    
    # Check if agreement_id column exists
    try:
        columns = db.execute_query('PRAGMA table_info(members)')
        if columns:
            agreement_cols = [col for col in columns if 'agreement' in col['name'].lower()]
            print(f'\n📊 Agreement-related columns: {[col["name"] for col in agreement_cols]}')
        else:
            print('\n⚠️ No columns returned from table info query')
        
        # Count how many members have null vs populated agreement_id
        null_count = db.execute_query('SELECT COUNT(*) as count FROM members WHERE agreement_id IS NULL')[0]['count']
        populated_count = db.execute_query('SELECT COUNT(*) as count FROM members WHERE agreement_id IS NOT NULL')[0]['count']
        
        print(f'\n📈 Agreement ID Status:')
        print(f'  - Members with NULL agreement_id: {null_count}')
        print(f'  - Members with populated agreement_id: {populated_count}')
        
    except Exception as e:
        print(f'❌ Error checking columns: {e}')

if __name__ == "__main__":
    check_agreement_ids()