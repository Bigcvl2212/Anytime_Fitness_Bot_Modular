"""
Analytics Manager - Comprehensive analytics, KPIs, and AI-powered insights
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

@dataclass
class KPIMetric:
    """Represents a Key Performance Indicator."""
    name: str
    current_value: float
    previous_value: float
    target_value: float
    unit: str
    trend: str  # "up", "down", "stable"
    description: str

@dataclass
class AnalyticsInsight:
    """Represents an AI-generated insight."""
    id: str
    title: str
    description: str
    category: str  # "membership", "revenue", "retention", "operations"
    priority: str  # "high", "medium", "low"
    recommendation: str
    impact: str
    created_at: str

class AnalyticsManager:
    """Main service for analytics and business insights."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.kpis = []
        self.insights = []
        
        # Initialize with demo data
        self._init_demo_data()
    
    def _init_demo_data(self):
        """Initialize with comprehensive demo analytics data."""
        # Key Performance Indicators
        self.kpis = [
            KPIMetric(
                name="Active Members",
                current_value=847,
                previous_value=823,
                target_value=900,
                unit="members",
                trend="up",
                description="Total active memberships"
            ),
            KPIMetric(
                name="Monthly Revenue",
                current_value=89420,
                previous_value=86750,
                target_value=95000,
                unit="USD",
                trend="up",
                description="Total monthly recurring revenue"
            ),
            KPIMetric(
                name="Member Retention",
                current_value=92.5,
                previous_value=91.2,
                target_value=95.0,
                unit="%",
                trend="up",
                description="Monthly member retention rate"
            ),
            KPIMetric(
                name="Average Visit Frequency",
                current_value=3.2,
                previous_value=3.4,
                target_value=3.5,
                unit="visits/week",
                trend="down",
                description="Average weekly visits per member"
            ),
            KPIMetric(
                name="New Signups",
                current_value=45,
                previous_value=52,
                target_value=60,
                unit="members",
                trend="down",
                description="New memberships this month"
            ),
            KPIMetric(
                name="Cancellation Rate",
                current_value=7.5,
                previous_value=8.8,
                target_value=5.0,
                unit="%",
                trend="up",
                description="Monthly membership cancellation rate"
            )
        ]
        
        # AI-Generated Insights
        self.insights = [
            AnalyticsInsight(
                id="insight_001",
                title="Peak Hours Optimization Opportunity",
                description="Analysis shows 40% of members visit between 6-8 PM, causing equipment bottlenecks.",
                category="operations",
                priority="high",
                recommendation="Consider incentivizing off-peak visits with rewards program or extended operating hours for popular equipment.",
                impact="Could improve member satisfaction by 15% and reduce cancellations",
                created_at=datetime.now().isoformat()
            ),
            AnalyticsInsight(
                id="insight_002",
                title="Personal Training Revenue Growth",
                description="Personal training bookings increased 25% this quarter but capacity is reaching limits.",
                category="revenue",
                priority="medium",
                recommendation="Hire 1-2 additional certified trainers to meet demand and capture missed revenue opportunities.",
                impact="Potential $8,000-12,000 monthly revenue increase",
                created_at=(datetime.now() - timedelta(days=1)).isoformat()
            ),
            AnalyticsInsight(
                id="insight_003",
                title="Member Engagement Declining in First 30 Days",
                description="New members show 35% drop in visit frequency after first month.",
                category="retention",
                priority="high",
                recommendation="Implement structured 30-day onboarding program with check-ins and goal setting.",
                impact="Could improve 3-month retention from 75% to 85%",
                created_at=(datetime.now() - timedelta(days=2)).isoformat()
            )
        ]
    
    def get_kpis(self) -> List[Dict[str, Any]]:
        """Get all Key Performance Indicators."""
        return [asdict(kpi) for kpi in self.kpis]
    
    def get_revenue_analytics(self) -> Dict[str, Any]:
        """Get detailed revenue analytics."""
        # Demo data for revenue analytics
        monthly_revenue = [
            {"month": "Jan", "revenue": 82500, "target": 85000},
            {"month": "Feb", "revenue": 84200, "target": 85000},
            {"month": "Mar", "revenue": 86750, "target": 88000},
            {"month": "Apr", "revenue": 89420, "target": 90000},
            {"month": "May", "revenue": 0, "target": 92000},  # Future
            {"month": "Jun", "revenue": 0, "target": 95000}   # Future
        ]
        
        revenue_breakdown = {
            "membership_fees": {"amount": 72450, "percentage": 81.0},
            "personal_training": {"amount": 12880, "percentage": 14.4},
            "supplements": {"amount": 2890, "percentage": 3.2},
            "guest_passes": {"amount": 1200, "percentage": 1.4}
        }
        
        return {
            "monthly_trend": monthly_revenue,
            "revenue_breakdown": revenue_breakdown,
            "total_revenue": 89420,
            "growth_rate": 3.1,
            "annual_projection": 1098000
        }
    
    def get_membership_analytics(self) -> Dict[str, Any]:
        """Get detailed membership analytics."""
        membership_trends = [
            {"month": "Jan", "new": 42, "cancelled": 15, "net": 27},
            {"month": "Feb", "new": 38, "cancelled": 12, "net": 26},
            {"month": "Mar", "new": 52, "cancelled": 18, "net": 34},
            {"month": "Apr", "new": 45, "cancelled": 21, "net": 24}
        ]
        
        member_segments = {
            "premium": {"count": 245, "percentage": 28.9},
            "standard": {"count": 487, "percentage": 57.5},
            "basic": {"count": 115, "percentage": 13.6}
        }
        
        retention_by_tenure = [
            {"tenure": "0-3 months", "retention": 75.2},
            {"tenure": "3-6 months", "retention": 89.1},
            {"tenure": "6-12 months", "retention": 94.3},
            {"tenure": "12+ months", "retention": 97.8}
        ]
        
        return {
            "membership_trends": membership_trends,
            "member_segments": member_segments,
            "retention_by_tenure": retention_by_tenure,
            "average_ltv": 1847,  # Lifetime Value
            "churn_risk_members": 34
        }
    
    def get_operational_analytics(self) -> Dict[str, Any]:
        """Get operational analytics and facility usage data."""
        peak_hours = [
            {"hour": "6 AM", "utilization": 45},
            {"hour": "7 AM", "utilization": 78},
            {"hour": "8 AM", "utilization": 65},
            {"hour": "12 PM", "utilization": 82},
            {"hour": "5 PM", "utilization": 92},
            {"hour": "6 PM", "utilization": 98},
            {"hour": "7 PM", "utilization": 95},
            {"hour": "8 PM", "utilization": 73}
        ]
        
        equipment_usage = [
            {"equipment": "Treadmills", "usage": 87, "maintenance_due": 2},
            {"equipment": "Weight Machines", "usage": 78, "maintenance_due": 0},
            {"equipment": "Free Weights", "usage": 92, "maintenance_due": 1},
            {"equipment": "Ellipticals", "usage": 65, "maintenance_due": 0}
        ]
        
        class_attendance = [
            {"class": "HIIT", "avg_attendance": 18, "capacity": 20},
            {"class": "Yoga", "avg_attendance": 15, "capacity": 16},
            {"class": "Spin", "avg_attendance": 22, "capacity": 24},
            {"class": "Strength Training", "avg_attendance": 12, "capacity": 15}
        ]
        
        return {
            "peak_hours": peak_hours,
            "equipment_usage": equipment_usage,
            "class_attendance": class_attendance,
            "staff_efficiency": 94.2,
            "facility_utilization": 78.5
        }
    
    def get_insights(self) -> List[Dict[str, Any]]:
        """Get AI-generated business insights."""
        return [asdict(insight) for insight in self.insights]
    
    def get_dashboard_summary(self) -> Dict[str, Any]:
        """Get comprehensive dashboard summary with key metrics."""
        # Calculate key summary metrics
        total_members = 847
        monthly_revenue = 89420
        retention_rate = 92.5
        growth_rate = 3.1
        
        # Recent trends
        member_growth = 24  # Net new members this month
        revenue_growth = 2670  # Revenue increase from last month
        
        # Alerts and notifications
        alerts = [
            {"type": "warning", "message": "Peak hour capacity approaching limits"},
            {"type": "info", "message": "Personal training bookings up 25%"},
            {"type": "success", "message": "Member retention target achieved"}
        ]
        
        return {
            "summary_metrics": {
                "total_members": total_members,
                "monthly_revenue": monthly_revenue,
                "retention_rate": retention_rate,
                "growth_rate": growth_rate
            },
            "trends": {
                "member_growth": member_growth,
                "revenue_growth": revenue_growth,
                "retention_change": 1.3
            },
            "alerts": alerts,
            "top_insights": [insight for insight in self.insights if insight.priority == "high"][:3],
            "performance_score": 87.2  # Overall gym performance score
        }
    
    def generate_report(self, report_type: str, date_range: str) -> Dict[str, Any]:
        """Generate comprehensive analytics report."""
        # This would generate detailed reports based on type and date range
        reports = {
            "monthly": {
                "title": "Monthly Performance Report",
                "period": "April 2024",
                "sections": ["Revenue", "Membership", "Operations", "Insights"],
                "generated_at": datetime.now().isoformat()
            },
            "quarterly": {
                "title": "Quarterly Business Review",
                "period": "Q1 2024",
                "sections": ["Financial Summary", "Growth Analysis", "Member Satisfaction", "Strategic Recommendations"],
                "generated_at": datetime.now().isoformat()
            }
        }
        
        return reports.get(report_type, {})

# Global instance
analytics_manager = AnalyticsManager()

def get_analytics_manager() -> AnalyticsManager:
    """Get the global analytics manager instance."""
    return analytics_manager