#!/usr/bin/env python3
import psycopg2
from datetime import datetime

print('🔍 DIRECT POSTGRESQL TEST')
print('=' * 40)

# Test direct PostgreSQL connection and simple queries
try:
    conn = psycopg2.connect(
        host='34.31.91.96',
        port=5432,
        dbname='gym_bot',
        user='postgres', 
        password='GymBot2025!'
    )
    cursor = conn.cursor()
    
    # Test 1: Simple SELECT
    print('Testing simple query...')
    cursor.execute('SELECT 1 as test')
    result = cursor.fetchone()
    print(f'✅ Simple query works: {result}')
    
    # Test 2: Parameterized query with %s
    print('\nTesting parameterized query with %s...')
    cursor.execute('SELECT %s as test_param', ('hello',))
    result = cursor.fetchone()
    print(f'✅ Parameterized query works: {result}')
    
    # Test 3: Check if members table exists and is empty
    print('\nChecking members table...')
    cursor.execute('SELECT COUNT(*) FROM members')
    count = cursor.fetchone()[0]
    print(f'✅ Members table exists, count: {count}')
    
    # Test 4: Try a simple INSERT with %s parameters
    print('\nTesting simple INSERT...')
    test_id = f'test_{int(datetime.now().timestamp())}'
    cursor.execute("""
        INSERT INTO members (prospect_id, first_name, last_name, created_at)
        VALUES (%s, %s, %s, %s)
    """, (test_id, 'Test', 'User', datetime.now()))
    
    cursor.execute('SELECT COUNT(*) FROM members')
    count = cursor.fetchone()[0]
    print(f'✅ INSERT successful, new count: {count}')
    
    # Clean up test record
    cursor.execute('DELETE FROM members WHERE prospect_id = %s', (test_id,))
    conn.commit()
    print('✅ Test record cleaned up')
    
    conn.close()
    print('\n🎯 Direct PostgreSQL operations work fine!')
    print('❌ The issue is in our Python code, not PostgreSQL')
    
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()