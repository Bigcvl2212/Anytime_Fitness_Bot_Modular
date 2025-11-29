"""Debug all training clients to see who has past due amounts."""
import sys
sys.path.insert(0, 'src')
import logging
logging.basicConfig(level=logging.WARNING)

from services.clubos_integration import ClubOSIntegration

print("Fetching training clients...")
integration = ClubOSIntegration()
clients = integration.get_training_clients()

print(f"\nTotal clients: {len(clients)}")
print("\nClients with past_due_amount > 0:")
print("-" * 50)

past_due_clients = []
for c in clients:
    name = c.get('member_name') or c.get('full_name') or 'UNKNOWN'
    past_due = c.get('past_due_amount', 0)
    total_past_due = c.get('total_past_due', 0)
    agreement_count = c.get('agreement_count', 0)
    
    if past_due > 0 or total_past_due > 0:
        past_due_clients.append({
            'name': name,
            'past_due_amount': past_due,
            'total_past_due': total_past_due,
            'agreement_count': agreement_count
        })

# Sort by past due amount descending
past_due_clients.sort(key=lambda x: x['past_due_amount'] or x['total_past_due'], reverse=True)

for c in past_due_clients:
    print(f"  {c['name']}: past_due={c['past_due_amount']:.2f}, total={c['total_past_due']:.2f}, agreements={c['agreement_count']}")

print("-" * 50)
print(f"Total with past due > 0: {len(past_due_clients)}")
