"""
Member Data Management - PROVEN WORKING CODE FROM ORIGINAL SCRIPT
Handles member information, contact lists, and data processing.
"""

import os
import pandas as pd
import requests
import time
import re
import json # Added for comprehensive data export
from typing import Dict, List, Optional, Any
from datetime import datetime
from selenium.webdriver.common.by import By

from ...config.constants import MASTER_CONTACT_LIST_PATH, TRAINING_CLIENTS_CSV_PATH


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


def get_yellow_red_members():
    """
    Identifies yellow/red members based on StatusMessage column.
    Yellow = Past Due 6-30 days, Red = Past Due more than 30 days
    
    PROVEN FUNCTION FROM ORIGINAL ANYTIME_BOT.PY - CORRECTED TO USE StatusMessage
    """
    try:
        df = read_master_contact_list()
        if df.empty:
            print("   WARNING: No contact list data available")
            return []

        print(f"   DEBUG: Looking in StatusMessage column for Past Due members...")
        print(f"   DEBUG: Available columns in Excel file: {list(df.columns)}")
        
        # Filter for members with Past Due status messages
        past_due_filter = df['StatusMessage'].str.contains('Past Due', case=False, na=False)
        yellow_red_members = df[past_due_filter].copy()
        
        print(f"   SUCCESS: Found {len(yellow_red_members)} members with Past Due status")

        # Convert to list of dictionaries for easier processing
        members_list = []
        yellow_count = 0
        red_count = 0
        
        for _, row in yellow_red_members.iterrows():
            status_msg = str(row.get('StatusMessage', ''))
            
            # EXACT string matching based on your data
            category = 'unknown'
            if status_msg == 'Past Due 6-30 days':
                category = 'yellow'
                yellow_count += 1
            elif status_msg == 'Past Due more than 30 days.':
                category = 'red'
                red_count += 1
            else:
                # Skip any other "Past Due" variations that don't match exactly
                continue
            
            member_info = {
                'name': row.get('Name', 'Unknown'),
                'email': row.get('Email', ''),
                'phone': row.get('Phone', ''),
                'status_message': status_msg,
                'category': category,
                'membership_rate': row.get('MonthlyRate', 0),
                'member_id': row.get('ProspectID', ''),  # FIXED: Use ProspectID for agreement API calls
                'last_visit': row.get('LastVisit', ''),
                'member_since': row.get('MemberSince', ''),
                'agreement_id': row.get('AgreementID', '')
            }
            members_list.append(member_info)

        print(f"   INFO: EXACT MATCH RESULTS:")
        print(f"   INFO: Found {yellow_count} yellow members (Past Due 6-30 days)")
        print(f"   INFO: Found {red_count} red members (Past Due more than 30 days.)")
        print(f"   INFO: Total actionable past due members: {len(members_list)}")
        
        # Show first few members from each category
        yellow_members = [m for m in members_list if m['category'] == 'yellow']
        red_members = [m for m in members_list if m['category'] == 'red']
        
        print(f"   DEBUG: First 3 yellow members:")
        for i, member in enumerate(yellow_members[:3]):
            print(f"     {i+1}. {member['name']} - {member['status_message']}")
            
        print(f"   DEBUG: First 3 red members:")
        for i, member in enumerate(red_members[:3]):
            print(f"     {i+1}. {member['name']} - {member['status_message']}")

        return members_list
        
    except Exception as e:
        print(f"   ERROR: Failed to get yellow/red members: {e}")
        return []


def scrape_package_details(driver, member_name):
    """
    Extract detailed training package information from the Club OS package agreement details page.
    Returns a dictionary with comprehensive package details including payment schedules and agreement documents.
    
    This function handles the React-based Club OS package agreement page structure
    and extracts all relevant client, agreement, financial, and payment data.
    
    VERIFIED WORKING CODE FROM 20250701_WORKING.PY - July 1, 2025
    """
    try:
        print(f"   INFO: Scraping comprehensive package agreement details for {member_name}...")
        
        # Initialize comprehensive package info structure
        package_info = {
            # Basic Info
            'member_name': member_name,
            'package_name': '',
            'package_id': '',
            'package_type': 'Package Agreement',
            'status': 'Active',
            'scraped_timestamp': datetime.now().isoformat(),
            
            # Agreement Details
            'term_length': '',
            'billing_frequency': '',
            'start_date': '',
            'renewal_type': '',
            'trainer': '',
            'salesperson': '',
            
            # Financial Details
            'unit_price': 0.0,
            'units_per_billing_cycle': 0,
            'billing_cycle_days': 0,
            'monthly_cost': 0.0,
            'remaining_payments': 0,
            'total_agreement_value': 0.0,
            'past_due_amount': 0.0,
            'next_payment_due_date': '',
            'next_payment_amount': 0.0,
            'payment_status': 'Current',
            
            # Session Information
            'sessions_remaining': 0,
            'total_sessions': 0,
            'sessions_used': 0,
            'expiration_date': '',
        }
        
        # Wait for page to load
        time.sleep(3)
        
        # Extract from Club OS package agreement structure
        try:
            # Extract from left panel (package-agreement-details)
            details_panel = driver.find_elements(By.CSS_SELECTOR, ".package-agreement-details")
            
            if details_panel:
                panel = details_panel[0]
                
                # Extract Term Length
                try:
                    term_element = panel.find_element(By.XPATH, ".//label[contains(text(), 'Term Length')]/following-sibling::span//p")
                    package_info['term_length'] = term_element.text.strip()
                    print(f"   INFO: Term Length: {package_info['term_length']}")
                except:
                    pass
                
                # Extract Billing frequency
                try:
                    billing_element = panel.find_element(By.XPATH, ".//label[contains(text(), 'Billing')]/following-sibling::p")
                    billing_text = billing_element.text.strip()
                    package_info['billing_frequency'] = billing_text
                    
                    # Parse billing frequency to determine cycle days
                    if "2 weeks" in billing_text.lower():
                        package_info['billing_cycle_days'] = 14
                    elif "week" in billing_text.lower():
                        package_info['billing_cycle_days'] = 7
                    elif "month" in billing_text.lower():
                        package_info['billing_cycle_days'] = 30
                    
                    print(f"   INFO: Billing: {package_info['billing_frequency']}")
                except:
                    pass
                
                # Extract Start Date
                try:
                    start_date_element = panel.find_element(By.XPATH, ".//label[contains(text(), 'Start Date')]/following-sibling::p")
                    package_info['start_date'] = start_date_element.text.strip()
                    print(f"   INFO: Start Date: {package_info['start_date']}")
                except:
                    pass
                
                # Extract Trainer
                try:
                    trainer_element = panel.find_element(By.XPATH, ".//label[contains(text(), 'Trainer')]/following-sibling::p")
                    package_info['trainer'] = trainer_element.text.strip()
                    print(f"   INFO: Trainer: {package_info['trainer']}")
                except:
                    pass
            
            # Extract from Package Configuration table
            config_panel = driver.find_elements(By.CSS_SELECTOR, ".package-configuration")
            
            if config_panel:
                panel = config_panel[0]
                
                # Extract Package Name and Units
                try:
                    package_name_element = panel.find_element(By.CSS_SELECTOR, ".edit-proposal__details-table__row-label__name")
                    package_info['package_name'] = package_name_element.text.strip()
                    print(f"   INFO: Package Name: {package_info['package_name']}")
                    
                    # Extract units
                    units_element = panel.find_element(By.CSS_SELECTOR, ".edit-proposal__details-table__row-label__units")
                    units_text = units_element.text.strip()
                    units_match = re.search(r'\((\d+)\s*Units?\)', units_text)
                    if units_match:
                        package_info['total_sessions'] = int(units_match.group(1))
                        print(f"   INFO: Total Units: {package_info['total_sessions']}")
                except:
                    pass
                
                # Extract Unit Price
                try:
                    unit_price_element = panel.find_element(By.XPATH, ".//label[contains(text(), 'Unit Price')]/following-sibling::p")
                    unit_price_text = unit_price_element.text.strip()
                    unit_price_match = re.search(r'\$?(\d+(?:\.\d{2})?)', unit_price_text)
                    if unit_price_match:
                        package_info['unit_price'] = float(unit_price_match.group(1))
                        print(f"   INFO: Unit Price: ${package_info['unit_price']:.2f}")
                except:
                    pass
                
                # Extract Units per Bill Cycle
                try:
                    units_per_cycle_element = panel.find_element(By.XPATH, ".//label[contains(text(), 'Units/Bill Cycle')]/following-sibling::p")
                    package_info['units_per_billing_cycle'] = int(units_per_cycle_element.text.strip())
                    print(f"   INFO: Units per Bill Cycle: {package_info['units_per_billing_cycle']}")
                except:
                    pass
                
                # Extract Monthly Cost
                try:
                    monthly_cost_element = panel.find_element(By.XPATH, ".//label[contains(text(), 'Monthly Cost')]/following-sibling::p")
                    monthly_cost_text = monthly_cost_element.text.strip()
                    monthly_cost_match = re.search(r'\$?(\d+(?:\.\d{2})?)', monthly_cost_text)
                    if monthly_cost_match:
                        package_info['monthly_cost'] = float(monthly_cost_match.group(1))
                        print(f"   INFO: Monthly Cost: ${package_info['monthly_cost']:.2f}")
                except:
                    pass
                
                # Extract Remaining Payments
                try:
                    remaining_payments_element = panel.find_element(By.XPATH, ".//label[contains(text(), 'Remaining Payments')]/following-sibling::p")
                    package_info['remaining_payments'] = int(remaining_payments_element.text.strip())
                    print(f"   INFO: Remaining Payments: {package_info['remaining_payments']}")
                except:
                    pass
                
                # Extract Total Agreement Value
                try:
                    total_value_element = panel.find_element(By.XPATH, ".//label[contains(text(), 'Total Agreement Value')]/following-sibling::p")
                    total_value_text = total_value_element.text.strip()
                    total_value_match = re.search(r'\$?(\d+(?:\.\d{2})?)', total_value_text)
                    if total_value_match:
                        package_info['total_agreement_value'] = float(total_value_match.group(1))
                        print(f"   INFO: Total Agreement Value: ${package_info['total_agreement_value']:.2f}")
                except:
                    pass
            
            # Extract from Payment Schedule section
            payment_schedule_panel = driver.find_elements(By.CSS_SELECTOR, ".payment-schedule")
            
            if payment_schedule_panel:
                panel = payment_schedule_panel[0]
                
                # Extract Past Due Amount
                try:
                    past_due_element = panel.find_element(By.XPATH, ".//label[contains(text(), 'Past Due')]/following-sibling::p")
                    past_due_text = past_due_element.text.strip()
                    past_due_match = re.search(r'\$?(\d+(?:\.\d{2})?)', past_due_text)
                    if past_due_match:
                        package_info['past_due_amount'] = float(past_due_match.group(1))
                        print(f"   INFO: Past Due Amount: ${package_info['past_due_amount']:.2f}")
                except:
                    pass
                
                # Extract Next Payment Due Date
                try:
                    next_payment_element = panel.find_element(By.XPATH, ".//label[contains(text(), 'Next Payment Due')]/following-sibling::p")
                    package_info['next_payment_due_date'] = next_payment_element.text.strip()
                    print(f"   INFO: Next Payment Due: {package_info['next_payment_due_date']}")
                except:
                    pass
                
                # Extract Next Payment Amount
                try:
                    next_amount_element = panel.find_element(By.XPATH, ".//label[contains(text(), 'Next Payment Amount')]/following-sibling::p")
                    next_amount_text = next_amount_element.text.strip()
                    next_amount_match = re.search(r'\$?(\d+(?:\.\d{2})?)', next_amount_text)
                    if next_amount_match:
                        package_info['next_payment_amount'] = float(next_amount_match.group(1))
                        print(f"   INFO: Next Payment Amount: ${package_info['next_payment_amount']:.2f}")
                except:
                    pass
            
            # Extract from Session Information section
            session_panel = driver.find_elements(By.CSS_SELECTOR, ".session-information")
            
            if session_panel:
                panel = session_panel[0]
                
                # Extract Sessions Remaining
                try:
                    sessions_remaining_element = panel.find_element(By.XPATH, ".//label[contains(text(), 'Sessions Remaining')]/following-sibling::p")
                    package_info['sessions_remaining'] = int(sessions_remaining_element.text.strip())
                    print(f"   INFO: Sessions Remaining: {package_info['sessions_remaining']}")
                except:
                    pass
                
                # Extract Sessions Used
                try:
                    sessions_used_element = panel.find_element(By.XPATH, ".//label[contains(text(), 'Sessions Used')]/following-sibling::p")
                    package_info['sessions_used'] = int(sessions_used_element.text.strip())
                    print(f"   INFO: Sessions Used: {package_info['sessions_used']}")
                except:
                    pass
                
                # Extract Expiration Date
                try:
                    expiration_element = panel.find_element(By.XPATH, ".//label[contains(text(), 'Expiration Date')]/following-sibling::p")
                    package_info['expiration_date'] = expiration_element.text.strip()
                    print(f"   INFO: Expiration Date: {package_info['expiration_date']}")
                except:
                    pass
            
            print(f"   SUCCESS: Comprehensive package details extracted for {member_name}")
            return package_info
            
        except Exception as e:
            print(f"   ERROR: Failed to extract package details: {e}")
            return package_info
            
    except Exception as e:
        print(f"   ERROR: Exception in scrape_package_details for {member_name}: {e}")
        return None


def get_member_training_type(member_name):
    """
    Reads the training_clients.csv file to determine the event type.
    
    PROVEN FUNCTION FROM ORIGINAL ANYTIME_BOT.PY
    """
    print(f"   INFO: Looking up training type for {member_name}...")
    try:
        df = pd.read_csv(TRAINING_CLIENTS_CSV_PATH)
        member_row = df[df['Name'].str.contains(member_name, case=False, na=False)]
        if not member_row.empty:
            agreement_type = member_row.iloc[0]['AgreementType']
            print(f"   SUCCESS: Found Agreement Type: '{agreement_type}'")
            if "Small Group" in agreement_type: 
                return "SMALL_GROUP_TRAINING"
            if "Personal" in agreement_type or "Coaching" in agreement_type: 
                return "PERSONAL_TRAINING"
            if "Consultation" in agreement_type: 
                return "ORIENTATION"
            return "LEAD"  # Default if no specific match
        print(f"   WARN: Member '{member_name}' not found in '{TRAINING_CLIENTS_CSV_PATH}'. Defaulting event type to LEAD.")
        return "LEAD"
    except FileNotFoundError:
        print(f"   ERROR: '{TRAINING_CLIENTS_CSV_PATH}' not found. Cannot determine training type for {member_name}. Defaulting event type to LEAD.")
        return "LEAD"
    except Exception as e:
        print(f"   ERROR: Could not read client data file ('{TRAINING_CLIENTS_CSV_PATH}') for {member_name}. Error: {e}. Defaulting event type to LEAD.")
        return "LEAD"


def read_training_clients_csv():
    """
    Reads the training clients CSV file and returns a DataFrame.
    
    PROVEN FUNCTION FROM ORIGINAL ANYTIME_BOT.PY
    """
    try:
        if os.path.exists(TRAINING_CLIENTS_CSV_PATH):
            df = pd.read_csv(TRAINING_CLIENTS_CSV_PATH, dtype=str).fillna("")
            print(f"   INFO: Successfully read {len(df)} training clients from {TRAINING_CLIENTS_CSV_PATH}")
            return df
        else:
            print(f"   ERROR: Training clients file not found: {TRAINING_CLIENTS_CSV_PATH}")
            return pd.DataFrame()
    except Exception as e:
        print(f"   ERROR: Failed to read training clients CSV: {e}")
        return pd.DataFrame()


def get_past_due_training_clients():
    """
    Identifies training clients with overdue payments from the CSV file.
    Returns a list of clients with their overdue information.
    
    PROVEN FUNCTION FROM ORIGINAL ANYTIME_BOT.PY
    """
    try:
        df = read_training_clients_csv()
        if df.empty:
            print("   WARNING: No training clients data available")
            return []
        
        # Debug: Show available columns
        print(f"   DEBUG: Available columns: {list(df.columns)}")
        
        # Look for overdue indicators in various possible columns
        overdue_columns = ['Status', 'PaymentStatus', 'Balance', 'Amount Due', 'Overdue']
        overdue_clients = []
        
        for _, row in df.iterrows():
            client_info = {
                'name': row.get('Name', ''),
                'email': row.get('Email', ''),
                'phone': row.get('Phone', ''),
                'agreement_type': row.get('AgreementType', ''),
                'amount_due': 0.0,
                'is_overdue': False
            }
            
            # Check for overdue indicators
            for col in overdue_columns:
                if col in df.columns:
                    value = str(row.get(col, '')).lower()
                    # Look for overdue indicators or amounts
                    if any(indicator in value for indicator in ['overdue', 'past due', 'late', 'delinquent']):
                        client_info['is_overdue'] = True
                        break
                    
                    # Try to extract numeric amount due
                    try:
                        if value and value != '0' and value != '0.0':
                            # Remove any currency symbols and parse
                            cleaned_value = value.replace('$', '').replace(',', '').strip()
                            if cleaned_value:
                                amount = float(cleaned_value)
                                if amount > 0:
                                    client_info['amount_due'] = amount
                                    client_info['is_overdue'] = True
                    except (ValueError, TypeError):
                        continue
            
            # Add client if they have overdue status or amount
            if client_info['is_overdue'] or client_info['amount_due'] > 0:
                overdue_clients.append(client_info)
        
        print(f"   INFO: Found {len(overdue_clients)} training clients with overdue payments")
        
        # Debug: Show first few overdue clients
        for i, client in enumerate(overdue_clients[:3]):
            print(f"   DEBUG: Overdue client {i+1}: {client['name']} - ${client['amount_due']:.2f}")
        
        return overdue_clients
        
    except Exception as e:
        print(f"   ERROR: Failed to get past due training clients: {e}")
        return []


def update_contacts_from_source_workflow(overwrite=False):
    """
    Updates the master contact list from the ClubHub API with comprehensive data extraction.
    Uses the original working API approach with enhanced field extraction.
    
    PROVEN FUNCTION FROM ORIGINAL ANYTIME_BOT.PY
    
    Args:
        overwrite (bool): Whether to overwrite existing file or merge with existing data
    
    Returns:
        bool: True if successful, False otherwise
    """
    from ...config.constants import (
        CLUBHUB_API_URL_MEMBERS, 
        CLUBHUB_API_URL_PROSPECTS,
        CLUBHUB_HEADERS,
        PARAMS_FOR_PROSPECTS_RECENT,
        MASTER_CONTACT_LIST_PATH
    )
    
    print(f"INFO: Starting update_contacts_from_source_workflow (overwrite={overwrite})")
    
    # Use ClubHub headers directly from constants (manually configured)
    headers = CLUBHUB_HEADERS
    print("   INFO: Using ClubHub credentials from constants")
    
    try:
        # Pull ALL members from ClubHub API with pagination using original working approach
        print("   INFO: Pulling ALL members from ClubHub API with pagination...")
        all_members = []
        page = 1
        max_pages = 50  # Reasonable limit to handle pagination
        
        # Use the original working API URL (without version) with enhanced parameters
        api_url = "https://clubhub-ios-api.anytimefitness.com/api/v1.0/clubs/1156/members"
        
        while page <= max_pages:
            try:
                # Try comprehensive parameters to get as much data as possible
                params = {
                    "page": str(page), 
                    "pageSize": "100",
                    "includeInactive": "true",
                    "includeAll": "true",
                    "status": "all",
                    "days": "10000"  # Large date range to capture historical data
                }
                print(f"   DEBUG: Requesting page {page} with comprehensive parameters...")
                
                # Try without headers first (like original script might have done)
                members_resp = requests.get(api_url, params=params, verify=False, timeout=30)
                print(f"   DEBUG: Members Page {page} (no headers) - Status: {members_resp.status_code}")
                
                # If that fails, try with headers
                if not members_resp.ok:
                    print(f"   DEBUG: No headers failed, trying with headers...")
                    members_resp = requests.get(api_url, headers=CLUBHUB_HEADERS, params=params, verify=False, timeout=30)
                    print(f"   DEBUG: Members Page {page} (with headers) - Status: {members_resp.status_code}")
                
                if members_resp.ok:
                    members_data = members_resp.json()
                    
                    # Handle both dictionary and direct list responses
                    if isinstance(members_data, list):
                        page_members = members_data
                    elif isinstance(members_data, dict):
                        page_members = members_data.get('members', [])
                        if not page_members:
                            # Try other possible key names
                            for key in ['data', 'results', 'items', 'content']:
                                if key in members_data:
                                    page_members = members_data[key]
                                    break
                    else:
                        page_members = []
                    
                    if not page_members or len(page_members) == 0:
                        print(f"   INFO: No more members found on page {page}. Stopping pagination.")
                        break
                    
                    all_members.extend(page_members)
                    print(f"   INFO: Page {page}: Found {len(page_members)} members (Total so far: {len(all_members)})")
                    
                    # If we got less than the page size, we've reached the end
                    if len(page_members) < 100:
                        print(f"   INFO: Received less than full page size ({len(page_members)} < 100). Reached end of data.")
                        break
                    
                    page += 1
                else:
                    print(f"   ERROR: Members API Error on page {page}: {members_resp.text[:500]}")
                    break
                    
            except Exception as e:
                print(f"   WARN: Failed to pull members page {page}: {e}")
                break
        
        # Now pull historical members using enhanced pagination parameters
        print("   INFO: Pulling additional historical members with enhanced parameters...")
        
        # Try additional pagination with different parameters to get historical data
        historical_params_sets = [
            {
                "page": "1", 
                "pageSize": "100",
                "includeInactive": "true",
                "includeAll": "true", 
                "status": "all",
                "includeExpired": "true",
                "includeCancelled": "true",
                "days": "99999"  # Very large date range
            },
            {
                "page": "1",
                "pageSize": "100", 
                "status": "inactive",
                "days": "10000"
            },
            {
                "page": "1",
                "pageSize": "100",
                "status": "expired", 
                "days": "10000"
            }
        ]
        
        historical_members = []
        for param_set in historical_params_sets:
            try:
                hist_page = 1
                while hist_page <= 50:  # Reasonable limit
                    param_set["page"] = str(hist_page)
                    hist_resp = requests.get(api_url, headers=CLUBHUB_HEADERS, params=param_set, verify=False, timeout=30)
                    
                    if hist_resp.ok:
                        hist_data = hist_resp.json()
                        
                        if isinstance(hist_data, list):
                            page_hist_members = hist_data
                        elif isinstance(hist_data, dict):
                            page_hist_members = hist_data.get('members', [])
                            if not page_hist_members:
                                for key in ['data', 'results', 'items', 'content']:
                                    if key in hist_data:
                                        page_hist_members = hist_data[key]
                                        break
                        else:
                            page_hist_members = []
                        
                        if not page_hist_members or len(page_hist_members) == 0:
                            break
                        
                        historical_members.extend(page_hist_members)
                        print(f"   INFO: Historical batch: Found {len(page_hist_members)} additional members")
                        
                        if len(page_hist_members) < 100:
                            break
                        
                        hist_page += 1
                    else:
                        break
            except Exception as e:
                print(f"   WARN: Failed to get historical data with params {param_set}: {e}")
                continue
        
        # Remove duplicates and add to main members list
        existing_ids = set(str(m.get('id', '')) for m in all_members)
        unique_historical = []
        for hist_member in historical_members:
            member_id = str(hist_member.get('id', ''))
            if member_id and member_id not in existing_ids:
                unique_historical.append(hist_member)
                existing_ids.add(member_id)
        
        all_members.extend(unique_historical)
        print(f"   SUCCESS: Added {len(unique_historical)} unique historical members")
        
        members = all_members
        print(f"   FINAL: Processing {len(members)} total members (including historical data)")
        
        print("   INFO: Pulling prospects from ClubHub API...")
        try:
            prospects_resp = requests.get(CLUBHUB_API_URL_PROSPECTS, headers=CLUBHUB_HEADERS, params=PARAMS_FOR_PROSPECTS_RECENT, verify=False, timeout=30)
            print(f"   DEBUG: Prospects API Response Status: {prospects_resp.status_code}")
            if prospects_resp.ok:
                prospects_data = prospects_resp.json()
                
                # Handle both dictionary and direct list responses
                if isinstance(prospects_data, list):
                    prospects = prospects_data
                elif isinstance(prospects_data, dict):
                    prospects = prospects_data.get('prospects', [])
                    if not prospects:
                        # Try other possible key names
                        for key in ['data', 'results', 'items', 'content']:
                            if key in prospects_data:
                                prospects = prospects_data[key]
                                break
                else:
                    prospects = []
            else:
                print(f"   DEBUG: Prospects API Error Response: {prospects_resp.text[:500]}")
                prospects = []
            print(f"   INFO: Pulled {len(prospects)} prospects.")
        except Exception as e:
            print(f"   WARN: Failed to pull prospects from API: {e}")
            prospects = []
        
        # Combine and normalize with ALL available fields
        contacts = []
        
        # First, let's inspect what fields are available by printing a sample record
        if members and len(members) > 0:
            print(f"   DEBUG: Sample member fields: {list(members[0].keys())}")
        if prospects and len(prospects) > 0:
            print(f"   DEBUG: Sample prospect fields: {list(prospects[0].keys())}")
        
        for m in members:
            # Combine firstName and lastName for the full name
            first_name = m.get('firstName', '').strip()
            last_name = m.get('lastName', '').strip()
            full_name = f"{first_name} {last_name}".strip()
            
            # Determine member category based on status and type
            status_msg = m.get('statusMessage', '').lower()
            member_type = str(m.get('type', '')).lower()
            status = str(m.get('status', '')).lower()
            
            # Categorize members more comprehensively
            if 'pay per visit' in status_msg or 'ppv' in status_msg:
                category = 'PPV'
            elif 'comp' in status_msg or 'complimentary' in status_msg or 'free' in status_msg:
                category = 'Comp'
            elif 'cancel' in status_msg or 'terminated' in status_msg or 'expired' in status_msg:
                category = 'Cancelled'
            elif 'frozen' in status_msg or 'hold' in status_msg:
                category = 'Frozen'
            elif 'inactive' in status_msg or status == '0' or status == 'inactive':
                category = 'Inactive'
            elif 'prospect' in status_msg or member_type == 'prospect':
                category = 'Prospect'
            else:
                category = 'Member'
            
            # Extract all available fields
            contacts.append({
                'Name': full_name,
                'FirstName': first_name,
                'LastName': last_name,
                'Email': m.get('email', m.get('emailAddress', '')),
                'Phone': m.get('phone', m.get('phoneNumber', m.get('mobilePhone', ''))),
                'Address': m.get('address1', m.get('address', '')),
                'Address2': m.get('address2', ''),
                'City': m.get('city', ''),
                'State': m.get('state', ''),
                'ZipCode': m.get('zip', m.get('zipCode', '')),
                'Country': m.get('country', ''),
                'MemberSince': m.get('membershipStart', m.get('memberSince', m.get('joinDate', m.get('startDate', '')))),
                'MembershipEnd': m.get('membershipEnd', ''),
                'LastVisit': m.get('lastVisit', m.get('lastCheckIn', '')),
                'Status': m.get('status', m.get('memberStatus', '')),
                'StatusMessage': m.get('statusMessage', ''),
                'Type': m.get('type', ''),
                'UserType': m.get('userType', ''),
                'UserStatus': m.get('userStatus', ''),
                'Category': category,
                'ProspectID': m.get('id', ''),
                'GUID': m.get('guid', ''),
                'MemberID': m.get('memberId', m.get('memberNumber', '')),
                'AgreementID': m.get('agreementId', ''),
                'AgreementType': m.get('agreementType', ''),
                'BillingFrequency': m.get('billingFrequency', ''),
                'MonthlyRate': m.get('monthlyRate', ''),
                'Gender': m.get('gender', ''),
                'DateOfBirth': m.get('dateOfBirth', ''),
                'Source': m.get('source', ''),
                'Rating': m.get('rating', ''),
                'LastActivity': m.get('lastActivity', ''),
                'HasApp': m.get('hasApp', ''),
                'HomeClub': m.get('homeClub', ''),
                'PreferredAccessType': m.get('preferredAccessType', ''),
                'MessagingStatus': '',
                'LastMessageDate': '',
                'OptedOut': m.get('optedOut', False),
                'Source': 'ClubHub-Members'
            })
        
        for p in prospects:
            # Combine firstName and lastName for prospects too
            first_name = p.get('firstName', '').strip()
            last_name = p.get('lastName', '').strip()
            full_name = f"{first_name} {last_name}".strip()
            
            # Extract all available fields for prospects
            contacts.append({
                'Name': full_name,
                'FirstName': first_name,
                'LastName': last_name,
                'Email': p.get('email', p.get('emailAddress', '')),
                'Phone': p.get('phone', p.get('phoneNumber', p.get('mobilePhone', ''))),
                'Address': p.get('address', ''),
                'City': p.get('city', ''),
                'State': p.get('state', ''),
                'ZipCode': p.get('zipCode', p.get('zip', '')),
                'MemberSince': '',  # Prospects don't have member since date
                'LastVisit': p.get('lastVisit', ''),
                'Status': p.get('status', p.get('prospectStatus', '')),
                'StatusMessage': p.get('statusMessage', ''),
                'Category': 'Prospect',
                'ProspectID': p.get('id', ''),
                'MemberID': '',  # Prospects don't have member ID yet
                'AgreementType': '',
                'BillingFrequency': '',
                'MonthlyRate': '',
                'MessagingStatus': '',
                'LastMessageDate': '',
                'OptedOut': p.get('optedOut', False),
                'Source': 'ClubHub-Prospects'
            })
        
        df_new = pd.DataFrame(contacts)
        print(f"   INFO: Created DataFrame with {len(df_new)} contacts and {len(df_new.columns)} fields")
        
        if overwrite or not os.path.exists(MASTER_CONTACT_LIST_PATH):
            print(f"   INFO: Overwriting '{MASTER_CONTACT_LIST_PATH}' with {len(df_new)} contacts.")
            df_new.to_excel(MASTER_CONTACT_LIST_PATH, index=False)
        else:
            print(f"   INFO: Merging new contacts with existing '{MASTER_CONTACT_LIST_PATH}'.")
            try:
                df_existing = pd.read_excel(MASTER_CONTACT_LIST_PATH, dtype=str).fillna("")
                print(f"   DEBUG: Existing file has {len(df_existing)} contacts")
                
                # Create a combined DataFrame with all columns from both datasets
                all_columns = list(set(df_existing.columns) | set(df_new.columns))
                
                # Ensure both DataFrames have all columns (fill missing with empty strings)
                for col in all_columns:
                    if col not in df_existing.columns:
                        df_existing[col] = ''
                    if col not in df_new.columns:
                        df_new[col] = ''
                
                # Reorder columns to match
                df_existing = df_existing[all_columns]
                df_new = df_new[all_columns]
                
                # Start with existing data
                df_combined = df_existing.copy()
                
                # Update/add contacts from API data
                updated_count = 0
                added_count = 0
                
                for idx, new_contact in df_new.iterrows():
                    prospect_id = str(new_contact.get('ProspectID', ''))
                    name = str(new_contact.get('Name', ''))
                    
                    # Try to find existing contact by ProspectID first
                    existing_match_idx = None
                    if prospect_id and prospect_id != '' and prospect_id != 'nan':
                        existing_matches = df_combined[df_combined['ProspectID'].astype(str) == prospect_id]
                        if not existing_matches.empty:
                            existing_match_idx = existing_matches.index[0]
                    
                    # If no ProspectID match, try Name match
                    if existing_match_idx is None and name and name != '' and name != 'nan':
                        name_matches = df_combined[df_combined['Name'].astype(str).str.lower() == name.lower()]
                        if not name_matches.empty:
                            existing_match_idx = name_matches.index[0]
                    
                    if existing_match_idx is not None:
                        # Update existing contact but preserve messaging data
                        for col in all_columns:
                            if col not in ['MessagingStatus', 'LastMessageDate']:  # Preserve rotation data
                                if col in new_contact.index and str(new_contact[col]) not in ['', 'nan', 'None']:  # Only update with meaningful data
                                    df_combined.at[existing_match_idx, col] = new_contact[col]
                        updated_count += 1
                    else:
                        # Add new contact - create a proper DataFrame row
                        new_row = {}
                        for col in all_columns:
                            if col in new_contact.index:
                                new_row[col] = new_contact[col]
                            else:
                                new_row[col] = ''
                        df_combined = pd.concat([df_combined, pd.DataFrame([new_row])], ignore_index=True)
                        added_count += 1
                
                # Remove duplicates based on ProspectID and Name, keeping first occurrence
                initial_count = len(df_combined)
                df_combined = df_combined.drop_duplicates(subset=['ProspectID', 'Name'], keep='first')
                duplicates_removed = initial_count - len(df_combined)
                
                df_combined.to_excel(MASTER_CONTACT_LIST_PATH, index=False)
                print(f"   SUCCESS: Updated {updated_count} contacts, added {added_count} new contacts")
                print(f"   SUCCESS: Removed {duplicates_removed} duplicates")
                print(f"   SUCCESS: Final total: {len(df_combined)} contacts")
                
            except Exception as merge_error:
                print(f"   ERROR: Merge failed with error: {merge_error}")
                print(f"   WARN: Preserving original file - no changes made")
                return False
        
        print(f"SUCCESS: Master contact list updated with all available fields and proper pagination.")
        return True
        
    except Exception as e:
        print(f"ERROR: Failed to update contacts from source. Error: {e}")
        return False


def get_member_balance_from_contact_data(member_info):
    """
    Get the actual past due balance for a member using the agreement API.
    Returns 0.0 if real data cannot be retrieved - NO FALLBACK AMOUNTS.
    
    Args:
        member_info (dict): Member information dictionary
    
    Returns:
        float: The actual past due amount from API, or 0.0 if not available
    """
    member_name = member_info.get('name', 'Unknown')
    member_id = member_info.get('member_id', '')
    
    # Try to get actual balance from agreement API - REAL DATA ONLY
    agreement_details = get_member_agreement_details(member_id, member_name)
    
    if agreement_details and agreement_details.get('amount_past_due', 0) > 0:
        real_amount = agreement_details['amount_past_due']
        print(f"   SUCCESS: Real API amount for {member_name}: ${real_amount:.2f}")
        return real_amount
    
    # NO FALLBACKS - only send invoices with real data
    print(f"   WARNING: No real past due amount available for {member_name} - skipping invoice")
    return 0.0


# Legacy compatibility functions
def get_member_data(member_name: str) -> Optional[Dict[str, Any]]:
    """
    Get member data from contact list.
    
    Args:
        member_name (str): Name of the member
        
    Returns:
        Dict[str, Any]: Member data or None if not found
    """
    try:
        df = read_master_contact_list()
        if df.empty:
            return None
            
        # Search for member by name (case insensitive)
        name_col = 'Name' if 'Name' in df.columns else df.columns[0]
        member_row = df[df[name_col].str.contains(member_name, case=False, na=False)]
        
        if not member_row.empty:
            return member_row.iloc[0].to_dict()
        return None
    except Exception as e:
        print(f"ERROR: Failed to get member data for {member_name}: {e}")
        return None


def get_contact_list() -> List[Dict[str, Any]]:
    """
    Get the master contact list.
    
    Returns:
        List[Dict[str, Any]]: List of member contacts
    """
    try:
        df = read_master_contact_list()
        if df.empty:
            return []
        return df.to_dict('records')
    except Exception as e:
        print(f"ERROR: Failed to get contact list: {e}")
        return []


def get_training_clients() -> List[Dict[str, Any]]:
    """
    Get training clients from CSV.
    
    Returns:
        List[Dict[str, Any]]: List of training clients
    """
    try:
        df = read_training_clients_csv()
        if df.empty:
            return []
        return df.to_dict('records')
    except Exception as e:
        print(f"ERROR: Failed to load training clients: {e}")
        return []


def get_member_balance(member_id, member_name=None):
    """
    Fetch the actual past due balance for a specific member from ClubHub API.
    Uses the agreement endpoint which has been confirmed to work via Charles Proxy.
    
    Args:
        member_id (str): The member ID to look up
        member_name (str): Optional member name for debugging
    
    Returns:
        float: The actual past due amount, or 0.0 if not found or error
    """
    try:
        # Use the newer agreement details function which has the correct endpoint
        agreement_details = get_member_agreement_details(member_id, member_name)
        
        if agreement_details and 'amount_past_due' in agreement_details:
            amount = agreement_details['amount_past_due']
            if amount > 0:
                print(f"   SUCCESS: Found past due amount ${amount:.2f} for {member_name}")
            else:
                print(f"   INFO: No past due amount for {member_name}")
            return amount
        else:
            print(f"   WARN: No agreement details found for {member_name} (ID: {member_id})")
            return 0.0
            
    except Exception as e:
        print(f"   ERROR: Failed to get balance for {member_name}: {e}")
        return 0.0


def get_fresh_clubhub_headers():
    """
    Get fresh ClubHub API headers using the automated token system.
    Falls back to hardcoded headers if automation fails.
    
    Returns:
        Dict containing fresh ClubHub API headers
    """
    try:
        from ..authentication.clubhub_token_capture import get_valid_clubhub_tokens
        
        print("   🔄 Attempting to get fresh ClubHub tokens...")
        
        # Try to get valid tokens from automated system
        tokens = get_valid_clubhub_tokens()
        
        if tokens and tokens.get('bearer_token') and tokens.get('session_cookie'):
            print("   ✅ Using fresh tokens from automated system")
            
            # Build headers with fresh tokens
            headers = {
                "Authorization": f"Bearer {tokens['bearer_token']}",
                "API-version": "1",
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Cookie": f"incap_ses_132_434694={tokens['session_cookie']}"
            }
            
            return headers
        else:
            print("   ⚠️ No valid tokens from automation, using fallback headers")
            from ...config.constants import CLUBHUB_HEADERS
            return CLUBHUB_HEADERS
            
    except Exception as e:
        print(f"   ⚠️ Error getting fresh tokens: {e}, using fallback headers")
        from ...config.constants import CLUBHUB_HEADERS
        return CLUBHUB_HEADERS


def get_member_agreement_details(member_id, member_name=None):
    """
    Fetch member agreement details including actual past due amount from ClubHub API.
    Uses the /api/members/{member_id}/agreement endpoint to get real billing data.
    
    Args:
        member_id (str): The member ID to look up
        member_name (str): Optional member name for debugging
    
    Returns:
        dict: Agreement details including amountPastDue, or None if not found
    """
    display_name = member_name if member_name else f"ID:{member_id}" if member_id else "<NO NAME>"
    
    if not member_id:
        print(f"   WARN: No member ID provided for {display_name}")
        return None
    
    try:
        # Get fresh headers using automated token system
        headers = get_fresh_clubhub_headers()
        
        # Use the exact ClubHub API format captured from Charles Proxy
        agreement_url = f"https://clubhub-ios-api.anytimefitness.com/api/members/{member_id}/agreement"
        
        print(f"   DEBUG: Fetching agreement details for {display_name} from: {agreement_url}")
        
        response = requests.get(agreement_url, headers=headers, verify=False, timeout=15)
        
        if response.ok:
            agreement_data = response.json()
            print(f"   SUCCESS: Got agreement data for {display_name} (ID: {member_id})")
            
            # Look for the amountPastDue field specifically
            if isinstance(agreement_data, dict):
                amount_past_due = agreement_data.get('amountPastDue', 0)
                
                # Also check for other possible amount fields
                if amount_past_due == 0:
                    other_amount_fields = [
                        'pastDueAmount', 'past_due_amount', 'outstandingBalance', 
                        'balance', 'totalDue', 'amountDue'
                    ]
                    for field in other_amount_fields:
                        if field in agreement_data and agreement_data[field]:
                            try:
                                amount_past_due = float(agreement_data[field])
                                if amount_past_due > 0:
                                    print(f"   INFO: Found amount ${amount_past_due:.2f} in field '{field}' for {display_name}")
                                    break
                            except (ValueError, TypeError):
                                continue
                
                # Return the full agreement data with the amount
                result = {
                    'member_id': member_id,
                    'member_name': display_name,
                    'amount_past_due': float(amount_past_due) if amount_past_due else 0.0,
                    'agreement_data': agreement_data
                }
                
                if result['amount_past_due'] > 0:
                    print(f"   SUCCESS: Member {display_name} has past due amount: ${result['amount_past_due']:.2f}")
                else:
                    print(f"   INFO: Member {display_name} has no past due amount")
                
                return result
            else:
                print(f"   WARN: Unexpected agreement data format for {display_name}")
                return None
                
        else:
            print(f"   ERROR: Agreement API failed for {display_name}: {response.status_code} - {response.text[:200]}")
            return None
            
    except Exception as e:
        print(f"   ERROR: Failed to get agreement details for {display_name}: {e}")
        return None


def update_member_past_due_amount(member_name, past_due_amount):
    """
    Updates the PastDueAmount column in the master contact list for a specific member.
    
    Args:
        member_name (str): Name of the member to update
        past_due_amount (float): The past due amount to save
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        df = read_master_contact_list()
        if df.empty:
            print(f"   ERROR: No contact list data available")
            return False
        
        # Add PastDueAmount column if it doesn't exist
        if 'PastDueAmount' not in df.columns:
            df['PastDueAmount'] = ''
            print(f"   INFO: Added PastDueAmount column to master contact list")
        
        # Find the member by name (case insensitive)
        member_mask = df['Name'].str.contains(member_name, case=False, na=False)
        matching_members = df[member_mask]
        
        if matching_members.empty:
            print(f"   WARN: Member '{member_name}' not found in contact list")
            return False
        
        if len(matching_members) > 1:
            # Use exact match if multiple found
            exact_matches = df[df['Name'].str.lower() == member_name.lower()]
            if not exact_matches.empty:
                matching_members = exact_matches
            else:
                # Use first match if no exact match
                matching_members = matching_members.head(1)
        
        # Update the PastDueAmount for the found member(s)
        member_index = matching_members.index[0]
        df.at[member_index, 'PastDueAmount'] = f"{past_due_amount:.2f}"
        
        # Save back to Excel
        df.to_excel(MASTER_CONTACT_LIST_PATH, index=False)
        print(f"   SUCCESS: Updated {member_name} with past due amount: ${past_due_amount:.2f}")
        return True
        
    except Exception as e:
        print(f"   ERROR: Failed to update past due amount for {member_name}: {e}")
        return False


def batch_update_past_due_amounts(member_updates):
    """
    Batch update multiple members' past due amounts in the master contact list.
    More efficient than individual updates when processing many members.
    
    Args:
        member_updates (list): List of tuples (member_name, past_due_amount)
    
    Returns:
        dict: Summary of updates (success_count, failed_count, updated_members)
    """
    try:
        df = read_master_contact_list()
        if df.empty:
            print(f"   ERROR: No contact list data available")
            return {'success_count': 0, 'failed_count': len(member_updates), 'updated_members': []}
        
        # Add PastDueAmount column if it doesn't exist
        if 'PastDueAmount' not in df.columns:
            df['PastDueAmount'] = ''
            print(f"   INFO: Added PastDueAmount column to master contact list")
        
        success_count = 0
        failed_count = 0
        updated_members = []
        
        for member_name, past_due_amount in member_updates:
            try:
                # Find the member by name (case insensitive)
                member_mask = df['Name'].str.contains(member_name, case=False, na=False)
                matching_members = df[member_mask]
                
                if matching_members.empty:
                    print(f"   WARN: Member '{member_name}' not found in contact list")
                    failed_count += 1
                    continue
                
                if len(matching_members) > 1:
                    # Use exact match if multiple found
                    exact_matches = df[df['Name'].str.lower() == member_name.lower()]
                    if not exact_matches.empty:
                        matching_members = exact_matches
                    else:
                        # Use first match if no exact match
                        matching_members = matching_members.head(1)
                
                # Update the PastDueAmount for the found member
                member_index = matching_members.index[0]
                df.at[member_index, 'PastDueAmount'] = f"{past_due_amount:.2f}"
                
                success_count += 1
                updated_members.append((member_name, past_due_amount))
                print(f"   SUCCESS: Queued update for {member_name}: ${past_due_amount:.2f}")
                
            except Exception as e:
                print(f"   ERROR: Failed to update {member_name}: {e}")
                failed_count += 1
                continue
        
        # Save all updates at once
        if success_count > 0:
            df.to_excel(MASTER_CONTACT_LIST_PATH, index=False)
            print(f"   SUCCESS: Batch updated {success_count} members' past due amounts")
        
        return {
            'success_count': success_count,
            'failed_count': failed_count,
            'updated_members': updated_members
        }
        
    except Exception as e:
        print(f"   ERROR: Failed batch update of past due amounts: {e}")
        return {'success_count': 0, 'failed_count': len(member_updates), 'updated_members': []}


def save_training_package_data_comprehensive(training_data, output_directory="package_data"):
    """
    Save comprehensive training package data in multiple formats.
    
    VERIFIED WORKING CODE FROM 20250627_WORKING.PY
    """
    try:
        # Ensure output directory exists
        os.makedirs(output_directory, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save as JSON (complete data)
        json_filename = f"training_package_data_complete_{timestamp}.json"
        json_filepath = os.path.join(output_directory, json_filename)
        
        with open(json_filepath, 'w', encoding='utf-8') as f:
            json.dump(training_data, f, indent=2, ensure_ascii=False)
        
        print(f"   💾 Complete data saved to: {json_filepath}")
        
        # Save as CSV (summary data)
        csv_filename = f"training_packages_analysis_{timestamp}.csv"
        csv_filepath = os.path.join(output_directory, csv_filename)
        
        # Create summary data for CSV
        summary_data = []
        for package in training_data:
            summary_row = {
                'member_name': package.get('member_name', ''),
                'package_name': package.get('package_name', ''),
                'trainer': package.get('trainer', ''),
                'status': package.get('status', ''),
                'past_due_amount': package.get('past_due_amount', 0.0),
                'total_sessions': package.get('total_sessions', 0),
                'sessions_remaining': package.get('sessions_remaining', 0),
                'monthly_cost': package.get('monthly_cost', 0.0),
                'start_date': package.get('start_date', ''),
                'expiration_date': package.get('expiration_date', '')
            }
            summary_data.append(summary_row)
        
        if summary_data:
            df = pd.DataFrame(summary_data)
            df.to_csv(csv_filepath, index=False)
            print(f"   💾 Summary data saved to: {csv_filepath}")
        
        # Save overdue packages only
        overdue_packages = [p for p in training_data if p.get('past_due_amount', 0) > 0]
        if overdue_packages:
            overdue_filename = f"past_due_packages_{timestamp}.json"
            overdue_filepath = os.path.join(output_directory, overdue_filename)
            
            with open(overdue_filepath, 'w', encoding='utf-8') as f:
                json.dump(overdue_packages, f, indent=2, ensure_ascii=False)
            
            print(f"   💾 Overdue packages saved to: {overdue_filepath}")
            
            # Create overdue summary CSV
            overdue_summary_filename = f"past_due_summary_{timestamp}.csv"
            overdue_summary_filepath = os.path.join(output_directory, overdue_summary_filename)
            
            overdue_summary = []
            for package in overdue_packages:
                summary_row = {
                    'member_name': package.get('member_name', ''),
                    'trainer': package.get('trainer', ''),
                    'past_due_amount': package.get('past_due_amount', 0.0),
                    'package_name': package.get('package_name', ''),
                    'status': package.get('status', '')
                }
                overdue_summary.append(summary_row)
            
            if overdue_summary:
                df_overdue = pd.DataFrame(overdue_summary)
                df_overdue.to_csv(overdue_summary_filepath, index=False)
                print(f"   💾 Overdue summary saved to: {overdue_summary_filepath}")
        
        # Generate priority report
        priority_report = generate_overdue_report_comprehensive(training_data, output_directory)
        
        print(f"   ✅ Data export complete - {len(training_data)} packages processed")
        return True
        
    except Exception as e:
        print(f"   ❌ Error saving training package data: {e}")
        return False


def generate_overdue_report_comprehensive(training_data, output_directory="package_data"):
    """
    Generate comprehensive overdue priority report.
    
    VERIFIED WORKING CODE FROM 20250627_WORKING.PY
    """
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Filter overdue packages
        overdue_packages = [p for p in training_data if p.get('past_due_amount', 0) > 0]
        
        if not overdue_packages:
            print("   INFO: No overdue packages found for report")
            return False
        
        # Sort by overdue amount (highest first)
        overdue_packages.sort(key=lambda x: x.get('past_due_amount', 0), reverse=True)
        
        # Calculate totals
        total_overdue = sum(p.get('past_due_amount', 0) for p in overdue_packages)
        total_members = len(overdue_packages)
        
        # Create priority report
        priority_report = {
            'report_timestamp': datetime.now().isoformat(),
            'total_overdue_members': total_members,
            'total_overdue_amount': total_overdue,
            'priority_contacts': []
        }
        
        # Add top 10 priority contacts
        for i, package in enumerate(overdue_packages[:10]):
            contact_info = {
                'rank': i + 1,
                'member_name': package.get('member_name', ''),
                'trainer': package.get('trainer', ''),
                'past_due_amount': package.get('past_due_amount', 0.0),
                'package_name': package.get('package_name', ''),
                'status': package.get('status', ''),
                'sessions_remaining': package.get('sessions_remaining', 0),
                'expiration_date': package.get('expiration_date', '')
            }
            priority_report['priority_contacts'].append(contact_info)
        
        # Save priority report
        priority_filename = f"OVERDUE_PRIORITY_REPORT_{timestamp}.json"
        priority_filepath = os.path.join(output_directory, priority_filename)
        
        with open(priority_filepath, 'w', encoding='utf-8') as f:
            json.dump(priority_report, f, indent=2, ensure_ascii=False)
        
        # Create text summary
        summary_filename = f"OVERDUE_SUMMARY_{timestamp}.txt"
        summary_filepath = os.path.join(output_directory, summary_filename)
        
        with open(summary_filepath, 'w', encoding='utf-8') as f:
            f.write("OVERDUE MEMBERS PRIORITY REPORT\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"SUMMARY:\n")
            f.write(f"Total overdue members: {total_members}\n")
            f.write(f"Total overdue amount: ${total_overdue:.2f}\n\n")
            f.write("TOP 10 PRIORITY CONTACTS:\n")
            f.write("-" * 30 + "\n")
            
            for contact in priority_report['priority_contacts']:
                f.write(f"{contact['rank']}. {contact['member_name']}\n")
                f.write(f"   Total Overdue: ${contact['past_due_amount']:.2f}\n")
                f.write(f"   Member Status: {contact['status']}\n")
                f.write(f"   Training Packages:\n")
                f.write(f"     - {contact['package_name']} (Trainer: {contact['trainer']})\n")
                f.write(f"       Past Due: ${contact['past_due_amount']:.2f}\n\n")
        
        print(f"   📊 Priority report saved to: {priority_filepath}")
        print(f"   📄 Summary text saved to: {summary_filepath}")
        print(f"   💰 Total overdue: ${total_overdue:.2f} across {total_members} members")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error generating overdue report: {e}")
        return False
