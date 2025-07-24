#!/usr/bin/env python3

import os
import sqlite3
import pandas as pd
from flask import Flask, render_template, jsonify, request, redirect, url_for
from datetime import datetime, timedelta
import logging
import json

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path='gym_bot.db'):
        self.db_path = db_path
        self.init_database()
        
    def init_database(self):
        """Initialize the database with required tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Drop existing tables to recreate with new schema
        cursor.execute('DROP TABLE IF EXISTS members')
        cursor.execute('DROP TABLE IF EXISTS prospects')
        cursor.execute('DROP TABLE IF EXISTS training_clients')
        
        # Enhanced members table with agreement fields
        cursor.execute('''
            CREATE TABLE members (
                id INTEGER PRIMARY KEY,
                guid TEXT,
                club_id INTEGER,
                first_name TEXT,
                last_name TEXT,
                full_name TEXT,
                email TEXT,
                mobile_phone TEXT,
                home_phone TEXT,
                work_phone TEXT,
                address1 TEXT,
                address2 TEXT,
                city TEXT,
                state TEXT,
                zip_code TEXT,
                country TEXT,
                date_of_birth DATE,
                gender TEXT,
                membership_start DATE,
                membership_end DATE,
                last_visit DATE,
                status TEXT,
                status_message TEXT,
                user_type TEXT,
                key_fob TEXT,
                photo_url TEXT,
                
                -- Home Club Information
                home_club_name TEXT,
                home_club_address TEXT,
                home_club_city TEXT,
                home_club_state TEXT,
                home_club_zip TEXT,
                home_club_af_number TEXT,
                
                -- Agreement Information
                agreement_id TEXT,
                agreement_guid TEXT,
                agreement_status TEXT,
                agreement_start_date DATE,
                agreement_end_date DATE,
                agreement_type TEXT,
                agreement_rate REAL,
                
                -- Agreement History
                agreement_history_count INTEGER DEFAULT 0,
                past_agreements TEXT, -- JSON format
                
                -- Payment Information
                payment_token TEXT,
                card_type TEXT,
                card_last4 TEXT,
                expiration_month TEXT,
                expiration_year TEXT,
                billing_name TEXT,
                billing_address TEXT,
                billing_city TEXT,
                billing_state TEXT,
                billing_zip TEXT,
                account_type TEXT,
                routing_number TEXT,
                
                -- Additional Fields
                emergency_contact TEXT,
                emergency_phone TEXT,
                employer TEXT,
                occupation TEXT,
                has_app BOOLEAN DEFAULT 0,
                last_activity_timestamp TEXT,
                contract_types TEXT,
                bucket INTEGER,
                color INTEGER,
                rating INTEGER,
                source TEXT,
                trial BOOLEAN DEFAULT 0,
                originated_from TEXT,
                
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Enhanced prospects table
        cursor.execute('''
            CREATE TABLE prospects (
                id INTEGER PRIMARY KEY,
                guid TEXT,
                club_id INTEGER,
                first_name TEXT,
                last_name TEXT,
                full_name TEXT,
                email TEXT,
                mobile_phone TEXT,
                home_phone TEXT,
                work_phone TEXT,
                address1 TEXT,
                address2 TEXT,
                city TEXT,
                state TEXT,
                zip_code TEXT,
                country TEXT,
                date_of_birth DATE,
                gender TEXT,
                status TEXT,
                status_message TEXT,
                
                -- Prospect-specific fields
                lead_source TEXT,
                interest_level INTEGER,
                follow_up_date DATE,
                notes TEXT,
                trial_session_date DATE,
                tour_completed BOOLEAN DEFAULT 0,
                
                -- Contact preferences
                preferred_contact_method TEXT,
                best_time_to_call TEXT,
                
                -- Additional tracking
                bucket INTEGER,
                color INTEGER,
                rating INTEGER,
                source TEXT,
                trial BOOLEAN DEFAULT 1,
                originated_from TEXT,
                
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Training clients table
        cursor.execute('''
            CREATE TABLE training_clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                member_id INTEGER,
                trainer_name TEXT,
                session_type TEXT,
                sessions_remaining INTEGER DEFAULT 0,
                last_session DATE,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (member_id) REFERENCES members (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def import_master_contact_list(self, csv_path):
        """Import master contact list from CSV with comprehensive data."""
        if not os.path.exists(csv_path):
            logger.warning(f"Master contact list not found: {csv_path}")
            return
            
        logger.info(f"Importing master contact list from: {csv_path}")
        
        df = pd.read_csv(csv_path)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Clear existing data
        cursor.execute('DELETE FROM members')
        cursor.execute('DELETE FROM prospects')
        
        members_count = 0
        prospects_count = 0
        
        for _, row in df.iterrows():
            try:
                # Determine if this is a member or prospect
                is_prospect = str(row.get('prospect', 'False')).lower() == 'true'
                
                # Common fields
                common_data = {
                    'id': row.get('id'),
                    'guid': row.get('guid'),
                    'club_id': row.get('clubId'),
                    'first_name': row.get('firstName'),
                    'last_name': row.get('lastName'),
                    'full_name': f"{row.get('firstName', '')} {row.get('lastName', '')}".strip(),
                    'email': row.get('email'),
                    'mobile_phone': row.get('mobilePhone'),
                    'home_phone': row.get('homePhone'),
                    'work_phone': row.get('workPhone'),
                    'address1': row.get('address1'),
                    'address2': row.get('address2'),
                    'city': row.get('city'),
                    'state': row.get('state'),
                    'zip_code': row.get('zip'),
                    'country': row.get('country'),
                    'date_of_birth': row.get('dateOfBirth'),
                    'gender': 'Female' if str(row.get('female', '')).lower() == 'true' else 'Male' if str(row.get('female', '')).lower() == 'false' else 'Unknown',
                    'status': row.get('status'),
                    'status_message': row.get('statusMessage'),
                    'bucket': row.get('bucket'),
                    'color': row.get('color'),
                    'rating': row.get('rating'),
                    'source': row.get('source'),
                    'trial': str(row.get('trial', 'False')).lower() == 'true',
                    'originated_from': row.get('originatedFrom')
                }
                
                if is_prospect:
                    # Insert as prospect
                    prospect_data = {
                        **common_data,
                        'lead_source': row.get('source'),
                        'interest_level': row.get('rating', 0),
                        'notes': row.get('statusMessage', ''),
                    }
                    
                    columns = ', '.join(prospect_data.keys())
                    placeholders = ', '.join(['?' for _ in prospect_data.values()])
                    
                    cursor.execute(f'''
                        INSERT OR REPLACE INTO prospects ({columns})
                        VALUES ({placeholders})
                    ''', list(prospect_data.values()))
                    
                    prospects_count += 1
                    
                else:
                    # Insert as member with agreement data
                    member_data = {
                        **common_data,
                        'membership_start': row.get('membershipStart'),
                        'membership_end': row.get('membershipEnd'),
                        'last_visit': row.get('lastVisit'),
                        'user_type': row.get('userType'),
                        'key_fob': row.get('keyFob'),
                        'photo_url': row.get('photoUrl'),
                        
                        # Home Club Information
                        'home_club_name': row.get('homeClub_name'),
                        'home_club_address': row.get('homeClub_address1'),
                        'home_club_city': row.get('homeClub_city'),
                        'home_club_state': row.get('homeClub_state'),
                        'home_club_zip': row.get('homeClub_zip'),
                        'home_club_af_number': row.get('homeClub_afNumber'),
                        
                        # Agreement Information
                        'agreement_id': row.get('agreement_agreementID'),
                        'agreement_guid': row.get('agreement_agreementGuid'),
                        'agreement_status': row.get('agreement_status'),
                        'agreement_start_date': row.get('agreement_startDate'),
                        'agreement_end_date': row.get('agreement_endDate'),
                        'agreement_type': row.get('agreement_type'),
                        'agreement_rate': row.get('agreement_rate'),
                        
                        # Agreement History
                        'agreement_history_count': row.get('agreementHistory_count', 0),
                        
                        # Payment Information
                        'payment_token': row.get('agreementTokenQuery_paymentToken'),
                        'card_type': row.get('agreementTokenQuery_cardType'),
                        'card_last4': row.get('agreementTokenQuery_accountLast4'),
                        'expiration_month': row.get('agreementTokenQuery_expirationMonth'),
                        'expiration_year': row.get('agreementTokenQuery_expirationYear'),
                        'billing_name': row.get('agreementTokenQuery_holderName'),
                        'billing_address': row.get('agreementTokenQuery_holderStreet'),
                        'billing_city': row.get('agreementTokenQuery_holderCity'),
                        'billing_state': row.get('agreementTokenQuery_holderState'),
                        'billing_zip': row.get('agreementTokenQuery_holderZip'),
                        'account_type': row.get('agreementTokenQuery_accountType'),
                        'routing_number': row.get('agreementTokenQuery_routingNumber'),
                        
                        # Additional Fields
                        'emergency_contact': row.get('emergencyContact'),
                        'emergency_phone': row.get('emergencyPhone'),
                        'employer': row.get('employer'),
                        'occupation': row.get('occupation'),
                        'has_app': str(row.get('hasApp', 'False')).lower() == 'true',
                        'last_activity_timestamp': row.get('lastActivityTimestamp'),
                        'contract_types': row.get('contractTypes')
                    }
                    
                    columns = ', '.join(member_data.keys())
                    placeholders = ', '.join(['?' for _ in member_data.values()])
                    
                    cursor.execute(f'''
                        INSERT OR REPLACE INTO members ({columns})
                        VALUES ({placeholders})
                    ''', list(member_data.values()))
                    
                    members_count += 1
                    
            except Exception as e:
                logger.error(f"Error importing row {row.get('id', 'unknown')}: {e}")
                continue
        
        conn.commit()
        conn.close()
        
        logger.info(f"Import complete: {members_count} members, {prospects_count} prospects")
        return members_count, prospects_count

# Initialize database manager
db_manager = DatabaseManager()

# Import the latest master contact list with agreements
latest_csv = "master_contact_list_with_agreements_20250722_180712.csv"
if os.path.exists(latest_csv):
    db_manager.import_master_contact_list(latest_csv)

@app.route('/')
def dashboard():
    """Main dashboard with overview."""
    conn = sqlite3.connect(db_manager.db_path)
    cursor = conn.cursor()
    
    # Get counts
    cursor.execute("SELECT COUNT(*) FROM members")
    total_members = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM prospects")
    total_prospects = cursor.fetchone()[0]
    
    # Get recent members
    cursor.execute("SELECT * FROM members ORDER BY created_at DESC LIMIT 5")
    recent_members = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]
    
    # Get recent prospects
    cursor.execute("SELECT * FROM prospects ORDER BY created_at DESC LIMIT 5")
    recent_prospects = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]
    
    # Get training clients
    cursor.execute("SELECT COUNT(*) FROM training_clients")
    total_training_clients = cursor.fetchone()[0]
    
    conn.close()
    
    return render_template('dashboard.html', 
                         total_members=total_members,
                         total_prospects=total_prospects,
                         total_training_clients=total_training_clients,
                         recent_members=recent_members,
                         recent_prospects=recent_prospects)

@app.route('/members')
def members_page():
    """Members page - Active paying members only."""
    conn = sqlite3.connect(db_manager.db_path)
    cursor = conn.cursor()
    
    # Get search parameters
    search = request.args.get('search', '')
    page = int(request.args.get('page', 1))
    per_page = 25
    offset = (page - 1) * per_page
    
    # Build query
    where_clause = ""
    params = []
    
    if search:
        where_clause = "WHERE (first_name LIKE ? OR last_name LIKE ? OR email LIKE ? OR mobile_phone LIKE ?)"
        search_term = f"%{search}%"
        params = [search_term, search_term, search_term, search_term]
    
    # Get total count
    cursor.execute(f"SELECT COUNT(*) FROM members {where_clause}", params)
    total_members = cursor.fetchone()[0]
    
    # Get members with pagination
    cursor.execute(f'''
        SELECT * FROM members {where_clause} 
        ORDER BY full_name 
        LIMIT ? OFFSET ?
    ''', params + [per_page, offset])
    
    members = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]
    
    conn.close()
    
    # Calculate pagination
    total_pages = (total_members + per_page - 1) // per_page
    has_prev = page > 1
    has_next = page < total_pages
    
    return render_template('members.html', 
                         members=members,
                         search=search,
                         page=page,
                         total_pages=total_pages,
                         total_members=total_members,
                         has_prev=has_prev,
                         has_next=has_next,
                         per_page=per_page)

@app.route('/prospects')
def prospects_page():
    """Prospects page - Potential members only."""
    conn = sqlite3.connect(db_manager.db_path)
    cursor = conn.cursor()
    
    # Get search parameters
    search = request.args.get('search', '')
    page = int(request.args.get('page', 1))
    per_page = 50
    offset = (page - 1) * per_page
    
    # Build query
    where_clause = ""
    params = []
    
    if search:
        where_clause = "WHERE (first_name LIKE ? OR last_name LIKE ? OR email LIKE ? OR mobile_phone LIKE ?)"
        search_term = f"%{search}%"
        params = [search_term, search_term, search_term, search_term]
    
    # Get total count
    cursor.execute(f"SELECT COUNT(*) FROM prospects {where_clause}", params)
    total_prospects = cursor.fetchone()[0]
    
    # Get prospects with pagination
    cursor.execute(f'''
        SELECT * FROM prospects {where_clause} 
        ORDER BY full_name 
        LIMIT ? OFFSET ?
    ''', params + [per_page, offset])
    
    prospects = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]
    
    conn.close()
    
    # Calculate pagination
    total_pages = (total_prospects + per_page - 1) // per_page
    has_prev = page > 1
    has_next = page < total_pages
    
    return render_template('prospects.html', 
                         prospects=prospects,
                         search=search,
                         page=page,
                         total_pages=total_pages,
                         total_prospects=total_prospects,
                         has_prev=has_prev,
                         has_next=has_next,
                         per_page=per_page)

@app.route('/member/<int:member_id>')
def member_detail(member_id):
    """Detailed view of a specific member."""
    conn = sqlite3.connect(db_manager.db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM members WHERE id = ?", (member_id,))
    row = cursor.fetchone()
    
    if not row:
        return redirect(url_for('members_page'))
    
    member = dict(zip([col[0] for col in cursor.description], row))
    
    # Get training sessions for this member
    cursor.execute('''
        SELECT * FROM training_clients 
        WHERE member_id = ? 
        ORDER BY created_at DESC
    ''', (member_id,))
    
    training_sessions = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]
    
    conn.close()
    
    return render_template('member_detail.html', member=member, training_sessions=training_sessions)

@app.route('/prospect/<int:prospect_id>')
def prospect_detail(prospect_id):
    """Detailed view of a specific prospect."""
    conn = sqlite3.connect(db_manager.db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM prospects WHERE id = ?", (prospect_id,))
    row = cursor.fetchone()
    
    if not row:
        return redirect(url_for('prospects_page'))
    
    prospect = dict(zip([col[0] for col in cursor.description], row))
    
    conn.close()
    
    return render_template('prospect_detail.html', prospect=prospect)

@app.route('/training-clients')
def training_clients_page():
    """Training clients page."""
    conn = sqlite3.connect(db_manager.db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT tc.*, m.full_name as member_name 
        FROM training_clients tc 
        LEFT JOIN members m ON tc.member_id = m.id 
        ORDER BY tc.created_at DESC
    ''')
    clients = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]
    
    conn.close()
    
    return render_template('training_clients.html', clients=clients)

def create_templates():
    """Create HTML templates with proper Anytime Fitness branding and enhanced member/prospect displays."""
    templates_dir = 'templates'
    if not os.path.exists(templates_dir):
        os.makedirs(templates_dir)
    
    # Base template with official Anytime Fitness branding
    base_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Anytime Fitness Club Management{% endblock %}</title>
    
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Font Awesome -->
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    
    <style>
        :root {
            --af-purple: #663399;
            --af-light-purple: #8A4FBE;
            --af-dark-purple: #4A2570;
            --af-white: #FFFFFF;
            --af-light-gray: #F8F9FA;
            --af-gray: #6C757D;
            --af-success: #28A745;
            --af-warning: #FFC107;
            --af-danger: #DC3545;
        }
        
        body {
            background-color: var(--af-light-gray);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        .navbar {
            background: linear-gradient(135deg, var(--af-purple) 0%, var(--af-dark-purple) 100%);
            box-shadow: 0 2px 10px rgba(102, 51, 153, 0.3);
        }
        
        .navbar-brand {
            font-weight: bold;
            font-size: 1.5rem;
            color: var(--af-white) !important;
        }
        
        .nav-link {
            color: var(--af-white) !important;
            transition: all 0.3s ease;
            margin: 0 5px;
            border-radius: 5px;
        }
        
        .nav-link:hover {
            background-color: rgba(255, 255, 255, 0.2);
            transform: translateY(-1px);
        }
        
        .nav-link.active {
            background-color: var(--af-light-purple) !important;
        }
        
        .card {
            border: none;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
        }
        
        .card-header {
            background: linear-gradient(135deg, var(--af-purple) 0%, var(--af-light-purple) 100%);
            color: var(--af-white);
            border-radius: 15px 15px 0 0 !important;
            border: none;
            padding: 1.5rem;
        }
        
        .btn-purple {
            background: linear-gradient(135deg, var(--af-purple) 0%, var(--af-light-purple) 100%);
            border: none;
            color: var(--af-white);
            border-radius: 25px;
            padding: 10px 25px;
            transition: all 0.3s ease;
        }
        
        .btn-purple:hover {
            background: linear-gradient(135deg, var(--af-dark-purple) 0%, var(--af-purple) 100%);
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 51, 153, 0.4);
            color: var(--af-white);
        }
        
        .badge-purple {
            background-color: var(--af-purple);
            color: var(--af-white);
        }
        
        .text-purple { color: var(--af-purple) !important; }
        
        .member-card, .prospect-card {
            border-left: 5px solid var(--af-purple);
            margin-bottom: 1rem;
            transition: all 0.3s ease;
        }
        
        .member-card:hover, .prospect-card:hover {
            border-left-color: var(--af-light-purple);
            box-shadow: 0 8px 20px rgba(102, 51, 153, 0.2);
        }
        
        .agreement-info {
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            border-radius: 10px;
            padding: 1rem;
            margin: 1rem 0;
        }
        
        .payment-info {
            background: linear-gradient(135deg, #e8f5e8 0%, #d4edda 100%);
            border-radius: 10px;
            padding: 1rem;
            margin: 1rem 0;
        }
        
        .contact-info {
            background: linear-gradient(135deg, #fff3cd 0%, #ffeeba 100%);
            border-radius: 10px;
            padding: 1rem;
            margin: 1rem 0;
        }
        
        .search-bar {
            border-radius: 25px;
            border: 2px solid var(--af-purple);
            padding: 10px 20px;
        }
        
        .search-bar:focus {
            border-color: var(--af-light-purple);
            box-shadow: 0 0 0 0.2rem rgba(102, 51, 153, 0.25);
        }
        
        .pagination .page-link {
            color: var(--af-purple);
            border-color: var(--af-purple);
        }
        
        .pagination .page-item.active .page-link {
            background-color: var(--af-purple);
            border-color: var(--af-purple);
        }
        
        .stat-card {
            background: linear-gradient(135deg, var(--af-white) 0%, var(--af-light-gray) 100%);
            border-left: 5px solid var(--af-purple);
            padding: 2rem;
            border-radius: 15px;
            text-align: center;
        }
        
        .stat-number {
            font-size: 3rem;
            font-weight: bold;
            color: var(--af-purple);
            margin-bottom: 0.5rem;
        }
        
        .stat-label {
            color: var(--af-gray);
            font-size: 1.1rem;
        }
        
        .detail-section {
            margin-bottom: 2rem;
        }
        
        .detail-label {
            font-weight: bold;
            color: var(--af-purple);
            margin-right: 10px;
        }
        
        .detail-value {
            color: var(--af-gray);
        }
        
        .table-purple thead {
            background: linear-gradient(135deg, var(--af-purple) 0%, var(--af-light-purple) 100%);
            color: var(--af-white);
        }
        
        .status-active { color: var(--af-success); }
        .status-inactive { color: var(--af-danger); }
        .status-trial { color: var(--af-warning); }
        
        @media (max-width: 768px) {
            .stat-number { font-size: 2rem; }
            .card { margin-bottom: 1rem; }
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark">
        <div class="container-fluid">
            <a class="navbar-brand" href="/">
                <i class="fas fa-dumbbell me-2"></i>
                Anytime Fitness Management
            </a>
            
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav me-auto">
                    <li class="nav-item">
                        <a class="nav-link" href="/"><i class="fas fa-tachometer-alt me-1"></i>Dashboard</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/members"><i class="fas fa-users me-1"></i>Members</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/prospects"><i class="fas fa-user-plus me-1"></i>Prospects</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/training-clients"><i class="fas fa-dumbbell me-1"></i>Training</a>
                    </li>
                </ul>
                
                <ul class="navbar-nav">
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle" href="#" id="navbarDropdown" role="button" data-bs-toggle="dropdown">
                            <i class="fas fa-user-circle me-1"></i>Admin
                        </a>
                        <ul class="dropdown-menu">
                            <li><a class="dropdown-item" href="#"><i class="fas fa-cog me-2"></i>Settings</a></li>
                            <li><a class="dropdown-item" href="#"><i class="fas fa-download me-2"></i>Export Data</a></li>
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="dropdown-item" href="#"><i class="fas fa-sign-out-alt me-2"></i>Logout</a></li>
                        </ul>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <main class="container-fluid py-4">
        {% block content %}{% endblock %}
    </main>

    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    
    {% block scripts %}{% endblock %}
</body>
</html>'''
    
    with open(f'{templates_dir}/base.html', 'w') as f:
        f.write(base_template)
    
    # Dashboard template
    dashboard_template = '''{% extends "base.html" %}

{% block title %}Dashboard - Anytime Fitness Management{% endblock %}

{% block content %}
<div class="row mb-4">
    <div class="col-12">
        <h1 class="text-purple mb-3">
            <i class="fas fa-tachometer-alt me-2"></i>
            Club Dashboard
        </h1>
        <p class="lead text-muted">Welcome to your Anytime Fitness club management system</p>
    </div>
</div>

<!-- Statistics Cards -->
<div class="row mb-4">
    <div class="col-md-3 mb-3">
        <div class="stat-card">
            <div class="stat-number">{{ total_members }}</div>
            <div class="stat-label">Active Members</div>
        </div>
    </div>
    <div class="col-md-3 mb-3">
        <div class="stat-card">
            <div class="stat-number">{{ total_prospects }}</div>
            <div class="stat-label">Prospects</div>
        </div>
    </div>
    <div class="col-md-3 mb-3">
        <div class="stat-card">
            <div class="stat-number">{{ total_training_clients }}</div>
            <div class="stat-label">Training Clients</div>
        </div>
    </div>
    <div class="col-md-3 mb-3">
        <div class="stat-card">
            <div class="stat-number">{{ total_members + total_prospects }}</div>
            <div class="stat-label">Total Contacts</div>
        </div>
    </div>
</div>

<!-- Quick Access Cards -->
<div class="row mb-4">
    <div class="col-md-6 mb-3">
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0"><i class="fas fa-users me-2"></i>Recent Members</h5>
            </div>
            <div class="card-body">
                {% if recent_members %}
                    {% for member in recent_members %}
                    <div class="d-flex justify-content-between align-items-center py-2 border-bottom">
                        <div>
                            <strong>{{ member.full_name }}</strong><br>
                            <small class="text-muted">{{ member.email }}</small>
                        </div>
                        <a href="/member/{{ member.id }}" class="btn btn-sm btn-purple">
                            <i class="fas fa-eye"></i>
                        </a>
                    </div>
                    {% endfor %}
                {% else %}
                    <p class="text-muted">No recent members</p>
                {% endif %}
                <div class="text-center mt-3">
                    <a href="/members" class="btn btn-purple">
                        <i class="fas fa-users me-2"></i>View All Members
                    </a>
                </div>
            </div>
        </div>
    </div>
    
    <div class="col-md-6 mb-3">
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0"><i class="fas fa-user-plus me-2"></i>Recent Prospects</h5>
            </div>
            <div class="card-body">
                {% if recent_prospects %}
                    {% for prospect in recent_prospects %}
                    <div class="d-flex justify-content-between align-items-center py-2 border-bottom">
                        <div>
                            <strong>{{ prospect.full_name }}</strong><br>
                            <small class="text-muted">{{ prospect.email }}</small>
                        </div>
                        <a href="/prospect/{{ prospect.id }}" class="btn btn-sm btn-purple">
                            <i class="fas fa-eye"></i>
                        </a>
                    </div>
                    {% endfor %}
                {% else %}
                    <p class="text-muted">No recent prospects</p>
                {% endif %}
                <div class="text-center mt-3">
                    <a href="/prospects" class="btn btn-purple">
                        <i class="fas fa-user-plus me-2"></i>View All Prospects
                    </a>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}'''
    
    with open(f'{templates_dir}/dashboard.html', 'w') as f:
        f.write(dashboard_template)
    
    # Members template with full agreement information
    members_template = '''{% extends "base.html" %}

{% block title %}Members - Anytime Fitness Management{% endblock %}

{% block content %}
<div class="row mb-4">
    <div class="col-12">
        <h1 class="text-purple mb-3">
            <i class="fas fa-users me-2"></i>
            Active Members
            <span class="badge badge-purple ms-3">{{ total_members }} Total</span>
        </h1>
        <p class="lead text-muted">Manage your active paying members with complete agreement information</p>
    </div>
</div>

<!-- Search and Controls -->
<div class="row mb-4">
    <div class="col-md-8">
        <form method="GET" class="d-flex">
            <input type="text" name="search" class="form-control search-bar me-2" 
                   placeholder="Search members by name, email, or phone..." 
                   value="{{ search }}">
            <button type="submit" class="btn btn-purple">
                <i class="fas fa-search"></i>
            </button>
        </form>
    </div>
    <div class="col-md-4 text-end">
        <a href="/member/new" class="btn btn-purple">
            <i class="fas fa-plus me-2"></i>Add New Member
        </a>
    </div>
</div>

<!-- Members List -->
<div class="row">
    {% for member in members %}
    <div class="col-12 mb-4">
        <div class="card member-card">
            <div class="card-body">
                <div class="row">
                    <!-- Basic Info -->
                    <div class="col-md-3">
                        <h5 class="text-purple mb-2">
                            <i class="fas fa-user me-2"></i>
                            {{ member.full_name }}
                        </h5>
                        <p class="mb-1">
                            <i class="fas fa-id-card me-2 text-muted"></i>
                            <strong>ID:</strong> {{ member.id }}
                        </p>
                        {% if member.email %}
                        <p class="mb-1">
                            <i class="fas fa-envelope me-2 text-muted"></i>
                            <a href="mailto:{{ member.email }}">{{ member.email }}</a>
                        </p>
                        {% endif %}
                        {% if member.mobile_phone %}
                        <p class="mb-1">
                            <i class="fas fa-phone me-2 text-muted"></i>
                            <a href="tel:{{ member.mobile_phone }}">{{ member.mobile_phone }}</a>
                        </p>
                        {% endif %}
                        <p class="mb-1">
                            <i class="fas fa-calendar me-2 text-muted"></i>
                            <strong>Since:</strong> {{ member.membership_start or 'N/A' }}
                        </p>
                    </div>
                    
                    <!-- Address & Club Info -->
                    <div class="col-md-3">
                        <h6 class="text-purple mb-2">
                            <i class="fas fa-map-marker-alt me-2"></i>Address
                        </h6>
                        <p class="mb-1">{{ member.address1 or 'N/A' }}</p>
                        {% if member.address2 %}
                        <p class="mb-1">{{ member.address2 }}</p>
                        {% endif %}
                        <p class="mb-1">{{ member.city or 'N/A' }}, {{ member.state or 'N/A' }} {{ member.zip_code or '' }}</p>
                        
                        {% if member.home_club_name %}
                        <h6 class="text-purple mb-2 mt-3">
                            <i class="fas fa-building me-2"></i>Home Club
                        </h6>
                        <p class="mb-1"><strong>{{ member.home_club_name }}</strong></p>
                        <p class="mb-1">{{ member.home_club_address or '' }}</p>
                        <p class="mb-1">{{ member.home_club_city or '' }}, {{ member.home_club_state or '' }} {{ member.home_club_zip or '' }}</p>
                        {% endif %}
                    </div>
                    
                    <!-- Agreement Info -->
                    <div class="col-md-3">
                        {% if member.agreement_id %}
                        <div class="agreement-info">
                            <h6 class="text-purple mb-2">
                                <i class="fas fa-file-contract me-2"></i>Agreement
                            </h6>
                            <p class="mb-1"><strong>ID:</strong> {{ member.agreement_id }}</p>
                            {% if member.agreement_status %}
                            <p class="mb-1"><strong>Status:</strong> 
                                <span class="badge bg-success">{{ member.agreement_status }}</span>
                            </p>
                            {% endif %}
                            {% if member.agreement_start_date %}
                            <p class="mb-1"><strong>Start:</strong> {{ member.agreement_start_date }}</p>
                            {% endif %}
                            {% if member.agreement_end_date %}
                            <p class="mb-1"><strong>End:</strong> {{ member.agreement_end_date }}</p>
                            {% endif %}
                            {% if member.agreement_rate %}
                            <p class="mb-1"><strong>Rate:</strong> ${{ member.agreement_rate }}</p>
                            {% endif %}
                            {% if member.agreement_history_count and member.agreement_history_count > 0 %}
                            <p class="mb-1"><strong>History:</strong> {{ member.agreement_history_count }} agreements</p>
                            {% endif %}
                        </div>
                        {% endif %}
                    </div>
                    
                    <!-- Payment Info -->
                    <div class="col-md-3">
                        {% if member.payment_token or member.card_type %}
                        <div class="payment-info">
                            <h6 class="text-purple mb-2">
                                <i class="fas fa-credit-card me-2"></i>Payment
                            </h6>
                            {% if member.card_type %}
                            <p class="mb-1"><strong>Card:</strong> {{ member.card_type }}</p>
                            {% endif %}
                            {% if member.card_last4 %}
                            <p class="mb-1"><strong>Last 4:</strong> ****{{ member.card_last4 }}</p>
                            {% endif %}
                            {% if member.expiration_month and member.expiration_year %}
                            <p class="mb-1"><strong>Expires:</strong> {{ member.expiration_month }}/{{ member.expiration_year }}</p>
                            {% endif %}
                            {% if member.billing_name %}
                            <p class="mb-1"><strong>Billing Name:</strong> {{ member.billing_name }}</p>
                            {% endif %}
                            {% if member.account_type %}
                            <p class="mb-1"><strong>Account Type:</strong> {{ member.account_type }}</p>
                            {% endif %}
                        </div>
                        {% endif %}
                    </div>
                </div>
                
                <!-- Expandable Details -->
                <div class="row mt-3">
                    <div class="col-12">
                        <button class="btn btn-outline-purple btn-sm" type="button" 
                                data-bs-toggle="collapse" data-bs-target="#details-{{ member.id }}" 
                                aria-expanded="false">
                            <i class="fas fa-info-circle me-2"></i>More Details
                        </button>
                        <a href="/member/{{ member.id }}" class="btn btn-purple btn-sm ms-2">
                            <i class="fas fa-eye me-2"></i>Full Profile
                        </a>
                    </div>
                </div>
                
                <div class="collapse mt-3" id="details-{{ member.id }}">
                    <div class="row">
                        <!-- Personal Details -->
                        <div class="col-md-4">
                            <div class="contact-info">
                                <h6 class="text-purple mb-2">
                                    <i class="fas fa-user-circle me-2"></i>Personal Details
                                </h6>
                                {% if member.date_of_birth %}
                                <p class="mb-1"><strong>DOB:</strong> {{ member.date_of_birth }}</p>
                                {% endif %}
                                {% if member.gender %}
                                <p class="mb-1"><strong>Gender:</strong> {{ member.gender }}</p>
                                {% endif %}
                                {% if member.emergency_contact %}
                                <p class="mb-1"><strong>Emergency:</strong> {{ member.emergency_contact }}</p>
                                {% endif %}
                                {% if member.emergency_phone %}
                                <p class="mb-1"><strong>Emergency Phone:</strong> {{ member.emergency_phone }}</p>
                                {% endif %}
                                {% if member.employer %}
                                <p class="mb-1"><strong>Employer:</strong> {{ member.employer }}</p>
                                {% endif %}
                                {% if member.occupation %}
                                <p class="mb-1"><strong>Occupation:</strong> {{ member.occupation }}</p>
                                {% endif %}
                            </div>
                        </div>
                        
                        <!-- Membership Details -->
                        <div class="col-md-4">
                            <div class="agreement-info">
                                <h6 class="text-purple mb-2">
                                    <i class="fas fa-id-badge me-2"></i>Membership Details
                                </h6>
                                {% if member.key_fob %}
                                <p class="mb-1"><strong>Key Fob:</strong> {{ member.key_fob }}</p>
                                {% endif %}
                                {% if member.last_visit %}
                                <p class="mb-1"><strong>Last Visit:</strong> {{ member.last_visit }}</p>
                                {% endif %}
                                {% if member.user_type %}
                                <p class="mb-1"><strong>Type:</strong> {{ member.user_type }}</p>
                                {% endif %}
                                {% if member.status_message %}
                                <p class="mb-1"><strong>Status:</strong> {{ member.status_message }}</p>
                                {% endif %}
                                <p class="mb-1"><strong>Has App:</strong> 
                                    <span class="badge bg-{{ 'success' if member.has_app else 'secondary' }}">
                                        {{ 'Yes' if member.has_app else 'No' }}
                                    </span>
                                </p>
                                {% if member.trial %}
                                <p class="mb-1"><strong>Trial Member:</strong> 
                                    <span class="badge bg-warning">Yes</span>
                                </p>
                                {% endif %}
                            </div>
                        </div>
                        
                        <!-- System Info -->
                        <div class="col-md-4">
                            <div class="contact-info">
                                <h6 class="text-purple mb-2">
                                    <i class="fas fa-cogs me-2"></i>System Info
                                </h6>
                                {% if member.guid %}
                                <p class="mb-1"><strong>GUID:</strong> <small>{{ member.guid }}</small></p>
                                {% endif %}
                                {% if member.source %}
                                <p class="mb-1"><strong>Source:</strong> {{ member.source }}</p>
                                {% endif %}
                                {% if member.rating %}
                                <p class="mb-1"><strong>Rating:</strong> {{ member.rating }}/5</p>
                                {% endif %}
                                {% if member.bucket %}
                                <p class="mb-1"><strong>Bucket:</strong> {{ member.bucket }}</p>
                                {% endif %}
                                {% if member.last_activity_timestamp %}
                                <p class="mb-1"><strong>Last Activity:</strong> {{ member.last_activity_timestamp }}</p>
                                {% endif %}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    {% else %}
    <div class="col-12">
        <div class="card">
            <div class="card-body text-center py-5">
                <i class="fas fa-users fa-3x text-muted mb-3"></i>
                <h5 class="text-muted">No members found</h5>
                {% if search %}
                <p class="text-muted">Try adjusting your search criteria.</p>
                <a href="/members" class="btn btn-purple">Show All Members</a>
                {% else %}
                <p class="text-muted">Get started by adding your first member.</p>
                <a href="/member/new" class="btn btn-purple">Add Member</a>
                {% endif %}
            </div>
        </div>
    </div>
    {% endfor %}
</div>

<!-- Pagination -->
{% if total_pages > 1 %}
<div class="row mt-4">
    <div class="col-12">
        <nav aria-label="Members pagination">
            <ul class="pagination justify-content-center">
                {% if has_prev %}
                <li class="page-item">
                    <a class="page-link" href="?page={{ page - 1 }}{% if search %}&search={{ search }}{% endif %}">
                        <i class="fas fa-chevron-left"></i>
                    </a>
                </li>
                {% endif %}
                
                {% for p in range(1, total_pages + 1) %}
                    {% if p == page %}
                    <li class="page-item active">
                        <span class="page-link">{{ p }}</span>
                    </li>
                    {% elif p <= 5 or p > total_pages - 5 or (p >= page - 2 and p <= page + 2) %}
                    <li class="page-item">
                        <a class="page-link" href="?page={{ p }}{% if search %}&search={{ search }}{% endif %}">{{ p }}</a>
                    </li>
                    {% elif p == 6 or p == total_pages - 5 %}
                    <li class="page-item disabled">
                        <span class="page-link">...</span>
                    </li>
                    {% endif %}
                {% endfor %}
                
                {% if has_next %}
                <li class="page-item">
                    <a class="page-link" href="?page={{ page + 1 }}{% if search %}&search={{ search }}{% endif %}">
                        <i class="fas fa-chevron-right"></i>
                    </a>
                </li>
                {% endif %}
            </ul>
        </nav>
        
        <div class="text-center text-muted">
            Showing {{ ((page - 1) * per_page) + 1 }} to {{ min(page * per_page, total_members) }} of {{ total_members }} members
        </div>
    </div>
</div>
{% endif %}
{% endblock %}'''
    
    with open(f'{templates_dir}/members.html', 'w') as f:
        f.write(members_template)
    
    # Prospects template
    prospects_template = '''{% extends "base.html" %}

{% block title %}Prospects - Anytime Fitness Management{% endblock %}

{% block content %}
<div class="row mb-4">
    <div class="col-12">
        <h1 class="text-purple mb-3">
            <i class="fas fa-user-plus me-2"></i>
            Prospects
            <span class="badge badge-purple ms-3">{{ total_prospects }} Total</span>
        </h1>
        <p class="lead text-muted">Manage your potential members and track their journey to membership</p>
    </div>
</div>

<!-- Search and Controls -->
<div class="row mb-4">
    <div class="col-md-8">
        <form method="GET" class="d-flex">
            <input type="text" name="search" class="form-control search-bar me-2" 
                   placeholder="Search prospects by name, email, or phone..." 
                   value="{{ search }}">
            <button type="submit" class="btn btn-purple">
                <i class="fas fa-search"></i>
            </button>
        </form>
    </div>
    <div class="col-md-4 text-end">
        <a href="/prospect/new" class="btn btn-purple">
            <i class="fas fa-plus me-2"></i>Add New Prospect
        </a>
    </div>
</div>

<!-- Prospects List -->
<div class="row">
    {% for prospect in prospects %}
    <div class="col-md-6 col-lg-4 mb-4">
        <div class="card prospect-card h-100">
            <div class="card-body">
                <h5 class="text-purple mb-2">
                    <i class="fas fa-user-plus me-2"></i>
                    {{ prospect.full_name }}
                </h5>
                
                <!-- Contact Info -->
                <div class="contact-info mb-3">
                    <p class="mb-1">
                        <i class="fas fa-id-card me-2 text-muted"></i>
                        <strong>ID:</strong> {{ prospect.id }}
                    </p>
                    {% if prospect.email %}
                    <p class="mb-1">
                        <i class="fas fa-envelope me-2 text-muted"></i>
                        <a href="mailto:{{ prospect.email }}">{{ prospect.email }}</a>
                    </p>
                    {% endif %}
                    {% if prospect.mobile_phone %}
                    <p class="mb-1">
                        <i class="fas fa-phone me-2 text-muted"></i>
                        <a href="tel:{{ prospect.mobile_phone }}">{{ prospect.mobile_phone }}</a>
                    </p>
                    {% endif %}
                    {% if prospect.address1 %}
                    <p class="mb-1">
                        <i class="fas fa-map-marker-alt me-2 text-muted"></i>
                        {{ prospect.address1 }}, {{ prospect.city or '' }}, {{ prospect.state or '' }}
                    </p>
                    {% endif %}
                </div>
                
                <!-- Prospect-specific Info -->
                <div class="agreement-info mb-3">
                    {% if prospect.lead_source %}
                    <p class="mb-1">
                        <i class="fas fa-source me-2 text-muted"></i>
                        <strong>Source:</strong> {{ prospect.lead_source }}
                    </p>
                    {% endif %}
                    {% if prospect.interest_level %}
                    <p class="mb-1">
                        <i class="fas fa-star me-2 text-muted"></i>
                        <strong>Interest:</strong> {{ prospect.interest_level }}/5
                    </p>
                    {% endif %}
                    {% if prospect.trial %}
                    <p class="mb-1">
                        <i class="fas fa-dumbbell me-2 text-muted"></i>
                        <span class="badge bg-warning">Trial Interested</span>
                    </p>
                    {% endif %}
                    {% if prospect.tour_completed %}
                    <p class="mb-1">
                        <i class="fas fa-check-circle me-2 text-success"></i>
                        <span class="badge bg-success">Tour Completed</span>
                    </p>
                    {% endif %}
                </div>
                
                <!-- Status and Actions -->
                <div class="d-flex justify-content-between align-items-center">
                    {% if prospect.status %}
                    <span class="badge bg-info">{{ prospect.status }}</span>
                    {% else %}
                    <span class="badge bg-secondary">New Lead</span>
                    {% endif %}
                    
                    <div>
                        <a href="/prospect/{{ prospect.id }}" class="btn btn-sm btn-purple">
                            <i class="fas fa-eye"></i>
                        </a>
                        <button class="btn btn-sm btn-outline-purple ms-1" 
                                data-bs-toggle="modal" 
                                data-bs-target="#followUpModal{{ prospect.id }}">
                            <i class="fas fa-calendar"></i>
                        </button>
                    </div>
                </div>
                
                <!-- Follow-up info -->
                {% if prospect.follow_up_date %}
                <div class="mt-2">
                    <small class="text-muted">
                        <i class="fas fa-calendar-alt me-1"></i>
                        Follow-up: {{ prospect.follow_up_date }}
                    </small>
                </div>
                {% endif %}
                
                <!-- Expandable Details -->
                <div class="mt-3">
                    <button class="btn btn-outline-purple btn-sm w-100" type="button" 
                            data-bs-toggle="collapse" data-bs-target="#details-{{ prospect.id }}" 
                            aria-expanded="false">
                        <i class="fas fa-info-circle me-2"></i>More Details
                    </button>
                </div>
                
                <div class="collapse mt-3" id="details-{{ prospect.id }}">
                    {% if prospect.date_of_birth %}
                    <p class="mb-1"><strong>DOB:</strong> {{ prospect.date_of_birth }}</p>
                    {% endif %}
                    {% if prospect.gender %}
                    <p class="mb-1"><strong>Gender:</strong> {{ prospect.gender }}</p>
                    {% endif %}
                    {% if prospect.preferred_contact_method %}
                    <p class="mb-1"><strong>Preferred Contact:</strong> {{ prospect.preferred_contact_method }}</p>
                    {% endif %}
                    {% if prospect.best_time_to_call %}
                    <p class="mb-1"><strong>Best Time to Call:</strong> {{ prospect.best_time_to_call }}</p>
                    {% endif %}
                    {% if prospect.trial_session_date %}
                    <p class="mb-1"><strong>Trial Session:</strong> {{ prospect.trial_session_date }}</p>
                    {% endif %}
                    {% if prospect.notes %}
                    <p class="mb-1"><strong>Notes:</strong> {{ prospect.notes }}</p>
                    {% endif %}
                </div>
            </div>
        </div>
        
        <!-- Follow-up Modal -->
        <div class="modal fade" id="followUpModal{{ prospect.id }}" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Schedule Follow-up for {{ prospect.full_name }}</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <form>
                            <div class="mb-3">
                                <label class="form-label">Follow-up Date</label>
                                <input type="date" class="form-control" name="follow_up_date">
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Notes</label>
                                <textarea class="form-control" name="notes" rows="3"></textarea>
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-purple">Schedule</button>
                    </div>
                </div>
            </div>
        </div>
    </div>
    {% else %}
    <div class="col-12">
        <div class="card">
            <div class="card-body text-center py-5">
                <i class="fas fa-user-plus fa-3x text-muted mb-3"></i>
                <h5 class="text-muted">No prospects found</h5>
                {% if search %}
                <p class="text-muted">Try adjusting your search criteria.</p>
                <a href="/prospects" class="btn btn-purple">Show All Prospects</a>
                {% else %}
                <p class="text-muted">Get started by adding your first prospect.</p>
                <a href="/prospect/new" class="btn btn-purple">Add Prospect</a>
                {% endif %}
            </div>
        </div>
    </div>
    {% endfor %}
</div>

<!-- Pagination -->
{% if total_pages > 1 %}
<div class="row mt-4">
    <div class="col-12">
        <nav aria-label="Prospects pagination">
            <ul class="pagination justify-content-center">
                {% if has_prev %}
                <li class="page-item">
                    <a class="page-link" href="?page={{ page - 1 }}{% if search %}&search={{ search }}{% endif %}">
                        <i class="fas fa-chevron-left"></i>
                    </a>
                </li>
                {% endif %}
                
                {% for p in range(1, total_pages + 1) %}
                    {% if p == page %}
                    <li class="page-item active">
                        <span class="page-link">{{ p }}</span>
                    </li>
                    {% elif p <= 5 or p > total_pages - 5 or (p >= page - 2 and p <= page + 2) %}
                    <li class="page-item">
                        <a class="page-link" href="?page={{ p }}{% if search %}&search={{ search }}{% endif %}">{{ p }}</a>
                    </li>
                    {% elif p == 6 or p == total_pages - 5 %}
                    <li class="page-item disabled">
                        <span class="page-link">...</span>
                    </li>
                    {% endif %}
                {% endfor %}
                
                {% if has_next %}
                <li class="page-item">
                    <a class="page-link" href="?page={{ page + 1 }}{% if search %}&search={{ search }}{% endif %}">
                        <i class="fas fa-chevron-right"></i>
                    </a>
                </li>
                {% endif %}
            </ul>
        </nav>
        
        <div class="text-center text-muted">
            Showing {{ ((page - 1) * per_page) + 1 }} to {{ min(page * per_page, total_prospects) }} of {{ total_prospects }} prospects
        </div>
    </div>
</div>
{% endif %}
{% endblock %}'''
    
    with open(f'{templates_dir}/prospects.html', 'w') as f:
        f.write(prospects_template)
    
    # Member detail template
    member_detail_template = '''{% extends "base.html" %}

{% block title %}{{ member.full_name }} - Member Details{% endblock %}

{% block content %}
<div class="row">
    <div class="col-12">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h1 class="text-purple">
                <i class="fas fa-user me-2"></i>
                {{ member.full_name }}
                <span class="badge badge-purple ms-3">Member ID: {{ member.id }}</span>
            </h1>
            <a href="/members" class="btn btn-outline-purple">
                <i class="fas fa-arrow-left me-2"></i>Back to Members
            </a>
        </div>
    </div>
</div>

<!-- Quick Stats -->
<div class="row mb-4">
    <div class="col-md-3">
        <div class="card">
            <div class="card-body text-center">
                <i class="fas fa-id-card fa-2x text-purple mb-2"></i>
                <h5>Member Status</h5>
                <span class="badge bg-success">{{ member.status or 'Active' }}</span>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card">
            <div class="card-body text-center">
                <i class="fas fa-calendar fa-2x text-purple mb-2"></i>
                <h5>Join Date</h5>
                <p class="mb-0">{{ member.join_date or 'N/A' }}</p>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card">
            <div class="card-body text-center">
                <i class="fas fa-credit-card fa-2x text-purple mb-2"></i>
                <h5>Payment Type</h5>
                <p class="mb-0">{{ member.card_type or 'N/A' }}</p>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card">
            <div class="card-body text-center">
                <i class="fas fa-home fa-2x text-purple mb-2"></i>
                <h5>Home Club</h5>
                <p class="mb-0">{{ member.home_club_name or 'N/A' }}</p>
            </div>
        </div>
    </div>
</div>

<div class="row">
    <!-- Contact Information -->
    <div class="col-md-6 mb-4">
        <div class="card h-100">
            <div class="card-header bg-purple text-white">
                <h5 class="mb-0">
                    <i class="fas fa-address-book me-2"></i>Contact Information
                </h5>
            </div>
            <div class="card-body">
                <div class="row">
                    <div class="col-12 mb-3">
                        <strong>Full Name:</strong> {{ member.full_name }}
                    </div>
                    {% if member.email %}
                    <div class="col-12 mb-3">
                        <strong>Email:</strong> 
                        <a href="mailto:{{ member.email }}">{{ member.email }}</a>
                    </div>
                    {% endif %}
                    {% if member.mobile_phone %}
                    <div class="col-12 mb-3">
                        <strong>Mobile:</strong> 
                        <a href="tel:{{ member.mobile_phone }}">{{ member.mobile_phone }}</a>
                    </div>
                    {% endif %}
                    {% if member.home_phone %}
                    <div class="col-12 mb-3">
                        <strong>Home Phone:</strong> 
                        <a href="tel:{{ member.home_phone }}">{{ member.home_phone }}</a>
                    </div>
                    {% endif %}
                    {% if member.work_phone %}
                    <div class="col-12 mb-3">
                        <strong>Work Phone:</strong> 
                        <a href="tel:{{ member.work_phone }}">{{ member.work_phone }}</a>
                    </div>
                    {% endif %}
                    {% if member.address1 %}
                    <div class="col-12 mb-3">
                        <strong>Address:</strong><br>
                        {{ member.address1 }}<br>
                        {% if member.address2 %}{{ member.address2 }}<br>{% endif %}
                        {{ member.city or '' }}, {{ member.state or '' }} {{ member.zip_code or '' }}
                    </div>
                    {% endif %}
                </div>
            </div>
        </div>
    </div>
    
    <!-- Personal Information -->
    <div class="col-md-6 mb-4">
        <div class="card h-100">
            <div class="card-header bg-purple text-white">
                <h5 class="mb-0">
                    <i class="fas fa-user me-2"></i>Personal Information
                </h5>
            </div>
            <div class="card-body">
                {% if member.date_of_birth %}
                <div class="mb-3">
                    <strong>Date of Birth:</strong> {{ member.date_of_birth }}
                </div>
                {% endif %}
                {% if member.gender %}
                <div class="mb-3">
                    <strong>Gender:</strong> {{ member.gender }}
                </div>
                {% endif %}
                {% if member.emergency_contact_name %}
                <div class="mb-3">
                    <strong>Emergency Contact:</strong> {{ member.emergency_contact_name }}
                    {% if member.emergency_contact_phone %}
                    <br><small class="text-muted">{{ member.emergency_contact_phone }}</small>
                    {% endif %}
                </div>
                {% endif %}
                {% if member.preferred_contact_method %}
                <div class="mb-3">
                    <strong>Preferred Contact:</strong> {{ member.preferred_contact_method }}
                </div>
                {% endif %}
                {% if member.referral_source %}
                <div class="mb-3">
                    <strong>Referral Source:</strong> {{ member.referral_source }}
                </div>
                {% endif %}
            </div>
        </div>
    </div>
</div>

<!-- Agreement Information -->
{% if member.agreement_id %}
<div class="row mb-4">
    <div class="col-12">
        <div class="card">
            <div class="card-header bg-purple text-white">
                <h5 class="mb-0">
                    <i class="fas fa-file-contract me-2"></i>Agreement Information
                </h5>
            </div>
            <div class="card-body">
                <div class="row">
                    <div class="col-md-4 mb-3">
                        <strong>Agreement ID:</strong> {{ member.agreement_id }}
                    </div>
                    {% if member.agreement_status %}
                    <div class="col-md-4 mb-3">
                        <strong>Status:</strong> 
                        <span class="badge bg-success">{{ member.agreement_status }}</span>
                    </div>
                    {% endif %}
                    {% if member.agreement_type %}
                    <div class="col-md-4 mb-3">
                        <strong>Type:</strong> {{ member.agreement_type }}
                    </div>
                    {% endif %}
                    {% if member.start_date %}
                    <div class="col-md-4 mb-3">
                        <strong>Start Date:</strong> {{ member.start_date }}
                    </div>
                    {% endif %}
                    {% if member.end_date %}
                    <div class="col-md-4 mb-3">
                        <strong>End Date:</strong> {{ member.end_date }}
                    </div>
                    {% endif %}
                    {% if member.monthly_amount %}
                    <div class="col-md-4 mb-3">
                        <strong>Monthly Amount:</strong> ${{ member.monthly_amount }}
                    </div>
                    {% endif %}
                    {% if member.billing_frequency %}
                    <div class="col-md-4 mb-3">
                        <strong>Billing Frequency:</strong> {{ member.billing_frequency }}
                    </div>
                    {% endif %}
                    {% if member.next_billing_date %}
                    <div class="col-md-4 mb-3">
                        <strong>Next Billing:</strong> {{ member.next_billing_date }}
                    </div>
                    {% endif %}
                    {% if member.auto_renew %}
                    <div class="col-md-4 mb-3">
                        <strong>Auto Renew:</strong> 
                        <span class="badge bg-{{ 'success' if member.auto_renew == 'true' else 'warning' }}">
                            {{ 'Yes' if member.auto_renew == 'true' else 'No' }}
                        </span>
                    </div>
                    {% endif %}
                </div>
            </div>
        </div>
    </div>
</div>
{% endif %}

<!-- Payment Information -->
{% if member.payment_token %}
<div class="row mb-4">
    <div class="col-12">
        <div class="card">
            <div class="card-header bg-purple text-white">
                <h5 class="mb-0">
                    <i class="fas fa-credit-card me-2"></i>Payment Information
                </h5>
            </div>
            <div class="card-body">
                <div class="row">
                    {% if member.card_type %}
                    <div class="col-md-3 mb-3">
                        <strong>Card Type:</strong> {{ member.card_type }}
                    </div>
                    {% endif %}
                    {% if member.card_last_four %}
                    <div class="col-md-3 mb-3">
                        <strong>Last 4 Digits:</strong> •••• {{ member.card_last_four }}
                    </div>
                    {% endif %}
                    {% if member.card_exp_month and member.card_exp_year %}
                    <div class="col-md-3 mb-3">
                        <strong>Expiration:</strong> {{ member.card_exp_month }}/{{ member.card_exp_year }}
                    </div>
                    {% endif %}
                    {% if member.billing_name %}
                    <div class="col-md-3 mb-3">
                        <strong>Billing Name:</strong> {{ member.billing_name }}
                    </div>
                    {% endif %}
                    {% if member.billing_address1 %}
                    <div class="col-12 mb-3">
                        <strong>Billing Address:</strong><br>
                        {{ member.billing_address1 }}<br>
                        {% if member.billing_address2 %}{{ member.billing_address2 }}<br>{% endif %}
                        {{ member.billing_city or '' }}, {{ member.billing_state or '' }} {{ member.billing_zip_code or '' }}
                    </div>
                    {% endif %}
                </div>
            </div>
        </div>
    </div>
</div>
{% endif %}

<!-- Home Club Information -->
{% if member.home_club_name %}
<div class="row mb-4">
    <div class="col-12">
        <div class="card">
            <div class="card-header bg-purple text-white">
                <h5 class="mb-0">
                    <i class="fas fa-home me-2"></i>Home Club Information
                </h5>
            </div>
            <div class="card-body">
                <div class="row">
                    <div class="col-md-6 mb-3">
                        <strong>Club Name:</strong> {{ member.home_club_name }}
                    </div>
                    {% if member.home_club_id %}
                    <div class="col-md-6 mb-3">
                        <strong>Club ID:</strong> {{ member.home_club_id }}
                    </div>
                    {% endif %}
                    {% if member.home_club_phone %}
                    <div class="col-md-6 mb-3">
                        <strong>Club Phone:</strong> 
                        <a href="tel:{{ member.home_club_phone }}">{{ member.home_club_phone }}</a>
                    </div>
                    {% endif %}
                    {% if member.home_club_address1 %}
                    <div class="col-12 mb-3">
                        <strong>Club Address:</strong><br>
                        {{ member.home_club_address1 }}<br>
                        {% if member.home_club_address2 %}{{ member.home_club_address2 }}<br>{% endif %}
                        {{ member.home_club_city or '' }}, {{ member.home_club_state or '' }} {{ member.home_club_zip_code or '' }}
                    </div>
                    {% endif %}
                </div>
            </div>
        </div>
    </div>
</div>
{% endif %}

<!-- Action Buttons -->
<div class="row mt-4">
    <div class="col-12 text-center">
        <a href="/member/{{ member.id }}/edit" class="btn btn-purple me-2">
            <i class="fas fa-edit me-2"></i>Edit Member
        </a>
        <button class="btn btn-outline-purple me-2" data-bs-toggle="modal" data-bs-target="#messageModal">
            <i class="fas fa-envelope me-2"></i>Send Message
        </button>
        <a href="/member/{{ member.id }}/agreements" class="btn btn-outline-purple">
            <i class="fas fa-file-contract me-2"></i>View All Agreements
        </a>
    </div>
</div>

<!-- Message Modal -->
<div class="modal fade" id="messageModal" tabindex="-1">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">Send Message to {{ member.full_name }}</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                <form>
                    <div class="mb-3">
                        <label class="form-label">Message Type</label>
                        <select class="form-select" name="message_type">
                            <option value="email">Email</option>
                            <option value="sms">SMS</option>
                        </select>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Subject</label>
                        <input type="text" class="form-control" name="subject">
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Message</label>
                        <textarea class="form-control" name="message" rows="5"></textarea>
                    </div>
                </form>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                <button type="button" class="btn btn-purple">Send Message</button>
            </div>
        </div>
    </div>
</div>
{% endblock %}'''
    
    with open(f'{templates_dir}/member_detail.html', 'w') as f:
        f.write(member_detail_template)
    
    print(f"Enhanced dashboard created with complete member/prospect separation!")
    print(f"Templates created: base.html, index.html, members.html, prospects.html, member_detail.html")
    print(f"Database tables: members (with full agreement data), prospects")
    print(f"Features: Member agreement display, payment info, home club data, search, pagination")

if __name__ == "__main__":
    # Create templates first
    create_templates()
    # Then run the app
    app.run(debug=True, host='0.0.0.0', port=5001)
