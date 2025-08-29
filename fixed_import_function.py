def import_fresh_clubhub_data():
    """Import fresh data from ClubHub API on startup"""
    try:
        # Import ClubHub API client
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'services'))
        from api.clubhub_api_client import ClubHubAPIClient
        from config.clubhub_credentials import CLUBHUB_EMAIL, CLUBHUB_PASSWORD
        
        # Initialize and authenticate
        client = ClubHubAPIClient()
        if not client.authenticate(CLUBHUB_EMAIL, CLUBHUB_PASSWORD):
            print("❌ ClubHub authentication failed - using existing database")
            return
        
        print("✅ ClubHub authenticated - importing fresh member data...")
        
        # Get all members from ClubHub
        all_members = []
        page = 1
        page_size = 100
        
        while True:
            members_response = client.get_all_members(page=page, page_size=page_size)
            
            if not members_response or not isinstance(members_response, list):
                break
                
            all_members.extend(members_response)
            page += 1
            
            # If we got less than page_size, we've reached the end
            if len(members_response) < page_size:
                break
        
        print(f"📥 Retrieved {len(all_members)} members from ClubHub")
        
        # Connect to database using absolute path (FIXED: was using relative path)
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'gym_bot.db')
        print(f"📂 Using database: {db_path}")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get existing member IDs for incremental updates (FIXED: was deleting all data)
        cursor.execute("SELECT id FROM members WHERE id IS NOT NULL")
        existing_ids = set(str(row[0]) for row in cursor.fetchall())
        print(f"🔄 Found {len(existing_ids)} existing members, doing smart incremental update...")
        
        # Import fresh member data with incremental updates
        members_added = 0
        members_updated = 0
        
        for member in all_members:
            member_id = str(member.get('id'))
            
            # Check if member already exists
            if member_id in existing_ids:
                # Update existing member
                cursor.execute("""
                    UPDATE members SET
                        guid=?, first_name=?, last_name=?, full_name=?, email=?, mobile_phone=?, 
                        status=?, status_message=?, membership_start=?, membership_end=?, last_visit=?
                    WHERE id=?
                """, (
                    member.get('guid'),
                    member.get('firstName', ''),
                    member.get('lastName', ''),
                    f"{member.get('firstName', '')} {member.get('lastName', '')}".strip(),
                    member.get('email', ''),
                    member.get('mobilePhone', ''),
                    member.get('status', ''),
                    member.get('statusMessage', ''),
                    member.get('membershipStart', ''),
                    member.get('membershipEnd', ''),
                    member.get('lastVisit', ''),
                    member_id
                ))
                members_updated += 1
            else:
                # Add new member
                cursor.execute("""
                    INSERT INTO members (
                        id, guid, first_name, last_name, full_name, email, mobile_phone, 
                        status, status_message, membership_start, membership_end, last_visit
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    member_id,
                    member.get('guid'),
                    member.get('firstName', ''),
                    member.get('lastName', ''),
                    f"{member.get('firstName', '')} {member.get('lastName', '')}".strip(),
                    member.get('email', ''),
                    member.get('mobilePhone', ''),
                    member.get('status', ''),
                    member.get('statusMessage', ''),
                    member.get('membershipStart', ''),
                    member.get('membershipEnd', ''),
                    member.get('lastVisit', '')
                ))
                members_added += 1
        
        conn.commit()
        conn.close()
        
        print(f"✅ Smart data import completed: {members_added} new members, {members_updated} updated members")
        
    except Exception as e:
        print(f"❌ Error importing fresh data: {e}")
        print("📊 Continuing with existing database...")
