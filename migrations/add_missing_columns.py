#!/usr/bin/env python3
"""
Add Missing Columns to PostgreSQL Database
This script adds all columns that the application expects but may be missing from the existing PostgreSQL schema.
"""

import os
import sys
import psycopg2
import logging
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_postgres_connection():
    """Get PostgreSQL connection"""
    try:
        config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', '5432')),
            'dbname': os.getenv('DB_NAME', 'gym_bot'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', '')
        }
        return psycopg2.connect(**config)
    except Exception as e:
        logger.error(f"❌ Failed to connect to PostgreSQL: {e}")
        raise

def column_exists(cursor, table_name, column_name):
    """Check if a column exists in a table"""
    cursor.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = %s AND column_name = %s
    """, (table_name, column_name))
    return cursor.fetchone() is not None

def add_column_if_missing(cursor, table_name, column_name, column_definition):
    """Add a column to a table if it doesn't exist"""
    if not column_exists(cursor, table_name, column_name):
        try:
            alter_sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition}"
            cursor.execute(alter_sql)
            logger.info(f"✅ Added column {table_name}.{column_name}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to add column {table_name}.{column_name}: {e}")
            return False
    else:
        logger.info(f"ℹ️ Column {table_name}.{column_name} already exists")
        return True

def add_missing_columns():
    """Add all missing columns to PostgreSQL tables"""
    conn = get_postgres_connection()
    cursor = conn.cursor()
    
    try:
        logger.info("🔧 Adding missing columns to PostgreSQL database...")
        
        # ===============================
        # MEMBERS TABLE COLUMNS
        # ===============================
        members_columns = [
            ('prospect_id', 'TEXT'),
            ('guid', 'TEXT'),
            ('first_name', 'TEXT'),
            ('last_name', 'TEXT'),
            ('full_name', 'TEXT'),
            ('email', 'TEXT'),
            ('phone', 'TEXT'),
            ('mobile_phone', 'TEXT'),
            ('status', 'TEXT'),
            ('status_message', 'TEXT'),
            ('member_type', 'TEXT'),
            ('user_type', 'TEXT'),
            ('join_date', 'TEXT'),
            ('amount_past_due', 'DECIMAL(10,2) DEFAULT 0.0'),
            ('base_amount_past_due', 'DECIMAL(10,2) DEFAULT 0.0'),
            ('late_fees', 'DECIMAL(10,2) DEFAULT 0.0'),
            ('missed_payments', 'INTEGER DEFAULT 0'),
            ('agreement_recurring_cost', 'DECIMAL(10,2) DEFAULT 0.0'),
            ('date_of_next_payment', 'TEXT'),
            ('created_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'),
            ('updated_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP')
        ]
        
        for column_name, column_def in members_columns:
            add_column_if_missing(cursor, 'members', column_name, column_def)
        
        # ===============================
        # PROSPECTS TABLE COLUMNS
        # ===============================
        prospects_columns = [
            ('prospect_id', 'TEXT NOT NULL'),
            ('first_name', 'TEXT'),
            ('last_name', 'TEXT'),
            ('full_name', 'TEXT'),
            ('email', 'TEXT'),
            ('phone', 'TEXT'),
            ('status', 'TEXT'),
            ('prospect_type', 'TEXT'),
            ('created_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'),
            ('updated_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP')
        ]
        
        for column_name, column_def in prospects_columns:
            add_column_if_missing(cursor, 'prospects', column_name, column_def)
        
        # ===============================
        # TRAINING_CLIENTS TABLE COLUMNS
        # ===============================
        training_clients_columns = [
            ('member_id', 'TEXT'),
            ('clubos_member_id', 'TEXT'),
            ('first_name', 'TEXT'),
            ('last_name', 'TEXT'),
            ('full_name', 'TEXT'),
            ('member_name', 'TEXT'),
            ('email', 'TEXT'),
            ('phone', 'TEXT'),
            ('status', 'TEXT'),
            ('training_package', 'TEXT'),
            ('trainer_name', 'TEXT'),
            ('membership_type', 'TEXT'),
            ('source', 'TEXT'),
            ('active_packages', 'TEXT'),
            ('package_summary', 'TEXT'),
            ('package_details', 'TEXT'),
            ('past_due_amount', 'DECIMAL(10,2) DEFAULT 0.0'),
            ('total_past_due', 'DECIMAL(10,2) DEFAULT 0.0'),
            ('payment_status', 'TEXT'),
            ('sessions_remaining', 'INTEGER DEFAULT 0'),
            ('last_session', 'TEXT'),
            ('financial_summary', 'TEXT'),
            ('last_updated', 'TIMESTAMP'),
            ('created_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'),
            ('updated_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP')
        ]
        
        for column_name, column_def in training_clients_columns:
            add_column_if_missing(cursor, 'training_clients', column_name, column_def)
        
        # ===============================
        # MESSAGES TABLE (Create table if it doesn't exist)
        # ===============================
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
        logger.info("✅ Ensured messages table exists")
        
        # ===============================
        # MEMBER_CATEGORIES TABLE COLUMNS
        # ===============================
        member_categories_columns = [
            ('member_id', 'TEXT UNIQUE'),
            ('category', 'TEXT'),
            ('status_message', 'TEXT'),
            ('status', 'TEXT'),
            ('created_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'),
            ('updated_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP')
        ]
        
        for column_name, column_def in member_categories_columns:
            add_column_if_missing(cursor, 'member_categories', column_name, column_def)
        
        # ===============================
        # FUNDING_STATUS_CACHE TABLE COLUMNS
        # ===============================
        funding_cache_columns = [
            ('member_name', 'TEXT'),
            ('member_email', 'TEXT'),
            ('member_id', 'TEXT'),
            ('funding_status', 'TEXT'),
            ('package_details', 'TEXT'),
            ('last_updated', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'),
            ('cache_expiry', 'TIMESTAMP')
        ]
        
        for column_name, column_def in funding_cache_columns:
            add_column_if_missing(cursor, 'funding_status_cache', column_name, column_def)
        
        # ===============================
        # INVOICES TABLE COLUMNS
        # ===============================
        invoices_columns = [
            ('member_id', 'TEXT'),
            ('square_invoice_id', 'TEXT UNIQUE'),
            ('amount', 'DECIMAL(10,2)'),
            ('status', 'TEXT'),
            ('payment_method', 'TEXT'),
            ('delivery_method', 'TEXT'),
            ('due_date', 'TEXT'),
            ('payment_date', 'TEXT'),
            ('square_payment_id', 'TEXT'),
            ('notes', 'TEXT'),
            ('created_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'),
            ('updated_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP')
        ]
        
        for column_name, column_def in invoices_columns:
            add_column_if_missing(cursor, 'invoices', column_name, column_def)
        
        # ===============================
        # EVENTS TABLE COLUMNS
        # ===============================
        events_columns = [
            ('event_id', 'TEXT UNIQUE'),
            ('title', 'TEXT'),
            ('description', 'TEXT'),
            ('start_time', 'TEXT'),
            ('end_time', 'TEXT'),
            ('location', 'TEXT'),
            ('is_all_day', 'BOOLEAN DEFAULT FALSE'),
            ('is_training_session', 'BOOLEAN DEFAULT FALSE'),
            ('participants', 'TEXT'),
            ('participant_emails', 'TEXT'),
            ('created_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'),
            ('updated_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP')
        ]
        
        for column_name, column_def in events_columns:
            add_column_if_missing(cursor, 'events', column_name, column_def)
        
        # ===============================
        # DATA_REFRESH_LOG TABLE COLUMNS
        # ===============================
        refresh_log_columns = [
            ('table_name', 'TEXT'),
            ('last_refresh', 'TIMESTAMP'),
            ('record_count', 'INTEGER'),
            ('category_breakdown', 'TEXT')
        ]
        
        for column_name, column_def in refresh_log_columns:
            add_column_if_missing(cursor, 'data_refresh_log', column_name, column_def)
        
        # ===============================
        # CREATE MISSING INDEXES
        # ===============================
        logger.info("🔧 Creating missing indexes...")
        
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_members_prospect_id ON members(prospect_id)",
            "CREATE INDEX IF NOT EXISTS idx_members_status ON members(status)",
            "CREATE INDEX IF NOT EXISTS idx_members_email ON members(email)",
            "CREATE INDEX IF NOT EXISTS idx_members_status_message ON members(status_message)",
            "CREATE INDEX IF NOT EXISTS idx_prospects_prospect_id ON prospects(prospect_id)",
            "CREATE INDEX IF NOT EXISTS idx_training_clients_member_id ON training_clients(member_id)",
            "CREATE INDEX IF NOT EXISTS idx_member_categories_member_id ON member_categories(member_id)",
            "CREATE INDEX IF NOT EXISTS idx_member_categories_category ON member_categories(category)",
            "CREATE INDEX IF NOT EXISTS idx_funding_cache_member_name ON funding_status_cache(member_name)",
            "CREATE INDEX IF NOT EXISTS idx_invoices_member_id ON invoices(member_id)",
            "CREATE INDEX IF NOT EXISTS idx_events_event_id ON events(event_id)",
            "CREATE INDEX IF NOT EXISTS idx_messages_member_id ON messages(member_id)",
            "CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp)"
        ]
        
        for index_sql in indexes:
            try:
                cursor.execute(index_sql)
                logger.info(f"✅ Created/verified index: {index_sql.split(' ON ')[1] if ' ON ' in index_sql else 'unknown'}")
            except Exception as e:
                logger.warning(f"⚠️ Index creation warning: {e}")
        
        # Commit all changes
        conn.commit()
        logger.info("🎉 Successfully added all missing columns and indexes!")
        
        # Verify columns were added by checking members table structure
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default 
            FROM information_schema.columns 
            WHERE table_name = 'members' 
            ORDER BY ordinal_position
        """)
        
        columns = cursor.fetchall()
        logger.info(f"📋 Members table now has {len(columns)} columns:")
        for col in columns:
            logger.info(f"  {col[0]} ({col[1]}) - nullable: {col[2]}, default: {col[3]}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error adding missing columns: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

def verify_table_structure():
    """Verify that all expected tables and columns exist"""
    conn = get_postgres_connection()
    cursor = conn.cursor()
    
    try:
        logger.info("🔍 Verifying table structure...")
        
        # Check all expected tables exist
        expected_tables = ['members', 'prospects', 'training_clients', 'member_categories', 
                          'data_refresh_log', 'funding_status_cache', 'invoices', 'events', 'messages']
        
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
        """)
        
        existing_tables = [row[0] for row in cursor.fetchall()]
        
        for table in expected_tables:
            if table in existing_tables:
                logger.info(f"✅ Table {table} exists")
                
                # Count records in each table
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                logger.info(f"   📊 {table}: {count} records")
            else:
                logger.warning(f"⚠️ Table {table} missing")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error verifying table structure: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    """Run the column addition script"""
    logger.info("🚀 Starting missing columns addition...")
    
    success = add_missing_columns()
    
    if success:
        logger.info("✅ Column addition completed successfully!")
        verify_table_structure()
    else:
        logger.error("❌ Column addition failed!")
        sys.exit(1)