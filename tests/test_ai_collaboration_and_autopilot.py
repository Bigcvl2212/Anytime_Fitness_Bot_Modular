#!/usr/bin/env python3
"""
Comprehensive tests for AI Collaboration Engine and Autopilot Engine

Tests AI-powered content generation, refinement, clip suggestion,
video assembly, autonomous content generation, and scheduled posting.
"""

import pytest
import json
import tempfile
import os
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock, patch

from services.content_automation.ai_collaboration_engine import AICollaborationEngine
from services.content_automation.autopilot_engine import AutopilotEngine


# ===== AI COLLABORATION ENGINE TESTS =====

class TestAICollaborationEngine:
    """Test AI Collaboration Engine"""

    @pytest.fixture
    def mock_db(self):
        """Create mock database manager"""
        db = Mock()
        db.execute = Mock(return_value=Mock())
        db.cursor = Mock()
        db.cursor.lastrowid = 1
        db.cursor.fetchone = Mock(return_value=None)
        db.cursor.fetchall = Mock(return_value=[])
        return db

    @pytest.fixture
    def collaboration_engine(self, mock_db):
        """Create collaboration engine for testing"""
        return AICollaborationEngine(groq_client=None, db_manager=mock_db)

    def test_engine_initialization(self, collaboration_engine, mock_db):
        """Test engine initializes correctly"""
        assert collaboration_engine is not None
        assert collaboration_engine.db_manager == mock_db
        assert collaboration_engine.groq_client is None

    def test_generate_script_basic(self, collaboration_engine):
        """Test basic script generation"""
        result = collaboration_engine.generate_script(
            project_name="Test Project",
            content_type="workout",
            platform="tiktok",
            description="Quick 15-minute workout",
            duration_seconds=15
        )

        assert "project_id" in result
        assert "script" in result
        assert result["status"] == "generated"
        assert result["content_type"] == "workout"
        assert result["platform"] == "tiktok"

    def test_generate_script_with_audience(self, collaboration_engine):
        """Test script generation with specific audience"""
        result = collaboration_engine.generate_script(
            project_name="Yoga Class",
            content_type="yoga",
            platform="instagram",
            description="Relaxing yoga flow",
            duration_seconds=60,
            target_audience="yoga beginners"
        )

        assert result["status"] == "generated"
        assert "[HOOK]" in result["script"] or "[MAIN]" in result["script"]

    def test_generate_script_different_types(self, collaboration_engine):
        """Test script generation for different content types"""
        content_types = ["workout", "testimonial", "class_promo", "motivation"]

        for content_type in content_types:
            result = collaboration_engine.generate_script(
                project_name=f"{content_type} Project",
                content_type=content_type,
                platform="youtube",
                description=f"Test {content_type}",
            )

            assert result["status"] == "generated"
            assert result["content_type"] == content_type

    def test_generate_script_all_platforms(self, collaboration_engine):
        """Test script generation for all platforms"""
        platforms = ["tiktok", "instagram", "youtube", "facebook"]

        for platform in platforms:
            result = collaboration_engine.generate_script(
                project_name=f"{platform} Project",
                content_type="workout",
                platform=platform,
                description=f"Test for {platform}"
            )

            assert result["status"] == "generated"
            assert result["platform"] == platform

    def test_refine_script_without_db(self):
        """Test script refinement without database"""
        engine = AICollaborationEngine(groq_client=None, db_manager=None)
        result = engine.refine_script(project_id=1, refinement_feedback="Make it shorter")

        assert result["status"] == "failed"
        assert "error" in result

    def test_refine_script_with_db(self, collaboration_engine, mock_db):
        """Test script refinement with database"""
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = (1, "[HOOK] Original script [MAIN]", 1)
        mock_db.execute.return_value = mock_cursor

        result = collaboration_engine.refine_script(
            project_id=1,
            refinement_feedback="Make it more energetic"
        )

        assert result["status"] == "refined"
        assert result["iteration"] == 2
        assert "script" in result

    def test_suggest_clips(self, collaboration_engine):
        """Test clip suggestion"""
        script = "[HOOK] Start\n[MAIN] Middle\n[CTA] End"

        result = collaboration_engine.suggest_clips(
            project_id=1,
            script_content=script,
            available_clips=["clip_1", "clip_2", "clip_3"]
        )

        assert result["status"] == "suggestions_generated"
        assert "clips" in result
        assert result["count"] > 0

    def test_assemble_video(self, collaboration_engine):
        """Test video assembly"""
        clips = [
            {"clip_id": "clip_1", "duration": 5, "position": 0},
            {"clip_id": "clip_2", "duration": 30, "position": 5},
            {"clip_id": "clip_3", "duration": 10, "position": 35}
        ]

        result = collaboration_engine.assemble_video(
            project_id=1,
            clips=clips,
            music_track="/music/motivational.mp3",
            captions=True
        )

        assert result["status"] == "assembled"
        assert "output_path" in result
        assert result["clips_count"] == 3
        assert result["captions"] == True

    def test_get_project(self, collaboration_engine, mock_db):
        """Test getting project details"""
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = (
            1, "Test Project", "A test project", "workout", "tiktok", "draft", "2024-01-01"
        )
        mock_db.execute.return_value = mock_cursor

        result = collaboration_engine.get_project(project_id=1)

        assert result is not None
        assert result["name"] == "Test Project"

    def test_list_projects_empty(self, collaboration_engine, mock_db):
        """Test listing projects when empty"""
        mock_db.execute.return_value = Mock()
        mock_db.cursor.fetchall.return_value = []

        result = collaboration_engine.list_projects()

        assert isinstance(result, list)
        assert len(result) == 0

    def test_list_projects_with_status_filter(self, collaboration_engine, mock_db):
        """Test listing projects with status filter"""
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [
            (1, "Project 1", "workout", "tiktok", "draft", "2024-01-01"),
            (2, "Project 2", "testimonial", "instagram", "draft", "2024-01-02")
        ]
        mock_db.execute.return_value = mock_cursor

        result = collaboration_engine.list_projects(status="draft")

        assert len(result) == 2

    def test_template_script_generation(self, collaboration_engine):
        """Test template script is generated correctly"""
        script = collaboration_engine._generate_template_script("workout", "tiktok")

        assert "[HOOK]" in script
        assert "[MAIN]" in script
        assert "[CTA]" in script

    def test_template_script_for_testimonial(self, collaboration_engine):
        """Test testimonial template script"""
        script = collaboration_engine._generate_template_script("testimonial", "instagram")

        assert "testimonial" not in script or "transform" in script.lower()

    def test_suggest_clips_algorithm(self, collaboration_engine):
        """Test clip suggestion algorithm"""
        script = "[HOOK] Opening hook\n[MAIN] Main workout\n[CTA] Call to action"
        suggestions = collaboration_engine._suggest_clips_with_ai(script, [])

        assert len(suggestions) > 0
        assert all("section" in s or "suggested_duration" in s for s in suggestions)


# ===== AUTOPILOT ENGINE TESTS =====

class TestAutopilotEngine:
    """Test Autopilot Engine"""

    @pytest.fixture
    def mock_db(self):
        """Create mock database"""
        db = Mock()
        db.execute = Mock(return_value=Mock())
        db.cursor = Mock()
        db.cursor.lastrowid = 1
        db.cursor.fetchone = Mock(return_value=None)
        db.cursor.fetchall = Mock(return_value=[])
        return db

    @pytest.fixture
    def mock_ai_engine(self):
        """Create mock AI collaboration engine"""
        engine = Mock(spec=AICollaborationEngine)
        engine.generate_script = Mock(return_value={
            "project_id": 1,
            "script": "[HOOK] Test [MAIN] Content [CTA]",
            "status": "generated"
        })
        return engine

    @pytest.fixture
    def autopilot_engine(self, mock_db, mock_ai_engine):
        """Create autopilot engine for testing"""
        return AutopilotEngine(
            db_manager=mock_db,
            ai_collaboration_engine=mock_ai_engine,
            social_poster=None,
            groq_client=None
        )

    def test_engine_initialization(self, autopilot_engine, mock_db):
        """Test autopilot engine initializes"""
        assert autopilot_engine is not None
        assert autopilot_engine.db_manager == mock_db

    def test_enable_autopilot(self, autopilot_engine):
        """Test enabling autopilot"""
        result = autopilot_engine.enable_autopilot(
            name="Gym Content",
            content_types=["workout", "motivation"],
            platforms=["tiktok", "instagram"],
            posting_strategy="moderate"
        )

        assert result["status"] == "enabled"
        assert result["name"] == "Gym Content"
        assert result["enabled"] == True

    def test_disable_autopilot(self, autopilot_engine):
        """Test disabling autopilot"""
        result = autopilot_engine.disable_autopilot(config_id=1)

        assert result["status"] == "disabled"
        assert result["enabled"] == False

    def test_monitor_trends(self, autopilot_engine):
        """Test trend monitoring"""
        result = autopilot_engine.monitor_trends(
            trend_type="hashtag",
            platforms=["tiktok", "instagram"]
        )

        assert result["status"] == "monitoring_active"
        assert result["trend_type"] == "hashtag"
        assert "trending_content" in result

    def test_monitor_trends_types(self, autopilot_engine):
        """Test different trend types"""
        trend_types = ["hashtag", "topic", "creator", "challenge", "sound"]

        for trend_type in trend_types:
            result = autopilot_engine.monitor_trends(
                trend_type=trend_type,
                platforms=["tiktok"]
            )

            assert result["status"] == "monitoring_active"
            assert result["trend_type"] == trend_type

    def test_generate_autonomous_content_without_ai(self):
        """Test content generation without AI engine"""
        mock_db = Mock()
        engine = AutopilotEngine(db_manager=mock_db, ai_collaboration_engine=None)

        result = engine.generate_autonomous_content(config_id=1)

        assert result["status"] == "failed"

    def test_generate_autonomous_content(self, autopilot_engine, mock_db):
        """Test autonomous content generation"""
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = (
            json.dumps(["workout", "motivation"]),
            json.dumps(["tiktok", "instagram"])
        )
        mock_db.execute.return_value = mock_cursor

        result = autopilot_engine.generate_autonomous_content(config_id=1, count=2)

        assert result["status"] == "generated"
        assert result["generated_count"] == 2

    def test_schedule_post(self, autopilot_engine):
        """Test post scheduling"""
        result = autopilot_engine.schedule_autonomous_post(
            content_id="content_123",
            platforms=["tiktok", "instagram"],
            posting_strategy="moderate"
        )

        assert result["status"] == "scheduled"
        assert result["content_id"] == "content_123"
        assert "scheduled_time" in result

    def test_schedule_post_strategies(self, autopilot_engine):
        """Test different posting strategies"""
        strategies = ["aggressive", "moderate", "conservative"]

        for strategy in strategies:
            result = autopilot_engine.schedule_autonomous_post(
                content_id=f"content_{strategy}",
                platforms=["tiktok"],
                posting_strategy=strategy
            )

            assert result["status"] == "scheduled"
            assert result["strategy"] == strategy

    def test_calculate_optimal_posting_times(self, autopilot_engine):
        """Test optimal posting time calculation"""
        platforms = ["tiktok", "instagram", "youtube", "facebook"]

        for platform in platforms:
            times = autopilot_engine.calculate_optimal_posting_times(platform)

            assert isinstance(times, list)
            assert len(times) > 0
            assert all(":" in time for time in times)

    def test_post_scheduled_content_without_poster(self, autopilot_engine):
        """Test posting without social media poster service"""
        # Autopilot engine should handle gracefully
        result = autopilot_engine.post_scheduled_content()

        assert "status" in result

    def test_get_analytics(self, autopilot_engine, mock_db):
        """Test analytics retrieval"""
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = (5, 3)
        mock_db.execute.return_value = mock_cursor

        result = autopilot_engine.get_analytics(period_days=7)

        assert result["status"] == "analytics_ready"
        assert "posts_scheduled" in result
        assert "posts_published" in result
        assert "success_rate" in result

    def test_fetch_trending_content(self, autopilot_engine):
        """Test trending content fetching"""
        trending = autopilot_engine._fetch_trending_content("hashtag", ["tiktok"])

        assert isinstance(trending, list)
        assert len(trending) > 0

    def test_fetch_trending_all_types(self, autopilot_engine):
        """Test trending for all trend types"""
        trend_types = ["hashtag", "topic", "creator", "challenge", "sound"]

        for trend_type in trend_types:
            trending = autopilot_engine._fetch_trending_content(trend_type, ["tiktok"])

            assert isinstance(trending, list)

    def test_optimal_posting_time_aggressive(self, autopilot_engine):
        """Test aggressive posting strategy timing"""
        posting_time = autopilot_engine._calculate_optimal_posting_time("aggressive")
        now = datetime.now()

        assert posting_time > now
        assert posting_time < now + timedelta(hours=2)

    def test_optimal_posting_time_moderate(self, autopilot_engine):
        """Test moderate posting strategy timing"""
        posting_time = autopilot_engine._calculate_optimal_posting_time("moderate")
        now = datetime.now()

        assert posting_time > now
        assert posting_time < now + timedelta(hours=13)

    def test_optimal_posting_time_conservative(self, autopilot_engine):
        """Test conservative posting strategy timing"""
        posting_time = autopilot_engine._calculate_optimal_posting_time("conservative")
        now = datetime.now()

        assert posting_time > now + timedelta(hours=23)
        assert posting_time < now + timedelta(hours=25)


# ===== INTEGRATION TESTS =====

class TestCollaborationAndAutopilotIntegration:
    """Test integration between collaboration and autopilot engines"""

    @pytest.fixture
    def mock_db(self):
        """Create mock database"""
        db = Mock()
        db.execute = Mock(return_value=Mock())
        db.cursor = Mock()
        db.cursor.lastrowid = 1
        db.cursor.fetchone = Mock(return_value=None)
        db.cursor.fetchall = Mock(return_value=[])
        return db

    def test_autopilot_uses_collaboration_engine(self, mock_db):
        """Test autopilot can use collaboration engine"""
        ai_engine = AICollaborationEngine(db_manager=mock_db)
        autopilot = AutopilotEngine(
            db_manager=mock_db,
            ai_collaboration_engine=ai_engine
        )

        assert autopilot.ai_collaboration_engine == ai_engine

    def test_end_to_end_workflow(self, mock_db):
        """Test complete workflow: enable autopilot, generate, schedule, post"""
        # Initialize engines
        ai_engine = AICollaborationEngine(db_manager=mock_db)
        autopilot = AutopilotEngine(
            db_manager=mock_db,
            ai_collaboration_engine=ai_engine
        )

        # Enable autopilot
        enable_result = autopilot.enable_autopilot(
            name="Complete Workflow Test",
            content_types=["workout"],
            platforms=["tiktok"],
            posting_strategy="moderate"
        )
        assert enable_result["status"] == "enabled"

        # Monitor trends
        trends_result = autopilot.monitor_trends(
            trend_type="hashtag",
            platforms=["tiktok"]
        )
        assert trends_result["status"] == "monitoring_active"

        # Generate content (mocking the DB response)
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = (
            json.dumps(["workout"]),
            json.dumps(["tiktok"])
        )
        mock_db.execute.return_value = mock_cursor

        content_result = autopilot.generate_autonomous_content(
            config_id=1,
            count=1
        )
        assert content_result["status"] == "generated"

        # Schedule post
        schedule_result = autopilot.schedule_autonomous_post(
            content_id="content_123",
            platforms=["tiktok"],
            posting_strategy="moderate"
        )
        assert schedule_result["status"] == "scheduled"

        # Verify complete workflow
        assert all([
            enable_result["status"] == "enabled",
            trends_result["status"] == "monitoring_active",
            content_result["status"] == "generated",
            schedule_result["status"] == "scheduled"
        ])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
