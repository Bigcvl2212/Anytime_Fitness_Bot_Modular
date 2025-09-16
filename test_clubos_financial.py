#!/usr/bin/env python3

from src.services.clubos_integration import ClubOSIntegration
from src.services.database_manager import DatabaseManager

# Test the ClubOS integration with updated logic
integration = ClubOSIntegration()
training_clients = integration.get_training_clients()

print(f'Found {len(training_clients)} training clients')

# Check for past due amounts
past_due_count = 0
for client in training_clients:
    past_due = client.get('past_due_amount', 0)
    total_past_due = client.get('total_past_due', 0)
    if past_due > 0 or total_past_due > 0:
        past_due_count += 1
        print(f'  {client.get("member_name", "Unknown")}: past_due=${past_due}, total=${total_past_due}')

print(f'\nTraining clients with past due amounts: {past_due_count}')

# Save to database
if training_clients:
    db = DatabaseManager()
    success = db.save_training_clients_to_db(training_clients)
    print(f'\nSaved to database: {success}')
    
    # Check database results
    conn = db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM training_clients WHERE past_due_amount > 0 OR total_past_due > 0')
    count = cursor.fetchone()[0]
    print(f'Training clients with past due amounts in database: {count}')
    
    conn.close()
