"""
Active Training Package Data Extractor via API

This script takes a CSV file of training clients and uses ClubOS API 
to extract their ACTIVE training package data and payment status.

Usage:
    python extract_training_packages_from_csv.py --csv_file "path/to/clients.csv"
"""

import os
import sys
import pandas as pd
import argparse
import time
import json
from datetime import datetime

# Add the current directory to the path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.services.api.enhanced_clubos_client import create_enhanced_clubos_client
from src.services.data.member_data import save_training_package_data_comprehensive


def extract_member_ids_from_profile_urls(df):
    """
    Extract member IDs from ClubOS profile URLs in the CSV.
    
    Expects URLs like: https://anytime.club-os.com/action/Member/profile/view/id/123456
    """
    member_ids = []
    
    print(f"🔍 Extracting member IDs from {len(df)} rows...")
    
    for index, row in df.iterrows():
        member_name = row.get('Member Name', '')
        profile_url = row.get('Profile', '')
        
        if not profile_url:
            print(f"   ⚠️  No profile URL found for {member_name}")
            continue
            
        # Extract ID from URL - looking for /Delegate/ID format
        if '/Delegate/' in profile_url:
            try:
                member_id = profile_url.split('/Delegate/')[-1].split('/')[0].split('?')[0]
                member_ids.append({
                    'member_name': member_name,
                    'member_id': member_id,
                    'profile_url': profile_url
                })
                print(f"   ✅ {member_name}: ID {member_id}")
            except Exception as e:
                print(f"   ❌ Failed to extract ID from {profile_url} for {member_name}: {e}")
        else:
            print(f"   ⚠️  Invalid profile URL format for {member_name}: {profile_url}")
    
    print(f"   📊 Successfully extracted {len(member_ids)} member IDs")
    return member_ids


def scrape_training_package_data_for_members(member_data_list):
    """
    Fetch ACTIVE training package data for a list of members using ClubOS API.
    This will check each member's account for active training packages and payment status.
    """
    print("🏋️ FETCHING ACTIVE TRAINING PACKAGE DATA VIA API")
    print("="*60)
    
    # Initialize the ClubOS API client
    client = create_enhanced_clubos_client()
    if not client:
        print("❌ Failed to initialize ClubOS API client")
        return []
    
    print("✅ ClubOS API client initialized successfully")
    
    all_package_data = []
    
    for i, member_data in enumerate(member_data_list, 1):
        member_name = member_data['member_name']
        member_id = member_data['member_id']
        
        print(f"\n   📦 Processing {i}/{len(member_data_list)}: {member_name} (ID: {member_id})")
        
        try:
            # Use the API to get member's training packages
            result = client.get_training_packages_for_client(member_id)
            
            if result.get("success", False):
                packages = result.get("training_packages", [])
                print(f"   ✅ Found {len(packages)} training packages")
                
                # Filter for ACTIVE packages only
                active_packages = []
                for package in packages:
                    if package.get('status', '').upper() == 'ACTIVE':
                        active_packages.append(package)
                
                if active_packages:
                    # Add member metadata to the result
                    package_data = {
                        'member_name': member_name,
                        'member_id': member_id,
                        'profile_url': member_data['profile_url'],
                        'extraction_timestamp': datetime.now().isoformat(),
                        'active_training_packages': active_packages,
                        'total_packages': len(packages),
                        'active_package_count': len(active_packages),
                        'member_details': result.get('member_details', {}),
                        'payment_status': result.get('payment_status', 'unknown'),
                        'overdue_amount': result.get('overdue_amount', 0)
                    }
                    
                    all_package_data.append(package_data)
                    print(f"   ✅ Found {len(active_packages)} ACTIVE packages for {member_name}")
                    
                    # Log payment issues if any
                    if result.get('overdue_amount', 0) > 0:
                        print(f"   ⚠️  OVERDUE BALANCE: ${result.get('overdue_amount', 0):.2f}")
                else:
                    print(f"   ⚠️  No ACTIVE packages found for {member_name}")
                    
            else:
                print(f"   ⚠️  No package data found for {member_name}")
                
            # Small delay to avoid overwhelming the API
            time.sleep(0.5)
                
        except Exception as e:
            print(f"   ❌ Error fetching data for {member_name}: {e}")
            continue
    
    return all_package_data


def process_training_clients_csv(csv_file_path):
    """
    Main function to process the training clients CSV and extract package data.
    """
    print("🚀 TRAINING PACKAGE EXTRACTION STARTED")
    print("="*60)
    print(f"   📄 Input file: {csv_file_path}")
    
    # Read the CSV file
    try:
        df = pd.read_csv(csv_file_path)
        print(f"   📊 Loaded {len(df)} rows from CSV")
        print(f"   📋 Columns: {list(df.columns)}")
    except Exception as e:
        print(f"   ❌ Error reading CSV file: {e}")
        return False
    
    # Extract member IDs from profile URLs
    member_data_list = extract_member_ids_from_profile_urls(df)
    
    if not member_data_list:
        print("   ❌ No valid member IDs found in CSV file")
        return False
    
    # Fetch training package data
    package_data = scrape_training_package_data_for_members(member_data_list)
    
    if not package_data:
        print("   ❌ No package data was successfully extracted")
        return False
    
    # Save the comprehensive package data
    try:
        success = save_training_package_data_comprehensive(package_data)
        if success:
            print(f"\n✅ SUCCESS: Extracted training package data for {len(package_data)} members")
            print(f"   💾 Data saved to package_data/ directory")
            return True
        else:
            print("   ❌ Failed to save package data")
            return False
            
    except Exception as e:
        print(f"   ❌ Error saving package data: {e}")
        return False


def main():
    """
    Main entry point for the script.
    """
    parser = argparse.ArgumentParser(description='Extract training package data from CSV of training clients')
    parser.add_argument('--csv_file', required=True, help='Path to the training clients CSV file')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.csv_file):
        print(f"❌ CSV file not found: {args.csv_file}")
        sys.exit(1)
    
    success = process_training_clients_csv(args.csv_file)
    
    if success:
        print("\n🎉 Training package extraction completed successfully!")
        sys.exit(0)
    else:
        print("\n💥 Training package extraction failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
