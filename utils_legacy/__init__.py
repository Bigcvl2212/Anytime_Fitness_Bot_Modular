"""
Utils package initialization
"""

from .debug import get_debug_manager, debug_page_state, log_action
from .formatting import format_message, format_currency, format_phone

# Import available utility modules (data_import is in src/utils, not here)
try:
    from . import staff_designations
    from . import validation
    from . import bulk_checkin_tracking
except ImportError as e:
    print(f"Warning: Could not import some utils modules: {e}")