#!/usr/bin/env python3
"""
Member Retention System - Automated Check-ins
Automatically checks in members to increase gym usage and prevent transfers
"""

import sys
import os
import json
import sqlite3
import time
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
import logging

# Add the services directory to the path so we can import the ClubHub API client
sys.path.append(os.path.join(os.path.dirname(__file__), 'services'))
from api.clubhub_api_client import ClubHubAPIClient

# Import stored credentials
from config.clubhub_credentials import CLUBHUB_EMAIL, CLUBHUB_PASSWORD

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MemberRetentionSystem:
    """
    Automated member check-in system to boost usage statistics for retention
    """
    
    def __init__(self):
        """Initialize the retention system with automatic ClubHub authentication"""
        self.club_id = 1156  # Your club ID
        self.door_id = 772   # Main entrance door ID (from API logs)
        
        # Initialize ClubHub API client
        self.clubhub_client = ClubHubAPIClient()
        self.authenticated = False
        
        # Automatically authenticate using stored credentials
        self.authenticate()
    
    def authenticate(self) -> bool:
        """Authenticate with ClubHub using stored credentials"""
        try:
            success = self.clubhub_client.authenticate(CLUBHUB_EMAIL, CLUBHUB_PASSWORD)
            if success:
                self.authenticated = True
                logger.info("✅ ClubHub authentication successful (automated)")
                return True
            else:
                logger.error("❌ ClubHub authentication failed")
                return False
        except Exception as e:
            logger.error(f"❌ Authentication error: {e}")
            return False
    
    def manual_checkin_member(self, member_id: str, checkin_datetime: datetime = None) -> bool:
        """
        Perform a manual check-in for a specific member
        
        Args:
            member_id: The ClubHub member ID
            checkin_datetime: When to mark the check-in (defaults to now)
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self.authenticated:
                logger.error("❌ Not authenticated - please authenticate first")
                return False
            
            # Use provided datetime or current time
            if checkin_datetime is None:
                checkin_datetime = datetime.now()
            
            # Format datetime for API (ISO format with timezone)
            formatted_date = checkin_datetime.strftime("%Y-%m-%dT%H:%M:%S-05:00")
            
            # Prepare check-in data
            checkin_data = {
                "date": formatted_date,
                "door": {"id": self.door_id},
                "club": {"id": self.club_id},
                "manual": True
            }
            
            logger.info(f"🔄 Checking in member {member_id} at {formatted_date}")
            
            # Use ClubHub API client to post the usage
            response = self.clubhub_client.post_member_usage(member_id, checkin_data)
            
            if response is not None:
                logger.info(f"✅ Successfully checked in member {member_id}")
                return True
            else:
                logger.error(f"❌ Check-in failed for member {member_id}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error checking in member {member_id}: {e}")
            return False
    
    def get_member_list(self) -> List[Dict[str, Any]]:
        """
        Get list of members from the local database
        Returns list of members with their ClubHub IDs
        """
        try:
            # Connect to the gym database
            conn = sqlite3.connect('gym_bot.db')
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get members with ClubHub member IDs
            cursor.execute("""
                SELECT id, email, first_name, last_name, clubhub_member_id
                FROM members 
                WHERE clubhub_member_id IS NOT NULL 
                AND clubhub_member_id != ''
                LIMIT 100
            """)
            
            members = []
            for row in cursor.fetchall():
                members.append({
                    'id': row['id'],
                    'email': row['email'],
                    'name': f"{row['first_name']} {row['last_name']}".strip(),
                    'clubhub_id': row['clubhub_member_id']
                })
            
            conn.close()
            logger.info(f"📋 Found {len(members)} members with ClubHub IDs")
            return members
            
        except Exception as e:
            logger.error(f"❌ Error getting member list: {e}")
            return []
    
    def bulk_checkin_members(self, member_list: List[Dict], checkin_date: datetime = None, 
                           delay_seconds: int = 2) -> Dict[str, int]:
        """
        Check in multiple members with random timing to appear natural
        
        Args:
            member_list: List of member dictionaries with 'clubhub_id' and 'name'
            checkin_date: Date to check them in (defaults to today)
            delay_seconds: Delay between check-ins to avoid rate limiting
        
        Returns:
            Dict with success/failure counts
        """
        if checkin_date is None:
            checkin_date = datetime.now()
        
        results = {'success': 0, 'failed': 0, 'total': len(member_list)}
        
        logger.info(f"🎯 Starting bulk check-in for {len(member_list)} members on {checkin_date.strftime('%Y-%m-%d')}")
        
        for i, member in enumerate(member_list):
            try:
                # Add random variation to check-in times (spread over the day)
                random_hours = random.randint(6, 22)  # 6 AM to 10 PM
                random_minutes = random.randint(0, 59)
                
                member_checkin_time = checkin_date.replace(
                    hour=random_hours,
                    minute=random_minutes,
                    second=random.randint(0, 59)
                )
                
                # Perform the check-in
                success = self.manual_checkin_member(member['clubhub_id'], member_checkin_time)
                
                if success:
                    results['success'] += 1
                    logger.info(f"✅ [{i+1}/{len(member_list)}] Checked in {member.get('name', 'Unknown')}")
                else:
                    results['failed'] += 1
                    logger.warning(f"❌ [{i+1}/{len(member_list)}] Failed to check in {member.get('name', 'Unknown')}")
                
                # Add delay to avoid rate limiting and appear more natural
                if i < len(member_list) - 1:  # Don't delay after the last member
                    time.sleep(delay_seconds + random.uniform(0, 2))  # Random additional delay
                    
            except Exception as e:
                logger.error(f"❌ Error processing member {member.get('name', 'Unknown')}: {e}")
                results['failed'] += 1
        
        logger.info(f"🎉 Bulk check-in complete: {results['success']} successful, {results['failed']} failed")
        return results
    
    def daily_retention_checkins(self, percentage: float = 0.3) -> Dict[str, int]:
        """
        Perform daily automatic check-ins for member retention
        
        Args:
            percentage: What percentage of members to check in (0.0 to 1.0)
        
        Returns:
            Dict with results
        """
        logger.info(f"🚀 Starting daily retention check-ins ({percentage*100:.1f}% of members)")
        
        # Get all members
        all_members = self.get_member_list()
        
        if not all_members:
            logger.warning("⚠️ No members found with ClubHub IDs")
            return {'success': 0, 'failed': 0, 'total': 0}
        
        # Select random subset of members
        num_to_checkin = int(len(all_members) * percentage)
        selected_members = random.sample(all_members, min(num_to_checkin, len(all_members)))
        
        logger.info(f"🎯 Selected {len(selected_members)} members out of {len(all_members)} for check-in")
        
        # Perform bulk check-ins
        return self.bulk_checkin_members(selected_members)

def main():
    """Main function to test the retention system"""
    
    print("🏋️ Member Retention System - Automated Check-ins")
    print("=" * 50)
    
    # Initialize with automatic authentication
    retention_system = MemberRetentionSystem()
    
    if not retention_system.authenticated:
        print("❌ Authentication failed. Exiting.")
        return
    
    # Test with a few members first
    print("\n🧪 Testing with a small sample...")
    members = retention_system.get_member_list()[:5]  # Test with first 5 members
    
    if members:
        results = retention_system.bulk_checkin_members(members)
        print(f"\n📊 Test Results: {results}")
        
        # Ask if they want to do a full run
        if input("\nRun full daily retention check-ins? (y/n): ").lower() == 'y':
            percentage = float(input("Enter percentage of members to check in (0.1-1.0): ") or 0.3)
            full_results = retention_system.daily_retention_checkins(percentage)
            print(f"\n🎉 Full Results: {full_results}")
    else:
        print("❌ No members found to test with")

if __name__ == "__main__":
    main()
