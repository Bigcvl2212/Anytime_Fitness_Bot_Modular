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
    """Members page with separate tabs for members and prospects."""
    conn = sqlite3.connect(db_manager.db_path)
    cursor = conn.cursor()
    
    # Get members only
    cursor.execute("SELECT * FROM members ORDER BY name")
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
    """Create HTML templates."""
    templates_dir = 'templates'
    if not os.path.exists(templates_dir):
        os.makedirs(templates_dir)
    
    # Base template
    base_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Gym Bot Dashboard{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            --secondary-gradient: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            --success-gradient: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            --warning-gradient: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
            --dark-gradient: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            --glass-bg: rgba(255, 255, 255, 0.1);
            --glass-border: rgba(255, 255, 255, 0.2);
            --sidebar-gradient: linear-gradient(180deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
            --text-primary: #2d3748;
            --text-secondary: #718096;
            --shadow-lg: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
            --shadow-xl: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body { 
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: var(--primary-gradient);
            min-height: 100vh;
            overflow-x: hidden;
        }
        
        .sidebar {
            background: var(--sidebar-gradient);
            min-height: 100vh;
            position: fixed;
            width: 280px;
            left: 0;
            top: 0;
            padding: 0;
            backdrop-filter: blur(20px);
            border-right: 1px solid var(--glass-border);
            z-index: 1000;
        }
        
        .sidebar::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="50" cy="50" r="1" fill="rgba(255,255,255,0.03)"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
            opacity: 0.5;
        }
        
        .content-area {
            margin-left: 280px;
            padding: 30px 40px;
            min-height: 100vh;
            position: relative;
        }
        
        .logo-section {
            padding: 30px 25px;
            text-align: center;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            position: relative;
            z-index: 2;
        }
        
        .logo-section h4 {
            background: linear-gradient(45deg, #fff, #a78bfa);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-weight: 800;
            font-size: 1.5rem;
            letter-spacing: -0.025em;
        }
        
        .nav-section {
            padding: 20px 0;
            position: relative;
            z-index: 2;
        }
        
        .nav-link {
            color: rgba(255, 255, 255, 0.8) !important;
            padding: 16px 25px;
            margin: 4px 15px;
            border-radius: 12px;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            display: flex;
            align-items: center;
            font-weight: 500;
            font-size: 0.95rem;
            text-decoration: none;
            position: relative;
            overflow: hidden;
        }
        
        .nav-link::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.1), rgba(255, 255, 255, 0.05));
            opacity: 0;
            transition: opacity 0.3s ease;
        }
        
        .nav-link:hover::before,
        .nav-link.active::before {
            opacity: 1;
        }
        
        .nav-link:hover,
        .nav-link.active {
            color: #fff !important;
            transform: translateX(8px);
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
        }
        
        .nav-link i {
            margin-right: 12px;
            font-size: 1.1rem;
            width: 20px;
        }
        
        .card {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 20px;
            box-shadow: var(--shadow-lg);
            margin-bottom: 30px;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            overflow: hidden;
        }
        
        .card:hover {
            transform: translateY(-5px);
            box-shadow: var(--shadow-xl);
        }
        
        .card-header {
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.1), rgba(255, 255, 255, 0.05));
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            padding: 20px 25px;
            font-weight: 600;
            font-size: 1.1rem;
            color: var(--text-primary);
        }
        
        .card-body {
            padding: 25px;
        }
        
        .metric-card {
            background: var(--glass-bg);
            backdrop-filter: blur(20px);
            border: 1px solid var(--glass-border);
            color: white;
            text-align: center;
            position: relative;
            overflow: hidden;
        }
        
        .metric-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: var(--primary-gradient);
            opacity: 0.9;
            z-index: 1;
        }
        
        .metric-card .card-body {
            position: relative;
            z-index: 2;
        }
        
        .metric-card:nth-child(2)::before { background: var(--secondary-gradient); }
        .metric-card:nth-child(3)::before { background: var(--success-gradient); }
        .metric-card:nth-child(4)::before { background: var(--warning-gradient); }
        
        .metric-card h3 {
            font-size: 2.5rem;
            font-weight: 800;
            margin: 10px 0;
        }
        
        .metric-card h5 {
            font-weight: 600;
            opacity: 0.9;
        }
        
        .btn-primary {
            background: var(--primary-gradient);
            border: none;
            border-radius: 12px;
            padding: 12px 24px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            transition: all 0.3s ease;
        }
        
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4);
        }
        
        .table {
            background: transparent;
        }
        
        .table thead th {
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
            border: none;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-size: 0.85rem;
            color: var(--text-primary);
            padding: 20px 15px;
        }
        
        .table tbody td {
            border: none;
            padding: 15px;
            font-weight: 500;
            color: var(--text-primary);
            border-bottom: 1px solid rgba(0, 0, 0, 0.05);
        }
        
        .table tbody tr {
            transition: all 0.2s ease;
        }
        
        .table tbody tr:hover {
            background: rgba(102, 126, 234, 0.05);
            transform: scale(1.01);
        }
        
        .page-title {
            font-size: 2.5rem;
            font-weight: 800;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 10px;
        }
        
        .page-subtitle {
            color: rgba(255, 255, 255, 0.8);
            font-size: 1.1rem;
            font-weight: 400;
            margin-bottom: 30px;
        }
        
        .nav-tabs {
            border: none;
            margin-bottom: 30px;
        }
        
        .nav-tabs .nav-link {
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            color: rgba(255, 255, 255, 0.8);
            border-radius: 12px 12px 0 0;
            margin-right: 10px;
            padding: 15px 25px;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        
        .nav-tabs .nav-link.active {
            background: rgba(255, 255, 255, 0.95);
            color: var(--text-primary);
            border-color: rgba(255, 255, 255, 0.2);
        }
        
        .tab-content {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 0 20px 20px 20px;
            padding: 30px;
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .badge {
            padding: 8px 12px;
            font-weight: 600;
            border-radius: 8px;
        }
        
        .badge.bg-success { background: var(--success-gradient) !important; }
        .badge.bg-warning { background: var(--warning-gradient) !important; }
        .badge.bg-primary { background: var(--primary-gradient) !important; }
        
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .fade-in-up {
            animation: fadeInUp 0.6s ease-out;
        }
        
        .glassmorphism {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
    </style>
</head>
<body>
    <div class="d-flex">
        <nav class="sidebar">
            <div class="logo-section">
                <h4>
                    <i class="fas fa-dumbbell me-2"></i>Gym Bot Pro
                </h4>
            </div>
            <div class="nav-section">
                <ul class="nav flex-column">
                    <li class="nav-item">
                        <a class="nav-link" href="/"><i class="fas fa-chart-line"></i>Dashboard</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/members"><i class="fas fa-users"></i>Members</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/training-clients"><i class="fas fa-user-friends"></i>Training Clients</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/messaging"><i class="fas fa-comments"></i>Messaging</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/payments"><i class="fas fa-credit-card"></i>Payments</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/social-media"><i class="fas fa-share-alt"></i>Social Media</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/workflows"><i class="fas fa-cogs"></i>Workflows</a>
                    </li>
                </ul>
            </div>
        </nav>

        <div class="content-area">
            <div class="container-fluid">
                <div class="row mb-4">
                    <div class="col-12">
                        <h1 class="page-title">{% block page_title %}{% endblock %}</h1>
                        <p class="page-subtitle">{% block page_subtitle %}{% endblock %}</p>
                    </div>
                </div>
                <div class="row">
                    {% block content %}{% endblock %}
                </div>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    {% block scripts %}{% endblock %}
</body>
</html>'''

    # Dashboard template
    dashboard_template = '''{% extends "base.html" %}
{% block title %}Dashboard - Gym Bot Pro{% endblock %}
{% block page_title %}Dashboard Overview{% endblock %}
{% block page_subtitle %}Welcome to your state-of-the-art gym management system{% endblock %}

{% block content %}
<div class="col-md-3 fade-in-up" style="animation-delay: 0.1s;">
    <div class="card metric-card">
        <div class="card-body text-center">
            <i class="fas fa-users fa-2x mb-3" style="opacity: 0.8;"></i>
            <h5 class="card-title">Total Members</h5>
            <h3 class="counter" data-count="{{ total_members }}">0</h3>
            <small style="opacity: 0.8;">Active gym members</small>
        </div>
    </div>
</div>
<div class="col-md-3 fade-in-up" style="animation-delay: 0.2s;">
    <div class="card metric-card">
        <div class="card-body text-center">
            <i class="fas fa-user-plus fa-2x mb-3" style="opacity: 0.8;"></i>
            <h5 class="card-title">Active Prospects</h5>
            <h3 class="counter" data-count="{{ total_prospects }}">0</h3>
            <small style="opacity: 0.8;">Potential new members</small>
        </div>
    </div>
</div>
<div class="col-md-3 fade-in-up" style="animation-delay: 0.3s;">
    <div class="card metric-card">
        <div class="card-body text-center">
            <i class="fas fa-dumbbell fa-2x mb-3" style="opacity: 0.8;"></i>
            <h5 class="card-title">Training Clients</h5>
            <h3 class="counter" data-count="{{ total_training_clients }}">0</h3>
            <small style="opacity: 0.8;">Personal training clients</small>
        </div>
    </div>
</div>
<div class="col-md-3 fade-in-up" style="animation-delay: 0.4s;">
    <div class="card metric-card">
        <div class="card-body text-center">
            <i class="fas fa-envelope fa-2x mb-3" style="opacity: 0.8;"></i>
            <h5 class="card-title">Pending Messages</h5>
            <h3 class="counter" data-count="{{ pending_messages }}">0</h3>
            <small style="opacity: 0.8;">Unread member messages</small>
        </div>
    </div>
</div>

<div class="col-12 fade-in-up" style="animation-delay: 0.5s;">
    <div class="row">
        <div class="col-lg-8">
            <div class="card">
                <div class="card-header">
                    <h5><i class="fas fa-chart-pulse me-2"></i>Quick Actions</h5>
                </div>
                <div class="card-body">
                    <div class="row g-3">
                        <div class="col-md-6">
                            <a href="/members" class="btn btn-primary w-100 py-3">
                                <i class="fas fa-users me-2"></i>Manage Members
                            </a>
                        </div>
                        <div class="col-md-6">
                            <a href="/training-clients" class="btn btn-primary w-100 py-3">
                                <i class="fas fa-dumbbell me-2"></i>Training Clients
                            </a>
                        </div>
                        <div class="col-md-6">
                            <a href="/messaging" class="btn btn-primary w-100 py-3">
                                <i class="fas fa-comments me-2"></i>Messaging Center
                            </a>
                        </div>
                        <div class="col-md-6">
                            <a href="/workflows" class="btn btn-primary w-100 py-3">
                                <i class="fas fa-cogs me-2"></i>Automation
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <div class="col-lg-4">
            <div class="card">
                <div class="card-header">
                    <h5><i class="fas fa-bolt me-2"></i>System Status</h5>
                </div>
                <div class="card-body">
                    <div class="d-flex align-items-center mb-3">
                        <div class="status-indicator me-3">
                            <i class="fas fa-circle text-success"></i>
                        </div>
                        <div>
                            <strong>Database</strong><br>
                            <small class="text-muted">Connected and operational</small>
                        </div>
                    </div>
                    <div class="d-flex align-items-center mb-3">
                        <div class="status-indicator me-3">
                            <i class="fas fa-circle text-success"></i>
                        </div>
                        <div>
                            <strong>API Services</strong><br>
                            <small class="text-muted">All systems online</small>
                        </div>
                    </div>
                    <div class="d-flex align-items-center">
                        <div class="status-indicator me-3">
                            <i class="fas fa-circle text-warning"></i>
                        </div>
                        <div>
                            <strong>Messaging Bot</strong><br>
                            <small class="text-muted">Pending configuration</small>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script>
// Animate counters
document.addEventListener('DOMContentLoaded', function() {
    const counters = document.querySelectorAll('.counter');
    
    counters.forEach(counter => {
        const target = +counter.getAttribute('data-count');
        const increment = target / 100;
        let current = 0;
        
        const updateCounter = () => {
            if (current < target) {
                current += increment;
                counter.textContent = Math.ceil(current);
                setTimeout(updateCounter, 20);
            } else {
                counter.textContent = target;
            }
        };
        
        // Start animation with delay
        setTimeout(updateCounter, 500);
    });
});
</script>
{% endblock %}'''

    # All templates
    templates = {
        'base.html': base_template,
        'dashboard.html': dashboard_template,
        'members.html': '''{% extends "base.html" %}
{% block title %}Members{% endblock %}
{% block page_title %}Member Management{% endblock %}
{% block page_subtitle %}Manage your gym members and prospects with advanced tools{% endblock %}

{% block content %}
<div class="col-12">
    <ul class="nav nav-tabs" id="memberTabs" role="tablist">
        <li class="nav-item" role="presentation">
            <button class="nav-link active" id="members-tab" data-bs-toggle="tab" data-bs-target="#members" type="button" role="tab">
                <i class="fas fa-users me-2"></i>Active Members <span class="badge bg-primary ms-2">{{ members|length }}</span>
            </button>
        </li>
        <li class="nav-item" role="presentation">
            <button class="nav-link" id="prospects-tab" data-bs-toggle="tab" data-bs-target="#prospects" type="button" role="tab">
                <i class="fas fa-user-plus me-2"></i>Prospects <span class="badge bg-warning ms-2">{{ prospects|length }}</span>
            </button>
        </li>
    </ul>
    
    <div class="tab-content" id="memberTabContent">
        <div class="tab-pane fade show active" id="members" role="tabpanel">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h5 class="mb-0"><i class="fas fa-users me-2"></i>Active Members</h5>
                <div class="d-flex gap-2">
                    <button class="btn btn-primary">
                        <i class="fas fa-plus me-2"></i>Add Member
                    </button>
                    <button class="btn btn-outline-primary">
                        <i class="fas fa-download me-2"></i>Export
                    </button>
                </div>
            </div>
            
            {% if members %}
            <div class="table-responsive">
                <table class="table table-hover">
                    <thead>
                        <tr>
                            <th><i class="fas fa-user me-2"></i>Name</th>
                            <th><i class="fas fa-envelope me-2"></i>Email</th>
                            <th><i class="fas fa-phone me-2"></i>Phone</th>
                            <th><i class="fas fa-crown me-2"></i>Membership</th>
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
                                    <div class="avatar-circle me-3">
                                        {{ member.name[0]|upper }}
                                    </div>
                                    <div>
                                        <strong>{{ member.name }}</strong>
                                        {% if member.notes %}
                                        <br><small class="text-muted">{{ member.notes[:50] }}...</small>
                                        {% endif %}
                                    </div>
                                </div>
                            </td>
                            <td>{{ member.email or 'N/A' }}</td>
                            <td>{{ member.phone or 'N/A' }}</td>
                            <td>
                                <span class="badge bg-primary">{{ member.membership_type or 'Basic' }}</span>
                            </td>
                            <td>{{ member.join_date or 'N/A' }}</td>
                            <td>
                                {% if member.monthly_fee %}
                                <strong>${{ "%.2f"|format(member.monthly_fee) }}</strong>
                                {% else %}
                                N/A
                                {% endif %}
                            </td>
                            <td>
                                <span class="badge bg-success">{{ member.status|title }}</span>
                            </td>
                            <td>
                                <div class="btn-group" role="group">
                                    <button class="btn btn-sm btn-outline-primary" title="Edit">
                                        <i class="fas fa-edit"></i>
                                    </button>
                                    <button class="btn btn-sm btn-outline-info" title="Message">
                                        <i class="fas fa-envelope"></i>
                                    </button>
                                    <button class="btn btn-sm btn-outline-success" title="Payment">
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
                <i class="fas fa-users fa-4x text-muted mb-3"></i>
                <h5 class="text-muted">No members found</h5>
                <p class="text-muted">Start by adding your first member to the system.</p>
                <button class="btn btn-primary">
                    <i class="fas fa-plus me-2"></i>Add First Member
                </button>
            </div>
            {% endif %}
        </div>
        
        <div class="tab-pane fade" id="prospects" role="tabpanel">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h5 class="mb-0"><i class="fas fa-user-plus me-2"></i>Prospects</h5>
                <div class="d-flex gap-2">
                    <button class="btn btn-warning">
                        <i class="fas fa-plus me-2"></i>Add Prospect
                    </button>
                    <button class="btn btn-outline-warning">
                        <i class="fas fa-download me-2"></i>Export
                    </button>
                </div>
            </div>
            
            {% if prospects %}
            <div class="table-responsive">
                <table class="table table-hover">
                    <thead>
                        <tr>
                            <th><i class="fas fa-user me-2"></i>Name</th>
                            <th><i class="fas fa-envelope me-2"></i>Email</th>
                            <th><i class="fas fa-phone me-2"></i>Phone</th>
                            <th><i class="fas fa-chart-line me-2"></i>Status</th>
                            <th><i class="fas fa-calendar me-2"></i>Added</th>
                            <th><i class="fas fa-cogs me-2"></i>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for prospect in prospects %}
                        <tr>
                            <td>
                                <div class="d-flex align-items-center">
                                    <div class="avatar-circle me-3" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
                                        {{ prospect.name[0]|upper }}
                                    </div>
                                    <div>
                                        <strong>{{ prospect.name }}</strong>
                                        {% if prospect.notes %}
                                        <br><small class="text-muted">{{ prospect.notes[:50] }}...</small>
                                        {% endif %}
                                    </div>
                                </div>
                            </td>
                            <td>{{ prospect.email or 'N/A' }}</td>
                            <td>{{ prospect.phone or 'N/A' }}</td>
                            <td>
                                <span class="badge bg-warning">{{ prospect.status|title }}</span>
                            </td>
                            <td>{{ prospect.created_at[:10] if prospect.created_at else 'N/A' }}</td>
                            <td>
                                <div class="btn-group" role="group">
                                    <button class="btn btn-sm btn-outline-primary" title="Edit">
                                        <i class="fas fa-edit"></i>
                                    </button>
                                    <button class="btn btn-sm btn-outline-info" title="Message">
                                        <i class="fas fa-envelope"></i>
                                    </button>
                                    <button class="btn btn-sm btn-outline-success" title="Convert to Member">
                                        <i class="fas fa-user-check"></i>
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
                <i class="fas fa-user-plus fa-4x text-muted mb-3"></i>
                <h5 class="text-muted">No prospects found</h5>
                <p class="text-muted">Start building your prospect pipeline.</p>
                <button class="btn btn-warning">
                    <i class="fas fa-plus me-2"></i>Add First Prospect
                </button>
            </div>
            {% endif %}
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
<style>
.avatar-circle {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-weight: bold;
    font-size: 14px;
}
</style>
{% endblock %}''',
        'training_clients.html': '''{% extends "base.html" %}
{% block title %}Training Clients{% endblock %}
{% block page_title %}Personal Training Clients{% endblock %}
{% block content %}
<div class="col-12">
    <div class="card">
        <div class="card-header"><h5>Active Training Clients</h5></div>
        <div class="card-body">
            <div class="table-responsive">
                <table class="table">
                    <thead>
                        <tr>
                            <th>Member</th>
                            <th>Trainer</th>
                            <th>Session Type</th>
                            <th>Sessions Remaining</th>
                            <th>Last Session</th>
                            <th>Notes</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for client in clients %}
                        <tr>
                            <td>{{ client.member_name or 'Unknown Member' }}</td>
                            <td>{{ client.trainer_name }}</td>
                            <td>{{ client.session_type }}</td>
                            <td>{{ client.sessions_remaining }}</td>
                            <td>{{ client.last_session or 'Never' }}</td>
                            <td>{{ client.notes or 'No notes' }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</div>
{% endblock %}''',
        'messaging.html': '''{% extends "base.html" %}
{% block title %}Messaging{% endblock %}
{% block page_title %}Member Messaging{% endblock %}
{% block content %}
<div class="col-12">
    <div class="card">
        <div class="card-header"><h5>Messaging Center</h5></div>
        <div class="card-body">
            <p>Messaging functionality coming soon!</p>
        </div>
    </div>
</div>
{% endblock %}''',
        'payments.html': '''{% extends "base.html" %}
{% block title %}Payments{% endblock %}
{% block page_title %}Payment Management{% endblock %}
{% block content %}
<div class="col-12">
    <div class="card">
        <div class="card-header"><h5>Payment Management</h5></div>
        <div class="card-body">
            <p>Payment management coming soon!</p>
        </div>
    </div>
</div>
{% endblock %}''',
        'social_media.html': '''{% extends "base.html" %}
{% block title %}Social Media{% endblock %}
{% block page_title %}Social Media Management{% endblock %}
{% block content %}
<div class="col-12">
    <div class="card">
        <div class="card-header"><h5>Social Media Management</h5></div>
        <div class="card-body">
            <p>Social media management coming soon!</p>
        </div>
    </div>
</div>
{% endblock %}''',
        'workflows.html': '''{% extends "base.html" %}
{% block title %}Workflows{% endblock %}
{% block page_title %}Bot Controls{% endblock %}
{% block content %}
<div class="col-12">
    <div class="card">
        <div class="card-header"><h5>Workflow Controls</h5></div>
        <div class="card-body">
            <p>Workflow controls coming soon!</p>
        </div>
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
    print("Dashboard starting at http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
