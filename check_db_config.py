#!/usr/bin/env python3
"""
Check database configuration in Flask app context
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set the database type environment variable
os.environ['DB_TYPE'] = 'postgresql'

from src.app import create_app
app = create_app()

with app.app_context():
    from flask import current_app
    
    print("🔍 Checking database configuration...")
    print(f"DB_TYPE env var: {os.getenv('DB_TYPE')}")
    print(f"DATABASE_TYPE env var: {os.getenv('DATABASE_TYPE')}")
    
    if hasattr(current_app, 'db_manager'):
        db_mgr = current_app.db_manager
        print(f"App db_manager db_type: {db_mgr.db_type}")
        
        if db_mgr.db_type == 'postgresql':
            print(f"PostgreSQL config: {db_mgr.postgres_config}")
            
            # Test connection
            try:
                conn = db_mgr.get_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM training_clients")
                count = cursor.fetchone()[0]
                print(f"✅ PostgreSQL connection works: {count} training clients")
                conn.close()
            except Exception as e:
                print(f"❌ PostgreSQL connection failed: {e}")
        else:
            print(f"❌ Using SQLite instead of PostgreSQL")
    else:
        print("❌ No db_manager found in current_app")