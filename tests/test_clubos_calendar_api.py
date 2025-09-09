"""
Comprehensive test suite for ClubOS API endpoints - Calendar functionality.
Tests calendar CRUD operations and session management.
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.services.api.enhanced_clubos_client import create_enhanced_clubos_client


class ClubOSCalendarTests:
    """Test suite for ClubOS calendar API endpoints"""
    
    def __init__(self):
        self.client = None
        self.test_results = {
            "test_suite": "ClubOS Calendar API",
            "start_time": datetime.now().isoformat(),
            "tests": [],
            "summary": {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "skipped": 0
            }
        }
        self.test_session_ids = []  # To track sessions created during testing
        self.test_member_ids = ["66735385", "test_member_1"]
    
    def setup(self) -> bool:
        """Initialize ClubOS API client for testing"""
        print("🔧 Setting up ClubOS Calendar Tests...")
        
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
        """Run all calendar tests"""
        print("\n" + "="*60)
        print("🧪 RUNNING CLUBOS CALENDAR API TESTS")
        print("="*60)
        
        if not self.setup():
            return self._finalize_results("Setup failed")
        
        # Calendar viewing tests
        self.test_get_calendar_sessions()
        self.test_get_calendar_sessions_specific_date()
        
        # Calendar CRUD tests
        self.test_create_calendar_session()
        self.test_update_calendar_session()
        self.test_delete_calendar_session()
        
        # Session management tests
        self.test_add_member_to_session()
        
        # Error handling tests
        self.test_calendar_error_handling()
        
        # Cleanup
        self.cleanup_test_sessions()
        
        return self._finalize_results()
    
    def test_get_calendar_sessions(self):
        """Test retrieving calendar sessions for today"""
        test_name = "Get Calendar Sessions (Today)"
        print(f"\n🧪 Testing: {test_name}")
        
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            
            sessions = self.client.get_calendar_sessions(
                date=today,
                schedule_name="My schedule"
            )
            
            success = isinstance(sessions, list)
            
            self._record_test_result(
                test_name=test_name,
                success=success,
                details={
                    "date": today,
                    "schedule": "My schedule",
                    "sessions_count": len(sessions) if success else 0,
                    "sessions": sessions[:3] if success and len(sessions) > 0 else []  # First 3 for brevity
                }
            )
            
            if success:
                print(f"   ✅ Retrieved {len(sessions)} calendar sessions for {today}")
                if sessions:
                    print(f"      Sample session: {sessions[0]}")
            else:
                print(f"   ❌ Failed to retrieve calendar sessions")
                
        except Exception as e:
            self._record_test_result(test_name, False, {"error": str(e)})
            print(f"   ❌ Test error: {e}")
    
    def test_get_calendar_sessions_specific_date(self):
        """Test retrieving calendar sessions for a specific date"""
        test_name = "Get Calendar Sessions (Specific Date)"
        print(f"\n🧪 Testing: {test_name}")
        
        try:
            # Test with tomorrow's date
            tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
            
            sessions = self.client.get_calendar_sessions(
                date=tomorrow,
                schedule_name="My schedule"
            )
            
            success = isinstance(sessions, list)
            
            self._record_test_result(
                test_name=test_name,
                success=success,
                details={
                    "date": tomorrow,
                    "schedule": "My schedule",
                    "sessions_count": len(sessions) if success else 0,
                    "sessions": sessions[:3] if success and len(sessions) > 0 else []
                }
            )
            
            if success:
                print(f"   ✅ Retrieved {len(sessions)} calendar sessions for {tomorrow}")
            else:
                print(f"   ❌ Failed to retrieve calendar sessions for specific date")
                
        except Exception as e:
            self._record_test_result(test_name, False, {"error": str(e)})
            print(f"   ❌ Test error: {e}")
    
    def test_create_calendar_session(self):
        """Test creating a new calendar session"""
        test_name = "Create Calendar Session"
        print(f"\n🧪 Testing: {test_name}")
        
        try:
            # Create test session for tomorrow
            tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
            
            session_data = {
                "title": f"API Test Session {datetime.now().strftime('%H:%M:%S')}",
                "date": tomorrow,
                "start_time": "10:00",
                "end_time": "11:00",
                "description": "Test session created via API",
                "schedule": "My schedule"
            }
            
            result = self.client.create_calendar_session(session_data)
            
            success = result.get("success", False)
            
            self._record_test_result(
                test_name=test_name,
                success=success,
                details={
                    "session_data": session_data,
                    "result": result
                }
            )
            
            if success:
                print(f"   ✅ Calendar session created successfully")
                print(f"      Title: {session_data['title']}")
                print(f"      Date: {session_data['date']} {session_data['start_time']}-{session_data['end_time']}")
                
                # Store for cleanup
                self.test_session_ids.append(session_data["title"])
            else:
                print(f"   ❌ Failed to create calendar session: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            self._record_test_result(test_name, False, {"error": str(e)})
            print(f"   ❌ Test error: {e}")
    
    def test_update_calendar_session(self):
        """Test updating an existing calendar session"""
        test_name = "Update Calendar Session"
        print(f"\n🧪 Testing: {test_name}")
        
        try:
            # First create a session to update
            tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
            
            session_data = {
                "title": f"Update Test Session {datetime.now().strftime('%H:%M:%S')}",
                "date": tomorrow,
                "start_time": "14:00",
                "end_time": "15:00",
                "description": "Session to be updated",
                "schedule": "My schedule"
            }
            
            create_result = self.client.create_calendar_session(session_data)
            
            if not create_result.get("success"):
                self._record_test_result(test_name, False, {"error": "Failed to create session for update test"})
                return
            
            # Now try to update it (using title as ID for simplicity)
            session_id = session_data["title"]
            updates = {
                "title": f"Updated {session_data['title']}",
                "description": "This session has been updated via API",
                "end_time": "15:30"
            }
            
            result = self.client.update_calendar_session(session_id, updates)
            
            success = result.get("success", False)
            
            self._record_test_result(
                test_name=test_name,
                success=success,
                details={
                    "original_session": session_data,
                    "updates": updates,
                    "result": result
                }
            )
            
            if success:
                print(f"   ✅ Calendar session updated successfully")
                print(f"      Session ID: {session_id}")
                print(f"      Updates applied: {updates}")
            else:
                print(f"   ❌ Failed to update calendar session: {result.get('error', 'Unknown error')}")
            
            # Store for cleanup
            self.test_session_ids.append(session_id)
            self.test_session_ids.append(updates.get("title", session_id))
                
        except Exception as e:
            self._record_test_result(test_name, False, {"error": str(e)})
            print(f"   ❌ Test error: {e}")
    
    def test_delete_calendar_session(self):
        """Test deleting a calendar session"""
        test_name = "Delete Calendar Session"
        print(f"\n🧪 Testing: {test_name}")
        
        try:
            # First create a session to delete
            tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
            
            session_data = {
                "title": f"Delete Test Session {datetime.now().strftime('%H:%M:%S')}",
                "date": tomorrow,
                "start_time": "16:00",
                "end_time": "17:00",
                "description": "Session to be deleted",
                "schedule": "My schedule"
            }
            
            create_result = self.client.create_calendar_session(session_data)
            
            if not create_result.get("success"):
                self._record_test_result(test_name, False, {"error": "Failed to create session for delete test"})
                return
            
            # Now try to delete it
            session_id = session_data["title"]
            
            result = self.client.delete_calendar_session(session_id)
            
            success = result.get("success", False)
            
            self._record_test_result(
                test_name=test_name,
                success=success,
                details={
                    "session_data": session_data,
                    "session_id": session_id,
                    "result": result
                }
            )
            
            if success:
                print(f"   ✅ Calendar session deleted successfully")
                print(f"      Session ID: {session_id}")
            else:
                print(f"   ❌ Failed to delete calendar session: {result.get('error', 'Unknown error')}")
                # Add to cleanup list in case deletion failed
                self.test_session_ids.append(session_id)
                
        except Exception as e:
            self._record_test_result(test_name, False, {"error": str(e)})
            print(f"   ❌ Test error: {e}")
    
    def test_add_member_to_session(self):
        """Test adding a member to an existing session"""
        test_name = "Add Member to Session"
        print(f"\n🧪 Testing: {test_name}")
        
        try:
            # First create a session
            tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
            
            session_data = {
                "title": f"Member Test Session {datetime.now().strftime('%H:%M:%S')}",
                "date": tomorrow,
                "start_time": "18:00",
                "end_time": "19:00",
                "description": "Session for member addition test",
                "schedule": "My schedule"
            }
            
            create_result = self.client.create_calendar_session(session_data)
            
            if not create_result.get("success"):
                self._record_test_result(test_name, False, {"error": "Failed to create session for member test"})
                return
            
            # Now try to add a member
            session_id = session_data["title"]
            member_id = self.test_member_ids[0]
            
            result = self.client.add_member_to_session(session_id, member_id)
            
            success = result.get("success", False)
            
            self._record_test_result(
                test_name=test_name,
                success=success,
                details={
                    "session_data": session_data,
                    "session_id": session_id,
                    "member_id": member_id,
                    "result": result
                }
            )
            
            if success:
                print(f"   ✅ Member added to session successfully")
                print(f"      Session ID: {session_id}")
                print(f"      Member ID: {member_id}")
            else:
                print(f"   ❌ Failed to add member to session: {result.get('error', 'Unknown error')}")
            
            # Store for cleanup
            self.test_session_ids.append(session_id)
                
        except Exception as e:
            self._record_test_result(test_name, False, {"error": str(e)})
            print(f"   ❌ Test error: {e}")
    
    def test_calendar_error_handling(self):
        """Test calendar error handling with invalid inputs"""
        test_name = "Calendar Error Handling"
        print(f"\n🧪 Testing: {test_name}")
        
        error_tests = [
            {
                "description": "Invalid date format",
                "session_data": {
                    "title": "Invalid Date Test",
                    "date": "invalid-date",
                    "start_time": "10:00",
                    "end_time": "11:00"
                }
            },
            {
                "description": "Missing required fields",
                "session_data": {
                    "title": "Incomplete Session"
                    # Missing date, start_time, end_time
                }
            },
            {
                "description": "Invalid time format",
                "session_data": {
                    "title": "Invalid Time Test",
                    "date": "2024-12-31",
                    "start_time": "25:00",  # Invalid hour
                    "end_time": "26:00"
                }
            }
        ]
        
        all_errors_handled = True
        error_results = []
        
        try:
            for error_test in error_tests:
                print(f"   🔍 Testing: {error_test['description']}")
                
                result = self.client.create_calendar_session(error_test["session_data"])
                
                # We expect these to fail gracefully
                if result.get("success"):
                    print(f"      ⚠️ Expected failure but got success for: {error_test['description']}")
                    all_errors_handled = False
                    # Add to cleanup just in case
                    self.test_session_ids.append(error_test["session_data"].get("title", "unknown"))
                else:
                    print(f"      ✅ Error handled correctly: {result.get('error', 'No error message')}")
                
                error_results.append({
                    "test": error_test["description"],
                    "result": result
                })
            
            # Test invalid session operations
            print("   🔍 Testing: Invalid session operations")
            
            invalid_ops = [
                ("update", self.client.update_calendar_session("invalid_session_id", {"title": "test"})),
                ("delete", self.client.delete_calendar_session("invalid_session_id")),
                ("add_member", self.client.add_member_to_session("invalid_session_id", "invalid_member_id"))
            ]
            
            for op_name, op_result in invalid_ops:
                if op_result.get("success"):
                    print(f"      ⚠️ Expected failure for invalid {op_name} operation")
                    all_errors_handled = False
                else:
                    print(f"      ✅ Invalid {op_name} operation handled correctly")
                
                error_results.append({
                    "test": f"Invalid {op_name} operation",
                    "result": op_result
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
    
    def cleanup_test_sessions(self):
        """Clean up sessions created during testing"""
        test_name = "Cleanup Test Sessions"
        print(f"\n🧹 {test_name}")
        
        cleanup_results = []
        
        for session_id in self.test_session_ids:
            try:
                result = self.client.delete_calendar_session(session_id)
                cleanup_results.append({
                    "session_id": session_id,
                    "deleted": result.get("success", False),
                    "error": result.get("error")
                })
                
                if result.get("success"):
                    print(f"   ✅ Cleaned up session: {session_id}")
                else:
                    print(f"   ⚠️ Failed to cleanup session: {session_id}")
                    
            except Exception as e:
                print(f"   ❌ Error cleaning up session {session_id}: {e}")
                cleanup_results.append({
                    "session_id": session_id,
                    "deleted": False,
                    "error": str(e)
                })
        
        self._record_test_result(
            test_name=test_name,
            success=True,  # Cleanup is best effort
            details={
                "sessions_to_cleanup": len(self.test_session_ids),
                "cleanup_results": cleanup_results
            }
        )
    
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
        print("📊 CALENDAR API TEST RESULTS")
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
            filename = f"/tmp/clubos_calendar_test_results_{timestamp}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(self.test_results, f, indent=2)
            print(f"📁 Test results saved to: {filename}")
        except Exception as e:
            print(f"❌ Error saving results: {e}")


def run_calendar_tests():
    """Run all ClubOS calendar API tests"""
    test_suite = ClubOSCalendarTests()
    results = test_suite.run_all_tests()
    test_suite.save_results()
    return results


if __name__ == "__main__":
    run_calendar_tests()