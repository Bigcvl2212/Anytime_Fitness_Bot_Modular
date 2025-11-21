#!/usr/bin/env python3
"""
Test Member Sync Fix
Verify that personal information (email, phone, address) is now captured correctly
"""

import sys
import logging
from src.services.multi_club_startup_sync import sync_members_for_club
from src.services.database_manager import DatabaseManager

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def main():
    """Test member sync with personal information"""
    
    logger.info("=" * 80)
    logger.info("TESTING MEMBER SYNC FIX - Personal Information Capture")
    logger.info("=" * 80)
    
    # Sync just a few members to test
    logger.info("\nSyncing members (limit: 5 for testing)...")
    members = sync_members_for_club(club_id='1156', app=None, manager_id='187032782')
    
    if not members:
        logger.error("❌ No members synced")
        return 1
    
    logger.info(f"✅ Synced {len(members)} members\n")
    
    # Check first 5 members for personal information
    logger.info("PERSONAL INFORMATION CHECK:")
    logger.info("-" * 80)
    
    fields_to_check = ['email', 'mobile_phone', 'phone', 'address', 'city', 'state', 'zip_code']
    
    for i, member in enumerate(members[:5], 1):
        logger.info(f"\nMember {i}: {member.get('full_name', 'Unknown')}")
        logger.info(f"   Prospect ID: {member.get('prospect_id')}")
        
        has_all_info = True
        for field in fields_to_check:
            value = member.get(field)
            status = "✅" if value else "❌"
            logger.info(f"   {status} {field}: {value or 'MISSING'}")
            if not value and field in ['email', 'mobile_phone']:  # Critical fields
                has_all_info = False
        
        if has_all_info:
            logger.info(f"   🎉 ALL PERSONAL INFO CAPTURED!")
        else:
            logger.info(f"   ⚠️  Missing critical personal information")
    
    # Summary statistics
    members_with_email = sum(1 for m in members if m.get('email'))
    members_with_phone = sum(1 for m in members if m.get('mobile_phone') or m.get('phone'))
    members_with_address = sum(1 for m in members if m.get('address'))
    
    logger.info(f"\n{'=' * 80}")
    logger.info("SUMMARY STATISTICS:")
    logger.info(f"   Total members synced: {len(members)}")
    logger.info(f"   Members with email: {members_with_email} ({members_with_email/len(members)*100:.1f}%)")
    logger.info(f"   Members with phone: {members_with_phone} ({members_with_phone/len(members)*100:.1f}%)")
    logger.info(f"   Members with address: {members_with_address} ({members_with_address/len(members)*100:.1f}%)")
    
    if members_with_email > len(members) * 0.9:  # 90%+ have email
        logger.info(f"\n✅ FIX SUCCESSFUL! Personal information is being captured correctly.")
        return 0
    else:
        logger.info(f"\n❌ FIX INCOMPLETE! Still missing personal information for many members.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
