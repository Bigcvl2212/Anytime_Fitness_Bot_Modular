#!/usr/bin/env python3

import os
import sys
import json
import socket
sys.path.append('src')

from src.config.environment_setup import load_environment_variables
load_environment_variables()

from src.services.authentication.secure_secrets_manager import SecureSecretsManager

def diagnose_database():
    """Diagnose database connection issues"""
    print("🔍 Diagnosing database connection...")
    
    # First check environment variables
    print("\n📋 Checking environment variables...")
    env_vars = {
        'DATABASE_CONFIG': os.environ.get('DATABASE_CONFIG'),
        'DB_HOST': os.environ.get('DB_HOST'),
        'DB_PORT': os.environ.get('DB_PORT'),
        'DB_DATABASE': os.environ.get('DB_DATABASE'),
        'DB_USERNAME': os.environ.get('DB_USERNAME'),
        'DB_PASSWORD': os.environ.get('DB_PASSWORD')
    }
    
    found_env_vars = {k: v for k, v in env_vars.items() if v is not None}
    if found_env_vars:
        print('✅ Found environment variables:')
        for k, v in found_env_vars.items():
            if 'PASSWORD' in k:
                print(f'  {k}: {"*" * min(len(v), 10) if v else "NOT SET"}')
            else:
                print(f'  {k}: {v}')
    else:
        print('❌ No database environment variables found')
    
    # Check what database config we have from secrets manager
    print("\n🔒 Checking Google Secret Manager...")
    secrets_manager = SecureSecretsManager()
    db_config = None
    
    try:
        # Try to get database config as JSON
        db_config_str = secrets_manager.get_secret('database-config')
        if db_config_str:
            try:
                db_config = json.loads(db_config_str)
                print('✅ Database config found in Secret Manager:')
                print(f'  Host: {db_config.get("host", "NOT SET")}')
                print(f'  Port: {db_config.get("port", "NOT SET")}')
                print(f'  Database: {db_config.get("database", "NOT SET")}')
                print(f'  Username: {db_config.get("username", "NOT SET")}')
                print(f'  Password: {"SET" if db_config.get("password") else "NOT SET"}')
            except json.JSONDecodeError:
                print(f'✅ Database config found but not JSON: {db_config_str[:50]}...')
                db_config = None
        else:
            print('❌ No database-config secret found in Secret Manager')
            db_config = None
            
        # Test connection if we have config
        if db_config:
            host = db_config.get("host")
            port = int(db_config.get("port", 5432))
            
            print(f"\n🌐 Testing network connectivity to {host}:{port}...")
            try:
                sock = socket.create_connection((host, port), timeout=10)
                sock.close()
                print("✅ Network connection successful")
                
                # Test PostgreSQL connection
                print("\n🐘 Testing PostgreSQL connection...")
                import psycopg2
                conn = psycopg2.connect(
                    host=host,
                    port=port,
                    database=db_config.get("database"),
                    user=db_config.get("username"),
                    password=db_config.get("password")
                )
                cursor = conn.cursor()
                cursor.execute("SELECT version();")
                version = cursor.fetchone()
                print(f"✅ PostgreSQL connection successful: {version[0]}")
                cursor.close()
                conn.close()
                
            except socket.timeout:
                print("❌ Network connection timed out - database server may be down or unreachable")
            except socket.error as e:
                print(f"❌ Network connection failed: {e}")
            except Exception as e:
                print(f"❌ Database connection failed: {e}")
        else:
            print("\n⚠️ No database configuration found - cannot test connection")
            
    except Exception as e:
        print(f'❌ Error during diagnosis: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    diagnose_database()