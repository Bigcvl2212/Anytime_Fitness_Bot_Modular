#!/usr/bin/env python3
"""
Test script for enhanced member categorization and revenue calculation
"""

import sqlite3

def test_revenue_calculation():
    conn = sqlite3.connect('gym_bot.db')
    cursor = conn.cursor()

    print('=== TESTING ENHANCED GREEN MEMBER CATEGORIZATION ===')

    # Test enhanced green member query
    cursor.execute("""
        SELECT COUNT(*) as green_count,
               SUM(agreement_recurring_cost) as green_revenue
        FROM members
        WHERE (COALESCE(amount_past_due, 0) = 0)
        AND (status_message NOT LIKE '%Past Due%' OR status_message IS NULL)
        AND (status_message NOT LIKE '%comp%' OR status_message IS NULL)
        AND (status_message NOT LIKE '%staff%' OR status_message IS NULL)
        AND (status_message NOT LIKE '%per visit%' OR status_message IS NULL)
        AND (status_message NOT LIKE '%ppv%' OR status_message IS NULL)
        AND (user_type NOT LIKE '%comp%' OR user_type IS NULL)
        AND (user_type NOT LIKE '%staff%' OR user_type IS NULL)
        AND (user_type NOT LIKE '%ppv%' OR user_type IS NULL)
        AND (status NOT IN ('Inactive','inactive','Suspended','suspended','Cancelled','cancelled') OR status IS NULL)
        AND (email NOT LIKE '%anytimefitness%' OR email IS NULL)
    """)

    green_result = cursor.fetchone()
    green_count, green_revenue = green_result
    print(f'Enhanced Green Members: {green_count} members')
    print(f'Green Member Revenue: ${green_revenue:.2f}')

    print('\n=== REVENUE-GENERATING CATEGORY BREAKDOWN ===')

    # Show breakdown by category
    categories = [
        ('Good Standing', "status_message LIKE '%Member is in good standing%'"),
        ('Active', "status_message LIKE '%Active%'"),
        ('Comp Members', "status_message LIKE '%comp%' OR user_type LIKE '%comp%'"),
        ('Staff Members', "status_message LIKE '%staff%' OR user_type LIKE '%staff%' OR email LIKE '%anytimefitness%'"),
        ('PPV Members', "status_message LIKE '%per visit%' OR status_message LIKE '%ppv%' OR user_type LIKE '%ppv%'"),
        ('Past Due', 'COALESCE(amount_past_due, 0) > 0'),
        ('Inactive', "status IN ('Inactive','inactive','Suspended','suspended','Cancelled','cancelled')")
    ]

    for category_name, condition in categories:
        cursor.execute(f"""
        SELECT COUNT(*) as count,
               SUM(COALESCE(agreement_recurring_cost, 0)) as revenue
        FROM members 
        WHERE {condition}
        """)
        
        count, revenue = cursor.fetchone()
        revenue_amount = revenue or 0
        print(f'{category_name}: {count} members, ${revenue_amount:.2f} revenue')

    print('\n=== TRAINING CLIENT REVENUE ===')
    cursor.execute("""
        SELECT COUNT(*) as training_count,
               SUM(COALESCE(past_due_amount, 0)) as training_revenue
        FROM training_clients
        WHERE past_due_amount > 0 OR payment_status = 'Current'
    """)

    training_result = cursor.fetchone()
    if training_result:
        training_count, training_revenue = training_result
        print(f'Training Clients: {training_count}')
        print(f'Training Revenue: ${training_revenue:.2f}')
    else:
        training_revenue = 0
        print('No training clients found')

    print('\n=== TOTAL MONTHLY REVENUE CALCULATION ===')
    total_revenue = (green_revenue or 0) + (training_revenue or 0)
    print(f'Total Monthly Revenue: ${total_revenue:.2f}')
    print(f'  - Member Revenue: ${green_revenue or 0:.2f}')
    print(f'  - Training Revenue: ${training_revenue or 0:.2f}')

    conn.close()

if __name__ == "__main__":
    test_revenue_calculation()