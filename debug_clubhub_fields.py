#!/usr/bin/env python3
"""
Debug script to verify ClubHub API response fields
Tests what fields are actually returned for member data
"""

import sys
import os
import logging
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from services.api.clubhub_api_client import ClubHubAPIClient
from services.authentication.secure_secrets_manager import SecureSecretsManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def debug_clubhub_fields():
    """Test ClubHub API to see what fields are returned"""

    logger.info("🔍 Testing ClubHub API field structure...")

    # Get credentials - try both global and manager-specific
    secrets_manager = SecureSecretsManager()

    # Try to get manager ID from database
    manager_id = None
    try:
        import sqlite3
        db_path = os.path.expanduser("~\\AppData\\Local\\GymBot\\data\\gym_bot.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT manager_id FROM admin_users LIMIT 1")
        result = cursor.fetchone()
        if result:
            manager_id = result[0]
        conn.close()
    except Exception as e:
        logger.warning(f"⚠️ Could not get manager_id from database: {e}")

    # Get credentials (manager-specific or global)
    if manager_id:
        logger.info(f"📋 Using manager_id: {manager_id}")
        credentials = secrets_manager.get_credentials(manager_id)
        clubhub_email = credentials.get('clubhub_email') if credentials else None
        clubhub_password = credentials.get('clubhub_password') if credentials else None
    else:
        logger.info("📋 Using global credentials")
        clubhub_email = secrets_manager.get_secret('clubhub-email')
        clubhub_password = secrets_manager.get_secret('clubhub-password')

    if not clubhub_email or not clubhub_password:
        logger.error("❌ Missing ClubHub credentials")
        return

    # Authenticate
    clubhub_client = ClubHubAPIClient()
    if not clubhub_client.authenticate(clubhub_email, clubhub_password):
        logger.error("❌ ClubHub authentication failed")
        return

    logger.info("✅ ClubHub authenticated")

    # Get first member from members list
    logger.info("📥 Fetching members list...")
    members_response = clubhub_client.get_members(limit=1)

    if not members_response or 'data' not in members_response:
        logger.error("❌ Failed to get members")
        return

    members = members_response.get('data', [])
    if not members:
        logger.error("❌ No members found")
        return

    first_member = members[0]
    member_id = first_member.get('id') or first_member.get('prospectId')

    logger.info(f"📋 Testing with member ID: {member_id}")
    logger.info(f"📋 Member name: {first_member.get('firstName')} {first_member.get('lastName')}")

    # Show what fields are in the base members list response
    logger.info("\n" + "="*80)
    logger.info("📄 FIELDS IN BASE MEMBERS LIST RESPONSE:")
    logger.info("="*80)
    for key in sorted(first_member.keys()):
        value = first_member[key]
        if isinstance(value, (dict, list)):
            logger.info(f"  {key}: {type(value).__name__}")
        else:
            logger.info(f"  {key}: {value}")

    # Now get detailed member data
    logger.info("\n" + "="*80)
    logger.info(f"📥 Fetching detailed member data for ID: {member_id}")
    logger.info("="*80)

    member_details = clubhub_client.get_member_details(str(member_id))

    if member_details:
        logger.info("\n📄 FIELDS IN DETAILED MEMBER RESPONSE:")
        logger.info("="*80)
        for key in sorted(member_details.keys()):
            value = member_details[key]
            if isinstance(value, (dict, list)):
                logger.info(f"  {key}: {type(value).__name__}")
            else:
                logger.info(f"  {key}: {value}")

        # Check specifically for address fields
        logger.info("\n" + "="*80)
        logger.info("🏠 ADDRESS-RELATED FIELDS:")
        logger.info("="*80)

        address_fields = [
            'address', 'address1', 'address2', 'streetAddress',
            'city', 'state', 'zip', 'zipCode', 'postalCode',
            'phone', 'phoneNumber', 'homePhone', 'workPhone',
            'mobile', 'mobilePhone', 'cellPhone'
        ]

        for field in address_fields:
            if field in member_details:
                logger.info(f"  ✅ {field}: {member_details[field]}")
            else:
                logger.info(f"  ❌ {field}: NOT FOUND")

        # Save full response to file
        output_file = "clubhub_member_response.json"
        with open(output_file, 'w') as f:
            json.dump(member_details, f, indent=2)
        logger.info(f"\n💾 Full response saved to: {output_file}")

    else:
        logger.error("❌ Failed to get detailed member data")

    # Also test get_member_agreement
    logger.info("\n" + "="*80)
    logger.info(f"📥 Fetching member agreement data for ID: {member_id}")
    logger.info("="*80)

    agreement_data = clubhub_client.get_member_agreement(member_id)
    if agreement_data:
        logger.info("\n📄 FIELDS IN AGREEMENT RESPONSE:")
        logger.info("="*80)
        for key in sorted(agreement_data.keys()):
            value = agreement_data[key]
            if isinstance(value, (dict, list)):
                logger.info(f"  {key}: {type(value).__name__}")
            else:
                logger.info(f"  {key}: {value}")

        # Save agreement response
        agreement_file = "clubhub_agreement_response.json"
        with open(agreement_file, 'w') as f:
            json.dump(agreement_data, f, indent=2)
        logger.info(f"\n💾 Full agreement response saved to: {agreement_file}")
    else:
        logger.info("⚠️ No agreement data found")

if __name__ == "__main__":
    debug_clubhub_fields()
