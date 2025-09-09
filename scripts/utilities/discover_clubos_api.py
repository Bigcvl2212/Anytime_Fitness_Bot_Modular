#!/usr/bin/env python3
"""
ClubOS API Endpoint Discovery Tool

This script systematically discovers and documents ClubOS API endpoints by:
1. Analyzing existing network traffic
2. Testing common API patterns
3. Mapping form submissions to API calls
4. Validating discovered endpoints

Usage:
    python discover_clubos_api.py --username <user> --password <pass>
"""

import argparse
import json
import time
import requests
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from pathlib import Path

from src.services.api.network_analyzer import NetworkAnalyzer, run_network_analysis
from src.services.api.clubos_api_client import create_clubos_api_client
from config.constants import (
    CLUBOS_LOGIN_URL, CLUBOS_DASHBOARD_URL, CLUBOS_MESSAGES_URL, 
    CLUBOS_CALENDAR_URL
)


class ClubOSAPIDiscovery:
    """Comprehensive ClubOS API endpoint discovery system"""
    
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.discovered_endpoints = {}
        self.tested_endpoints = {}
        self.api_client = None
        
        # Create output directory
        self.output_dir = Path("docs/api_discovery")
        self.output_dir.mkdir(exist_ok=True)
        
    def run_complete_discovery(self) -> Dict[str, Any]:
        """
        Run complete API discovery process
        
        Returns:
            Dict containing all discovered API information
        """
        print("🚀 Starting comprehensive ClubOS API discovery...")
        
        results = {
            "discovery_timestamp": datetime.now().isoformat(),
            "network_analysis": {},
            "endpoint_tests": {},
            "api_client_analysis": {},
            "recommendations": []
        }
        
        try:
            # Step 1: Network traffic analysis
            print("\n📡 Step 1: Network Traffic Analysis")
            results["network_analysis"] = self._run_network_analysis()
            
            # Step 2: API client analysis
            print("\n🔧 Step 2: API Client Analysis")
            results["api_client_analysis"] = self._analyze_api_client()
            
            # Step 3: Endpoint testing
            print("\n🧪 Step 3: Endpoint Testing")
            results["endpoint_tests"] = self._test_discovered_endpoints()
            
            # Step 4: Generate recommendations
            print("\n📝 Step 4: Generate Recommendations")
            results["recommendations"] = self._generate_recommendations(results)
            
            # Step 5: Save comprehensive report
            print("\n💾 Step 5: Save Discovery Report")
            self._save_discovery_report(results)
            
            print("\n✅ API discovery completed successfully!")
            return results
            
        except Exception as e:
            print(f"\n❌ Error during API discovery: {e}")
            return results
    
    def _run_network_analysis(self) -> Dict[str, Any]:
        """Run network traffic analysis to discover endpoints"""
        print("   🔍 Analyzing network traffic patterns...")
        
        try:
            # Define comprehensive URL list for analysis
            urls_to_analyze = [
                CLUBOS_DASHBOARD_URL,
                CLUBOS_MESSAGES_URL,
                CLUBOS_CALENDAR_URL,
                "https://anytime.club-os.com/action/Dashboard/PersonalTraining",
                "https://anytime.club-os.com/action/Members",
                "https://anytime.club-os.com/action/Members/search",
                "https://anytime.club-os.com/action/Reports",
                "https://anytime.club-os.com/action/Sales"
            ]
            
            # Run network analysis
            analysis_results = run_network_analysis(
                self.username, 
                self.password, 
                urls_to_analyze
            )
            
            if analysis_results:
                print(f"   ✅ Network analysis completed - found {len(analysis_results.get('endpoints', {}))} endpoint groups")
                
                # Extract discovered endpoints
                endpoints = analysis_results.get('endpoints', {})
                for endpoint_path, endpoint_data in endpoints.items():
                    self.discovered_endpoints[endpoint_path] = {
                        "source": "network_analysis",
                        "methods": endpoint_data.get("methods", []),
                        "call_count": endpoint_data.get("call_count", 0),
                        "sample_calls": endpoint_data.get("sample_calls", [])
                    }
                
                return analysis_results
            else:
                print("   ⚠️ Network analysis returned no results")
                return {}
                
        except Exception as e:
            print(f"   ❌ Error in network analysis: {e}")
            return {}
    
    def _analyze_api_client(self) -> Dict[str, Any]:
        """Analyze existing API client capabilities"""
        print("   🔧 Testing existing API client...")
        
        try:
            # Create API client
            self.api_client = create_clubos_api_client(self.username, self.password)
            
            if not self.api_client:
                print("   ❌ Failed to create API client")
                return {"status": "failed", "error": "Authentication failed"}
            
            print("   ✅ API client authenticated successfully")
            
            # Test endpoint discovery
            discovered_endpoints = self.api_client.discover_api_endpoints()
            
            analysis = {
                "status": "success",
                "authentication": "successful",
                "discovered_endpoints": discovered_endpoints,
                "available_methods": []
            }
            
            # Test available methods
            test_methods = [
                ("get_calendar_sessions", self._test_calendar_api),
                ("search_members", self._test_member_search_api),
                ("send_message", self._test_messaging_api)
            ]
            
            for method_name, test_func in test_methods:
                try:
                    result = test_func()
                    analysis["available_methods"].append({
                        "method": method_name,
                        "status": "success" if result else "failed",
                        "result": result
                    })
                except Exception as e:
                    analysis["available_methods"].append({
                        "method": method_name,
                        "status": "error",
                        "error": str(e)
                    })
            
            return analysis
            
        except Exception as e:
            print(f"   ❌ Error analyzing API client: {e}")
            return {"status": "error", "error": str(e)}
    
    def _test_calendar_api(self) -> bool:
        """Test calendar API functionality"""
        try:
            sessions = self.api_client.get_calendar_sessions()
            return len(sessions) >= 0  # Success if we get a list (even empty)
        except Exception:
            return False
    
    def _test_member_search_api(self) -> bool:
        """Test member search API functionality"""
        try:
            results = self.api_client.search_members("test")
            return len(results) >= 0  # Success if we get a list (even empty)
        except Exception:
            return False
    
    def _test_messaging_api(self) -> bool:
        """Test messaging API functionality (dry run)"""
        try:
            # Don't actually send a message, just test the method exists
            return hasattr(self.api_client, 'send_message')
        except Exception:
            return False
    
    def _test_discovered_endpoints(self) -> Dict[str, Any]:
        """Test discovered endpoints for functionality"""
        print("   🧪 Testing discovered endpoints...")
        
        test_results = {
            "tested_count": 0,
            "successful_count": 0,
            "failed_count": 0,
            "endpoint_results": {}
        }
        
        try:
            if not self.api_client:
                print("   ⚠️ No API client available for testing")
                return test_results
            
            # Test common ClubOS API patterns
            common_endpoints = [
                "/api/messages",
                "/api/members",
                "/api/calendar",
                "/api/training",
                "/ajax/messages",
                "/ajax/members/search",
                "/ajax/calendar/sessions"
            ]
            
            for endpoint in common_endpoints:
                test_results["tested_count"] += 1
                result = self._test_single_endpoint(endpoint)
                test_results["endpoint_results"][endpoint] = result
                
                if result["status"] == "success":
                    test_results["successful_count"] += 1
                else:
                    test_results["failed_count"] += 1
            
            print(f"   ✅ Tested {test_results['tested_count']} endpoints")
            print(f"   📊 Results: {test_results['successful_count']} successful, {test_results['failed_count']} failed")
            
            return test_results
            
        except Exception as e:
            print(f"   ❌ Error testing endpoints: {e}")
            return test_results
    
    def _test_single_endpoint(self, endpoint: str) -> Dict[str, Any]:
        """Test a single endpoint for availability and functionality"""
        result = {
            "endpoint": endpoint,
            "status": "unknown",
            "methods_tested": [],
            "response_data": None,
            "error": None
        }
        
        try:
            base_url = "https://anytime.club-os.com"
            full_url = f"{base_url}{endpoint}"
            
            # Get authentication headers from API client
            headers = self.api_client.auth.get_headers()
            
            # Test GET request
            try:
                response = requests.get(full_url, headers=headers, timeout=10)
                result["methods_tested"].append("GET")
                
                if response.status_code == 200:
                    result["status"] = "success"
                    try:
                        result["response_data"] = response.json()
                    except:
                        result["response_data"] = "Non-JSON response"
                elif response.status_code == 404:
                    result["status"] = "not_found"
                elif response.status_code in [401, 403]:
                    result["status"] = "auth_required"
                else:
                    result["status"] = "failed"
                    result["error"] = f"HTTP {response.status_code}"
                    
            except requests.exceptions.Timeout:
                result["status"] = "timeout"
                result["error"] = "Request timeout"
            except Exception as e:
                result["status"] = "error"
                result["error"] = str(e)
            
            return result
            
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
            return result
    
    def _generate_recommendations(self, discovery_results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on discovery results"""
        recommendations = []
        
        try:
            # Analysis-based recommendations
            network_analysis = discovery_results.get("network_analysis", {})
            if network_analysis.get("endpoints"):
                endpoint_count = len(network_analysis["endpoints"])
                recommendations.append(f"Implement {endpoint_count} discovered API endpoints for direct integration")
            
            # Authentication recommendations
            if discovery_results.get("api_client_analysis", {}).get("authentication") == "successful":
                recommendations.append("Use existing session-based authentication for API calls")
            else:
                recommendations.append("Implement robust authentication mechanism for API access")
            
            # Messaging recommendations
            messaging_endpoints = [ep for ep in self.discovered_endpoints.keys() if "message" in ep.lower()]
            if messaging_endpoints:
                recommendations.append(f"Replace Selenium messaging with {len(messaging_endpoints)} discovered messaging API endpoints")
            else:
                recommendations.append("Investigate ClubOS messaging API - may require form submission fallback")
            
            # Performance recommendations
            recommendations.append("Implement API caching and rate limiting for optimal performance")
            recommendations.append("Add comprehensive error handling and retry logic")
            
            # Testing recommendations
            successful_tests = discovery_results.get("endpoint_tests", {}).get("successful_count", 0)
            total_tests = discovery_results.get("endpoint_tests", {}).get("tested_count", 0)
            
            if total_tests > 0:
                success_rate = (successful_tests / total_tests) * 100
                recommendations.append(f"Current API success rate: {success_rate:.1f}% - focus on improving failed endpoints")
            
            # Migration strategy recommendations
            recommendations.append("Implement hybrid approach: API-first with Selenium fallback")
            recommendations.append("Create comprehensive test suite for API vs Selenium comparison")
            recommendations.append("Gradual migration: start with read-only operations, then write operations")
            
            return recommendations
            
        except Exception as e:
            print(f"   ⚠️ Error generating recommendations: {e}")
            return ["Error generating recommendations - review discovery results manually"]
    
    def _save_discovery_report(self, results: Dict[str, Any]) -> bool:
        """Save comprehensive discovery report"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Save main report
            main_report_file = self.output_dir / f"clubos_api_discovery_{timestamp}.json"
            with open(main_report_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            
            # Save endpoint summary
            endpoint_summary = {
                "discovery_date": results["discovery_timestamp"],
                "total_endpoints": len(self.discovered_endpoints),
                "endpoints": self.discovered_endpoints,
                "recommendations": results["recommendations"]
            }
            
            summary_file = self.output_dir / f"endpoint_summary_{timestamp}.json"
            with open(summary_file, 'w') as f:
                json.dump(endpoint_summary, f, indent=2, default=str)
            
            # Save human-readable report
            readable_file = self.output_dir / f"discovery_report_{timestamp}.md"
            with open(readable_file, 'w') as f:
                f.write(self._generate_readable_report(results))
            
            print(f"   ✅ Discovery report saved:")
            print(f"      📄 Main report: {main_report_file}")
            print(f"      📋 Summary: {summary_file}")
            print(f"      📖 Readable: {readable_file}")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Error saving discovery report: {e}")
            return False
    
    def _generate_readable_report(self, results: Dict[str, Any]) -> str:
        """Generate human-readable discovery report"""
        report = f"""# ClubOS API Discovery Report

**Discovery Date**: {results.get('discovery_timestamp', 'Unknown')}

## Summary

### Discovered Endpoints
Total endpoints discovered: {len(self.discovered_endpoints)}

"""
        
        # Add endpoint details
        if self.discovered_endpoints:
            report += "### Endpoint Details\n\n"
            for endpoint, data in self.discovered_endpoints.items():
                report += f"**{endpoint}**\n"
                report += f"- Source: {data.get('source', 'Unknown')}\n"
                report += f"- Methods: {', '.join(data.get('methods', []))}\n"
                report += f"- Call count: {data.get('call_count', 0)}\n\n"
        
        # Add test results
        endpoint_tests = results.get("endpoint_tests", {})
        if endpoint_tests:
            report += f"""### Test Results

- **Tested**: {endpoint_tests.get('tested_count', 0)} endpoints
- **Successful**: {endpoint_tests.get('successful_count', 0)}
- **Failed**: {endpoint_tests.get('failed_count', 0)}

"""
        
        # Add recommendations
        recommendations = results.get("recommendations", [])
        if recommendations:
            report += "### Recommendations\n\n"
            for i, rec in enumerate(recommendations, 1):
                report += f"{i}. {rec}\n"
        
        # Add technical details
        report += """
## Technical Details

### Authentication
- Session-based authentication with CSRF tokens
- Cookie management required
- Bearer tokens may be available for some endpoints

### Implementation Notes
- Use existing ClubOS API client as foundation
- Implement proper error handling and retry logic
- Add rate limiting to prevent API abuse
- Consider hybrid approach (API + Selenium fallback)

### Next Steps
1. Implement discovered endpoints in ClubOS API client
2. Create API-based versions of Selenium workflows
3. Test API functions against Selenium equivalents
4. Update main application to use API calls
5. Document migration process and limitations
"""
        
        return report


def main():
    """Main entry point for API discovery"""
    parser = argparse.ArgumentParser(description="Discover ClubOS API endpoints")
    parser.add_argument("--username", required=True, help="ClubOS username")
    parser.add_argument("--password", required=True, help="ClubOS password")
    parser.add_argument("--output", default="docs/api_discovery", help="Output directory")
    
    args = parser.parse_args()
    
    # Run discovery
    discovery = ClubOSAPIDiscovery(args.username, args.password)
    results = discovery.run_complete_discovery()
    
    # Print summary
    print(f"\n📊 Discovery Summary:")
    print(f"   🔍 Endpoints discovered: {len(discovery.discovered_endpoints)}")
    print(f"   🧪 Tests completed: {results.get('endpoint_tests', {}).get('tested_count', 0)}")
    print(f"   ✅ Successful tests: {results.get('endpoint_tests', {}).get('successful_count', 0)}")
    print(f"   📝 Recommendations: {len(results.get('recommendations', []))}")
    
    return 0 if results else 1


if __name__ == "__main__":
    exit(main())