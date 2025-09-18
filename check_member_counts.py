#!/usr/bin/env python3
"""
Check member counts in database
"""

from src.services.database_manager import DatabaseManager

def main():
    db = DatabaseManager()
    
    # Total active members
    total = db.execute_query('SELECT COUNT(*) as count FROM members WHERE status > 0')
    print(f'Total active members: {total[0]["count"] if total else "No data"}')
    
    # Excluded members
    excluded = db.execute_query('''
        SELECT COUNT(*) as count FROM members 
        WHERE status_message LIKE "%cancelled%" 
        OR status_message LIKE "%expired%" 
        OR status_message LIKE "%inactive%"
    ''')  
    print(f'Excluded members: {excluded[0]["count"] if excluded else "No data"}')
    
    # Eligible members (same query as bulk check-in)
    eligible = db.execute_query('''
        SELECT COUNT(*) as count FROM members 
        WHERE status_message NOT LIKE "%cancelled%" 
        AND status_message NOT LIKE "%expired%" 
        AND status_message NOT LIKE "%inactive%" 
        AND status > 0
    ''')
    print(f'Eligible members: {eligible[0]["count"] if eligible else "No data"}')
    
    # Sample of eligible members
    sample = db.execute_query('''
        SELECT prospect_id, first_name, last_name, full_name, status_message, 
               user_type, member_type, agreement_type, status
        FROM members 
        WHERE status_message NOT LIKE "%cancelled%" 
        AND status_message NOT LIKE "%expired%" 
        AND status_message NOT LIKE "%inactive%" 
        AND status > 0
        LIMIT 5
    ''')
    print(f'\nSample eligible members:')
    for member in sample:
        print(f'  {member["full_name"]} (ID: {member["prospect_id"]}) - Status: {member["status_message"]}')

if __name__ == "__main__":
    main()