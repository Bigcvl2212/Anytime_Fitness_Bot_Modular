#!/usr/bin/env python3
"""
Simple script to check training clients and add missing contact info
"""

import sqlite3

def main():
    conn = sqlite3.connect('gym_bot.db')
    cursor = conn.cursor()
    
    print('=== SEARCHING FOR RASHIDA AND MINDY ===')
    cursor.execute('''SELECT member_id, member_name, first_name, last_name, email, phone, past_due_amount, payment_status 
                      FROM training_clients 
                      WHERE LOWER(member_name) LIKE ? OR LOWER(member_name) LIKE ? 
                      OR LOWER(first_name) LIKE ? OR LOWER(first_name) LIKE ?''', 
                      ('%rashida%', '%mindy%', '%rashida%', '%mindy%'))
    
    results = cursor.fetchall()
    if results:
        print("Found matches:")
        for row in results:
            print(f"ID: {row[0]} | Name: {row[1]} | First: {row[2]} | Last: {row[3]} | Email: {row[4]} | Phone: {row[5]} | Past Due: ${row[6]} | Status: {row[7]}")
    else:
        print('No exact matches found for Rashida or Mindy')
    
    print('\n=== SEARCHING FOR SIMILAR NAMES ===')
    cursor.execute('''SELECT member_id, member_name, first_name, last_name, email, phone, past_due_amount, payment_status 
                      FROM training_clients 
                      WHERE LOWER(member_name) LIKE '%hull%' OR LOWER(member_name) LIKE '%feil%'
                      OR LOWER(last_name) LIKE '%hull%' OR LOWER(last_name) LIKE '%feil%'
                      ORDER BY member_name''')
    
    similar_results = cursor.fetchall()
    if similar_results:
        print("Found similar names:")
        for row in similar_results:
            print(f"ID: {row[0]} | Name: {row[1]} | First: {row[2]} | Last: {row[3]} | Email: {row[4]} | Phone: {row[5]} | Past Due: ${row[6]} | Status: {row[7]}")
    else:
        print('No similar names found')
    
    print('\n=== ANTHONY JORDAN CHECK ===')
    cursor.execute('''SELECT member_id, member_name, first_name, last_name, email, phone, past_due_amount, payment_status 
                      FROM training_clients 
                      WHERE LOWER(member_name) LIKE '%anthony%' OR LOWER(first_name) LIKE '%anthony%'
                      OR LOWER(member_name) LIKE '%jordan%' OR LOWER(last_name) LIKE '%jordan%'
                      ORDER BY member_name''')
    
    anthony_results = cursor.fetchall()
    if anthony_results:
        print("Found Anthony Jordan:")
        for row in anthony_results:
            print(f"ID: {row[0]} | Name: {row[1]} | First: {row[2]} | Last: {row[3]} | Email: {row[4]} | Phone: {row[5]} | Past Due: ${row[6]} | Status: {row[7]}")
    else:
        print('Anthony Jordan not found')
    
    print('\n=== CLIENTS WITH MISSING EMAIL/PHONE ===')
    cursor.execute('''SELECT member_id, member_name, first_name, last_name, email, phone, past_due_amount, payment_status 
                      FROM training_clients 
                      WHERE (email IS NULL OR email = '' OR phone IS NULL OR phone = '')
                      AND past_due_amount > 0
                      ORDER BY past_due_amount DESC
                      LIMIT 10''')
    
    missing_contact = cursor.fetchall()
    if missing_contact:
        print("Clients with missing contact info:")
        for row in missing_contact:
            print(f"ID: {row[0]} | Name: {row[1]} | First: {row[2]} | Last: {row[3]} | Email: {row[4]} | Phone: {row[5]} | Past Due: ${row[6]} | Status: {row[7]}")
    
    conn.close()

if __name__ == '__main__':
    main()