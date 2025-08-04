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
        
        # Members table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE,
                phone TEXT,
                membership_type TEXT,
                status TEXT DEFAULT 'active',
                join_date DATE,
                monthly_fee REAL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Prospects table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS prospects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE,
                phone TEXT,
                status TEXT DEFAULT 'active',
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
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
        """Import master contact list from CSV."""
        if not os.path.exists(csv_path):
            logger.warning(f"Master contact list not found: {csv_path}")
            return
            
        df = pd.read_csv(csv_path)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for _, row in df.iterrows():
            # Check if it's a member or prospect based on membership type
            if pd.notna(row.get('MembershipType')) and str(row.get('MembershipType')).strip():
                # It's a member
                cursor.execute('''
                    INSERT OR REPLACE INTO members (name, email, phone, membership_type, status, join_date, monthly_fee, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    row.get('Name', ''), row.get('Email', ''), row.get('Phone', ''), 
                    row.get('MembershipType', ''), row.get('Status', 'active'), 
                    row.get('JoinDate', ''), row.get('MonthlyFee', 0), row.get('Notes', '')
                ))
            else:
                # It's a prospect
                cursor.execute('''
                    INSERT OR REPLACE INTO prospects (name, email, phone, status, notes)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    row.get('Name', ''), row.get('Email', ''), row.get('Phone', ''), 
                    row.get('Status', 'active'), row.get('Notes', '')
                ))
        
        conn.commit()
        conn.close()
        logger.info("Master contact list imported successfully")
        
    def import_training_clients(self, csv_path):
        """Import training clients from CSV."""
        if not os.path.exists(csv_path):
            logger.warning(f"Training clients list not found: {csv_path}")
            return
            
        try:
            df = pd.read_csv(csv_path)
            if df.empty:
                logger.info("Training clients CSV is empty")
                return
        except pd.errors.EmptyDataError:
            logger.info("Training clients CSV has no data")
            return
        except Exception as e:
            logger.warning(f"Error reading training clients CSV: {e}")
            return
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for _, row in df.iterrows():
            # Try to find member_id by name
            cursor.execute('SELECT id FROM members WHERE name = ?', (row.get('Name', ''),))
            member = cursor.fetchone()
            member_id = member[0] if member else None
            cursor.execute('''
                INSERT INTO training_clients (member_id, trainer_name, session_type, sessions_remaining, last_session, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                member_id, row.get('Trainer', ''), row.get('SessionType', ''), 
                row.get('SessionsRemaining', 0), row.get('LastSession', ''), row.get('Notes', '')
            ))
        conn.commit()
        conn.close()
        logger.info("Training clients imported successfully")

# Initialize database
db_manager = DatabaseManager()

# Import data from CSVs
master_csv = 'data/exports/master_contact_list_20250715_233148.csv'
training_csv = 'data/exports/training_clients_list.csv'
db_manager.import_master_contact_list(master_csv)
db_manager.import_training_clients(training_csv)

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
    
    # Get members only (those with membership types)
    cursor.execute("SELECT * FROM members WHERE membership_type IS NOT NULL AND membership_type != '' ORDER BY name")
    members = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]
    
    # Get prospects only
    cursor.execute("SELECT * FROM prospects ORDER BY name")
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

def create_templates():
    """Create HTML templates with Anytime Fitness branding."""
    templates_dir = 'templates'
    if not os.path.exists(templates_dir):
        os.makedirs(templates_dir)
    
    # Base template with official Anytime Fitness branding
    base_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Anytime Fitness Management Hub{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
    <style>
        :root {
            --af-purple: #522D80;
            --af-orange: #F15A24;
            --af-light-purple: #6A4C93;
            --af-dark-purple: #3C1A5B;
            --af-gray: #F8F9FA;
            --af-white: #FFFFFF;
            --af-black: #1A1A1A;
            --af-gradient: linear-gradient(135deg, #522D80 0%, #F15A24 100%);
            --af-shadow: 0 8px 32px rgba(82, 45, 128, 0.2);
            --af-hover-shadow: 0 12px 40px rgba(82, 45, 128, 0.3);
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body { 
            font-family: 'Montserrat', sans-serif;
            background: linear-gradient(135deg, #522D80 0%, #6A4C93 50%, #F15A24 100%);
            background-attachment: fixed;
            min-height: 100vh;
            color: var(--af-black);
            overflow-x: hidden;
        }
        
        .sidebar {
            background: rgba(26, 26, 26, 0.95);
            backdrop-filter: blur(20px);
            min-height: 100vh;
            position: fixed;
            width: 280px;
            left: 0;
            top: 0;
            padding: 0;
            box-shadow: 4px 0 30px rgba(0,0,0,0.3);
            border-right: 3px solid var(--af-orange);
            z-index: 1000;
        }
        
        .sidebar-brand {
            background: var(--af-gradient);
            padding: 25px 20px;
            text-align: center;
            position: relative;
            overflow: hidden;
        }
        
        .sidebar-brand::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: linear-gradient(45deg, transparent, rgba(255,255,255,0.1), transparent);
            animation: shine 3s infinite;
        }
        
        @keyframes shine {
            0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
            100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
        }
        
        .sidebar-brand h3 {
            color: white;
            font-weight: 800;
            font-size: 1.4rem;
            margin: 0;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            position: relative;
            z-index: 1;
        }
        
        .sidebar-brand .tagline {
            color: rgba(255,255,255,0.9);
            font-size: 0.75rem;
            font-weight: 500;
            margin-top: 5px;
            letter-spacing: 1px;
            text-transform: uppercase;
        }
        
        .content-area {
            margin-left: 280px;
            padding: 30px;
            min-height: 100vh;
        }
        
        .nav-link {
            color: rgba(255,255,255,0.8) !important;
            padding: 18px 25px;
            border-radius: 0;
            transition: all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
            font-weight: 500;
            font-size: 0.95rem;
            border-left: 4px solid transparent;
            position: relative;
            overflow: hidden;
        }
        
        .nav-link::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(241, 90, 36, 0.2), transparent);
            transition: left 0.5s;
        }
        
        .nav-link:hover::before {
            left: 100%;
        }
        
        .nav-link:hover, .nav-link.active {
            background: linear-gradient(90deg, rgba(241, 90, 36, 0.15), rgba(82, 45, 128, 0.15));
            color: #F15A24 !important;
            border-left-color: var(--af-orange);
            transform: translateX(8px);
            box-shadow: inset 0 0 20px rgba(241, 90, 36, 0.1);
        }
        
        .nav-link i {
            width: 20px;
            margin-right: 12px;
            font-size: 1.1rem;
        }
        
        .card {
            border: none;
            border-radius: 20px;
            box-shadow: var(--af-shadow);
            margin-bottom: 30px;
            backdrop-filter: blur(20px);
            background: rgba(255,255,255,0.95);
            transition: all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
            overflow: hidden;
            position: relative;
        }
        
        .card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: var(--af-gradient);
        }
        
        .card:hover {
            transform: translateY(-8px);
            box-shadow: var(--af-hover-shadow);
        }
        
        .card-header {
            background: linear-gradient(135deg, rgba(82, 45, 128, 0.1), rgba(241, 90, 36, 0.05));
            border-bottom: 2px solid rgba(82, 45, 128, 0.1);
            padding: 20px 25px;
            font-weight: 700;
            color: var(--af-dark-purple);
        }
        
        .card-body {
            padding: 25px;
        }
        
        .metric-card {
            background: var(--af-gradient);
            color: white;
            text-align: center;
            border: none;
            transform-style: preserve-3d;
            perspective: 1000px;
        }
        
        .metric-card:hover {
            transform: translateY(-12px) rotateX(5deg);
        }
        
        .metric-card .card-body {
            padding: 30px 20px;
            position: relative;
            overflow: hidden;
        }
        
        .metric-card::after {
            content: '';
            position: absolute;
            top: -50%;
            right: -50%;
            width: 100%;
            height: 200%;
            background: linear-gradient(45deg, transparent, rgba(255,255,255,0.1), transparent);
            transform: rotate(45deg);
            animation: shimmer 4s infinite;
        }
        
        @keyframes shimmer {
            0% { transform: translateX(-100%) rotate(45deg); }
            100% { transform: translateX(200%) rotate(45deg); }
        }
        
        .metric-number {
            font-size: 3rem;
            font-weight: 900;
            margin: 15px 0;
            text-shadow: 2px 2px 8px rgba(0,0,0,0.3);
            position: relative;
            z-index: 1;
        }
        
        .metric-title {
            font-size: 1.1rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            opacity: 0.95;
            position: relative;
            z-index: 1;
        }
        
        .metric-subtitle {
            font-size: 0.85rem;
            opacity: 0.8;
            margin-top: 8px;
            position: relative;
            z-index: 1;
        }
        
        .btn-primary {
            background: var(--af-gradient);
            border: none;
            border-radius: 50px;
            padding: 12px 30px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(82, 45, 128, 0.3);
        }
        
        .btn-primary:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(82, 45, 128, 0.4);
            background: linear-gradient(135deg, #F15A24 0%, #522D80 100%);
        }
        
        .page-header {
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(20px);
            border-radius: 20px;
            padding: 25px 30px;
            margin-bottom: 30px;
            border: 1px solid rgba(255,255,255,0.2);
        }
        
        .page-title {
            font-size: 2.2rem;
            font-weight: 800;
            color: white;
            text-shadow: 2px 2px 8px rgba(0,0,0,0.3);
            margin: 0;
        }
        
        .page-subtitle {
            color: rgba(255,255,255,0.8);
            font-size: 1rem;
            margin-top: 8px;
            font-weight: 500;
        }
        
        .table {
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        }
        
        .table thead th {
            background: var(--af-gradient);
            color: white;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            border: none;
            padding: 18px 15px;
        }
        
        .table tbody tr {
            transition: all 0.3s ease;
        }
        
        .table tbody tr:hover {
            background: linear-gradient(90deg, rgba(82, 45, 128, 0.05), rgba(241, 90, 36, 0.05));
            transform: scale(1.01);
        }
        
        .table tbody td {
            padding: 15px;
            border-color: rgba(82, 45, 128, 0.1);
            vertical-align: middle;
        }
        
        .badge {
            padding: 8px 15px;
            border-radius: 50px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .nav-tabs {
            border: none;
            margin-bottom: 25px;
        }
        
        .nav-tabs .nav-link {
            border: none;
            border-radius: 50px;
            margin-right: 10px;
            padding: 12px 25px;
            font-weight: 600;
            color: var(--af-purple);
            background: rgba(255,255,255,0.8);
            transition: all 0.3s ease;
        }
        
        .nav-tabs .nav-link.active {
            background: var(--af-gradient);
            color: white;
            box-shadow: 0 4px 15px rgba(82, 45, 128, 0.3);
        }
        
        .nav-tabs .nav-link:hover {
            background: rgba(82, 45, 128, 0.1);
            transform: translateY(-2px);
        }
        
        .status-indicator {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            display: inline-block;
            margin-right: 8px;
            box-shadow: 0 0 10px currentColor;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        
        .glass-effect {
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255,255,255,0.2);
        }
        
        @media (max-width: 768px) {
            .sidebar {
                transform: translateX(-100%);
                transition: transform 0.3s ease;
            }
            
            .content-area {
                margin-left: 0;
                padding: 20px;
            }
            
            .metric-number {
                font-size: 2rem;
            }
        }
    </style>
</head>
<body>
    <div class="d-flex">
        <nav class="sidebar">
            <div class="sidebar-brand">
                <h3><i class="fas fa-dumbbell me-2"></i>ANYTIME FITNESS</h3>
                <div class="tagline">Management Hub</div>
            </div>
            <div class="mt-3">
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
                        <a class="nav-link" href="/messaging"><i class="fas fa-comments"></i>Member Communications</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/payments"><i class="fas fa-credit-card"></i>Billing & Payments</a>
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
        // Add active class to current nav item
        document.addEventListener('DOMContentLoaded', function() {
            const currentPath = window.location.pathname;
            document.querySelectorAll('.nav-link').forEach(link => {
                if (link.getAttribute('href') === currentPath) {
                    link.classList.add('active');
                }
            });
        });
        
        // Animate numbers on page load
        function animateNumbers() {
            document.querySelectorAll('.metric-number').forEach(element => {
                const target = parseInt(element.textContent);
                let current = 0;
                const increment = target / 50;
                const timer = setInterval(() => {
                    current += increment;
                    if (current >= target) {
                        current = target;
                        clearInterval(timer);
                    }
                    element.textContent = Math.floor(current);
                }, 30);
            });
        }
        
        // Initialize animations
        setTimeout(animateNumbers, 500);
    </script>
    {% block scripts %}{% endblock %}
</body>
</html>'''

    # Dashboard template with Anytime Fitness styling
    dashboard_template = '''{% extends "base.html" %}
{% block title %}Dashboard - Anytime Fitness Management Hub{% endblock %}
{% block page_title %}Club Dashboard{% endblock %}
{% block page_subtitle %}Real-time overview of your Anytime Fitness location{% endblock %}

{% block content %}
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
                <div class="metric-title">Hot Prospects</div>
                <div class="metric-number">{{ total_prospects }}</div>
                <div class="metric-subtitle">Ready to convert</div>
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
                <div class="metric-title">Pending Tasks</div>
                <div class="metric-number">{{ pending_messages }}</div>
                <div class="metric-subtitle">Requires attention</div>
            </div>
        </div>
    </div>
</div>

<div class="row">
    <div class="col-lg-8 mb-4">
        <div class="card">
            <div class="card-header">
                <h5><i class="fas fa-chart-line me-2"></i>Club Performance Metrics</h5>
            </div>
            <div class="card-body">
                <div class="row">
                    <div class="col-md-6 mb-3">
                        <div class="glass-effect p-3 rounded">
                            <h6 class="text-purple fw-bold">Member Retention</h6>
                            <div class="d-flex align-items-center">
                                <div class="status-indicator bg-success"></div>
                                <span class="fs-4 fw-bold text-success">94.2%</span>
                            </div>
                            <small class="text-muted">Above industry average</small>
                        </div>
                    </div>
                    <div class="col-md-6 mb-3">
                        <div class="glass-effect p-3 rounded">
                            <h6 class="text-purple fw-bold">Monthly Growth</h6>
                            <div class="d-flex align-items-center">
                                <div class="status-indicator bg-warning"></div>
                                <span class="fs-4 fw-bold text-warning">+12.8%</span>
                            </div>
                            <small class="text-muted">New member acquisitions</small>
                        </div>
                    </div>
                    <div class="col-md-6 mb-3">
                        <div class="glass-effect p-3 rounded">
                            <h6 class="text-purple fw-bold">Revenue Growth</h6>
                            <div class="d-flex align-items-center">
                                <div class="status-indicator bg-success"></div>
                                <span class="fs-4 fw-bold text-success">+18.5%</span>
                            </div>
                            <small class="text-muted">Year over year</small>
                        </div>
                    </div>
                    <div class="col-md-6 mb-3">
                        <div class="glass-effect p-3 rounded">
                            <h6 class="text-purple fw-bold">PT Utilization</h6>
                            <div class="d-flex align-items-center">
                                <div class="status-indicator bg-info"></div>
                                <span class="fs-4 fw-bold text-info">87.3%</span>
                            </div>
                            <small class="text-muted">Trainer capacity used</small>
                        </div>
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
                        <i class="fas fa-users me-2"></i>Manage Members
                    </a>
                    <a href="/training-clients" class="btn btn-primary">
                        <i class="fas fa-user-friends me-2"></i>Personal Training
                    </a>
                    <a href="/payments" class="btn btn-primary">
                        <i class="fas fa-credit-card me-2"></i>Process Payments
                    </a>
                    <a href="/messaging" class="btn btn-primary">
                        <i class="fas fa-comments me-2"></i>Member Messages
                    </a>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}'''

    # Members template with separate sections
    members_template = '''{% extends "base.html" %}
{% block title %}Members & Prospects - Anytime Fitness{% endblock %}
{% block page_title %}Member Management{% endblock %}
{% block page_subtitle %}Manage your active members and convert prospects{% endblock %}

{% block content %}
<!-- Tab Navigation -->
<ul class="nav nav-tabs" id="memberTabs" role="tablist">
    <li class="nav-item" role="presentation">
        <button class="nav-link active" id="members-tab" data-bs-toggle="tab" data-bs-target="#members" type="button" role="tab">
            <i class="fas fa-users me-2"></i>Active Members ({{ members|length }})
        </button>
    </li>
    <li class="nav-item" role="presentation">
        <button class="nav-link" id="prospects-tab" data-bs-toggle="tab" data-bs-target="#prospects" type="button" role="tab">
            <i class="fas fa-user-plus me-2"></i>Hot Prospects ({{ prospects|length }})
        </button>
    </li>
</ul>

<!-- Tab Content -->
<div class="tab-content" id="memberTabContent">
    <!-- Members Tab -->
    <div class="tab-pane fade show active" id="members" role="tabpanel">
        <div class="card">
            <div class="card-header d-flex justify-content-between align-items-center">
                <h5><i class="fas fa-users me-2"></i>Active Anytime Fitness Members</h5>
                <button class="btn btn-primary btn-sm">
                    <i class="fas fa-plus me-2"></i>Add Member
                </button>
            </div>
            <div class="card-body">
                {% if members %}
                <div class="table-responsive">
                    <table class="table table-hover">
                        <thead>
                            <tr>
                                <th><i class="fas fa-user me-2"></i>Member Name</th>
                                <th><i class="fas fa-envelope me-2"></i>Email</th>
                                <th><i class="fas fa-phone me-2"></i>Phone</th>
                                <th><i class="fas fa-id-card me-2"></i>Membership</th>
                                <th><i class="fas fa-calendar me-2"></i>Join Date</th>
                                <th><i class="fas fa-dollar-sign me-2"></i>Monthly Fee</th>
                                <th><i class="fas fa-chart-line me-2"></i>Status</th>
                                <th><i class="fas fa-cogs me-2"></i>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for member in members %}
                            <tr>
                                <td>
                                    <div class="d-flex align-items-center">
                                        <div class="bg-gradient-purple rounded-circle d-flex align-items-center justify-content-center me-3" style="width: 40px; height: 40px;">
                                            <i class="fas fa-user text-white"></i>
                                        </div>
                                        <strong>{{ member.name }}</strong>
                                    </div>
                                </td>
                                <td>{{ member.email or 'Not provided' }}</td>
                                <td>{{ member.phone or 'Not provided' }}</td>
                                <td>
                                    <span class="badge bg-gradient" style="background: var(--af-gradient);">
                                        {{ member.membership_type }}
                                    </span>
                                </td>
                                <td>{{ member.join_date or 'N/A' }}</td>
                                <td>
                                    <strong class="text-success">
                                        ${{ "%.2f"|format(member.monthly_fee or 0) }}
                                    </strong>
                                </td>
                                <td>
                                    <span class="badge {% if member.status == 'active' %}bg-success{% else %}bg-warning{% endif %}">
                                        {{ member.status.title() }}
                                    </span>
                                </td>
                                <td>
                                    <div class="btn-group btn-group-sm">
                                        <button class="btn btn-outline-primary" title="Edit Member">
                                            <i class="fas fa-edit"></i>
                                        </button>
                                        <button class="btn btn-outline-info" title="Send Message">
                                            <i class="fas fa-envelope"></i>
                                        </button>
                                        <button class="btn btn-outline-success" title="Process Payment">
                                            <i class="fas fa-credit-card"></i>
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
                    <i class="fas fa-users fa-3x text-muted mb-3"></i>
                    <h5 class="text-muted">No active members found</h5>
                    <p class="text-muted">Start by adding your first member to the system.</p>
                    <button class="btn btn-primary">
                        <i class="fas fa-plus me-2"></i>Add First Member
                    </button>
                </div>
                {% endif %}
            </div>
        </div>
    </div>

    <!-- Prospects Tab -->
    <div class="tab-pane fade" id="prospects" role="tabpanel">
        <div class="card">
            <div class="card-header d-flex justify-content-between align-items-center">
                <h5><i class="fas fa-user-plus me-2"></i>Hot Prospects Ready to Convert</h5>
                <button class="btn btn-primary btn-sm">
                    <i class="fas fa-plus me-2"></i>Add Prospect
                </button>
            </div>
            <div class="card-body">
                {% if prospects %}
                <div class="table-responsive">
                    <table class="table table-hover">
                        <thead>
                            <tr>
                                <th><i class="fas fa-user-plus me-2"></i>Prospect Name</th>
                                <th><i class="fas fa-envelope me-2"></i>Email</th>
                                <th><i class="fas fa-phone me-2"></i>Phone</th>
                                <th><i class="fas fa-calendar-plus me-2"></i>Added Date</th>
                                <th><i class="fas fa-chart-line me-2"></i>Status</th>
                                <th><i class="fas fa-sticky-note me-2"></i>Notes</th>
                                <th><i class="fas fa-cogs me-2"></i>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for prospect in prospects %}
                            <tr>
                                <td>
                                    <div class="d-flex align-items-center">
                                        <div class="bg-gradient-orange rounded-circle d-flex align-items-center justify-content-center me-3" style="width: 40px; height: 40px; background: var(--af-orange);">
                                            <i class="fas fa-user-plus text-white"></i>
                                        </div>
                                        <strong>{{ prospect.name }}</strong>
                                    </div>
                                </td>
                                <td>{{ prospect.email or 'Not provided' }}</td>
                                <td>{{ prospect.phone or 'Not provided' }}</td>
                                <td>{{ prospect.created_at[:10] if prospect.created_at else 'N/A' }}</td>
                                <td>
                                    <span class="badge bg-warning">
                                        {{ prospect.status.title() }}
                                    </span>
                                </td>
                                <td>
                                    <small>{{ (prospect.notes[:50] + '...') if prospect.notes and prospect.notes|length > 50 else (prospect.notes or 'No notes') }}</small>
                                </td>
                                <td>
                                    <div class="btn-group btn-group-sm">
                                        <button class="btn btn-outline-success" title="Convert to Member">
                                            <i class="fas fa-check"></i>
                                        </button>
                                        <button class="btn btn-outline-primary" title="Edit Prospect">
                                            <i class="fas fa-edit"></i>
                                        </button>
                                        <button class="btn btn-outline-info" title="Send Follow-up">
                                            <i class="fas fa-envelope"></i>
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
                    <i class="fas fa-user-plus fa-3x text-muted mb-3"></i>
                    <h5 class="text-muted">No prospects in the pipeline</h5>
                    <p class="text-muted">Add prospects to track potential new members.</p>
                    <button class="btn btn-primary">
                        <i class="fas fa-plus me-2"></i>Add First Prospect
                    </button>
                </div>
                {% endif %}
            </div>
        </div>
    </div>
</div>
{% endblock %}'''

    # All templates
    templates = {
        'base.html': base_template,
        'dashboard.html': dashboard_template,
        'members.html': members_template,
        'training_clients.html': '''{% extends "base.html" %}
{% block title %}Personal Training - Anytime Fitness{% endblock %}
{% block page_title %}Personal Training Management{% endblock %}
{% block page_subtitle %}Maximize your personal training revenue and client satisfaction{% endblock %}
{% block content %}
<div class="card">
    <div class="card-header d-flex justify-content-between align-items-center">
        <h5><i class="fas fa-user-friends me-2"></i>Active Personal Training Clients</h5>
        <button class="btn btn-primary btn-sm">
            <i class="fas fa-plus me-2"></i>Add PT Client
        </button>
    </div>
    <div class="card-body">
        {% if clients %}
        <div class="table-responsive">
            <table class="table table-hover">
                <thead>
                    <tr>
                        <th><i class="fas fa-user me-2"></i>Client</th>
                        <th><i class="fas fa-user-tie me-2"></i>Trainer</th>
                        <th><i class="fas fa-dumbbell me-2"></i>Session Type</th>
                        <th><i class="fas fa-clock me-2"></i>Sessions Left</th>
                        <th><i class="fas fa-calendar me-2"></i>Last Session</th>
                        <th><i class="fas fa-sticky-note me-2"></i>Notes</th>
                        <th><i class="fas fa-cogs me-2"></i>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {% for client in clients %}
                    <tr>
                        <td>
                            <div class="d-flex align-items-center">
                                <div class="bg-gradient rounded-circle d-flex align-items-center justify-content-center me-3" style="width: 40px; height: 40px; background: var(--af-gradient);">
                                    <i class="fas fa-user text-white"></i>
                                </div>
                                <strong>{{ client.member_name or 'Unknown Member' }}</strong>
                            </div>
                        </td>
                        <td>{{ client.trainer_name }}</td>
                        <td>
                            <span class="badge bg-info">{{ client.session_type }}</span>
                        </td>
                        <td>
                            <span class="badge {% if client.sessions_remaining > 5 %}bg-success{% elif client.sessions_remaining > 2 %}bg-warning{% else %}bg-danger{% endif %}">
                                {{ client.sessions_remaining }}
                            </span>
                        </td>
                        <td>{{ client.last_session or 'Never' }}</td>
                        <td>
                            <small>{{ (client.notes[:30] + '...') if client.notes and client.notes|length > 30 else (client.notes or 'No notes') }}</small>
                        </td>
                        <td>
                            <div class="btn-group btn-group-sm">
                                <button class="btn btn-outline-primary" title="Schedule Session">
                                    <i class="fas fa-calendar-plus"></i>
                                </button>
                                <button class="btn btn-outline-success" title="Add Sessions">
                                    <i class="fas fa-plus"></i>
                                </button>
                                <button class="btn btn-outline-info" title="View Progress">
                                    <i class="fas fa-chart-line"></i>
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
            <i class="fas fa-user-friends fa-3x text-muted mb-3"></i>
            <h5 class="text-muted">No personal training clients</h5>
            <p class="text-muted">Start building your PT revenue by adding clients.</p>
            <button class="btn btn-primary">
                <i class="fas fa-plus me-2"></i>Add First PT Client
            </button>
        </div>
        {% endif %}
    </div>
</div>
{% endblock %}''',
        'messaging.html': '''{% extends "base.html" %}
{% block title %}Member Communications - Anytime Fitness{% endblock %}
{% block page_title %}Member Communications{% endblock %}
{% block page_subtitle %}Stay connected with your Anytime Fitness community{% endblock %}
{% block content %}
<div class="card">
    <div class="card-header">
        <h5><i class="fas fa-comments me-2"></i>Communication Center</h5>
    </div>
    <div class="card-body text-center py-5">
        <i class="fas fa-comments fa-3x text-muted mb-3"></i>
        <h5 class="text-muted">Member Communications Coming Soon</h5>
        <p class="text-muted">Advanced messaging features will be available here.</p>
    </div>
</div>
{% endblock %}''',
        'payments.html': '''{% extends "base.html" %}
{% block title %}Billing & Payments - Anytime Fitness{% endblock %}
{% block page_title %}Billing & Payment Management{% endblock %}
{% block page_subtitle %}Streamline your revenue collection and billing processes{% endblock %}
{% block content %}
<div class="card">
    <div class="card-header">
        <h5><i class="fas fa-credit-card me-2"></i>Payment Processing Center</h5>
    </div>
    <div class="card-body text-center py-5">
        <i class="fas fa-credit-card fa-3x text-muted mb-3"></i>
        <h5 class="text-muted">Payment Management Coming Soon</h5>
        <p class="text-muted">Comprehensive billing and payment features will be available here.</p>
    </div>
</div>
{% endblock %}''',
        'social_media.html': '''{% extends "base.html" %}
{% block title %}Social Media - Anytime Fitness{% endblock %}
{% block page_title %}Social Media Management{% endblock %}
{% block page_subtitle %}Build your brand and engage your community online{% endblock %}
{% block content %}
<div class="card">
    <div class="card-header">
        <h5><i class="fas fa-share-alt me-2"></i>Social Media Hub</h5>
    </div>
    <div class="card-body text-center py-5">
        <i class="fas fa-share-alt fa-3x text-muted mb-3"></i>
        <h5 class="text-muted">Social Media Management Coming Soon</h5>
        <p class="text-muted">Powerful social media tools will be available here.</p>
    </div>
</div>
{% endblock %}''',
        'workflows.html': '''{% extends "base.html" %}
{% block title %}Automation - Anytime Fitness{% endblock %}
{% block page_title %}Automation & Workflows{% endblock %}
{% block page_subtitle %}Automate your club operations for maximum efficiency{% endblock %}
{% block content %}
<div class="card">
    <div class="card-header">
        <h5><i class="fas fa-cogs me-2"></i>Automation Center</h5>
    </div>
    <div class="card-body text-center py-5">
        <i class="fas fa-cogs fa-3x text-muted mb-3"></i>
        <h5 class="text-muted">Automation Features Coming Soon</h5>
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
    print("Anytime Fitness Management Hub starting at http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
