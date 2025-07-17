"""
Social Media Analytics Module
Tracks performance, analyzes engagement, and provides optimization insights.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import json
import statistics

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Data class for post performance metrics."""
    post_id: str
    content_type: str
    theme: str
    likes: int
    comments: int
    shares: int
    reach: int
    engagement_rate: float
    timestamp: str
    performance_score: float = 0.0


@dataclass
class OptimizationInsight:
    """Data class for optimization insights."""
    insight_type: str
    description: str
    recommendation: str
    confidence: float
    impact: str  # high, medium, low


class SocialMediaAnalytics:
    """
    Analytics engine for social media performance tracking and optimization.
    """
    
    def __init__(self, facebook_manager):
        """
        Initialize analytics with Facebook manager.
        
        Args:
            facebook_manager: FacebookManager instance for data access
        """
        self.facebook_manager = facebook_manager
        self.performance_history = []
        self.optimization_rules = self._load_optimization_rules()
        self.benchmark_metrics = self._load_benchmark_metrics()
    
    def _load_optimization_rules(self) -> Dict[str, Any]:
        """Load rules for content optimization analysis."""
        return {
            "engagement_thresholds": {
                "excellent": 0.08,
                "good": 0.05,
                "fair": 0.02,
                "poor": 0.01
            },
            "reach_thresholds": {
                "excellent": 1000,
                "good": 600,
                "fair": 300,
                "poor": 100
            },
            "optimal_post_times": {
                "weekday_morning": {"start": 8, "end": 10, "multiplier": 1.2},
                "weekday_evening": {"start": 17, "end": 19, "multiplier": 1.3},
                "weekend_afternoon": {"start": 13, "end": 16, "multiplier": 1.1}
            },
            "content_length": {
                "optimal_min": 50,
                "optimal_max": 200,
                "penalty_factor": 0.1
            },
            "emoji_impact": 0.15,  # 15% boost for posts with emojis
            "question_impact": 0.25,  # 25% boost for posts with questions
            "hashtag_optimal": {"min": 3, "max": 8}
        }
    
    def _load_benchmark_metrics(self) -> Dict[str, float]:
        """Load industry benchmark metrics for comparison."""
        return {
            "fitness_industry_engagement_rate": 0.045,
            "small_business_engagement_rate": 0.038,
            "average_reach_per_follower": 0.35,
            "optimal_posting_frequency": 2.5,  # posts per day
            "response_time_target": 2.0  # hours
        }
    
    def analyze_post_performance(self, post_id: str) -> Dict[str, Any]:
        """
        Analyze individual post performance with detailed insights.
        
        Args:
            post_id: ID of the post to analyze
            
        Returns:
            Comprehensive performance analysis
        """
        try:
            # Get post performance data
            perf_response = self.facebook_manager.get_post_performance(post_id)
            if not perf_response.get("success"):
                return perf_response
            
            performance = perf_response.get("performance")
            metrics = performance.get("metrics")
            
            # Create performance metrics object
            perf_metrics = PerformanceMetrics(
                post_id=post_id,
                content_type="text",  # Would be determined from post data
                theme="unknown",      # Would be determined from content analysis
                likes=metrics["likes"],
                comments=metrics["comments"],
                shares=metrics["shares"],
                reach=metrics["reach"],
                engagement_rate=metrics["engagement_rate"],
                timestamp=performance["timestamp"]
            )
            
            # Calculate performance score
            perf_metrics.performance_score = self._calculate_performance_score(perf_metrics)
            
            # Generate insights
            insights = self._generate_performance_insights(perf_metrics, performance.get("content", ""))
            
            # Compare to benchmarks
            benchmark_comparison = self._compare_to_benchmarks(perf_metrics)
            
            analysis = {
                "post_id": post_id,
                "performance_metrics": {
                    "engagement_rate": perf_metrics.engagement_rate,
                    "reach": perf_metrics.reach,
                    "total_engagement": perf_metrics.likes + perf_metrics.comments + perf_metrics.shares,
                    "performance_score": perf_metrics.performance_score,
                    "rating": performance.get("performance_rating")
                },
                "benchmark_comparison": benchmark_comparison,
                "insights": insights,
                "recommendations": self._generate_recommendations(perf_metrics, insights)
            }
            
            # Store for historical analysis
            self.performance_history.append(perf_metrics)
            
            return {
                "success": True,
                "analysis": analysis
            }
            
        except Exception as e:
            logger.error(f"Error analyzing post performance: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _calculate_performance_score(self, metrics: PerformanceMetrics) -> float:
        """
        Calculate a comprehensive performance score (0-100).
        
        Args:
            metrics: Performance metrics for the post
            
        Returns:
            Performance score between 0 and 100
        """
        score = 0.0
        
        # Engagement rate component (40% of score)
        engagement_score = min(metrics.engagement_rate / 0.1, 1.0) * 40
        score += engagement_score
        
        # Reach component (30% of score)
        reach_score = min(metrics.reach / 1500, 1.0) * 30
        score += reach_score
        
        # Individual engagement metrics (30% of score)
        likes_score = min(metrics.likes / 100, 1.0) * 10
        comments_score = min(metrics.comments / 20, 1.0) * 15  # Comments weighted higher
        shares_score = min(metrics.shares / 10, 1.0) * 5
        score += likes_score + comments_score + shares_score
        
        return round(score, 2)
    
    def _generate_performance_insights(self, metrics: PerformanceMetrics, content: str) -> List[Dict[str, Any]]:
        """Generate specific insights about post performance."""
        insights = []
        
        # Engagement rate insights
        if metrics.engagement_rate >= self.optimization_rules["engagement_thresholds"]["excellent"]:
            insights.append({
                "type": "positive",
                "category": "engagement",
                "message": "Excellent engagement rate! This content resonated well with your audience.",
                "metric_value": metrics.engagement_rate
            })
        elif metrics.engagement_rate <= self.optimization_rules["engagement_thresholds"]["poor"]:
            insights.append({
                "type": "improvement",
                "category": "engagement", 
                "message": "Low engagement rate. Consider more interactive content or posting at peak times.",
                "metric_value": metrics.engagement_rate
            })
        
        # Reach insights
        if metrics.reach >= self.optimization_rules["reach_thresholds"]["excellent"]:
            insights.append({
                "type": "positive",
                "category": "reach",
                "message": "Great reach! Your content is being seen by a wide audience.",
                "metric_value": metrics.reach
            })
        elif metrics.reach <= self.optimization_rules["reach_thresholds"]["poor"]:
            insights.append({
                "type": "improvement",
                "category": "reach",
                "message": "Limited reach. Consider using trending hashtags or posting when followers are active.",
                "metric_value": metrics.reach
            })
        
        # Content-specific insights
        content_insights = self._analyze_content_factors(content)
        insights.extend(content_insights)
        
        # Timing insights
        timing_insight = self._analyze_posting_time(metrics.timestamp)
        if timing_insight:
            insights.append(timing_insight)
        
        return insights
    
    def _analyze_content_factors(self, content: str) -> List[Dict[str, Any]]:
        """Analyze content characteristics that impact performance."""
        insights = []
        
        # Content length analysis
        content_length = len(content)
        optimal_min = self.optimization_rules["content_length"]["optimal_min"]
        optimal_max = self.optimization_rules["content_length"]["optimal_max"]
        
        if content_length < optimal_min:
            insights.append({
                "type": "improvement",
                "category": "content_length",
                "message": f"Content is quite short ({content_length} characters). Consider adding more detail or context.",
                "metric_value": content_length
            })
        elif content_length > optimal_max:
            insights.append({
                "type": "improvement", 
                "category": "content_length",
                "message": f"Content is quite long ({content_length} characters). Shorter posts often perform better.",
                "metric_value": content_length
            })
        
        # Emoji analysis
        emoji_count = sum(1 for char in content if ord(char) > 127)  # Simple emoji detection
        if emoji_count == 0:
            insights.append({
                "type": "suggestion",
                "category": "emojis",
                "message": "Consider adding emojis to make your content more engaging and visually appealing.",
                "metric_value": emoji_count
            })
        
        # Question analysis
        if "?" in content:
            insights.append({
                "type": "positive",
                "category": "engagement",
                "message": "Great use of questions! This encourages audience interaction.",
                "metric_value": content.count("?")
            })
        
        # Hashtag analysis
        hashtag_count = content.count("#")
        optimal_min = self.optimization_rules["hashtag_optimal"]["min"]
        optimal_max = self.optimization_rules["hashtag_optimal"]["max"]
        
        if hashtag_count < optimal_min:
            insights.append({
                "type": "suggestion",
                "category": "hashtags",
                "message": f"Consider adding more hashtags ({hashtag_count} used, {optimal_min}-{optimal_max} recommended).",
                "metric_value": hashtag_count
            })
        elif hashtag_count > optimal_max:
            insights.append({
                "type": "improvement",
                "category": "hashtags", 
                "message": f"Too many hashtags ({hashtag_count} used). {optimal_min}-{optimal_max} is optimal.",
                "metric_value": hashtag_count
            })
        
        return insights
    
    def _analyze_posting_time(self, timestamp: str) -> Optional[Dict[str, Any]]:
        """Analyze if post was published at an optimal time."""
        try:
            post_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            hour = post_time.hour
            weekday = post_time.weekday()  # 0 = Monday, 6 = Sunday
            
            # Check against optimal posting times
            optimal_times = self.optimization_rules["optimal_post_times"]
            
            is_optimal = False
            time_category = ""
            
            if weekday < 5:  # Weekday
                if optimal_times["weekday_morning"]["start"] <= hour <= optimal_times["weekday_morning"]["end"]:
                    is_optimal = True
                    time_category = "weekday morning"
                elif optimal_times["weekday_evening"]["start"] <= hour <= optimal_times["weekday_evening"]["end"]:
                    is_optimal = True
                    time_category = "weekday evening"
            else:  # Weekend
                if optimal_times["weekend_afternoon"]["start"] <= hour <= optimal_times["weekend_afternoon"]["end"]:
                    is_optimal = True
                    time_category = "weekend afternoon"
            
            if is_optimal:
                return {
                    "type": "positive",
                    "category": "timing",
                    "message": f"Posted at an optimal time ({time_category})!",
                    "metric_value": hour
                }
            else:
                return {
                    "type": "suggestion",
                    "category": "timing",
                    "message": "Consider posting during peak engagement times (8-10am or 5-7pm on weekdays).",
                    "metric_value": hour
                }
                
        except Exception as e:
            logger.warning(f"Could not analyze posting time: {e}")
            return None
    
    def _compare_to_benchmarks(self, metrics: PerformanceMetrics) -> Dict[str, Any]:
        """Compare performance to industry benchmarks."""
        fitness_benchmark = self.benchmark_metrics["fitness_industry_engagement_rate"]
        general_benchmark = self.benchmark_metrics["small_business_engagement_rate"]
        
        comparison = {
            "vs_fitness_industry": {
                "performance": metrics.engagement_rate / fitness_benchmark,
                "status": "above" if metrics.engagement_rate > fitness_benchmark else "below",
                "difference": round((metrics.engagement_rate - fitness_benchmark) * 100, 2)
            },
            "vs_small_business": {
                "performance": metrics.engagement_rate / general_benchmark,
                "status": "above" if metrics.engagement_rate > general_benchmark else "below", 
                "difference": round((metrics.engagement_rate - general_benchmark) * 100, 2)
            },
            "benchmarks": {
                "fitness_industry_avg": fitness_benchmark,
                "small_business_avg": general_benchmark,
                "your_performance": metrics.engagement_rate
            }
        }
        
        return comparison
    
    def _generate_recommendations(self, metrics: PerformanceMetrics, insights: List[Dict[str, Any]]) -> List[str]:
        """Generate actionable recommendations based on analysis."""
        recommendations = []
        
        # Performance-based recommendations
        if metrics.performance_score < 30:
            recommendations.append("Consider revising content strategy - current performance is below expectations")
        
        # Insight-based recommendations
        improvement_insights = [i for i in insights if i.get("type") == "improvement"]
        suggestion_insights = [i for i in insights if i.get("type") == "suggestion"]
        
        for insight in improvement_insights[:2]:  # Top 2 improvements
            if insight["category"] == "engagement":
                recommendations.append("Try posts with questions or calls-to-action to boost engagement")
            elif insight["category"] == "reach":
                recommendations.append("Use trending hashtags and post during peak hours to increase reach")
            elif insight["category"] == "content_length":
                recommendations.append("Optimize content length to 50-200 characters for better performance")
        
        for insight in suggestion_insights[:2]:  # Top 2 suggestions
            if insight["category"] == "emojis":
                recommendations.append("Add relevant emojis to make content more visually appealing")
            elif insight["category"] == "hashtags":
                recommendations.append("Include 3-8 relevant hashtags to improve discoverability")
            elif insight["category"] == "timing":
                recommendations.append("Post during peak engagement times (8-10am or 5-7pm weekdays)")
        
        # General recommendations
        if len(recommendations) == 0:
            recommendations.append("Continue current content strategy - performance is meeting expectations")
        
        return recommendations[:4]  # Limit to top 4 recommendations
    
    def generate_weekly_report(self, weeks_back: int = 1) -> Dict[str, Any]:
        """
        Generate comprehensive weekly performance report.
        
        Args:
            weeks_back: Number of weeks to include in report
            
        Returns:
            Weekly analytics report
        """
        try:
            # Get posts from the specified period
            end_date = datetime.now()
            start_date = end_date - timedelta(weeks=weeks_back)
            
            posts_response = self.facebook_manager.api.get_posts(limit=100)
            if not posts_response.get("success"):
                return {"success": False, "error": "Failed to fetch posts"}
            
            posts = posts_response.get("posts", [])
            
            # Filter posts within date range
            from datetime import timezone
            period_posts = []
            
            for post in posts:
                try:
                    post_time = datetime.fromisoformat(post["timestamp"].replace('Z', '+00:00'))
                    # If the post_time is naive, assume it's UTC
                    if post_time.tzinfo is None:
                        post_time = post_time.replace(tzinfo=timezone.utc)
                    
                    start_time_aware = start_date.replace(tzinfo=timezone.utc)
                    end_time_aware = end_date.replace(tzinfo=timezone.utc)
                    
                    if start_time_aware <= post_time <= end_time_aware:
                        period_posts.append(post)
                except Exception as e:
                    logger.warning(f"Could not parse timestamp for post analysis: {e}")
                    # Include the post anyway if we can't parse the timestamp
                    period_posts.append(post)
            
            # Calculate aggregate metrics
            total_posts = len(period_posts)
            total_likes = sum(post["likes"] for post in period_posts)
            total_comments = sum(post["comments"] for post in period_posts)
            total_shares = sum(post["shares"] for post in period_posts)
            total_reach = sum(post["reach"] for post in period_posts)
            
            avg_engagement_rate = statistics.mean([post["engagement_rate"] for post in period_posts]) if period_posts else 0
            
            # Identify top performing posts
            top_posts = sorted(period_posts, key=lambda p: p["engagement_rate"], reverse=True)[:3]
            
            # Analyze content themes
            theme_performance = self._analyze_theme_performance(period_posts)
            
            # Generate optimization insights
            optimization_insights = self._generate_optimization_insights(period_posts)
            
            report = {
                "period": {
                    "start_date": start_date.strftime("%Y-%m-%d"),
                    "end_date": end_date.strftime("%Y-%m-%d"),
                    "weeks": weeks_back
                },
                "summary_metrics": {
                    "total_posts": total_posts,
                    "total_engagement": total_likes + total_comments + total_shares,
                    "total_reach": total_reach,
                    "average_engagement_rate": round(avg_engagement_rate, 4),
                    "posts_per_day": round(total_posts / (weeks_back * 7), 1)
                },
                "top_performing_posts": [
                    {
                        "content": post["content"][:100] + "..." if len(post["content"]) > 100 else post["content"],
                        "engagement_rate": post["engagement_rate"],
                        "reach": post["reach"],
                        "total_engagement": post["likes"] + post["comments"] + post["shares"]
                    }
                    for post in top_posts
                ],
                "theme_performance": theme_performance,
                "optimization_insights": optimization_insights,
                "benchmark_comparison": {
                    "vs_fitness_industry": {
                        "your_rate": avg_engagement_rate,
                        "industry_avg": self.benchmark_metrics["fitness_industry_engagement_rate"],
                        "performance": "above" if avg_engagement_rate > self.benchmark_metrics["fitness_industry_engagement_rate"] else "below"
                    }
                },
                "recommendations": self._generate_weekly_recommendations(period_posts, optimization_insights)
            }
            
            return {
                "success": True,
                "report": report
            }
            
        except Exception as e:
            logger.error(f"Error generating weekly report: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _analyze_theme_performance(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze performance by content theme."""
        # This would ideally classify posts by theme using content analysis
        # For now, we'll use a simplified approach
        
        themes = {
            "motivation": [],
            "workout_tips": [],
            "promotions": [],
            "member_success": [],
            "general": []
        }
        
        # Simple keyword-based classification
        for post in posts:
            content = post["content"].lower()
            classified = False
            
            if any(word in content for word in ["motivation", "inspire", "achieve", "goal"]):
                themes["motivation"].append(post)
                classified = True
            elif any(word in content for word in ["tip", "workout", "exercise", "training"]):
                themes["workout_tips"].append(post)
                classified = True
            elif any(word in content for word in ["offer", "join", "membership", "special"]):
                themes["promotions"].append(post)
                classified = True
            elif any(word in content for word in ["member", "success", "transformation", "achievement"]):
                themes["member_success"].append(post)
                classified = True
            
            if not classified:
                themes["general"].append(post)
        
        # Calculate average performance by theme
        theme_performance = {}
        for theme, theme_posts in themes.items():
            if theme_posts:
                avg_engagement = statistics.mean([p["engagement_rate"] for p in theme_posts])
                avg_reach = statistics.mean([p["reach"] for p in theme_posts])
                theme_performance[theme] = {
                    "post_count": len(theme_posts),
                    "avg_engagement_rate": round(avg_engagement, 4),
                    "avg_reach": round(avg_reach, 1),
                    "performance_rating": "high" if avg_engagement > 0.05 else "medium" if avg_engagement > 0.02 else "low"
                }
        
        return theme_performance
    
    def _generate_optimization_insights(self, posts: List[Dict[str, Any]]) -> List[OptimizationInsight]:
        """Generate optimization insights from post data."""
        insights = []
        
        if not posts:
            return insights
        
        # Analyze posting frequency
        posting_frequency = len(posts) / 7  # posts per day
        optimal_frequency = self.benchmark_metrics["optimal_posting_frequency"]
        
        if posting_frequency < optimal_frequency * 0.7:
            insights.append(OptimizationInsight(
                insight_type="frequency",
                description=f"Posting frequency is below optimal ({posting_frequency:.1f} vs {optimal_frequency} posts/day)",
                recommendation="Increase posting frequency to 2-3 posts per day for better reach and engagement",
                confidence=0.8,
                impact="medium"
            ))
        elif posting_frequency > optimal_frequency * 1.5:
            insights.append(OptimizationInsight(
                insight_type="frequency",
                description=f"Posting frequency may be too high ({posting_frequency:.1f} posts/day)",
                recommendation="Consider reducing post frequency to avoid audience fatigue",
                confidence=0.7,
                impact="low"
            ))
        
        # Analyze engagement patterns
        engagement_rates = [p["engagement_rate"] for p in posts]
        avg_engagement = statistics.mean(engagement_rates)
        
        if avg_engagement < self.benchmark_metrics["fitness_industry_engagement_rate"] * 0.8:
            insights.append(OptimizationInsight(
                insight_type="engagement",
                description="Overall engagement rate is below industry average",
                recommendation="Focus on more interactive content with questions, polls, and calls-to-action",
                confidence=0.9,
                impact="high"
            ))
        
        return insights
    
    def _generate_weekly_recommendations(self, posts: List[Dict[str, Any]], insights: List[OptimizationInsight]) -> List[str]:
        """Generate weekly strategic recommendations."""
        recommendations = []
        
        # High-impact insights first
        high_impact_insights = [i for i in insights if i.impact == "high"]
        for insight in high_impact_insights[:2]:
            recommendations.append(insight.recommendation)
        
        # General recommendations based on performance
        if posts:
            avg_engagement = statistics.mean([p["engagement_rate"] for p in posts])
            
            if avg_engagement < 0.03:
                recommendations.append("Experiment with video content and user-generated content to boost engagement")
            
            if len(posts) < 10:  # Less than ~1.4 posts per day
                recommendations.append("Increase posting consistency to maintain audience engagement")
        
        # Always include growth-oriented recommendation
        recommendations.append("Continue analyzing top-performing content and replicate successful formats")
        
        return recommendations[:4]