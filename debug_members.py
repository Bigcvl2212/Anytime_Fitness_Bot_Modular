#!/usr/bin/env python3
import psycopg2
import psycopg2.extras
import os

# Connect to PostgreSQL
conn = psycopg2.connect(
    host='34.31.91.96',
    port=5432,
    database='gym_bot',
    user='postgres',
    password='GymBot2025!'
)

try:
    # Check member_categories table
    cur = conn.cursor(psycopg2.extras.RealDictCursor)
    cur.execute('SELECT COUNT(*) as count FROM member_categories')
    result = cur.fetchone()
    print(f'Member categories count: {result["count"]}')

    # Check some sample members and their status messages
    cur.execute('SELECT prospect_id, first_name, last_name, status_message FROM members ORDER BY created_at DESC LIMIT 10')
    members = cur.fetchall()
    print('\nSample members and status messages:')
    for member in members:
        print(f'{member["first_name"]} {member["last_name"]}: {member["status_message"]}')

    # Check unique status messages 
    cur.execute('SELECT status_message, COUNT(*) as count FROM members WHERE status_message IS NOT NULL GROUP BY status_message ORDER BY count DESC')
    status_messages = cur.fetchall()
    print('\nAll status messages in database:')
    for sm in status_messages:
        print(f'{sm["status_message"]}: {sm["count"]}')
        
    # Let's manually categorize a few members and populate member_categories
    print('\nTesting categorization logic...')
    cur.execute('SELECT prospect_id, first_name, last_name, status_message, status FROM members LIMIT 5')
    test_members = cur.fetchall()
    
    for member in test_members:
        status_message = str(member['status_message'] or '').lower()
        status = str(member['status'] or '').lower()
        
        # Apply categorization logic
        category = 'green'  # default
        
        if 'past due more than 30 days' in status_message:
            category = 'red'
        elif 'past due' in status_message:
            category = 'past_due'
        elif 'staff' in status_message or 'staff' in status:
            category = 'staff'
        elif 'comp' in status_message or 'comp' in status:
            category = 'comp'
        elif 'pay per visit' in status_message:
            category = 'ppv'
        elif 'good standing' in status_message:
            category = 'green'
            
        print(f'{member["first_name"]} {member["last_name"]}: {member["status_message"]} -> {category}')
        
        # Insert into member_categories
        try:
            cur.execute("""
                INSERT INTO member_categories (member_id, category, status_message, full_name, created_at) 
                VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)
                ON CONFLICT (member_id) DO UPDATE SET 
                    category = EXCLUDED.category,
                    status_message = EXCLUDED.status_message,
                    updated_at = CURRENT_TIMESTAMP
            """, (
                member['prospect_id'], 
                category, 
                member['status_message'], 
                f"{member['first_name']} {member['last_name']}"
            ))
        except Exception as e:
            print(f'Error inserting category for {member["first_name"]}: {e}')
    
    conn.commit()
    
    # Check if categories were inserted
    cur.execute('SELECT COUNT(*) as count FROM member_categories')
    result = cur.fetchone()
    print(f'\nMember categories count after manual insert: {result["count"]}')

except Exception as e:
    print(f'Error: {e}')
finally:
    conn.close()