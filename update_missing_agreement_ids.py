import sys
sys.path.append('.')
from src.services.database_manager import DatabaseManager
from src.services.api.clubhub_api_client import ClubHubAPIClient

def update_missing_agreement_ids():
    """Update missing agreement IDs for past due members"""
    db = DatabaseManager()
    
    print('🔄 Updating missing agreement IDs for past due members...')
    
    # Get past due members without agreement_id
    missing_agreement_members = db.execute_query("""
        SELECT id, full_name, prospect_id, guid, email, amount_past_due
        FROM members 
        WHERE (status_message LIKE '%Past Due 6-30 days%' 
               OR status_message LIKE '%Past Due more than 30 days%')
          AND agreement_id IS NULL
        ORDER BY amount_past_due DESC
    """)
    
    print(f'📋 Found {len(missing_agreement_members)} past due members without agreement IDs:')
    for member in missing_agreement_members:
        print(f'  - {member["full_name"]}: ${member["amount_past_due"]} (ID: {member["prospect_id"]})')
    
    if not missing_agreement_members:
        print('✅ All past due members already have agreement IDs!')
        return
    
    # Initialize ClubHub API
    try:
        api = ClubHubAPIClient()
        print('✅ ClubHub API client initialized')
    except Exception as e:
        print(f'❌ Error initializing ClubHub API: {e}')
        return
    
    updated_count = 0
    
    for member in missing_agreement_members:
        member_id = member['prospect_id'] or member['guid']
        if not member_id:
            print(f'⚠️ Skipping {member["full_name"]} - no member ID')
            continue
            
        print(f'🔄 Processing {member["full_name"]} (ID: {member_id})...')
        
        try:
            # Get member agreement data from ClubHub API
            agreement_data = api.get_member_agreement(member_id)
            
            if agreement_data and isinstance(agreement_data, dict):
                agreement_id = agreement_data.get('agreementID')
                agreement_guid = agreement_data.get('agreementGuid')
                agreement_type = agreement_data.get('agreementName', 'Membership')
                
                if agreement_id:
                    # Update the member record
                    db.execute_query("""
                        UPDATE members 
                        SET agreement_id = ?, agreement_guid = ?, agreement_type = ?
                        WHERE id = ?
                    """, (agreement_id, agreement_guid, agreement_type, member['id']))
                    
                    print(f'  ✅ Updated: Agreement ID {agreement_id}')
                    updated_count += 1
                else:
                    print(f'  ⚠️ No agreement ID found in API response')
            else:
                print(f'  ⚠️ No agreement data returned from API')
                
        except Exception as e:
            print(f'  ❌ Error processing {member["full_name"]}: {e}')
            
    print(f'\n✅ Updated {updated_count} members with agreement IDs')
    
    if updated_count > 0:
        print('\n🔄 Verifying updates...')
        # Verify the updates
        updated_members = db.execute_query("""
            SELECT full_name, agreement_id, amount_past_due
            FROM members 
            WHERE (status_message LIKE '%Past Due 6-30 days%' 
                   OR status_message LIKE '%Past Due more than 30 days%')
              AND agreement_id IS NOT NULL
            ORDER BY amount_past_due DESC
            LIMIT 10
        """)
        
        print('📋 Past due members with agreement IDs after update:')
        for member in updated_members:
            print(f'  - {member["full_name"]}: Agreement {member["agreement_id"]} (${member["amount_past_due"]})')

if __name__ == "__main__":
    update_missing_agreement_ids()