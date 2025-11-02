# Phase 2/3 API Reference

Complete API documentation for AI Collaboration Engine and Autopilot Engine endpoints.

## Table of Contents

1. [AI Collaboration Endpoints](#ai-collaboration-endpoints)
2. [Autopilot Endpoints](#autopilot-endpoints)
3. [Authentication](#authentication)
4. [Rate Limits](#rate-limits)
5. [Error Codes](#error-codes)
6. [Examples](#examples)

---

## AI Collaboration Endpoints

### 1. Generate Script

**POST** `/api/collaboration/generate-script`

Generate AI-powered video script for content marketing.

**Request:**
```json
{
  "project_name": "Q1 Fitness Campaign",
  "content_type": "workout",
  "platform": "tiktok",
  "description": "15-minute HIIT workout showcase",
  "duration_seconds": 15,
  "target_audience": "fitness enthusiasts aged 18-35"
}
```

**Response (200 OK):**
```json
{
  "project_id": 1,
  "project_name": "Q1 Fitness Campaign",
  "content_type": "workout",
  "platform": "tiktok",
  "script": "[HOOK] Ready for an intense workout?\n[MAIN] 15-minute full-body routine...\n[CTA] Join our gym today!",
  "iteration": 1,
  "status": "generated",
  "timestamp": "2025-01-15T10:30:00Z"
}
```

**Content Types:**
- `workout` - Exercise routines and fitness classes
- `testimonial` - Member transformation stories
- `class_promo` - Class promotion and registration
- `motivation` - Motivational fitness content

**Platforms:**
- `tiktok` - TikTok (15-60 second videos)
- `instagram` - Instagram Reels (15-90 second videos)
- `youtube` - YouTube Shorts/Long Form (any duration)
- `facebook` - Facebook (landscape or vertical)

---

### 2. Refine Script

**POST** `/api/collaboration/refine-script`

Refine generated script based on feedback.

**Request:**
```json
{
  "project_id": 1,
  "refinement_feedback": "Make it more energetic, add motivation quotes"
}
```

**Response (200 OK):**
```json
{
  "project_id": 1,
  "iteration": 2,
  "script": "[HOOK] Ready for an intense workout?\n[MAIN] 15-minute full-body routine with motivational cues...\n[CTA] Join our gym today!",
  "feedback": "Make it more energetic, add motivation quotes",
  "status": "refined",
  "timestamp": "2025-01-15T10:35:00Z"
}
```

**Refinement Tips:**
- Specify tone (energetic, calm, professional)
- Request specific content additions
- Mention pacing preferences
- Request call-to-action changes

---

### 3. Suggest Clips

**POST** `/api/collaboration/suggest-clips`

Get AI-suggested video clips that match the script.

**Request:**
```json
{
  "project_id": 1,
  "script_content": "[HOOK] Ready for an intense workout?\n[MAIN] Full-body routine...\n[CTA] Join!",
  "available_clips": ["clip_001", "clip_002", "clip_003", "clip_004", "clip_005"]
}
```

**Response (200 OK):**
```json
{
  "project_id": 1,
  "clips": [
    {
      "section": "Ready for an intense workout?",
      "suggested_duration": "3-5",
      "type": "action",
      "priority": "high"
    },
    {
      "section": "Full-body routine",
      "suggested_duration": "10-15",
      "type": "action",
      "priority": "high"
    }
  ],
  "count": 2,
  "status": "suggestions_generated",
  "timestamp": "2025-01-15T10:40:00Z"
}
```

---

### 4. Assemble Video

**POST** `/api/collaboration/assemble-video`

Assemble final video from selected clips, music, and captions.

**Request:**
```json
{
  "project_id": 1,
  "clips": [
    {
      "clip_id": "clip_001",
      "duration": 5,
      "position": 0
    },
    {
      "clip_id": "clip_002",
      "duration": 15,
      "position": 5
    }
  ],
  "music_track": "/music/energetic_fitness.mp3",
  "captions": true
}
```

**Response (200 OK):**
```json
{
  "project_id": 1,
  "output_path": "/outputs/project_1_assembled.mp4",
  "clips_count": 2,
  "music_track": "/music/energetic_fitness.mp3",
  "captions": true,
  "status": "assembled",
  "assembly_plan": {
    "clips": [...],
    "music": "...",
    "captions_enabled": true,
    "created_at": "2025-01-15T10:45:00Z"
  },
  "timestamp": "2025-01-15T10:45:00Z"
}
```

---

### 5. Get Project

**GET** `/api/collaboration/projects/{project_id}`

Get details for a specific collaboration project.

**Response (200 OK):**
```json
{
  "id": 1,
  "name": "Q1 Fitness Campaign",
  "description": "15-minute HIIT workout showcase",
  "content_type": "workout",
  "platform": "tiktok",
  "status": "assembled",
  "created_at": "2025-01-15T10:30:00Z"
}
```

---

### 6. List Projects

**GET** `/api/collaboration/projects?status=assembled`

List all collaboration projects with optional status filter.

**Query Parameters:**
- `status` (optional) - Filter by status: `draft`, `in_progress`, `assembled`, `published`

**Response (200 OK):**
```json
{
  "projects": [
    {
      "id": 1,
      "name": "Q1 Fitness Campaign",
      "content_type": "workout",
      "platform": "tiktok",
      "status": "assembled",
      "created_at": "2025-01-15T10:30:00Z"
    },
    {
      "id": 2,
      "name": "Member Testimonial",
      "content_type": "testimonial",
      "platform": "instagram",
      "status": "draft",
      "created_at": "2025-01-15T09:00:00Z"
    }
  ],
  "total": 2
}
```

---

## Autopilot Endpoints

### 1. Enable Autopilot

**POST** `/api/autopilot/enable`

Enable autonomous content generation and posting.

**Request:**
```json
{
  "name": "Gym Daily Content",
  "content_types": ["workout", "motivation", "testimonial"],
  "platforms": ["tiktok", "instagram", "youtube"],
  "posting_strategy": "moderate"
}
```

**Response (200 OK):**
```json
{
  "config_id": 1,
  "name": "Gym Daily Content",
  "enabled": true,
  "content_types": ["workout", "motivation", "testimonial"],
  "platforms": ["tiktok", "instagram", "youtube"],
  "posting_strategy": "moderate",
  "status": "enabled",
  "timestamp": "2025-01-15T10:30:00Z"
}
```

**Posting Strategies:**
- `aggressive` - Post within 1 hour
- `moderate` - Post within 12 hours (default)
- `conservative` - Post within 24 hours
- `custom` - Custom timing rules

---

### 2. Disable Autopilot

**POST** `/api/autopilot/disable`

Disable autopilot configuration.

**Request:**
```json
{
  "config_id": 1
}
```

**Response (200 OK):**
```json
{
  "config_id": 1,
  "enabled": false,
  "status": "disabled",
  "timestamp": "2025-01-15T10:35:00Z"
}
```

---

### 3. Monitor Trends

**POST** `/api/autopilot/trends/monitor`

Start monitoring trends for content inspiration.

**Request:**
```json
{
  "trend_type": "hashtag",
  "platforms": ["tiktok", "instagram"]
}
```

**Response (200 OK):**
```json
{
  "trend_type": "hashtag",
  "platforms": ["tiktok", "instagram"],
  "trending_content": [
    "#fitness",
    "#gym",
    "#workout",
    "#motivation",
    "#fitnessgains"
  ],
  "status": "monitoring_active",
  "timestamp": "2025-01-15T10:40:00Z"
}
```

**Trend Types:**
- `hashtag` - Trending hashtags
- `topic` - Trending topics
- `creator` - Popular fitness creators
- `challenge` - Trending challenges
- `sound` - Trending audio/music

---

### 4. Generate Autonomous Content

**POST** `/api/autopilot/generate-content`

Generate content autonomously based on trends and config.

**Request:**
```json
{
  "config_id": 1,
  "count": 3
}
```

**Response (200 OK):**
```json
{
  "config_id": 1,
  "generated_count": 3,
  "content": [
    {
      "project_id": 2,
      "script": "[HOOK] Trending workout routine...",
      "content_type": "workout",
      "platform": "tiktok",
      "status": "generated"
    },
    {
      "project_id": 3,
      "script": "[HOOK] Motivational fitness message...",
      "content_type": "motivation",
      "platform": "instagram",
      "status": "generated"
    },
    {
      "project_id": 4,
      "script": "[HOOK] Member success story...",
      "content_type": "testimonial",
      "platform": "youtube",
      "status": "generated"
    }
  ],
  "status": "generated",
  "timestamp": "2025-01-15T10:45:00Z"
}
```

---

### 5. Schedule Post

**POST** `/api/autopilot/schedule-post`

Schedule generated content for posting.

**Request:**
```json
{
  "content_id": "content_123",
  "platforms": ["tiktok", "instagram"],
  "posting_strategy": "moderate"
}
```

**Response (200 OK):**
```json
{
  "post_id": 1,
  "content_id": "content_123",
  "platforms": ["tiktok", "instagram"],
  "scheduled_time": "2025-01-15T22:30:00Z",
  "strategy": "moderate",
  "status": "scheduled",
  "timestamp": "2025-01-15T10:50:00Z"
}
```

---

### 6. Calculate Optimal Posting Times

**GET** `/api/autopilot/posting-times?platform=tiktok&timezone=US/Central`

Get optimal posting times for maximum engagement.

**Query Parameters:**
- `platform` - Target platform (tiktok, instagram, youtube, facebook)
- `timezone` (optional) - User timezone (default: US/Central)

**Response (200 OK):**
```json
{
  "platform": "tiktok",
  "timezone": "US/Central",
  "optimal_times": [
    "11:00 AM",
    "02:00 PM",
    "07:00 PM"
  ],
  "engagement_info": "Peak engagement hours based on platform analytics"
}
```

---

### 7. Get Analytics

**GET** `/api/autopilot/analytics?period_days=7`

Get autopilot analytics and performance metrics.

**Query Parameters:**
- `period_days` (optional) - Number of days to analyze (default: 7)

**Response (200 OK):**
```json
{
  "period_days": 7,
  "posts_scheduled": 21,
  "posts_published": 19,
  "success_rate": 90.5,
  "engagement_metrics": {
    "avg_likes": 245,
    "avg_comments": 18,
    "avg_shares": 12
  },
  "top_performing_type": "workout",
  "status": "analytics_ready",
  "timestamp": "2025-01-15T10:55:00Z"
}
```

---

## Authentication

All API endpoints require authentication token in header:

```
Authorization: Bearer {access_token}
```

**Example Request:**
```bash
curl -X POST https://api.gymbot.com/api/collaboration/generate-script \
  -H "Authorization: Bearer eyJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{...}'
```

---

## Rate Limits

- **Tier 1** (Free): 100 requests/hour
- **Tier 2** (Pro): 1,000 requests/hour
- **Tier 3** (Enterprise): Unlimited

**Rate Limit Headers:**
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1705347600
```

---

## Error Codes

### 400 Bad Request
```json
{
  "error": "Invalid request parameters",
  "details": "Missing required field: platform"
}
```

### 401 Unauthorized
```json
{
  "error": "Authentication required",
  "details": "Invalid or missing authorization token"
}
```

### 404 Not Found
```json
{
  "error": "Resource not found",
  "details": "Project ID 999 does not exist"
}
```

### 429 Too Many Requests
```json
{
  "error": "Rate limit exceeded",
  "details": "Please wait 30 seconds before making another request"
}
```

### 500 Server Error
```json
{
  "error": "Internal server error",
  "details": "Please try again later or contact support"
}
```

---

## Examples

### Example 1: Complete Collaboration Workflow

```bash
# 1. Generate script
curl -X POST https://api.gymbot.com/api/collaboration/generate-script \
  -H "Authorization: Bearer token" \
  -d '{
    "project_name": "Monday Motivation",
    "content_type": "motivation",
    "platform": "instagram",
    "description": "Motivational Monday fitness post"
  }'

# 2. Refine script
curl -X POST https://api.gymbot.com/api/collaboration/refine-script \
  -H "Authorization: Bearer token" \
  -d '{
    "project_id": 1,
    "refinement_feedback": "Add more energy and excitement"
  }'

# 3. Suggest clips
curl -X POST https://api.gymbot.com/api/collaboration/suggest-clips \
  -H "Authorization: Bearer token" \
  -d '{
    "project_id": 1,
    "script_content": "...",
    "available_clips": ["clip_1", "clip_2"]
  }'

# 4. Assemble video
curl -X POST https://api.gymbot.com/api/collaboration/assemble-video \
  -H "Authorization: Bearer token" \
  -d '{
    "project_id": 1,
    "clips": [{...}],
    "captions": true
  }'
```

### Example 2: Autopilot Setup and Posting

```bash
# 1. Enable autopilot
curl -X POST https://api.gymbot.com/api/autopilot/enable \
  -H "Authorization: Bearer token" \
  -d '{
    "name": "Daily Gym Content",
    "content_types": ["workout", "motivation"],
    "platforms": ["tiktok", "instagram"],
    "posting_strategy": "moderate"
  }'

# 2. Monitor trends
curl -X POST https://api.gymbot.com/api/autopilot/trends/monitor \
  -H "Authorization: Bearer token" \
  -d '{
    "trend_type": "hashtag",
    "platforms": ["tiktok", "instagram"]
  }'

# 3. Generate autonomous content
curl -X POST https://api.gymbot.com/api/autopilot/generate-content \
  -H "Authorization: Bearer token" \
  -d '{
    "config_id": 1,
    "count": 5
  }'

# 4. Schedule posts
curl -X POST https://api.gymbot.com/api/autopilot/schedule-post \
  -H "Authorization: Bearer token" \
  -d '{
    "content_id": "content_1",
    "platforms": ["tiktok"],
    "posting_strategy": "moderate"
  }'
```

---

## Support

For API support, contact: `api-support@gymbot.com`

**Last Updated:** January 2025
**API Version:** 2.1.9
