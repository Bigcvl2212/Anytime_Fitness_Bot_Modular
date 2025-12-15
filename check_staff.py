#!/usr/bin/env python3
"""Check staff member IDs"""
from src.services.database_manager import DatabaseManager
db = DatabaseManager()

# Find Jeremy Mayo and any staff
result = db.execute_query(
    "SELECT prospect_id, full_name FROM members WHERE LOWER(full_name) LIKE ? OR LOWER(full_name) LIKE ?",
    ('%mayo%', '%jeremy%'),
    fetch_all=True
)
print("Potential staff members:")
for r in (result or []):
    print(f"  {dict(r)}")
