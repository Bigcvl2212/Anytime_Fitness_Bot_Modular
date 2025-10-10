"""
AI Agent Tools

Collection of tools that the AI agent can use to interact with gym systems
"""

from .campaign_tools import (
    get_campaign_prospects,
    get_green_members,
    get_ppv_members,
    send_bulk_campaign,
    get_campaign_templates
)

from .collections_tools import (
    get_past_due_members,
    get_past_due_training_clients,
    send_payment_reminder,
    track_collection_attempt,
    get_collection_attempts,
    generate_collections_referral_list
)

from .access_tools import (
    lock_door_for_member,
    unlock_door_for_member,
    check_member_access_status,
    auto_manage_access_by_payment_status
)

from .member_tools import (
    get_member_profile,
    add_member_note,
    get_member_messages,
    send_message_to_member
)

__all__ = [
    # Campaign tools
    'get_campaign_prospects',
    'get_green_members',
    'get_ppv_members',
    'send_bulk_campaign',
    'get_campaign_templates',
    
    # Collections tools
    'get_past_due_members',
    'get_past_due_training_clients',
    'send_payment_reminder',
    'track_collection_attempt',
    'get_collection_attempts',
    'generate_collections_referral_list',
    
    # Access tools
    'lock_door_for_member',
    'unlock_door_for_member',
    'check_member_access_status',
    'auto_manage_access_by_payment_status',
    
    # Member tools
    'get_member_profile',
    'add_member_note',
    'get_member_messages',
    'send_message_to_member',
]
