"""
Gym Bot Dashboard - Clean Functional Version
"""

import os
import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'gym-bot-dashboard-secret-key'

# Database initialization
def init_database():
    """Initialize SQLite database with proper schema."""
    conn = sqlite3.connect('gym_bot.db')
    cursor = conn.cursor()
    
    # Members table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            membership_type TEXT NOT NULL,
            monthly_fee REAL NOT NULL,
            join_date TEXT NOT NULL,
            status TEXT DEFAULT 'active',
            last_payment_date TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Prospects table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS prospects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            interest_level TEXT,
            source TEXT,
            notes TEXT,
            last_contact_date TEXT,
            status TEXT DEFAULT 'new',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Training clients table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS training_clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            trainer_name TEXT,
            session_rate REAL,
            sessions_remaining INTEGER DEFAULT 0,
            last_session_date TEXT,
            status TEXT DEFAULT 'active',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Payments table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            member_id INTEGER,
            amount REAL NOT NULL,
            payment_date TEXT,
            due_date TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            payment_method TEXT,
            description TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (member_id) REFERENCES members (id)
        )
    ''')
    
    # Messages table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            member_name TEXT NOT NULL,
            member_email TEXT,
            message TEXT NOT NULL,
            response TEXT,
            status TEXT DEFAULT 'unread',
            message_type TEXT DEFAULT 'inquiry',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            responded_at TEXT
        )
    ''')
    
    # Social media accounts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS social_accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            platform TEXT NOT NULL,
            account_name TEXT NOT NULL,
            access_token TEXT,
            followers_count INTEGER DEFAULT 0,
            is_connected BOOLEAN DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Scheduled posts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scheduled_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            platform TEXT NOT NULL,
            content TEXT NOT NULL,
            scheduled_time TEXT NOT NULL,
            status TEXT DEFAULT 'scheduled',
            posted_at TEXT,
            engagement_count INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # System logs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS system_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            level TEXT NOT NULL,
            component TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    
    # Add initial log entry
    log_system_event('INFO', 'Database', 'Database initialized successfully')

def log_system_event(level: str, component: str, message: str):
    """Log system events to database."""
    conn = sqlite3.connect('gym_bot.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO system_logs (level, component, message, timestamp)
        VALUES (?, ?, ?, ?)
    ''', (level, component, message, datetime.now().isoformat()))
    conn.commit()
    conn.close()

# Business Logic Classes
class MemberManager:
    """Manages member operations."""
    
    @staticmethod
    def get_all_members():
        """Get all members from database."""
        conn = sqlite3.connect('gym_bot.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM members ORDER BY name')
        members = cursor.fetchall()
        conn.close()
        return [dict(zip([col[0] for col in cursor.description], member)) for member in members]
    
    @staticmethod
    def add_member(name: str, email: str, phone: str, membership_type: str, monthly_fee: float):
        """Add new member."""
        conn = sqlite3.connect('gym_bot.db')
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO members (name, email, phone, membership_type, monthly_fee, join_date)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (name, email, phone, membership_type, monthly_fee, datetime.now().date().isoformat()))
            conn.commit()
            log_system_event('INFO', 'MemberManager', f'New member added: {name}')
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    @staticmethod
    def get_member_statistics():
        """Get member statistics."""
        conn = sqlite3.connect('gym_bot.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM members WHERE status = "active"')
        active_members = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM prospects WHERE status = "new"')
        new_prospects = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM training_clients WHERE status = "active"')
        training_clients = cursor.fetchone()[0]
        
        cursor.execute('SELECT SUM(monthly_fee) FROM members WHERE status = "active"')
        monthly_revenue = cursor.fetchone()[0] or 0
        
        conn.close()
        return {
            'active_members': active_members,
            'new_prospects': new_prospects,
            'training_clients': training_clients,
            'monthly_revenue': monthly_revenue
        }

class PaymentManager:
    """Manages payment operations."""
    
    @staticmethod
    def get_overdue_payments():
        """Get overdue payments."""
        conn = sqlite3.connect('gym_bot.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT p.*, m.name as member_name
            FROM payments p
            JOIN members m ON p.member_id = m.id
            WHERE p.status = 'pending' AND p.due_date < date('now')
            ORDER BY p.due_date
        ''')
        payments = cursor.fetchall()
        conn.close()
        return [dict(zip([col[0] for col in cursor.description], payment)) for payment in payments]
    
    @staticmethod
    def send_payment_reminders():
        """Send payment reminders to overdue members."""
        overdue = PaymentManager.get_overdue_payments()
        count = 0
        for payment in overdue:
            # Simulate sending reminder
            MessageManager.add_system_message(
                payment['member_name'],
                payment.get('member_email', 'no-email@gym.com'),
                f"Payment reminder: ${payment['amount']} overdue since {payment['due_date']}",
                "payment_reminder"
            )
            count += 1
        
        log_system_event('INFO', 'PaymentManager', f'Sent {count} payment reminders')
        return count
    
    @staticmethod
    def generate_monthly_invoices():
        """Generate monthly invoices for all active members."""
        members = MemberManager.get_all_members()
        count = 0
        
        conn = sqlite3.connect('gym_bot.db')
        cursor = conn.cursor()
        
        for member in members:
            if member['status'] == 'active':
                due_date = (datetime.now() + timedelta(days=30)).date().isoformat()
                cursor.execute('''
                    INSERT INTO payments (member_id, amount, due_date, description)
                    VALUES (?, ?, ?, ?)
                ''', (member['id'], member['monthly_fee'], due_date, f"Monthly membership fee - {datetime.now().strftime('%B %Y')}"))
                count += 1
        
        conn.commit()
        conn.close()
        
        log_system_event('INFO', 'PaymentManager', f'Generated {count} monthly invoices')
        return count

class MessageManager:
    """Manages messaging operations."""
    
    @staticmethod
    def get_unread_messages():
        """Get unread messages."""
        conn = sqlite3.connect('gym_bot.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM messages WHERE status = "unread" ORDER BY created_at DESC')
        messages = cursor.fetchall()
        conn.close()
        return [dict(zip([col[0] for col in cursor.description], message)) for message in messages]
    
    @staticmethod
    def add_system_message(member_name: str, member_email: str, message: str, message_type: str = 'system'):
        """Add system-generated message."""
        conn = sqlite3.connect('gym_bot.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO messages (member_name, member_email, message, message_type, status)
            VALUES (?, ?, ?, ?, 'sent')
        ''', (member_name, member_email, message, message_type))
        conn.commit()
        conn.close()
    
    @staticmethod
    def respond_to_message(message_id: int, response: str):
        """Respond to a message."""
        conn = sqlite3.connect('gym_bot.db')
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE messages 
            SET response = ?, status = 'responded', responded_at = ?
            WHERE id = ?
        ''', (response, datetime.now().isoformat(), message_id))
        conn.commit()
        conn.close()
        
        log_system_event('INFO', 'MessageManager', f'Responded to message ID {message_id}')

class SocialMediaManager:
    """Manages social media operations."""
    
    @staticmethod
    def get_connected_accounts():
        """Get connected social media accounts."""
        conn = sqlite3.connect('gym_bot.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM social_accounts WHERE is_connected = 1')
        accounts = cursor.fetchall()
        conn.close()
        return [dict(zip([col[0] for col in cursor.description], account)) for account in accounts]
    
    @staticmethod
    def add_social_account(platform: str, account_name: str, access_token: str = None):
        """Add social media account."""
        conn = sqlite3.connect('gym_bot.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO social_accounts (platform, account_name, access_token)
            VALUES (?, ?, ?)
        ''', (platform, account_name, access_token or 'demo_token'))
        conn.commit()
        conn.close()
        
        log_system_event('INFO', 'SocialMediaManager', f'Added {platform} account: {account_name}')
    
    @staticmethod
    def schedule_post(platform: str, content: str, scheduled_time: str):
        """Schedule a social media post."""
        conn = sqlite3.connect('gym_bot.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO scheduled_posts (platform, content, scheduled_time)
            VALUES (?, ?, ?)
        ''', (platform, content, scheduled_time))
        conn.commit()
        conn.close()
        
        log_system_event('INFO', 'SocialMediaManager', f'Scheduled {platform} post for {scheduled_time}')

class WorkflowManager:
    """Manages automated workflows."""
    
    @staticmethod
    def send_daily_messages():
        """Send daily promotional/reminder messages via ClubOS."""
        members = MemberManager.get_all_members()
        count = 0
        real_sends = 0
        
        daily_messages = [
            "Don't forget to check in today! Your fitness journey continues",
            "New class schedule available - check out our evening yoga sessions!",
            "Reminder: Stay hydrated during your workout today",
            "Weekend warrior tip: Recovery is just as important as training!"
        ]
        
        # Try to connect to ClubOS if available
        clubos_client = None
        if CLUBOS_AVAILABLE:
            clubos_client = get_clubos_client()
            if not clubos_client.is_connected:
                print("🔗 Attempting to connect to ClubOS...")
                clubos_client.connect()
        
        import random
        for member in members[:5]:  # Send to first 5 members as example
            message = random.choice(daily_messages)
            
            # Try to send via ClubOS first
            if clubos_client and clubos_client.is_connected:
                if clubos_client.send_real_message(member['name'], message):
                    real_sends += 1
                    log_system_event('INFO', 'WorkflowManager', f'Real ClubOS message sent to {member["name"]}')
                else:
                    # Fallback to database storage
                    MessageManager.add_system_message(
                        member['name'],
                        member['email'],
                        message,
                        'daily_reminder'
                    )
            else:
                # Store in database if ClubOS not available
                MessageManager.add_system_message(
                    member['name'],
                    member['email'],
                    message,
                    'daily_reminder'
                )
            count += 1
        
        if real_sends > 0:
            log_system_event('INFO', 'WorkflowManager', f'Sent {real_sends} real ClubOS messages, {count-real_sends} stored locally')
        else:
            log_system_event('INFO', 'WorkflowManager', f'Sent {count} messages (stored locally - ClubOS not available)')
        
        return count
    
    @staticmethod
    def process_overdue_payments():
        """Process overdue payment workflow."""
        reminder_count = PaymentManager.send_payment_reminders()
        log_system_event('INFO', 'WorkflowManager', f'Processed overdue payments workflow - {reminder_count} reminders sent')
        return reminder_count

# Initialize database on startup
init_database()

# ClubOS Integration
try:
    from clubos_integration_fixed import get_clubos_client
    CLUBOS_AVAILABLE = True
    print("✅ ClubOS integration available")
except ImportError:
    CLUBOS_AVAILABLE = False
    print("⚠️ ClubOS integration not available - using local database only")

# Routes
@app.route('/')
def dashboard_home():
    """Main dashboard page."""
    stats = MemberManager.get_member_statistics()
    
    # Get recent system logs
    conn = sqlite3.connect('gym_bot.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM system_logs ORDER BY timestamp DESC LIMIT 10')
    logs = cursor.fetchall()
    conn.close()
    recent_logs = [dict(zip([col[0] for col in cursor.description], log)) for log in logs]
    
    return render_template('dashboard.html', 
                         stats=stats,
                         logs=recent_logs)

@app.route('/workflows')
def workflows_page():
    """Workflows management page."""
    workflows = {
        'send_daily_messages': {
            'name': 'Send Daily Messages',
            'description': 'Send daily promotional and reminder messages to members',
            'status': 'available'
        },
        'process_overdue_payments': {
            'name': 'Process Overdue Payments',
            'description': 'Send payment reminders to members with overdue payments',
            'status': 'available'
        },
        'generate_monthly_invoices': {
            'name': 'Generate Monthly Invoices',
            'description': 'Generate monthly membership invoices for all active members',
            'status': 'available'
        }
    }
    return render_template('workflows.html', workflows=workflows)

@app.route('/members')
def members_page():
    """Members management page."""
    members = MemberManager.get_all_members()
    return render_template('members.html', members=members)

@app.route('/prospects')
def prospects_page():
    """Prospects management page."""
    conn = sqlite3.connect('gym_bot.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM prospects ORDER BY created_at DESC')
    prospects_data = cursor.fetchall()
    conn.close()
    prospects = [dict(zip([col[0] for col in cursor.description], prospect)) for prospect in prospects_data]
    return render_template('prospects.html', prospects=prospects)

@app.route('/training-clients')
def training_clients_page():
    """Training clients management page."""
    conn = sqlite3.connect('gym_bot.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM training_clients ORDER BY name')
    clients_data = cursor.fetchall()
    conn.close()
    clients = [dict(zip([col[0] for col in cursor.description], client)) for client in clients_data]
    return render_template('training_clients.html', clients=clients)

@app.route('/social-media')
def social_media_page():
    """Social Media Management page."""
    accounts = SocialMediaManager.get_connected_accounts()
    
    conn = sqlite3.connect('gym_bot.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM scheduled_posts ORDER BY scheduled_time')
    posts_data = cursor.fetchall()
    conn.close()
    scheduled_posts = [dict(zip([col[0] for col in cursor.description], post)) for post in posts_data]
    
    return render_template('social_media.html', 
                         accounts=accounts, 
                         scheduled_posts=scheduled_posts)

@app.route('/payments')
def payments_page():
    """Payments page."""
    overdue_payments = PaymentManager.get_overdue_payments()
    
    conn = sqlite3.connect('gym_bot.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT p.*, m.name as member_name
        FROM payments p
        JOIN members m ON p.member_id = m.id
        WHERE p.status = 'paid'
        ORDER BY p.payment_date DESC
        LIMIT 10
    ''')
    recent_data = cursor.fetchall()
    conn.close()
    recent_payments = [dict(zip([col[0] for col in cursor.description], payment)) for payment in recent_data]
    
    return render_template('payments.html', 
                         overdue_payments=overdue_payments,
                         recent_payments=recent_payments)

@app.route('/messaging')
def messaging_page():
    """Messaging page."""
    unread_messages = MessageManager.get_unread_messages()
    
    conn = sqlite3.connect('gym_bot.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM messages WHERE status = "responded" ORDER BY responded_at DESC LIMIT 10')
    recent_data = cursor.fetchall()
    conn.close()
    recent_responses = [dict(zip([col[0] for col in cursor.description], message)) for message in recent_data]
    
    return render_template('messaging.html', 
                         unread_messages=unread_messages,
                         recent_responses=recent_responses)

@app.route('/analytics')
def analytics_page():
    """Analytics page."""
    stats = MemberManager.get_member_statistics()
    return render_template('analytics.html', stats=stats)

@app.route('/logs')
def logs_page():
    """System logs page."""
    conn = sqlite3.connect('gym_bot.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM system_logs ORDER BY timestamp DESC LIMIT 50')
    logs_data = cursor.fetchall()
    conn.close()
    logs = [dict(zip([col[0] for col in cursor.description], log)) for log in logs_data]
    return render_template('logs.html', logs=logs)

@app.route('/calendar')
def calendar_page():
    """Calendar page with real ClubOS data."""
    calendar_data = []
    clubos_status = "disconnected"
    
    # Try to get real calendar data from ClubOS
    if CLUBOS_AVAILABLE:
        clubos_client = get_clubos_client()
        if not clubos_client.is_connected:
            clubos_client.connect()
        
        if clubos_client.is_connected:
            clubos_status = "connected"
            calendar_data = clubos_client.get_real_calendar_data()
            log_system_event('INFO', 'Calendar', f'Retrieved {len(calendar_data)} calendar items from ClubOS')
        else:
            log_system_event('WARNING', 'Calendar', 'ClubOS connection failed - using mock data')
    
    # Fallback to mock data if ClubOS not available
    if not calendar_data:
        calendar_data = [
            {'title': 'Morning Yoga', 'time': '7:00 AM', 'instructor': 'Lisa M.', 'spots': 8},
            {'title': 'HIIT Training', 'time': '6:00 PM', 'instructor': 'Mark S.', 'spots': 3},
            {'title': 'Personal Training - John', 'time': '3:00 PM', 'instructor': 'Sarah K.', 'spots': 1}
        ]
    return render_template('calendar.html', 
                         calendar_data=calendar_data,
                         clubos_status=clubos_status)

# API Routes
@app.route('/api/test-clubos', methods=['GET'])
def api_test_clubos():
    """Test ClubOS connection and return status."""
    if not CLUBOS_AVAILABLE:
        return jsonify({
            'success': False, 
            'error': 'ClubOS integration not available',
            'details': 'clubos_integration_fixed.py not found or credentials missing'
        })
    
    try:
        clubos_client = get_clubos_client()
        test_result = clubos_client.test_connection()
        
        return jsonify({
            'success': test_result.get('connected', False),
            'clubos_status': test_result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'details': 'ClubOS connection test failed'
        })

@app.route('/api/run-workflow', methods=['POST'])
def api_run_workflow():
    """API endpoint to run a workflow."""
    workflow_name = request.json.get('workflow')
    
    if workflow_name == 'send_daily_messages':
        count = WorkflowManager.send_daily_messages()
        return jsonify({'success': True, 'message': f'Sent {count} daily messages'})
    elif workflow_name == 'process_overdue_payments':
        count = WorkflowManager.process_overdue_payments()
        return jsonify({'success': True, 'message': f'Sent {count} payment reminders'})
    elif workflow_name == 'generate_monthly_invoices':
        count = PaymentManager.generate_monthly_invoices()
        return jsonify({'success': True, 'message': f'Generated {count} monthly invoices'})
    
    return jsonify({'success': False, 'error': 'Unknown workflow'})

@app.route('/api/members/add', methods=['POST'])
def api_add_member():
    """Add new member."""
    data = request.json
    success = MemberManager.add_member(
        data['name'], 
        data['email'], 
        data['phone'], 
        data['membership_type'], 
        float(data['monthly_fee'])
    )
    return jsonify({'success': success})

@app.route('/api/social-media/add-account', methods=['POST'])
def api_add_social_account():
    """Add social media account."""
    data = request.json
    SocialMediaManager.add_social_account(
        data['platform'], 
        data['account_name'], 
        data.get('access_token')
    )
    return jsonify({'success': True})

@app.route('/api/social-media/schedule-post', methods=['POST'])
def api_schedule_post():
    """Schedule social media post."""
    data = request.json
    SocialMediaManager.schedule_post(
        data['platform'], 
        data['content'], 
        data['scheduled_time']
    )
    return jsonify({'success': True})

@app.route('/api/messages/respond', methods=['POST'])
def api_respond_message():
    """Respond to a message."""
    data = request.json
    MessageManager.respond_to_message(
        data['message_id'], 
        data['response']
    )
    return jsonify({'success': True})

def create_templates():
    """Create HTML templates."""
    templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
    os.makedirs(templates_dir, exist_ok=True)
    
    # Base template
    base_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Gym Bot Dashboard{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        .sidebar {
            position: fixed;
            top: 0;
            left: 0;
            height: 100vh;
            width: 280px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            z-index: 1000;
            overflow-y: auto;
            box-shadow: 4px 0 15px rgba(0,0,0,0.1);
        }
        
        .sidebar-header {
            padding: 1.5rem;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        
        .sidebar-brand {
            font-size: 1.5rem;
            font-weight: 700;
            color: white;
            text-decoration: none;
        }
        
        .nav-link {
            display: flex;
            align-items: center;
            padding: 0.875rem 1rem;
            color: rgba(255,255,255,0.8);
            text-decoration: none;
            border-radius: 0.5rem;
            margin: 0.25rem 1rem;
            transition: all 0.2s;
        }
        
        .nav-link:hover, .nav-link.active {
            background-color: rgba(255,255,255,0.15);
            color: white;
            transform: translateX(4px);
        }
        
        .nav-link i {
            width: 20px;
            margin-right: 0.75rem;
        }
        
        .main-content {
            margin-left: 280px;
            min-height: 100vh;
        }
        
        .top-bar {
            background: white;
            border-bottom: 1px solid #e5e7eb;
            padding: 1rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .content-area {
            padding: 2rem;
        }
        
        .card {
            border: none;
            border-radius: 1rem;
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
            margin-bottom: 1.5rem;
        }
        
        .metric-card {
            text-align: center;
            padding: 1.5rem;
        }
        
        .metric-value {
            font-size: 2.5rem;
            font-weight: 700;
            line-height: 1;
        }
        
        .metric-label {
            color: #6b7280;
            font-size: 0.875rem;
            margin-top: 0.5rem;
        }
        
        .status-indicator {
            display: inline-flex;
            align-items: center;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.875rem;
            font-weight: 500;
        }
        
        .status-healthy {
            background-color: #dcfce7;
            color: #166534;
        }
        
        .btn-primary {
            background: #6366f1;
            border-color: #6366f1;
            border-radius: 0.5rem;
            font-weight: 600;
        }
    </style>
</head>
<body>
    <nav class="sidebar">
        <div class="sidebar-header">
            <a href="{{ url_for('dashboard_home') }}" class="sidebar-brand">
                <i class="fas fa-dumbbell me-2"></i>Gym Bot Pro
            </a>
        </div>
        <ul class="sidebar-nav">
            <li><a class="nav-link" href="{{ url_for('dashboard_home') }}"><i class="fas fa-chart-line"></i>Dashboard</a></li>
            <li><a class="nav-link" href="{{ url_for('workflows_page') }}"><i class="fas fa-cogs"></i>Bot Controls</a></li>
            <li><a class="nav-link" href="{{ url_for('members_page') }}"><i class="fas fa-users"></i>Members</a></li>
            <li><a class="nav-link" href="{{ url_for('prospects_page') }}"><i class="fas fa-user-plus"></i>Prospects</a></li>
            <li><a class="nav-link" href="{{ url_for('training_clients_page') }}"><i class="fas fa-dumbbell"></i>Training</a></li>
            <li><a class="nav-link" href="{{ url_for('social_media_page') }}"><i class="fab fa-instagram"></i>Social Media</a></li>
            <li><a class="nav-link" href="{{ url_for('payments_page') }}"><i class="fas fa-credit-card"></i>Payments</a></li>
            <li><a class="nav-link" href="{{ url_for('messaging_page') }}"><i class="fas fa-comments"></i>Messaging</a></li>
            <li><a class="nav-link" href="{{ url_for('analytics_page') }}"><i class="fas fa-chart-bar"></i>Analytics</a></li>
            <li><a class="nav-link" href="{{ url_for('logs_page') }}"><i class="fas fa-file-alt"></i>Logs</a></li>
            <li><a class="nav-link" href="{{ url_for('calendar_page') }}"><i class="fas fa-calendar-alt"></i>Calendar</a></li>
        </ul>
    </nav>

    <div class="main-content">
        <div class="top-bar">
            <h4 class="mb-0">{% block page_title %}{% endblock %}</h4>
            <span class="status-indicator status-healthy">
                <i class="fas fa-circle me-1"></i>System Online
            </span>
        </div>

        <div class="content-area">
            {% block content %}{% endblock %}
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

{% block content %}
<div class="row mb-4">
    <div class="col-md-3">
        <div class="card metric-card">
            <div class="metric-value text-primary">{{ stats.active_members }}</div>
            <div class="metric-label">Active Members</div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card metric-card">
            <div class="metric-value text-success">${{ "%.0f"|format(stats.monthly_revenue) }}</div>
            <div class="metric-label">Monthly Revenue</div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card metric-card">
            <div class="metric-value text-info">{{ stats.new_prospects }}</div>
            <div class="metric-label">New Prospects</div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card metric-card">
            <div class="metric-value text-warning">{{ stats.training_clients }}</div>
            <div class="metric-label">Training Clients</div>
        </div>
    </div>
</div>

<div class="row">
    <div class="col-lg-8">
        <div class="card">
            <div class="card-header">
                <h5><i class="fas fa-list me-2"></i>Recent System Activity</h5>
            </div>
            <div class="card-body">
                {% for log in logs %}
                <div class="d-flex justify-content-between mb-2">
                    <div>
                        <span class="badge bg-info">{{ log.level }}</span>
                        {{ log.message }}
                    </div>
                    <small class="text-muted">{{ log.component }} - {{ log.timestamp[:19] }}</small>
                </div>
                {% endfor %}
            </div>
        </div>
    </div>
    
    <div class="col-lg-4">
        <div class="card">
            <div class="card-header">
                <h5><i class="fas fa-bolt me-2"></i>Quick Actions</h5>
            </div>
            <div class="card-body">
                <div class="d-grid gap-2">
                    <a href="{{ url_for('workflows_page') }}" class="btn btn-outline-primary">
                        <i class="fas fa-play me-2"></i>Run Workflow
                    </a>
                    <a href="{{ url_for('social_media_page') }}" class="btn btn-outline-success">
                        <i class="fab fa-instagram me-2"></i>Schedule Social Post
                    </a>
                    <a href="{{ url_for('members_page') }}" class="btn btn-outline-info">
                        <i class="fas fa-user-plus me-2"></i>Add Member
                    </a>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}'''

    # Workflows template
    workflows_template = '''{% extends "base.html" %}
{% block title %}Workflows - Gym Bot Pro{% endblock %}
{% block page_title %}Bot Controls{% endblock %}

{% block content %}
<div class="row">
    {% for workflow_id, workflow in workflows.items() %}
    <div class="col-md-6 mb-4">
        <div class="card">
            <div class="card-header">
                <h5>{{ workflow.name }}</h5>
            </div>
            <div class="card-body">
                <p>{{ workflow.description }}</p>
                <button class="btn btn-primary" onclick="runWorkflow('{{ workflow_id }}')">
                    <i class="fas fa-play me-1"></i> Run Workflow
                </button>
            </div>
        </div>
    </div>
    {% endfor %}
</div>

<script>
function runWorkflow(workflowId) {
    fetch('/api/run-workflow', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({workflow: workflowId})
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(data.message);
            location.reload();
        } else {
            alert('Error: ' + data.error);
        }
    });
}
</script>
{% endblock %}'''

    # Members template
    members_template = '''{% extends "base.html" %}
{% block title %}Members{% endblock %}
{% block page_title %}Member Management{% endblock %}

{% block content %}
<div class="row mb-3">
    <div class="col-12">
        <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#addMemberModal">
            <i class="fas fa-plus me-1"></i> Add Member
        </button>
    </div>
</div>

<div class="card">
    <div class="card-header">
        <h5>All Members</h5>
    </div>
    <div class="card-body">
        <div class="table-responsive">
            <table class="table">
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Email</th>
                        <th>Membership Type</th>
                        <th>Monthly Fee</th>
                        <th>Status</th>
                        <th>Join Date</th>
                    </tr>
                </thead>
                <tbody>
                    {% for member in members %}
                    <tr>
                        <td>{{ member.name }}</td>
                        <td>{{ member.email }}</td>
                        <td>{{ member.membership_type }}</td>
                        <td>${{ member.monthly_fee }}</td>
                        <td><span class="badge bg-success">{{ member.status }}</span></td>
                        <td>{{ member.join_date }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</div>

<!-- Add Member Modal -->
<div class="modal fade" id="addMemberModal" tabindex="-1">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">Add New Member</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                <form id="addMemberForm">
                    <div class="mb-3">
                        <label class="form-label">Name</label>
                        <input type="text" class="form-control" name="name" required>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Email</label>
                        <input type="email" class="form-control" name="email" required>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Phone</label>
                        <input type="text" class="form-control" name="phone">
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Membership Type</label>
                        <select class="form-control" name="membership_type" required>
                            <option value="Basic">Basic</option>
                            <option value="Premium">Premium</option>
                            <option value="VIP">VIP</option>
                        </select>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Monthly Fee</label>
                        <input type="number" class="form-control" name="monthly_fee" step="0.01" required>
                    </div>
                </form>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                <button type="button" class="btn btn-primary" onclick="addMember()">Add Member</button>
            </div>
        </div>
    </div>
</div>

<script>
function addMember() {
    const form = document.getElementById('addMemberForm');
    const formData = new FormData(form);
    const data = Object.fromEntries(formData);
    
    fetch('/api/members/add', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Member added successfully!');
            location.reload();
        } else {
            alert('Error adding member');
        }
    });
}
</script>
{% endblock %}'''

    # Social Media template
    social_media_template = '''{% extends "base.html" %}
{% block title %}Social Media{% endblock %}
{% block page_title %}Social Media Management{% endblock %}

{% block content %}
<div class="row mb-3">
    <div class="col-12">
        <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#addAccountModal">
            <i class="fas fa-plus me-1"></i> Connect Account
        </button>
        <button class="btn btn-success" data-bs-toggle="modal" data-bs-target="#schedulePostModal">
            <i class="fas fa-calendar me-1"></i> Schedule Post
        </button>
    </div>
</div>

<div class="row">
    <div class="col-md-6">
        <div class="card">
            <div class="card-header"><h5>Connected Accounts</h5></div>
            <div class="card-body">
                {% if accounts %}
                    {% for account in accounts %}
                    <div class="d-flex justify-content-between mb-2">
                        <span><i class="fab fa-{{ account.platform }}"></i> {{ account.account_name }}</span>
                        <span class="badge bg-success">Connected</span>
                    </div>
                    {% endfor %}
                {% else %}
                    <p class="text-muted">No social media accounts connected yet.</p>
                {% endif %}
            </div>
        </div>
    </div>
    <div class="col-md-6">
        <div class="card">
            <div class="card-header"><h5>Scheduled Posts</h5></div>
            <div class="card-body">
                {% if scheduled_posts %}
                    {% for post in scheduled_posts %}
                    <div class="border rounded p-2 mb-2">
                        <strong>{{ post.platform.title() }}</strong><br>
                        <small>{{ post.content[:50] }}...</small><br>
                        <small class="text-muted">{{ post.scheduled_time }}</small>
                    </div>
                    {% endfor %}
                {% else %}
                    <p class="text-muted">No posts scheduled yet.</p>
                {% endif %}
            </div>
        </div>
    </div>
</div>

<!-- Add Account Modal -->
<div class="modal fade" id="addAccountModal" tabindex="-1">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">Connect Social Media Account</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                <form id="addAccountForm">
                    <div class="mb-3">
                        <label class="form-label">Platform</label>
                        <select class="form-control" name="platform" required>
                            <option value="instagram">Instagram</option>
                            <option value="facebook">Facebook</option>
                            <option value="twitter">Twitter</option>
                            <option value="linkedin">LinkedIn</option>
                        </select>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Account Name</label>
                        <input type="text" class="form-control" name="account_name" required>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Access Token (Optional)</label>
                        <input type="text" class="form-control" name="access_token">
                    </div>
                </form>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                <button type="button" class="btn btn-primary" onclick="addAccount()">Connect Account</button>
            </div>
        </div>
    </div>
</div>

<!-- Schedule Post Modal -->
<div class="modal fade" id="schedulePostModal" tabindex="-1">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">Schedule Social Media Post</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                <form id="schedulePostForm">
                    <div class="mb-3">
                        <label class="form-label">Platform</label>
                        <select class="form-control" name="platform" required>
                            {% for account in accounts %}
                            <option value="{{ account.platform }}">{{ account.platform.title() }} - {{ account.account_name }}</option>
                            {% endfor %}
                        </select>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Content</label>
                        <textarea class="form-control" name="content" rows="4" required></textarea>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Scheduled Time</label>
                        <input type="datetime-local" class="form-control" name="scheduled_time" required>
                    </div>
                </form>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                <button type="button" class="btn btn-primary" onclick="schedulePost()">Schedule Post</button>
            </div>
        </div>
    </div>
</div>

<script>
function addAccount() {
    const form = document.getElementById('addAccountForm');
    const formData = new FormData(form);
    const data = Object.fromEntries(formData);
    
    fetch('/api/social-media/add-account', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Account connected successfully!');
            location.reload();
        } else {
            alert('Error connecting account');
        }
    });
}

function schedulePost() {
    const form = document.getElementById('schedulePostForm');
    const formData = new FormData(form);
    const data = Object.fromEntries(formData);
    
    fetch('/api/social-media/schedule-post', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Post scheduled successfully!');
            location.reload();
        } else {
            alert('Error scheduling post');
        }
    });
}
</script>
{% endblock %}'''

    # Simple templates for other pages
    templates = {
        'base.html': base_template,
        'dashboard.html': dashboard_template,
        'workflows.html': workflows_template,
        'members.html': members_template,
        'social_media.html': social_media_template,
        'prospects.html': '''{% extends "base.html" %}
{% block title %}Prospects{% endblock %}
{% block page_title %}Prospect Management{% endblock %}
{% block content %}
<div class="card">
    <div class="card-header"><h5>All Prospects</h5></div>
    <div class="card-body">
        {% if prospects %}
            <div class="table-responsive">
                <table class="table">
                    <thead>
                        <tr><th>Name</th><th>Email</th><th>Phone</th><th>Interest Level</th><th>Source</th><th>Status</th></tr>
                    </thead>
                    <tbody>
                        {% for prospect in prospects %}
                        <tr>
                            <td>{{ prospect.name }}</td>
                            <td>{{ prospect.email or 'N/A' }}</td>
                            <td>{{ prospect.phone or 'N/A' }}</td>
                            <td>{{ prospect.interest_level or 'N/A' }}</td>
                            <td>{{ prospect.source or 'N/A' }}</td>
                            <td><span class="badge bg-primary">{{ prospect.status }}</span></td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        {% else %}
            <p class="text-muted">No prospects found.</p>
        {% endif %}
    </div>
</div>
{% endblock %}''',
        'training_clients.html': '''{% extends "base.html" %}
{% block title %}Training Clients{% endblock %}
{% block page_title %}Training Client Management{% endblock %}
{% block content %}
<div class="card">
    <div class="card-header"><h5>All Training Clients</h5></div>
    <div class="card-body">
        {% if clients %}
            <div class="table-responsive">
                <table class="table">
                    <thead>
                        <tr><th>Name</th><th>Email</th><th>Trainer</th><th>Session Rate</th><th>Sessions Remaining</th><th>Status</th></tr>
                    </thead>
                    <tbody>
                        {% for client in clients %}
                        <tr>
                            <td>{{ client.name }}</td>
                            <td>{{ client.email or 'N/A' }}</td>
                            <td>{{ client.trainer_name or 'N/A' }}</td>
                            <td>${{ client.session_rate or 'N/A' }}</td>
                            <td>{{ client.sessions_remaining }}</td>
                            <td><span class="badge bg-success">{{ client.status }}</span></td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        {% else %}
            <p class="text-muted">No training clients found.</p>
        {% endif %}
    </div>
</div>
{% endblock %}''',
        'payments.html': '''{% extends "base.html" %}
{% block title %}Payments{% endblock %}
{% block page_title %}Payment Management{% endblock %}
{% block content %}
<div class="row">
    <div class="col-md-6">
        <div class="card">
            <div class="card-header"><h5>Overdue Payments</h5></div>
            <div class="card-body">
                {% if overdue_payments %}
                    {% for payment in overdue_payments %}
                    <div class="d-flex justify-content-between mb-2">
                        <span>{{ payment.member_name }}</span>
                        <span class="text-danger">${{ payment.amount }} (Due: {{ payment.due_date }})</span>
                    </div>
                    {% endfor %}
                {% else %}
                    <p class="text-success">No overdue payments!</p>
                {% endif %}
            </div>
        </div>
    </div>
    <div class="col-md-6">
        <div class="card">
            <div class="card-header"><h5>Recent Payments</h5></div>
            <div class="card-body">
                {% if recent_payments %}
                    {% for payment in recent_payments %}
                    <div class="d-flex justify-content-between mb-2">
                        <span>{{ payment.member_name }}</span>
                        <span class="text-success">${{ payment.amount }}</span>
                    </div>
                    {% endfor %}
                {% else %}
                    <p class="text-muted">No recent payments found.</p>
                {% endif %}
            </div>
        </div>
    </div>
</div>
{% endblock %}''',
        'messaging.html': '''{% extends "base.html" %}
{% block title %}Messaging{% endblock %}
{% block page_title %}Member Messaging{% endblock %}
{% block content %}
<div class="row">
    <div class="col-md-6">
        <div class="card">
            <div class="card-header"><h5>Unread Messages</h5></div>
            <div class="card-body">
                {% if unread_messages %}
                    {% for message in unread_messages %}
                    <div class="border rounded p-2 mb-2">
                        <strong>{{ message.member_name }}</strong><br>
                        <small>{{ message.message }}</small><br>
                        <small class="text-muted">{{ message.created_at[:19] }}</small>
                        <button class="btn btn-sm btn-primary mt-1" onclick="respondToMessage({{ message.id }})">Respond</button>
                    </div>
                    {% endfor %}
                {% else %}
                    <p class="text-success">No pending messages!</p>
                {% endif %}
            </div>
        </div>
    </div>
    <div class="col-md-6">
        <div class="card">
            <div class="card-header"><h5>Recent AI Responses</h5></div>
            <div class="card-body">
                {% if recent_responses %}
                    {% for response in recent_responses %}
                    <div class="border rounded p-2 mb-2">
                        <strong>{{ response.member_name }}</strong><br>
                        <small>{{ response.response }}</small><br>
                        <small class="text-muted">{{ response.responded_at[:19] }}</small>
                    </div>
                    {% endfor %}
                {% else %}
                    <p class="text-muted">No recent responses found.</p>
                {% endif %}
            </div>
        </div>
    </div>
</div>

<script>
function respondToMessage(messageId) {
    const response = prompt('Enter your response:');
    if (response) {
        fetch('/api/messages/respond', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({message_id: messageId, response: response})
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Response sent!');
                location.reload();
            } else {
                alert('Error sending response');
            }
        });
    }
}
</script>
{% endblock %}''',
        'analytics.html': '''{% extends "base.html" %}
{% block title %}Analytics{% endblock %}
{% block page_title %}Analytics & Business Insights{% endblock %}
{% block content %}
<div class="row mb-4">
    <div class="col-md-3">
        <div class="card metric-card">
            <div class="metric-value text-primary">{{ stats.active_members }}</div>
            <div class="metric-label">Active Members</div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card metric-card">
            <div class="metric-value text-success">${{ "%.0f"|format(stats.monthly_revenue) }}</div>
            <div class="metric-label">Monthly Revenue</div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card metric-card">
            <div class="metric-value text-info">{{ stats.new_prospects }}</div>
            <div class="metric-label">New Prospects</div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card metric-card">
            <div class="metric-value text-warning">{{ stats.training_clients }}</div>
            <div class="metric-label">Training Clients</div>
        </div>
    </div>
</div>
<div class="card">
    <div class="card-header"><h5>Analytics Summary</h5></div>
    <div class="card-body">
        <p>Detailed analytics and business insights will be displayed here.</p>
    </div>
</div>
{% endblock %}''',
        'logs.html': '''{% extends "base.html" %}
{% block title %}Logs{% endblock %}
{% block page_title %}System Logs{% endblock %}
{% block content %}
<div class="card">
    <div class="card-header"><h5>Recent Activity</h5></div>
    <div class="card-body">
        {% for log in logs %}
        <div class="d-flex justify-content-between mb-2">
            <div>
                <span class="badge bg-info">{{ log.level }}</span>
                {{ log.message }}
            </div>
            <small class="text-muted">{{ log.component }} - {{ log.timestamp[:19] }}</small>
        </div>
        {% endfor %}
    </div>
</div>
{% endblock %}''',
        'calendar.html': '''{% extends "base.html" %}
{% block title %}Calendar{% endblock %}
{% block page_title %}ClubOS Calendar Integration{% endblock %}
{% block content %}
<div class="card">
    <div class="card-header">
        <h5>Upcoming Events</h5>
        <span class="badge bg-secondary">{{ clubos_status }}</span>
    </div>
    <div class="card-body">
        {% if calendar_data %}
            <div class="table-responsive">
                <table class="table">
                    <thead>
                        <tr><th>Title</th><th>Time</th><th>Instructor</th><th>Spots Available</th></tr>
                    </thead>
                    <tbody>
                        {% for event in calendar_data %}
                        <tr>
                            <td>{{ event.title }}</td>
                            <td>{{ event.time }}</td>
                            <td>{{ event.instructor }}</td>
                            <td>{{ event.spots }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        {% else %}
            <p class="text-muted">No upcoming events found.</p>
        {% endif %}
    </div>
</div>
{% endblock %}'''
    }
    
    for filename, content in templates.items():
        filepath = os.path.join(templates_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

if __name__ == '__main__':
    create_templates()
    print("Dashboard starting at http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
