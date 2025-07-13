"""
Enhanced Advanced Data Management - IMPROVED FROM EXPERIMENTAL CODE
Uses the experimental data processing patterns but enhanced with verified patterns.
"""

import json
import csv
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import os

from ...config.constants import DATA_DIR
from ...utils.debug_helpers import debug_page_state


class EnhancedAdvancedDataManagement:
    """
    Enhanced advanced data management service with improved processing and analysis.
    Based on experimental data processing patterns but enhanced with verified patterns.
    """
    
    def __init__(self, data_dir: str = DATA_DIR):
        """Initialize advanced data management service"""
        self.data_dir = data_dir
        self.ensure_data_directory()
    
    def ensure_data_directory(self):
        """Ensure data directory exists"""
        try:
            os.makedirs(self.data_dir, exist_ok=True)
            print(f"✅ Data directory ensured: {self.data_dir}")
        except Exception as e:
            print(f"❌ Error creating data directory: {e}")
    
    def load_and_validate_data(self, file_path: str, data_type: str = "csv") -> pd.DataFrame:
        """
        Load and validate data from file with enhanced error handling.
        
        IMPROVED FROM EXPERIMENTAL CODE
        """
        print(f"📊 Loading {data_type} data from {file_path}...")
        
        try:
            if data_type.lower() == "csv":
                df = pd.read_csv(file_path)
            elif data_type.lower() == "excel":
                df = pd.read_excel(file_path)
            elif data_type.lower() == "json":
                with open(file_path, 'r') as f:
                    data = json.load(f)
                df = pd.DataFrame(data)
            else:
                raise ValueError(f"Unsupported data type: {data_type}")
            
            print(f"   ✅ Loaded {len(df)} records from {file_path}")
            print(f"   📋 Columns: {list(df.columns)}")
            
            # Basic validation
            if df.empty:
                print("   ⚠️ Warning: Empty dataset loaded")
            else:
                print(f"   📊 Data shape: {df.shape}")
                print(f"   🔍 Sample data:")
                print(df.head(3).to_string())
            
            return df
            
        except FileNotFoundError:
            print(f"   ❌ Error: File not found: {file_path}")
            return pd.DataFrame()
        except Exception as e:
            print(f"   ❌ Error loading data: {e}")
            return pd.DataFrame()
    
    def process_member_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Process member data with enhanced cleaning and validation.
        
        IMPROVED FROM EXPERIMENTAL CODE
        """
        print("🔄 Processing member data...")
        
        if df.empty:
            print("   ❌ No data to process")
            return df
        
        try:
            # Create a copy to avoid modifying original
            processed_df = df.copy()
            
            # Standardize column names
            processed_df.columns = processed_df.columns.str.strip().str.lower()
            
            # Clean and standardize text fields
            text_columns = ['name', 'email', 'phone', 'category', 'statusmessage']
            for col in text_columns:
                if col in processed_df.columns:
                    processed_df[col] = processed_df[col].astype(str).str.strip()
                    processed_df[col] = processed_df[col].replace(['nan', 'None', ''], '')
            
            # Standardize phone numbers
            if 'phone' in processed_df.columns:
                processed_df['phone'] = processed_df['phone'].apply(self._standardize_phone)
            
            # Standardize email addresses
            if 'email' in processed_df.columns:
                processed_df['email'] = processed_df['email'].apply(self._standardize_email)
            
            # Clean prospect IDs
            if 'prospectid' in processed_df.columns:
                processed_df['prospectid'] = processed_df['prospectid'].astype(str).str.strip()
            
            # Add processing timestamp
            processed_df['processed_timestamp'] = datetime.now().isoformat()
            
            # Remove duplicates based on key fields
            key_columns = ['prospectid', 'email', 'phone']
            available_keys = [col for col in key_columns if col in processed_df.columns]
            
            if available_keys:
                initial_count = len(processed_df)
                processed_df = processed_df.drop_duplicates(subset=available_keys, keep='first')
                removed_count = initial_count - len(processed_df)
                if removed_count > 0:
                    print(f"   🧹 Removed {removed_count} duplicate records")
            
            print(f"   ✅ Processed {len(processed_df)} member records")
            return processed_df
            
        except Exception as e:
            print(f"   ❌ Error processing member data: {e}")
            return df
    
    def _standardize_phone(self, phone: str) -> str:
        """Standardize phone number format"""
        if pd.isna(phone) or phone == '':
            return ''
        
        # Remove all non-digit characters
        digits_only = ''.join(filter(str.isdigit, str(phone)))
        
        # Format as (XXX) XXX-XXXX
        if len(digits_only) == 10:
            return f"({digits_only[:3]}) {digits_only[3:6]}-{digits_only[6:]}"
        elif len(digits_only) == 11 and digits_only[0] == '1':
            return f"({digits_only[1:4]}) {digits_only[4:7]}-{digits_only[7:]}"
        else:
            return str(phone).strip()
    
    def _standardize_email(self, email: str) -> str:
        """Standardize email address format"""
        if pd.isna(email) or email == '':
            return ''
        
        email_str = str(email).strip().lower()
        
        # Basic email validation
        if '@' in email_str and '.' in email_str.split('@')[1]:
            return email_str
        else:
            return ''
    
    def categorize_members(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Categorize members based on status and type.
        
        IMPROVED FROM EXPERIMENTAL CODE
        """
        print("🏷️ Categorizing members...")
        
        if df.empty:
            print("   ❌ No data to categorize")
            return df
        
        try:
            categorized_df = df.copy()
            
            # Create category column if it doesn't exist
            if 'category' not in categorized_df.columns:
                categorized_df['category'] = 'Unknown'
            
            # Categorize based on status message
            if 'statusmessage' in categorized_df.columns:
                status_lower = categorized_df['statusmessage'].str.lower()
                
                # Apply categorization rules
                categorized_df.loc[status_lower.str.contains('pay per visit', na=False), 'category'] = 'PPV'
                categorized_df.loc[status_lower.str.contains('comp member', na=False), 'category'] = 'CompMember'
                categorized_df.loc[status_lower.str.contains('past due more then 30 days', na=False), 'category'] = 'RedList'
                categorized_df.loc[status_lower.str.contains('past due 6-30 days', na=False), 'category'] = 'YellowList'
                categorized_df.loc[status_lower.str.contains('pending cancel', na=False), 'category'] = 'PendingCancel'
                categorized_df.loc[status_lower.str.contains('good standing', na=False), 'category'] = 'Member_Green'
                categorized_df.loc[status_lower.str.contains('prospect', na=False), 'category'] = 'Prospect'
            
            # Count categories
            category_counts = categorized_df['category'].value_counts()
            print("   📊 Category distribution:")
            for category, count in category_counts.items():
                print(f"      - {category}: {count}")
            
            return categorized_df
            
        except Exception as e:
            print(f"   ❌ Error categorizing members: {e}")
            return df
    
    def filter_members_by_criteria(self, df: pd.DataFrame, 
                                 categories: List[str] = None,
                                 has_email: bool = None,
                                 has_phone: bool = None,
                                 status_keywords: List[str] = None) -> pd.DataFrame:
        """
        Filter members based on multiple criteria.
        
        IMPROVED FROM EXPERIMENTAL CODE
        """
        print("🔍 Filtering members by criteria...")
        
        if df.empty:
            print("   ❌ No data to filter")
            return df
        
        try:
            filtered_df = df.copy()
            initial_count = len(filtered_df)
            
            # Filter by categories
            if categories:
                filtered_df = filtered_df[filtered_df['category'].isin(categories)]
                print(f"   📊 Filtered by categories {categories}: {len(filtered_df)} records")
            
            # Filter by email availability
            if has_email is not None:
                if has_email:
                    filtered_df = filtered_df[filtered_df['email'].notna() & (filtered_df['email'] != '')]
                else:
                    filtered_df = filtered_df[filtered_df['email'].isna() | (filtered_df['email'] == '')]
                print(f"   📧 Filtered by email availability ({has_email}): {len(filtered_df)} records")
            
            # Filter by phone availability
            if has_phone is not None:
                if has_phone:
                    filtered_df = filtered_df[filtered_df['phone'].notna() & (filtered_df['phone'] != '')]
                else:
                    filtered_df = filtered_df[filtered_df['phone'].isna() | (filtered_df['phone'] == '')]
                print(f"   📱 Filtered by phone availability ({has_phone}): {len(filtered_df)} records")
            
            # Filter by status keywords
            if status_keywords and 'statusmessage' in filtered_df.columns:
                keyword_mask = filtered_df['statusmessage'].str.lower().str.contains('|'.join(status_keywords), na=False)
                filtered_df = filtered_df[keyword_mask]
                print(f"   🔍 Filtered by status keywords {status_keywords}: {len(filtered_df)} records")
            
            final_count = len(filtered_df)
            removed_count = initial_count - final_count
            print(f"   ✅ Filtering complete: {removed_count} records removed, {final_count} remaining")
            
            return filtered_df
            
        except Exception as e:
            print(f"   ❌ Error filtering members: {e}")
            return df
    
    def export_processed_data(self, df: pd.DataFrame, filename: str, 
                            export_format: str = "csv") -> bool:
        """
        Export processed data to file with enhanced formatting.
        
        IMPROVED FROM EXPERIMENTAL CODE
        """
        print(f"💾 Exporting data to {filename}...")
        
        if df.empty:
            print("   ❌ No data to export")
            return False
        
        try:
            # Create timestamped filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_name = os.path.splitext(filename)[0]
            extension = os.path.splitext(filename)[1] or f".{export_format}"
            
            timestamped_filename = f"{base_name}_{timestamp}{extension}"
            file_path = os.path.join(self.data_dir, timestamped_filename)
            
            # Export based on format
            if export_format.lower() == "csv":
                df.to_csv(file_path, index=False)
            elif export_format.lower() == "excel":
                df.to_excel(file_path, index=False)
            elif export_format.lower() == "json":
                df.to_json(file_path, orient='records', indent=2)
            else:
                raise ValueError(f"Unsupported export format: {export_format}")
            
            print(f"   ✅ Exported {len(df)} records to {file_path}")
            print(f"   📊 File size: {os.path.getsize(file_path)} bytes")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Error exporting data: {e}")
            return False
    
    def generate_data_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate comprehensive data summary with statistics.
        
        IMPROVED FROM EXPERIMENTAL CODE
        """
        print("📊 Generating data summary...")
        
        if df.empty:
            return {"error": "No data to summarize"}
        
        try:
            summary = {
                "total_records": len(df),
                "timestamp": datetime.now().isoformat(),
                "columns": list(df.columns),
                "data_types": df.dtypes.to_dict(),
                "missing_values": df.isnull().sum().to_dict(),
                "duplicates": df.duplicated().sum()
            }
            
            # Category distribution
            if 'category' in df.columns:
                summary["category_distribution"] = df['category'].value_counts().to_dict()
            
            # Contact information statistics
            if 'email' in df.columns:
                summary["email_coverage"] = {
                    "total": len(df),
                    "with_email": len(df[df['email'].notna() & (df['email'] != '')]),
                    "without_email": len(df[df['email'].isna() | (df['email'] == '')])
                }
            
            if 'phone' in df.columns:
                summary["phone_coverage"] = {
                    "total": len(df),
                    "with_phone": len(df[df['phone'].notna() & (df['phone'] != '')]),
                    "without_phone": len(df[df['phone'].isna() | (df['phone'] == '')])
                }
            
            # Status message analysis
            if 'statusmessage' in df.columns:
                status_counts = df['statusmessage'].value_counts().head(10).to_dict()
                summary["top_status_messages"] = status_counts
            
            print(f"   ✅ Summary generated for {summary['total_records']} records")
            return summary
            
        except Exception as e:
            print(f"   ❌ Error generating summary: {e}")
            return {"error": str(e)}
    
    def merge_data_sources(self, dataframes: List[Tuple[pd.DataFrame, str]], 
                          merge_strategy: str = "outer") -> pd.DataFrame:
        """
        Merge multiple data sources with enhanced conflict resolution.
        
        IMPROVED FROM EXPERIMENTAL CODE
        """
        print(f"🔄 Merging {len(dataframes)} data sources...")
        
        if not dataframes:
            print("   ❌ No data sources to merge")
            return pd.DataFrame()
        
        try:
            # Start with the first dataframe
            merged_df = dataframes[0][0].copy()
            source_name = dataframes[0][1]
            print(f"   📊 Starting with {source_name}: {len(merged_df)} records")
            
            # Merge additional dataframes
            for df, source_name in dataframes[1:]:
                print(f"   📊 Merging {source_name}: {len(df)} records")
                
                # Standardize column names for merging
                df_copy = df.copy()
                df_copy.columns = df_copy.columns.str.strip().str.lower()
                
                # Find common columns for merging
                common_columns = set(merged_df.columns) & set(df_copy.columns)
                print(f"      Common columns: {list(common_columns)}")
                
                if common_columns:
                    # Use the first common column as merge key
                    merge_key = list(common_columns)[0]
                    print(f"      Merging on: {merge_key}")
                    
                    # Perform merge
                    if merge_strategy == "outer":
                        merged_df = pd.merge(merged_df, df_copy, on=merge_key, how='outer', suffixes=('', f'_{source_name}'))
                    elif merge_strategy == "inner":
                        merged_df = pd.merge(merged_df, df_copy, on=merge_key, how='inner', suffixes=('', f'_{source_name}'))
                    elif merge_strategy == "left":
                        merged_df = pd.merge(merged_df, df_copy, on=merge_key, how='left', suffixes=('', f'_{source_name}'))
                    else:
                        merged_df = pd.merge(merged_df, df_copy, on=merge_key, how='right', suffixes=('', f'_{source_name}'))
                    
                    print(f"      ✅ Merged: {len(merged_df)} records")
                else:
                    print(f"      ⚠️ No common columns found, appending")
                    merged_df = pd.concat([merged_df, df_copy], ignore_index=True)
            
            # Remove duplicate columns
            duplicate_columns = merged_df.columns[merged_df.columns.duplicated()]
            if len(duplicate_columns) > 0:
                print(f"   🧹 Removing {len(duplicate_columns)} duplicate columns")
                merged_df = merged_df.loc[:, ~merged_df.columns.duplicated()]
            
            print(f"   ✅ Merge complete: {len(merged_df)} total records")
            return merged_df
            
        except Exception as e:
            print(f"   ❌ Error merging data sources: {e}")
            return pd.DataFrame()
    
    def validate_data_quality(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Validate data quality with comprehensive checks.
        
        IMPROVED FROM EXPERIMENTAL CODE
        """
        print("🔍 Validating data quality...")
        
        if df.empty:
            return {"error": "No data to validate"}
        
        try:
            quality_report = {
                "total_records": len(df),
                "timestamp": datetime.now().isoformat(),
                "quality_score": 0,
                "issues": [],
                "recommendations": []
            }
            
            # Check for missing values
            missing_data = df.isnull().sum()
            high_missing_columns = missing_data[missing_data > len(df) * 0.1]
            if not high_missing_columns.empty:
                quality_report["issues"].append(f"High missing values in columns: {list(high_missing_columns.index)}")
            
            # Check for duplicates
            duplicate_count = df.duplicated().sum()
            if duplicate_count > 0:
                quality_report["issues"].append(f"Found {duplicate_count} duplicate records")
            
            # Check data types
            for column, dtype in df.dtypes.items():
                if dtype == 'object':
                    # Check for mixed data types in object columns
                    unique_types = df[column].apply(type).nunique()
                    if unique_types > 1:
                        quality_report["issues"].append(f"Mixed data types in column '{column}'")
            
            # Check for empty strings in text fields
            text_columns = ['name', 'email', 'phone']
            for col in text_columns:
                if col in df.columns:
                    empty_count = (df[col] == '').sum()
                    if empty_count > len(df) * 0.5:
                        quality_report["issues"].append(f"High empty values in '{col}' column")
            
            # Calculate quality score
            total_checks = 4  # missing, duplicates, types, empty
            passed_checks = total_checks - len(quality_report["issues"])
            quality_report["quality_score"] = (passed_checks / total_checks) * 100
            
            # Generate recommendations
            if quality_report["quality_score"] < 80:
                quality_report["recommendations"].append("Consider data cleaning and validation")
            if duplicate_count > 0:
                quality_report["recommendations"].append("Remove duplicate records")
            if not high_missing_columns.empty:
                quality_report["recommendations"].append("Address missing data in key columns")
            
            print(f"   ✅ Quality validation complete: {quality_report['quality_score']:.1f}% score")
            return quality_report
            
        except Exception as e:
            print(f"   ❌ Error validating data quality: {e}")
            return {"error": str(e)}


# Convenience functions for backward compatibility
def load_and_validate_data(file_path: str, data_type: str = "csv") -> pd.DataFrame:
    """Load and validate data from file"""
    service = EnhancedAdvancedDataManagement()
    return service.load_and_validate_data(file_path, data_type)


def process_member_data(df: pd.DataFrame) -> pd.DataFrame:
    """Process member data"""
    service = EnhancedAdvancedDataManagement()
    return service.process_member_data(df)


def export_processed_data(df: pd.DataFrame, filename: str, export_format: str = "csv") -> bool:
    """Export processed data to file"""
    service = EnhancedAdvancedDataManagement()
    return service.export_processed_data(df, filename, export_format)


def generate_data_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """Generate data summary"""
    service = EnhancedAdvancedDataManagement()
    return service.generate_data_summary(df) 