#!/usr/bin/env python3
from main_app import create_app
import psycopg2
from datetime import datetime

app = create_app()
with app.app_context():
    print('🔍 DEBUG MEMBER INSERT')
    print('=' * 40)
    
    # Get the actual data from API
    print('Fetching fresh data...')
    fresh_data = app.db_manager.get_fresh_data_from_clubos()
    
    if not fresh_data or not fresh_data.get('members'):
        print('❌ No fresh data available')
        exit(1)
    
    # Get just the first member for testing
    test_member = fresh_data['members'][0]
    print(f'Test member data: {test_member}')
    
    # Test PostgreSQL connection
    conn = psycopg2.connect(
        host='34.31.91.96',
        port=5432,
        dbname='gym_bot',
        user='postgres', 
        password='GymBot2025!'
    )
    cursor = conn.cursor()
    
    # Prepare the data exactly as our code does
    member_data = (
        test_member.get('ProspectID'),
        test_member.get('FirstName'),
        test_member.get('LastName'),
        test_member.get('Name'),
        test_member.get('Email'),
        test_member.get('Phone'),
        test_member.get('MobilePhone'),
        test_member.get('Status'),
        test_member.get('StatusMessage'),
        test_member.get('MembershipType'),
        test_member.get('MemberSince'),
        float(test_member.get('AmountPastDue', 0) or 0),
        test_member.get('NextPaymentDate'),
        datetime.now(),
        datetime.now()
    )
    
    print(f'\nMember data tuple:')
    for i, value in enumerate(member_data):
        print(f'  {i}: {repr(value)}')
    
    # Try the exact INSERT query from our code
    try:
        print('\nTesting INSERT query...')
        insert_query = """
            INSERT INTO members (
                prospect_id, first_name, last_name, full_name, email, phone, mobile_phone,
                status, status_message, member_type, join_date, amount_past_due,
                date_of_next_payment, created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        cursor.execute(insert_query, member_data)
        conn.commit()
        
        cursor.execute('SELECT COUNT(*) FROM members')
        count = cursor.fetchone()[0]
        print(f'✅ INSERT successful! Members count: {count}')
        
        # Show the inserted record
        cursor.execute('SELECT prospect_id, first_name, last_name, email FROM members LIMIT 1')
        record = cursor.fetchone()
        print(f'✅ Inserted record: {record}')
        
    except Exception as e:
        print(f'❌ INSERT failed: {e}')
        import traceback
        traceback.print_exc()
        
        # Check for problematic data values
        print('\nChecking for problematic values:')
        for i, value in enumerate(member_data):
            if isinstance(value, str) and '%' in value:
                print(f'  Found % in value {i}: {repr(value)}')
    
    conn.close()