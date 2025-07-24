#!/usr/bin/env python3
"""
Dashboard Feature Test Suite
Tests the new social media and analytics features.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_social_media_service():
    """Test social media management service."""
    print("Testing Social Media Service...")
    
    from new_services_social_media.social_media_manager import get_social_media_manager
    
    sm = get_social_media_manager()
    
    # Test connected accounts
    accounts = sm.get_connected_accounts()
    assert len(accounts) == 3, f"Expected 3 accounts, got {len(accounts)}"
    
    connected = [acc for acc in accounts if acc['is_connected']]
    assert len(connected) == 2, f"Expected 2 connected accounts, got {len(connected)}"
    
    # Test scheduled posts
    posts = sm.get_scheduled_posts()
    assert len(posts) >= 2, f"Expected at least 2 posts, got {len(posts)}"
    
    # Test engagement overview
    overview = sm.get_engagement_overview()
    assert overview['total_followers'] > 0, "Should have followers"
    assert overview['connected_platforms'] == 2, "Should have 2 connected platforms"
    
    # Test content recommendations
    recommendations = sm.get_content_recommendations()
    assert len(recommendations) >= 2, "Should have content recommendations"
    
    print("✅ Social Media Service: All tests passed!")
    return True

def test_analytics_service():
    """Test analytics and insights service."""
    print("Testing Analytics Service...")
    
    from new_services_analytics.analytics_manager import get_analytics_manager
    
    analytics = get_analytics_manager()
    
    # Test KPIs
    kpis = analytics.get_kpis()
    assert len(kpis) == 6, f"Expected 6 KPIs, got {len(kpis)}"
    
    # Verify required KPI fields
    for kpi in kpis:
        assert 'name' in kpi, "KPI missing name"
        assert 'current_value' in kpi, "KPI missing current_value"
        assert 'trend' in kpi, "KPI missing trend"
    
    # Test revenue analytics
    revenue = analytics.get_revenue_analytics()
    assert revenue['total_revenue'] > 0, "Should have revenue"
    assert 'revenue_breakdown' in revenue, "Should have revenue breakdown"
    
    # Test membership analytics
    membership = analytics.get_membership_analytics()
    assert 'membership_trends' in membership, "Should have membership trends"
    assert 'retention_by_tenure' in membership, "Should have retention data"
    
    # Test operational analytics
    operational = analytics.get_operational_analytics()
    assert 'peak_hours' in operational, "Should have peak hours data"
    assert 'equipment_usage' in operational, "Should have equipment usage"
    
    # Test AI insights
    insights = analytics.get_insights()
    assert len(insights) >= 3, f"Expected at least 3 insights, got {len(insights)}"
    
    # Test dashboard summary
    summary = analytics.get_dashboard_summary()
    assert 'summary_metrics' in summary, "Should have summary metrics"
    assert 'top_insights' in summary, "Should have top insights"
    
    print("✅ Analytics Service: All tests passed!")
    return True

def test_dashboard_integration():
    """Test dashboard integration and imports."""
    print("Testing Dashboard Integration...")
    
    # Test dashboard imports
    import gym_bot_dashboard
    
    # Test template creation
    gym_bot_dashboard.create_templates()
    
    # Verify templates exist
    templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
    required_templates = [
        'base.html',
        'dashboard.html', 
        'social_media.html',
        'analytics.html',
        'feature_unavailable.html'
    ]
    
    for template in required_templates:
        template_path = os.path.join(templates_dir, template)
        assert os.path.exists(template_path), f"Template {template} not found"
    
    print("✅ Dashboard Integration: All tests passed!")
    return True

def main():
    """Run all tests."""
    print("🚀 Starting Gym Bot Pro Dashboard Tests\n")
    
    tests = [
        test_social_media_service,
        test_analytics_service,
        test_dashboard_integration
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ {test.__name__}: {e}")
            failed += 1
    
    print(f"\n📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! Dashboard is ready for production.")
        return True
    else:
        print("❌ Some tests failed. Please check the implementation.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)