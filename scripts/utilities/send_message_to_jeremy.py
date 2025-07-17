#!/usr/bin/env python3
"""
Send SMS and Email to Jeremy Mayo via ClubOS API
"""

from services.api.clubos_api_client import ClubOSAPIClient

TARGET_NAME = "Jeremy Mayo"
SMS_MESSAGE = "This is a test SMS sent via the ClubOS API."
EMAIL_MESSAGE = "This is a test EMAIL sent via the ClubOS API."


def main():
    print(f"🔍 Searching for member: {TARGET_NAME}")
    client = ClubOSAPIClient()
    if not client.authenticate():
        print("❌ Authentication failed")
        return

    # Search for Jeremy Mayo
    members = client.search_members(TARGET_NAME)
    if not members:
        print(f"❌ No members found for '{TARGET_NAME}'")
        return

    # Print all found members
    print(f"✅ Found {len(members)} member(s):")
    for idx, member in enumerate(members):
        print(f"  {idx+1}. {member.get('name', 'Unknown')} (ID: {member.get('id', 'N/A')})")

    # Try to find exact match
    member_id = None
    for member in members:
        if member.get('name', '').lower() == TARGET_NAME.lower():
            member_id = member.get('id')
            break
    if not member_id and members:
        member_id = members[0].get('id')  # fallback to first

    if not member_id:
        print(f"❌ Could not extract member ID for '{TARGET_NAME}'")
        return

    print(f"\n📲 Sending SMS to {TARGET_NAME} (ID: {member_id})...")
    sms_result = client.send_message(member_id, SMS_MESSAGE, message_type="text")
    print(f"SMS send result: {'✅ Success' if sms_result else '❌ Failed'}")

    print(f"\n📧 Sending EMAIL to {TARGET_NAME} (ID: {member_id})...")
    email_result = client.send_message(member_id, EMAIL_MESSAGE, message_type="email")
    print(f"Email send result: {'✅ Success' if email_result else '❌ Failed'}")

if __name__ == "__main__":
    main() 