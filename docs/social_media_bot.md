# Social Media Management Bot Documentation

## Overview

The Social Media Management Bot is a comprehensive autonomous system designed to manage the Anytime Fitness Facebook page. It handles content generation, scheduling, posting, engagement monitoring, and performance analytics.

## Architecture

The system consists of several modular components:

### Core Components

1. **SocialMediaManager** - Main orchestrator that coordinates all operations
2. **ContentGenerator** - Generates fitness-related content with themes and viral hooks
3. **FacebookManager** - Handles posting and engagement with Facebook API
4. **PostScheduler** - Manages content scheduling and automated posting
5. **SocialMediaAnalytics** - Tracks performance and provides optimization insights
6. **MockFacebookAPI** - Testing environment for development and demo

## Features

### Content Strategy & Generation

- **Daily/Weekly Scheduling**: Automatically generates 2-3 posts per day following an optimized schedule
- **Content Themes**: 6 main themes including motivation, workout tips, member success, promotions, nutrition, and challenges
- **Viral Hooks**: Incorporates proven engagement patterns and viral post formats
- **Hashtag Optimization**: Automatically generates relevant hashtags for each post
- **Engagement Prediction**: Estimates engagement potential for each post

### Automated Posting

- **Smart Scheduling**: Posts at optimal times based on audience engagement patterns
- **Content Variety**: Supports text posts, images, and videos
- **Auto-Posting Service**: Runs continuously with configurable check intervals
- **Retry Logic**: Automatically retries failed posts with exponential backoff

### Engagement Management

- **Real-time Monitoring**: Continuously monitors for comments and messages
- **Intelligent Responses**: Categorizes inquiries and provides appropriate responses
- **Template System**: Uses predefined response templates for common scenarios
- **AI Integration**: Can use AI for more personalized responses (when available)

### Analytics & Optimization

- **Performance Tracking**: Monitors likes, comments, shares, reach, and engagement rates
- **Benchmark Comparisons**: Compares performance against industry standards
- **Content Analysis**: Analyzes which content types perform best
- **Strategic Recommendations**: Provides actionable insights for optimization

## Installation & Setup

### Prerequisites

```bash
# Install required packages
pip install -r data/exports/requirements.txt
```

### Running the Social Media Bot

```bash
# Start autonomous social media management
python main.py --action social-media
```

## Usage Examples

### Manual Content Generation

```python
from services.social_media.social_media_manager import SocialMediaManager

# Initialize the manager
social_manager = SocialMediaManager(use_mock_api=True)

# Generate and post content immediately
result = social_manager.generate_and_post_content(
    theme="motivation", 
    immediate=True
)

# Schedule content for optimal time
result = social_manager.generate_and_post_content(
    theme="workout_tips", 
    immediate=False
)
```

### Autonomous Operation

```python
# Start fully autonomous operation
result = social_manager.start_autonomous_operation()

# The system will now:
# - Schedule weekly content automatically
# - Post content at optimal times
# - Monitor and respond to engagement
# - Generate performance reports

# Stop autonomous operation
result = social_manager.stop_autonomous_operation()
```

### Performance Analytics

```python
# Generate performance report
report = social_manager.generate_performance_report(period="week")

# Optimize content strategy
optimization = social_manager.optimize_content_strategy()
```

## Configuration

### Posting Schedule

The default posting schedule follows optimal engagement times:

- **Monday**: 8:00 AM (motivation), 5:30 PM (workout_tips)
- **Tuesday**: 9:00 AM (nutrition), 6:00 PM (challenges)
- **Wednesday**: 8:30 AM (member_success), 5:00 PM (gym_promotions)
- **Thursday**: 9:30 AM (workout_tips), 6:30 PM (motivation)
- **Friday**: 8:00 AM (challenges), 5:00 PM (member_success)
- **Saturday**: 10:00 AM (gym_promotions), 3:00 PM (nutrition)
- **Sunday**: 11:00 AM (motivation), 4:00 PM (challenges)

### Content Themes

1. **Motivation**: Inspirational quotes and encouragement
2. **Workout Tips**: Exercise guidance and form tips
3. **Member Success**: Spotlights and transformation stories
4. **Gym Promotions**: Membership offers and facility features
5. **Nutrition**: Healthy eating tips and meal prep advice
6. **Challenges**: Interactive fitness challenges and engagement

## API Integration

### Facebook API (Production)

For production use with real Facebook API:

```python
# Initialize with real Facebook API
social_manager = SocialMediaManager(use_mock_api=False)
```

### Mock API (Development/Testing)

For development and testing:

```python
# Initialize with mock API
social_manager = SocialMediaManager(use_mock_api=True)

# Simulate engagement for testing
result = social_manager.simulate_engagement_for_testing(
    num_comments=3, 
    num_messages=2
)
```

## Testing

### Running Tests

```bash
# Run all social media tests
python tests/test_social_media.py

# Run specific component tests
python -c "from tests.test_social_media import test_content_generator; test_content_generator()"
```

### Test Coverage

The test suite covers:
- Content generation and themes
- Mock Facebook API functionality
- Posting and scheduling
- Engagement monitoring and responses
- Analytics and performance tracking
- Complete workflow integration

## Monitoring & Maintenance

### System Status

```python
# Check system status
status = social_manager.get_system_status()

# Get scheduler status
scheduler_status = social_manager.scheduler.get_scheduler_status()

# View upcoming posts
upcoming = social_manager.scheduler.get_scheduled_posts(days_ahead=7)
```

### Performance Metrics

Key metrics tracked:
- **Engagement Rate**: Likes + Comments + Shares / Reach
- **Reach**: Number of unique users who saw the post
- **Response Time**: Average time to respond to comments/messages
- **Content Performance**: Success rate by theme and format

### Optimization Recommendations

The system provides automatic recommendations for:
- Posting frequency adjustments
- Content theme optimization
- Timing improvements
- Engagement strategy enhancements

## Troubleshooting

### Common Issues

1. **Timezone Errors**: Ensure datetime objects are timezone-aware
2. **API Rate Limits**: Mock API simulates realistic rate limits
3. **Content Generation**: Falls back to templates if AI is unavailable
4. **Scheduling Conflicts**: System prevents duplicate scheduling

### Logs

The system provides comprehensive logging:
- Content generation activities
- Posting attempts and results
- Engagement monitoring
- Performance analytics
- Error handling and recovery

## Security Considerations

- API credentials are managed through the config system
- Mock API is used by default for safety
- Real posting requires explicit configuration
- All sensitive data is excluded from version control

## Future Enhancements

Potential improvements:
- Instagram integration
- Video content generation
- Advanced AI content creation
- Multi-language support
- Enhanced analytics dashboard
- A/B testing capabilities

## Support

For issues or questions:
1. Check the test suite for examples
2. Review logs for error details
3. Use mock API for safe testing
4. Refer to the main gym bot documentation

## License

This module is part of the Anytime Fitness Bot Modular system.