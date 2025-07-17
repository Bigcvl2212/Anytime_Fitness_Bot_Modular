"""
Facebook Manager for Social Media Management
Handles posting, engagement, and interaction with Facebook API.
"""

import logging
import time
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import json

from .mock_facebook_api import MockFacebookAPI

logger = logging.getLogger(__name__)


class FacebookManager:
    """
    Manages Facebook page interactions including posting, engagement, and monitoring.
    """
    
    def __init__(self, api_client=None, use_mock: bool = True, ai_client=None):
        """
        Initialize Facebook manager.
        
        Args:
            api_client: Real Facebook API client (for production)
            use_mock: Whether to use mock API for testing
            ai_client: AI client for generating responses
        """
        self.use_mock = use_mock
        self.ai_client = ai_client
        
        if use_mock or api_client is None:
            self.api = MockFacebookAPI()
            logger.info("Using Mock Facebook API for testing")
        else:
            self.api = api_client
            logger.info("Using real Facebook API")
        
        self.response_templates = self._load_response_templates()
        self.moderation_keywords = self._load_moderation_keywords()
    
    def _load_response_templates(self) -> Dict[str, List[str]]:
        """Load predefined response templates for common interactions."""
        return {
            "membership_inquiry": [
                "Thanks for your interest! We'd love to help you start your fitness journey. Please visit us or call for membership details! 💪",
                "Great question! Our team would be happy to discuss membership options with you. Drop by anytime or send us a message!",
                "Welcome to the Anytime Fitness community! Let's get you started - please reach out to our staff for membership info! 🏋️‍♂️"
            ],
            "class_schedule": [
                "Check out our class schedule on our website or app! We have something for everyone. 🏃‍♀️",
                "Great question! Our group fitness classes are updated weekly. Visit our website for the latest schedule! ⏰",
                "We offer various classes throughout the week! Check our schedule online or ask our staff when you visit! 💃"
            ],
            "hours_inquiry": [
                "We're open 24/7 for our members! That's the beauty of Anytime Fitness - workout on YOUR schedule! ⏰",
                "24 hours a day, 7 days a week! Your gym is always ready when you are! 🌙☀️",
                "Round-the-clock access! Whether you're an early bird or night owl, we're here for you! 🦉"
            ],
            "equipment_question": [
                "We have all the equipment you need for a great workout! Come check out our facilities anytime! 🏋️‍♀️",
                "Our gym is fully equipped with cardio machines, free weights, and strength training equipment! 💪",
                "From treadmills to dumbbells, we've got you covered! Stop by for a tour of our facilities! 🏃‍♂️"
            ],
            "positive_feedback": [
                "Thank you so much! We're thrilled to be part of your fitness journey! Keep up the amazing work! 🌟",
                "This made our day! Thanks for being such an awesome member of our community! 💪",
                "We appreciate you! Comments like this motivate us to keep providing the best fitness experience! 🙌"
            ],
            "complaint_concern": [
                "We sincerely apologize for your experience. Please send us a direct message so we can make this right! 🙏",
                "We take all feedback seriously. Please reach out to our manager directly so we can address your concerns! 📞",
                "Thank you for bringing this to our attention. We'd like to resolve this - please contact us directly! 💬"
            ],
            "general_support": [
                "Thanks for reaching out! Our team is here to help - feel free to message us anytime! 😊",
                "We're here to support your fitness goals! Don't hesitate to ask if you need anything! 💪",
                "Great to hear from you! Our staff is always ready to help make your workout experience the best! 🏋️‍♂️"
            ]
        }
    
    def _load_moderation_keywords(self) -> Dict[str, List[str]]:
        """Load keywords for content moderation and categorization."""
        return {
            "spam": ["buy now", "click here", "free money", "weight loss pills", "get rich"],
            "inappropriate": ["hate", "violence", "inappropriate language markers"],
            "membership": ["join", "membership", "price", "cost", "rate", "sign up"],
            "schedule": ["class", "schedule", "time", "when", "hours", "open"],
            "equipment": ["equipment", "machine", "weights", "treadmill", "gym"],
            "complaint": ["bad", "terrible", "worst", "awful", "disappointed", "unhappy"],
            "praise": ["great", "awesome", "love", "amazing", "best", "excellent"]
        }
    
    def post_content(self, content: str, post_type: str = "text", 
                    scheduled_time: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Post content to Facebook page.
        
        Args:
            content: Post content
            post_type: Type of post (text, image, video)
            scheduled_time: When to publish (None for immediate)
            
        Returns:
            Response with post details and success status
        """
        try:
            # Convert datetime to ISO string if provided
            scheduled_str = scheduled_time.isoformat() if scheduled_time else None
            
            response = self.api.create_post(
                content=content,
                post_type=post_type,
                scheduled_time=scheduled_str
            )
            
            if response.get("success"):
                logger.info(f"Post created successfully: {response.get('post_id')}")
                
                # Log post for analytics
                self._log_post_action("created", response.get('post_id'), {
                    "content_length": len(content),
                    "post_type": post_type,
                    "scheduled": scheduled_time is not None
                })
            else:
                logger.error(f"Failed to create post: {response.get('error')}")
            
            return response
            
        except Exception as e:
            logger.error(f"Error posting content: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def monitor_engagement(self, hours_back: int = 24) -> Dict[str, Any]:
        """
        Monitor recent posts for new comments and messages.
        
        Args:
            hours_back: How many hours back to check for engagement
            
        Returns:
            Summary of new engagement requiring attention
        """
        try:
            # Get recent posts
            posts_response = self.api.get_posts(limit=50)
            if not posts_response.get("success"):
                return {"success": False, "error": "Failed to fetch posts"}
            
            posts = posts_response.get("posts", [])
            
            # Filter posts from the specified time period
            cutoff_time = datetime.now() - timedelta(hours=hours_back)
            recent_posts = [
                post for post in posts
                if datetime.fromisoformat(post["timestamp"].replace('Z', '+00:00')) > cutoff_time
            ]
            
            engagement_summary = {
                "new_comments": [],
                "new_messages": [],
                "high_engagement_posts": [],
                "needs_response": []
            }
            
            # Check comments on recent posts
            for post in recent_posts:
                comments_response = self.api.get_post_comments(post["id"])
                if comments_response.get("success"):
                    comments = comments_response.get("comments", [])
                    
                    # Identify comments needing response
                    for comment in comments:
                        if self._needs_response(comment):
                            engagement_summary["new_comments"].append(comment)
                            engagement_summary["needs_response"].append({
                                "type": "comment",
                                "id": comment["id"],
                                "content": comment["content"],
                                "author": comment["author"],
                                "post_id": post["id"]
                            })
            
            # Check for new messages
            messages_response = self.api.get_messages(limit=25)
            if messages_response.get("success"):
                messages = messages_response.get("messages", [])
                
                for message in messages:
                    if not message.get("response_sent", False):
                        engagement_summary["new_messages"].append(message)
                        engagement_summary["needs_response"].append({
                            "type": "message",
                            "id": message["id"],
                            "content": message["content"],
                            "sender": message["sender"]
                        })
            
            # Identify high-engagement posts
            for post in recent_posts:
                engagement_rate = post.get("engagement_rate", 0)
                if engagement_rate > 0.05:  # 5% engagement rate threshold
                    engagement_summary["high_engagement_posts"].append(post)
            
            logger.info(f"Monitoring complete: {len(engagement_summary['needs_response'])} items need response")
            return {
                "success": True,
                "summary": engagement_summary,
                "monitoring_period_hours": hours_back
            }
            
        except Exception as e:
            logger.error(f"Error monitoring engagement: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _needs_response(self, comment: Dict[str, Any]) -> bool:
        """Determine if a comment needs a response."""
        content = comment.get("content", "").lower()
        
        # Check if it's a question
        if "?" in content:
            return True
        
        # Check for keywords that typically need responses
        response_keywords = [
            "help", "question", "info", "information", "price", "cost",
            "membership", "join", "sign up", "schedule", "class", "hours"
        ]
        
        return any(keyword in content for keyword in response_keywords)
    
    def respond_to_engagement(self, engagement_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Automatically respond to comments and messages.
        
        Args:
            engagement_items: List of engagement items needing response
            
        Returns:
            Summary of responses sent
        """
        responses_sent = {
            "comments": 0,
            "messages": 0,
            "failed": 0,
            "details": []
        }
        
        for item in engagement_items:
            try:
                response_content = self._generate_response(item)
                
                if item["type"] == "comment":
                    # Reply to comment
                    response = self.api.reply_to_comment(item["id"], response_content)
                    if response.get("success"):
                        responses_sent["comments"] += 1
                        responses_sent["details"].append({
                            "type": "comment_reply",
                            "item_id": item["id"],
                            "response": response_content
                        })
                    else:
                        responses_sent["failed"] += 1
                
                elif item["type"] == "message":
                    # Send direct message
                    response = self.api.send_message(item["sender"], response_content)
                    if response.get("success"):
                        responses_sent["messages"] += 1
                        responses_sent["details"].append({
                            "type": "message_reply",
                            "item_id": item["id"],
                            "response": response_content
                        })
                    else:
                        responses_sent["failed"] += 1
                
                # Add small delay between responses
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Error responding to engagement item {item.get('id')}: {e}")
                responses_sent["failed"] += 1
        
        logger.info(f"Responses sent: {responses_sent['comments']} comments, {responses_sent['messages']} messages")
        return {
            "success": True,
            "responses_sent": responses_sent
        }
    
    def _generate_response(self, engagement_item: Dict[str, Any]) -> str:
        """
        Generate appropriate response to engagement.
        
        Args:
            engagement_item: Comment or message to respond to
            
        Returns:
            Generated response content
        """
        content = engagement_item.get("content", "").lower()
        
        # Try AI generation first if available
        if self.ai_client:
            try:
                ai_response = self._generate_ai_response(engagement_item)
                if ai_response:
                    return ai_response
            except Exception as e:
                logger.warning(f"AI response generation failed: {e}")
        
        # Fall back to template-based responses
        return self._generate_template_response(content)
    
    def _generate_ai_response(self, engagement_item: Dict[str, Any]) -> Optional[str]:
        """Generate response using AI client."""
        if not self.ai_client:
            return None
        
        prompt = f"""
        You are a friendly customer service representative for Anytime Fitness gym.
        
        Someone {engagement_item['type']} said: "{engagement_item['content']}"
        
        Generate a helpful, friendly, and professional response that:
        - Addresses their question or comment appropriately
        - Maintains a positive, motivational tone
        - Encourages them to visit or contact the gym if needed
        - Is under 200 characters
        - Includes appropriate emojis
        
        Keep it conversational and authentic.
        """
        
        return self.ai_client.generate_response(prompt)
    
    def _generate_template_response(self, content: str) -> str:
        """Generate response using predefined templates."""
        # Categorize the content
        category = self._categorize_content(content)
        
        # Get appropriate template
        templates = self.response_templates.get(category, self.response_templates["general_support"])
        
        # Select random template to vary responses
        import random
        return random.choice(templates)
    
    def _categorize_content(self, content: str) -> str:
        """Categorize content to select appropriate response template."""
        content_lower = content.lower()
        
        # Check for specific keywords
        for category, keywords in self.moderation_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                # Map moderation categories to response categories
                if category == "membership":
                    return "membership_inquiry"
                elif category == "schedule":
                    return "class_schedule"
                elif category == "equipment":
                    return "equipment_question"
                elif category == "complaint":
                    return "complaint_concern"
                elif category == "praise":
                    return "positive_feedback"
        
        # Check for hours/schedule related content
        if any(word in content_lower for word in ["hour", "open", "close", "time", "24"]):
            return "hours_inquiry"
        
        # Default to general support
        return "general_support"
    
    def get_post_performance(self, post_id: str) -> Dict[str, Any]:
        """Get detailed performance metrics for a specific post."""
        try:
            response = self.api.get_post(post_id)
            if not response.get("success"):
                return response
            
            post = response.get("post")
            
            # Calculate additional metrics
            total_engagement = post["likes"] + post["comments"] + post["shares"]
            
            performance = {
                "post_id": post_id,
                "content": post["content"][:100] + "..." if len(post["content"]) > 100 else post["content"],
                "metrics": {
                    "likes": post["likes"],
                    "comments": post["comments"],
                    "shares": post["shares"],
                    "reach": post["reach"],
                    "engagement_rate": post["engagement_rate"],
                    "total_engagement": total_engagement
                },
                "performance_rating": self._rate_performance(post),
                "timestamp": post["timestamp"]
            }
            
            return {
                "success": True,
                "performance": performance
            }
            
        except Exception as e:
            logger.error(f"Error getting post performance: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _rate_performance(self, post: Dict[str, Any]) -> str:
        """Rate post performance as excellent, good, fair, or poor."""
        engagement_rate = post.get("engagement_rate", 0)
        reach = post.get("reach", 0)
        
        if engagement_rate >= 0.08 and reach >= 800:
            return "excellent"
        elif engagement_rate >= 0.05 and reach >= 500:
            return "good"
        elif engagement_rate >= 0.02 and reach >= 200:
            return "fair"
        else:
            return "poor"
    
    def _log_post_action(self, action: str, post_id: str, metadata: Dict[str, Any]):
        """Log post actions for analytics and monitoring."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "post_id": post_id,
            "metadata": metadata
        }
        
        # In production, this would log to a proper logging system or database
        logger.info(f"Post action logged: {action} for post {post_id}")
    
    def bulk_post_schedule(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Schedule multiple posts at once.
        
        Args:
            posts: List of post dictionaries with content and scheduled times
            
        Returns:
            Summary of scheduled posts
        """
        results = {
            "scheduled": 0,
            "failed": 0,
            "details": []
        }
        
        for post_data in posts:
            try:
                response = self.post_content(
                    content=post_data["content"],
                    post_type=post_data.get("post_type", "text"),
                    scheduled_time=post_data.get("scheduled_time")
                )
                
                if response.get("success"):
                    results["scheduled"] += 1
                    results["details"].append({
                        "post_id": response.get("post_id"),
                        "scheduled_time": post_data.get("scheduled_time"),
                        "status": "scheduled"
                    })
                else:
                    results["failed"] += 1
                    results["details"].append({
                        "content": post_data["content"][:50] + "...",
                        "error": response.get("error"),
                        "status": "failed"
                    })
                
            except Exception as e:
                results["failed"] += 1
                results["details"].append({
                    "content": post_data.get("content", "Unknown")[:50] + "...",
                    "error": str(e),
                    "status": "failed"
                })
        
        logger.info(f"Bulk scheduling complete: {results['scheduled']} scheduled, {results['failed']} failed")
        return {
            "success": True,
            "results": results
        }