"""
Services package initialization
"""

# Import authentication services (these are always available)
try:
    from .authentication import (
        SecureSecretsManager, 
        SecureAuthService, 
        SecureCredentialService,
        get_secret,
        get_clubos_credentials,
        get_clubhub_credentials
    )
except ImportError:
    pass

# Import other services with graceful error handling
try:
    from .ai import get_gemini_client, initialize_services, get_firestore_client
except ImportError:
    pass

try:
    from .clubos import get_messaging_service, send_clubos_message, get_member_conversation
except ImportError:
    pass

try:
    from .payments import get_square_client, create_invoice_for_member, test_square_connection
except ImportError:
    pass
