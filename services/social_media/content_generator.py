"""
Content Generator for Social Media Management
Generates original content ideas, text posts, and optimizes content for engagement.
"""

import random
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)


class ContentGenerator:
    """Generate fitness-related content for social media posts."""
    
    def __init__(self, ai_client=None):
        """
        Initialize the content generator.
        
        Args:
            ai_client: AI client for advanced content generation (optional)
        """
        self.ai_client = ai_client
        self.content_themes = self._load_content_themes()
        self.viral_hooks = self._load_viral_hooks()
        self.posting_schedule = self._create_default_schedule()
    
    def _load_content_themes(self) -> Dict[str, List[str]]:
        """Load predefined content themes and ideas."""
        return {
            "motivation": [
                "Your only limit is your mind. Push through and make it happen! 💪",
                "Success isn't just about what you accomplish, but what you inspire others to do.",
                "The pain you feel today will be the strength you feel tomorrow.",
                "Every workout brings you one step closer to your goals. Keep going!",
                "Transform your challenges into your greatest victories."
            ],
            "workout_tips": [
                "💡 Pro Tip: Focus on form over speed. Quality reps build quality results!",
                "🏋️‍♂️ Try this: Add 30 seconds of rest between sets to maximize your next lift.",
                "🔥 Cardio hack: Interval training burns more calories than steady-state cardio.",
                "💪 Remember: Progressive overload is key to building muscle - gradually increase your weight!",
                "🎯 Target different muscle groups each day for optimal recovery and growth."
            ],
            "member_success": [
                "🌟 Member Spotlight: [Member Name] crushed their fitness goals this month!",
                "👏 Celebrating our amazing members who show up every day to better themselves!",
                "💪 From beginner to beast mode - watch our members transform their lives!",
                "🏆 Success Story: How [Member Name] lost 20 pounds and gained confidence!",
                "✨ Real results, real people, real inspiration - that's what Anytime Fitness is about!"
            ],
            "gym_promotions": [
                "🔥 Limited Time Offer: Join today and get your first month FREE!",
                "💪 New Year, New You - Start your fitness journey with us!",
                "🎯 Personal Training Special: Book a session and transform your workout!",
                "⏰ 24/7 Access means you can workout on YOUR schedule!",
                "🏋️‍♀️ Group Classes now available - find your fitness community!"
            ],
            "nutrition": [
                "🥗 Fuel your body right: Protein within 30 minutes post-workout!",
                "💧 Hydration Station: Aim for half your body weight in ounces of water daily.",
                "🍎 Prep for success: Meal prep Sunday sets you up for a healthy week!",
                "⚡ Pre-workout fuel: A banana and coffee can power your best session!",
                "🥑 Healthy fats aren't the enemy - avocados, nuts, and olive oil are your friends!"
            ],
            "challenges": [
                "30-Day Plank Challenge: Can you hold a plank for 2 minutes by month's end?",
                "Monday Motivation: Share your workout selfie and inspire others! #MondayMotivation",
                "Water Wednesday: Track your water intake and share your progress!",
                "Fitness Friday: What's your favorite exercise? Tell us in the comments!",
                "Weekend Warrior: How are you staying active this weekend?"
            ]
        }
    
    def _load_viral_hooks(self) -> List[str]:
        """Load viral hooks and engaging post starters."""
        return [
            "You won't believe what happened when...",
            "This one simple trick will...",
            "The secret that trainers don't want you to know...",
            "Before vs After: The transformation that shocked everyone...",
            "Stop doing this exercise wrong! Here's how...",
            "The 5-minute routine that changed everything...",
            "Why 99% of people fail at fitness (and how you won't)...",
            "This mistake is sabotaging your results...",
            "The game-changing mindset shift that...",
            "From couch to confident in just..."
        ]
    
    def _create_default_schedule(self) -> Dict[str, List[str]]:
        """Create a default posting schedule."""
        return {
            "monday": ["motivation", "workout_tips"],
            "tuesday": ["nutrition", "challenges"],
            "wednesday": ["member_success", "gym_promotions"],
            "thursday": ["workout_tips", "motivation"],
            "friday": ["challenges", "member_success"],
            "saturday": ["gym_promotions", "nutrition"],
            "sunday": ["motivation", "challenges"]
        }
    
    def generate_daily_content(self, date: Optional[datetime] = None) -> List[Dict[str, str]]:
        """
        Generate 2-3 posts for a specific day.
        
        Args:
            date: Date to generate content for (defaults to today)
            
        Returns:
            List of post dictionaries with content and metadata
        """
        if date is None:
            date = datetime.now()
        
        day_name = date.strftime('%A').lower()
        themes = self.posting_schedule.get(day_name, ["motivation", "workout_tips"])
        
        posts = []
        for i, theme in enumerate(themes[:3]):  # Max 3 posts per day
            post = self._generate_themed_post(theme, i + 1)
            posts.append(post)
        
        return posts
    
    def _generate_themed_post(self, theme: str, post_number: int) -> Dict[str, str]:
        """Generate a single themed post."""
        content_pool = self.content_themes.get(theme, self.content_themes["motivation"])
        base_content = random.choice(content_pool)
        
        # Add viral hook occasionally
        if random.random() < 0.3:  # 30% chance of viral hook
            hook = random.choice(self.viral_hooks)
            content = f"{hook} {base_content}"
        else:
            content = base_content
        
        # Add hashtags
        hashtags = self._generate_hashtags(theme)
        full_content = f"{content}\n\n{hashtags}"
        
        post = {
            "content": full_content,
            "theme": theme,
            "post_type": "text",
            "post_number": post_number,
            "timestamp": datetime.now().isoformat(),
            "engagement_potential": self._estimate_engagement_potential(content, theme)
        }
        
        return post
    
    def _generate_hashtags(self, theme: str) -> str:
        """Generate relevant hashtags for a theme."""
        base_hashtags = ["#AnytimeFitness", "#Fitness", "#Gym", "#Health"]
        
        theme_hashtags = {
            "motivation": ["#Motivation", "#FitnessMotivation", "#NeverGiveUp", "#StrongMind"],
            "workout_tips": ["#WorkoutTips", "#FitnessTips", "#Training", "#Exercise"],
            "member_success": ["#MemberSpotlight", "#Transformation", "#Success", "#Inspiration"],
            "gym_promotions": ["#JoinNow", "#FitnessOffer", "#GymMembership", "#FitnessJourney"],
            "nutrition": ["#Nutrition", "#HealthyEating", "#FuelYourBody", "#HealthyLife"],
            "challenges": ["#FitnessChallenge", "#Challenge", "#Community", "#FitnessGoals"]
        }
        
        tags = base_hashtags + theme_hashtags.get(theme, [])
        return " ".join(tags)
    
    def _estimate_engagement_potential(self, content: str, theme: str) -> str:
        """Estimate engagement potential based on content characteristics."""
        score = 0
        
        # Check for engagement factors
        if "?" in content:
            score += 2  # Questions drive engagement
        if any(emoji in content for emoji in ["💪", "🔥", "⚡", "🎯", "🏆", "✨"]):
            score += 1  # Emojis increase engagement
        if theme in ["challenges", "member_success"]:
            score += 2  # These themes typically perform well
        if len(content) < 200:
            score += 1  # Shorter posts often perform better
        
        if score >= 4:
            return "high"
        elif score >= 2:
            return "medium"
        else:
            return "low"
    
    def generate_ai_content(self, prompt: str, theme: str) -> Optional[str]:
        """
        Generate content using AI client if available.
        
        Args:
            prompt: Content prompt/idea
            theme: Content theme for context
            
        Returns:
            Generated content or None if AI not available
        """
        if not self.ai_client:
            logger.warning("AI client not available for content generation")
            return None
        
        try:
            enhanced_prompt = f"""
            Create an engaging social media post for Anytime Fitness gym about: {prompt}
            
            Theme: {theme}
            Requirements:
            - Keep it under 200 characters
            - Include relevant emojis
            - Make it motivational and action-oriented
            - Include a call-to-action or question to drive engagement
            - Sound authentic and personal
            """
            
            response = self.ai_client.generate_response(enhanced_prompt)
            return response
            
        except Exception as e:
            logger.error(f"AI content generation failed: {e}")
            return None
    
    def scan_trending_content(self) -> List[Dict[str, str]]:
        """
        Scan for trending fitness content (mock implementation).
        In production, this would analyze social media trends.
        """
        # Mock trending topics
        trending_topics = [
            {
                "trend": "15-minute morning workouts",
                "engagement_rate": "high",
                "adaptation": "Quick morning routine to start your day strong! Try our 15-minute express classes."
            },
            {
                "trend": "protein coffee recipes",
                "engagement_rate": "medium", 
                "adaptation": "Fuel your workout with protein coffee! Here's how to make the perfect pre-gym blend."
            },
            {
                "trend": "fitness accountability partners",
                "engagement_rate": "high",
                "adaptation": "Find your workout buddy at Anytime Fitness! Accountability makes all the difference."
            }
        ]
        
        logger.info(f"Found {len(trending_topics)} trending topics")
        return trending_topics
    
    def create_video_content_ideas(self) -> List[Dict[str, str]]:
        """Generate ideas for video content creation."""
        video_ideas = [
            {
                "type": "workout_demo",
                "title": "Perfect Squat Form in 60 Seconds",
                "description": "Quick tutorial showing proper squat technique",
                "length": "60 seconds",
                "equipment_needed": "None"
            },
            {
                "type": "member_transformation",
                "title": "6-Month Transformation Story",
                "description": "Member shares their fitness journey and results",
                "length": "2-3 minutes",
                "equipment_needed": "Before/after photos"
            },
            {
                "type": "gym_tour",
                "title": "24/7 Access Gym Tour",
                "description": "Show off gym facilities and equipment",
                "length": "90 seconds",
                "equipment_needed": "None"
            },
            {
                "type": "quick_tip",
                "title": "5 Exercises for Busy People",
                "description": "High-impact exercises for time-crunched schedules",
                "length": "45 seconds",
                "equipment_needed": "Basic gym equipment"
            }
        ]
        
        return video_ideas
    
    def get_posting_schedule(self, start_date: datetime, days: int = 7) -> Dict[str, List[Dict]]:
        """
        Generate a content schedule for multiple days.
        
        Args:
            start_date: Starting date for schedule
            days: Number of days to generate content for
            
        Returns:
            Dictionary mapping dates to lists of posts
        """
        schedule = {}
        
        for i in range(days):
            current_date = start_date + timedelta(days=i)
            date_str = current_date.strftime('%Y-%m-%d')
            daily_posts = self.generate_daily_content(current_date)
            schedule[date_str] = daily_posts
        
        logger.info(f"Generated content schedule for {days} days starting {start_date.strftime('%Y-%m-%d')}")
        return schedule