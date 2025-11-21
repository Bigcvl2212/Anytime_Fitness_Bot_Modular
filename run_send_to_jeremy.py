#!/usr/bin/env python3
"""
Send a single test SMS to Jeremy (ID: 187032782) using the proven working client.
"""

import logging
from src.services.authentication.secure_secrets_manager import SecureSecretsManager
from clubos_working_messaging import ClubOSWorkingMessagingClient

logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

JEREMY_ID = "187032782"
TEST_MESSAGE = "🧪 Test SMS to Jeremy from working pattern client (single send)"

def main():
    try:
        sm = SecureSecretsManager()
        username = sm.get_secret('clubos-username')
        password = sm.get_secret('clubos-password')
        
        client = ClubOSWorkingMessagingClient(username, password)
        if not client.authenticate():
            print("❌ Authentication failed")
            return
        
        ok = client.send_message_working_pattern(JEREMY_ID, TEST_MESSAGE)
        if ok:
            print("✅ Message sent successfully to Jeremy (187032782)")
        else:
            print("❌ Message send failed (check logs)")
    except Exception as e:
        print(f"❌ Exception during send: {e}")

if __name__ == "__main__":
    main()
