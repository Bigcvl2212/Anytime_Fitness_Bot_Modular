#!/usr/bin/env python3
"""
Test script to verify environment configuration and database connection
"""

import os
import sys

# Add src to path to enable imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.config.environment_setup import load_environment_variables
from src.services.database_manager import DatabaseManager

def test_environment_config():
    """Test if environment variables are loaded correctly"""
    print("🧪 Testing environment configuration...")
    
    # Load environment variables
    env_loaded = load_environment_variables()
    print(f"Environment file loaded: {env_loaded}")
    
    # Check key environment variables
    db_type = os.getenv('DB_TYPE', 'not_set')
    db_host = os.getenv('DB_HOST', 'not_set')
    db_port = os.getenv('DB_PORT', 'not_set')
    db_name = os.getenv('DB_NAME', 'not_set')
    db_user = os.getenv('DB_USER', 'not_set')
    
    print(f"DB_TYPE: {db_type}")
    print(f"DB_HOST: {db_host}")
    print(f"DB_PORT: {db_port}")
    print(f"DB_NAME: {db_name}")
    print(f"DB_USER: {db_user}")
    
    return db_type == 'postgresql'

def test_database_connection():
    """Test database connection using DatabaseManager"""
    print("\n🔌 Testing database connection...")
    
    try:
        # Initialize DatabaseManager (should use PostgreSQL based on environment)
        db_manager = DatabaseManager()
        
        # Test connection
        conn = db_manager.get_connection()
        print(f"✅ Database connection successful!")
        print(f"Connection type: {type(conn)}")
        
        # Test a simple query
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"PostgreSQL Version: {version[0]}")
        
        # Test if training_clients table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'training_clients'
            );
        """)
        table_exists = cursor.fetchone()[0]
        print(f"training_clients table exists: {table_exists}")
        
        if table_exists:
            cursor.execute("SELECT COUNT(*) FROM training_clients;")
            count = cursor.fetchone()[0]
            print(f"training_clients count: {count}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

if __name__ == '__main__':
    print("🚀 Starting environment and database tests...\n")
    
    # Test environment configuration
    env_ok = test_environment_config()
    
    if env_ok:
        # Test database connection
        db_ok = test_database_connection()
        
        if db_ok:
            print("\n✅ All tests passed! PostgreSQL configuration is working.")
        else:
            print("\n❌ Database connection test failed. Check PostgreSQL settings.")
    else:
        print("\n❌ Environment configuration test failed. Check .env file.")