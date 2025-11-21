#!/usr/bin/env python3
"""
Script to sync training clients from SQLite to PostgreSQL
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.database_manager import DatabaseManager
import psycopg2
import sqlite3
import json

print("🔄 Syncing training clients from SQLite to PostgreSQL...")

# Initialize database manager (SQLite)
sqlite_db_manager = DatabaseManager()

# Get PostgreSQL connection details
try:
    # Get all training clients from SQLite
    print("📖 Reading training clients from SQLite...")
    sqlite_training_clients = sqlite_db_manager.execute_query("""
        SELECT * FROM training_clients ORDER BY created_at DESC
    """)
    
    if not sqlite_training_clients:
        print("❌ No training clients found in SQLite database")
        exit(1)
        
    print(f"✅ Found {len(sqlite_training_clients)} training clients in SQLite")
    
    # Get PostgreSQL connection using database manager's method
    print("🔌 Connecting to PostgreSQL...")
    pg_conn = sqlite_db_manager.get_connection()  # This should return PostgreSQL connection
    pg_cursor = pg_conn.cursor()
    
    # Check if training_clients table exists in PostgreSQL
    pg_cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'training_clients'
        );
    """)
    table_exists = pg_cursor.fetchone()[0]
    
    if not table_exists:
        print("📋 Creating training_clients table in PostgreSQL...")
        # Create table based on SQLite schema
        pg_cursor.execute("""
            CREATE TABLE training_clients (
                id SERIAL PRIMARY KEY,
                member_id TEXT,
                prospect_id TEXT,
                member_name TEXT,
                first_name TEXT,
                last_name TEXT,
                full_name TEXT,
                email TEXT,
                phone TEXT,
                package_details JSONB,
                payment_status TEXT,
                total_past_due DECIMAL(10,2) DEFAULT 0.00,
                sessions_remaining INTEGER DEFAULT 0,
                trainer_name TEXT DEFAULT 'Jeremy Mayo',
                active_packages TEXT,
                last_session TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("✅ Created training_clients table in PostgreSQL")
    else:
        print("📋 training_clients table already exists in PostgreSQL")
    
    # Clear existing data and insert SQLite data
    print("🗑️ Clearing existing training clients in PostgreSQL...")
    pg_cursor.execute("DELETE FROM training_clients")
    
    print("📥 Inserting training clients into PostgreSQL...")
    inserted_count = 0
    
    for client in sqlite_training_clients:
        try:
            # Handle the package_details JSON field
            package_details = client.get('package_details')
            if package_details and isinstance(package_details, str):
                try:
                    # Validate it's valid JSON
                    json.loads(package_details)
                except json.JSONDecodeError:
                    package_details = None
            
            pg_cursor.execute("""
                INSERT INTO training_clients 
                (member_id, prospect_id, member_name, first_name, last_name, full_name, 
                 email, phone, package_details, payment_status, total_past_due, 
                 sessions_remaining, trainer_name, active_packages, last_session, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                client.get('member_id'),
                client.get('prospect_id'), 
                client.get('member_name'),
                client.get('first_name'),
                client.get('last_name'),
                client.get('full_name'),
                client.get('email'),
                client.get('phone'),
                package_details,
                client.get('payment_status'),
                float(client.get('total_past_due', 0)) if client.get('total_past_due') else 0.0,
                int(client.get('sessions_remaining', 0)) if client.get('sessions_remaining') else 0,
                client.get('trainer_name', 'Jeremy Mayo'),
                client.get('active_packages'),
                client.get('last_session'),
                client.get('created_at'),
                client.get('updated_at', client.get('created_at'))
            ))
            inserted_count += 1
            
        except Exception as insert_error:
            print(f"⚠️ Error inserting client {client.get('member_name', 'Unknown')}: {insert_error}")
    
    # Commit the changes
    pg_conn.commit()
    print(f"✅ Successfully inserted {inserted_count} training clients into PostgreSQL")
    
    # Verify the data
    pg_cursor.execute("SELECT COUNT(*) FROM training_clients")
    pg_count = pg_cursor.fetchone()[0]
    print(f"📊 Verification: {pg_count} training clients now in PostgreSQL")
    
    # Test a few specific names
    test_names = ['David Berendt', 'Alejandra Espinoza', 'Grace Sphatt', 'Dennis Rost']
    print(f"\n🔍 Testing specific name lookups in PostgreSQL:")
    
    for name in test_names:
        pg_cursor.execute("""
            SELECT member_name, first_name, last_name, total_past_due
            FROM training_clients 
            WHERE LOWER(member_name) LIKE LOWER(%s) 
            LIMIT 1
        """, (f'%{name}%',))
        
        result = pg_cursor.fetchone()
        if result:
            print(f"  ✅ Found '{name}': {result[0]} (Past due: ${result[3]})")
        else:
            print(f"  ❌ Not found: '{name}'")
    
    pg_cursor.close()
    pg_conn.close()
    print("\n🎉 Migration completed successfully!")
    
except Exception as e:
    print(f"❌ Error during migration: {e}")
    import traceback
    traceback.print_exc()