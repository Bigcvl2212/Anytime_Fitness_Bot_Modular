"""Test fixed campaign prospects function"""
from src.services.ai.agent_tools.campaign_tools import get_campaign_prospects

print("\n=== Testing Fixed get_campaign_prospects ===")
result = get_campaign_prospects()

print(f"\nSuccess: {result['success']}")
print(f"Active prospects count: {result['count']}")
print(f"Note: {result.get('note', 'N/A')}")

if result['prospects']:
    print(f"\nSample prospect:")
    sample = result['prospects'][0]
    print(f"  ID: {sample.get('id')}")
    print(f"  Name: {sample.get('name')}")
    print(f"  Email: {sample.get('email')}")
    print(f"  Status: {sample.get('status')}")
