"""
Mock Facebook API for Testing
Simulates Facebook API interactions for development and testing.
"""

import json
import logging
import random
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class MockPost:
    """Represents a Facebook post in the mock system."""
    id: str
    content: str
    post_type: str
    timestamp: str
    likes: int = 0
    comments: int = 0
    shares: int = 0
    reach: int = 0
    engagement_rate: float = 0.0
    status: str = "published"


@dataclass
class MockComment:
    """Represents a comment on a post."""
    id: str
    post_id: str
    author: str
    content: str
    timestamp: str
    sentiment: str = "neutral"  # positive, negative, neutral


@dataclass
class MockMessage:
    """Represents a direct message."""
    id: str
    sender: str
    content: str
    timestamp: str
    is_read: bool = False
    response_sent: bool = False


class MockFacebookAPI:
    """
    Mock Facebook API for testing social media management functionality.
    Simulates real Facebook API responses and behaviors.
    """
    
    def __init__(self, simulate_delays: bool = True):
        """
        Initialize the mock Facebook API.
        
        Args:
            simulate_delays: Whether to simulate network delays
        """
        self.simulate_delays = simulate_delays
        self.posts = {}  # Store posts by ID
        self.comments = {}  # Store comments by ID
        self.messages = {}  # Store messages by ID
        self.page_analytics = {
            "total_likes": 1250,
            "total_followers": 1180,
            "weekly_reach": 5000,
            "engagement_rate": 0.045
        }
        self.api_calls = []  # Log all API calls for testing
        
        # Initialize with some mock data
        self._initialize_mock_data()
    
    def _initialize_mock_data(self):
        """Initialize with some existing posts and comments for testing."""
        # Add some existing posts
        current_time = datetime.now()
        sample_posts = [
            {
                "id": "mock_post_1",
                "content": "Welcome to Anytime Fitness! Your journey starts here! 💪 #AnytimeFitness",
                "post_type": "text",
                "timestamp": (current_time - timedelta(hours=2)).isoformat() + "Z",
                "likes": 45,
                "comments": 8,
                "shares": 3,
                "reach": 890
            },
            {
                "id": "mock_post_2", 
                "content": "Workout tip: Focus on form over speed! Quality reps build quality results! 🏋️‍♂️",
                "post_type": "text",
                "timestamp": (current_time - timedelta(hours=5)).isoformat() + "Z",
                "likes": 32,
                "comments": 5,
                "shares": 7,
                "reach": 650
            }
        ]
        
        for post_data in sample_posts:
            post = MockPost(**post_data)
            post.engagement_rate = self._calculate_engagement_rate(post)
            self.posts[post.id] = post
        
        # Add some mock comments
        sample_comments = [
            {
                "id": "comment_1",
                "post_id": "mock_post_1",
                "author": "John Doe",
                "content": "Great motivation! Just signed up!",
                "timestamp": (current_time - timedelta(minutes=30)).isoformat() + "Z",
                "sentiment": "positive"
            },
            {
                "id": "comment_2",
                "post_id": "mock_post_1", 
                "author": "Jane Smith",
                "content": "What are your membership rates?",
                "timestamp": (current_time - timedelta(minutes=15)).isoformat() + "Z",
                "sentiment": "neutral"
            }
        ]
        
        for comment_data in sample_comments:
            comment = MockComment(**comment_data)
            self.comments[comment.id] = comment
        
        # Add some mock messages
        sample_messages = [
            {
                "id": "msg_1",
                "sender": "Mike Johnson",
                "content": "Hi, I'm interested in personal training sessions. What are your rates?",
                "timestamp": (current_time - timedelta(hours=1)).isoformat() + "Z",
                "is_read": False
            }
        ]
        
        for msg_data in sample_messages:
            message = MockMessage(**msg_data)
            self.messages[message.id] = message
    
    def _simulate_delay(self):
        """Simulate API response delay."""
        if self.simulate_delays:
            time.sleep(random.uniform(0.1, 0.5))  # 100-500ms delay
    
    def _log_api_call(self, method: str, endpoint: str, data: Any = None):
        """Log API call for testing verification."""
        call = {
            "method": method,
            "endpoint": endpoint,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        self.api_calls.append(call)
        logger.info(f"Mock API: {method} {endpoint}")
    
    def _calculate_engagement_rate(self, post: MockPost) -> float:
        """Calculate engagement rate for a post."""
        if post.reach == 0:
            return 0.0
        
        total_engagements = post.likes + post.comments + post.shares
        return round(total_engagements / post.reach, 4)
    
    def create_post(self, content: str, post_type: str = "text", 
                   scheduled_time: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new Facebook post.
        
        Args:
            content: Post content
            post_type: Type of post (text, image, video)
            scheduled_time: When to publish (None for immediate)
            
        Returns:
            Response with post details
        """
        self._simulate_delay()
        self._log_api_call("POST", "/posts", {"content": content, "type": post_type})
        
        # Generate unique post ID
        post_id = f"mock_post_{len(self.posts) + 1}_{int(time.time())}"
        
        # Create post
        post = MockPost(
            id=post_id,
            content=content,
            post_type=post_type,
            timestamp=scheduled_time or datetime.now().isoformat(),
            status="scheduled" if scheduled_time else "published"
        )
        
        self.posts[post_id] = post
        
        # Simulate initial engagement after a few seconds for published posts
        if not scheduled_time:
            self._simulate_initial_engagement(post_id)
        
        return {
            "success": True,
            "post_id": post_id,
            "status": post.status,
            "message": "Post created successfully"
        }
    
    def _simulate_initial_engagement(self, post_id: str):
        """Simulate realistic initial engagement on a new post."""
        post = self.posts.get(post_id)
        if not post:
            return
        
        # Simulate realistic engagement numbers
        post.likes = random.randint(5, 50)
        post.comments = random.randint(0, 8)
        post.shares = random.randint(0, 5)
        post.reach = random.randint(200, 1000)
        post.engagement_rate = self._calculate_engagement_rate(post)
    
    def get_post(self, post_id: str) -> Dict[str, Any]:
        """Get details of a specific post."""
        self._simulate_delay()
        self._log_api_call("GET", f"/posts/{post_id}")
        
        post = self.posts.get(post_id)
        if not post:
            return {
                "success": False,
                "error": "Post not found"
            }
        
        return {
            "success": True,
            "post": asdict(post)
        }
    
    def get_posts(self, limit: int = 25) -> Dict[str, Any]:
        """Get list of recent posts."""
        self._simulate_delay()
        self._log_api_call("GET", f"/posts?limit={limit}")
        
        # Sort posts by timestamp (newest first)
        sorted_posts = sorted(
            self.posts.values(),
            key=lambda p: p.timestamp,
            reverse=True
        )
        
        limited_posts = sorted_posts[:limit]
        
        return {
            "success": True,
            "posts": [asdict(post) for post in limited_posts],
            "total": len(self.posts)
        }
    
    def get_post_comments(self, post_id: str) -> Dict[str, Any]:
        """Get comments for a specific post."""
        self._simulate_delay()
        self._log_api_call("GET", f"/posts/{post_id}/comments")
        
        post_comments = [
            comment for comment in self.comments.values()
            if comment.post_id == post_id
        ]
        
        return {
            "success": True,
            "comments": [asdict(comment) for comment in post_comments]
        }
    
    def reply_to_comment(self, comment_id: str, reply_content: str) -> Dict[str, Any]:
        """Reply to a comment on a post."""
        self._simulate_delay()
        self._log_api_call("POST", f"/comments/{comment_id}/reply", {"content": reply_content})
        
        comment = self.comments.get(comment_id)
        if not comment:
            return {
                "success": False,
                "error": "Comment not found"
            }
        
        # Create reply (simplified - just log it)
        reply_id = f"reply_{comment_id}_{int(time.time())}"
        
        return {
            "success": True,
            "reply_id": reply_id,
            "message": "Reply posted successfully"
        }
    
    def get_messages(self, limit: int = 25) -> Dict[str, Any]:
        """Get direct messages."""
        self._simulate_delay()
        self._log_api_call("GET", f"/messages?limit={limit}")
        
        # Sort messages by timestamp (newest first)
        sorted_messages = sorted(
            self.messages.values(),
            key=lambda m: m.timestamp,
            reverse=True
        )
        
        limited_messages = sorted_messages[:limit]
        
        return {
            "success": True,
            "messages": [asdict(msg) for msg in limited_messages]
        }
    
    def send_message(self, recipient: str, content: str) -> Dict[str, Any]:
        """Send a direct message."""
        self._simulate_delay()
        self._log_api_call("POST", "/messages", {"recipient": recipient, "content": content})
        
        message_id = f"sent_msg_{int(time.time())}"
        
        return {
            "success": True,
            "message_id": message_id,
            "message": "Message sent successfully"
        }
    
    def get_page_analytics(self, period: str = "week") -> Dict[str, Any]:
        """Get page analytics and insights."""
        self._simulate_delay()
        self._log_api_call("GET", f"/insights?period={period}")
        
        # Simulate analytics data with some variation
        base_analytics = self.page_analytics.copy()
        
        # Add some random variation to simulate real data
        if period == "week":
            base_analytics["weekly_reach"] = random.randint(4000, 6000)
            base_analytics["engagement_rate"] = round(random.uniform(0.03, 0.06), 4)
        elif period == "month":
            base_analytics["monthly_reach"] = random.randint(15000, 25000)
            base_analytics["new_followers"] = random.randint(50, 150)
        
        return {
            "success": True,
            "analytics": base_analytics,
            "period": period
        }
    
    def get_ad_performance(self, ad_id: Optional[str] = None) -> Dict[str, Any]:
        """Get advertising performance data."""
        self._simulate_delay()
        endpoint = f"/ads/{ad_id}" if ad_id else "/ads"
        self._log_api_call("GET", endpoint)
        
        # Mock ad performance data
        ad_data = {
            "ad_id": ad_id or "mock_ad_123",
            "impressions": random.randint(1000, 5000),
            "clicks": random.randint(50, 200),
            "cost": round(random.uniform(25.0, 100.0), 2),
            "conversions": random.randint(2, 15),
            "ctr": round(random.uniform(0.02, 0.08), 4),
            "cpc": round(random.uniform(0.50, 2.00), 2)
        }
        
        return {
            "success": True,
            "ad_performance": ad_data
        }
    
    def moderate_content(self, content_id: str, action: str) -> Dict[str, Any]:
        """Moderate content (hide, delete, approve)."""
        self._simulate_delay()
        self._log_api_call("POST", f"/moderate/{content_id}", {"action": action})
        
        return {
            "success": True,
            "action": action,
            "content_id": content_id,
            "message": f"Content {action} successfully"
        }
    
    def get_api_call_log(self) -> List[Dict[str, Any]]:
        """Get log of all API calls made (for testing)."""
        return self.api_calls.copy()
    
    def reset_mock_data(self):
        """Reset all mock data (useful for testing)."""
        self.posts.clear()
        self.comments.clear() 
        self.messages.clear()
        self.api_calls.clear()
        self._initialize_mock_data()
        logger.info("Mock data reset successfully")
    
    def simulate_new_message(self, sender: str, content: str) -> str:
        """Simulate receiving a new message (for testing)."""
        message_id = f"sim_msg_{int(time.time())}"
        message = MockMessage(
            id=message_id,
            sender=sender,
            content=content,
            timestamp=datetime.now().isoformat()
        )
        self.messages[message_id] = message
        logger.info(f"Simulated new message from {sender}")
        return message_id
    
    def simulate_new_comment(self, post_id: str, author: str, content: str) -> str:
        """Simulate receiving a new comment (for testing)."""
        comment_id = f"sim_comment_{int(time.time())}"
        comment = MockComment(
            id=comment_id,
            post_id=post_id,
            author=author,
            content=content,
            timestamp=datetime.now().isoformat()
        )
        self.comments[comment_id] = comment
        logger.info(f"Simulated new comment on post {post_id}")
        return comment_id