"""
CSV Data Handler
Handles loading and saving CSV data files.
"""

import pandas as pd
from typing import List, Dict, Any, Optional


def load_csv_data(file_path: str) -> Optional[List[Dict[str, Any]]]:
    """
    Load data from a CSV file.
    
    Args:
        file_path (str): Path to the CSV file
        
    Returns:
        List[Dict[str, Any]]: List of records or None if failed
    """
    try:
        df = pd.read_csv(file_path)
        return df.to_dict('records')
    except FileNotFoundError:
        print(f"WARNING: CSV file not found: {file_path}")
        return None
    except Exception as e:
        print(f"ERROR: Failed to load CSV data from {file_path}: {e}")
        return None


def save_csv_data(data: List[Dict[str, Any]], file_path: str) -> bool:
    """
    Save data to a CSV file.
    
    Args:
        data (List[Dict[str, Any]]): Data to save
        file_path (str): Path to save the CSV file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        df = pd.DataFrame(data)
        df.to_csv(file_path, index=False)
        print(f"SUCCESS: Saved CSV data to {file_path}")
        return True
    except Exception as e:
        print(f"ERROR: Failed to save CSV data to {file_path}: {e}")
        return False
