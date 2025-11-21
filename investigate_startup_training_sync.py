#!/usr/bin/env python3
"""
Investigate the startup training client sync process and agreement data structure
"""

import sys
import os
import logging
import json

# Add the src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def investigate_training_client_startup():
    """Investigate how training clients are loaded during startup"""
    print("🔍 Investigating training client startup sync process...")
    
    try:
        # Import the multi-club startup sync
        from services.multi_club_startup_sync import sync_training_clients_for_club
        
        # Test the training client sync function directly
        print("\n📊 Testing training client sync...")
        training_clients = sync_training_clients_for_club(club_id="1156")
        
        if training_clients:
            print(f"✅ Found {len(training_clients)} training clients from startup sync")
            
            # Examine the structure of the first few training clients
            print("\n📋 Training client data structure:")
            for i, client in enumerate(training_clients[:3]):
                print(f"\n--- Training Client {i+1} ---")
                print(f"Keys: {list(client.keys())}")
                
                # Look for revenue-related fields
                revenue_fields = {}
                for key, value in client.items():
                    if any(keyword in key.lower() for keyword in ['amount', 'payment', 'due', 'cost', 'price', 'revenue', 'billing', 'invoice', 'agreement']):
                        revenue_fields[key] = value
                
                if revenue_fields:
                    print(f"Revenue-related fields: {json.dumps(revenue_fields, indent=2)}")
                else:
                    print("❌ No revenue-related fields found")
                    
            # Check for package/agreement details
            print("\n🏋️ Package/Agreement details:")
            for i, client in enumerate(training_clients[:3]):
                print(f"\n--- Client {i+1}: {client.get('member_name', 'Unknown')} ---")
                
                # Look for package details
                package_fields = {}
                for key, value in client.items():
                    if any(keyword in key.lower() for keyword in ['package', 'agreement', 'training', 'session']):
                        package_fields[key] = value
                
                if package_fields:
                    print(f"Package fields: {json.dumps(package_fields, indent=2)}")
                else:
                    print("❌ No package fields found")
                    
        else:
            print("❌ No training clients found from startup sync")
            
    except Exception as e:
        print(f"❌ Error investigating startup sync: {e}")
        import traceback
        traceback.print_exc()

def investigate_clubos_integration():
    """Investigate the ClubOS integration for training clients"""
    print("\n🔧 Investigating ClubOS integration...")
    
    try:
        from services.clubos_integration import ClubOSIntegration
        
        clubos = ClubOSIntegration()
        training_clients = clubos.get_training_clients()
        
        if training_clients:
            print(f"✅ ClubOS integration found {len(training_clients)} training clients")
            
            # Examine structure
            for i, client in enumerate(training_clients[:2]):
                print(f"\n--- ClubOS Client {i+1} ---")
                print(f"Keys: {list(client.keys())}")
                print(f"Data sample: {json.dumps(client, indent=2)}")
                
        else:
            print("❌ ClubOS integration returned no training clients")
            
    except Exception as e:
        print(f"❌ Error with ClubOS integration: {e}")

def investigate_database_structure():
    """Investigate the current database structure and data"""
    print("\n🗄️ Investigating database training client structure...")
    
    try:
        from services.database_manager import DatabaseManager
        
        db_manager = DatabaseManager()
        
        # Get table schema
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("PRAGMA table_info(training_clients)")
        columns = cursor.fetchall()
        
        print("📊 training_clients table schema:")
        for col in columns:
            print(f"  {col[1]} ({col[2]})")
            
        # Get sample data
        cursor.execute("SELECT * FROM training_clients LIMIT 3")
        rows = cursor.fetchall()
        
        print(f"\n📋 Sample training client records ({len(rows)} found):")
        for i, row in enumerate(rows):
            print(f"\n--- Database Record {i+1} ---")
            row_dict = dict(row)
            print(f"Keys: {list(row_dict.keys())}")
            
            # Focus on revenue fields
            revenue_fields = {}
            for key, value in row_dict.items():
                if any(keyword in key.lower() for keyword in ['amount', 'payment', 'due', 'cost', 'price', 'revenue', 'billing']):
                    revenue_fields[key] = value
            
            if revenue_fields:
                print(f"Revenue fields: {json.dumps(revenue_fields, indent=2)}")
            else:
                print("❌ No revenue fields in database")
                
        conn.close()
        
    except Exception as e:
        print(f"❌ Error investigating database: {e}")

def investigate_revenue_calculation():
    """Investigate the current revenue calculation method"""
    print("\n💰 Investigating revenue calculation...")
    
    try:
        from services.database_manager import DatabaseManager
        
        db_manager = DatabaseManager()
        revenue_data = db_manager.get_monthly_revenue_calculation()
        
        print("📊 Current revenue calculation results:")
        print(f"Member revenue: ${revenue_data['member_revenue']:.2f}")
        print(f"Training revenue: ${revenue_data['training_revenue']:.2f}")
        print(f"Total monthly revenue: ${revenue_data['total_monthly_revenue']:.2f}")
        print(f"Revenue members count: {revenue_data['revenue_members_count']}")
        print(f"Training clients count: {revenue_data['training_clients_count']}")
        
        # Check what the training revenue query is actually finding
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                member_name, 
                past_due_amount, 
                payment_status,
                package_details,
                financial_summary
            FROM training_clients
            WHERE past_due_amount > 0 OR payment_status = 'Current'
        """)
        
        training_rows = cursor.fetchall()
        print(f"\n📋 Training clients included in revenue calculation ({len(training_rows)} found):")
        
        for row in training_rows:
            row_dict = dict(row)
            print(f"  {row_dict['member_name']}: past_due=${row_dict['past_due_amount']}, status={row_dict['payment_status']}")
            
        conn.close()
        
    except Exception as e:
        print(f"❌ Error investigating revenue calculation: {e}")

if __name__ == "__main__":
    print("🔍 INVESTIGATING TRAINING CLIENT STARTUP SYNC AND REVENUE CALCULATION")
    print("=" * 80)
    
    investigate_training_client_startup()
    investigate_clubos_integration() 
    investigate_database_structure()
    investigate_revenue_calculation()
    
    print("\n" + "=" * 80)
    print("🏁 Investigation complete!")