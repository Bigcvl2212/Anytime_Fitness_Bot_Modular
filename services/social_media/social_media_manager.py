"""
Social Media Manager - Main orchestrator for all social media operations
Coordinates content generation, posting, engagement, and analytics.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from .content_generator import ContentGenerator
from .facebook_manager import FacebookManager
from .analytics import SocialMediaAnalytics
from .scheduler import PostScheduler
from .mock_facebook_api import MockFacebookAPI

logger = logging.getLogger(__name__)


class SocialMediaManager:
    """
    Main social media management orchestrator that coordinates all social media operations.
    """
    
    def __init__(self, ai_client=None, use_mock_api: bool = True):
        """
        Initialize the social media manager with all required components.
        
        Args:
            ai_client: AI client for content generation and responses
            use_mock_api: Whether to use mock Facebook API for testing
        """
        self.ai_client = ai_client
        self.use_mock_api = use_mock_api
        
        # Initialize components
        self.content_generator = ContentGenerator(ai_client=ai_client)
        self.facebook_manager = FacebookManager(
            api_client=None, 
            use_mock=use_mock_api, 
            ai_client=ai_client
        )
        self.analytics = SocialMediaAnalytics(self.facebook_manager)
        self.scheduler = PostScheduler(self.content_generator, self.facebook_manager)
        
        logger.info(f"Social Media Manager initialized (mock_api: {use_mock_api})")
    
    def start_autonomous_operation(self) -> Dict[str, Any]:
        """
        Start fully autonomous social media management.
        
        Returns:
            Status of autonomous operation startup
        """
        try:
            results = {
                "content_scheduling": {},
                "auto_posting": {},
                "engagement_monitoring": {},
                "status": "starting"
            }
            
            # 1. Schedule content for the next week
            logger.info("Scheduling weekly content...")
            schedule_result = self.scheduler.schedule_weekly_content()
            results["content_scheduling"] = schedule_result
            
            if not schedule_result.get("success"):
                return {
                    "success": False,
                    "error": "Failed to schedule weekly content",
                    "details": results
                }
            
            # 2. Start auto-posting service
            logger.info("Starting auto-posting service...")
            auto_post_result = self.scheduler.start_auto_posting(check_interval=300)  # Check every 5 minutes
            results["auto_posting"] = auto_post_result
            
            if not auto_post_result.get("success"):
                return {
                    "success": False,
                    "error": "Failed to start auto-posting",
                    "details": results
                }
            
            # 3. Perform initial engagement check
            logger.info("Monitoring engagement...")
            engagement_result = self.monitor_and_respond_to_engagement()
            results["engagement_monitoring"] = engagement_result
            
            results["status"] = "operational"
            
            logger.info("Autonomous social media operation started successfully")
            
            return {
                "success": True,
                "message": "Autonomous social media management is now operational",
                "details": results,
                "operation_summary": {
                    "posts_scheduled": schedule_result.get("total_posts_scheduled", 0),
                    "auto_posting_enabled": True,
                    "engagement_items_processed": len(engagement_result.get("engagement_summary", {}).get("needs_response", []))
                }
            }
            
        except Exception as e:
            logger.error(f"Error starting autonomous operation: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def stop_autonomous_operation(self) -> Dict[str, Any]:
        """Stop autonomous social media management."""
        try:
            # Stop auto-posting
            stop_result = self.scheduler.stop_auto_posting()
            
            logger.info("Autonomous social media operation stopped")
            
            return {
                "success": True,
                "message": "Autonomous operation stopped",
                "auto_posting_stopped": stop_result.get("success", False)
            }
            
        except Exception as e:
            logger.error(f"Error stopping autonomous operation: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def generate_and_post_content(self, theme: Optional[str] = None, 
                                 immediate: bool = True) -> Dict[str, Any]:
        """
        Generate and post content immediately or schedule it.
        
        Args:
            theme: Content theme to generate (random if None)
            immediate: Whether to post immediately or schedule
            
        Returns:
            Result of content generation and posting
        """
        try:
            # Generate content
            if theme:
                post = self.content_generator._generate_themed_post(theme, 1)
            else:
                daily_posts = self.content_generator.generate_daily_content()
                post = daily_posts[0] if daily_posts else None
            
            if not post:
                return {
                    "success": False,
                    "error": "Failed to generate content"
                }
            
            # Post or schedule content
            if immediate:
                result = self.facebook_manager.post_content(
                    content=post["content"],
                    post_type=post.get("post_type", "text")
                )
                
                return {
                    "success": result.get("success", False),
                    "post_id": result.get("post_id"),
                    "content": post["content"],
                    "theme": post["theme"],
                    "posted_immediately": True,
                    "error": result.get("error")
                }
            else:
                # Schedule for optimal time
                optimal_time = self._get_next_optimal_posting_time()
                schedule_result = self.scheduler.schedule_post(
                    content=post["content"],
                    scheduled_time=optimal_time,
                    post_type=post.get("post_type", "text"),
                    theme=post["theme"]
                )
                
                return {
                    "success": schedule_result.get("success", False),
                    "scheduled_post_id": schedule_result.get("post_id"),
                    "content": post["content"],
                    "theme": post["theme"],
                    "scheduled_time": optimal_time.isoformat(),
                    "posted_immediately": False,
                    "error": schedule_result.get("error")
                }
                
        except Exception as e:
            logger.error(f"Error generating and posting content: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def monitor_and_respond_to_engagement(self, hours_back: int = 24) -> Dict[str, Any]:
        """
        Monitor for new engagement and respond automatically.
        
        Args:
            hours_back: How many hours back to check for engagement
            
        Returns:
            Summary of engagement monitoring and responses
        """
        try:
            # Monitor engagement
            monitoring_result = self.facebook_manager.monitor_engagement(hours_back=hours_back)
            
            if not monitoring_result.get("success"):
                return monitoring_result
            
            engagement_summary = monitoring_result.get("summary", {})
            items_needing_response = engagement_summary.get("needs_response", [])
            
            # Respond to engagement
            response_result = {"responses_sent": {"comments": 0, "messages": 0, "failed": 0}}
            
            if items_needing_response:
                response_result = self.facebook_manager.respond_to_engagement(items_needing_response)
            
            return {
                "success": True,
                "engagement_summary": engagement_summary,
                "responses": response_result.get("responses_sent", {}),
                "monitoring_period_hours": hours_back,
                "items_processed": len(items_needing_response)
            }
            
        except Exception as e:
            logger.error(f"Error monitoring engagement: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def generate_performance_report(self, period: str = "week") -> Dict[str, Any]:
        """
        Generate comprehensive performance report.
        
        Args:
            period: Report period ('week', 'month')
            
        Returns:
            Performance report with analytics and insights
        """
        try:
            # Generate analytics report
            if period == "week":
                weeks_back = 1
                analytics_report = self.analytics.generate_weekly_report(weeks_back=weeks_back)
            else:
                # For month, generate 4 weeks
                weeks_back = 4
                analytics_report = self.analytics.generate_weekly_report(weeks_back=weeks_back)
            
            if not analytics_report.get("success"):
                return analytics_report
            
            # Get scheduler statistics
            scheduler_stats = self.scheduler.get_posting_statistics()
            
            # Get current scheduled posts
            upcoming_posts = self.scheduler.get_scheduled_posts(days_ahead=7)
            
            # Combine into comprehensive report
            report = {
                "period": period,
                "generated_at": datetime.now().isoformat(),
                "analytics": analytics_report.get("report", {}),
                "scheduling_performance": scheduler_stats.get("statistics", {}),
                "upcoming_content": {
                    "posts_scheduled": upcoming_posts.get("total_scheduled", 0),
                    "next_post": self._get_next_post_preview(upcoming_posts)
                },
                "system_status": self.get_system_status(),
                "recommendations": self._generate_strategic_recommendations(analytics_report.get("report", {}))
            }
            
            return {
                "success": True,
                "report": report
            }
            
        except Exception as e:
            logger.error(f"Error generating performance report: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def optimize_content_strategy(self) -> Dict[str, Any]:
        """
        Analyze performance and optimize content strategy.
        
        Returns:
            Optimization recommendations and updated strategy
        """
        try:
            # Get recent post performance data
            posts_response = self.facebook_manager.api.get_posts(limit=50)
            if not posts_response.get("success"):
                return {"success": False, "error": "Failed to fetch posts for analysis"}
            
            posts = posts_response.get("posts", [])
            
            # Analyze performance patterns
            optimization_insights = []
            
            if posts:
                # Analyze top performing posts
                top_posts = sorted(posts, key=lambda p: p.get("engagement_rate", 0), reverse=True)[:5]
                
                # Extract patterns from top performers
                patterns = self._analyze_top_post_patterns(top_posts)
                optimization_insights.extend(patterns)
                
                # Analyze underperforming content
                low_posts = [p for p in posts if p.get("engagement_rate", 0) < 0.02]
                if low_posts:
                    optimization_insights.append({
                        "type": "improvement",
                        "category": "underperforming_content",
                        "insight": f"{len(low_posts)} posts have low engagement rates",
                        "recommendation": "Review and adjust content themes with poor performance"
                    })
            
            # Get posting time optimization
            time_optimization = self.scheduler.optimize_posting_times()
            
            # Update content generator themes based on insights
            strategy_updates = self._update_content_strategy(optimization_insights)
            
            return {
                "success": True,
                "optimization_insights": optimization_insights,
                "posting_time_optimization": time_optimization,
                "strategy_updates": strategy_updates,
                "next_steps": [
                    "Apply optimized posting schedule",
                    "Focus on high-performing content themes",
                    "Test new content formats based on insights",
                    "Monitor performance changes over next week"
                ]
            }
            
        except Exception as e:
            logger.error(f"Error optimizing content strategy: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _analyze_top_post_patterns(self, top_posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze patterns in top-performing posts."""
        insights = []
        
        # Analyze content characteristics
        total_posts = len(top_posts)
        posts_with_questions = sum(1 for post in top_posts if "?" in post.get("content", ""))
        posts_with_emojis = sum(1 for post in top_posts if any(ord(char) > 127 for char in post.get("content", "")))
        
        if posts_with_questions / total_posts > 0.6:
            insights.append({
                "type": "pattern",
                "category": "content_format",
                "insight": "Posts with questions perform significantly better",
                "recommendation": "Increase use of questions in content to drive engagement"
            })
        
        if posts_with_emojis / total_posts > 0.8:
            insights.append({
                "type": "pattern",
                "category": "content_format", 
                "insight": "Posts with emojis show higher engagement rates",
                "recommendation": "Continue using emojis to enhance visual appeal"
            })
        
        # Analyze posting times
        posting_hours = [
            datetime.fromisoformat(post["timestamp"].replace('Z', '+00:00')).hour
            for post in top_posts
        ]
        
        if posting_hours:
            avg_hour = sum(posting_hours) / len(posting_hours)
            if 8 <= avg_hour <= 10:
                insights.append({
                    "type": "pattern",
                    "category": "timing",
                    "insight": "Morning posts (8-10am) show strong performance",
                    "recommendation": "Prioritize morning posting for high-engagement content"
                })
            elif 17 <= avg_hour <= 19:
                insights.append({
                    "type": "pattern",
                    "category": "timing",
                    "insight": "Evening posts (5-7pm) drive high engagement",
                    "recommendation": "Focus evening posts on interactive content"
                })
        
        return insights
    
    def _update_content_strategy(self, insights: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Update content strategy based on optimization insights."""
        updates = {
            "content_adjustments": [],
            "posting_frequency_changes": [],
            "format_recommendations": []
        }
        
        for insight in insights:
            if insight["category"] == "content_format":
                if "questions" in insight["insight"].lower():
                    updates["format_recommendations"].append("Increase question-based content by 30%")
                elif "emojis" in insight["insight"].lower():
                    updates["format_recommendations"].append("Maintain high emoji usage in posts")
            
            elif insight["category"] == "timing":
                updates["posting_frequency_changes"].append(f"Adjust posting schedule based on insight: {insight['insight']}")
            
            elif insight["category"] == "underperforming_content":
                updates["content_adjustments"].append("Reduce frequency of low-performing content themes")
        
        return updates
    
    def _get_next_optimal_posting_time(self) -> datetime:
        """Get the next optimal posting time based on current schedule."""
        now = datetime.now()
        day_name = now.strftime('%A').lower()
        
        # Get optimal times for current day
        optimal_times = self.scheduler.optimal_times.get(day_name, [(9, 11), (17, 19)])
        
        # Find next available optimal time
        for start_hour, end_hour in optimal_times:
            optimal_time = now.replace(hour=start_hour, minute=0, second=0, microsecond=0)
            if optimal_time > now:
                return optimal_time
        
        # If no optimal time today, use first optimal time tomorrow
        tomorrow = now + timedelta(days=1)
        tomorrow_day = tomorrow.strftime('%A').lower()
        tomorrow_optimal = self.scheduler.optimal_times.get(tomorrow_day, [(9, 11)])[0]
        
        return tomorrow.replace(
            hour=tomorrow_optimal[0],
            minute=0,
            second=0,
            microsecond=0
        )
    
    def _get_next_post_preview(self, upcoming_posts: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get preview of next scheduled post."""
        posts = upcoming_posts.get("upcoming_posts", [])
        if not posts:
            return None
        
        next_post = posts[0]  # Should be sorted by time
        return {
            "content_preview": next_post.get("content", "")[:50] + "...",
            "theme": next_post.get("theme"),
            "scheduled_time": next_post.get("scheduled_time"),
            "time_until_post": next_post.get("time_until_post")
        }
    
    def _generate_strategic_recommendations(self, analytics_report: Dict[str, Any]) -> List[str]:
        """Generate strategic recommendations based on analytics."""
        recommendations = []
        
        summary_metrics = analytics_report.get("summary_metrics", {})
        theme_performance = analytics_report.get("theme_performance", {})
        
        # Posting frequency recommendations
        posts_per_day = summary_metrics.get("posts_per_day", 0)
        if posts_per_day < 2:
            recommendations.append("Increase posting frequency to 2-3 posts per day for better engagement")
        elif posts_per_day > 4:
            recommendations.append("Consider reducing posting frequency to avoid audience fatigue")
        
        # Theme-based recommendations
        if theme_performance:
            best_theme = max(theme_performance.items(), key=lambda x: x[1].get("avg_engagement_rate", 0))
            worst_theme = min(theme_performance.items(), key=lambda x: x[1].get("avg_engagement_rate", 0))
            
            recommendations.append(f"Focus more on '{best_theme[0]}' content - it shows highest engagement")
            
            if worst_theme[1].get("avg_engagement_rate", 0) < 0.02:
                recommendations.append(f"Revise or reduce '{worst_theme[0]}' content strategy")
        
        # Engagement recommendations
        avg_engagement = summary_metrics.get("average_engagement_rate", 0)
        if avg_engagement < 0.03:
            recommendations.append("Implement more interactive content (polls, questions, challenges)")
        
        return recommendations[:5]  # Limit to top 5 recommendations
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current status of all social media management components."""
        return {
            "scheduler_status": self.scheduler.get_scheduler_status().get("status", {}),
            "content_generator_ready": True,
            "facebook_manager_ready": True,
            "analytics_ready": True,
            "mock_api_mode": self.use_mock_api,
            "ai_client_available": self.ai_client is not None
        }
    
    def simulate_engagement_for_testing(self, num_comments: int = 3, num_messages: int = 2) -> Dict[str, Any]:
        """
        Simulate new engagement for testing purposes (only works with mock API).
        
        Args:
            num_comments: Number of comments to simulate
            num_messages: Number of messages to simulate
            
        Returns:
            Summary of simulated engagement
        """
        if not self.use_mock_api:
            return {
                "success": False,
                "error": "Engagement simulation only available in mock API mode"
            }
        
        try:
            mock_api = self.facebook_manager.api
            
            # Get a recent post to comment on
            posts_response = mock_api.get_posts(limit=5)
            posts = posts_response.get("posts", [])
            
            simulated_items = {
                "comments": [],
                "messages": []
            }
            
            # Simulate comments
            if posts and num_comments > 0:
                post = posts[0]
                for i in range(num_comments):
                    comment_id = mock_api.simulate_new_comment(
                        post_id=post["id"],
                        author=f"Test User {i+1}",
                        content=f"Great post! What are your membership rates? This is test comment {i+1}."
                    )
                    simulated_items["comments"].append(comment_id)
            
            # Simulate messages
            for i in range(num_messages):
                message_id = mock_api.simulate_new_message(
                    sender=f"Test Sender {i+1}",
                    content=f"Hi, I'm interested in your services. Can you help me? This is test message {i+1}."
                )
                simulated_items["messages"].append(message_id)
            
            return {
                "success": True,
                "simulated_engagement": simulated_items,
                "message": f"Simulated {num_comments} comments and {num_messages} messages for testing"
            }
            
        except Exception as e:
            logger.error(f"Error simulating engagement: {e}")
            return {
                "success": False,
                "error": str(e)
            }