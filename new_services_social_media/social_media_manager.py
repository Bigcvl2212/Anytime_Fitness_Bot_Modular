"""
Social Media Manager - Main service for managing gym social media channels
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

@dataclass
class SocialMediaAccount:
    """Represents a connected social media account."""
    platform: str
    account_id: str
    account_name: str
    is_connected: bool
    last_sync: Optional[str] = None
    followers_count: int = 0
    posts_count: int = 0

@dataclass
class SocialMediaPost:
    """Represents a social media post."""
    id: str
    platform: str
    content: str
    scheduled_time: str
    status: str  # draft, scheduled, published, failed
    media_urls: List[str]
    tags: List[str]
    engagement_metrics: Dict[str, int]

class SocialMediaManager:
    """Main service for managing social media operations."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.connected_accounts = []
        self.scheduled_posts = []
        
        # Initialize with demo data for testing
        self._init_demo_data()
    
    def _init_demo_data(self):
        """Initialize with demo data for testing purposes."""
        self.connected_accounts = [
            SocialMediaAccount(
                platform="facebook",
                account_id="fb_123456",
                account_name="Anytime Fitness Demo Gym",
                is_connected=True,
                last_sync=datetime.now().isoformat(),
                followers_count=1250,
                posts_count=89
            ),
            SocialMediaAccount(
                platform="instagram",
                account_id="ig_789012",
                account_name="@anytimefitnessdemo",
                is_connected=True,
                last_sync=datetime.now().isoformat(),
                followers_count=2100,
                posts_count=156
            ),
            SocialMediaAccount(
                platform="twitter",
                account_id="tw_345678",
                account_name="@AFDemoGym",
                is_connected=False,
                followers_count=0,
                posts_count=0
            )
        ]
        
        self.scheduled_posts = [
            SocialMediaPost(
                id="post_001",
                platform="facebook",
                content="💪 New week, new goals! Join us for our Monday motivation workout at 6 AM. #MondayMotivation #AnytimeFitness",
                scheduled_time=(datetime.now() + timedelta(days=1)).isoformat(),
                status="scheduled",
                media_urls=["https://example.com/workout_image.jpg"],
                tags=["MondayMotivation", "AnytimeFitness", "Workout"],
                engagement_metrics={"likes": 0, "shares": 0, "comments": 0}
            ),
            SocialMediaPost(
                id="post_002",
                platform="instagram",
                content="🏋️‍♀️ Member spotlight: Sarah's incredible 6-month transformation! 👏 #MemberSpotlight #Transformation",
                scheduled_time=(datetime.now() + timedelta(days=2)).isoformat(),
                status="scheduled",
                media_urls=["https://example.com/transformation.jpg"],
                tags=["MemberSpotlight", "Transformation", "Fitness"],
                engagement_metrics={"likes": 0, "shares": 0, "comments": 0}
            )
        ]
    
    def get_connected_accounts(self) -> List[Dict[str, Any]]:
        """Get all connected social media accounts."""
        return [asdict(account) for account in self.connected_accounts]
    
    def connect_account(self, platform: str, account_data: Dict[str, Any]) -> bool:
        """Connect a new social media account."""
        try:
            new_account = SocialMediaAccount(
                platform=platform,
                account_id=account_data.get('account_id', ''),
                account_name=account_data.get('account_name', ''),
                is_connected=True,
                last_sync=datetime.now().isoformat()
            )
            self.connected_accounts.append(new_account)
            self.logger.info(f"Connected {platform} account: {new_account.account_name}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect {platform} account: {e}")
            return False
    
    def get_scheduled_posts(self) -> List[Dict[str, Any]]:
        """Get all scheduled posts."""
        return [asdict(post) for post in self.scheduled_posts]
    
    def schedule_post(self, post_data: Dict[str, Any]) -> str:
        """Schedule a new social media post."""
        try:
            post_id = f"post_{len(self.scheduled_posts) + 1:03d}"
            new_post = SocialMediaPost(
                id=post_id,
                platform=post_data.get('platform', ''),
                content=post_data.get('content', ''),
                scheduled_time=post_data.get('scheduled_time', ''),
                status='scheduled',
                media_urls=post_data.get('media_urls', []),
                tags=post_data.get('tags', []),
                engagement_metrics={"likes": 0, "shares": 0, "comments": 0}
            )
            self.scheduled_posts.append(new_post)
            self.logger.info(f"Scheduled post {post_id} for {new_post.platform}")
            return post_id
        except Exception as e:
            self.logger.error(f"Failed to schedule post: {e}")
            return ""
    
    def get_engagement_overview(self) -> Dict[str, Any]:
        """Get overview of engagement metrics across all platforms."""
        total_followers = sum(account.followers_count for account in self.connected_accounts if account.is_connected)
        total_posts = sum(account.posts_count for account in self.connected_accounts if account.is_connected)
        connected_platforms = len([acc for acc in self.connected_accounts if acc.is_connected])
        
        # Calculate recent engagement (demo data)
        recent_engagement = {
            "total_likes": 342,
            "total_shares": 67,
            "total_comments": 89,
            "engagement_rate": 4.2,
            "reach": 8500,
            "impressions": 15600
        }
        
        return {
            "total_followers": total_followers,
            "total_posts": total_posts,
            "connected_platforms": connected_platforms,
            "scheduled_posts": len([post for post in self.scheduled_posts if post.status == 'scheduled']),
            "recent_engagement": recent_engagement,
            "top_performing_content": [
                {"content": "New equipment arrival!", "engagement": 156},
                {"content": "Member transformation story", "engagement": 134},
                {"content": "Group class highlight", "engagement": 98}
            ]
        }
    
    def get_content_recommendations(self) -> List[Dict[str, Any]]:
        """Get AI-powered content recommendations."""
        recommendations = [
            {
                "type": "member_spotlight",
                "title": "Feature Member Success Story",
                "description": "Share a transformation story to inspire others",
                "suggested_time": "Tuesday 10:00 AM",
                "expected_engagement": "High",
                "template": "🌟 Member Spotlight: [Name]'s amazing [timeframe] journey! [achievement] 💪 #MemberSpotlight #Transformation"
            },
            {
                "type": "workout_tip",
                "title": "Share Workout Tip",
                "description": "Post a quick fitness tip or exercise demonstration",
                "suggested_time": "Wednesday 7:00 AM",
                "expected_engagement": "Medium",
                "template": "💡 Fitness Tip: [tip content] Try this today! #FitnessTip #HealthyLiving"
            }
        ]
        
        return recommendations

# Global instance
social_media_manager = SocialMediaManager()

def get_social_media_manager() -> SocialMediaManager:
    """Get the global social media manager instance."""
    return social_media_manager