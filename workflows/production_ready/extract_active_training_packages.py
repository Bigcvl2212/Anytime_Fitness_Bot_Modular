"""
Training Package Data Extractor for Active Clients

This module extracts ACTIVE training package data and payment status 
for training clients using the ClubOS API infrastructure.

Integrates with the existing gym bot app filesystem.
"""

import os
import sys
import pandas as pd
import json
import time
from datetime import datetime
from typing import List, Dict, Any

# Add the current directory to the path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Add the parent directories to path for absolute imports
sys.path.insert(0, os.path.join(current_dir, 'services'))
sys.path.insert(0, os.path.join(current_dir, 'services', 'api'))
sys.path.insert(0, os.path.join(current_dir, 'services', 'data'))
sys.path.insert(0, os.path.join(current_dir, 'config'))

try:
    from services.api.enhanced_clubos_client import create_enhanced_clubos_client
    from services.data.member_data import save_training_package_data_comprehensive
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("   Trying alternative import approach...")
    try:
        # Try importing the modules directly
        import importlib.util
        
        # Import enhanced_clubos_client
        client_spec = importlib.util.spec_from_file_location(
            "enhanced_clubos_client", 
            os.path.join(current_dir, "services", "api", "enhanced_clubos_client.py")
        )
        client_module = importlib.util.module_from_spec(client_spec)
        client_spec.loader.exec_module(client_module)
        create_enhanced_clubos_client = client_module.create_enhanced_clubos_client
        
        # Import member_data
        data_spec = importlib.util.spec_from_file_location(
            "member_data", 
            os.path.join(current_dir, "services", "data", "member_data.py")
        )
        data_module = importlib.util.module_from_spec(data_spec)
        data_spec.loader.exec_module(data_module)
        save_training_package_data_comprehensive = data_module.save_training_package_data_comprehensive
        
        print("✅ Successfully imported modules using alternative method")
        
    except Exception as e2:
        print(f"❌ Alternative import failed: {e2}")
        print("   Please ensure you're running from the gym-bot-modular directory")
        sys.exit(1)


def extract_member_ids_from_csv(csv_file_path: str) -> List[Dict[str, str]]:
    """
    Extract member IDs and data from training clients CSV.
    
    Args:
        csv_file_path: Path to the CSV file with training client data
        
    Returns:
        List of dictionaries with member data including ID, name, and profile URL
    """
    print(f"📄 Loading training clients from: {csv_file_path}")
    
    try:
        df = pd.read_csv(csv_file_path)
        print(f"✅ Loaded {len(df)} training clients")
        print(f"📋 CSV Columns: {list(df.columns)}")
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        return []
    
    member_data = []
    
    print(f"🔍 Extracting member IDs from {len(df)} rows...")
    
    for index, row in df.iterrows():
        member_name = row.get('Member Name', '').strip()
        profile_url = row.get('Profile', '').strip()
        agreement_name = row.get('Agreement Name', '').strip()
        next_invoice = row.get('Next Invoice Subtotal', 0)
        
        if not profile_url or not member_name:
            print(f"   ⚠️  Missing data for row {index + 1}")
            continue
            
        # Extract member ID from Profile URL
        if '/Delegate/' in profile_url:
            try:
                member_id = profile_url.split('/Delegate/')[-1].split('/')[0].split('?')[0]
                member_data.append({
                    'member_name': member_name,
                    'member_id': member_id,
                    'profile_url': profile_url,
                    'agreement_name': agreement_name,
                    'next_invoice_amount': next_invoice,
                    'csv_row_index': index
                })
                print(f"   ✅ {member_name}: ID {member_id} | Agreement: {agreement_name} | Next Invoice: ${next_invoice}")
            except Exception as e:
                print(f"   ❌ Failed to extract ID from {profile_url} for {member_name}: {e}")
        else:
            print(f"   ⚠️  Invalid profile URL format for {member_name}: {profile_url}")
    
    print(f"   📊 Successfully extracted {len(member_data)} member records")
    return member_data


def fetch_active_training_packages_via_api(member_data_list: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    """
    Fetch ACTIVE training package data for members using ClubOS API.
    
    Args:
        member_data_list: List of member data dictionaries
        
    Returns:
        List of dictionaries containing active training package data
    """
    print("🏋️ FETCHING ACTIVE TRAINING PACKAGE DATA VIA CLUBOS API")
    print("="*65)
    
    # Initialize the ClubOS API client
    client = create_enhanced_clubos_client()
    if not client:
        print("❌ Failed to initialize ClubOS API client")
        return []
    
    print("✅ ClubOS API client initialized successfully")
    
    all_active_packages = []
    
    for i, member_data in enumerate(member_data_list, 1):
        member_name = member_data['member_name']
        member_id = member_data['member_id']
        
        print(f"\n   📦 Processing {i}/{len(member_data_list)}: {member_name} (ID: {member_id})")
        
        try:
            # Get training packages via API
            result = client.get_training_packages_for_client(member_id)
            
            if result.get("success", False):
                packages = result.get("training_packages", [])
                
                if packages:
                    print(f"   📋 Found {len(packages)} total training packages")
                    
                    # Filter for ACTIVE packages only
                    active_packages = [pkg for pkg in packages if pkg.get('status', '').upper() == 'ACTIVE']
                    
                    if active_packages:
                        print(f"   ✅ Found {len(active_packages)} ACTIVE training packages")
                        
                        # Create comprehensive record
                        active_package_record = {
                            'member_name': member_name,
                            'member_id': member_id,
                            'profile_url': member_data['profile_url'],
                            'agreement_name': member_data['agreement_name'],
                            'next_invoice_amount': member_data['next_invoice_amount'],
                            'active_packages_count': len(active_packages),
                            'active_training_packages': active_packages,
                            'extraction_timestamp': datetime.now().isoformat(),
                            'api_result': result
                        }
                        
                        all_active_packages.append(active_package_record)
                        
                        # Show package details
                        for pkg in active_packages:
                            print(f"      🎯 Package: {pkg.get('name', 'Unknown')} | Status: {pkg.get('status', 'Unknown')}")
                    else:
                        print(f"   ⚠️  No ACTIVE training packages found (found {len(packages)} total)")
                else:
                    print(f"   ⚠️  No training packages found")
                    
            else:
                error_msg = result.get("error", "Unknown API error")
                print(f"   ❌ API error: {error_msg}")
                
            # Rate limiting - be nice to the API
            time.sleep(1)
                
        except Exception as e:
            print(f"   💥 Exception processing {member_name}: {e}")
            continue
    
    print(f"\n📊 EXTRACTION SUMMARY:")
    print(f"   Total members processed: {len(member_data_list)}")
    print(f"   Members with ACTIVE packages: {len(all_active_packages)}")
    
    return all_active_packages


def process_training_clients_csv(csv_file_path: str) -> bool:
    """
    Main function to process training clients CSV and extract active package data.
    
    Args:
        csv_file_path: Path to the training clients CSV file
        
    Returns:
        True if successful, False otherwise
    """
    print("🚀 TRAINING PACKAGE EXTRACTION STARTED")
    print("="*60)
    print(f"   📄 Input file: {csv_file_path}")
    
    # Step 1: Extract member data from CSV
    member_data = extract_member_ids_from_csv(csv_file_path)
    
    if not member_data:
        print("❌ No valid member data found in CSV")
        return False
    
    # Step 2: Fetch active training packages via API
    active_packages = fetch_active_training_packages_via_api(member_data)
    
    if not active_packages:
        print("❌ No active training packages found")
        return False
    
    # Step 3: Save comprehensive data
    try:
        save_success = save_training_package_data_comprehensive(active_packages)
        if save_success:
            print(f"\n✅ SUCCESS: Extracted active training package data for {len(active_packages)} members")
            print(f"   💾 Data saved to package_data/ directory")
            return True
        else:
            print("❌ Failed to save package data")
            return False
            
    except Exception as e:
        print(f"❌ Error saving package data: {e}")
        return False


def main():
    """
    Main entry point - can be used both as module or standalone script.
    """
    # Default to the CSV file in Downloads
    default_csv_path = r"c:\Users\mayoj\Downloads\Clients_1753310478191.csv"
    
    if os.path.exists(default_csv_path):
        print(f"🎯 Using default CSV file: {default_csv_path}")
        success = process_training_clients_csv(default_csv_path)
    else:
        print(f"❌ Default CSV file not found: {default_csv_path}")
        print("Please provide the path to your training clients CSV file")
        return False
        
    if success:
        print("\n🎉 Training package extraction completed successfully!")
        return True
    else:
        print("\n💥 Training package extraction failed!")
        return False


if __name__ == "__main__":
    main()
