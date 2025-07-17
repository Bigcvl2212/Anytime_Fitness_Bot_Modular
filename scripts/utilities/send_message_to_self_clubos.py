#!/usr/bin/env python3
"""
Send a message and email to Jeremy Mayo via ClubOS API, printing full API responses.
"""

from services.api.clubos_api_client import ClubOSAPIClient
from config.secrets_local import get_secret


def send_message_and_email():
    member_id = "187032782"
    message = "Fucking perfect. now send me that message and email via api on clubos"
    email_message = "Fucking perfect. This is your ClubOS API email notification."

    client = ClubOSAPIClient()
    if not client.authenticate():
        print("❌ ClubOS authentication failed")
        return

    # Patch the send_message method to print the full response
    def send_message_verbose(self, member_id, message, message_type="text"):
        print(f"📤 Sending {message_type} message to member {member_id}")
        try:
            endpoint = "/action/Dashboard/messages"
            headers = self.auth.get_headers()
            message_data = {
                "memberId": member_id,
                "messageType": message_type,
                "messageText": message,
                "sendMethod": "sms" if message_type == "text" else "email"
            }
            response = self.auth.session.post(
                f"{self.base_url}{endpoint}",
                data=message_data,
                headers=headers,
                timeout=30,
                verify=False
            )
            print(f"   Status code: {response.status_code}")
            print(f"   Response body: {response.text[:1000]}")
            if response.ok:
                print("✅ Message sent successfully (API returned OK)")
                return True
            else:
                print(f"❌ Message send failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Message send error: {e}")
            return False

    # Monkey-patch the method for this run
    client.send_message = send_message_verbose.__get__(client, ClubOSAPIClient)

    print("\n📤 Sending SMS message...")
    sms_success = client.send_message(member_id, message, message_type="text")
    print(f"SMS sent: {sms_success}")

    print("\n📤 Sending email message...")
    email_success = client.send_message(member_id, email_message, message_type="email")
    print(f"Email sent: {email_success}")

    if sms_success and email_success:
        print("\n✅ Both SMS and email sent successfully!")
    else:
        print("\n⚠️ There was a problem sending one or both messages.")

if __name__ == "__main__":
    send_message_and_email() 