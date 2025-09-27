#!/usr/bin/env python3
"""
Database Performance Optimization
Add indexes and optimize queries for dramatic speed improvements
"""

import sqlite3
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class DatabaseOptimizer:
    """Database optimization utilities for performance improvements"""
    
    def __init__(self, db_path):
        self.db_path = db_path
        
    def add_performance_indexes(self):
        """Add indexes to frequently queried columns for dramatic speed improvements"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Indexes for members table (most frequently accessed) - using actual column names
            indexes_to_create = [
                # Search optimization
                ("idx_members_email", "CREATE INDEX IF NOT EXISTS idx_members_email ON members(email)"),
                ("idx_members_full_name", "CREATE INDEX IF NOT EXISTS idx_members_full_name ON members(full_name)"),
                ("idx_members_mobile_phone", "CREATE INDEX IF NOT EXISTS idx_members_mobile_phone ON members(mobile_phone)"),
                ("idx_members_phone", "CREATE INDEX IF NOT EXISTS idx_members_phone ON members(phone)"),
                ("idx_members_first_name", "CREATE INDEX IF NOT EXISTS idx_members_first_name ON members(first_name)"),
                ("idx_members_last_name", "CREATE INDEX IF NOT EXISTS idx_members_last_name ON members(last_name)"),
                
                # Status filtering optimization
                ("idx_members_status", "CREATE INDEX IF NOT EXISTS idx_members_status ON members(status)"),
                ("idx_members_user_type", "CREATE INDEX IF NOT EXISTS idx_members_user_type ON members(user_type)"),
                ("idx_members_member_type", "CREATE INDEX IF NOT EXISTS idx_members_member_type ON members(member_type)"),
                
                # Date-based queries optimization
                ("idx_members_created_at", "CREATE INDEX IF NOT EXISTS idx_members_created_at ON members(created_at)"),
                ("idx_members_join_date", "CREATE INDEX IF NOT EXISTS idx_members_join_date ON members(join_date)"),
                ("idx_members_date_of_next_payment", "CREATE INDEX IF NOT EXISTS idx_members_date_of_next_payment ON members(date_of_next_payment)"),
                
                # Revenue calculations optimization - using actual column names
                ("idx_members_amount_past_due", "CREATE INDEX IF NOT EXISTS idx_members_amount_past_due ON members(amount_past_due)"),
                ("idx_members_agreement_recurring_cost", "CREATE INDEX IF NOT EXISTS idx_members_agreement_recurring_cost ON members(agreement_recurring_cost)"),
                ("idx_members_base_amount_past_due", "CREATE INDEX IF NOT EXISTS idx_members_base_amount_past_due ON members(base_amount_past_due)"),
                ("idx_members_late_fees", "CREATE INDEX IF NOT EXISTS idx_members_late_fees ON members(late_fees)"),
                ("idx_members_agreement_id", "CREATE INDEX IF NOT EXISTS idx_members_agreement_id ON members(agreement_id)"),
                
                # Prospects table optimization
                ("idx_prospects_email", "CREATE INDEX IF NOT EXISTS idx_prospects_email ON prospects(email)"),
                ("idx_prospects_full_name", "CREATE INDEX IF NOT EXISTS idx_prospects_full_name ON prospects(full_name)"),
                ("idx_prospects_status", "CREATE INDEX IF NOT EXISTS idx_prospects_status ON prospects(status)"),
                ("idx_prospects_created_at", "CREATE INDEX IF NOT EXISTS idx_prospects_created_at ON prospects(created_at)"),
                
                # Training clients optimization
                ("idx_training_member_name", "CREATE INDEX IF NOT EXISTS idx_training_member_name ON training_clients(member_name)"),
                ("idx_training_clubos_id", "CREATE INDEX IF NOT EXISTS idx_training_clubos_id ON training_clients(clubos_member_id)"),
                ("idx_training_trainer_name", "CREATE INDEX IF NOT EXISTS idx_training_trainer_name ON training_clients(trainer_name)"),
                ("idx_training_created_at", "CREATE INDEX IF NOT EXISTS idx_training_created_at ON training_clients(created_at)"),
                
                # Composite indexes for common multi-column queries - using actual columns
                ("idx_members_status_type", "CREATE INDEX IF NOT EXISTS idx_members_status_type ON members(status, user_type)"),
                ("idx_members_name_email", "CREATE INDEX IF NOT EXISTS idx_members_name_email ON members(full_name, email)"),
                ("idx_members_payment_status", "CREATE INDEX IF NOT EXISTS idx_members_payment_status ON members(status, amount_past_due)"),
            ]
            
            logger.info(f"🔧 Creating {len(indexes_to_create)} performance indexes...")
            
            for index_name, sql in indexes_to_create:
                try:
                    cursor.execute(sql)
                    logger.info(f"✅ Created index: {index_name}")
                except Exception as e:
                    logger.warning(f"⚠️ Index {index_name} may already exist: {e}")
            
            # Create compound indexes for complex queries - using actual column names
            compound_indexes = [
                # Search with status filter
                ("idx_search_status", """
                    CREATE INDEX IF NOT EXISTS idx_search_status 
                    ON members(full_name, email, mobile_phone, status)
                """),
                
                # Revenue calculation optimization - using actual columns
                ("idx_revenue_calc", """
                    CREATE INDEX IF NOT EXISTS idx_revenue_calc 
                    ON members(status, user_type, agreement_recurring_cost, amount_past_due, created_at)
                """),
                
                # Dashboard summary optimization - using actual columns
                ("idx_dashboard_summary", """
                    CREATE INDEX IF NOT EXISTS idx_dashboard_summary 
                    ON members(status, user_type, created_at, agreement_recurring_cost)
                """),
            ]
            
            for index_name, sql in compound_indexes:
                try:
                    cursor.execute(sql.strip())
                    logger.info(f"✅ Created compound index: {index_name}")
                except Exception as e:
                    logger.warning(f"⚠️ Compound index {index_name} may already exist: {e}")
            
            conn.commit()
            conn.close()
            
            logger.info("🚀 Database indexing complete - queries should be dramatically faster!")
            
        except Exception as e:
            logger.error(f"❌ Error adding performance indexes: {e}")
            raise
    
    def optimize_database_settings(self):
        """Optimize SQLite settings for better performance"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Performance optimization settings
            optimizations = [
                "PRAGMA journal_mode = WAL",          # Write-Ahead Logging for better concurrency
                "PRAGMA synchronous = NORMAL",        # Balance between safety and speed
                "PRAGMA cache_size = 10000",          # Increase cache size (40MB)
                "PRAGMA temp_store = MEMORY",         # Store temp tables in memory
                "PRAGMA mmap_size = 268435456",       # Memory-mapped I/O (256MB)
            ]
            
            for pragma in optimizations:
                cursor.execute(pragma)
                logger.info(f"✅ Applied optimization: {pragma}")
            
            conn.commit()
            conn.close()
            
            logger.info("🚀 Database optimization settings applied!")
            
        except Exception as e:
            logger.error(f"❌ Error optimizing database settings: {e}")
            raise
    
    def analyze_query_performance(self):
        """Analyze current query performance and suggest optimizations"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Enable query planner
            cursor.execute("PRAGMA query_planner = ON")
            
            # Test common queries - using actual column names
            test_queries = [
                ("Member count", "SELECT COUNT(*) FROM members"),
                ("Search by email", "SELECT * FROM members WHERE email LIKE '%test%'"),
                ("Filter by status", "SELECT * FROM members WHERE status = 'ppv'"),
                ("Revenue calculation", "SELECT SUM(agreement_recurring_cost) FROM members WHERE status != 'comp'"),
                ("Recent members", "SELECT * FROM members ORDER BY created_at DESC LIMIT 10"),
                ("Past due members", "SELECT * FROM members WHERE amount_past_due > 0"),
            ]
            
            logger.info("📊 Query Performance Analysis:")
            
            for query_name, sql in test_queries:
                start_time = datetime.now()
                cursor.execute(sql)
                results = cursor.fetchall()
                end_time = datetime.now()
                
                duration = (end_time - start_time).total_seconds() * 1000
                logger.info(f"  {query_name}: {duration:.2f}ms ({len(results)} rows)")
            
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ Error analyzing query performance: {e}")

def optimize_database_performance(db_path='gym_bot.db'):
    """Main function to optimize database performance"""
    logger.info("🔧 Starting database performance optimization...")
    
    optimizer = DatabaseOptimizer(db_path)
    
    # Step 1: Add performance indexes
    optimizer.add_performance_indexes()
    
    # Step 2: Optimize database settings
    optimizer.optimize_database_settings()
    
    # Step 3: Analyze performance
    optimizer.analyze_query_performance()
    
    logger.info("✅ Database optimization complete!")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    optimize_database_performance()