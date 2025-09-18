"""
Test Campaign System - Verify campaign management functionality
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from src.services.database_manager import DatabaseManager
from src.services.campaign_service import CampaignService
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_campaign_system():
    """Test the campaign management system"""
    try:
        logger.info("🧪 Testing Campaign System...")
        
        # Initialize database manager
        db_path = os.path.join(project_root, 'gym_bot.db')
        db_manager = DatabaseManager(db_path=db_path)
        
        # Initialize database tables
        db_manager.init_database()
        logger.info("✅ Database initialized")
        
        # Initialize campaign service
        campaign_service = CampaignService(db_manager)
        logger.info("✅ Campaign service initialized")
        
        # Test getting campaign status for a category
        status = campaign_service.get_campaign_status('good_standing')
        logger.info(f"📊 Campaign status for 'good_standing': {status}")
        
        # Test creating a campaign template
        template_data = {
            'name': 'Welcome Back Message',
            'category': 'good_standing',
            'message': 'Welcome back! We miss you at the gym. Come in for a free personal training session!',
            'target_group': 'good_standing',
            'max_recipients': 50
        }
        
        template_result = campaign_service.save_template(template_data)
        logger.info(f"📝 Template creation result: {template_result}")
        
        # Test getting templates
        templates = campaign_service.get_templates()
        logger.info(f"📋 Found {len(templates)} templates")
        
        # Test creating a campaign
        campaign_data = {
            'category': 'good_standing',
            'name': 'Test Welcome Campaign',
            'message': 'This is a test welcome message for good standing members.',
            'message_type': 'sms',
            'max_recipients': 10
        }
        
        # Mock recipients for testing
        mock_recipients = [
            {
                'member_id': '12345',
                'full_name': 'John Doe',
                'email': 'john@example.com',
                'phone': '555-0123'
            },
            {
                'member_id': '67890',
                'full_name': 'Jane Smith', 
                'email': 'jane@example.com',
                'phone': '555-0456'
            }
        ]
        
        campaign_result = campaign_service.create_campaign(campaign_data, mock_recipients)
        logger.info(f"🎯 Campaign creation result: {campaign_result}")
        
        if campaign_result.get('status') == 'success':
            campaign_id = campaign_result['campaign_id']
            
            # Test getting campaign progress
            progress = campaign_service.get_campaign_progress(campaign_id)
            logger.info(f"📊 Campaign progress: {progress}")
            
            # Test campaign status update
            campaign_status = campaign_service.get_campaign_status('good_standing')
            logger.info(f"📊 Updated campaign status: {campaign_status}")
        
        logger.info("✅ Campaign system test completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Campaign system test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_campaign_system()
    if success:
        print("✅ Campaign system is working correctly!")
    else:
        print("❌ Campaign system test failed!")
        sys.exit(1)