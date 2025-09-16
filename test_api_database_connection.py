#!/usr/bin/env python3
"""
Test the database connection that the API routes should be using
"""

import os
import sys
import sqlite3
from src.services.database_manager import DatabaseManager

def test_training_clients_api():
    """Test what the /api/training/clients route should return"""
    
    # Initialize DatabaseManager with absolute path (same fix we applied)
    project_root = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(project_root, 'gym_bot.db')
    
    print(f"📁 Database path: {db_path}")
    print(f"📁 Database exists: {os.path.exists(db_path)}")
    
    # Initialize database manager with absolute path
    db_manager = DatabaseManager(db_path=db_path)
    
    try:
        # Get training clients from database (exact same query as the route)
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        # Same query as in the route
        cursor.execute("""
            SELECT tc.*, m.first_name, m.last_name, m.full_name, m.email, m.mobile_phone, m.status_message
            FROM training_clients tc
            LEFT JOIN members m ON (tc.member_id = m.guid OR tc.member_id = m.prospect_id)
            ORDER BY tc.member_name, tc.created_at DESC
        """)
        
        training_clients = []
        for row in cursor.fetchall():
            client = dict(row)
            
            # Same processing as in the route
            client['member_name'] = (client.get('member_name') or 
                                   client.get('full_name') or 
                                   f"{client.get('first_name', '')} {client.get('last_name', '')}".strip() or
                                   f"Training Client #{str(client.get('clubos_member_id', 'Unknown'))[-4:]}")
            
            client['member_id'] = client.get('clubos_member_id') or client.get('member_id')
            client['prospect_id'] = client.get('clubos_member_id') or client.get('prospect_id')
            client['payment_status'] = client.get('payment_status') or 'Current'
            client['total_past_due'] = float(client.get('total_past_due', 0))
            client['past_due_amount'] = float(client.get('past_due_amount', 0))
            client['trainer_name'] = client.get('trainer_name') or 'Jeremy Mayo'
            client['sessions_remaining'] = client.get('sessions_remaining') or 0
            client['last_session'] = client.get('last_session') or 'Never'
            
            training_clients.append(client)
        
        conn.close()
        
        print(f"✅ Found {len(training_clients)} training clients in database")
        
        # Show first few for debugging
        for i, client in enumerate(training_clients[:3]):
            print(f"Training Client {i+1}: {client.get('member_name')} - Past Due: ${client.get('total_past_due', 0)}")
        
        # Return what the API should return
        result = {'success': True, 'training_clients': training_clients}
        print(f"\n🔥 API should return: {len(result['training_clients'])} training clients")
        
        return result
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return {'success': False, 'error': str(e)}

if __name__ == '__main__':
    test_training_clients_api()