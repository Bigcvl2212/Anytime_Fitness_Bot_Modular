"""
Payments package initialization
"""

from .square_client_fixed import get_square_client, create_square_invoice, test_square_connection, create_overdue_payment_message_with_invoice

# Aliases for backward compatibility
create_invoice_for_member = create_square_invoice
