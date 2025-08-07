#!/usr/bin/env python3
"""
Debug script to find Dennis Rost in the database
"""
import sqlite3

def debug_dennis_rost():
    conn = sqlite3.connect('gym_bot.db')
    cursor = conn.cursor()

    print('=== SEARCHING FOR DENNIS ROST ===')

    # Check members table
    print('\n1. Checking MEMBERS table:')
    cursor.execute("""
        SELECT id, first_name, last_name, full_name, email 
        FROM members 
        WHERE LOWER(first_name) LIKE '%dennis%' OR LOWER(last_name) LIKE '%rost%' OR LOWER(full_name) LIKE '%dennis%' OR LOWER(full_name) LIKE '%rost%'
    """)
    members = cursor.fetchall()
    
    if members:
        for member in members:
            print(f'  ✅ ID: {member[0]}, Name: {member[1]} {member[2]}, Full: {member[3]}, Email: {member[4]}')
    else:
        print('  ❌ No Dennis Rost found in members table')

    # Check training_clients table
    print('\n2. Checking TRAINING_CLIENTS table:')
    cursor.execute("""
        SELECT id, member_id, clubos_member_id, member_name 
        FROM training_clients 
        WHERE LOWER(member_name) LIKE '%dennis%' OR LOWER(member_name) LIKE '%rost%'
    """)
    training_clients = cursor.fetchall()
    
    if training_clients:
        for client in training_clients:
            print(f'  ✅ ID: {client[0]}, Member ID: {client[1]}, ClubOS ID: {client[2]}, Name: {client[3]}')
    else:
        print('  ❌ No Dennis Rost found in training_clients table')

    # Check funding cache
    print('\n3. Checking FUNDING_STATUS_CACHE table:')
    cursor.execute("""
        SELECT id, member_id, clubos_member_id, member_name, funding_status 
        FROM funding_status_cache 
        WHERE LOWER(member_name) LIKE '%dennis%' OR LOWER(member_name) LIKE '%rost%'
    """)
    funding = cursor.fetchall()
    
    if funding:
        for fund in funding:
            print(f'  ✅ ID: {fund[0]}, Member ID: {fund[1]}, ClubOS ID: {fund[2]}, Name: {fund[3]}, Status: {fund[4]}')
    else:
        print('  ❌ No Dennis Rost found in funding_status_cache table')

    # Let's also check for similar names (typos, variations)
    print('\n4. Checking for SIMILAR NAMES:')
    cursor.execute("""
        SELECT first_name, last_name, full_name 
        FROM members 
        WHERE first_name LIKE '%Den%' OR last_name LIKE '%Ros%' OR full_name LIKE '%Den%' OR full_name LIKE '%Ros%'
        LIMIT 10
    """)
    similar = cursor.fetchall()
    
    if similar:
        for sim in similar:
            print(f'  🔍 Similar: {sim[0]} {sim[1]} ({sim[2]})')
    else:
        print('  ❌ No similar names found')

    # Check training clients with similar names
    print('\n5. Checking TRAINING_CLIENTS for similar names:')
    cursor.execute("""
        SELECT member_name, clubos_member_id
        FROM training_clients 
        WHERE member_name LIKE '%Den%' OR member_name LIKE '%Ros%'
        LIMIT 10
    """)
    similar_training = cursor.fetchall()
    
    if similar_training:
        for sim in similar_training:
            print(f'  🔍 Training Client: {sim[0]} (ClubOS ID: {sim[1]})')
    else:
        print('  ❌ No similar names in training clients')

    # Get total counts for context
    print('\n6. DATABASE STATS:')
    cursor.execute("SELECT COUNT(*) FROM members")
    total_members = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM training_clients")
    total_training = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM funding_status_cache")
    total_funding = cursor.fetchone()[0]
    
    print(f'  📊 Total Members: {total_members}')
    print(f'  📊 Total Training Clients: {total_training}')
    print(f'  📊 Total Funding Cache: {total_funding}')

    conn.close()

if __name__ == "__main__":
    debug_dennis_rost()
