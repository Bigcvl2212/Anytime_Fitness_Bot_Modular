"""
Enhanced Experimental Workflow - IMPROVED FROM EXPERIMENTAL CODE
Integrates ClubHub API, multi-channel notifications, and advanced data management.
Uses experimental patterns but enhanced with verified patterns and better error handling.
"""

import time
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from ...config.constants import DATA_DIR
from ...services.data.clubhub_api import EnhancedClubHubAPIService
from ...services.notifications.multi_channel_notifications import EnhancedMultiChannelNotifications
from ...services.data.advanced_data_management import EnhancedAdvancedDataManagement
from ...utils.debug_helpers import debug_page_state


class EnhancedExperimentalWorkflow:
    """
    Enhanced experimental workflow that integrates all experimental features.
    Based on experimental patterns but enhanced with verified patterns.
    """
    
    def __init__(self, driver=None, gemini_model=None):
        """Initialize enhanced experimental workflow"""
        self.driver = driver
        self.gemini_model = gemini_model
        self.clubhub_service = None
        self.notification_service = None
        self.data_service = None
        self._initialize_services()
    
    def _initialize_services(self):
        """Initialize all experimental services"""
        try:
            print("🚀 Initializing enhanced experimental workflow services...")
            
            # Initialize ClubHub API service
            self.clubhub_service = EnhancedClubHubAPIService()
            print("   ✅ ClubHub API service initialized")
            
            # Initialize multi-channel notification service
            self.notification_service = EnhancedMultiChannelNotifications(self.gemini_model)
            print("   ✅ Multi-channel notification service initialized")
            
            # Initialize advanced data management service
            self.data_service = EnhancedAdvancedDataManagement()
            print("   ✅ Advanced data management service initialized")
            
            print("✅ All experimental services initialized successfully")
            
        except Exception as e:
            print(f"❌ Error initializing experimental services: {e}")
    
    def run_comprehensive_data_collection(self, include_historical: bool = False) -> Dict[str, Any]:
        """
        Run comprehensive data collection from ClubHub API.
        
        IMPROVED FROM EXPERIMENTAL CODE
        """
        print("📊 Running comprehensive data collection...")
        
        try:
            # Fetch all data from ClubHub API
            api_data = self.clubhub_service.fetch_and_process_all_data(include_historical)
            
            if not api_data or api_data.get('total_records', 0) == 0:
                print("   ❌ No data collected from ClubHub API")
                return {"error": "No data collected"}
            
            print(f"   ✅ Collected {api_data['total_records']} total records")
            
            # Process and categorize the data
            processed_data = self._process_collected_data(api_data)
            
            # Export processed data
            export_results = self._export_collected_data(processed_data)
            
            # Generate data summary
            summary = self._generate_comprehensive_summary(processed_data)
            
            return {
                "api_data": api_data,
                "processed_data": processed_data,
                "export_results": export_results,
                "summary": summary,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"   ❌ Error in comprehensive data collection: {e}")
            return {"error": str(e)}
    
    def _process_collected_data(self, api_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process collected data with advanced data management"""
        print("🔄 Processing collected data...")
        
        try:
            processed_data = {}
            
            # Process members data
            if api_data.get('members'):
                members_df = self.data_service.load_and_validate_data_from_dict(api_data['members'])
                if not members_df.empty:
                    members_df = self.data_service.process_member_data(members_df)
                    members_df = self.data_service.categorize_members(members_df)
                    processed_data['members'] = members_df
                    print(f"   ✅ Processed {len(members_df)} member records")
            
            # Process prospects data
            if api_data.get('prospects'):
                prospects_df = self.data_service.load_and_validate_data_from_dict(api_data['prospects'])
                if not prospects_df.empty:
                    prospects_df = self.data_service.process_member_data(prospects_df)
                    prospects_df = self.data_service.categorize_members(prospects_df)
                    processed_data['prospects'] = prospects_df
                    print(f"   ✅ Processed {len(prospects_df)} prospect records")
            
            # Process historical data
            if api_data.get('historical'):
                historical_df = self.data_service.load_and_validate_data_from_dict(api_data['historical'])
                if not historical_df.empty:
                    historical_df = self.data_service.process_member_data(historical_df)
                    historical_df = self.data_service.categorize_members(historical_df)
                    processed_data['historical'] = historical_df
                    print(f"   ✅ Processed {len(historical_df)} historical records")
            
            return processed_data
            
        except Exception as e:
            print(f"   ❌ Error processing collected data: {e}")
            return {}
    
    def _export_collected_data(self, processed_data: Dict[str, Any]) -> Dict[str, bool]:
        """Export processed data to various formats"""
        print("💾 Exporting processed data...")
        
        export_results = {}
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Export members data
            if 'members' in processed_data and not processed_data['members'].empty:
                filename = f"processed_members_{timestamp}.csv"
                export_results['members_csv'] = self.data_service.export_processed_data(
                    processed_data['members'], filename, "csv"
                )
                
                filename = f"processed_members_{timestamp}.xlsx"
                export_results['members_excel'] = self.data_service.export_processed_data(
                    processed_data['members'], filename, "excel"
                )
            
            # Export prospects data
            if 'prospects' in processed_data and not processed_data['prospects'].empty:
                filename = f"processed_prospects_{timestamp}.csv"
                export_results['prospects_csv'] = self.data_service.export_processed_data(
                    processed_data['prospects'], filename, "csv"
                )
            
            # Export historical data
            if 'historical' in processed_data and not processed_data['historical'].empty:
                filename = f"processed_historical_{timestamp}.csv"
                export_results['historical_csv'] = self.data_service.export_processed_data(
                    processed_data['historical'], filename, "csv"
                )
            
            print(f"   ✅ Export results: {sum(export_results.values())} successful exports")
            return export_results
            
        except Exception as e:
            print(f"   ❌ Error exporting data: {e}")
            return {}
    
    def _generate_comprehensive_summary(self, processed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive data summary"""
        print("📊 Generating comprehensive summary...")
        
        try:
            summary = {
                "timestamp": datetime.now().isoformat(),
                "total_records": 0,
                "category_distribution": {},
                "contact_coverage": {},
                "data_quality": {}
            }
            
            # Aggregate data from all sources
            all_dataframes = []
            for source_name, df in processed_data.items():
                if not df.empty:
                    all_dataframes.append((df, source_name))
                    summary["total_records"] += len(df)
                    
                    # Generate source-specific summary
                    source_summary = self.data_service.generate_data_summary(df)
                    summary[f"{source_name}_summary"] = source_summary
            
            # Merge all data for overall analysis
            if all_dataframes:
                merged_df = self.data_service.merge_data_sources(all_dataframes)
                if not merged_df.empty:
                    # Overall category distribution
                    if 'category' in merged_df.columns:
                        summary["category_distribution"] = merged_df['category'].value_counts().to_dict()
                    
                    # Contact coverage analysis
                    summary["contact_coverage"] = {
                        "total": len(merged_df),
                        "with_email": len(merged_df[merged_df['email'].notna() & (merged_df['email'] != '')]),
                        "with_phone": len(merged_df[merged_df['phone'].notna() & (merged_df['phone'] != '')]),
                        "with_both": len(merged_df[
                            (merged_df['email'].notna() & (merged_df['email'] != '')) &
                            (merged_df['phone'].notna() & (merged_df['phone'] != ''))
                        ])
                    }
                    
                    # Data quality assessment
                    summary["data_quality"] = self.data_service.validate_data_quality(merged_df)
            
            print(f"   ✅ Summary generated for {summary['total_records']} total records")
            return summary
            
        except Exception as e:
            print(f"   ❌ Error generating summary: {e}")
            return {"error": str(e)}
    
    def run_multi_channel_notification_campaign(self, member_list: List[Dict[str, Any]], 
                                              notification_type: str) -> Dict[str, Any]:
        """
        Run multi-channel notification campaign.
        
        IMPROVED FROM EXPERIMENTAL CODE
        """
        print(f"📢 Running multi-channel notification campaign: {notification_type}")
        
        try:
            # Validate member list
            if not member_list:
                print("   ❌ No members to notify")
                return {"error": "No members to notify"}
            
            print(f"   📊 Targeting {len(member_list)} members")
            
            # Send bulk notifications
            results = self.notification_service.send_bulk_notifications(
                member_list, notification_type, self.driver
            )
            
            # Generate campaign report
            campaign_report = self._generate_campaign_report(results, notification_type)
            
            print(f"   ✅ Campaign complete:")
            print(f"      - SMS: {results['successful_sms']}")
            print(f"      - Email: {results['successful_email']}")
            print(f"      - ClubOS: {results['successful_clubos']}")
            print(f"      - Failed: {results['failed']}")
            
            return {
                "campaign_results": results,
                "campaign_report": campaign_report,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"   ❌ Error in notification campaign: {e}")
            return {"error": str(e)}
    
    def _generate_campaign_report(self, results: Dict[str, Any], notification_type: str) -> Dict[str, Any]:
        """Generate detailed campaign report"""
        try:
            total_members = results.get('total_members', 0)
            successful_total = (results.get('successful_sms', 0) + 
                              results.get('successful_email', 0) + 
                              results.get('successful_clubos', 0))
            
            success_rate = (successful_total / total_members * 100) if total_members > 0 else 0
            
            return {
                "campaign_type": notification_type,
                "total_members": total_members,
                "successful_notifications": successful_total,
                "failed_notifications": results.get('failed', 0),
                "success_rate": round(success_rate, 2),
                "channel_breakdown": {
                    "sms": results.get('successful_sms', 0),
                    "email": results.get('successful_email', 0),
                    "clubos": results.get('successful_clubos', 0)
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def run_targeted_notification_workflow(self, categories: List[str] = None,
                                         notification_type: str = "payment_reminder") -> Dict[str, Any]:
        """
        Run targeted notification workflow based on member categories.
        
        IMPROVED FROM EXPERIMENTAL CODE
        """
        print(f"🎯 Running targeted notification workflow: {notification_type}")
        
        try:
            # Collect data from ClubHub API
            api_data = self.clubhub_service.fetch_and_process_all_data()
            
            if not api_data or api_data.get('total_records', 0) == 0:
                print("   ❌ No data available for targeted notifications")
                return {"error": "No data available"}
            
            # Process and filter data
            processed_data = self._process_collected_data(api_data)
            
            # Merge all data sources
            all_dataframes = []
            for source_name, df in processed_data.items():
                if not df.empty:
                    all_dataframes.append((df, source_name))
            
            if not all_dataframes:
                print("   ❌ No processed data available")
                return {"error": "No processed data available"}
            
            # Merge data sources
            merged_df = self.data_service.merge_data_sources(all_dataframes)
            
            if merged_df.empty:
                print("   ❌ No data after merging")
                return {"error": "No data after merging"}
            
            # Filter by categories if specified
            if categories:
                merged_df = self.data_service.filter_members_by_criteria(
                    merged_df, categories=categories
                )
                print(f"   📊 Filtered to {len(merged_df)} members in categories: {categories}")
            
            # Filter for members with contact information
            merged_df = self.data_service.filter_members_by_criteria(
                merged_df, has_email=True, has_phone=True
            )
            print(f"   📊 {len(merged_df)} members with contact information")
            
            # Convert to list of dictionaries for notification service
            member_list = merged_df.to_dict('records')
            
            # Run notification campaign
            campaign_results = self.run_multi_channel_notification_campaign(
                member_list, notification_type
            )
            
            return {
                "data_collection": api_data,
                "processed_data": processed_data,
                "filtered_members": len(member_list),
                "campaign_results": campaign_results,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"   ❌ Error in targeted notification workflow: {e}")
            return {"error": str(e)}
    
    def run_comprehensive_experimental_workflow(self) -> Dict[str, Any]:
        """
        Run comprehensive experimental workflow combining all features.
        
        IMPROVED FROM EXPERIMENTAL CODE
        """
        print("🚀 Running comprehensive experimental workflow...")
        
        try:
            workflow_results = {
                "timestamp": datetime.now().isoformat(),
                "data_collection": {},
                "notification_campaigns": {},
                "data_analysis": {},
                "errors": []
            }
            
            # Step 1: Comprehensive data collection
            print("   📊 Step 1: Comprehensive data collection")
            data_collection_results = self.run_comprehensive_data_collection(include_historical=True)
            workflow_results["data_collection"] = data_collection_results
            
            if "error" in data_collection_results:
                workflow_results["errors"].append(f"Data collection error: {data_collection_results['error']}")
            
            # Step 2: Targeted notification campaigns
            print("   📢 Step 2: Targeted notification campaigns")
            
            # Payment reminder campaign for overdue members
            payment_campaign = self.run_targeted_notification_workflow(
                categories=["RedList", "YellowList"],
                notification_type="overdue_payment"
            )
            workflow_results["notification_campaigns"]["payment_reminder"] = payment_campaign
            
            # Training reminder campaign for active members
            training_campaign = self.run_targeted_notification_workflow(
                categories=["Member_Green"],
                notification_type="training_reminder"
            )
            workflow_results["notification_campaigns"]["training_reminder"] = training_campaign
            
            # Step 3: Data analysis and reporting
            print("   📊 Step 3: Data analysis and reporting")
            
            if "processed_data" in data_collection_results:
                processed_data = data_collection_results["processed_data"]
                
                # Generate comprehensive analysis
                analysis_results = self._generate_comprehensive_analysis(processed_data)
                workflow_results["data_analysis"] = analysis_results
            
            print("   ✅ Comprehensive experimental workflow complete")
            return workflow_results
            
        except Exception as e:
            print(f"   ❌ Error in comprehensive experimental workflow: {e}")
            return {"error": str(e)}
    
    def _generate_comprehensive_analysis(self, processed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive data analysis"""
        try:
            analysis = {
                "timestamp": datetime.now().isoformat(),
                "data_sources": list(processed_data.keys()),
                "total_records": sum(len(df) for df in processed_data.values() if hasattr(df, '__len__')),
                "quality_metrics": {},
                "trends": {},
                "recommendations": []
            }
            
            # Analyze each data source
            for source_name, df in processed_data.items():
                if hasattr(df, 'shape') and not df.empty:
                    # Data quality metrics
                    quality_metrics = self.data_service.validate_data_quality(df)
                    analysis["quality_metrics"][source_name] = quality_metrics
                    
                    # Category trends
                    if 'category' in df.columns:
                        category_dist = df['category'].value_counts()
                        analysis["trends"][f"{source_name}_categories"] = category_dist.to_dict()
                    
                    # Contact coverage trends
                    if 'email' in df.columns and 'phone' in df.columns:
                        email_coverage = len(df[df['email'].notna() & (df['email'] != '')])
                        phone_coverage = len(df[df['phone'].notna() & (df['phone'] != '')])
                        analysis["trends"][f"{source_name}_contact_coverage"] = {
                            "email": email_coverage,
                            "phone": phone_coverage,
                            "total": len(df)
                        }
            
            # Generate recommendations
            if analysis["quality_metrics"]:
                low_quality_sources = [
                    source for source, metrics in analysis["quality_metrics"].items()
                    if metrics.get("quality_score", 0) < 80
                ]
                if low_quality_sources:
                    analysis["recommendations"].append(f"Improve data quality for: {low_quality_sources}")
            
            return analysis
            
        except Exception as e:
            return {"error": str(e)}


# Convenience functions for backward compatibility
def run_comprehensive_data_collection(driver=None, gemini_model=None, include_historical=False) -> Dict[str, Any]:
    """Run comprehensive data collection"""
    workflow = EnhancedExperimentalWorkflow(driver, gemini_model)
    return workflow.run_comprehensive_data_collection(include_historical)


def run_multi_channel_notification_campaign(member_list: List[Dict[str, Any]], 
                                          notification_type: str, 
                                          driver=None, gemini_model=None) -> Dict[str, Any]:
    """Run multi-channel notification campaign"""
    workflow = EnhancedExperimentalWorkflow(driver, gemini_model)
    return workflow.run_multi_channel_notification_campaign(member_list, notification_type)


def run_targeted_notification_workflow(categories: List[str] = None,
                                     notification_type: str = "payment_reminder",
                                     driver=None, gemini_model=None) -> Dict[str, Any]:
    """Run targeted notification workflow"""
    workflow = EnhancedExperimentalWorkflow(driver, gemini_model)
    return workflow.run_targeted_notification_workflow(categories, notification_type)


def run_comprehensive_experimental_workflow(driver=None, gemini_model=None) -> Dict[str, Any]:
    """Run comprehensive experimental workflow"""
    workflow = EnhancedExperimentalWorkflow(driver, gemini_model)
    return workflow.run_comprehensive_experimental_workflow() 