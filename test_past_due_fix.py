"""Test the fixed past due calculation."""
import sys
sys.path.insert(0, 'src')
import logging
logging.basicConfig(level=logging.WARNING)  # Suppress verbose logging

from services.clubos_integration import ClubOSIntegration

print("Fetching training clients (this takes ~30 seconds)...")
integration = ClubOSIntegration()
clients = integration.get_training_clients()

print(f"\nGot {len(clients)} training clients")
print()

# User's verified list
expected = {
    'Cecilia Gonzalez': 80,
    'Dale Roen': 200,
    'Diego Pastran': 1800,
    'Javae Dixon': 461.78,
    'Joe Benson': 1162.22,
    'Kymberley Marr': 350,
    'Mary Siegmann': 40,
    'Michael Stephens': 120,
    'Miguel Belmontes': 2129.70,
    'Mindy Feilbach': 3420,
    'Rashida Hull': 1169.22,
    'Ziann Crump': 275
}

# Build a name-to-past-due lookup from clients
client_lookup = {}
for c in clients:
    name = c.get('member_name') or c.get('full_name') or c.get('name', '')
    if name:
        past_due = c.get('past_due_amount', 0) or c.get('total_past_due', 0) or 0
        client_lookup[name.lower()] = (name, past_due)

print("=== COMPARING TO USER VERIFIED LIST ===")
print()

# Print comparison - match against lowercased names
print(f"{'Name':<25} {'Expected':>12} {'Found':>12} {'Match':>8}")
print("=" * 60)

matches = 0
close_matches = 0
for exp_name, exp_amount in expected.items():
    # Find the best matching client name
    found_amount = 0
    found_name = "NOT FOUND"
    
    for client_name_lower, (actual_name, amount) in client_lookup.items():
        if exp_name.lower() == client_name_lower:
            found_amount = amount
            found_name = actual_name
            break
    
    diff = abs(found_amount - exp_amount)
    if diff < 1:
        match = "YES"
        matches += 1
    elif diff < 10:
        match = "CLOSE"
        close_matches += 1
    else:
        match = "NO"
    
    print(f"{exp_name:<25} ${exp_amount:>10.2f} ${found_amount:>10.2f} {match:>8}")

print("=" * 60)
print(f"Exact Match: {matches}/12")
print(f"Close Match (within $10): {close_matches}/12")
print(f"Total: {matches + close_matches}/12")

# Also show clients with past due > 0 that we found
print()
print("=== ALL CLIENTS WITH PAST DUE > 0 ===")
for c in clients:
    past_due = c.get('past_due_amount', 0) or c.get('total_past_due', 0)
    if past_due > 0:
        name = c.get('member_name') or c.get('full_name') or c.get('name') or 'Unknown'
        print(f"  {name}: ${past_due:.2f}")

# Show summary counts
total_with_past_due = sum(1 for c in clients if (c.get('past_due_amount', 0) or c.get('total_past_due', 0)) > 0)
total_expected = len([c for c in expected.values() if c > 0])
print()
print(f"Total clients with past due > 0: {total_with_past_due}")
print(f"Expected past due clients: {total_expected}")
