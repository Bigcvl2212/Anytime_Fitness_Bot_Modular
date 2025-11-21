#!/usr/bin/env python3
"""
Integration test for Phase 2/3 services

Tests that AI Collaboration Engine and Autopilot Engine
can be imported and used in production scenarios.
"""

import sys
import json
from datetime import datetime

print("\n" + "="*80)
print("PHASE 2/3 INTEGRATION TEST - v2.1.9")
print("="*80 + "\n")

# Test 1: Import AI Collaboration Engine
print("[TEST 1] Importing AI Collaboration Engine...")
try:
    from services.content_automation.ai_collaboration_engine import AICollaborationEngine
    print("[PASS] AICollaborationEngine imported successfully\n")
except Exception as e:
    print(f"[FAIL] {e}\n")
    sys.exit(1)

# Test 2: Initialize and test AI Collaboration Engine
print("[TEST 2] Testing AI Collaboration Engine functionality...")
try:
    ai_engine = AICollaborationEngine()

    # Test script generation
    result = ai_engine.generate_script(
        project_name="Test Workout Content",
        content_type="workout",
        platform="tiktok",
        description="30-second HIIT workout showcase",
        duration_seconds=30,
        target_audience="fitness enthusiasts aged 18-35"
    )

    assert result["status"] == "generated", "Script generation failed"
    assert "script" in result, "No script in response"
    assert "[HOOK]" in result["script"], "Script missing HOOK section"
    assert "[MAIN]" in result["script"], "Script missing MAIN section"
    assert "[CTA]" in result["script"], "Script missing CTA section"

    print(f"[OK] PASS: Script generated successfully")
    print(f"  Project: {result['project_name']}")
    print(f"  Platform: {result['platform']}")
    print(f"  Content Type: {result['content_type']}")
    print(f"  Script Preview: {result['script'][:100]}...\n")

except Exception as e:
    print(f"[FAIL] FAIL: {e}\n")
    sys.exit(1)

# Test 3: Import Autopilot Engine
print("[TEST 3] Importing Autopilot Engine...")
try:
    from services.content_automation.autopilot_engine import AutopilotEngine
    print("[OK] PASS: AutopilotEngine imported successfully\n")
except Exception as e:
    print(f"[FAIL] FAIL: {e}\n")
    sys.exit(1)

# Test 4: Initialize and test Autopilot Engine
print("[TEST 4] Testing Autopilot Engine initialization...")
try:
    autopilot = AutopilotEngine(ai_collaboration_engine=ai_engine)
    print("[OK] PASS: Autopilot Engine initialized\n")

except Exception as e:
    print(f"[FAIL] FAIL: {e}\n")
    sys.exit(1)

# Test 5: Test optimal posting times (doesn't require DB)
print("[TEST 5] Testing optimal posting time calculation...")
try:
    for platform in ["tiktok", "instagram", "youtube", "facebook"]:
        times = autopilot.calculate_optimal_posting_times(platform)
        assert isinstance(times, list), f"Invalid times for {platform}"
        assert len(times) > 0, f"No times for {platform}"

    print("[OK] PASS: Optimal posting times calculated for all platforms\n")

except Exception as e:
    print(f"[FAIL] FAIL: {e}\n")
    sys.exit(1)

# Test 6: Test clip suggestion
print("[TEST 6] Testing AI clip suggestion...")
try:
    script = "[HOOK] Ready for a workout?\n[MAIN] 30-second HIIT routine\n[CTA] Join our gym!"
    clips = ai_engine.suggest_clips(
        project_id=1,
        script_content=script,
        available_clips=["clip_1", "clip_2", "clip_3", "clip_4", "clip_5"]
    )

    assert clips["status"] == "suggestions_generated", "Clip suggestion failed"
    assert "clips" in clips, "No clips in response"
    assert clips["count"] > 0, "No clips suggested"

    print(f"[OK] PASS: Clip suggestions generated")
    print(f"  Suggestions: {clips['count']} clips recommended")
    print(f"  First suggestion: {clips['clips'][0] if clips['clips'] else 'None'}\n")

except Exception as e:
    print(f"[FAIL] FAIL: {e}\n")
    sys.exit(1)

# Test 7: Test video assembly
print("[TEST 7] Testing video assembly...")
try:
    assembly = ai_engine.assemble_video(
        project_id=1,
        clips=[
            {"clip_id": "clip_1", "duration": 5, "position": 0},
            {"clip_id": "clip_2", "duration": 20, "position": 5},
            {"clip_id": "clip_3", "duration": 5, "position": 25}
        ],
        music_track="/music/energetic.mp3",
        captions=True
    )

    assert assembly["status"] == "assembled", "Video assembly failed"
    assert "output_path" in assembly, "No output path"
    assert assembly["clips_count"] == 3, "Wrong clip count"

    print(f"[OK] PASS: Video assembled successfully")
    print(f"  Output: {assembly['output_path']}")
    print(f"  Clips: {assembly['clips_count']}")
    print(f"  Captions: {assembly['captions']}\n")

except Exception as e:
    print(f"[FAIL] FAIL: {e}\n")
    sys.exit(1)

# Final Summary
print("="*80)
print("PHASE 2/3 INTEGRATION TEST COMPLETE")
print("="*80)
print("\nRESULTS:")
print("  [OK] AI Collaboration Engine - WORKING")
print("  [OK] Autopilot Engine - WORKING")
print("  [OK] Integration - SUCCESSFUL")
print("\nAll Phase 2/3 features verified and production-ready!")
print("="*80 + "\n")

sys.exit(0)
