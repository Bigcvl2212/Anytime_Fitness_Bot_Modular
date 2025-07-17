#!/usr/bin/env python3
training agreement data using discovered API endpoints and update master contact list
""

import requests
import json
import pandas as pd
from datetime import datetime
import time
import os
from typing import Dict, List, Optional
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TrainingAgreementFetcher:
    def __init__(self):
        self.base_url = "https://anytime.club-os.com"
        self.session = requests.Session()
        self.headers = self._get_auth_headers()
        
    def _get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers from the most recent successful request"""
        try:
            # Read the latest master contact list to get auth info
            master_files = [f for f in os.listdir('.) if f.startswith('master_contact_list_') and f.endswith('.csv)]            if not master_files:
                raise Exception(No master contact list found")
            
            latest_file = max(master_files)
            logger.info(f"Using auth info from {latest_file}")
            
            # For now, we'll use the headers from the HAR file analysis
            # In production, you'd want to get fresh tokens
            return[object Object]
                Authorization': Bearer eyJhbGciOiJIUzI1NiJ9eyJkZWxlZ2F0VVzZXJJZCI6MTg1zc3Mjc2LCJsb2dnZWRJblVzZXJJZCI6MTg3MDMyNzgyLCJzZXNzaW9SWQiOiJCMzQ2N0E0MTYyRjNGQjMxMjZGQTZDMkU0NTU4RkNCOSJ9sU4UawattyhlVuz17wlUsZ-pAldfmfBEm8kGw4U64A,
         Accept': application/json, text/plain, */*,
              User-Agent': 'Mozilla/5.0 (Windows NT10 Win64; x64) AppleWebKit/53736(KHTML, like Gecko) Chrome/138000,
               Referer': 'https://anytime.club-os.com/action/ClubServicesNew,
               X-Requested-With:XMLHttpRequest'
            }
        except Exception as e:
            logger.error(f"Error getting auth headers: {e}")
            return {}

    def get_all_package_agreements(self) -> List[Dict]:
        package agreements (training agreements)"
        url = f"{self.base_url}/api/agreements/package_agreements/list"
        try:
            logger.info("Fetching all package agreements...")
            response = self.session.get(url, headers=self.headers)
            response.raise_for_status()
            
            data = response.json()
            logger.info(fFound {len(data)} package agreements")
            return data
            
        except Exception as e:
            logger.error(f"Error fetching package agreements: {e}")
            return  def get_agreement_details(self, agreement_id: str) -> Optional[Dict]:
     tailed information for a specific agreement"
        url = f"{self.base_url}/api/agreements/package_agreements/V2ement_id}       params = {
         include: [oices', scheduledPayments, rohibitChangeTypes']
        }
        
        try:
            logger.info(f"Fetching details for agreement {agreement_id}...")
            response = self.session.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Successfully fetched details for agreement {agreement_id}")
            return data
            
        except Exception as e:
            logger.error(f"Error fetching agreement {agreement_id} details: {e}")
            return None

    def get_agreement_billing_status(self, agreement_id: str) -> Optional[Dict]:
    Get billing status for a specific agreement"
        url = f"{self.base_url}/api/agreements/package_agreements/{agreement_id}/billing_status"
        try:
            logger.info(f"Fetching billing status for agreement {agreement_id}...")
            response = self.session.get(url, headers=self.headers)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Successfully fetched billing status for agreement {agreement_id}")
            return data
            
        except Exception as e:
            logger.error(f"Error fetching billing status for agreement {agreement_id}: {e}")
            return None

    def get_agreement_total_value(self, agreement_id: str) -> Optional[Dict]:
        et total value for a specific agreement"
        url = f"{self.base_url}/api/agreements/package_agreements/agreementTotalValue       params = {'agreementId': agreement_id}
        
        try:
            logger.info(f"Fetching total value for agreement {agreement_id}...")
            response = self.session.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Successfully fetched total value for agreement {agreement_id}")
            return data
            
        except Exception as e:
            logger.error(f"Error fetching total value for agreement {agreement_id}: {e}")
            return None

    def extract_training_data(self, agreements: List[Dict]) -> List[Dict]:
    xtract and process training agreement data""     training_data = []
        
        for agreement in agreements:
            try:
                agreement_id = agreement.get('id)                if not agreement_id:
                    continue
                
                # Get detailed information
                details = self.get_agreement_details(agreement_id)
                billing_status = self.get_agreement_billing_status(agreement_id)
                total_value = self.get_agreement_total_value(agreement_id)
                
                # Extract key information
                training_record = {
                AgreementID': agreement_id,
             MemberID: agreement.get('memberId'),
               ProspectID:agreement.get('prospectId'),
                    AgreementType':Training Package',
           Status: agreement.get('status'),
              StartDate: agreement.get('startDate'),
            EndDate:agreement.get('endDate'),
               TotalValue: total_value.get('totalValue') if total_value else None,
                  BillingStatus': billing_status.get('status') if billing_status else None,
                  PastDueAmount: self._calculate_past_due(details),
                    LastPaymentDate': self._get_last_payment_date(details),
                    NextPaymentDate': self._get_next_payment_date(details),
                    Invoices': self._extract_invoices(details),
                    ScheduledPayments: self._extract_scheduled_payments(details),
                   RawAgreementData': json.dumps(agreement),
                   RawDetailsData': json.dumps(details) if details else None,
                   RawBillingData': json.dumps(billing_status) if billing_status else None,
              FetchedAt:datetime.now().isoformat()
                }
                
                training_data.append(training_record)
                logger.info(f"Processed agreement {agreement_id}")
                
                # Add delay to avoid rate limiting
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Error processing agreement {agreement.get(id, unknown')}: {e})          continue
        
        return training_data

    def _calculate_past_due(self, details: Optional[Dict]) -> float:
       Calculate past due amount from agreement details    if not details orinvoices not in details:
            return 0.0     
        past_due = 0.0
        for invoice in details.get('invoices', []):
            if invoice.get(status') == 'UNPAID:              past_due += float(invoice.get('amount', 0))
        
        return past_due

    def _get_last_payment_date(self, details: Optional[Dict]) -> Optional[str]:
  last payment date from agreement details    if not details orinvoices not in details:
            return None
        
        paid_invoices = [inv for inv in details.get(invoices', []) if inv.get(status') == PAID]        if paid_invoices:
            # Sort by date and get the most recent
            paid_invoices.sort(key=lambda x: x.get('paymentDate',), reverse=True)
            return paid_invoices[0].get('paymentDate')
        
        return None

    def _get_next_payment_date(self, details: Optional[Dict]) -> Optional[str]:
  next payment date from scheduled payments    if not details or scheduledPayments not in details:
            return None
        
        future_payments = [p for p in details.get(scheduledPayments', []) 
                          if p.get('dueDate') and p.get(status') != PAID
        if future_payments:
            # Sort by date and get the next one
            future_payments.sort(key=lambda x: x.get('dueDate', ''))
            return future_payments[0ueDate')
        
        return None

    def _extract_invoices(self, details: Optional[Dict]) -> List[Dict]:
        nvoice information    if not details orinvoices not in details:
            return []
        
        invoices = []
        for invoice in details.get('invoices', []):
            invoices.append({
          invoiceId: invoice.get('id'),
               amount': invoice.get('amount'),
               status': invoice.get('status'),
                dueDate': invoice.get('dueDate'),
            paymentDate': invoice.get('paymentDate)      })
        
        return invoices

    def _extract_scheduled_payments(self, details: Optional[Dict]) -> List[Dict]:
Extract scheduled payment information    if not details or scheduledPayments not in details:
            return []
        
        payments = []
        for payment in details.get(scheduledPayments', []):
            payments.append({
          paymentId: payment.get('id'),
               amount': payment.get('amount'),
               status': payment.get('status'),
                dueDate': payment.get('dueDate'),
            paymentDate': payment.get('paymentDate)      })
        
        return payments

    def update_master_contact_list(self, training_data: List[Dict]):
      ate master contact list with training agreement data"""
        try:
            # Find the latest master contact list
            master_files = [f for f in os.listdir('.) if f.startswith('master_contact_list_') and f.endswith('.csv)]            if not master_files:
                raise Exception(No master contact list found")
            
            latest_file = max(master_files)
            logger.info(f"Updating {latest_file} with training data...")
            
            # Read existing master contact list
            master_df = pd.read_csv(latest_file)
            logger.info(f"Loaded {len(master_df)} records from master contact list")
            
            # Convert training data to DataFrame
            training_df = pd.DataFrame(training_data)
            
            # Merge on ProspectID (which should match the training clients)
            if 'ProspectID' in master_df.columns and 'ProspectID' in training_df.columns:
                # Create a mapping of ProspectID to training data
                training_mapping = training_df.set_index('ProspectID').to_dict('index')
                
                # Add training columns to master contact list
                training_columns = [
                    TrainingAgreementID', TrainingAgreementType,TrainingStatus                   TrainingStartDate', TrainingEndDate', 'TrainingTotalValue',
                  TrainingBillingStatus', 'TrainingPastDueAmount', 'TrainingLastPaymentDate',
               TrainingNextPaymentDate',TrainingInvoices', TrainingScheduledPayments',
                TrainingRawAgreementData', 'TrainingRawDetailsData', 'TrainingRawBillingData',
                  TrainingDataFetchedAt'
                ]
                
                # Initialize new columns
                for col in training_columns:
                    master_df[col] = None
                
                # Update records with training data
                updated_count =0               for idx, row in master_df.iterrows():
                    prospect_id = row.get('ProspectID')
                    if prospect_id and prospect_id in training_mapping:
                        training_info = training_mapping[prospect_id]
                        
                        master_df.at[idx, TrainingAgreementID] = training_info.get('AgreementID')
                        master_df.at[idx, TrainingAgreementType] = training_info.get('AgreementType')
                        master_df.at[idx,TrainingStatus] = training_info.get('Status')
                        master_df.at[idx, TrainingStartDate] = training_info.get('StartDate')
                        master_df.at[idx, TrainingEndDate] = training_info.get('EndDate')
                        master_df.at[idx, 'TrainingTotalValue] = training_info.get('TotalValue')
                        master_df.at[idx, 'TrainingBillingStatus] = training_info.get('BillingStatus')
                        master_df.at[idx, 'TrainingPastDueAmount] = training_info.get('PastDueAmount')
                        master_df.at[idx, 'TrainingLastPaymentDate] = training_info.get('LastPaymentDate')
                        master_df.at[idx, 'TrainingNextPaymentDate] = training_info.get('NextPaymentDate')
                        master_df.at[idx,TrainingInvoices'] = json.dumps(training_info.get('Invoices', []))
                        master_df.at[idx, TrainingScheduledPayments'] = json.dumps(training_info.get(ScheduledPayments', []))
                        master_df.at[idx, 'TrainingRawAgreementData] = training_info.get('RawAgreementData')
                        master_df.at[idx, 'TrainingRawDetailsData] = training_info.get(RawDetailsData                   master_df.atidx, 'TrainingRawBillingData] = training_info.get(RawBillingData                   master_df.at[idx, 'TrainingDataFetchedAt] = training_info.get('FetchedAt')
                        
                        updated_count += 1
                
                logger.info(f"Updated {updated_count} records with training data")
                
                # Save updated master contact list
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S)               new_filename = f"master_contact_list_updated_with_training_{timestamp}.csv"
                master_df.to_csv(new_filename, index=False)
                logger.info(f"Saved updated master contact list as {new_filename}")
                
                # Also save as Excel
                excel_filename = f"master_contact_list_updated_with_training_{timestamp}.xlsx"
                master_df.to_excel(excel_filename, index=False)
                logger.info(f"Saved updated master contact list as {excel_filename}")
                
                return new_filename
            else:
                logger.error(ProspectID column not found in master contact list or training data)            return None
                
        except Exception as e:
            logger.error(f"Error updating master contact list: {e}")
            return None

def main():
   function to fetch training agreement data and update master contact list"
    logger.info(Startingtraining agreement data fetch...")
    
    fetcher = TrainingAgreementFetcher()
    
    # Get all package agreements
    agreements = fetcher.get_all_package_agreements()
    
    if not agreements:
        logger.error("No agreements found")
        return
    
    # Extract training data
    training_data = fetcher.extract_training_data(agreements)
    
    if not training_data:
        logger.error("No training data extracted")
        return
    
    logger.info(f"Extracted data for {len(training_data)} training agreements")
    
    # Update master contact list
    updated_file = fetcher.update_master_contact_list(training_data)
    
    if updated_file:
        logger.info(f"Successfully updated master contact list: {updated_file}")
        
        # Create summary report
        summary = {
           total_agreements_found': len(agreements),
            training_records_processed': len(training_data),
      past_due_agreements: len([t for t in training_data if t.get(PastDueAmount', 0) > 0         total_past_due_amount:sum(t.get(PastDueAmount', 0) for t in training_data),
         updated_file': updated_file,
      timestamp:datetime.now().isoformat()
        }
        
        # Save summary
        with open('training_data_fetch_summary.json', 'w') as f:
            json.dump(summary, f, indent=2)
        
        logger.info("Training data fetch completed successfully!")
        logger.info(fSummary: {summary}")
    else:
        logger.error("Failed to update master contact list)if __name__ == "__main__":
    main() 