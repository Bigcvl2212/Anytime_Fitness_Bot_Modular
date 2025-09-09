"""
Tests for Social Media Management Module
Comprehensive test suite for all social media components.
"""

import sys
import os
from datetime import datetime, timedelta

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_social_media_imports():
    """Test that all social media modules can be imported successfully."""
    print("Testing social media module imports...")
    
    try:
        from src.services.social_media.content_generator import ContentGenerator
        print("✅ ContentGenerator import successful")
        
        from src.services.social_media.mock_facebook_api import MockFacebookAPI
        print("✅ MockFacebookAPI import successful")
        
        from src.services.social_media.facebook_manager import FacebookManager
        print("✅ FacebookManager import successful")
        
        from src.services.social_media.analytics import SocialMediaAnalytics
        print("✅ SocialMediaAnalytics import successful")
        
        from src.services.social_media.scheduler import PostScheduler
        print("✅ PostScheduler import successful")
        
        from src.services.social_media.social_media_manager import SocialMediaManager
        print("✅ SocialMediaManager import successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False


def test_content_generator():
    """Test the ContentGenerator functionality."""
    print("Testing ContentGenerator...")
    
    try:
        from src.services.social_media.content_generator import ContentGenerator
        
        # Initialize without AI client for testing
        generator = ContentGenerator(ai_client=None)
        
        # Test daily content generation
        posts = generator.generate_daily_content()
        assert isinstance(posts, list), "Daily content should return a list"
        assert len(posts) >= 1, "Should generate at least one post"
        assert len(posts) <= 3, "Should not generate more than 3 posts"
        
        # Test each post has required fields
        for post in posts:
            assert "content" in post, "Post should have content"
            assert "theme" in post, "Post should have theme"
            assert "post_type" in post, "Post should have post_type"
            assert len(post["content"]) > 0, "Content should not be empty"
        
        # Test themed post generation
        themed_post = generator._generate_themed_post("motivation", 1)
        assert themed_post["theme"] == "motivation", "Themed post should have correct theme"
        assert "content" in themed_post, "Themed post should have content"
        
        # Test hashtag generation
        hashtags = generator._generate_hashtags("fitness")
        assert "#AnytimeFitness" in hashtags, "Should include base hashtag"
        assert hashtags.count("#") >= 3, "Should have multiple hashtags"
        
        print("✅ ContentGenerator tests passed")
        return True
        
    except Exception as e:
        print(f"❌ ContentGenerator test failed: {e}")
        return False


def test_mock_facebook_api():
    """Test the MockFacebookAPI functionality."""
    print("Testing MockFacebookAPI...")
    
    try:
        from src.services.social_media.mock_facebook_api import MockFacebookAPI
        
        # Initialize API without delays for testing
        api = MockFacebookAPI(simulate_delays=False)
        
        # Test post creation
        content = "Test post content! 💪 #AnytimeFitness"
        result = api.create_post(content, "text")
        
        assert result["success"] is True, "Post creation should succeed"
        assert "post_id" in result, "Should return post ID"
        
        post_id = result["post_id"]
        assert post_id in api.posts, "Post should be stored"
        
        # Test getting posts
        posts_result = api.get_posts(limit=5)
        assert posts_result["success"] is True, "Getting posts should succeed"
        assert "posts" in posts_result, "Should return posts list"
        assert len(posts_result["posts"]) > 0, "Should have posts"
        
        # Test comments
        comments_result = api.get_post_comments(post_id)
        assert comments_result["success"] is True, "Getting comments should succeed"
        
        # Test messages
        messages_result = api.get_messages()
        assert messages_result["success"] is True, "Getting messages should succeed"
        
        # Test analytics
        analytics_result = api.get_page_analytics()
        assert analytics_result["success"] is True, "Getting analytics should succeed"
        assert "analytics" in analytics_result, "Should return analytics data"
        
        print("✅ MockFacebookAPI tests passed")
        return True
        
    except Exception as e:
        print(f"❌ MockFacebookAPI test failed: {e}")
        return False


def test_facebook_manager():
    """Test the FacebookManager functionality."""
    print("Testing FacebookManager...")
    
    try:
        from src.services.social_media.facebook_manager import FacebookManager
        
        # Initialize with mock API
        manager = FacebookManager(use_mock=True)
        
        # Test posting content
        content = "Test gym motivation! 🏋️‍♂️ #Fitness"
        result = manager.post_content(content)
        
        assert result["success"] is True, "Content posting should succeed"
        assert "post_id" in result, "Should return post ID"
        
        # Test engagement monitoring
        monitor_result = manager.monitor_engagement(hours_back=24)
        assert monitor_result["success"] is True, "Monitoring should succeed"
        assert "summary" in monitor_result, "Should return engagement summary"
        
        # Test response generation
        test_content = "what are your membership rates"
        category = manager._categorize_content(test_content)
        assert category == "membership_inquiry", "Should categorize membership question correctly"
        
        # Test template response
        response = manager._generate_template_response(test_content)
        assert isinstance(response, str), "Should return string response"
        assert len(response) > 0, "Response should not be empty"
        
        print("✅ FacebookManager tests passed")
        return True
        
    except Exception as e:
        print(f"❌ FacebookManager test failed: {e}")
        return False


def test_post_scheduler():
    """Test the PostScheduler functionality."""
    print("Testing PostScheduler...")
    
    try:
        from src.services.social_media.content_generator import ContentGenerator
        from src.services.social_media.facebook_manager import FacebookManager
        from src.services.social_media.scheduler import PostScheduler, PostStatus
        
        # Initialize components
        content_gen = ContentGenerator()
        facebook_mgr = FacebookManager(use_mock=True)
        scheduler = PostScheduler(content_gen, facebook_mgr)
        
        # Test post scheduling
        content = "Test scheduled post"
        scheduled_time = datetime.now() + timedelta(hours=1)
        
        result = scheduler.schedule_post(content, scheduled_time)
        assert result["success"] is True, "Post scheduling should succeed"
        assert "post_id" in result, "Should return post ID"
        
        post_id = result["post_id"]
        assert post_id in scheduler.scheduled_posts, "Post should be stored"
        
        scheduled_post = scheduler.scheduled_posts[post_id]
        assert scheduled_post.content == content, "Content should match"
        assert scheduled_post.status == PostStatus.SCHEDULED, "Status should be scheduled"
        
        # Test getting scheduled posts
        upcoming_result = scheduler.get_scheduled_posts(days_ahead=7)
        assert upcoming_result["success"] is True, "Getting scheduled posts should succeed"
        assert "upcoming_posts" in upcoming_result, "Should return upcoming posts"
        
        # Test scheduling statistics
        stats_result = scheduler.get_posting_statistics()
        assert stats_result["success"] is True, "Getting statistics should succeed"
        assert "statistics" in stats_result, "Should return statistics"
        
        # Test canceling post
        cancel_result = scheduler.cancel_scheduled_post(post_id)
        assert cancel_result["success"] is True, "Canceling should succeed"
        assert scheduler.scheduled_posts[post_id].status == PostStatus.CANCELLED, "Post should be cancelled"
        
        print("✅ PostScheduler tests passed")
        return True
        
    except Exception as e:
        print(f"❌ PostScheduler test failed: {e}")
        return False


def test_social_media_manager():
    """Test the main SocialMediaManager orchestrator."""
    print("Testing SocialMediaManager...")
    
    try:
        from src.services.social_media.social_media_manager import SocialMediaManager
        
        # Initialize manager
        manager = SocialMediaManager(use_mock_api=True)
        
        # Test initialization
        assert manager.content_generator is not None, "Content generator should be initialized"
        assert manager.facebook_manager is not None, "Facebook manager should be initialized"
        assert manager.analytics is not None, "Analytics should be initialized"
        assert manager.scheduler is not None, "Scheduler should be initialized"
        
        # Test content generation and posting
        result = manager.generate_and_post_content(theme="motivation", immediate=True)
        assert result["success"] is True, "Content generation should succeed"
        assert "post_id" in result, "Should return post ID"
        assert "content" in result, "Should return content"
        assert result["posted_immediately"] is True, "Should indicate immediate posting"
        
        # Test scheduled posting
        scheduled_result = manager.generate_and_post_content(theme="workout_tips", immediate=False)
        assert scheduled_result["success"] is True, "Scheduled posting should succeed"
        assert "scheduled_post_id" in scheduled_result, "Should return scheduled post ID"
        assert scheduled_result["posted_immediately"] is False, "Should indicate scheduled posting"
        
        # Test engagement simulation
        sim_result = manager.simulate_engagement_for_testing(2, 1)
        assert sim_result["success"] is True, "Engagement simulation should succeed"
        
        # Test engagement monitoring
        monitor_result = manager.monitor_and_respond_to_engagement()
        assert monitor_result["success"] is True, "Engagement monitoring should succeed"
        
        # Test system status
        status = manager.get_system_status()
        assert "scheduler_status" in status, "Should return scheduler status"
        assert "mock_api_mode" in status, "Should indicate mock API mode"
        assert status["mock_api_mode"] is True, "Should be in mock mode"
        
        print("✅ SocialMediaManager tests passed")
        return True
        
    except Exception as e:
        print(f"❌ SocialMediaManager test failed: {e}")
        return False


def test_social_media_workflow():
    """Test the complete social media workflow."""
    print("Testing complete social media workflow...")
    
    try:
        from src.services.social_media.social_media_manager import SocialMediaManager
        
        # Initialize manager
        manager = SocialMediaManager(use_mock_api=True)
        
        print("  📝 Generating and posting content...")
        # Generate and post some content
        post_results = []
        themes = ["motivation", "workout_tips", "member_success"]
        
        for theme in themes:
            result = manager.generate_and_post_content(theme=theme, immediate=True)
            assert result["success"] is True, f"Posting {theme} content should succeed"
            post_results.append(result)
        
        print(f"  ✅ Successfully posted {len(post_results)} pieces of content")
        
        print("  📅 Scheduling weekly content...")
        # Schedule weekly content
        schedule_result = manager.scheduler.schedule_weekly_content()
        assert schedule_result["success"] is True, "Weekly scheduling should succeed"
        
        scheduled_count = schedule_result.get("total_posts_scheduled", 0)
        print(f"  ✅ Scheduled {scheduled_count} posts for the week")
        
        print("  💬 Simulating and processing engagement...")
        # Simulate engagement
        sim_result = manager.simulate_engagement_for_testing(3, 2)
        assert sim_result["success"] is True, "Engagement simulation should succeed"
        
        # Process engagement
        engagement_result = manager.monitor_and_respond_to_engagement()
        assert engagement_result["success"] is True, "Engagement processing should succeed"
        
        responses = engagement_result.get("responses", {})
        print(f"  ✅ Processed engagement: {responses.get('comments', 0)} comment responses, {responses.get('messages', 0)} message responses")
        
        print("  📊 Generating performance report...")
        # Generate performance report
        report_result = manager.generate_performance_report()
        assert report_result["success"] is True, "Report generation should succeed"
        
        report = report_result.get("report", {})
        analytics = report.get("analytics", {})
        summary = analytics.get("summary_metrics", {})
        
        print(f"  ✅ Report generated - Total posts: {summary.get('total_posts', 0)}, Avg engagement: {summary.get('average_engagement_rate', 0):.3f}")
        
        print("✅ Complete social media workflow test passed")
        return True
        
    except Exception as e:
        print(f"❌ Social media workflow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all social media tests."""
    print("🧪 RUNNING SOCIAL MEDIA TESTS")
    print("=" * 50)
    
    tests = [
        test_social_media_imports,
        test_content_generator,
        test_mock_facebook_api,
        test_facebook_manager,
        test_post_scheduler,
        test_social_media_manager,
        test_social_media_workflow
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            failed += 1
        print("-" * 50)
    
    print(f"\n📊 TEST RESULTS:")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📈 Success Rate: {(passed/(passed+failed)*100):.1f}%")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)