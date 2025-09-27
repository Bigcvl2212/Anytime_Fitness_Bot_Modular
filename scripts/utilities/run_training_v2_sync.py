#!/usr/bin/env python3
import os
import sys
import json
import time
from typing import List, Dict, Any

# Ensure project root is importable
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.services.api.clubos_training_api import ClubOSTrainingPackageAPI


def sync_training_v2(max_clients: int = 10) -> Dict[str, Any]:
    api = ClubOSTrainingPackageAPI()
    if not api.authenticate():
        return {"success": False, "error": "Authentication failed"}

    # 1) Get training clients (assignees)
    assignees = api.fetch_assignees() or []
    if not assignees:
        return {"success": False, "error": "No assignees returned"}

    results: List[Dict[str, Any]] = []
    processed = 0

    for a in assignees:
        if processed >= max_clients:
            break
        member_id = str(a.get("id") or "").strip()
        full_name = a.get("name", "Unknown").strip()
        if not member_id:
            continue

        # 2) Discover agreement IDs for the member
        agreement_ids = api.discover_member_agreement_ids(member_id) or []
        agreements: List[Dict[str, Any]] = []

        # 3) For each agreement, get V2 invoices/details
        for aid in agreement_ids:
            v2 = api.get_package_agreement_details(aid)
            if isinstance(v2, dict) and v2.get("success"):
                agreements.append({
                    "agreement_id": v2.get("agreement_id"),
                    "past_due_amount": v2.get("past_due_amount"),
                    "total_invoices": v2.get("total_invoices"),
                })
            else:
                agreements.append({
                    "agreement_id": str(aid),
                    "error": (v2 or {}).get("error") if isinstance(v2, dict) else "unknown",
                })
            # Be polite like a browser
            time.sleep(0.2)

        results.append({
            "member_id": member_id,
            "name": full_name,
            "agreements": agreements,
        })
        processed += 1
        time.sleep(0.2)

    return {"success": True, "count": len(results), "clients": results}


def main():
    max_clients = int(os.environ.get("MAX_CLIENTS", "5"))
    out = sync_training_v2(max_clients=max_clients)
    print(json.dumps(out))


if __name__ == "__main__":
    main()

