#!/usr/bin/env python3
import psycopg2
import psycopg2.extras

# Connect to PostgreSQL
conn = psycopg2.connect(
    host='34.31.91.96',
    port=5432,
    database='gym_bot',
    user='postgres',
    password='GymBot2025!',
    sslmode='require'
)

try:
    # Check current state
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute('SELECT COUNT(*) as count FROM member_categories')
    result = cur.fetchone()
    print(f'Current member categories count: {result["count"]}')

    # Check members count
    cur.execute('SELECT COUNT(*) as count FROM members')
    result = cur.fetchone()
    print(f'Total members in database: {result["count"]}')

    # Check some status messages
    cur.execute('SELECT status_message, COUNT(*) as count FROM members WHERE status_message IS NOT NULL GROUP BY status_message ORDER BY count DESC LIMIT 10')
    status_messages = cur.fetchall()
    print('\nTop 10 status messages:')
    for sm in status_messages:
        print(f'  "{sm["status_message"]}": {sm["count"]}')

    # Let's categorize ALL members at once
    print('\nCategorizing all members...')
    
    # Use regular cursor for bulk operations
    cur = conn.cursor()
    
    # First, clear existing categories
    cur.execute('TRUNCATE TABLE member_categories')
    
    # Get all members and categorize them
    cur.execute('SELECT prospect_id, first_name, last_name, status_message, status FROM members WHERE prospect_id IS NOT NULL')
    members = cur.fetchall()
    
    print(f'Processing {len(members)} members...')
    
    categories_to_insert = []
    category_counts = {'green': 0, 'past_due': 0, 'red': 0, 'comp': 0, 'ppv': 0, 'staff': 0, 'inactive': 0}
    
    for member in members:
        prospect_id, first_name, last_name, status_message, status = member
        
        status_message_lower = str(status_message or '').lower()
        status_lower = str(status or '').lower()
        
        # Apply categorization logic (same as in your database_manager.py)
        category = 'green'  # default
        
        if 'past due more than 30 days' in status_message_lower:
            category = 'red'
        elif 'past due' in status_message_lower:
            category = 'past_due'
        elif 'staff' in status_message_lower or 'staff' in status_lower:
            category = 'staff'
        elif 'comp' in status_message_lower or 'comp' in status_lower:
            category = 'comp'
        elif 'pay per visit' in status_message_lower:
            category = 'ppv'
        elif any(inactive in status_message_lower for inactive in ['cancelled', 'cancel', 'expire', 'pending', 'suspended']):
            category = 'inactive'
        elif 'good standing' in status_message_lower:
            category = 'green'
            
        full_name = f"{first_name or ''} {last_name or ''}".strip()
        
        categories_to_insert.append((
            prospect_id, 
            category, 
            status_message, 
            full_name
        ))
        category_counts[category] += 1
    
    # Bulk insert categories
    cur.executemany("""
        INSERT INTO member_categories (member_id, category, status_message, full_name, created_at) 
        VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)
    """, categories_to_insert)
    
    conn.commit()
    
    print(f'\nSuccessfully categorized {len(categories_to_insert)} members!')
    print('Category breakdown:')
    for category, count in category_counts.items():
        print(f'  {category}: {count}')
    
    # Verify the results
    cur.execute('SELECT COUNT(*) FROM member_categories')
    final_count = cur.fetchone()[0]
    print(f'\nFinal member_categories count: {final_count}')

except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
finally:
    conn.close()