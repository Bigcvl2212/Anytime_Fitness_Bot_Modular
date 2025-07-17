"""
Post Scheduler for Social Media Management
Handles scheduling, timing optimization, and automated posting workflows.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta, time
import json
import threading
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class PostStatus(Enum):
    """Enumeration for post status."""
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ScheduledPost:
    """Data class for a scheduled post."""
    id: str
    content: str
    post_type: str
    theme: str
    scheduled_time: datetime
    status: PostStatus
    created_at: datetime
    attempts: int = 0
    max_attempts: int = 3
    last_error: Optional[str] = None


class PostScheduler:
    """
    Manages scheduling and automated posting of social media content.
    """
    
    def __init__(self, content_generator, facebook_manager):
        """
        Initialize the post scheduler.
        
        Args:
            content_generator: ContentGenerator instance
            facebook_manager: FacebookManager instance
        """
        self.content_generator = content_generator
        self.facebook_manager = facebook_manager
        self.scheduled_posts = {}  # Store scheduled posts
        self.posting_schedule = self._create_default_posting_schedule()
        self.optimal_times = self._define_optimal_posting_times()
        self.is_running = False
        self.scheduler_thread = None
    
    def _create_default_posting_schedule(self) -> Dict[str, List[Dict[str, Any]]]:
        """Create default weekly posting schedule."""
        return {
            "monday": [
                {"time": "08:00", "theme": "motivation", "type": "text"},
                {"time": "17:30", "theme": "workout_tips", "type": "text"}
            ],
            "tuesday": [
                {"time": "09:00", "theme": "nutrition", "type": "text"},
                {"time": "18:00", "theme": "challenges", "type": "text"}
            ],
            "wednesday": [
                {"time": "08:30", "theme": "member_success", "type": "text"},
                {"time": "17:00", "theme": "gym_promotions", "type": "text"}
            ],
            "thursday": [
                {"time": "09:30", "theme": "workout_tips", "type": "text"},
                {"time": "18:30", "theme": "motivation", "type": "text"}
            ],
            "friday": [
                {"time": "08:00", "theme": "challenges", "type": "text"},
                {"time": "17:00", "theme": "member_success", "type": "text"}
            ],
            "saturday": [
                {"time": "10:00", "theme": "gym_promotions", "type": "text"},
                {"time": "15:00", "theme": "nutrition", "type": "text"}
            ],
            "sunday": [
                {"time": "11:00", "theme": "motivation", "type": "text"},
                {"time": "16:00", "theme": "challenges", "type": "text"}
            ]
        }
    
    def _define_optimal_posting_times(self) -> Dict[str, List[Tuple[int, int]]]:
        """Define optimal posting times by day of week."""
        return {
            "monday": [(8, 10), (17, 19)],      # Morning and evening commute
            "tuesday": [(9, 11), (18, 20)],    # Mid-morning and early evening
            "wednesday": [(8, 10), (17, 19)],  # Similar to Monday
            "thursday": [(9, 11), (18, 20)],   # Similar to Tuesday
            "friday": [(8, 10), (16, 18)],     # Earlier evening on Friday
            "saturday": [(10, 12), (14, 16)],  # Late morning and afternoon
            "sunday": [(11, 13), (15, 17)]     # Late morning and mid-afternoon
        }
    
    def schedule_post(self, content: str, scheduled_time: datetime, 
                     post_type: str = "text", theme: str = "general") -> Dict[str, Any]:
        """
        Schedule a single post for future publishing.
        
        Args:
            content: Post content
            scheduled_time: When to publish the post
            post_type: Type of post (text, image, video)
            theme: Content theme
            
        Returns:
            Response with scheduling details
        """
        try:
            # Generate unique post ID
            post_id = f"scheduled_{int(scheduled_time.timestamp())}_{len(self.scheduled_posts)}"
            
            # Create scheduled post object
            scheduled_post = ScheduledPost(
                id=post_id,
                content=content,
                post_type=post_type,
                theme=theme,
                scheduled_time=scheduled_time,
                status=PostStatus.SCHEDULED,
                created_at=datetime.now()
            )
            
            # Store in schedule
            self.scheduled_posts[post_id] = scheduled_post
            
            logger.info(f"Post scheduled: {post_id} for {scheduled_time}")
            
            return {
                "success": True,
                "post_id": post_id,
                "scheduled_time": scheduled_time.isoformat(),
                "message": "Post scheduled successfully"
            }
            
        except Exception as e:
            logger.error(f"Error scheduling post: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def schedule_daily_content(self, date: datetime) -> Dict[str, Any]:
        """
        Schedule content for a specific day based on the posting schedule.
        
        Args:
            date: Date to schedule content for
            
        Returns:
            Summary of scheduled posts
        """
        try:
            day_name = date.strftime('%A').lower()
            day_schedule = self.posting_schedule.get(day_name, [])
            
            scheduled_posts = []
            
            for slot in day_schedule:
                # Parse time
                time_str = slot["time"]
                hour, minute = map(int, time_str.split(":"))
                
                # Create scheduled datetime
                scheduled_datetime = date.replace(hour=hour, minute=minute, second=0, microsecond=0)
                
                # Only schedule future posts
                if scheduled_datetime > datetime.now():
                    # Generate content for the theme
                    posts = self.content_generator.generate_daily_content(date)
                    theme_posts = [p for p in posts if p["theme"] == slot["theme"]]
                    
                    if theme_posts:
                        content = theme_posts[0]["content"]
                    else:
                        # Fallback to generating themed content
                        themed_post = self.content_generator._generate_themed_post(slot["theme"], 1)
                        content = themed_post["content"]
                    
                    # Schedule the post
                    result = self.schedule_post(
                        content=content,
                        scheduled_time=scheduled_datetime,
                        post_type=slot["type"],
                        theme=slot["theme"]
                    )
                    
                    if result["success"]:
                        scheduled_posts.append({
                            "post_id": result["post_id"],
                            "time": scheduled_datetime.strftime("%H:%M"),
                            "theme": slot["theme"],
                            "content_preview": content[:50] + "..."
                        })
            
            return {
                "success": True,
                "date": date.strftime("%Y-%m-%d"),
                "scheduled_posts": scheduled_posts,
                "total_scheduled": len(scheduled_posts)
            }
            
        except Exception as e:
            logger.error(f"Error scheduling daily content: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def schedule_weekly_content(self, start_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Schedule content for an entire week.
        
        Args:
            start_date: Starting date for the week (defaults to next Monday)
            
        Returns:
            Summary of weekly schedule
        """
        try:
            if start_date is None:
                # Find next Monday
                today = datetime.now()
                days_ahead = 0 - today.weekday()  # 0 = Monday
                if days_ahead <= 0:  # Target day already happened this week
                    days_ahead += 7
                start_date = today + timedelta(days=days_ahead)
                start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
            
            weekly_schedule = {}
            total_scheduled = 0
            
            for i in range(7):  # 7 days in a week
                current_date = start_date + timedelta(days=i)
                day_result = self.schedule_daily_content(current_date)
                
                if day_result["success"]:
                    weekly_schedule[current_date.strftime("%Y-%m-%d")] = day_result["scheduled_posts"]
                    total_scheduled += day_result["total_scheduled"]
                else:
                    weekly_schedule[current_date.strftime("%Y-%m-%d")] = []
            
            return {
                "success": True,
                "week_start": start_date.strftime("%Y-%m-%d"),
                "schedule": weekly_schedule,
                "total_posts_scheduled": total_scheduled,
                "summary": self._generate_schedule_summary(weekly_schedule)
            }
            
        except Exception as e:
            logger.error(f"Error scheduling weekly content: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _generate_schedule_summary(self, weekly_schedule: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """Generate summary statistics for weekly schedule."""
        total_posts = sum(len(day_posts) for day_posts in weekly_schedule.values())
        
        theme_count = {}
        time_distribution = {}
        
        for day_posts in weekly_schedule.values():
            for post in day_posts:
                # Count themes
                theme = post["theme"]
                theme_count[theme] = theme_count.get(theme, 0) + 1
                
                # Count time slots
                hour = int(post["time"].split(":")[0])
                time_slot = "morning" if hour < 12 else "afternoon" if hour < 17 else "evening"
                time_distribution[time_slot] = time_distribution.get(time_slot, 0) + 1
        
        return {
            "total_posts": total_posts,
            "posts_per_day": round(total_posts / 7, 1),
            "theme_distribution": theme_count,
            "time_distribution": time_distribution
        }
    
    def get_scheduled_posts(self, days_ahead: int = 7) -> Dict[str, Any]:
        """
        Get all scheduled posts for the next N days.
        
        Args:
            days_ahead: Number of days to look ahead
            
        Returns:
            List of scheduled posts
        """
        try:
            cutoff_date = datetime.now() + timedelta(days=days_ahead)
            
            upcoming_posts = []
            for post in self.scheduled_posts.values():
                if (post.status == PostStatus.SCHEDULED and 
                    post.scheduled_time <= cutoff_date and
                    post.scheduled_time > datetime.now()):
                    
                    upcoming_posts.append({
                        "id": post.id,
                        "content": post.content[:100] + "..." if len(post.content) > 100 else post.content,
                        "theme": post.theme,
                        "scheduled_time": post.scheduled_time.isoformat(),
                        "time_until_post": str(post.scheduled_time - datetime.now()).split(".")[0],
                        "post_type": post.post_type
                    })
            
            # Sort by scheduled time
            upcoming_posts.sort(key=lambda x: x["scheduled_time"])
            
            return {
                "success": True,
                "upcoming_posts": upcoming_posts,
                "total_scheduled": len(upcoming_posts)
            }
            
        except Exception as e:
            logger.error(f"Error getting scheduled posts: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def cancel_scheduled_post(self, post_id: str) -> Dict[str, Any]:
        """
        Cancel a scheduled post.
        
        Args:
            post_id: ID of post to cancel
            
        Returns:
            Cancellation result
        """
        try:
            if post_id not in self.scheduled_posts:
                return {
                    "success": False,
                    "error": "Post not found"
                }
            
            post = self.scheduled_posts[post_id]
            
            if post.status != PostStatus.SCHEDULED:
                return {
                    "success": False,
                    "error": f"Cannot cancel post with status: {post.status.value}"
                }
            
            # Mark as cancelled
            post.status = PostStatus.CANCELLED
            
            logger.info(f"Post cancelled: {post_id}")
            
            return {
                "success": True,
                "message": "Post cancelled successfully",
                "post_id": post_id
            }
            
        except Exception as e:
            logger.error(f"Error cancelling post: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def reschedule_post(self, post_id: str, new_time: datetime) -> Dict[str, Any]:
        """
        Reschedule a post to a new time.
        
        Args:
            post_id: ID of post to reschedule
            new_time: New scheduled time
            
        Returns:
            Reschedule result
        """
        try:
            if post_id not in self.scheduled_posts:
                return {
                    "success": False,
                    "error": "Post not found"
                }
            
            post = self.scheduled_posts[post_id]
            
            if post.status != PostStatus.SCHEDULED:
                return {
                    "success": False,
                    "error": f"Cannot reschedule post with status: {post.status.value}"
                }
            
            if new_time <= datetime.now():
                return {
                    "success": False,
                    "error": "Cannot schedule post in the past"
                }
            
            old_time = post.scheduled_time
            post.scheduled_time = new_time
            
            logger.info(f"Post rescheduled: {post_id} from {old_time} to {new_time}")
            
            return {
                "success": True,
                "message": "Post rescheduled successfully",
                "post_id": post_id,
                "old_time": old_time.isoformat(),
                "new_time": new_time.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error rescheduling post: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def start_auto_posting(self, check_interval: int = 60) -> Dict[str, Any]:
        """
        Start the automatic posting service.
        
        Args:
            check_interval: How often to check for scheduled posts (seconds)
            
        Returns:
            Start result
        """
        try:
            if self.is_running:
                return {
                    "success": False,
                    "error": "Auto-posting is already running"
                }
            
            self.is_running = True
            self.scheduler_thread = threading.Thread(
                target=self._auto_posting_loop,
                args=(check_interval,),
                daemon=True
            )
            self.scheduler_thread.start()
            
            logger.info("Auto-posting service started")
            
            return {
                "success": True,
                "message": "Auto-posting service started",
                "check_interval": check_interval
            }
            
        except Exception as e:
            logger.error(f"Error starting auto-posting: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def stop_auto_posting(self) -> Dict[str, Any]:
        """Stop the automatic posting service."""
        try:
            if not self.is_running:
                return {
                    "success": False,
                    "error": "Auto-posting is not running"
                }
            
            self.is_running = False
            
            if self.scheduler_thread and self.scheduler_thread.is_alive():
                self.scheduler_thread.join(timeout=5)
            
            logger.info("Auto-posting service stopped")
            
            return {
                "success": True,
                "message": "Auto-posting service stopped"
            }
            
        except Exception as e:
            logger.error(f"Error stopping auto-posting: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _auto_posting_loop(self, check_interval: int):
        """Main loop for automatic posting service."""
        logger.info(f"Auto-posting loop started with {check_interval}s interval")
        
        while self.is_running:
            try:
                self._check_and_publish_scheduled_posts()
                
                # Sleep in smaller intervals to allow for responsive shutdown
                for _ in range(check_interval):
                    if not self.is_running:
                        break
                    threading.Event().wait(1)
                    
            except Exception as e:
                logger.error(f"Error in auto-posting loop: {e}")
                threading.Event().wait(10)  # Wait before retrying
        
        logger.info("Auto-posting loop terminated")
    
    def _check_and_publish_scheduled_posts(self):
        """Check for and publish any posts that are due."""
        current_time = datetime.now()
        
        posts_to_publish = []
        for post in self.scheduled_posts.values():
            if (post.status == PostStatus.SCHEDULED and 
                post.scheduled_time <= current_time):
                posts_to_publish.append(post)
        
        for post in posts_to_publish:
            self._publish_scheduled_post(post)
    
    def _publish_scheduled_post(self, post: ScheduledPost):
        """Publish a single scheduled post."""
        try:
            logger.info(f"Publishing scheduled post: {post.id}")
            
            # Attempt to publish
            result = self.facebook_manager.post_content(
                content=post.content,
                post_type=post.post_type
            )
            
            if result.get("success"):
                post.status = PostStatus.PUBLISHED
                logger.info(f"Post published successfully: {post.id}")
            else:
                post.attempts += 1
                post.last_error = result.get("error", "Unknown error")
                
                if post.attempts >= post.max_attempts:
                    post.status = PostStatus.FAILED
                    logger.error(f"Post failed after {post.max_attempts} attempts: {post.id}")
                else:
                    # Retry in 5 minutes
                    post.scheduled_time = datetime.now() + timedelta(minutes=5)
                    logger.warning(f"Post failed, retrying in 5 minutes: {post.id}")
                
        except Exception as e:
            post.attempts += 1
            post.last_error = str(e)
            
            if post.attempts >= post.max_attempts:
                post.status = PostStatus.FAILED
                logger.error(f"Post failed with exception after {post.max_attempts} attempts: {post.id} - {e}")
            else:
                post.scheduled_time = datetime.now() + timedelta(minutes=5)
                logger.warning(f"Post failed with exception, retrying: {post.id} - {e}")
    
    def get_posting_statistics(self) -> Dict[str, Any]:
        """Get statistics about posting performance."""
        try:
            total_posts = len(self.scheduled_posts)
            if total_posts == 0:
                return {
                    "success": True,
                    "statistics": {
                        "total_posts": 0,
                        "published": 0,
                        "scheduled": 0,
                        "failed": 0,
                        "cancelled": 0,
                        "success_rate": 0.0
                    }
                }
            
            status_counts = {}
            for status in PostStatus:
                status_counts[status.value] = sum(
                    1 for post in self.scheduled_posts.values() 
                    if post.status == status
                )
            
            published_count = status_counts["published"]
            failed_count = status_counts["failed"]
            
            success_rate = (published_count / (published_count + failed_count)) if (published_count + failed_count) > 0 else 0.0
            
            return {
                "success": True,
                "statistics": {
                    "total_posts": total_posts,
                    "published": status_counts["published"],
                    "scheduled": status_counts["scheduled"],
                    "failed": status_counts["failed"],
                    "cancelled": status_counts["cancelled"],
                    "success_rate": round(success_rate, 3)
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting posting statistics: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def optimize_posting_times(self, historical_data: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """
        Optimize posting times based on historical engagement data.
        
        Args:
            historical_data: Optional historical post performance data
            
        Returns:
            Optimized posting schedule recommendations
        """
        try:
            # For now, return the predefined optimal times
            # In production, this would analyze historical engagement data
            optimized_schedule = {}
            
            for day, times in self.optimal_times.items():
                optimized_schedule[day] = []
                for start_hour, end_hour in times:
                    # Pick the middle of the optimal window
                    optimal_hour = (start_hour + end_hour) // 2
                    optimized_schedule[day].append(f"{optimal_hour:02d}:00")
            
            recommendations = [
                "Post during peak engagement times for maximum reach",
                "Weekday morning posts (8-10am) perform well for motivation content",
                "Evening posts (5-7pm) are ideal for workout tips and engagement",
                "Weekend posts should be later in the day (10am-4pm)",
                "Avoid posting during late night hours (10pm-6am)"
            ]
            
            return {
                "success": True,
                "optimized_schedule": optimized_schedule,
                "recommendations": recommendations,
                "current_schedule": self.posting_schedule
            }
            
        except Exception as e:
            logger.error(f"Error optimizing posting times: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_scheduler_status(self) -> Dict[str, Any]:
        """Get current status of the scheduler."""
        return {
            "success": True,
            "status": {
                "auto_posting_enabled": self.is_running,
                "total_scheduled_posts": len([p for p in self.scheduled_posts.values() if p.status == PostStatus.SCHEDULED]),
                "next_post_time": self._get_next_post_time(),
                "failed_posts": len([p for p in self.scheduled_posts.values() if p.status == PostStatus.FAILED]),
                "published_today": self._get_posts_published_today()
            }
        }
    
    def _get_next_post_time(self) -> Optional[str]:
        """Get the time of the next scheduled post."""
        scheduled_posts = [
            p for p in self.scheduled_posts.values() 
            if p.status == PostStatus.SCHEDULED and p.scheduled_time > datetime.now()
        ]
        
        if not scheduled_posts:
            return None
        
        next_post = min(scheduled_posts, key=lambda p: p.scheduled_time)
        return next_post.scheduled_time.isoformat()
    
    def _get_posts_published_today(self) -> int:
        """Get count of posts published today."""
        today = datetime.now().date()
        return sum(
            1 for post in self.scheduled_posts.values()
            if (post.status == PostStatus.PUBLISHED and 
                post.scheduled_time.date() == today)
        )