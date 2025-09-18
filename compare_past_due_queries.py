import sys
sys.path.append('.')
from src.services.database_manager import DatabaseManager

def compare_past_due_queries():
    """Compare different past due queries to understand the agreement ID issue"""
    db = DatabaseManager()
    
    print('🔍 Checking different past due queries...')
    
    # Collections query (current)
    result1 = db.execute_query("""
        SELECT full_name, agreement_id, amount_past_due, status_message
        FROM members 
        WHERE status_message LIKE '%Past Due 6-30 days%' 
           OR status_message LIKE '%Past Due more than 30 days%'
        ORDER BY amount_past_due DESC LIMIT 5
    """)
    
    print('\n📋 Collections Query Results (status_message filter):')
    for r in result1:
        print(f'  {r["full_name"]} - Agreement ID: {r["agreement_id"]} - Amount: ${r["amount_past_due"]} - Status: {r["status_message"]}')
    
    # General past due query (what we tested earlier)
    result2 = db.execute_query("""
        SELECT full_name, agreement_id, amount_past_due, status_message
        FROM members 
        WHERE amount_past_due > 0 
        ORDER BY amount_past_due DESC LIMIT 5
    """)
    
    print('\n📋 General Past Due Query Results (amount_past_due > 0):')
    for r in result2:
        print(f'  {r["full_name"]} - Agreement ID: {r["agreement_id"]} - Amount: ${r["amount_past_due"]} - Status: {r["status_message"]}')
    
    # Check status messages for members with agreement IDs
    result3 = db.execute_query("""
        SELECT full_name, agreement_id, amount_past_due, status_message
        FROM members 
        WHERE agreement_id IS NOT NULL AND amount_past_due > 0
        ORDER BY amount_past_due DESC LIMIT 5
    """)
    
    print('\n📋 Members with Agreement IDs and Past Due Amounts:')
    for r in result3:
        print(f'  {r["full_name"]} - Agreement ID: {r["agreement_id"]} - Amount: ${r["amount_past_due"]} - Status: {r["status_message"]}')
    
    # Check what status messages exist
    result4 = db.execute_query("""
        SELECT DISTINCT status_message, COUNT(*) as count
        FROM members 
        WHERE amount_past_due > 0
        GROUP BY status_message
        ORDER BY count DESC
    """)
    
    print('\n📊 Status Messages for Past Due Members:')
    for r in result4:
        print(f'  "{r["status_message"]}" - {r["count"]} members')

if __name__ == "__main__":
    compare_past_due_queries()