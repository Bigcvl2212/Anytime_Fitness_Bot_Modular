"""Test get_campaign_prospects with ClubHub API"""
from src.services.ai.agent_tools.campaign_tools import get_campaign_prospects

print("Testing get_campaign_prospects...")
result = get_campaign_prospects()

print(f"\nSuccess: {result['success']}")
print(f"Count: {result['count']}")
print(f"Source: {result.get('source', 'N/A')}")

if result['prospects']:
    print(f"\nFirst 3 prospects:")
    for p in result['prospects'][:3]:
        print(f"  - {p.get('id')}: {p.get('name')} - {p.get('email')} - {p.get('phone')}")
else:
    print(f"Error: {result.get('error')}")
