#!/usr/bin/env python3
"""
Test enhanced ClubOS service with fallback for Colleen Chrysler
"""

from src.main_app import create_app

def test_colleen_fallback():
    """Test the enhanced ClubOS service fallback functionality"""
    app = create_app()
    with app.app_context():
        print("🔬 Testing enhanced ClubOS service fallback for Colleen Chrysler...")
        
        try:
            from src.services.api.enhanced_clubos_service import get_member_conversation_api
            from src.services.authentication.secure_secrets_manager import SecureSecretsManager
            
            # Get credentials
            secrets_manager = SecureSecretsManager()
            username = secrets_manager.get_secret('clubos-username')
            password = secrets_manager.get_secret('clubos-password')
            
            print(f"✅ Got credentials for {username[:5] if username else 'None'}...")
            
            # Test the enhanced conversation API for Colleen Chrysler
            print("🔍 Testing conversation lookup for Colleen Chrysler...")
            conversation = get_member_conversation_api(username, password, 'Colleen Chrysler')
            
            print(f"📋 Conversation results: {len(conversation) if conversation else 0} messages")
            for i, msg in enumerate(conversation[:3] if conversation else []):
                from_user = msg.get('from', 'N/A')
                content = msg.get('content', 'N/A')[:50]
                source = msg.get('source', 'unknown')
                print(f"  {i+1}: From {from_user} - Content: {content}...")
                print(f"      Source: {source}")
            
        except Exception as e:
            print(f"❌ Error testing enhanced service: {e}")
            import traceback
            traceback.print_exc()

        print("🏁 Test completed")

if __name__ == "__main__":
    test_colleen_fallback()