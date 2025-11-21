"""
Message formatting utilities.
"""

def format_message(template, **kwargs):
    """
    Format a message template with provided variables.
    
    Args:
        template (str): Message template with placeholders
        **kwargs: Variables to substitute in template
        
    Returns:
        str: Formatted message
    """
    try:
        return template.format(**kwargs)
    except KeyError as e:
        print(f"WARNING: Missing template variable: {e}")
        return template
    except Exception as e:
        print(f"ERROR: Message formatting failed: {e}")
        return template

def format_currency(amount):
    """Format currency amount."""
    return f"${amount:.2f}"

def format_phone(phone_number):
    """Format phone number."""
    # Simple phone formatting
    digits = ''.join(filter(str.isdigit, phone_number))
    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    return phone_number
