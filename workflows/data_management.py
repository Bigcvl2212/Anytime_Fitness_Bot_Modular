"""
Data Management Workflows - PROVEN WORKING CODE FROM ORIGINAL SCRIPT
Contains ONLY proven data management functions from Anytime_Bot.py
"""

import os
import pandas as pd
from ..config.constants import MASTER_CONTACT_LIST_PATH


def read_master_contact_list():
    """
    Reads the master contact list from Excel file and returns a DataFrame.
    
    PROVEN FUNCTION FROM ORIGINAL ANYTIME_BOT.PY
    """
    try:
        if os.path.exists(MASTER_CONTACT_LIST_PATH):
            df = pd.read_excel(MASTER_CONTACT_LIST_PATH, dtype=str).fillna("")
            print(f"   INFO: Successfully read {len(df)} contacts from {MASTER_CONTACT_LIST_PATH}")
            return df
        else:
            print(f"   ERROR: Contact list file not found: {MASTER_CONTACT_LIST_PATH}")
            return pd.DataFrame()
    except Exception as e:
        print(f"   ERROR: Failed to read contact list: {e}")
        return pd.DataFrame()
