#!/usr/bin/env python3
"""
Fix training clients duplicates and add unique constraint
"""
import sqlite3
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_duplicates():
    conn = sqlite3.connect('gym_bot.db')
    cursor = conn.cursor()

    # Check current state
    cursor.execute('SELECT COUNT(*) FROM training_clients')
    before_count = cursor.fetchone()[0]
    logger.info(f"Training clients before cleanup: {before_count}")

    # Create new table with proper unique constraint
    cursor.execute("""
        CREATE TABLE training_clients_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prospect_id TEXT,
            clubos_member_id TEXT UNIQUE NOT NULL,
            member_id TEXT,
            first_name TEXT,
            last_name TEXT,
            full_name TEXT,
            member_name TEXT,
            email TEXT,
            phone TEXT,
            mobile_phone TEXT,
            status TEXT,
            training_package TEXT,
            trainer_name TEXT,
            membership_type TEXT,
            source TEXT,
            active_packages TEXT,
            package_summary TEXT,
            package_details TEXT,
            past_due_amount REAL DEFAULT 0.0,
            total_past_due REAL DEFAULT 0.0,
            payment_status TEXT,
            sessions_remaining INTEGER DEFAULT 0,
            last_session TEXT,
            financial_summary TEXT,
            address TEXT,
            city TEXT,
            state TEXT,
            zip_code TEXT,
            agreement_id TEXT,
            last_updated TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Copy only the most recent version of each training client
    cursor.execute("""
        INSERT INTO training_clients_new
        SELECT
            NULL as id,
            prospect_id,
            clubos_member_id,
            member_id,
            first_name,
            last_name,
            full_name,
            member_name,
            email,
            phone,
            mobile_phone,
            status,
            training_package,
            trainer_name,
            membership_type,
            source,
            active_packages,
            package_summary,
            package_details,
            past_due_amount,
            total_past_due,
            payment_status,
            sessions_remaining,
            last_session,
            financial_summary,
            address,
            city,
            state,
            zip_code,
            agreement_id,
            last_updated,
            created_at,
            updated_at
        FROM training_clients
        WHERE id IN (
            SELECT MAX(id)
            FROM training_clients
            WHERE clubos_member_id IS NOT NULL
            GROUP BY clubos_member_id
        )
    """)

    # Check new count
    cursor.execute('SELECT COUNT(*) FROM training_clients_new')
    after_count = cursor.fetchone()[0]
    logger.info(f"Training clients after deduplication: {after_count}")
    logger.info(f"Removed {before_count - after_count} duplicates")

    # Drop old table and rename new one
    cursor.execute('DROP TABLE training_clients')
    cursor.execute('ALTER TABLE training_clients_new RENAME TO training_clients')

    # Recreate index
    cursor.execute('CREATE INDEX idx_training_clients_member_id ON training_clients(member_id)')
    cursor.execute('CREATE INDEX idx_training_clients_clubos_member_id ON training_clients(clubos_member_id)')

    conn.commit()
    conn.close()

    logger.info("✅ Fixed training clients duplicates and added unique constraint")

if __name__ == '__main__':
    fix_duplicates()
