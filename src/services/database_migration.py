#!/usr/bin/env python3
"""
PostgreSQL Migration Script for Gym-Bot
Safely migrates data from SQLite to PostgreSQL with comprehensive validation
"""

import os
import sys
import sqlite3
import psycopg2
import logging
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional
import json
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(__file__), '../.env'))

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PostgreSQLMigrator:
    """Safe and robust SQLite to PostgreSQL migration"""
    
    def __init__(self, sqlite_db_path: str, postgres_config: Dict[str, str]):
        self.sqlite_db_path = sqlite_db_path
        self.postgres_config = postgres_config
        self.migration_log = []
        
    def connect_sqlite(self):
        """Connect to SQLite database"""
        try:
            conn = sqlite3.connect(self.sqlite_db_path)
            conn.row_factory = sqlite3.Row  # Enable column access by name
            return conn
        except Exception as e:
            logger.error(f"❌ Failed to connect to SQLite: {e}")
            raise

    def connect_postgres(self):
        """Connect to PostgreSQL database"""
        try:
            conn = psycopg2.connect(**self.postgres_config)
            return conn
        except Exception as e:
            logger.error(f"❌ Failed to connect to PostgreSQL: {e}")
            raise

    def create_postgres_schema(self):
        """Create PostgreSQL schema matching SQLite structure"""
        import signal
        import psycopg2
        
        # Add connection timeout to prevent hanging
        pg_config = self.postgres_config.copy()
        pg_config['connect_timeout'] = 10  # 10 second timeout
        
        pg_conn = psycopg2.connect(**pg_config)
        cursor = pg_conn.cursor()
        
        try:
            # Create tables with PostgreSQL-optimized schema
            logger.info("🏗️ Creating PostgreSQL schema...")
            
            # Members table with all required columns
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS members (
                    id SERIAL PRIMARY KEY,
                    prospect_id TEXT UNIQUE,
                    guid TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    full_name TEXT,
                    email TEXT,
                    phone TEXT,
                    mobile_phone TEXT,
                    status TEXT,
                    status_message TEXT,
                    member_type TEXT,
                    user_type TEXT,
                    join_date TEXT,
                    amount_past_due DECIMAL(10,2) DEFAULT 0.0,
                    base_amount_past_due DECIMAL(10,2) DEFAULT 0.0,
                    late_fees DECIMAL(10,2) DEFAULT 0.0,
                    missed_payments INTEGER DEFAULT 0,
                    agreement_recurring_cost DECIMAL(10,2) DEFAULT 0.0,
                    date_of_next_payment TEXT,
                    agreement_id TEXT,
                    agreement_guid TEXT,
                    agreement_type TEXT DEFAULT 'Membership',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Commit members table creation immediately to reduce lock time
            pg_conn.commit()
            logger.info("✅ Members table created")
            
            # Prospects table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS prospects (
                    id SERIAL PRIMARY KEY,
                    prospect_id TEXT NOT NULL,
                    first_name TEXT,
                    last_name TEXT,
                    full_name TEXT,
                    email TEXT,
                    phone TEXT,
                    status TEXT,
                    prospect_type TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            pg_conn.commit()
            logger.info("✅ Prospects table created")
            
            # Training clients table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS training_clients (
                    id SERIAL PRIMARY KEY,
                    member_id TEXT,
                    clubos_member_id TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    full_name TEXT,
                    member_name TEXT,
                    email TEXT,
                    phone TEXT,
                    status TEXT,
                    training_package TEXT,
                    trainer_name TEXT,
                    membership_type TEXT,
                    source TEXT,
                    active_packages TEXT,
                    package_summary TEXT,
                    package_details TEXT,
                    past_due_amount DECIMAL(10,2) DEFAULT 0.0,
                    total_past_due DECIMAL(10,2) DEFAULT 0.0,
                    payment_status TEXT,
                    sessions_remaining INTEGER DEFAULT 0,
                    last_session TEXT,
                    financial_summary TEXT,
                    last_updated TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            pg_conn.commit()
            logger.info("✅ Training clients table created")
            
            # Member categories table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS member_categories (
                    id SERIAL PRIMARY KEY,
                    member_id TEXT UNIQUE,
                    category TEXT,
                    status_message TEXT,
                    status TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Data refresh log table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS data_refresh_log (
                    id SERIAL PRIMARY KEY,
                    table_name TEXT,
                    last_refresh TIMESTAMP,
                    record_count INTEGER,
                    category_breakdown TEXT
                )
            """)
            
            # Funding status cache table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS funding_status_cache (
                    id SERIAL PRIMARY KEY,
                    member_name TEXT,
                    member_email TEXT,
                    member_id TEXT,
                    funding_status TEXT,
                    package_details TEXT,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    cache_expiry TIMESTAMP
                )
            """)
            
            # Invoices table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS invoices (
                    id SERIAL PRIMARY KEY,
                    member_id TEXT,
                    square_invoice_id TEXT UNIQUE,
                    amount DECIMAL(10,2),
                    status TEXT,
                    payment_method TEXT,
                    delivery_method TEXT,
                    due_date TEXT,
                    payment_date TEXT,
                    square_payment_id TEXT,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Events table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id SERIAL PRIMARY KEY,
                    event_id TEXT UNIQUE,
                    title TEXT,
                    description TEXT,
                    start_time TEXT,
                    end_time TEXT,
                    location TEXT,
                    is_all_day BOOLEAN DEFAULT FALSE,
                    is_training_session BOOLEAN DEFAULT FALSE,
                    participants TEXT,
                    participant_emails TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Messages table for messaging functionality
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id TEXT PRIMARY KEY,
                    message_type TEXT,
                    content TEXT,
                    timestamp TEXT,
                    from_user TEXT,
                    to_user TEXT,
                    status TEXT,
                    owner_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    delivery_status TEXT DEFAULT 'received',
                    campaign_id TEXT,
                    channel TEXT DEFAULT 'clubos',
                    member_id TEXT,
                    message_actions TEXT,
                    is_confirmation BOOLEAN DEFAULT FALSE,
                    is_opt_in BOOLEAN DEFAULT FALSE,
                    is_opt_out BOOLEAN DEFAULT FALSE,
                    has_emoji BOOLEAN DEFAULT FALSE,
                    emoji_reactions TEXT,
                    conversation_id TEXT,
                    thread_id TEXT
                )
            """)
            
            # Create indexes for performance
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_members_prospect_id ON members(prospect_id)",
                "CREATE INDEX IF NOT EXISTS idx_members_status ON members(status)",
                "CREATE INDEX IF NOT EXISTS idx_members_email ON members(email)",
                "CREATE INDEX IF NOT EXISTS idx_prospects_prospect_id ON prospects(prospect_id)",
                "CREATE INDEX IF NOT EXISTS idx_training_clients_member_id ON training_clients(member_id)",
                "CREATE INDEX IF NOT EXISTS idx_member_categories_member_id ON member_categories(member_id)",
                "CREATE INDEX IF NOT EXISTS idx_member_categories_category ON member_categories(category)",
                "CREATE INDEX IF NOT EXISTS idx_funding_cache_member_name ON funding_status_cache(member_name)",
                "CREATE INDEX IF NOT EXISTS idx_invoices_member_id ON invoices(member_id)",
                "CREATE INDEX IF NOT EXISTS idx_events_event_id ON events(event_id)",
                "CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at)",
                "CREATE INDEX IF NOT EXISTS idx_messages_owner_id ON messages(owner_id)",
                "CREATE INDEX IF NOT EXISTS idx_messages_from_user ON messages(from_user)"
            ]
            
            for index_sql in indexes:
                cursor.execute(index_sql)
            
            pg_conn.commit()
            logger.info("✅ PostgreSQL schema created successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to create PostgreSQL schema: {e}")
            pg_conn.rollback()
            raise
        finally:
            cursor.close()
            pg_conn.close()

    def get_sqlite_tables(self) -> List[str]:
        """Get list of tables from SQLite database"""
        sqlite_conn = self.connect_sqlite()
        cursor = sqlite_conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        cursor.close()
        sqlite_conn.close()
        
        return tables

    def migrate_table_data(self, table_name: str) -> bool:
        """Migrate data from SQLite table to PostgreSQL"""
        try:
            logger.info(f"🔄 Migrating table: {table_name}")
            
            # Connect to both databases
            sqlite_conn = self.connect_sqlite()
            pg_conn = self.connect_postgres()
            
            sqlite_cursor = sqlite_conn.cursor()
            pg_cursor = pg_conn.cursor()
            
            # Get table structure from SQLite
            sqlite_cursor.execute(f"PRAGMA table_info({table_name})")
            columns_info = sqlite_cursor.fetchall()
            column_names = [col[1] for col in columns_info]
            
            # Skip SQLite-specific columns that don't exist in PostgreSQL
            if 'id' in column_names and table_name != 'data_refresh_log':
                column_names = [col for col in column_names if col != 'id']  # Skip SQLite id for SERIAL columns
            
            # Get all data from SQLite
            sqlite_cursor.execute(f"SELECT * FROM {table_name}")
            rows = sqlite_cursor.fetchall()
            
            if not rows:
                logger.info(f"ℹ️ No data to migrate in table: {table_name}")
                return True
            
            # Prepare PostgreSQL insert statement
            if column_names:
                placeholders = ', '.join(['%s'] * len(column_names))
                insert_sql = f"INSERT INTO {table_name} ({', '.join(column_names)}) VALUES ({placeholders}) ON CONFLICT DO NOTHING"
                
                # Convert SQLite rows to PostgreSQL format
                pg_rows = []
                for row in rows:
                    # Skip the id column for SERIAL tables
                    if 'id' in [col[1] for col in columns_info] and table_name != 'data_refresh_log':
                        pg_row = row[1:]  # Skip first column (id)
                    else:
                        pg_row = row
                    
                    # Handle data type conversions
                    converted_row = []
                    for i, value in enumerate(pg_row):
                        if i < len(column_names):  # Make sure we don't exceed column count
                            # Convert SQLite data types to PostgreSQL
                            if value == '':
                                converted_row.append(None)  # Empty strings to NULL
                            elif isinstance(value, str) and value.isdigit() and column_names[i] in ['sessions_remaining']:
                                converted_row.append(int(value))  # String numbers to integers
                            elif isinstance(value, str) and '.' in value and column_names[i] in ['amount_past_due', 'total_past_due', 'amount']:
                                try:
                                    converted_row.append(float(value))  # String decimals to floats
                                except ValueError:
                                    converted_row.append(value)
                            else:
                                converted_row.append(value)
                    
                    pg_rows.append(tuple(converted_row))
                
                # Batch insert
                pg_cursor.executemany(insert_sql, pg_rows)
                pg_conn.commit()
                
                logger.info(f"✅ Migrated {len(pg_rows)} rows from {table_name}")
            
            sqlite_cursor.close()
            sqlite_conn.close()
            pg_cursor.close()
            pg_conn.close()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to migrate table {table_name}: {e}")
            return False

    def validate_migration(self) -> bool:
        """Validate that migration was successful by comparing row counts"""
        try:
            logger.info("🔍 Validating migration...")
            
            sqlite_conn = self.connect_sqlite()
            pg_conn = self.connect_postgres()
            
            sqlite_cursor = sqlite_conn.cursor()
            pg_cursor = pg_conn.cursor()
            
            tables = self.get_sqlite_tables()
            validation_results = []
            
            for table in tables:
                if table.startswith('sqlite_'):  # Skip SQLite system tables
                    continue
                    
                # Count rows in SQLite
                sqlite_cursor.execute(f"SELECT COUNT(*) FROM {table}")
                sqlite_count = sqlite_cursor.fetchone()[0]
                
                # Count rows in PostgreSQL
                pg_cursor.execute(f"SELECT COUNT(*) FROM {table}")
                pg_count = pg_cursor.fetchone()[0]
                
                validation_results.append({
                    'table': table,
                    'sqlite_count': sqlite_count,
                    'postgres_count': pg_count,
                    'match': sqlite_count == pg_count
                })
                
                if sqlite_count == pg_count:
                    logger.info(f"✅ {table}: {sqlite_count} rows (match)")
                else:
                    logger.warning(f"⚠️ {table}: SQLite={sqlite_count}, PostgreSQL={pg_count} (mismatch)")
            
            sqlite_cursor.close()
            sqlite_conn.close()
            pg_cursor.close()
            pg_conn.close()
            
            # Check if all tables match
            all_match = all(result['match'] for result in validation_results)
            
            if all_match:
                logger.info("🎉 Migration validation successful - all row counts match!")
            else:
                logger.warning("⚠️ Some tables have mismatched row counts")
            
            return all_match
            
        except Exception as e:
            logger.error(f"❌ Validation failed: {e}")
            return False

    def run_migration(self) -> bool:
        """Run the complete migration process"""
        try:
            logger.info("🚀 Starting PostgreSQL migration...")
            
            # Step 1: Create PostgreSQL schema
            self.create_postgres_schema()
            
            # Step 2: Get list of tables to migrate
            tables = self.get_sqlite_tables()
            logger.info(f"📋 Found {len(tables)} tables to migrate: {tables}")
            
            # Step 3: Migrate each table
            success_count = 0
            for table in tables:
                if table.startswith('sqlite_'):  # Skip SQLite system tables
                    continue
                    
                if self.migrate_table_data(table):
                    success_count += 1
                else:
                    logger.error(f"❌ Failed to migrate table: {table}")
            
            # Step 4: Validate migration
            validation_success = self.validate_migration()
            
            # Step 5: Summary
            logger.info(f"📊 Migration Summary:")
            logger.info(f"   Tables migrated: {success_count}")
            logger.info(f"   Validation: {'✅ Passed' if validation_success else '❌ Failed'}")
            
            if success_count > 0 and validation_success:
                logger.info("🎉 PostgreSQL migration completed successfully!")
                return True
            else:
                logger.error("❌ Migration completed with errors")
                return False
                
        except Exception as e:
            logger.error(f"❌ Migration failed: {e}")
            return False


def run_migration_from_env():
    """Run migration using environment variables for PostgreSQL connection"""
    try:
        # Get PostgreSQL connection details from environment
        postgres_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', '5432')),
            'dbname': os.getenv('DB_NAME', 'gym_bot'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', '')
        }
        
        # SQLite database path
        sqlite_db_path = os.getenv('SQLITE_PATH', '../gym_bot.db')
        # Try different possible locations
        if not os.path.exists(sqlite_db_path):
            sqlite_db_path = 'gym_bot.db'
        if not os.path.exists(sqlite_db_path):
            sqlite_db_path = '../gym_bot.db'
        
        # Create migrator and run
        migrator = PostgreSQLMigrator(sqlite_db_path, postgres_config)
        success = migrator.run_migration()
        
        if success:
            logger.info("✅ Migration completed successfully!")
            return True
        else:
            logger.error("❌ Migration failed!")
            return False
            
    except Exception as e:
        logger.error(f"❌ Migration error: {e}")
        return False


if __name__ == "__main__":
    """Run migration when script is executed directly"""
    success = run_migration_from_env()
    sys.exit(0 if success else 1)