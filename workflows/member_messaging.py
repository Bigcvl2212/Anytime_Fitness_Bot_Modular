"""
Member Messaging Workflow - PROVEN WORKING CODE FROM ORIGINAL SCRIPT
Contains the EXACT working member processing functions from Anytime_Bot.py
"""

import pandas as pd

# Import the read_master_contact_list function from data_management
from .data_management import read_master_contact_list

def get_yellow_red_members():
    """
    Identifies yellow/red members from the contact list who need invoice processing.
    Returns a list of members with their overdue information.
    
    PROVEN FUNCTION FROM ORIGINAL ANYTIME_BOT.PY
    """
    try:
        df = read_master_contact_list()
        if df.empty:
            print("   WARNING: No contact list data available")
            return []
        
        # Debug: Show available columns
        print(f"   DEBUG: Available columns: {list(df.columns)}")
        
        # Try different possible column names for status
        status_columns = ['MessagingStatus', 'Status', 'Membership Status', 'Member Status']
        status_col = None
        for col in status_columns:
            if col in df.columns:
                status_col = col
                break
        
        if not status_col:
            print("   WARNING: No status column found in contact list")
            return []
        
        # Filter for yellow/red members
        yellow_red_filter = df[status_col].str.contains('Yellow|Red', case=False, na=False)
        yellow_red_members = df[yellow_red_filter].copy()
        
        print(f"   INFO: Found {len(yellow_red_members)} yellow/red members")
        
        # Convert to list of dictionaries for easier processing
        members_list = []
        for _, row in yellow_red_members.iterrows():
            member_info = {
                'name': row.get('Name', ''),
                'status': row.get(status_col, ''),
                'email': row.get('Email', ''),
                'phone': row.get('Phone', ''),
                'prospect_id': row.get('ProspectID', ''),
                'category': row.get('Category', '')
            }
            members_list.append(member_info)
        
        # Debug: Show first few members
        for i, member in enumerate(members_list[:3]):
            print(f"   DEBUG: Member {i+1}: {member['name']} - {member['status']}")
        
        return members_list
        
    except Exception as e:
        print(f"   ERROR: Failed to get yellow/red members: {e}")
        return []


def create_overdue_payment_message_with_invoice(member_name, membership_amount, late_fee=25.00):
    """
    Creates an overdue payment message with Square invoice link.
    
    PROVEN FUNCTION FROM ORIGINAL ANYTIME_BOT.PY
    
    Args:
        member_name (str): Member's name
        membership_amount (float): Base membership amount owed
        late_fee (float): Late fee amount
    
    Returns:
        tuple: (message_text, invoice_url) or (None, None) if failed
    """
    # Import locally to avoid circular imports
    from ..services.payments.square_client import create_square_invoice
    
    total_amount = membership_amount + late_fee
    
    # Create Square invoice
    invoice_url = create_square_invoice(
        member_name=member_name,
        amount=total_amount, 
        description=f"Overdue Membership Payment + Late Fee"
    )
    
    if not invoice_url:
        print(f"ERROR: Could not create invoice for {member_name}")
        return None, None
    
    # Create message with invoice link (using hardcoded template to avoid imports)
    message_template = """Hi {member_name}! Your membership payment is overdue: ${membership_amount:.2f} + ${late_fee:.2f} late fee = ${total_amount:.2f}. Pay now: {invoice_link} IF YOU DO NOT RESPOND WITHIN 7 DAYS YOUR ACCOUNT WILL BE FLAGGED FOR COLLECTIONS! -Anytime Fitness FDL"""
    
    message = message_template.format(
        member_name=member_name,
        membership_amount=membership_amount,
        late_fee=late_fee,
        total_amount=total_amount,
        invoice_link=invoice_url
    )
    
    return message, invoice_url
