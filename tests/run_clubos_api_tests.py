"""
Comprehensive test runner for all ClubOS API endpoints.
Executes messaging, calendar, and training package tests and generates consolidated reports.
"""

import json
import sys
import traceback
from datetime import datetime
from typing import Dict, List, Any

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import test suites
from test_clubos_messaging_api import run_messaging_tests
from test_clubos_calendar_api import run_calendar_tests  
from test_clubos_training_packages_api import run_training_package_tests


class ClubOSAPITestRunner:
    """Comprehensive test runner for all ClubOS API functionality"""
    
    def __init__(self):
        self.consolidated_results = {
            "test_run_info": {
                "start_time": datetime.now().isoformat(),
                "test_suites": ["messaging", "calendar", "training_packages"],
                "runner_version": "1.0.0"
            },
            "results": {},
            "summary": {
                "total_suites": 0,
                "successful_suites": 0,
                "failed_suites": 0,
                "total_tests": 0,
                "passed_tests": 0,
                "failed_tests": 0,
                "overall_success_rate": 0.0
            },
            "documented_endpoints": {},
            "issues_found": []
        }
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all ClubOS API test suites"""
        print("🚀 STARTING COMPREHENSIVE CLUBOS API TESTING")
        print("=" * 80)
        
        test_suites = [
            ("messaging", "ClubOS Messaging API", run_messaging_tests),
            ("calendar", "ClubOS Calendar API", run_calendar_tests),
            ("training_packages", "ClubOS Training Package API", run_training_package_tests)
        ]
        
        for suite_key, suite_name, test_function in test_suites:
            print(f"\n🧪 Running {suite_name} Tests...")
            
            try:
                suite_results = test_function()
                self.consolidated_results["results"][suite_key] = suite_results
                
                # Update summary statistics
                self.consolidated_results["summary"]["total_suites"] += 1
                
                suite_summary = suite_results.get("summary", {})
                suite_total = suite_summary.get("total", 0)
                suite_passed = suite_summary.get("passed", 0)
                suite_failed = suite_summary.get("failed", 0)
                
                self.consolidated_results["summary"]["total_tests"] += suite_total
                self.consolidated_results["summary"]["passed_tests"] += suite_passed
                self.consolidated_results["summary"]["failed_tests"] += suite_failed
                
                if suite_total > 0 and suite_failed == 0:
                    self.consolidated_results["summary"]["successful_suites"] += 1
                else:
                    self.consolidated_results["summary"]["failed_suites"] += 1
                
                print(f"✅ {suite_name} completed: {suite_passed}/{suite_total} tests passed")
                
            except Exception as e:
                print(f"❌ {suite_name} failed with error: {e}")
                print(f"   Traceback: {traceback.format_exc()}")
                
                self.consolidated_results["results"][suite_key] = {
                    "test_suite": suite_name,
                    "error": str(e),
                    "traceback": traceback.format_exc(),
                    "summary": {"total": 0, "passed": 0, "failed": 1}
                }
                
                self.consolidated_results["summary"]["total_suites"] += 1
                self.consolidated_results["summary"]["failed_suites"] += 1
                self.consolidated_results["summary"]["failed_tests"] += 1
        
        # Calculate overall success rate
        total_tests = self.consolidated_results["summary"]["total_tests"]
        if total_tests > 0:
            passed_tests = self.consolidated_results["summary"]["passed_tests"]
            self.consolidated_results["summary"]["overall_success_rate"] = (passed_tests / total_tests) * 100
        
        # Document endpoints and analyze results
        self._document_endpoints()
        self._analyze_issues()
        
        # Finalize results
        self.consolidated_results["test_run_info"]["end_time"] = datetime.now().isoformat()
        
        return self.consolidated_results
    
    def _document_endpoints(self):
        """Document the endpoints used and their success/failure status"""
        print("\n📋 Documenting API endpoints...")
        
        documented_endpoints = {
            "messaging": {
                "individual_text": {
                    "endpoint": "/action/Dashboard/sendText",
                    "method": "POST",
                    "status": "unknown",
                    "description": "Send individual text message to member"
                },
                "individual_email": {
                    "endpoint": "/action/Dashboard/sendEmail", 
                    "method": "POST",
                    "status": "unknown",
                    "description": "Send individual email message to member"
                },
                "group_messaging": {
                    "endpoint": "Multiple calls to individual endpoints",
                    "method": "POST",
                    "status": "unknown", 
                    "description": "Send messages to multiple members"
                }
            },
            "calendar": {
                "get_events": {
                    "endpoint": "/api/calendar/events",
                    "method": "GET",
                    "status": "unknown",
                    "description": "Retrieve calendar events/sessions"
                },
                "create_session": {
                    "endpoint": "/action/Calendar/createSession",
                    "method": "POST", 
                    "status": "unknown",
                    "description": "Create new calendar session"
                },
                "update_session": {
                    "endpoint": "/action/Calendar/updateSession",
                    "method": "POST",
                    "status": "unknown",
                    "description": "Update existing calendar session"
                },
                "delete_session": {
                    "endpoint": "/action/Calendar/deleteSession",
                    "method": "POST",
                    "status": "unknown",
                    "description": "Delete calendar session"
                }
            },
            "training_packages": {
                "client_packages": {
                    "endpoint": "/api/members/{member_id}/training/packages",
                    "method": "GET",
                    "status": "unknown",
                    "description": "Get training packages for specific client"
                },
                "all_clients": {
                    "endpoint": "/api/training/clients",
                    "method": "GET", 
                    "status": "unknown",
                    "description": "Get all training clients"
                },
                "member_details": {
                    "endpoint": "/api/members/{member_id}",
                    "method": "GET",
                    "status": "unknown",
                    "description": "Get detailed member information"
                }
            }
        }
        
        # Update endpoint status based on test results
        for suite_key, suite_results in self.consolidated_results["results"].items():
            if suite_key in documented_endpoints:
                suite_tests = suite_results.get("tests", [])
                
                for test in suite_tests:
                    test_name = test.get("name", "").lower()
                    test_success = test.get("success", False)
                    
                    # Map test names to endpoints
                    if suite_key == "messaging":
                        if "individual text" in test_name:
                            documented_endpoints["messaging"]["individual_text"]["status"] = "working" if test_success else "failed"
                        elif "individual email" in test_name:
                            documented_endpoints["messaging"]["individual_email"]["status"] = "working" if test_success else "failed"
                        elif "group" in test_name:
                            documented_endpoints["messaging"]["group_messaging"]["status"] = "working" if test_success else "failed"
                    
                    elif suite_key == "calendar":
                        if "get calendar sessions" in test_name:
                            documented_endpoints["calendar"]["get_events"]["status"] = "working" if test_success else "failed"
                        elif "create" in test_name:
                            documented_endpoints["calendar"]["create_session"]["status"] = "working" if test_success else "failed"
                        elif "update" in test_name:
                            documented_endpoints["calendar"]["update_session"]["status"] = "working" if test_success else "failed"
                        elif "delete" in test_name:
                            documented_endpoints["calendar"]["delete_session"]["status"] = "working" if test_success else "failed"
                    
                    elif suite_key == "training_packages":
                        if "training packages for client" in test_name:
                            documented_endpoints["training_packages"]["client_packages"]["status"] = "working" if test_success else "failed"
                        elif "all training clients" in test_name:
                            documented_endpoints["training_packages"]["all_clients"]["status"] = "working" if test_success else "failed"
                        elif "member details" in test_name:
                            documented_endpoints["training_packages"]["member_details"]["status"] = "working" if test_success else "failed"
        
        self.consolidated_results["documented_endpoints"] = documented_endpoints
    
    def _analyze_issues(self):
        """Analyze test results and identify common issues"""
        print("\n🔍 Analyzing issues...")
        
        issues = []
        
        for suite_key, suite_results in self.consolidated_results["results"].items():
            suite_tests = suite_results.get("tests", [])
            failed_tests = [test for test in suite_tests if not test.get("success", False)]
            
            if failed_tests:
                for test in failed_tests:
                    test_details = test.get("details", {})
                    error_msg = test_details.get("error", "Unknown error")
                    
                    issue = {
                        "suite": suite_key,
                        "test": test.get("name"),
                        "error": error_msg,
                        "timestamp": test.get("timestamp"),
                        "severity": self._classify_error_severity(error_msg)
                    }
                    
                    issues.append(issue)
        
        # Add general issues based on overall results
        total_tests = self.consolidated_results["summary"]["total_tests"]
        success_rate = self.consolidated_results["summary"]["overall_success_rate"]
        
        if success_rate < 50:
            issues.append({
                "suite": "overall",
                "test": "General API connectivity",
                "error": f"Low overall success rate: {success_rate:.1f}% - possible authentication or connectivity issues",
                "severity": "high"
            })
        elif success_rate < 80:
            issues.append({
                "suite": "overall", 
                "test": "API reliability",
                "error": f"Moderate success rate: {success_rate:.1f}% - some endpoints may need Selenium fallback",
                "severity": "medium"
            })
        
        self.consolidated_results["issues_found"] = issues
    
    def _classify_error_severity(self, error_msg: str) -> str:
        """Classify error severity based on error message"""
        error_lower = error_msg.lower()
        
        if any(term in error_lower for term in ["authentication", "login", "unauthorized", "forbidden"]):
            return "high"
        elif any(term in error_lower for term in ["timeout", "connection", "network"]):
            return "high"
        elif any(term in error_lower for term in ["not found", "404", "invalid"]):
            return "medium"
        elif any(term in error_lower for term in ["parse", "json", "format"]):
            return "medium"
        else:
            return "low"
    
    def print_summary_report(self):
        """Print a comprehensive summary report"""
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE CLUBOS API TEST REPORT")
        print("=" * 80)
        
        summary = self.consolidated_results["summary"]
        
        print(f"\n📈 OVERALL RESULTS:")
        print(f"   Test Suites: {summary['successful_suites']}/{summary['total_suites']} successful")
        print(f"   Individual Tests: {summary['passed_tests']}/{summary['total_tests']} passed")
        print(f"   Overall Success Rate: {summary['overall_success_rate']:.1f}%")
        
        print(f"\n🎯 ENDPOINT STATUS:")
        for category, endpoints in self.consolidated_results["documented_endpoints"].items():
            print(f"   {category.upper()}:")
            for endpoint_name, endpoint_info in endpoints.items():
                status = endpoint_info["status"]
                status_icon = "✅" if status == "working" else "❌" if status == "failed" else "⚪"
                print(f"      {status_icon} {endpoint_name}: {endpoint_info['endpoint']} ({status})")
        
        if self.consolidated_results["issues_found"]:
            print(f"\n⚠️ ISSUES FOUND ({len(self.consolidated_results['issues_found'])}):")
            for issue in self.consolidated_results["issues_found"][:5]:  # Show first 5 issues
                severity_icon = "🔴" if issue["severity"] == "high" else "🟡" if issue["severity"] == "medium" else "🟢"
                print(f"   {severity_icon} [{issue['suite']}] {issue['test']}: {issue['error']}")
            
            if len(self.consolidated_results["issues_found"]) > 5:
                print(f"   ... and {len(self.consolidated_results['issues_found']) - 5} more issues")
        else:
            print(f"\n✅ NO ISSUES FOUND - All tests passed!")
        
        print(f"\n📋 RECOMMENDATIONS:")
        success_rate = summary['overall_success_rate']
        
        if success_rate >= 90:
            print("   🎉 Excellent! ClubOS API endpoints are working well.")
            print("   💡 Consider moving from Selenium to API-first approach for these functions.")
        elif success_rate >= 70:
            print("   👍 Good results! Most endpoints are functional.")
            print("   💡 Implement hybrid approach: API-first with Selenium fallback for failed endpoints.")
            print("   🔧 Focus on fixing authentication or connectivity issues for failed tests.")
        elif success_rate >= 50:
            print("   ⚠️ Mixed results. API endpoints have moderate reliability.")
            print("   💡 Use API for working endpoints, keep Selenium for others.")
            print("   🔧 Investigate authentication, network, or endpoint URL issues.")
        else:
            print("   🚨 Poor results. API endpoints need significant work.")
            print("   💡 Continue using Selenium as primary method for now.")
            print("   🔧 Focus on basic authentication and connectivity before testing specific endpoints.")
        
        print(f"\n📁 DETAILED RESULTS: Check individual test files in /tmp/")
    
    def save_consolidated_report(self, filename: str = None):
        """Save consolidated test report to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"/tmp/clubos_api_comprehensive_test_report_{timestamp}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(self.consolidated_results, f, indent=2)
            print(f"\n💾 Comprehensive report saved to: {filename}")
            return filename
        except Exception as e:
            print(f"❌ Error saving consolidated report: {e}")
            return None


def main():
    """Main function to run all ClubOS API tests"""
    try:
        print("🔧 Initializing ClubOS API Test Runner...")
        
        runner = ClubOSAPITestRunner()
        results = runner.run_all_tests()
        
        # Print summary report
        runner.print_summary_report()
        
        # Save comprehensive report
        report_filename = runner.save_consolidated_report()
        
        # Determine exit code based on results
        success_rate = results["summary"]["overall_success_rate"]
        
        if success_rate >= 80:
            print(f"\n🎉 TEST RUN COMPLETED SUCCESSFULLY! ({success_rate:.1f}% success rate)")
            sys.exit(0)
        elif success_rate >= 50:
            print(f"\n⚠️ TEST RUN COMPLETED WITH WARNINGS! ({success_rate:.1f}% success rate)")
            sys.exit(1)
        else:
            print(f"\n🚨 TEST RUN FAILED! ({success_rate:.1f}% success rate)")
            sys.exit(2)
            
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR in test runner: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        sys.exit(3)


if __name__ == "__main__":
    main()