#!/usr/bin/env python3

from src.services.database_manager import DatabaseManager
from src.config.environment_setup import load_environment_variables

load_environment_variables()
db_manager = DatabaseManager()

print("=== DEBUG: CHECKING ACTUAL MESSAGES IN DATABASE ===")

try:
    conn = db_manager.get_connection()
    cursor = db_manager.get_cursor(conn)
    
    # Check what's actually stored in messages table
    cursor.execute("SELECT id, from_user, content, delivery_status, timestamp FROM messages ORDER BY timestamp DESC LIMIT 10")
    messages = cursor.fetchall()
    
    print(f"Found {len(messages)} messages in database:")
    print()
    
    for i, msg in enumerate(messages):
        if hasattr(msg, 'keys'):
            # RealDictRow
            msg_id = msg.get('id', 'No ID')
            sender = msg.get('from_user', 'No sender')
            content = msg.get('content', 'No content')
            status = msg.get('delivery_status', 'unknown')
            timestamp = msg.get('timestamp', 'No timestamp')
        else:
            # Tuple
            msg_id = msg[0] if len(msg) > 0 else 'No ID'
            sender = msg[1] if len(msg) > 1 else 'No sender'  
            content = msg[2] if len(msg) > 2 else 'No content'
            status = msg[3] if len(msg) > 3 else 'unknown'
            timestamp = msg[4] if len(msg) > 4 else 'No timestamp'
        
        print(f"Message {i+1}:")
        print(f"  ID: {msg_id}")
        print(f"  From: {sender}")
        print(f"  Status: {status}")
        print(f"  Time: {timestamp}")
        print(f"  Content: {content}")
        print()
    
    conn.close()
    
    # Now test get_recent_message_threads to see what it returns
    print("\n=== TESTING get_recent_message_threads OUTPUT ===")
    threads = db_manager.get_recent_message_threads(limit=5)
    
    print(f"Found {len(threads)} threads:")
    print()
    
    for i, thread in enumerate(threads):
        latest_msg = thread.get('latest_message', {})
        print(f"Thread {i+1}:")
        print(f"  Member: {thread.get('member_name', 'Unknown')}")
        print(f"  Thread Type: {thread.get('thread_type', 'unknown')}")
        print(f"  Unread Count: {thread.get('unread_count', 0)}")
        print(f"  Latest Message Content: {latest_msg.get('message_content', 'No content')}")
        print(f"  Latest Message Sender Type: {latest_msg.get('sender_type', 'unknown')}")
        print()

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("=== DEBUG COMPLETE ===")