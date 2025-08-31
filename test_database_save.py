#!/usr/bin/env python3
"""Test script to validate database save methods."""

import sys
import os
sys.path.insert(0, 'src')

from services.database_manager import DatabaseManager
from services.api.clubhub_api_client import ClubHubAPIClient  
from config.clubhub_credentials import CLUBHUB_EMAIL, CLUBHUB_PASSWORD
import sqlite3

def test_database_save():
    print('🧪 Testing database save methods...')
    
    # Initialize database manager
    db_manager = DatabaseManager()
    
    # Get a few real prospects from API
    clubhub_client = ClubHubAPIClient()
    if clubhub_client.authenticate(CLUBHUB_EMAIL, CLUBHUB_PASSWORD):
        print('✅ Authenticated to ClubHub')
        
        # Get first 10 prospects for testing
        prospects = clubhub_client.get_all_prospects(page=1, page_size=10) 
        if prospects:
            # Process prospects to ensure full_name is set
            for prospect in prospects:
                prospect['full_name'] = f"{prospect.get('firstName', '')} {prospect.get('lastName', '')}".strip()
            
            print(f'📥 Got {len(prospects)} prospects from API')
            print(f'📝 Sample prospect: {prospects[0].get("firstName")} {prospects[0].get("lastName")}')
            
            # Test database save
            result = db_manager.save_prospects_to_db(prospects)
            print(f'💾 Database save result: {result}')
            
            # Check database count
            conn = sqlite3.connect('gym_bot.db')
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM prospects')
            count = cursor.fetchone()[0]
            print(f'📊 Prospects now in database: {count}')
            conn.close()
            
        else:
            print('❌ No prospects returned from API')
    else:
        print('❌ Authentication failed')

if __name__ == '__main__':
    test_database_save()
