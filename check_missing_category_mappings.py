#!/usr/bin/env python3

import sqlite3
import logging

logging.basicConfig(level=logging.INFO)

def check_status_messages():
    """Check what status messages exist in the database that might need category mappings"""
    try:
        conn = sqlite3.connect('gym_bot.db')
        cursor = conn.cursor()
        
        # Get all unique status messages and their counts
        cursor.execute('''
            SELECT status_message, COUNT(*) as count 
            FROM members 
            WHERE status_message IS NOT NULL AND status_message != ''
            GROUP BY status_message 
            ORDER BY count DESC
        ''')
        
        results = cursor.fetchall()
        
        print(f'📊 Found {len(results)} unique status messages:')
        print('=' * 60)
        
        # Current mapping from messaging.py
        current_mapping = {
            'past-due-6-30': 'Past Due 6-30 days',
            'past-due-30': 'Past Due more than 30 days.',
            'past-due-30-plus': 'Past Due more than 30 days.',
            'past-due-6-30-days': 'Past Due 6-30 days',
            'past-due-more-than-30-days': 'Past Due more than 30 days.',
            'good-standing': 'Member is in good standing',
            'in-good-standing': 'Member is in good standing',
            'green': 'Member is in good standing',
            'comp': 'Comp Member',
            'staff': 'Staff Member',
            'pay-per-visit': 'Pay Per Visit Member',
            'sent-to-collections': 'Sent to Collections',
            'pending-cancel': 'Member is pending cancel',
            'expired': 'Expired',
            'cancelled': 'Account has been cancelled.',
            'yellow': 'Invalid Billing Information.',
            'inactive': 'Inactive',
        }
        
        # Get all mapped status messages
        mapped_status_messages = set(current_mapping.values())
        mapped_status_messages.discard('all_members')
        mapped_status_messages.discard('prospects')
        
        print('✅ Status messages that HAVE category mappings:')
        print('-' * 40)
        
        missing_mappings = []
        
        for status_msg, count in results:
            if status_msg in mapped_status_messages:
                print(f'  ✅ {status_msg} ({count} members)')
            else:
                print(f'  ❌ {status_msg} ({count} members) - NO MAPPING')
                missing_mappings.append((status_msg, count))
        
        print('\n' + '=' * 60)
        print('🔍 STATUS MESSAGES MISSING CATEGORY MAPPINGS:')
        print('-' * 40)
        
        if missing_mappings:
            for status_msg, count in missing_mappings:
                # Suggest potential category names
                suggested_category = status_msg.lower().replace(' ', '-').replace('.', '').replace(',', '')
                print(f"  '{suggested_category}': '{status_msg}',  # {count} members")
        else:
            print('  🎉 All status messages have category mappings!')
        
        conn.close()
        
        return missing_mappings
        
    except Exception as e:
        print(f"❌ Error checking status messages: {e}")
        return []

if __name__ == "__main__":
    check_status_messages()