"""
Quick fix for messaging.py indentation issue.
This script will help identify what the frontend is sending.
"""

print("""
=== FRONTEND DEBUGGING GUIDE ===

To see what your frontend is sending, check the browser console (F12) Network tab:

1. Open Developer Tools (F12)
2. Go to Network tab
3. Click "Send Campaign" button
4. Look for the POST request to `/api/campaigns/send`
5. Click on it and look at "Payload" or "Request Payload"

The request should include one of these:
- selected_member_ids: [list of IDs you selected]
- member_ids: [list of IDs you selected]

If you don't see either of these, then the frontend ISN'T sending the selected IDs!

Example of what it SHOULD look like:
{
  "message": "Your message text...",
  "type": "sms",
  "category": "past_due_6_30",
  "selected_member_ids": ["12345", "67890", "11111"],  <-- THIS IS KEY!
  "mode": "fresh",
  "notes": "jeremy 10/9"
}

If selected_member_ids is missing or empty [], then we need to fix the FRONTEND JavaScript code.
""")
