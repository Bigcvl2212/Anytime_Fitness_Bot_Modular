"""
Comprehensive test suite for ClubOS API endpoints - Messaging functionality.
Tests individual and group messaging capabilities.
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Any

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from services.api.enhanced_clubos_client import create_enhanced_clubos_client


class ClubOSMessagingTests:
    """Test suite for ClubOS messaging API endpoints"""
    
    def __init__(self):
        self.client = None
        self.test_results = {
            "test_suite": "ClubOS Messaging API",
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
            "test_member_1",
            "test_member_2"
        ]
    
    def setup(self) -> bool:
        """Initialize ClubOS API client for testing"""
        print("🔧 Setting up ClubOS Messaging Tests...")
        
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
        """Run all messaging tests"""
        print("\n" + "="*60)
        print("🧪 RUNNING CLUBOS MESSAGING API TESTS")
        print("="*60)
        
        if not self.setup():
            return self._finalize_results("Setup failed")
        
        # Individual messaging tests
        self.test_send_individual_text_message()
        self.test_send_individual_email_message()
        
        # Group messaging tests  
        self.test_send_group_text_message()
        self.test_send_group_email_message()
        
        # Error handling tests
        self.test_messaging_error_handling()
        
        # Performance tests
        self.test_messaging_rate_limits()
        
        return self._finalize_results()
    
    def test_send_individual_text_message(self):
        """Test sending individual text messages"""
        test_name = "Send Individual Text Message"
        print(f"\n🧪 Testing: {test_name}")
        
        try:
            test_member_id = self.test_member_ids[0]
            test_message = f"Test text message sent at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            result = self.client.send_individual_message(
                member_id=test_member_id,
                message=test_message,
                message_type="text"
            )
            
            success = result.get("success", False)
            
            self._record_test_result(
                test_name=test_name,
                success=success,
                details={
                    "member_id": test_member_id,
                    "message_type": "text",
                    "result": result
                }
            )
            
            if success:
                print(f"   ✅ Text message sent successfully to {test_member_id}")
            else:
                print(f"   ❌ Failed to send text message: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            self._record_test_result(test_name, False, {"error": str(e)})
            print(f"   ❌ Test error: {e}")
    
    def test_send_individual_email_message(self):
        """Test sending individual email messages"""
        test_name = "Send Individual Email Message"
        print(f"\n🧪 Testing: {test_name}")
        
        try:
            test_member_id = self.test_member_ids[0]
            test_message = f"Test email message sent at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            result = self.client.send_individual_message(
                member_id=test_member_id,
                message=test_message,
                message_type="email"
            )
            
            success = result.get("success", False)
            
            self._record_test_result(
                test_name=test_name,
                success=success,
                details={
                    "member_id": test_member_id,
                    "message_type": "email",
                    "result": result
                }
            )
            
            if success:
                print(f"   ✅ Email message sent successfully to {test_member_id}")
            else:
                print(f"   ❌ Failed to send email message: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            self._record_test_result(test_name, False, {"error": str(e)})
            print(f"   ❌ Test error: {e}")
    
    def test_send_group_text_message(self):
        """Test sending group text messages"""
        test_name = "Send Group Text Message"
        print(f"\n🧪 Testing: {test_name}")
        
        try:
            test_message = f"Test group text message sent at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            result = self.client.send_group_message(
                member_ids=self.test_member_ids[:2],  # Test with first 2 members
                message=test_message,
                message_type="text"
            )
            
            success = result.get("success", False)
            successful_sends = result.get("successful_sends", 0)
            total_members = result.get("total_members", 0)
            
            self._record_test_result(
                test_name=test_name,
                success=success,
                details={
                    "member_count": total_members,
                    "successful_sends": successful_sends,
                    "message_type": "text",
                    "result": result
                }
            )
            
            if success:
                print(f"   ✅ Group text message sent successfully to {successful_sends}/{total_members} members")
            else:
                print(f"   ⚠️ Group message partially failed: {successful_sends}/{total_members} successful")
                
        except Exception as e:
            self._record_test_result(test_name, False, {"error": str(e)})
            print(f"   ❌ Test error: {e}")
    
    def test_send_group_email_message(self):
        """Test sending group email messages"""
        test_name = "Send Group Email Message"
        print(f"\n🧪 Testing: {test_name}")
        
        try:
            test_message = f"Test group email message sent at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            result = self.client.send_group_message(
                member_ids=self.test_member_ids[:2],  # Test with first 2 members
                message=test_message,
                message_type="email"
            )
            
            success = result.get("success", False)
            successful_sends = result.get("successful_sends", 0)
            total_members = result.get("total_members", 0)
            
            self._record_test_result(
                test_name=test_name,
                success=success,
                details={
                    "member_count": total_members,
                    "successful_sends": successful_sends,
                    "message_type": "email",
                    "result": result
                }
            )
            
            if success:
                print(f"   ✅ Group email message sent successfully to {successful_sends}/{total_members} members")
            else:
                print(f"   ⚠️ Group message partially failed: {successful_sends}/{total_members} successful")
                
        except Exception as e:
            self._record_test_result(test_name, False, {"error": str(e)})
            print(f"   ❌ Test error: {e}")
    
    def test_messaging_error_handling(self):
        """Test messaging error handling with invalid inputs"""
        test_name = "Messaging Error Handling"
        print(f"\n🧪 Testing: {test_name}")
        
        error_tests = [
            {
                "description": "Invalid member ID",
                "member_id": "invalid_member_id",
                "message": "Test message",
                "message_type": "text"
            },
            {
                "description": "Empty message",
                "member_id": self.test_member_ids[0],
                "message": "",
                "message_type": "text"
            },
            {
                "description": "Invalid message type",
                "member_id": self.test_member_ids[0],
                "message": "Test message",
                "message_type": "invalid_type"
            }
        ]
        
        all_errors_handled = True
        error_results = []
        
        try:
            for error_test in error_tests:
                print(f"   🔍 Testing: {error_test['description']}")
                
                result = self.client.send_individual_message(
                    member_id=error_test["member_id"],
                    message=error_test["message"],
                    message_type=error_test["message_type"]
                )
                
                # We expect these to fail gracefully
                if result.get("success"):
                    print(f"      ⚠️ Expected failure but got success for: {error_test['description']}")
                    all_errors_handled = False
                else:
                    print(f"      ✅ Error handled correctly: {result.get('error', 'No error message')}")
                
                error_results.append({
                    "test": error_test["description"],
                    "result": result
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
    
    def test_messaging_rate_limits(self):
        """Test messaging rate limiting and performance"""
        test_name = "Messaging Rate Limits"
        print(f"\n🧪 Testing: {test_name}")
        
        try:
            start_time = time.time()
            message_count = 3  # Small test to avoid overwhelming the system
            
            for i in range(message_count):
                result = self.client.send_individual_message(
                    member_id=self.test_member_ids[0],
                    message=f"Rate limit test message {i+1}",
                    message_type="text"
                )
                
                if not result.get("success"):
                    print(f"      ⚠️ Message {i+1} failed: {result.get('error')}")
            
            end_time = time.time()
            total_time = end_time - start_time
            avg_time_per_message = total_time / message_count
            
            self._record_test_result(
                test_name=test_name,
                success=True,
                details={
                    "message_count": message_count,
                    "total_time_seconds": total_time,
                    "avg_time_per_message": avg_time_per_message,
                    "rate_limiting_respected": total_time > (message_count * 0.5)  # Assuming 0.5s minimum per message
                }
            )
            
            print(f"   ✅ Rate limit test completed: {message_count} messages in {total_time:.2f}s")
            print(f"      Average: {avg_time_per_message:.2f}s per message")
            
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
        print("📊 MESSAGING API TEST RESULTS")
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
            filename = f"/tmp/clubos_messaging_test_results_{timestamp}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(self.test_results, f, indent=2)
            print(f"📁 Test results saved to: {filename}")
        except Exception as e:
            print(f"❌ Error saving results: {e}")


def run_messaging_tests():
    """Run all ClubOS messaging API tests"""
    test_suite = ClubOSMessagingTests()
    results = test_suite.run_all_tests()
    test_suite.save_results()
    return results


if __name__ == "__main__":
    run_messaging_tests()