#!/usr/bin/env python3
"""
Quick setup script for Google Cloud SQL PostgreSQL
Helps configure environment and test connections
"""

import os
import sys
import json
import subprocess
import getpass
from urllib.request import urlopen

def get_public_ip():
    """Get the current public IP address"""
    try:
        response = urlopen('https://api.ipify.org')
        return response.read().decode('utf-8')
    except Exception as e:
        print(f"⚠️ Could not get public IP: {e}")
        return None

def check_gcloud_installed():
    """Check if Google Cloud SDK is installed"""
    try:
        result = subprocess.run(['gcloud', 'version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Google Cloud SDK is installed")
            return True
        else:
            return False
    except FileNotFoundError:
        return False

def setup_environment_file():
    """Create or update .env file with Cloud SQL configuration"""
    print("\n🔧 Setting up environment configuration...")
    
    env_file = '../.env'  # Go up one directory to project root
    
    # Get configuration from user
    print("\nPlease provide your Cloud SQL configuration:")
    db_host = input("Database Host (Cloud SQL IP): ")
    db_password = getpass.getpass("Database Password: ")
    db_name = input("Database Name [gym_bot]: ").strip() or "gym_bot"
    db_user = input("Database User [postgres]: ").strip() or "postgres"
    
    # Create environment configuration
    env_config = f"""# Database Configuration - PostgreSQL on Google Cloud SQL
DB_TYPE=postgresql
DB_HOST={db_host}
DB_PORT=5432
DB_NAME={db_name}
DB_USER={db_user}
DB_PASSWORD={db_password}
DB_SSL_MODE=require

# Keep SQLite as backup
SQLITE_PATH=gym_bot.db
"""
    
    # Read existing .env file if it exists
    existing_env = {}
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if '=' in line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    existing_env[key] = value
    
    # Update with new database config
    updated_lines = []
    db_keys = {'DB_TYPE', 'DB_HOST', 'DB_PORT', 'DB_NAME', 'DB_USER', 'DB_PASSWORD', 'DB_SSL_MODE'}
    
    # Add non-database existing config
    for key, value in existing_env.items():
        if key not in db_keys:
            updated_lines.append(f"{key}={value}")
    
    # Add database config
    updated_lines.append("")
    updated_lines.append("# Database Configuration - PostgreSQL on Google Cloud SQL")
    updated_lines.append(f"DB_TYPE=postgresql")
    updated_lines.append(f"DB_HOST={db_host}")
    updated_lines.append(f"DB_PORT=5432")
    updated_lines.append(f"DB_NAME={db_name}")
    updated_lines.append(f"DB_USER={db_user}")
    updated_lines.append(f"DB_PASSWORD={db_password}")
    updated_lines.append(f"DB_SSL_MODE=require")
    updated_lines.append("")
    updated_lines.append("# Keep SQLite as backup")
    updated_lines.append(f"SQLITE_PATH=gym_bot.db")
    
    # Write updated config
    with open(env_file, 'w') as f:
        f.write('\n'.join(updated_lines))
    
    print(f"✅ Environment configuration saved to {env_file}")
    return {
        'host': db_host,
        'port': 5432,
        'dbname': db_name,
        'user': db_user,
        'password': db_password
    }

def test_cloud_sql_connection(config):
    """Test connection to Cloud SQL PostgreSQL"""
    try:
        import psycopg2
        print("\n🔍 Testing Cloud SQL connection...")
        
        conn = psycopg2.connect(**config)
        cursor = conn.cursor()
        
        # Test basic connectivity
        cursor.execute("SELECT version()")
        version = cursor.fetchone()[0]
        print(f"✅ Connected to PostgreSQL: {version}")
        
        # Test database access
        cursor.execute("SELECT current_database()")
        current_db = cursor.fetchone()[0]
        print(f"✅ Connected to database: {current_db}")
        
        cursor.close()
        conn.close()
        
        print("✅ Cloud SQL connection successful!")
        return True
        
    except ImportError:
        print("❌ psycopg2 not installed. Install with: pip install psycopg2-binary")
        return False
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\nTroubleshooting tips:")
        print("1. Check that your IP is in authorized networks")
        print("2. Verify the host IP address is correct")
        print("3. Confirm username and password")
        print("4. Ensure Cloud SQL instance is running")
        return False

def show_next_steps():
    """Show next steps after setup"""
    print("\n" + "="*60)
    print("🎉 Cloud SQL Setup Complete!")
    print("="*60)
    print()
    print("Next steps:")
    print("1. ✅ Cloud SQL instance configured")
    print("2. ✅ Environment variables updated")
    print("3. ✅ Connection tested")
    print()
    print("To migrate your data:")
    print("   python services/database_migration.py")
    print()
    print("To test your application with PostgreSQL:")
    print("   python -c 'from main_app import create_app; app = create_app(); print(\"App working with PostgreSQL!\")'")
    print()
    print("To switch back to SQLite (if needed):")
    print("   Remove or comment out DB_TYPE=postgresql in .env file")
    print()

def main():
    """Main setup flow"""
    print("🚀 Google Cloud SQL PostgreSQL Setup")
    print("="*50)
    
    # Check if gcloud is installed
    if not check_gcloud_installed():
        print("⚠️ Google Cloud SDK not found")
        print("   Download from: https://cloud.google.com/sdk/docs/install")
        print("   This is optional but recommended for management")
        print()
    
    # Show current public IP for reference
    public_ip = get_public_ip()
    if public_ip:
        print(f"📍 Your current public IP: {public_ip}")
        print("   Add this to Cloud SQL authorized networks")
        print()
    
    print("Before continuing, ensure you have:")
    print("1. Created a Cloud SQL PostgreSQL instance")
    print("2. Added your IP to authorized networks") 
    print("3. Created the 'gym_bot' database")
    print("4. Have the connection details ready")
    print()
    
    # Confirm user is ready
    ready = input("Are you ready to configure the connection? (y/N): ").lower().strip()
    if ready != 'y':
        print("\n📋 Please complete the Cloud SQL setup first:")
        print("   See: cloud_sql_setup_guide.md")
        print("   Or visit: https://console.cloud.google.com/sql")
        return
    
    # Setup environment
    config = setup_environment_file()
    
    # Test connection
    if test_cloud_sql_connection(config):
        show_next_steps()
    else:
        print("\n❌ Setup incomplete - connection test failed")
        print("   Please check the troubleshooting section in cloud_sql_setup_guide.md")

if __name__ == '__main__':
    main()