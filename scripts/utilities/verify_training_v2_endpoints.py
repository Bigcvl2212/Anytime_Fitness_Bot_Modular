#!/usr/bin/env python3
"""
Verify restored ClubOS Training Package V2 agreements flow.

Uses EnhancedClubOSAPIClient to fetch package agreements for a known test member.
"""

import os
import sys
import json

# Ensure project root is on sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.services.api.enhanced_clubos_client import create_enhanced_clubos_client


def main():
    member_id = os.environ.get("TEST_MEMBER_ID", "66735385")
    client = create_enhanced_clubos_client()
    if not client:
        print("❌ Failed to create EnhancedClubOSAPIClient (check credentials/secrets)")
        sys.exit(1)

    result = client.get_training_packages_for_client(member_id)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()


