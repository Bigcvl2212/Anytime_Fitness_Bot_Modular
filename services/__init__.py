"""
Services package initialization
"""

from .ai import get_gemini_client, initialize_services, get_firestore_client
from .clubos import get_messaging_service, send_clubos_message, get_member_conversation
from .payments import get_square_client, create_invoice_for_member, test_square_connection
