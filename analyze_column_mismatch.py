#!/usr/bin/env python3

"""
Analyze Training Clients Column Mismatch
=======================================

This script analyzes the exact column count issue in the training clients INSERT statement.
"""

# Count the columns in the INSERT statement
insert_columns = [
    "member_id", "clubos_member_id", "first_name", "last_name", "member_name",
    "email", "phone", "trainer_name", "membership_type", "source",
    "active_packages", "package_summary", "package_details",
    "past_due_amount", "total_past_due", "payment_status",
    "sessions_remaining", "last_session", "financial_summary",
    "last_updated", "created_at"
]

# Count the values being provided
insert_values = [
    "member_id", "clubos_member_id", "first_name", "last_name", "member_name",
    "email", "phone", "trainer_name", "membership_type", "source",
    "active_packages_json", "package_summary", "package_details_json",
    "past_due_amount", "total_past_due", "payment_status",
    "sessions_remaining", "last_session", "financial_summary",
    "last_updated"
]

print("📊 Column Analysis:")
print(f"INSERT columns specified: {len(insert_columns)}")
print(f"Values being provided: {len(insert_values)}")
print(f"Difference: {len(insert_columns) - len(insert_values)}")

print(f"\n📋 INSERT columns ({len(insert_columns)}):")
for i, col in enumerate(insert_columns, 1):
    print(f"  {i:2d}. {col}")

print(f"\n💾 Values provided ({len(insert_values)}):")
for i, val in enumerate(insert_values, 1):
    print(f"  {i:2d}. {val}")

print(f"\n🔍 Missing values:")
missing_columns = insert_columns[len(insert_values):]
for col in missing_columns:
    print(f"  - {col}")

# The created_at is handled by datetime('now') but we need to account for this in our count
print(f"\n💡 ISSUE: The INSERT statement specifies {len(insert_columns)} columns including 'created_at'")
print(f"   But only provides {len(insert_values)} parameter values, with created_at set to datetime('now')")
print(f"   SQLite expects exactly {len(insert_columns)} values or {len(insert_columns)-1} parameters + datetime('now')")