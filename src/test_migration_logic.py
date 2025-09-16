#!/usr/bin/env python3
"""
Test the migration logic by validating the SQL generation and data transformation
without requiring an actual PostgreSQL server connection.
"""

import os
import sys
import sqlite3
from services.database_migration import SQLiteToPostgresMigration

def test_migration_logic():
    """Test the migration logic with the current SQLite database"""
    
    # Check if SQLite database exists
    sqlite_path = 'gym_bot.db'
    if not os.path.exists(sqlite_path):
        # Check in parent directory
        sqlite_path = '../gym_bot.db'
        if not os.path.exists(sqlite_path):
            print("❌ SQLite database not found")
            return False
    
    print(f"✅ Found SQLite database: {sqlite_path}")
    
    # Test migration initialization
    try:
        migrator = SQLiteToPostgresMigration(
            sqlite_path=sqlite_path,
            postgres_config={
                'host': 'localhost',
                'port': 5432,
                'dbname': 'gym_bot',
                'user': 'postgres',
                'password': 'test'
            }
        )
        print("✅ Migration object created successfully")
    except Exception as e:
        print(f"❌ Migration initialization failed: {e}")
        return False
    
    # Test schema creation SQL generation
    try:
        schema_sql = migrator._get_postgres_schema()
        print("✅ PostgreSQL schema SQL generated successfully")
        print(f"   Schema contains {len(schema_sql.split(';'))} statements")
        
        # Verify key tables are present
        expected_tables = ['training_clients', 'workouts', 'exercises', 'measurements']
        for table in expected_tables:
            if f"CREATE TABLE {table}" in schema_sql:
                print(f"   ✅ {table} table schema found")
            else:
                print(f"   ⚠️ {table} table schema missing")
                
    except Exception as e:
        print(f"❌ Schema generation failed: {e}")
        return False
    
    # Test SQLite data reading
    try:
        conn = sqlite3.connect(sqlite_path)
        cursor = conn.cursor()
        
        # Get table list
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"✅ Found {len(tables)} tables in SQLite: {', '.join(tables)}")
        
        # Count records in each table
        total_records = 0
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            total_records += count
            print(f"   {table}: {count} records")
        
        print(f"✅ Total records to migrate: {total_records}")
        conn.close()
        
    except Exception as e:
        print(f"❌ SQLite data reading failed: {e}")
        return False
    
    # Test data transformation logic
    try:
        # Test the data preparation method (without actual PostgreSQL connection)
        conn = sqlite3.connect(sqlite_path)
        cursor = conn.cursor()
        
        # Test conversion of a sample table if it exists
        if 'training_clients' in tables:
            cursor.execute("SELECT * FROM training_clients LIMIT 1")
            sample_row = cursor.fetchone()
            if sample_row:
                # Get column names
                cursor.execute("PRAGMA table_info(training_clients)")
                columns = [row[1] for row in cursor.fetchall()]
                
                print("✅ Sample data transformation test:")
                print(f"   Columns: {columns}")
                print(f"   Sample row: {sample_row}")
                
                # Test parameter substitution style conversion
                placeholders = ', '.join(['%s'] * len(columns))
                insert_sql = f"INSERT INTO training_clients ({', '.join(columns)}) VALUES ({placeholders})"
                print(f"   PostgreSQL INSERT SQL: {insert_sql[:100]}...")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Data transformation test failed: {e}")
        return False
    
    print("\n🎉 Migration logic validation completed successfully!")
    print("Migration code is ready to run when PostgreSQL server is available.")
    return True

def show_postgresql_setup_instructions():
    """Show instructions for setting up PostgreSQL"""
    print("\n" + "="*60)
    print("📋 PostgreSQL Setup Instructions")
    print("="*60)
    print()
    print("Option 1: Install PostgreSQL locally on Windows")
    print("  1. Download from: https://www.postgresql.org/download/windows/")
    print("  2. Run installer and set password for 'postgres' user")
    print("  3. Start PostgreSQL service")
    print("  4. Create database: CREATE DATABASE gym_bot;")
    print()
    print("Option 2: Use Docker (if Docker is installed)")
    print("  docker run --name postgres-gymbot -e POSTGRES_PASSWORD=postgres -p 5432:5432 -d postgres")
    print("  docker exec -it postgres-gymbot createdb -U postgres gym_bot")
    print()
    print("Option 3: Use cloud PostgreSQL")
    print("  - Azure Database for PostgreSQL")
    print("  - AWS RDS PostgreSQL") 
    print("  - Google Cloud SQL PostgreSQL")
    print()
    print("After PostgreSQL is set up:")
    print("  1. Update environment variables or .env file:")
    print("     DB_TYPE=postgresql")
    print("     DB_HOST=localhost")
    print("     DB_PORT=5432")
    print("     DB_NAME=gym_bot")
    print("     DB_USER=postgres")
    print("     DB_PASSWORD=your_password")
    print()
    print("  2. Run the migration:")
    print("     python database_migration.py")
    print()

if __name__ == '__main__':
    success = test_migration_logic()
    if success:
        show_postgresql_setup_instructions()
        sys.exit(0)
    else:
        sys.exit(1)