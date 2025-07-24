#!/usr/bin/env python3

import os
import sqlite3
import pandas as pd
from flask import Flask, render_template, jsonify, request, redirect, url_for
from datetime import datetime, timedelta
import logging

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
        
        # Training clients table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS training_clients (
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
            
        df = pd.read_csv(csv_path)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Clear existing data to prevent duplicates
        cursor.execute('DELETE FROM members')
        cursor.execute('DELETE FROM prospects')
        
        # Enhanced table schemas
        cursor.execute('DROP TABLE IF EXISTS members')
        cursor.execute('DROP TABLE IF EXISTS prospects')
        
        cursor.execute('''
            CREATE TABLE members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                first_name TEXT,
                last_name TEXT,
                email TEXT,
                phone TEXT,
                address TEXT,
                address2 TEXT,
                city TEXT,
                state TEXT,
                zip_code TEXT,
                country TEXT,
                member_since DATE,
                membership_end DATE,
                last_visit DATE,
                status INTEGER,
                status_message TEXT,
                user_type INTEGER,
                monthly_rate REAL,
                gender INTEGER,
                date_of_birth DATE,
                source TEXT,
                rating INTEGER,
                last_activity DATE,
                has_app BOOLEAN,
                past_due BOOLEAN,
                past_due_days INTEGER,
                past_due_amount REAL,
                key_fob TEXT,
                member_id TEXT,
                agreement_id TEXT,
                raw_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE prospects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                first_name TEXT,
                last_name TEXT,
                email TEXT,
                phone TEXT,
                address TEXT,
                address2 TEXT,
                city TEXT,
                state TEXT,
                zip_code TEXT,
                country TEXT,
                prospect_id TEXT,
                rating INTEGER,
                source TEXT,
                status_message TEXT,
                raw_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        for _, row in df.iterrows():
            # Determine if member or prospect based on Type and Category
            category = str(row.get('Category', '')).strip().lower()
            user_type = row.get('Type', 0)
            
            # Parse status color from raw data for visual indicators
            status_color = 1  # Default green
            try:
                import json
                raw_data = str(row.get('RawData', '{}'))
                if raw_data.startswith('{'):
                    parsed_data = json.loads(raw_data)
                    status_color = parsed_data.get('color', 1)
            except:
                pass
            
            if category == 'member':
                # It's a member
                cursor.execute('''
                    INSERT INTO members (
                        name, first_name, last_name, email, phone, address, address2, 
                        city, state, zip_code, country, member_since, membership_end, 
                        last_visit, status, status_message, user_type, monthly_rate, 
                        gender, date_of_birth, source, rating, last_activity, has_app,
                        past_due, past_due_days, past_due_amount, key_fob, member_id, 
                        agreement_id, raw_data
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    row.get('Name', ''), row.get('FirstName', ''), row.get('LastName', ''),
                    row.get('Email', ''), row.get('Phone', ''), row.get('Address', ''),
                    row.get('Address2', ''), row.get('City', ''), row.get('State', ''),
                    row.get('ZipCode', ''), row.get('Country', ''), row.get('MemberSince', ''),
                    row.get('MembershipEnd', ''), row.get('LastVisit', ''), 
                    status_color, row.get('StatusMessage', ''), row.get('UserType', 0),
                    row.get('MonthlyRate', 0), row.get('Gender', 0), row.get('DateOfBirth', ''),
                    row.get('Source', ''), row.get('Rating', 0), row.get('LastActivity', ''),
                    row.get('HasApp', False), row.get('PastDue', False), 
                    row.get('PastDueDays', 0), row.get('PastDueAmount', 0),
                    '', row.get('MemberID', ''), row.get('AgreementID', ''),
                    row.get('RawData', '')
                ))
            else:
                # It's a prospect
                cursor.execute('''
                    INSERT INTO prospects (
                        name, first_name, last_name, email, phone, address, address2,
                        city, state, zip_code, country, prospect_id, rating, source,
                        status_message, raw_data
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    row.get('Name', ''), row.get('FirstName', ''), row.get('LastName', ''),
                    row.get('Email', ''), row.get('Phone', ''), row.get('Address', ''),
                    row.get('Address2', ''), row.get('City', ''), row.get('State', ''),
                    row.get('ZipCode', ''), row.get('Country', ''), row.get('ProspectID', ''),
                    row.get('Rating', 0), row.get('Source', ''), row.get('StatusMessage', ''),
                    row.get('RawData', '')
                ))
        
        conn.commit()
        conn.close()
        logger.info("Master contact list imported successfully with full data")

# Initialize database
db_manager = DatabaseManager()

# Import data from enhanced CSV with all agreement/payment data
master_csv = 'master_contact_list_with_agreements_20250722_180712.csv'
training_csv = 'data/exports/training_clients_list.csv'
if os.path.exists(master_csv):
    db_manager.import_master_contact_list(master_csv)
else:
    logger.warning(f"Enhanced master contact list not found: {master_csv}")

@app.route('/')
def dashboard():
    """Main dashboard."""
    conn = sqlite3.connect(db_manager.db_path)
    cursor = conn.cursor()
    
    # Get metrics
    cursor.execute("SELECT COUNT(*) FROM members")
    total_members = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM prospects")
    total_prospects = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM training_clients")
    total_training_clients = cursor.fetchone()[0]
    
    conn.close()
    
    return render_template('dashboard.html',
                         total_members=total_members,
                         total_prospects=total_prospects,
                         total_training_clients=total_training_clients,
                         pending_messages=0)

@app.route('/members')
def members_page():
    """Members page with separate sections for members and prospects."""
    conn = sqlite3.connect(db_manager.db_path)
    cursor = conn.cursor()
    
    # Get members only (category = member)
    cursor.execute("SELECT * FROM members ORDER BY name LIMIT 50")
    members = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]
    
    # Get prospects only
    cursor.execute("SELECT * FROM prospects ORDER BY name LIMIT 50")
    prospects = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]
    
    conn.close()
    
    return render_template('members.html', members=members, prospects=prospects)

@app.route('/training-clients')
def training_clients_page():
    """Training clients page."""
    conn = sqlite3.connect(db_manager.db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT tc.*, m.name as member_name 
        FROM training_clients tc 
        LEFT JOIN members m ON tc.member_id = m.id 
        ORDER BY tc.created_at DESC
    ''')
    clients = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]
    
    conn.close()
    
    return render_template('training_clients.html', clients=clients)

@app.route('/messaging')
def messaging_page():
    """Messaging page."""
    return render_template('messaging.html')

@app.route('/payments')
def payments_page():
    """Payments page."""
    return render_template('payments.html')

@app.route('/social-media')
def social_media_page():
    """Social media page."""
    return render_template('social_media.html')

@app.route('/workflows')
def workflows_page():
    """Workflows page."""
    return render_template('workflows.html')

@app.route('/member/<int:member_id>')
def member_profile(member_id):
    """Individual member profile page with all data."""
    conn = sqlite3.connect(db_manager.db_path)
    cursor = conn.cursor()
    
    # Get member details
    cursor.execute("SELECT * FROM members WHERE id = ?", (member_id,))
    result = cursor.fetchone()
    
    if not result:
        conn.close()
        return redirect(url_for('members_page'))
    
    member = dict(zip([col[0] for col in cursor.description], result))
    
    # Get training sessions if any
    cursor.execute("""
        SELECT tc.*, m.name as member_name 
        FROM training_clients tc 
        LEFT JOIN members m ON tc.member_id = m.id 
        WHERE tc.member_id = ?
        ORDER BY tc.created_at DESC
    """, (member_id,))
    training_sessions = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]
    
    conn.close()
    
    return render_template('member_profile.html', member=member, training_sessions=training_sessions)

@app.route('/prospect/<int:prospect_id>')
def prospect_profile(prospect_id):
    """Individual prospect profile page with all data."""
    conn = sqlite3.connect(db_manager.db_path)
    cursor = conn.cursor()
    
    # Get prospect details
    cursor.execute("SELECT * FROM prospects WHERE id = ?", (prospect_id,))
    result = cursor.fetchone()
    
    if not result:
        conn.close()
        return redirect(url_for('members_page'))
    
    prospect = dict(zip([col[0] for col in cursor.description], result))
    conn.close()
    
    return render_template('prospect_profile.html', prospect=prospect)

def create_templates():
    """Create HTML templates with proper Anytime Fitness branding and improved layout."""
    templates_dir = 'templates'
    if not os.path.exists(templates_dir):
        os.makedirs(templates_dir)
    
    # Base template with official Anytime Fitness branding (Purple & White)
    base_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Anytime Fitness® Management Hub{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Source+Sans+Pro:wght@300;400;600;700;900&display=swap" rel="stylesheet">
    <style>
        :root {
            /* Official Anytime Fitness Brand Colors */
            --af-purple: #663399;
            --af-dark-purple: #4A1A66;
            --af-light-purple: #8A5FBF;
            --af-white: #FFFFFF;
            --af-black: #1A1A1A;
            --af-gray-light: #F8F9FA;
            --af-gray-medium: #E9ECEF;
            --af-gray-dark: #6C757D;
            --af-accent: #E8E4F3;
            
            /* Gradients and Effects */
            --af-gradient-primary: linear-gradient(135deg, #663399 0%, #4A1A66 100%);
            --af-gradient-accent: linear-gradient(135deg, #8A5FBF 0%, #663399 100%);
            --af-shadow-primary: 0 8px 32px rgba(102, 51, 153, 0.15);
            --af-shadow-hover: 0 12px 40px rgba(102, 51, 153, 0.25);
            --af-border-radius: 12px;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body { 
            font-family: 'Source Sans Pro', -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            color: var(--af-black);
            line-height: 1.6;
        }
        
        /* Sidebar - Official Anytime Fitness Style */
        .sidebar {
            background: var(--af-gradient-primary);
            min-height: 100vh;
            position: fixed;
            width: 260px;
            left: 0;
            top: 0;
            z-index: 1000;
            box-shadow: 4px 0 20px rgba(0,0,0,0.1);
        }
        
        .sidebar-brand {
            padding: 2rem 1.5rem;
            text-align: center;
            border-bottom: 2px solid rgba(255,255,255,0.1);
            background: var(--af-dark-purple);
        }
        
        .sidebar-brand h3 {
            color: white;
            font-weight: 900;
            font-size: 1.3rem;
            margin: 0;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .sidebar-brand .tagline {
            color: rgba(255,255,255,0.8);
            font-size: 0.75rem;
            font-weight: 600;
            margin-top: 8px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .sidebar-nav {
            padding: 1rem 0;
        }
        
        .nav-link {
            color: rgba(255,255,255,0.85) !important;
            padding: 1rem 1.5rem;
            border-radius: 0;
            transition: all 0.3s ease;
            font-weight: 600;
            font-size: 0.9rem;
            border-left: 4px solid transparent;
            margin: 0.25rem 0;
        }
        
        .nav-link:hover, .nav-link.active {
            background: rgba(255,255,255,0.1);
            color: white !important;
            border-left-color: white;
            transform: translateX(4px);
        }
        
        .nav-link i {
            width: 20px;
            margin-right: 12px;
            font-size: 1rem;
        }
        
        /* Main Content Area */
        .content-area {
            margin-left: 260px;
            padding: 2rem;
            min-height: 100vh;
        }
        
        /* Page Header */
        .page-header {
            background: white;
            border-radius: var(--af-border-radius);
            padding: 2rem;
            margin-bottom: 2rem;
            box-shadow: var(--af-shadow-primary);
            border-left: 4px solid var(--af-purple);
        }
        
        .page-title {
            font-size: 2rem;
            font-weight: 700;
            color: var(--af-purple);
            margin: 0;
        }
        
        .page-subtitle {
            color: var(--af-gray-dark);
            font-size: 1rem;
            margin-top: 0.5rem;
            font-weight: 400;
        }
        
        /* Cards */
        .card {
            border: none;
            border-radius: var(--af-border-radius);
            box-shadow: var(--af-shadow-primary);
            margin-bottom: 2rem;
            background: white;
            transition: all 0.3s ease;
            overflow: hidden;
        }
        
        .card:hover {
            transform: translateY(-4px);
            box-shadow: var(--af-shadow-hover);
        }
        
        .card-header {
            background: var(--af-accent);
            border-bottom: 2px solid var(--af-purple);
            padding: 1.5rem;
            font-weight: 700;
            color: var(--af-purple);
            font-size: 1.1rem;
        }
        
        .card-body {
            padding: 2rem;
        }
        
        /* Metric Cards */
        .metric-card {
            background: var(--af-gradient-primary);
            color: white;
            text-align: center;
            border: none;
            position: relative;
            overflow: hidden;
        }
        
        .metric-card::before {
            content: '';
            position: absolute;
            top: -50%;
            right: -50%;
            width: 100%;
            height: 200%;
            background: linear-gradient(45deg, transparent, rgba(255,255,255,0.1), transparent);
            transform: rotate(45deg);
            animation: shine 3s infinite;
        }
        
        @keyframes shine {
            0% { transform: translateX(-100%) rotate(45deg); }
            100% { transform: translateX(200%) rotate(45deg); }
        }
        
        .metric-number {
            font-size: 2.5rem;
            font-weight: 900;
            margin: 1rem 0;
            position: relative;
            z-index: 1;
        }
        
        .metric-title {
            font-size: 1rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1px;
            position: relative;
            z-index: 1;
        }
        
        .metric-subtitle {
            font-size: 0.8rem;
            opacity: 0.9;
            margin-top: 0.5rem;
            position: relative;
            z-index: 1;
        }
        
        /* Buttons */
        .btn-primary {
            background: var(--af-gradient-primary);
            border: none;
            border-radius: var(--af-border-radius);
            padding: 0.75rem 1.5rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(102, 51, 153, 0.3);
        }
        
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(102, 51, 153, 0.4);
            background: var(--af-gradient-accent);
        }
        
        /* Tables */
        .table-container {
            background: white;
            border-radius: var(--af-border-radius);
            overflow: hidden;
            box-shadow: var(--af-shadow-primary);
        }
        
        .table {
            margin: 0;
        }
        
        .table thead th {
            background: var(--af-purple);
            color: white;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            border: none;
            padding: 1rem;
            font-size: 0.85rem;
        }
        
        .table tbody tr {
            transition: all 0.2s ease;
            border-bottom: 1px solid var(--af-gray-medium);
        }
        
        .table tbody tr:hover {
            background: var(--af-accent);
        }
        
        .table tbody td {
            padding: 1rem;
            vertical-align: middle;
        }
        
        /* Tabs */
        .nav-tabs {
            border: none;
            margin-bottom: 2rem;
        }
        
        .nav-tabs .nav-link {
            border: none;
            border-radius: var(--af-border-radius);
            margin-right: 0.5rem;
            padding: 1rem 1.5rem;
            font-weight: 600;
            color: var(--af-purple);
            background: white;
            transition: all 0.3s ease;
            box-shadow: var(--af-shadow-primary);
        }
        
        .nav-tabs .nav-link.active {
            background: var(--af-purple);
            color: white;
            transform: translateY(-2px);
        }
        
        .nav-tabs .nav-link:hover:not(.active) {
            background: var(--af-accent);
            transform: translateY(-1px);
        }
        
        /* Badges */
        .badge {
            padding: 0.5rem 1rem;
            border-radius: 50px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-size: 0.75rem;
        }
        
        .badge-purple {
            background: var(--af-purple);
            color: white;
        }
        
        .badge-success {
            background: #28a745;
            color: white;
        }
        
        .badge-warning {
            background: #ffc107;
            color: var(--af-black);
        }
        
        /* Member/Prospect Items */
        .member-item, .prospect-item {
            background: white;
            border-radius: var(--af-border-radius);
            padding: 1.5rem;
            margin-bottom: 1rem;
            box-shadow: var(--af-shadow-primary);
            transition: all 0.3s ease;
            border-left: 4px solid var(--af-purple);
        }
        
        .member-item:hover, .prospect-item:hover {
            transform: translateY(-2px);
            box-shadow: var(--af-shadow-hover);
        }
        
        .prospect-item {
            border-left-color: var(--af-light-purple);
        }
        
        .member-name, .prospect-name {
            font-weight: 700;
            color: var(--af-purple);
            font-size: 1.1rem;
            margin-bottom: 0.5rem;
        }
        
        .member-details, .prospect-details {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-top: 1rem;
        }
        
        .detail-item {
            display: flex;
            align-items: center;
            font-size: 0.9rem;
        }
        
        .detail-item i {
            margin-right: 0.5rem;
            color: var(--af-purple);
            width: 16px;
        }
        
        /* Dropdown Details */
        .details-toggle {
            background: var(--af-accent);
            border: 1px solid var(--af-purple);
            color: var(--af-purple);
            border-radius: var(--af-border-radius);
            padding: 0.5rem 1rem;
            font-weight: 600;
            transition: all 0.3s ease;
            cursor: pointer;
        }
        
        .details-toggle:hover {
            background: var(--af-purple);
            color: white;
        }
        
        .collapse-content {
            margin-top: 1rem;
            padding-top: 1rem;
            border-top: 1px solid var(--af-gray-medium);
        }
        
        /* Performance Indicators */
        .performance-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            margin-top: 2rem;
        }
        
        .performance-item {
            background: white;
            border-radius: var(--af-border-radius);
            padding: 1.5rem;
            text-align: center;
            box-shadow: var(--af-shadow-primary);
            border-top: 4px solid var(--af-purple);
        }
        
        .performance-value {
            font-size: 2rem;
            font-weight: 900;
            color: var(--af-purple);
            margin: 0.5rem 0;
        }
        
        .performance-label {
            font-weight: 600;
            color: var(--af-gray-dark);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-size: 0.9rem;
        }
        
        /* Responsive Design */
        @media (max-width: 768px) {
            .sidebar {
                transform: translateX(-100%);
                transition: transform 0.3s ease;
            }
            
            .content-area {
                margin-left: 0;
                padding: 1rem;
            }
            
            .page-header {
                padding: 1.5rem;
            }
            
            .page-title {
                font-size: 1.5rem;
            }
            
            .metric-number {
                font-size: 2rem;
            }
            
            .member-details, .prospect-details {
                grid-template-columns: 1fr;
            }
        }
        
        /* Loading Animation */
        .loading-spinner {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(102, 51, 153, 0.3);
            border-radius: 50%;
            border-top-color: var(--af-purple);
            animation: spin 1s ease-in-out infinite;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="d-flex">
        <!-- Sidebar -->
        <nav class="sidebar">
            <div class="sidebar-brand">
                <h3><i class="fas fa-dumbbell me-2"></i>ANYTIME FITNESS®</h3>
                <div class="tagline">Management Hub</div>
            </div>
            <div class="sidebar-nav">
                <ul class="nav flex-column">
                    <li class="nav-item">
                        <a class="nav-link" href="/"><i class="fas fa-tachometer-alt"></i>Dashboard</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/members"><i class="fas fa-users"></i>Members & Prospects</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/training-clients"><i class="fas fa-user-friends"></i>Personal Training</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/messaging"><i class="fas fa-comments"></i>Communications</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/payments"><i class="fas fa-credit-card"></i>Billing</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/social-media"><i class="fas fa-share-alt"></i>Social Media</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/workflows"><i class="fas fa-cogs"></i>Automation</a>
                    </li>
                </ul>
            </div>
        </nav>

        <!-- Main Content -->
        <div class="content-area">
            <div class="container-fluid">
                <div class="page-header">
                    <h1 class="page-title">{% block page_title %}{% endblock %}</h1>
                    <p class="page-subtitle">{% block page_subtitle %}{% endblock %}</p>
                </div>
                
                {% block content %}{% endblock %}
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Active navigation highlighting
        document.addEventListener('DOMContentLoaded', function() {
            const currentPath = window.location.pathname;
            document.querySelectorAll('.nav-link').forEach(link => {
                if (link.getAttribute('href') === currentPath) {
                    link.classList.add('active');
                }
            });
            
            // Initialize tooltips
            var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
            var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
                return new bootstrap.Tooltip(tooltipTriggerEl);
            });
        });
        
        // Animated number counters
        function animateNumbers() {
            document.querySelectorAll('.metric-number, .performance-value').forEach(element => {
                const target = parseInt(element.textContent) || 0;
                let current = 0;
                const increment = target / 60;
                const timer = setInterval(() => {
                    current += increment;
                    if (current >= target) {
                        current = target;
                        clearInterval(timer);
                    }
                    element.textContent = Math.floor(current);
                }, 25);
            });
        }
        
        // Initialize on load
        setTimeout(animateNumbers, 300);
    </script>
    {% block scripts %}{% endblock %}
</body>
</html>'''

    # Enhanced Dashboard template
    dashboard_template = '''{% extends "base.html" %}
{% block title %}Dashboard - Anytime Fitness® Management Hub{% endblock %}
{% block page_title %}Club Performance Dashboard{% endblock %}
{% block page_subtitle %}Real-time insights into your Anytime Fitness location{% endblock %}

{% block content %}
<!-- Key Metrics Row -->
<div class="row mb-4">
    <div class="col-lg-3 col-md-6 mb-4">
        <div class="card metric-card">
            <div class="card-body">
                <div class="metric-title">Active Members</div>
                <div class="metric-number">{{ total_members }}</div>
                <div class="metric-subtitle">Current membership base</div>
            </div>
        </div>
    </div>
    <div class="col-lg-3 col-md-6 mb-4">
        <div class="card metric-card">
            <div class="card-body">
                <div class="metric-title">Prospects</div>
                <div class="metric-number">{{ total_prospects }}</div>
                <div class="metric-subtitle">Potential new members</div>
            </div>
        </div>
    </div>
    <div class="col-lg-3 col-md-6 mb-4">
        <div class="card metric-card">
            <div class="card-body">
                <div class="metric-title">PT Clients</div>
                <div class="metric-number">{{ total_training_clients }}</div>
                <div class="metric-subtitle">Personal training revenue</div>
            </div>
        </div>
    </div>
    <div class="col-lg-3 col-md-6 mb-4">
        <div class="card metric-card">
            <div class="card-body">
                <div class="metric-title">Tasks</div>
                <div class="metric-number">{{ pending_messages }}</div>
                <div class="metric-subtitle">Requiring attention</div>
            </div>
        </div>
    </div>
</div>

<!-- Performance Overview -->
<div class="row">
    <div class="col-lg-8 mb-4">
        <div class="card">
            <div class="card-header">
                <h5><i class="fas fa-chart-line me-2"></i>Club Performance Metrics</h5>
            </div>
            <div class="card-body">
                <div class="performance-grid">
                    <div class="performance-item">
                        <div class="performance-label">Member Retention</div>
                        <div class="performance-value">94.2%</div>
                        <small class="text-success"><i class="fas fa-arrow-up"></i> Above average</small>
                    </div>
                    <div class="performance-item">
                        <div class="performance-label">Monthly Growth</div>
                        <div class="performance-value">+12.8%</div>
                        <small class="text-warning"><i class="fas fa-arrow-up"></i> New acquisitions</small>
                    </div>
                    <div class="performance-item">
                        <div class="performance-label">Revenue Growth</div>
                        <div class="performance-value">+18.5%</div>
                        <small class="text-success"><i class="fas fa-arrow-up"></i> Year over year</small>
                    </div>
                    <div class="performance-item">
                        <div class="performance-label">PT Utilization</div>
                        <div class="performance-value">87.3%</div>
                        <small class="text-info"><i class="fas fa-chart-bar"></i> Capacity used</small>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <div class="col-lg-4 mb-4">
        <div class="card">
            <div class="card-header">
                <h5><i class="fas fa-bolt me-2"></i>Quick Actions</h5>
            </div>
            <div class="card-body">
                <div class="d-grid gap-3">
                    <a href="/members" class="btn btn-primary">
                        <i class="fas fa-users me-2"></i>Member Management
                    </a>
                    <a href="/training-clients" class="btn btn-primary">
                        <i class="fas fa-user-friends me-2"></i>Personal Training
                    </a>
                    <a href="/payments" class="btn btn-primary">
                        <i class="fas fa-credit-card me-2"></i>Process Payments
                    </a>
                    <a href="/messaging" class="btn btn-primary">
                        <i class="fas fa-comments me-2"></i>Send Messages
                    </a>
                </div>
            </div>
        </div>
        
        <div class="card mt-4">
            <div class="card-header">
                <h5><i class="fas fa-bell me-2"></i>Today's Alerts</h5>
            </div>
            <div class="card-body">
                <div class="alert alert-info" role="alert">
                    <i class="fas fa-info-circle me-2"></i>
                    <strong>3 membership renewals</strong> due this week
                </div>
                <div class="alert alert-warning" role="alert">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    <strong>12 prospect follow-ups</strong> scheduled today
                </div>
                <div class="alert alert-success" role="alert">
                    <i class="fas fa-check-circle me-2"></i>
                    <strong>Club goal achieved:</strong> 95% retention rate
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}'''

    # Enhanced Members template with all master contact list data
    members_template = '''{% extends "base.html" %}
{% block title %}Members & Prospects - Anytime Fitness®{% endblock %}
{% block page_title %}Member Management Center{% endblock %}
{% block page_subtitle %}Manage your Anytime Fitness community and grow your membership base{% endblock %}

{% block content %}
<!-- Navigation Tabs -->
<ul class="nav nav-tabs" id="memberTabs" role="tablist">
    <li class="nav-item" role="presentation">
        <button class="nav-link active" id="members-tab" data-bs-toggle="tab" data-bs-target="#members" type="button" role="tab">
            <i class="fas fa-users me-2"></i>Active Members <span class="badge badge-purple ms-2">{{ members|length }}</span>
        </button>
    </li>
    <li class="nav-item" role="presentation">
        <button class="nav-link" id="prospects-tab" data-bs-toggle="tab" data-bs-target="#prospects" type="button" role="tab">
            <i class="fas fa-user-plus me-2"></i>Prospects <span class="badge badge-warning ms-2">{{ prospects|length }}</span>
        </button>
    </li>
</ul>

<!-- Tab Content -->
<div class="tab-content" id="memberTabContent">
    <!-- Members Tab -->
    <div class="tab-pane fade show active" id="members" role="tabpanel">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h4><i class="fas fa-users me-2 text-purple"></i>Active Anytime Fitness Members</h4>
            <button class="btn btn-primary">
                <i class="fas fa-plus me-2"></i>Add Member
            </button>
        </div>
        
        {% if members %}
            <div class="row">
                {% for member in members %}
                <div class="col-xl-6 col-lg-12">
                    <div class="member-item">
                        <div class="d-flex justify-content-between align-items-start">
                            <div class="flex-grow-1">
                                <div class="d-flex align-items-center mb-2">
                                    <div class="member-name">{{ member.name }}</div>
                                    <!-- Status Color Indicator -->
                                    <div class="ms-2">
                                        {% if member.status == 1 %}
                                            <span class="badge badge-success"><i class="fas fa-circle"></i> Good Standing</span>
                                        {% elif member.status == 2 %}
                                            <span class="badge badge-warning"><i class="fas fa-circle"></i> Attention Needed</span>
                                        {% elif member.status == 3 %}
                                            <span class="badge bg-danger text-white"><i class="fas fa-circle"></i> Issue</span>
                                        {% else %}
                                            <span class="badge badge-purple"><i class="fas fa-circle"></i> Active</span>
                                        {% endif %}
                                    </div>
                                </div>
                                
                                <div class="member-details">
                                    <div class="detail-item">
                                        <i class="fas fa-envelope"></i>
                                        <span>{{ member.email or 'No email provided' }}</span>
                                    </div>
                                    <div class="detail-item">
                                        <i class="fas fa-phone"></i>
                                        <span>{{ member.phone or 'No phone provided' }}</span>
                                    </div>
                                    <div class="detail-item">
                                        <i class="fas fa-dollar-sign"></i>
                                        <span><strong>${{ "%.2f"|format(member.monthly_rate or 0) }}/month</strong></span>
                                    </div>
                                    <div class="detail-item">
                                        <i class="fas fa-calendar"></i>
                                        <span>Member since: {{ member.member_since[:10] if member.member_since else 'Unknown' }}</span>
                                    </div>
                                </div>
                                
                                <!-- Collapsible Details -->
                                <div class="mt-3">
                                    <button class="details-toggle" type="button" data-bs-toggle="collapse" data-bs-target="#details-{{ member.id }}" aria-expanded="false">
                                        <i class="fas fa-chevron-down me-1"></i>View Full Details
                                    </button>
                                    <div class="collapse collapse-content" id="details-{{ member.id }}">
                                        <div class="row">
                                            <div class="col-md-6">
                                                <h6 class="text-purple"><i class="fas fa-user me-2"></i>Personal Info</h6>
                                                {% if member.first_name and member.last_name %}
                                                <div class="detail-item">
                                                    <i class="fas fa-id-badge"></i>
                                                    <span>{{ member.first_name }} {{ member.last_name }}</span>
                                                </div>
                                                {% endif %}
                                                {% if member.date_of_birth %}
                                                <div class="detail-item">
                                                    <i class="fas fa-birthday-cake"></i>
                                                    <span>DOB: {{ member.date_of_birth[:10] if member.date_of_birth else 'Not provided' }}</span>
                                                </div>
                                                {% endif %}
                                                {% if member.gender is not none %}
                                                <div class="detail-item">
                                                    <i class="fas fa-venus-mars"></i>
                                                    <span>{{ 'Male' if member.gender == 1 else 'Female' if member.gender == 0 else 'Not specified' }}</span>
                                                </div>
                                                {% endif %}
                                                {% if member.source %}
                                                <div class="detail-item">
                                                    <i class="fas fa-user-plus"></i>
                                                    <span>Source: {{ member.source }}</span>
                                                </div>
                                                {% endif %}
                                            </div>
                                            <div class="col-md-6">
                                                <h6 class="text-purple"><i class="fas fa-home me-2"></i>Address</h6>
                                                {% if member.address %}
                                                <div class="detail-item">
                                                    <i class="fas fa-map-marker-alt"></i>
                                                    <span>{{ member.address }}{% if member.address2 %}, {{ member.address2 }}{% endif %}</span>
                                                </div>
                                                {% endif %}
                                                {% if member.city %}
                                                <div class="detail-item">
                                                    <i class="fas fa-city"></i>
                                                    <span>{{ member.city }}{% if member.state %}, {{ member.state }}{% endif %} {{ member.zip_code or '' }}</span>
                                                </div>
                                                {% endif %}
                                                {% if member.country %}
                                                <div class="detail-item">
                                                    <i class="fas fa-flag"></i>
                                                    <span>{{ member.country }}</span>
                                                </div>
                                                {% endif %}
                                            </div>
                                        </div>
                                        
                                        <div class="row mt-3">
                                            <div class="col-md-6">
                                                <h6 class="text-purple"><i class="fas fa-chart-line me-2"></i>Membership Info</h6>
                                                {% if member.membership_end %}
                                                <div class="detail-item">
                                                    <i class="fas fa-calendar-times"></i>
                                                    <span>Expires: {{ member.membership_end[:10] if member.membership_end else 'Unknown' }}</span>
                                                </div>
                                                {% endif %}
                                                {% if member.last_visit %}
                                                <div class="detail-item">
                                                    <i class="fas fa-clock"></i>
                                                    <span>Last visit: {{ member.last_visit[:10] if member.last_visit else 'Never' }}</span>
                                                </div>
                                                {% endif %}
                                                {% if member.rating %}
                                                <div class="detail-item">
                                                    <i class="fas fa-star"></i>
                                                    <span>Rating: {{ member.rating }}/5</span>
                                                </div>
                                                {% endif %}
                                                {% if member.member_id %}
                                                <div class="detail-item">
                                                    <i class="fas fa-id-card"></i>
                                                    <span>Member ID: {{ member.member_id }}</span>
                                                </div>
                                                {% endif %}
                                            </div>
                                            <div class="col-md-6">
                                                <h6 class="text-purple"><i class="fas fa-exclamation-triangle me-2"></i>Account Status</h6>
                                                {% if member.status_message %}
                                                <div class="detail-item">
                                                    <i class="fas fa-info-circle"></i>
                                                    <span>{{ member.status_message }}</span>
                                                </div>
                                                {% endif %}
                                                {% if member.past_due %}
                                                <div class="detail-item text-danger">
                                                    <i class="fas fa-exclamation-circle"></i>
                                                    <span>Past Due: ${{ "%.2f"|format(member.past_due_amount or 0) }} ({{ member.past_due_days or 0 }} days)</span>
                                                </div>
                                                {% endif %}
                                                {% if member.has_app %}
                                                <div class="detail-item text-success">
                                                    <i class="fas fa-mobile-alt"></i>
                                                    <span>Has Mobile App</span>
                                                </div>
                                                {% endif %}
                                                {% if member.last_activity %}
                                                <div class="detail-item">
                                                    <i class="fas fa-clock"></i>
                                                    <span>Last activity: {{ member.last_activity[:10] if member.last_activity else 'Unknown' }}</span>
                                                </div>
                                                {% endif %}
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="dropdown">
                                <button class="btn btn-outline-primary dropdown-toggle btn-sm" type="button" data-bs-toggle="dropdown">
                                    Actions
                                </button>
                                <ul class="dropdown-menu">
                                    <li><a class="dropdown-item" href="#"><i class="fas fa-edit me-2"></i>Edit Profile</a></li>
                                    <li><a class="dropdown-item" href="#"><i class="fas fa-envelope me-2"></i>Send Message</a></li>
                                    <li><a class="dropdown-item" href="#"><i class="fas fa-credit-card me-2"></i>Process Payment</a></li>
                                    {% if member.past_due %}
                                    <li><a class="dropdown-item text-warning" href="#"><i class="fas fa-exclamation-triangle me-2"></i>Resolve Past Due</a></li>
                                    {% endif %}
                                    <li><hr class="dropdown-divider"></li>
                                    <li><a class="dropdown-item" href="#"><i class="fas fa-chart-bar me-2"></i>View History</a></li>
                                    <li><a class="dropdown-item" href="#"><i class="fas fa-user-friends me-2"></i>Add to PT</a></li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>
                {% endfor %}
            </div>
        {% else %}
            <div class="text-center py-5">
                <i class="fas fa-users fa-4x text-muted mb-3"></i>
                <h5 class="text-muted">No active members found</h5>
                <p class="text-muted">Start by adding your first member to the system.</p>
                <button class="btn btn-primary">
                    <i class="fas fa-plus me-2"></i>Add First Member
                </button>
            </div>
        {% endif %}
    </div>

    <!-- Prospects Tab -->
    <div class="tab-pane fade" id="prospects" role="tabpanel">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h4><i class="fas fa-user-plus me-2 text-purple"></i>Prospects Pipeline</h4>
            <button class="btn btn-primary">
                <i class="fas fa-plus me-2"></i>Add Prospect
            </button>
        </div>
        
        {% if prospects %}
            <div class="row">
                {% for prospect in prospects %}
                <div class="col-xl-6 col-lg-12">
                    <div class="prospect-item">
                        <div class="d-flex justify-content-between align-items-start">
                            <div class="flex-grow-1">
                                <div class="d-flex align-items-center mb-2">
                                    <div class="prospect-name">{{ prospect.name }}</div>
                                    {% if prospect.rating %}
                                    <div class="ms-2">
                                        <span class="badge badge-warning">
                                            {% for i in range(prospect.rating) %}<i class="fas fa-star"></i>{% endfor %}
                                            {{ prospect.rating }}/5
                                        </span>
                                    </div>
                                    {% endif %}
                                </div>
                                
                                <div class="prospect-details">
                                    <div class="detail-item">
                                        <i class="fas fa-envelope"></i>
                                        <span>{{ prospect.email or 'No email provided' }}</span>
                                    </div>
                                    <div class="detail-item">
                                        <i class="fas fa-phone"></i>
                                        <span>{{ prospect.phone or 'No phone provided' }}</span>
                                    </div>
                                    {% if prospect.source %}
                                    <div class="detail-item">
                                        <i class="fas fa-user-plus"></i>
                                        <span>Source: {{ prospect.source }}</span>
                                    </div>
                                    {% endif %}
                                    {% if prospect.prospect_id %}
                                    <div class="detail-item">
                                        <i class="fas fa-id-card"></i>
                                        <span>ID: {{ prospect.prospect_id }}</span>
                                    </div>
                                    {% endif %}
                                </div>
                                
                                <!-- Collapsible Details -->
                                <div class="mt-3">
                                    <button class="details-toggle" type="button" data-bs-toggle="collapse" data-bs-target="#prospect-details-{{ prospect.id }}" aria-expanded="false">
                                        <i class="fas fa-chevron-down me-1"></i>View Full Details
                                    </button>
                                    <div class="collapse collapse-content" id="prospect-details-{{ prospect.id }}">
                                        <div class="row">
                                            <div class="col-md-6">
                                                <h6 class="text-purple"><i class="fas fa-user me-2"></i>Personal Info</h6>
                                                {% if prospect.first_name and prospect.last_name %}
                                                <div class="detail-item">
                                                    <i class="fas fa-id-badge"></i>
                                                    <span>{{ prospect.first_name }} {{ prospect.last_name }}</span>
                                                </div>
                                                {% endif %}
                                                {% if prospect.status_message %}
                                                <div class="detail-item">
                                                    <i class="fas fa-info-circle"></i>
                                                    <span>{{ prospect.status_message }}</span>
                                                </div>
                                                {% endif %}
                                            </div>
                                            <div class="col-md-6">
                                                <h6 class="text-purple"><i class="fas fa-home me-2"></i>Address</h6>
                                                {% if prospect.address %}
                                                <div class="detail-item">
                                                    <i class="fas fa-map-marker-alt"></i>
                                                    <span>{{ prospect.address }}{% if prospect.address2 %}, {{ prospect.address2 }}{% endif %}</span>
                                                </div>
                                                {% endif %}
                                                {% if prospect.city %}
                                                <div class="detail-item">
                                                    <i class="fas fa-city"></i>
                                                    <span>{{ prospect.city }}{% if prospect.state %}, {{ prospect.state }}{% endif %} {{ prospect.zip_code or '' }}</span>
                                                </div>
                                                {% endif %}
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="dropdown">
                                <button class="btn btn-outline-success dropdown-toggle btn-sm" type="button" data-bs-toggle="dropdown">
                                    Actions
                                </button>
                                <ul class="dropdown-menu">
                                    <li><a class="dropdown-item text-success" href="#"><i class="fas fa-check me-2"></i>Convert to Member</a></li>
                                    <li><a class="dropdown-item" href="#"><i class="fas fa-edit me-2"></i>Edit Prospect</a></li>
                                    <li><a class="dropdown-item" href="#"><i class="fas fa-envelope me-2"></i>Send Follow-up</a></li>
                                    <li><a class="dropdown-item" href="#"><i class="fas fa-calendar me-2"></i>Schedule Tour</a></li>
                                    <li><a class="dropdown-item" href="#"><i class="fas fa-phone me-2"></i>Call Prospect</a></li>
                                    <li><hr class="dropdown-divider"></li>
                                    <li><a class="dropdown-item text-danger" href="#"><i class="fas fa-trash me-2"></i>Remove</a></li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>
                {% endfor %}
            </div>
        {% else %}
            <div class="text-center py-5">
                <i class="fas fa-user-plus fa-4x text-muted mb-3"></i>
                <h5 class="text-muted">No prospects in the pipeline</h5>
                <p class="text-muted">Add prospects to track potential new members and grow your business.</p>
                <button class="btn btn-primary">
                    <i class="fas fa-plus me-2"></i>Add First Prospect
                </button>
            </div>
        {% endif %}
    </div>
</div>
{% endblock %}'''

    # Save all templates
    templates = {
        'base.html': base_template,
        'dashboard.html': dashboard_template,
        'members.html': members_template,
        'training_clients.html': '''{% extends "base.html" %}
{% block title %}Personal Training - Anytime Fitness®{% endblock %}
{% block page_title %}Personal Training Management{% endblock %}
{% block page_subtitle %}Maximize your personal training revenue and client satisfaction{% endblock %}
{% block content %}
<div class="card">
    <div class="card-header d-flex justify-content-between align-items-center">
        <h5><i class="fas fa-user-friends me-2"></i>Personal Training Clients</h5>
        <button class="btn btn-primary btn-sm">
            <i class="fas fa-plus me-2"></i>Add PT Client
        </button>
    </div>
    <div class="card-body">
        {% if clients %}
        <div class="table-container">
            <table class="table">
                <thead>
                    <tr>
                        <th>Client</th>
                        <th>Trainer</th>
                        <th>Session Type</th>
                        <th>Sessions Left</th>
                        <th>Last Session</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {% for client in clients %}
                    <tr>
                        <td><strong>{{ client.member_name or 'Unknown Member' }}</strong></td>
                        <td>{{ client.trainer_name }}</td>
                        <td><span class="badge badge-purple">{{ client.session_type }}</span></td>
                        <td>
                            <span class="badge {% if client.sessions_remaining > 5 %}badge-success{% elif client.sessions_remaining > 2 %}badge-warning{% else %}bg-danger text-white{% endif %}">
                                {{ client.sessions_remaining }}
                            </span>
                        </td>
                        <td>{{ client.last_session or 'Never' }}</td>
                        <td>
                            <div class="btn-group btn-group-sm">
                                <button class="btn btn-outline-primary" title="Schedule Session">
                                    <i class="fas fa-calendar-plus"></i>
                                </button>
                                <button class="btn btn-outline-success" title="Add Sessions">
                                    <i class="fas fa-plus"></i>
                                </button>
                            </div>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        {% else %}
        <div class="text-center py-5">
            <i class="fas fa-user-friends fa-4x text-muted mb-3"></i>
            <h5 class="text-muted">No personal training clients</h5>
            <p class="text-muted">Start building your PT revenue by adding clients.</p>
        </div>
        {% endif %}
    </div>
</div>
{% endblock %}''',
        'messaging.html': '''{% extends "base.html" %}
{% block title %}Communications - Anytime Fitness®{% endblock %}
{% block page_title %}Member Communications{% endblock %}
{% block page_subtitle %}Stay connected with your Anytime Fitness community{% endblock %}
{% block content %}
<div class="card">
    <div class="card-header">
        <h5><i class="fas fa-comments me-2"></i>Communication Center</h5>
    </div>
    <div class="card-body text-center py-5">
        <i class="fas fa-comments fa-4x text-purple mb-3"></i>
        <h5>Advanced Communications Coming Soon</h5>
        <p class="text-muted">Powerful messaging features will be available here.</p>
    </div>
</div>
{% endblock %}''',
        'payments.html': '''{% extends "base.html" %}
{% block title %}Billing - Anytime Fitness®{% endblock %}
{% block page_title %}Billing & Payment Management{% endblock %}
{% block page_subtitle %}Streamline your revenue collection and billing processes{% endblock %}
{% block content %}
<div class="card">
    <div class="card-header">
        <h5><i class="fas fa-credit-card me-2"></i>Payment Processing Center</h5>
    </div>
    <div class="card-body text-center py-5">
        <i class="fas fa-credit-card fa-4x text-purple mb-3"></i>
        <h5>Payment Management Coming Soon</h5>
        <p class="text-muted">Comprehensive billing features will be available here.</p>
    </div>
</div>
{% endblock %}''',
        'social_media.html': '''{% extends "base.html" %}
{% block title %}Social Media - Anytime Fitness®{% endblock %}
{% block page_title %}Social Media Management{% endblock %}
{% block page_subtitle %}Build your brand and engage your community online{% endblock %}
{% block content %}
<div class="card">
    <div class="card-header">
        <h5><i class="fas fa-share-alt me-2"></i>Social Media Hub</h5>
    </div>
    <div class="card-body text-center py-5">
        <i class="fas fa-share-alt fa-4x text-purple mb-3"></i>
        <h5>Social Media Tools Coming Soon</h5>
        <p class="text-muted">Powerful social media management will be available here.</p>
    </div>
</div>
{% endblock %}''',
        'workflows.html': '''{% extends "base.html" %}
{% block title %}Automation - Anytime Fitness®{% endblock %}
{% block page_title %}Automation & Workflows{% endblock %}
{% block page_subtitle %}Automate your club operations for maximum efficiency{% endblock %}
{% block content %}
<div class="card">
    <div class="card-header">
        <h5><i class="fas fa-cogs me-2"></i>Automation Center</h5>
    </div>
    <div class="card-body text-center py-5">
        <i class="fas fa-cogs fa-4x text-purple mb-3"></i>
        <h5>Automation Features Coming Soon</h5>
        <p class="text-muted">Advanced workflow automation will be available here.</p>
    </div>
</div>
{% endblock %}'''
    }
    
    # Write templates to files
    for filename, content in templates.items():
        filepath = os.path.join(templates_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

if __name__ == '__main__':
    create_templates()
    print("Enhanced Anytime Fitness® Management Hub starting at http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
