"""
Comprehensive test suite for ClubOS API endpoints - Training Package functionality.
Tests training package data retrieval for training clients and single club members.
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Any

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.services.api.enhanced_clubos_client import create_enhanced_clubos_client


class ClubOSTrainingPackageTests:
    """Test suite for ClubOS training package API endpoints"""
    
    def __init__(self):
        self.client = None
        self.test_results = {
            "test_suite": "ClubOS Training Package API",
            "start_time": datetime.now().isoformat(),
            "tests": [],
            "summary": {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "skipped": 0
            }
        }
        self.test_member_ids = [
            "66735385",  # Test member ID from captured endpoints
            "test_training_client_1",
            "test_club_member_1"
        ]
    
    def setup(self) -> bool:
        """Initialize ClubOS API client for testing"""
        print("🔧 Setting up ClubOS Training Package Tests...")
        
        try:
            self.client = create_enhanced_clubos_client()
            if self.client:
                print("✅ ClubOS API client initialized successfully")
                return True
            else:
                print("❌ Failed to initialize ClubOS API client")
                return False
        except Exception as e:
            print(f"❌ Setup error: {e}")
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all training package tests"""
        print("\n" + "="*60)
        print("🧪 RUNNING CLUBOS TRAINING PACKAGE API TESTS")
        print("="*60)
        
        if not self.setup():
            return self._finalize_results("Setup failed")
        
        # Training client tests
        self.test_get_training_packages_for_client()
        self.test_get_all_training_clients()
        
        # Single club member tests
        self.test_get_single_club_member_packages()
        self.test_get_member_details()
        
        # Data validation tests
        self.test_validate_training_package_data()
        
        # Error handling tests
        self.test_training_package_error_handling()
        
        # Performance tests
        self.test_training_package_performance()
        
        return self._finalize_results()
    
    def test_get_training_packages_for_client(self):
        """Test retrieving training packages for a specific training client"""
        test_name = "Get Training Packages for Client"
        print(f"\n🧪 Testing: {test_name}")
        
        try:
            test_member_id = self.test_member_ids[0]
            
            result = self.client.get_training_packages_for_client(test_member_id)
            
            success = result.get("success", False)
            packages = result.get("packages", [])
            
            self._record_test_result(
                test_name=test_name,
                success=success,
                details={
                    "member_id": test_member_id,
                    "packages_count": len(packages) if success else 0,
                    "packages": packages[:3] if success and len(packages) > 0 else [],  # First 3 for brevity
                    "result": result
                }
            )
            
            if success:
                print(f"   ✅ Retrieved {len(packages)} training packages for client {test_member_id}")
                if packages:
                    print(f"      Sample package: {packages[0]}")
                else:
                    print("      No training packages found for this client")
            else:
                print(f"   ❌ Failed to retrieve training packages: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            self._record_test_result(test_name, False, {"error": str(e)})
            print(f"   ❌ Test error: {e}")
    
    def test_get_all_training_clients(self):
        """Test retrieving all training clients"""
        test_name = "Get All Training Clients"
        print(f"\n🧪 Testing: {test_name}")
        
        try:
            clients = self.client.get_all_training_clients()
            
            success = isinstance(clients, list)
            
            self._record_test_result(
                test_name=test_name,
                success=success,
                details={
                    "clients_count": len(clients) if success else 0,
                    "clients": clients[:3] if success and len(clients) > 0 else [],  # First 3 for brevity
                    "data_structure": type(clients).__name__
                }
            )
            
            if success:
                print(f"   ✅ Retrieved {len(clients)} training clients")
                if clients:
                    print(f"      Sample client: {clients[0]}")
                else:
                    print("      No training clients found")
            else:
                print(f"   ❌ Failed to retrieve training clients")
                
        except Exception as e:
            self._record_test_result(test_name, False, {"error": str(e)})
            print(f"   ❌ Test error: {e}")
    
    def test_get_single_club_member_packages(self):
        """Test retrieving training packages for a single club member"""
        test_name = "Get Single Club Member Packages"
        print(f"\n🧪 Testing: {test_name}")
        
        try:
            test_member_id = self.test_member_ids[0]
            
            result = self.client.get_single_club_member_packages(test_member_id)
            
            success = result.get("success", False)
            training_packages = result.get("training_packages", [])
            member_details = result.get("member_details", {})
            
            self._record_test_result(
                test_name=test_name,
                success=success,
                details={
                    "member_id": test_member_id,
                    "member_type": result.get("member_type"),
                    "packages_count": len(training_packages) if success else 0,
                    "has_member_details": bool(member_details),
                    "training_packages": training_packages[:2] if training_packages else [],
                    "result": result
                }
            )
            
            if success:
                print(f"   ✅ Retrieved training package data for club member {test_member_id}")
                print(f"      Member type: {result.get('member_type', 'unknown')}")
                print(f"      Training packages: {len(training_packages)}")
                print(f"      Has member details: {bool(member_details)}")
            else:
                print(f"   ❌ Failed to retrieve club member packages: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            self._record_test_result(test_name, False, {"error": str(e)})
            print(f"   ❌ Test error: {e}")
    
    def test_get_member_details(self):
        """Test retrieving detailed member information"""
        test_name = "Get Member Details"
        print(f"\n🧪 Testing: {test_name}")
        
        try:
            test_member_id = self.test_member_ids[0]
            
            result = self.client.get_member_details(test_member_id)
            
            success = result.get("success", False)
            member_data = result.get("member", {})
            
            self._record_test_result(
                test_name=test_name,
                success=success,
                details={
                    "member_id": test_member_id,
                    "member_data_keys": list(member_data.keys()) if member_data else [],
                    "has_member_data": bool(member_data),
                    "result": result
                }
            )
            
            if success:
                print(f"   ✅ Retrieved member details for {test_member_id}")
                if member_data:
                    print(f"      Data fields: {list(member_data.keys())[:5]}...")  # Show first 5 fields
                else:
                    print("      No member data returned")
            else:
                print(f"   ❌ Failed to retrieve member details: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            self._record_test_result(test_name, False, {"error": str(e)})
            print(f"   ❌ Test error: {e}")
    
    def test_validate_training_package_data(self):
        """Test validation of training package data structure and content"""
        test_name = "Validate Training Package Data"
        print(f"\n🧪 Testing: {test_name}")
        
        try:
            test_member_id = self.test_member_ids[0]
            
            # Get training packages for validation
            result = self.client.get_training_packages_for_client(test_member_id)
            
            if not result.get("success"):
                self._record_test_result(test_name, False, {"error": "Could not retrieve packages for validation"})
                return
            
            packages = result.get("packages", [])
            validation_results = {
                "total_packages": len(packages),
                "valid_packages": 0,
                "validation_errors": [],
                "data_quality": {}
            }
            
            # Expected fields in a training package
            expected_fields = ["id", "name", "type", "status", "sessions_remaining", "total_sessions"]
            
            for i, package in enumerate(packages[:5]):  # Validate first 5 packages
                package_valid = True
                package_errors = []
                
                # Check if package is a dictionary
                if not isinstance(package, dict):
                    package_errors.append(f"Package {i} is not a dictionary: {type(package)}")
                    package_valid = False
                else:
                    # Check for required fields (flexible - some may not exist)
                    available_fields = list(package.keys())
                    validation_results["data_quality"][f"package_{i}_fields"] = available_fields
                    
                    # Basic data type validation
                    if "id" in package and not isinstance(package["id"], (str, int)):
                        package_errors.append(f"Package {i} has invalid ID type: {type(package['id'])}")
                        package_valid = False
                    
                    if "name" in package and not isinstance(package["name"], str):
                        package_errors.append(f"Package {i} has invalid name type: {type(package['name'])}")
                        package_valid = False
                
                if package_valid:
                    validation_results["valid_packages"] += 1
                else:
                    validation_results["validation_errors"].extend(package_errors)
            
            # Calculate validation success rate
            if validation_results["total_packages"] > 0:
                success_rate = validation_results["valid_packages"] / validation_results["total_packages"]
                success = success_rate >= 0.8  # 80% threshold
            else:
                success = True  # No packages to validate is considered success
            
            self._record_test_result(
                test_name=test_name,
                success=success,
                details=validation_results
            )
            
            if success:
                print(f"   ✅ Training package data validation passed")
                print(f"      Valid packages: {validation_results['valid_packages']}/{validation_results['total_packages']}")
            else:
                print(f"   ❌ Training package data validation failed")
                print(f"      Valid packages: {validation_results['valid_packages']}/{validation_results['total_packages']}")
                for error in validation_results['validation_errors'][:3]:  # Show first 3 errors
                    print(f"      Error: {error}")
                
        except Exception as e:
            self._record_test_result(test_name, False, {"error": str(e)})
            print(f"   ❌ Test error: {e}")
    
    def test_training_package_error_handling(self):
        """Test error handling with invalid inputs"""
        test_name = "Training Package Error Handling"
        print(f"\n🧪 Testing: {test_name}")
        
        error_tests = [
            {
                "description": "Invalid member ID",
                "member_id": "invalid_member_id_12345",
                "test_function": "get_training_packages_for_client"
            },
            {
                "description": "Empty member ID",
                "member_id": "",
                "test_function": "get_training_packages_for_client"
            },
            {
                "description": "None member ID",
                "member_id": None,
                "test_function": "get_member_details"
            },
            {
                "description": "Non-existent member ID",
                "member_id": "999999999",
                "test_function": "get_single_club_member_packages"
            }
        ]
        
        all_errors_handled = True
        error_results = []
        
        try:
            for error_test in error_tests:
                print(f"   🔍 Testing: {error_test['description']}")
                
                try:
                    # Call the appropriate function
                    if error_test["test_function"] == "get_training_packages_for_client":
                        result = self.client.get_training_packages_for_client(error_test["member_id"])
                    elif error_test["test_function"] == "get_member_details":
                        result = self.client.get_member_details(error_test["member_id"])
                    elif error_test["test_function"] == "get_single_club_member_packages":
                        result = self.client.get_single_club_member_packages(error_test["member_id"])
                    else:
                        result = {"success": False, "error": "Unknown test function"}
                    
                    # We expect these to fail gracefully or return empty results
                    if result.get("success") and result.get("packages", []):
                        # If we get success with actual data, it might be a problem
                        print(f"      ⚠️ Got unexpected success with data for: {error_test['description']}")
                        all_errors_handled = False
                    else:
                        print(f"      ✅ Error handled correctly: {result.get('error', 'No data returned')}")
                    
                    error_results.append({
                        "test": error_test["description"],
                        "function": error_test["test_function"],
                        "result": result
                    })
                    
                except Exception as e:
                    # Exceptions are also acceptable error handling
                    print(f"      ✅ Exception handled correctly: {str(e)}")
                    error_results.append({
                        "test": error_test["description"],
                        "function": error_test["test_function"],
                        "result": {"success": False, "error": str(e)}
                    })
            
            self._record_test_result(
                test_name=test_name,
                success=all_errors_handled,
                details={
                    "error_tests": error_results,
                    "all_errors_handled": all_errors_handled
                }
            )
            
        except Exception as e:
            self._record_test_result(test_name, False, {"error": str(e)})
            print(f"   ❌ Test error: {e}")
    
    def test_training_package_performance(self):
        """Test performance of training package API calls"""
        test_name = "Training Package Performance"
        print(f"\n🧪 Testing: {test_name}")
        
        try:
            performance_tests = [
                {
                    "name": "Single client packages",
                    "function": lambda: self.client.get_training_packages_for_client(self.test_member_ids[0])
                },
                {
                    "name": "All training clients",
                    "function": lambda: self.client.get_all_training_clients()
                },
                {
                    "name": "Club member packages",
                    "function": lambda: self.client.get_single_club_member_packages(self.test_member_ids[0])
                },
                {
                    "name": "Member details",
                    "function": lambda: self.client.get_member_details(self.test_member_ids[0])
                }
            ]
            
            performance_results = []
            
            for test in performance_tests:
                print(f"   ⏱️ Testing performance: {test['name']}")
                
                start_time = time.time()
                try:
                    result = test["function"]()
                    end_time = time.time()
                    
                    duration = end_time - start_time
                    success = result.get("success", isinstance(result, list))
                    
                    performance_results.append({
                        "test_name": test["name"],
                        "duration_seconds": duration,
                        "success": success,
                        "status": "completed"
                    })
                    
                    print(f"      Duration: {duration:.2f}s, Success: {success}")
                    
                except Exception as e:
                    end_time = time.time()
                    duration = end_time - start_time
                    
                    performance_results.append({
                        "test_name": test["name"],
                        "duration_seconds": duration,
                        "success": False,
                        "status": "error",
                        "error": str(e)
                    })
                    
                    print(f"      Duration: {duration:.2f}s, Error: {e}")
            
            # Calculate average performance
            successful_tests = [t for t in performance_results if t["success"]]
            if successful_tests:
                avg_duration = sum(t["duration_seconds"] for t in successful_tests) / len(successful_tests)
                max_duration = max(t["duration_seconds"] for t in successful_tests)
            else:
                avg_duration = 0
                max_duration = 0
            
            # Consider test successful if average response time is reasonable (< 10 seconds)
            success = avg_duration < 10 and len(successful_tests) > 0
            
            self._record_test_result(
                test_name=test_name,
                success=success,
                details={
                    "performance_tests": performance_results,
                    "average_duration": avg_duration,
                    "max_duration": max_duration,
                    "successful_tests": len(successful_tests),
                    "total_tests": len(performance_tests)
                }
            )
            
            if success:
                print(f"   ✅ Performance test passed")
                print(f"      Average duration: {avg_duration:.2f}s")
                print(f"      Successful tests: {len(successful_tests)}/{len(performance_tests)}")
            else:
                print(f"   ❌ Performance test failed")
                print(f"      Average duration: {avg_duration:.2f}s (should be < 10s)")
                
        except Exception as e:
            self._record_test_result(test_name, False, {"error": str(e)})
            print(f"   ❌ Test error: {e}")
    
    def _record_test_result(self, test_name: str, success: bool, details: Dict[str, Any] = None):
        """Record test result"""
        self.test_results["tests"].append({
            "name": test_name,
            "success": success,
            "timestamp": datetime.now().isoformat(),
            "details": details or {}
        })
        
        self.test_results["summary"]["total"] += 1
        if success:
            self.test_results["summary"]["passed"] += 1
        else:
            self.test_results["summary"]["failed"] += 1
    
    def _finalize_results(self, error_msg: str = None) -> Dict[str, Any]:
        """Finalize and return test results"""
        self.test_results["end_time"] = datetime.now().isoformat()
        
        if error_msg:
            self.test_results["setup_error"] = error_msg
        
        # Print summary
        print("\n" + "="*60)
        print("📊 TRAINING PACKAGE API TEST RESULTS")
        print("="*60)
        
        summary = self.test_results["summary"]
        print(f"Total Tests: {summary['total']}")
        print(f"Passed: {summary['passed']} ✅")
        print(f"Failed: {summary['failed']} ❌")
        
        if summary["total"] > 0:
            success_rate = (summary["passed"] / summary["total"]) * 100
            print(f"Success Rate: {success_rate:.1f}%")
        
        return self.test_results
    
    def save_results(self, filename: str = None):
        """Save test results to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"/tmp/clubos_training_package_test_results_{timestamp}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(self.test_results, f, indent=2)
            print(f"📁 Test results saved to: {filename}")
        except Exception as e:
            print(f"❌ Error saving results: {e}")


def run_training_package_tests():
    """Run all ClubOS training package API tests"""
    test_suite = ClubOSTrainingPackageTests()
    results = test_suite.run_all_tests()
    test_suite.save_results()
    return results


if __name__ == "__main__":
    run_training_package_tests()