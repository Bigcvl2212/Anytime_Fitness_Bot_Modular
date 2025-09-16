#!/usr/bin/env python3
"""
Migration script to copy training clients from SQLite to PostgreSQL
"""

import os
import sys
import sqlite3
import psycopg2
from datetime import datetime

# Add src to path to enable imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.config.environment_setup import load_environment_variables

def migrate_training_clients():
    """Migrate training clients from SQLite to PostgreSQL"""
    print("🚀 Starting migration of training clients from SQLite to PostgreSQL...")
    
    # Load environment variables
    load_environment_variables()
    
    # SQLite connection
    project_root = os.path.dirname(os.path.abspath(__file__))
    sqlite_path = os.path.join(project_root, 'gym_bot.db')
    
    if not os.path.exists(sqlite_path):
        print(f"❌ SQLite database not found at: {sqlite_path}")
        return False
    
    # PostgreSQL connection
    postgres_config = {
        'host': os.getenv('DB_HOST'),
        'port': os.getenv('DB_PORT', 5432),
        'dbname': os.getenv('DB_NAME'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD')
    }
    
    try:
        # Connect to SQLite
        print("📁 Connecting to SQLite database...")
        sqlite_conn = sqlite3.connect(sqlite_path)
        sqlite_cursor = sqlite_conn.cursor()
        
        # Connect to PostgreSQL
        print("🐘 Connecting to PostgreSQL database...")
        pg_conn = psycopg2.connect(**postgres_config)
        pg_cursor = pg_conn.cursor()
        
        # Get SQLite table structure
        sqlite_cursor.execute("PRAGMA table_info(training_clients);")
        sqlite_columns = [col[1] for col in sqlite_cursor.fetchall()]
        print(f"📁 SQLite columns: {sqlite_columns}")
        
        # Get all training clients from SQLite
        sqlite_cursor.execute("SELECT * FROM training_clients;")
        sqlite_clients = sqlite_cursor.fetchall()
        
        print(f"📁 Found {len(sqlite_clients)} training clients in SQLite")
        
        if len(sqlite_clients) == 0:
            print("ℹ️ No training clients to migrate")
            return True
        
        # Clear existing PostgreSQL data (optional)
        print("🧹 Clearing existing PostgreSQL training_clients...")
        pg_cursor.execute("DELETE FROM training_clients;")
        
        # Prepare insert statement for PostgreSQL
        # Map SQLite columns to PostgreSQL columns
        insert_query = """
        INSERT INTO training_clients (
            member_id, clubos_member_id, first_name, last_name, full_name, member_name,
            email, phone, status, training_package, trainer_name, membership_type,
            source, active_packages, package_summary, package_details,
            past_due_amount, total_past_due, payment_status, sessions_remaining,
            last_session, financial_summary, last_updated, created_at, updated_at
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        """
        
        # Migrate each client
        migrated_count = 0
        error_count = 0
        
        for i, client in enumerate(sqlite_clients):
            try:
                # Map SQLite row to PostgreSQL columns
                # Assuming SQLite has similar structure - adjust indices as needed
                if len(client) >= 25:  # Ensure we have enough columns
                    pg_cursor.execute(insert_query, client[1:])  # Skip SQLite id (auto-increment)
                    migrated_count += 1
                    
                    if (i + 1) % 10 == 0:
                        print(f"✅ Migrated {i + 1}/{len(sqlite_clients)} clients...")
                else:
                    print(f"⚠️ Skipping client {i+1} - insufficient columns: {len(client)}")
                    error_count += 1
                    
            except Exception as e:
                print(f"❌ Error migrating client {i+1}: {e}")
                error_count += 1
                continue
        
        # Commit the transaction
        pg_conn.commit()
        
        # Verify migration
        pg_cursor.execute("SELECT COUNT(*) FROM training_clients;")
        pg_count = pg_cursor.fetchone()[0]
        
        print(f"\n🎉 Migration completed!")
        print(f"✅ Successfully migrated: {migrated_count} clients")
        print(f"❌ Errors: {error_count}")
        print(f"🐘 PostgreSQL now has: {pg_count} training clients")
        
        # Show sample of migrated data
        if pg_count > 0:
            pg_cursor.execute("SELECT member_name, first_name, last_name, email FROM training_clients LIMIT 5;")
            sample_clients = pg_cursor.fetchall()
            print("\nSample migrated clients:")
            for client in sample_clients:
                print(f"  - {client[0]} ({client[1]} {client[2]}) - {client[3]}")
        
        # Close connections
        sqlite_cursor.close()
        sqlite_conn.close()
        pg_cursor.close()
        pg_conn.close()
        
        return migrated_count > 0
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

if __name__ == '__main__':
    success = migrate_training_clients()
    if success:
        print("\n✅ Migration completed successfully!")
    else:
        print("\n❌ Migration failed!")