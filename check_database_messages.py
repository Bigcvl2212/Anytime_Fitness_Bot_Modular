#!/usr/bin/env python3
"""
Check database messages to understand what's available
"""
import sqlite3
import json
from datetime import datetime

def check_database_messages():
    """Check what messages are in the database"""
    
    db_path = r"c:\Users\mayoj\OneDrive\Documents\Gym-Bot\gym-bot\gym-bot-modular\gym_bot.db"
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get total message count
        cursor.execute("SELECT COUNT(*) as total FROM messages")
        total = cursor.fetchone()['total']
        print(f"📊 Total messages in database: {total}")
        
        if total > 0:
            # Get recent messages
            cursor.execute("""
                SELECT id, member_id, owner_id, from_user, to_user, content, created_at, message_type, status 
                FROM messages 
                ORDER BY created_at DESC 
                LIMIT 10
            """)
            
            recent_messages = cursor.fetchall()
            print(f"\n📋 Recent 10 messages:")
            for msg in recent_messages:
                print(f"  • ID: {msg['id']}, Member: {msg['member_id']}, Owner: {msg['owner_id']}")
                print(f"    From: {msg['from_user']} → To: {msg['to_user']}")
                print(f"    Content: {msg['content'][:60]}...")
                print(f"    Type: {msg['message_type']}, Status: {msg['status']}")
                print(f"    Created: {msg['created_at']}\n")
            
            # Check specific member IDs
            test_members = ['149169', '999', 'test_member']
            for member_id in test_members:
                cursor.execute("""
                    SELECT COUNT(*) as count FROM messages 
                    WHERE member_id = ? OR owner_id = ? OR content LIKE ? OR from_user LIKE ?
                """, (member_id, member_id, f'%{member_id}%', f'%{member_id}%'))
                
                count = cursor.fetchone()['count']
                print(f"🔍 Messages for member '{member_id}': {count}")
                
                if count > 0:
                    cursor.execute("""
                        SELECT from_user, content, created_at FROM messages 
                        WHERE member_id = ? OR owner_id = ? OR content LIKE ? OR from_user LIKE ?
                        ORDER BY created_at DESC LIMIT 3
                    """, (member_id, member_id, f'%{member_id}%', f'%{member_id}%'))
                    
                    member_messages = cursor.fetchall()
                    for msg in member_messages:
                        print(f"    • {msg['from_user']}: {msg['content'][:50]}... ({msg['created_at']})")
                    print()
        
        # Check table structure
        cursor.execute("PRAGMA table_info(messages)")
        columns = cursor.fetchall()
        print(f"📋 Messages table structure:")
        for col in columns:
            print(f"  • {col['name']} ({col['type']})")
            
        conn.close()
        
    except Exception as e:
        print(f"❌ Database error: {e}")

if __name__ == "__main__":
    check_database_messages()