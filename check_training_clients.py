#!/usr/bin/env python3
"""
Script to check training clients in both SQLite and PostgreSQL databases
"""

import os
import sys
import sqlite3
import psycopg2

# Add src to path to enable imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.config.environment_setup import load_environment_variables

def check_sqlite_training_clients():
    """Check training clients in local SQLite database"""
    print("🔍 Checking SQLite database for training clients...")
    
    try:
        # Find the SQLite database file
        project_root = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(project_root, 'gym_bot.db')
        
        if not os.path.exists(db_path):
            print(f"❌ SQLite database not found at: {db_path}")
            return []
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if training_clients table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='training_clients';")
        table_exists = cursor.fetchone()
        
        if not table_exists:
            print("❌ training_clients table does not exist in SQLite")
            return []
        
        # Get all training clients
        cursor.execute("SELECT COUNT(*) FROM training_clients;")
        count = cursor.fetchone()[0]
        print(f"📁 SQLite training_clients count: {count}")
        
        if count > 0:
            cursor.execute("SELECT member_name, first_name, last_name, email, created_at FROM training_clients LIMIT 5;")
            sample_clients = cursor.fetchall()
            print("Sample SQLite training clients:")
            for client in sample_clients:
                print(f"  - {client[0]} ({client[1]} {client[2]}) - {client[3]} - {client[4]}")
        
        # Get all training clients for potential migration
        cursor.execute("SELECT * FROM training_clients;")
        all_clients = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return all_clients
        
    except Exception as e:
        print(f"❌ Error checking SQLite database: {e}")
        return []

def check_postgresql_training_clients():
    """Check training clients in PostgreSQL database"""
    print("\n🐘 Checking PostgreSQL database for training clients...")
    
    try:
        # Load environment variables
        load_environment_variables()
        
        # Connect to PostgreSQL
        postgres_config = {
            'host': os.getenv('DB_HOST'),
            'port': os.getenv('DB_PORT', 5432),
            'dbname': os.getenv('DB_NAME'),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD')
        }
        
        print(f"Connecting to PostgreSQL: {postgres_config['host']}:{postgres_config['port']}/{postgres_config['dbname']}")
        
        conn = psycopg2.connect(**postgres_config)
        cursor = conn.cursor()
        
        # Check if training_clients table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'training_clients'
            );
        """)
        table_exists = cursor.fetchone()[0]
        
        if not table_exists:
            print("❌ training_clients table does not exist in PostgreSQL")
            return
        
        # Get all training clients
        cursor.execute("SELECT COUNT(*) FROM training_clients;")
        count = cursor.fetchone()[0]
        print(f"🐘 PostgreSQL training_clients count: {count}")
        
        if count > 0:
            cursor.execute("SELECT member_name, first_name, last_name, email, created_at FROM training_clients LIMIT 5;")
            sample_clients = cursor.fetchall()
            print("Sample PostgreSQL training clients:")
            for client in sample_clients:
                print(f"  - {client[0]} ({client[1]} {client[2]}) - {client[3]} - {client[4]}")
        
        # Show table structure
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_schema = 'public' 
            AND table_name = 'training_clients'
            ORDER BY ordinal_position;
        """)
        columns = cursor.fetchall()
        print("\nPostgreSQL training_clients table structure:")
        for column in columns:
            print(f"  - {column[0]}: {column[1]}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error checking PostgreSQL database: {e}")

if __name__ == '__main__':
    print("🚀 Checking training clients in both databases...\n")
    
    # Check SQLite first
    sqlite_clients = check_sqlite_training_clients()
    
    # Check PostgreSQL
    check_postgresql_training_clients()
    
    print(f"\n📊 Summary:")
    print(f"SQLite training clients: {len(sqlite_clients)}")
    print(f"Ready for migration: {len(sqlite_clients) > 0}")