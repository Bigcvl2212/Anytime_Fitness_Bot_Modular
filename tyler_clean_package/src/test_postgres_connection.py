#!/usr/bin/env python3
"""
Test PostgreSQL connectivity with various common configurations
"""

import psycopg2
import os
import sys

def test_postgres_connection():
    """Test PostgreSQL connections with various configurations"""
    
    # Check common PostgreSQL configurations
    configs = [
        {'host': 'localhost', 'port': 5432, 'dbname': 'postgres', 'user': 'postgres', 'password': ''},
        {'host': 'localhost', 'port': 5432, 'dbname': 'postgres', 'user': 'postgres', 'password': 'postgres'},
        {'host': 'localhost', 'port': 5432, 'dbname': 'postgres', 'user': 'postgres', 'password': 'password'},
    ]

    # Also check environment variables
    env_config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': int(os.getenv('DB_PORT', '5432')),
        'dbname': os.getenv('DB_NAME', 'gym_bot'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', '')
    }

    all_configs = configs + [env_config]

    for i, config in enumerate(all_configs):
        try:
            print(f"Testing config {i+1}: {config['user']}@{config['host']}:{config['port']}/{config['dbname']}")
            conn = psycopg2.connect(**config)
            conn.close()
            print(f'✅ PostgreSQL connection successful with config {i+1}')
            print(f'   Host: {config["host"]}:{config["port"]}')
            print(f'   Database: {config["dbname"]}')
            print(f'   User: {config["user"]}')
            return config
        except psycopg2.Error as e:
            print(f'❌ Config {i+1} failed: {str(e).strip()}')
        except Exception as e:
            print(f'❌ Config {i+1} error: {e}')

    print()
    print('⚠️ No PostgreSQL connection found. You may need to:')
    print('   1. Install PostgreSQL server')
    print('   2. Start PostgreSQL service')  
    print('   3. Configure connection credentials')
    return None

if __name__ == '__main__':
    working_config = test_postgres_connection()
    if working_config:
        sys.exit(0)
    else:
        sys.exit(1)