#!/usr/bin/env python3
"""Quick script to reset recent messages for AI reprocessing"""

from src.services.database_manager import DatabaseManager
db = DatabaseManager()

# Reset the most recent messages so they can be reprocessed
result = db.execute_query('''
    UPDATE messages 
    SET ai_processed = 0, ai_response = NULL, ai_response_time = NULL
    WHERE id IN (
        SELECT id FROM messages 
        WHERE from_user IN ('Unknown', 'Mary Siegmann')
        ORDER BY timestamp DESC 
        LIMIT 10
    )
''')
print(f'Reset recent messages for reprocessing: {result}')

# Check status
rows = db.execute_query('''
    SELECT id, from_user, content, ai_processed 
    FROM messages 
    WHERE from_user IN ('Unknown', 'Mary Siegmann') 
    ORDER BY timestamp DESC 
    LIMIT 5
''', fetch_all=True)
print('\nRecent messages:')
for r in (rows or []):
    d = dict(r)
    print(f"  ai_processed={d['ai_processed']}, from={d['from_user']!r}, content={d['content'][:40]}...")
