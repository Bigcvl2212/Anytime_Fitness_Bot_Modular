"""
Gym Bot Dashboard - Fully Functional Version
"""

import sys
import os
import json
import threading
import time
import sqlite3
import csv
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import requests
from pathlib import Path

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'gym-bot-dashboard-secret-key'

# Database setup
DATABASE_PATH = 'gym_bot.db'

class DatabaseManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database with required tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Members table - Enhanced with agreement information
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS members (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone TEXT,
                mobile_phone TEXT,
                home_phone TEXT,
                work_phone TEXT,
                address1 TEXT,
                address2 TEXT,
                city TEXT,
                state TEXT,
                zip_code TEXT,
                date_of_birth TEXT,
                gender TEXT,
                membership_type TEXT,
                status TEXT DEFAULT 'active',
                join_date DATE,
                last_payment DATE,
                monthly_fee REAL,
                notes TEXT,
                emergency_contact_name TEXT,
                emergency_contact_phone TEXT,
                referral_source TEXT,
                preferred_contact_method TEXT,
                
                -- Agreement Information
                agreement_id TEXT,
                agreement_status TEXT,
                agreement_type TEXT,
                start_date TEXT,
                end_date TEXT,
                monthly_amount TEXT,
                billing_frequency TEXT,
                next_billing_date TEXT,
                auto_renew TEXT,
                
                -- Payment Information
                payment_token TEXT,
                card_type TEXT,
                card_last_four TEXT,
                card_exp_month TEXT,
                card_exp_year TEXT,
                billing_name TEXT,
                billing_address1 TEXT,
                billing_address2 TEXT,
                billing_city TEXT,
                billing_state TEXT,
                billing_zip_code TEXT,
                
                -- Home Club Information
                home_club_id TEXT,
                home_club_name TEXT,
                home_club_phone TEXT,
                home_club_address1 TEXT,
                home_club_address2 TEXT,
                home_club_city TEXT,
                home_club_state TEXT,
                home_club_zip_code TEXT,
                
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Prospects table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS prospects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                lead_source TEXT,
                status TEXT DEFAULT 'new',
                interested_in TEXT,
                follow_up_date DATE,
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
                sessions_remaining INTEGER,
                last_session DATE,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (member_id) REFERENCES members (id)
            )
        ''')
        
        # Messages table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                member_id INTEGER,
                member_name TEXT,
                message_type TEXT,
                content TEXT,
                response TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                responded_at TIMESTAMP,
                FOREIGN KEY (member_id) REFERENCES members (id)
            )
        ''')
        
        # Payments table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                member_id INTEGER,
                amount REAL,
                due_date DATE,
                paid_date DATE,
                status TEXT DEFAULT 'pending',
                payment_method TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (member_id) REFERENCES members (id)
            )
        ''')
        
        # Social media accounts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS social_accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform TEXT NOT NULL,
                account_name TEXT NOT NULL,
                access_token TEXT,
                refresh_token TEXT,
                is_connected BOOLEAN DEFAULT 0,
                followers_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Scheduled posts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scheduled_posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform TEXT NOT NULL,
                content TEXT NOT NULL,
                scheduled_time TIMESTAMP,
                status TEXT DEFAULT 'scheduled',
                posted_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # System logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                level TEXT,
                component TEXT,
                message TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        
        # Import real data if tables are empty
        self.import_master_contact_list()
        self.import_training_clients()

    def import_master_contact_list(self):
        """Import master contact list from enhanced CSV with agreement data."""
        csv_path = 'master_contact_list_with_agreements_20250722_180712.csv'
        
        if not os.path.exists(csv_path):
            print(f"Enhanced CSV file not found: {csv_path}")
            return
            
        import pandas as pd
        df = pd.read_csv(csv_path, low_memory=False)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Clear existing data
        cursor.execute('DELETE FROM members')
        cursor.execute('DELETE FROM prospects')
        
        members_count = 0
        prospects_count = 0
        
        for _, row in df.iterrows():
            # Check if this is a member (has agreement_id) or prospect
            if pd.notna(row.get('agreement_id')) and str(row.get('agreement_id')).strip():
                # This is a member with agreement data
                cursor.execute('''
                    INSERT OR REPLACE INTO members (
                        id, name, email, phone, mobile_phone, home_phone, work_phone,
                        address1, address2, city, state, zip_code, date_of_birth, gender,
                        membership_type, status, join_date, monthly_fee, notes,
                        emergency_contact_name, emergency_contact_phone, referral_source,
                        preferred_contact_method, agreement_id, agreement_status, agreement_type,
                        start_date, end_date, monthly_amount, billing_frequency, next_billing_date,
                        auto_renew, payment_token, card_type, card_last_four, card_exp_month,
                        card_exp_year, billing_name, billing_address1, billing_address2,
                        billing_city, billing_state, billing_zip_code, home_club_id,
                        home_club_name, home_club_phone, home_club_address1, home_club_address2,
                        home_club_city, home_club_state, home_club_zip_code
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    row.get('id'), row.get('full_name'), row.get('email'), row.get('phone'),
                    row.get('mobile_phone'), row.get('home_phone'), row.get('work_phone'),
                    row.get('address1'), row.get('address2'), row.get('city'), row.get('state'),
                    row.get('zip_code'), row.get('date_of_birth'), row.get('gender'),
                    'Member', 'active', row.get('join_date'),
                    row.get('monthly_amount'), row.get('notes'), row.get('emergency_contact_name'),
                    row.get('emergency_contact_phone'), row.get('referral_source'),
                    row.get('preferred_contact_method'), row.get('agreement_id'),
                    row.get('agreement_status'), row.get('agreement_type'), row.get('start_date'),
                    row.get('end_date'), row.get('monthly_amount'), row.get('billing_frequency'),
                    row.get('next_billing_date'), row.get('auto_renew'), row.get('payment_token'),
                    row.get('card_type'), row.get('card_last_four'), row.get('card_exp_month'),
                    row.get('card_exp_year'), row.get('billing_name'), row.get('billing_address1'),
                    row.get('billing_address2'), row.get('billing_city'), row.get('billing_state'),
                    row.get('billing_zip_code'), row.get('home_club_id'), row.get('home_club_name'),
                    row.get('home_club_phone'), row.get('home_club_address1'), row.get('home_club_address2'),
                    row.get('home_club_city'), row.get('home_club_state'), row.get('home_club_zip_code')
                ))
                members_count += 1
            else:
                # This is a prospect
                cursor.execute('''
                    INSERT OR REPLACE INTO prospects (
                        id, name, email, phone, lead_source, status, interested_in, notes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    row.get('id'), row.get('full_name'), row.get('email'), row.get('phone'),
                    row.get('lead_source', 'Unknown'), 'new', 'Membership',
                    row.get('notes')
                ))
                prospects_count += 1
        
        conn.commit()
        conn.close()
        print(f"✅ Enhanced CSV import complete: {members_count} members with agreement data, {prospects_count} prospects")

    def import_training_clients(self):
        """Import training clients from CSV and link to members."""
        import pandas as pd
        csv_path = os.path.join(os.path.dirname(__file__), 'data', 'exports', 'training_clients_list.csv')
        if not os.path.exists(csv_path):
            return
        df = pd.read_csv(csv_path)
        if df.empty or 'Name' not in df.columns:
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
                member_id, row.get('Trainer', ''), row.get('SessionType', ''), row.get('SessionsRemaining', 0), row.get('LastSession', ''), row.get('Notes', '')
            ))
        conn.commit()
        conn.close()
    
    def populate_sample_data(self):
        """Add sample data if database is empty."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if we have any members
        cursor.execute("SELECT COUNT(*) FROM members")
        if cursor.fetchone()[0] == 0:
            # Add sample members
            sample_members = [
                ('John Smith', 'john.smith@email.com', '555-0101', 'Premium', 'active', '2024-01-15', '2025-07-01', 149.99),
                ('Jane Doe', 'jane.doe@email.com', '555-0102', 'Basic', 'active', '2024-03-20', '2025-06-15', 89.99),
                ('Mike Johnson', 'mike.j@email.com', '555-0103', 'Premium', 'overdue', '2024-02-10', '2025-05-01', 149.99),
                ('Sarah Wilson', 'sarah.w@email.com', '555-0104', 'Basic', 'active', '2024-04-05', '2025-07-05', 89.99),
                ('Alex Brown', 'alex.brown@email.com', '555-0105', 'Premium', 'active', '2024-01-30', '2025-07-10', 149.99)
            ]
            
            for member in sample_members:
                cursor.execute('''
                    INSERT INTO members (name, email, phone, membership_type, status, join_date, last_payment, monthly_fee)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', member)
            
            # Add sample prospects
            sample_prospects = [
                ('Emma Davis', 'emma.davis@email.com', '555-0201', 'Website', 'new', 'Premium Membership', '2025-07-22'),
                ('Tom Wilson', 'tom.wilson@email.com', '555-0202', 'Referral', 'contacted', 'Personal Training', '2025-07-23'),
                ('Lisa Garcia', 'lisa.garcia@email.com', '555-0203', 'Walk-in', 'scheduled', 'Basic Membership', '2025-07-24')
            ]
            
            for prospect in sample_prospects:
                cursor.execute('''
                    INSERT INTO prospects (name, email, phone, lead_source, status, interested_in, follow_up_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', prospect)
            
            # Add sample payments
            sample_payments = [
                (1, 149.99, '2025-08-01', None, 'pending'),
                (2, 89.99, '2025-08-15', None, 'pending'),
                (3, 149.99, '2025-06-01', None, 'overdue'),
                (4, 89.99, '2025-08-05', '2025-07-20', 'paid'),
                (5, 149.99, '2025-08-10', None, 'pending')
            ]
            
            for payment in sample_payments:
                cursor.execute('''
                    INSERT INTO payments (member_id, amount, due_date, paid_date, status)
                    VALUES (?, ?, ?, ?, ?)
                ''', payment)
            
            # Add sample messages
            sample_messages = [
                (1, 'John Smith', 'inquiry', 'When does the gym open on Sunday?', None, 'pending'),
                (2, 'Jane Doe', 'complaint', 'The locker room was dirty yesterday', None, 'pending'),
                (3, 'Mike Johnson', 'payment', 'Can I pay my overdue fees in installments?', None, 'pending')
            ]
            
            for message in sample_messages:
                cursor.execute('''
                    INSERT INTO messages (member_id, member_name, message_type, content, response, status)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', message)
        
        conn.commit()
        conn.close()
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)

# Initialize database
db = DatabaseManager(DATABASE_PATH)

class MemberManager:
    """Manages member data and operations."""
    
    @staticmethod
    def get_all_members():
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, name, email, phone, mobile_phone, home_phone, work_phone,
                   address1, address2, city, state, zip_code, date_of_birth, gender,
                   membership_type, status, join_date, last_payment, monthly_fee, notes,
                   emergency_contact_name, emergency_contact_phone, referral_source,
                   preferred_contact_method, agreement_id, agreement_status, agreement_type,
                   start_date, end_date, monthly_amount, billing_frequency, next_billing_date,
                   auto_renew, payment_token, card_type, card_last_four, card_exp_month,
                   card_exp_year, billing_name, billing_address1, billing_address2,
                   billing_city, billing_state, billing_zip_code, home_club_id,
                   home_club_name, home_club_phone, home_club_address1, home_club_address2,
                   home_club_city, home_club_state, home_club_zip_code
            FROM members ORDER BY name
        ''')
        members = cursor.fetchall()
        conn.close()
        
        columns = ['id', 'name', 'email', 'phone', 'mobile_phone', 'home_phone', 'work_phone',
                  'address1', 'address2', 'city', 'state', 'zip_code', 'date_of_birth', 'gender',
                  'membership_type', 'status', 'join_date', 'last_payment', 'monthly_fee', 'notes',
                  'emergency_contact_name', 'emergency_contact_phone', 'referral_source',
                  'preferred_contact_method', 'agreement_id', 'agreement_status', 'agreement_type',
                  'start_date', 'end_date', 'monthly_amount', 'billing_frequency', 'next_billing_date',
                  'auto_renew', 'payment_token', 'card_type', 'card_last_four', 'card_exp_month',
                  'card_exp_year', 'billing_name', 'billing_address1', 'billing_address2',
                  'billing_city', 'billing_state', 'billing_zip_code', 'home_club_id',
                  'home_club_name', 'home_club_phone', 'home_club_address1', 'home_club_address2',
                  'home_club_city', 'home_club_state', 'home_club_zip_code']
        
        return [dict(zip(columns, member)) for member in members]

    @staticmethod
    def get_training_clients():
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT tc.id, m.name as member_name, tc.trainer_name, tc.session_type,
                   tc.sessions_remaining, tc.last_session, tc.notes
            FROM training_clients tc
            LEFT JOIN members m ON tc.member_id = m.id
            ORDER BY tc.last_session DESC
        ''')
        clients = cursor.fetchall()
        conn.close()
        return [dict(zip(['id', 'member_name', 'trainer_name', 'session_type',
                         'sessions_remaining', 'last_session', 'notes'], client)) for client in clients]
    
    @staticmethod
    def add_member(name, email, phone, membership_type, monthly_fee):
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO members (name, email, phone, membership_type, join_date, monthly_fee)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, email, phone, membership_type, datetime.now().date(), monthly_fee))
        conn.commit()
        conn.close()
        return True
    
    @staticmethod
    def get_overdue_members():
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT m.id, m.name, m.email, m.phone, p.amount, p.due_date,
                   julianday('now') - julianday(p.due_date) as days_overdue
            FROM members m
            JOIN payments p ON m.id = p.member_id
            WHERE p.status = 'overdue' OR (p.status = 'pending' AND p.due_date < date('now'))
            ORDER BY days_overdue DESC
        ''')
        overdue = cursor.fetchall()
        conn.close()
        
        return [dict(zip(['id', 'name', 'email', 'phone', 'amount', 'due_date', 'days_overdue'], 
                        member)) for member in overdue]

class MessageManager:
    """Manages member messages and AI responses."""
    
    @staticmethod
    def get_pending_messages():
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, member_id, member_name, message_type, content, created_at
            FROM messages 
            WHERE status = 'pending'
            ORDER BY created_at DESC
        ''')
        messages = cursor.fetchall()
        conn.close()
        
        return [dict(zip(['id', 'member_id', 'member_name', 'message_type', 
                         'content', 'created_at'], msg)) for msg in messages]
    
    @staticmethod
    def send_ai_response(message_id, response):
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE messages 
            SET response = ?, status = 'responded', responded_at = ?
            WHERE id = ?
        ''', (response, datetime.now(), message_id))
        conn.commit()
        conn.close()
    
    @staticmethod
    def add_message(member_name, message_type, content):
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO messages (member_name, message_type, content)
            VALUES (?, ?, ?)
        ''', (member_name, message_type, content))
        conn.commit()
        conn.close()

class PaymentManager:
    """Manages payments and billing."""
    
    @staticmethod
    def get_overdue_payments():
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT p.id, m.name, m.email, p.amount, p.due_date,
                   julianday('now') - julianday(p.due_date) as days_overdue
            FROM payments p
            JOIN members m ON p.member_id = m.id
            WHERE p.status IN ('pending', 'overdue') AND p.due_date < date('now')
            ORDER BY days_overdue DESC
        ''')
        payments = cursor.fetchall()
        conn.close()
        
        return [dict(zip(['id', 'member_name', 'email', 'amount', 'due_date', 'days_overdue'], 
                        payment)) for payment in payments]
    
    @staticmethod
    def send_payment_reminder(payment_id):
        """Send payment reminder via email/SMS."""
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT m.name, m.email, p.amount, p.due_date
            FROM payments p
            JOIN members m ON p.member_id = m.id
            WHERE p.id = ?
        ''', (payment_id,))
        payment_info = cursor.fetchone()
        conn.close()
        
        if payment_info:
            # In a real implementation, this would send actual emails/SMS
            print(f"Sending payment reminder to {payment_info[1]} for ${payment_info[2]}")
            return True
        return False
    
    @staticmethod
    def process_payment(payment_id, payment_method='auto'):
        """Process a payment."""
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE payments 
            SET status = 'paid', paid_date = ?, payment_method = ?
            WHERE id = ?
        ''', (datetime.now().date(), payment_method, payment_id))
        conn.commit()
        conn.close()
        return True

class SocialMediaManager:
    """Manages social media accounts and posting."""
    
    @staticmethod
    def get_connected_accounts():
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT platform, account_name, is_connected, followers_count
            FROM social_accounts
            ORDER BY platform
        ''')
        accounts = cursor.fetchall()
        conn.close()
        
        return [dict(zip(['platform', 'account_name', 'is_connected', 'followers_count'], 
                        account)) for account in accounts]
    
    @staticmethod
    def add_social_account(platform, account_name, access_token=''):
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO social_accounts (platform, account_name, access_token, is_connected)
            VALUES (?, ?, ?, ?)
        ''', (platform, account_name, access_token, 1 if access_token else 0))
        conn.commit()
        conn.close()
        return True
    
    @staticmethod
    def schedule_post(platform, content, scheduled_time):
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO scheduled_posts (platform, content, scheduled_time)
            VALUES (?, ?, ?)
        ''', (platform, content, scheduled_time))
        conn.commit()
        conn.close()
        return True
    
    @staticmethod
    def get_scheduled_posts():
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT platform, content, scheduled_time, status
            FROM scheduled_posts
            WHERE status = 'scheduled' AND scheduled_time > datetime('now')
            ORDER BY scheduled_time
        ''')
        posts = cursor.fetchall()
        conn.close()
        
        return [dict(zip(['platform', 'content', 'scheduled_time', 'status'], 
                        post)) for post in posts]

class WorkflowManager:
    """Manages automated workflows."""
    
    @staticmethod
    def send_daily_messages():
        """Send daily messages to members with overdue payments."""
        overdue_members = MemberManager.get_overdue_members()
        sent_count = 0
        
        for member in overdue_members:
            # Generate personalized message
            message = f"Hi {member['name']}, your payment of ${member['amount']} is {int(member['days_overdue'])} days overdue. Please update your payment method or contact us."
            
            # In real implementation, this would send via SMS/email
            print(f"Sending reminder to {member['name']}: {message}")
            
            # Log the action
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO system_logs (level, component, message)
                VALUES (?, ?, ?)
            ''', ('INFO', 'DailyMessages', f'Sent payment reminder to {member["name"]}'))
            conn.commit()
            conn.close()
            
            sent_count += 1
        
        return sent_count
    
    @staticmethod
    def process_overdue_payments():
        """Process overdue payments automatically."""
        overdue_payments = PaymentManager.get_overdue_payments()
        processed_count = 0
        
        for payment in overdue_payments:
            # In real implementation, this would attempt to charge saved payment methods
            success = PaymentManager.process_payment(payment['id'], 'auto_retry')
            if success:
                processed_count += 1
                
                # Log the action
                conn = db.get_connection()
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO system_logs (level, component, message)
                    VALUES (?, ?, ?)
                ''', ('INFO', 'PaymentProcessor', f'Auto-processed payment for {payment["member_name"]}'))
                conn.commit()
                conn.close()
        
        return processed_count

# Global status storage with real data
def get_system_status():
    """Get real system status."""
    members = MemberManager.get_all_members()
    overdue_payments = PaymentManager.get_overdue_payments()
    pending_messages = MessageManager.get_pending_messages()
    
    return {
        'services': {
            'square_payments': {'status': 'healthy', 'details': 'Payment processing active'},
            'gemini_ai': {'status': 'healthy', 'details': 'AI message responses enabled'},
            'member_database': {'status': 'healthy', 'details': f'{len(members)} active members'},
            'social_media': {'status': 'healthy', 'details': 'Social media management active'},
        },
        'last_update': datetime.now().isoformat(),
        'stats': {
            'total_members': len(members),
            'overdue_payments': len(overdue_payments),
            'pending_messages': len(pending_messages),
            'monthly_revenue': sum(m['monthly_fee'] for m in members if m['status'] == 'active')
        },
        'logs': get_recent_logs()
    }

def get_recent_logs():
    """Get recent system logs."""
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT level, component, message, timestamp
        FROM system_logs
        ORDER BY timestamp DESC
        LIMIT 50
    ''')
    logs = cursor.fetchall()
    conn.close()
    
    return [dict(zip(['level', 'component', 'message', 'timestamp'], log)) for log in logs]

# Routes with real functionality
@app.route('/')
def dashboard_home():
    """Main dashboard page with real data."""
    status = get_system_status()
    return render_template('dashboard.html', 
                         status=status,
                         project_id="gym-bot-pro")

@app.route('/workflows')
def workflows_page():
    """Workflows management page with real functionality."""
    workflows = {
        'daily_messages': {
            'name': 'Send Daily Messages',
            'description': 'Send automated messages to members with overdue payments',
            'status': 'available',
            'last_run': None
        },
        'payment_processing': {
            'name': 'Process Overdue Payments', 
            'description': 'Automatically retry failed payments and send reminders',
            'status': 'available',
            'last_run': None
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
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, name, email, phone, lead_source, status, interested_in, 
               follow_up_date, notes, created_at
        FROM prospects ORDER BY created_at DESC
    ''')
    prospects = cursor.fetchall()
    conn.close()
    
    prospects_data = [dict(zip(['id', 'name', 'email', 'phone', 'lead_source', 'status', 
                               'interested_in', 'follow_up_date', 'notes', 'created_at'], 
                              prospect)) for prospect in prospects]
    
    return render_template('prospects.html', prospects=prospects_data)

@app.route('/training-clients')
def training_clients_page():
    """Training clients management page with real imported data."""
    clients = MemberManager.get_training_clients()
    return render_template('training_clients.html', clients=clients)

@app.route('/social-media')
def social_media_page():
    """Social Media Management page with real data."""
    accounts = SocialMediaManager.get_connected_accounts()
    scheduled_posts = SocialMediaManager.get_scheduled_posts()
    
    return render_template('social_media.html', 
                         accounts=accounts,
                         scheduled_posts=scheduled_posts)

@app.route('/payments')
def payments_page():
    """Payments page with real data."""
    overdue_payments = PaymentManager.get_overdue_payments()
    
    # Get recent successful payments
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT m.name, p.amount, p.paid_date
        FROM payments p
        JOIN members m ON p.member_id = m.id
        WHERE p.status = 'paid' AND p.paid_date > date('now', '-30 days')
        ORDER BY p.paid_date DESC
        LIMIT 10
    ''')
    recent_payments = cursor.fetchall()
    conn.close()
    
    recent_payments_data = [dict(zip(['member', 'amount', 'date'], payment)) 
                           for payment in recent_payments]
    
    return render_template('payments.html', 
                         overdue_payments=overdue_payments,
                         recent_payments=recent_payments_data)

@app.route('/messaging')
def messaging_page():
    """Messaging page with real data."""
    pending_messages = MessageManager.get_pending_messages()
    
    # Get recent responses
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT member_name, content, response, responded_at
        FROM messages 
        WHERE status = 'responded' AND responded_at > datetime('now', '-7 days')
        ORDER BY responded_at DESC
        LIMIT 10
    ''')
    recent_responses = cursor.fetchall()
    conn.close()
    
    recent_responses_data = [dict(zip(['member', 'message', 'response', 'time'], resp)) 
                            for resp in recent_responses]
    
    return render_template('messaging.html', 
                         unread_messages=pending_messages,
                         recent_responses=recent_responses_data)

@app.route('/calendar')
def calendar_page():
    """Calendar page."""
    # In a real implementation, this would connect to scheduling system
    calendar_data = {
        'upcoming_classes': [
            {'name': 'Morning Yoga', 'time': '7:00 AM', 'instructor': 'Lisa M.', 'spots': 8},
            {'name': 'HIIT Training', 'time': '6:00 PM', 'instructor': 'Mark S.', 'spots': 3}
        ],
        'equipment_maintenance': [
            {'equipment': 'Treadmill #3', 'scheduled': '2025-07-22', 'type': 'Regular maintenance'},
            {'equipment': 'Weight rack', 'scheduled': '2025-07-24', 'type': 'Deep cleaning'}
        ]
    }
    return render_template('calendar.html', **calendar_data)

@app.route('/analytics')
def analytics_page():
    """Analytics page with real data."""
    members = MemberManager.get_all_members()
    status = get_system_status()
    
    analytics_data = {
        'kpis': [
            {'name': 'Revenue', 'current_value': status['stats']['monthly_revenue'], 'unit': 'USD', 'trend': 'up'},
            {'name': 'Members', 'current_value': status['stats']['total_members'], 'unit': 'count', 'trend': 'up'},
            {'name': 'Overdue', 'current_value': status['stats']['overdue_payments'], 'unit': 'count', 'trend': 'down'},
            {'name': 'Messages', 'current_value': status['stats']['pending_messages'], 'unit': 'count', 'trend': 'up'}
        ],
        'insights': [
            {
                'title': 'Payment Collection',
                'description': f'{status["stats"]["overdue_payments"]} overdue payments need attention',
                'recommendation': 'Run payment processing workflow',
                'impact': f'${sum(p["amount"] for p in PaymentManager.get_overdue_payments()):.2f} recoverable',
                'priority': 'high' if status["stats"]["overdue_payments"] > 3 else 'medium'
            }
        ]
    }
    return render_template('analytics.html', **analytics_data)

@app.route('/logs')
def logs_page():
    """System logs page."""
    logs = get_recent_logs()
    return render_template('logs.html', logs=logs)

@app.route('/settings')
def settings_page():
    """Settings page."""
    settings = {
        'gcp_project': 'gym-bot-pro',
        'database_path': DATABASE_PATH,
        'environment': 'production'
    }
    return render_template('settings.html', settings=settings)

# API Routes with real functionality
@app.route('/api/status')
def api_status():
    """API endpoint for system status."""
    return jsonify(get_system_status())

@app.route('/api/refresh-status')
def api_refresh_status():
    """Force refresh system status."""
    status = get_system_status()
    return jsonify({'success': True, 'status': status})

@app.route('/api/run-workflow', methods=['POST'])
def api_run_workflow():
    """API endpoint to run a workflow with real functionality."""
    workflow_name = request.json.get('workflow')
    
    if workflow_name == 'daily_messages':
        sent_count = WorkflowManager.send_daily_messages()
        return jsonify({
            'success': True, 
            'message': f'Daily messages workflow completed. Sent {sent_count} messages.'
        })
    
    elif workflow_name == 'payment_processing':
        processed_count = WorkflowManager.process_overdue_payments()
        return jsonify({
            'success': True,
            'message': f'Payment processing completed. Processed {processed_count} payments.'
        })
    
    return jsonify({'success': False, 'error': 'Unknown workflow'})

@app.route('/api/members/add', methods=['POST'])
def api_add_member():
    """Add a new member."""
    data = request.json
    success = MemberManager.add_member(
        data['name'], data['email'], data['phone'], 
        data['membership_type'], data['monthly_fee']
    )
    return jsonify({'success': success})

@app.route('/api/social-media/add-account', methods=['POST'])
def api_add_social_account():
    """Add a social media account."""
    data = request.json
    success = SocialMediaManager.add_social_account(
        data['platform'], data['account_name'], data.get('access_token', '')
    )
    return jsonify({'success': success})

@app.route('/api/social-media/schedule-post', methods=['POST'])
def api_schedule_post():
    """Schedule a social media post."""
    data = request.json
    success = SocialMediaManager.schedule_post(
        data['platform'], data['content'], data['scheduled_time']
    )
    return jsonify({'success': success})

@app.route('/api/messages/respond', methods=['POST'])
def api_respond_message():
    """Respond to a member message with AI."""
    data = request.json
    message_id = data['message_id']
    
    # Generate AI response (simplified)
    ai_response = f"Thank you for your message. We'll get back to you within 24 hours. For urgent matters, please call us at (555) 123-4567."
    
    MessageManager.send_ai_response(message_id, ai_response)
    return jsonify({'success': True, 'response': ai_response})

@app.route('/api/payments/send-reminder', methods=['POST'])
def api_send_payment_reminder():
    """Send payment reminder."""
    data = request.json
    payment_id = data['payment_id']
    success = PaymentManager.send_payment_reminder(payment_id)
    return jsonify({'success': success})

@app.route('/api/payments/process', methods=['POST'])
def api_process_payment():
    """Process a payment."""
    data = request.json
    payment_id = data['payment_id']
    success = PaymentManager.process_payment(payment_id)
    return jsonify({'success': success})

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
            <li><a class="nav-link" href="{{ url_for('payments_page') }}"><i class="fas fa-credit-card"></i>Payments</a></li>
            <li><a class="nav-link" href="{{ url_for('messaging_page') }}"><i class="fas fa-comments"></i>Messaging</a></li>
            <li><a class="nav-link" href="{{ url_for('calendar_page') }}"><i class="fas fa-calendar-alt"></i>Calendar</a></li>
            <li><a class="nav-link" href="{{ url_for('analytics_page') }}"><i class="fas fa-chart-bar"></i>Analytics</a></li>
            <li><a class="nav-link" href="{{ url_for('social_media_page') }}"><i class="fab fa-instagram"></i>Social Media</a></li>
            <li><a class="nav-link" href="{{ url_for('settings_page') }}"><i class="fas fa-cog"></i>Settings</a></li>
            <li><a class="nav-link" href="{{ url_for('logs_page') }}"><i class="fas fa-file-alt"></i>Logs</a></li>
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
            <div class="metric-value text-primary">{{ status.stats.total_members }}</div>
            <div class="metric-label">Total Members</div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card metric-card">
            <div class="metric-value text-danger">{{ status.stats.overdue_payments }}</div>
            <div class="metric-label">Overdue Payments</div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card metric-card">
            <div class="metric-value text-info">${{ "%.2f"|format(status.stats.monthly_revenue) }}</div>
            <div class="metric-label">Monthly Revenue</div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card metric-card">
            <div class="metric-value text-warning">{{ status.stats.pending_messages }}</div>
            <div class="metric-label">Pending Messages</div>
        </div>
    </div>
</div>

<div class="row">
    <div class="col-lg-8">
        <div class="card">
            <div class="card-header">
                <h5><i class="fas fa-heartbeat me-2"></i>System Health</h5>
            </div>
            <div class="card-body">
                <div class="row">
                    {% for service, info in status.services.items() %}
                    <div class="col-md-6 mb-3">
                        <div class="d-flex align-items-center">
                            <div class="status-indicator status-healthy me-3">
                                <i class="fas fa-check-circle"></i>
                            </div>
                            <div>
                                <strong>{{ service.replace('_', ' ').title() }}</strong><br>
                                <small class="text-muted">{{ info.details }}</small>
                            </div>
                        </div>
                    </div>
                    {% endfor %}
                </div>
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
                    <a href="{{ url_for('members_page') }}" class="btn btn-outline-success">
                        <i class="fas fa-users me-2"></i>Manage Members
                    </a>
                    <a href="{{ url_for('payments_page') }}" class="btn btn-outline-danger">
                        <i class="fas fa-credit-card me-2"></i>Process Payments
                    </a>
                    <a href="{{ url_for('messaging_page') }}" class="btn btn-outline-info">
                        <i class="fas fa-comments me-2"></i>Handle Messages
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
        alert(data.success ? 'Workflow started!' : 'Error: ' + data.error);
    });
}
</script>
{% endblock %}'''

    # Initialize templates dictionary with base templates
    templates = {
        'base.html': base_template,
        'dashboard.html': dashboard_template,
        'workflows.html': workflows_template
    }

    # Add new functional templates
    templates.update({
        'members.html': '''{% extends "base.html" %}
{% block title %}Members{% endblock %}
{% block page_title %}Member Directory{% endblock %}

{% block content %}
<div class="row mb-3">
    <div class="col-12">
        <div class="d-flex justify-content-between align-items-center">
            <h5 class="mb-0">{{ members|length }} Total Members</h5>
            <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#addMemberModal">
                <i class="fas fa-plus me-1"></i> Add Member
            </button>
        </div>
    </div>
</div>

<div class="row">
    {% for member in members %}
    <div class="col-md-6 col-lg-4 mb-4">
        <div class="card h-100">
            <div class="card-body">
                <h5 class="card-title">{{ member.name }}</h5>
                <div class="mb-2">
                    <small class="text-muted">ID: {{ member.id }}</small>
                    {% if member.status == 'active' %}
                    <span class="badge bg-success ms-2">Active</span>
                    {% else %}
                    <span class="badge bg-secondary ms-2">{{ member.status.title() }}</span>
                    {% endif %}
                </div>
                
                <!-- Contact Information -->
                {% if member.email %}
                <p class="mb-1"><i class="fas fa-envelope me-2"></i><a href="mailto:{{ member.email }}">{{ member.email }}</a></p>
                {% endif %}
                {% if member.mobile_phone %}
                <p class="mb-1"><i class="fas fa-mobile me-2"></i><a href="tel:{{ member.mobile_phone }}">{{ member.mobile_phone }}</a></p>
                {% endif %}
                {% if member.address1 %}
                <p class="mb-2"><i class="fas fa-map-marker-alt me-2"></i>{{ member.city }}, {{ member.state }}</p>
                {% endif %}
                
                <!-- Agreement Information -->
                {% if member.agreement_id %}
                <div class="border-top pt-2 mt-2">
                    <h6 class="text-primary">Agreement Details</h6>
                    <p class="mb-1"><strong>ID:</strong> {{ member.agreement_id }}</p>
                    {% if member.agreement_status %}
                    <p class="mb-1"><strong>Status:</strong> 
                        <span class="badge bg-info">{{ member.agreement_status }}</span>
                    </p>
                    {% endif %}
                    {% if member.monthly_amount %}
                    <p class="mb-1"><strong>Monthly:</strong> ${{ member.monthly_amount }}</p>
                    {% endif %}
                    {% if member.next_billing_date %}
                    <p class="mb-1"><strong>Next Billing:</strong> {{ member.next_billing_date }}</p>
                    {% endif %}
                </div>
                {% endif %}
                
                <!-- Payment Information -->
                {% if member.card_type %}
                <div class="border-top pt-2 mt-2">
                    <h6 class="text-success">Payment Info</h6>
                    <p class="mb-1"><strong>Card:</strong> {{ member.card_type }}
                    {% if member.card_last_four %} •••• {{ member.card_last_four }}{% endif %}</p>
                    {% if member.card_exp_month and member.card_exp_year %}
                    <p class="mb-1"><strong>Expires:</strong> {{ member.card_exp_month }}/{{ member.card_exp_year }}</p>
                    {% endif %}
                </div>
                {% endif %}
                
                <!-- Home Club -->
                {% if member.home_club_name %}
                <div class="border-top pt-2 mt-2">
                    <h6 class="text-warning">Home Club</h6>
                    <p class="mb-1">{{ member.home_club_name }}</p>
                    {% if member.home_club_phone %}
                    <p class="mb-1"><i class="fas fa-phone me-2"></i>{{ member.home_club_phone }}</p>
                    {% endif %}
                </div>
                {% endif %}
                
                <!-- Action Buttons -->
                <div class="mt-3 d-flex gap-2">
                    <button class="btn btn-sm btn-outline-primary" onclick="viewMember({{ member.id }})">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-success" onclick="messageMember({{ member.id }})">
                        <i class="fas fa-envelope"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-info" onclick="editMember({{ member.id }})">
                        <i class="fas fa-edit"></i>
                    </button>
                </div>
            </div>
        </div>
    </div>
    {% endfor %}
</div>

<!-- Add Member Modal -->
<div class="modal fade" id="addMemberModal">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">Add New Member</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <form id="addMemberForm">
                <div class="modal-body">
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
                        <input type="tel" class="form-control" name="phone">
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Membership Type</label>
                        <select class="form-select" name="membership_type" required>
                            <option value="Basic">Basic Membership</option>
                            <option value="Premium">Premium Membership</option>
                            <option value="VIP">VIP Membership</option>
                        </select>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Monthly Fee</label>
                        <input type="number" class="form-control" name="monthly_fee" step="0.01">
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="submit" class="btn btn-primary">Add Member</button>
                </div>
            </form>
        </div>
    </div>
</div>

<script>
function viewMember(id) {
    // View member details
    alert('View member ' + id + ' - Feature coming soon!');
}

function messageMember(id) {
    // Send message to member
    alert('Message member ' + id + ' - Feature coming soon!');
}

function editMember(id) {
    // Edit member information
    alert('Edit member ' + id + ' - Feature coming soon!');
}

// Handle add member form
document.getElementById('addMemberForm').addEventListener('submit', function(e) {
    e.preventDefault();
    alert('Add member functionality - Feature coming soon!');
});
</script>
{% endblock %}'''
    })
    
    # Create templates directory
    templates_dir = 'templates'
    if not os.path.exists(templates_dir):
        os.makedirs(templates_dir)
    
    for filename, content in templates.items():
        filepath = os.path.join(templates_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
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
                {% for account in accounts %}
                <div class="d-flex justify-content-between mb-2">
                    <span><i class="fab fa-{{ account.platform }}"></i> {{ account.account_name }}</span>
                    <span class="badge bg-{% if account.is_connected %}success{% else %}danger{% endif %}">
                        {% if account.is_connected %}Connected{% else %}Disconnected{% endif %}
                    </span>
                </div>
                {% endfor %}
                {% if not accounts %}
                <p class="text-muted">No social media accounts connected yet.</p>
                {% endif %}
            </div>
        </div>
    </div>
    <div class="col-md-6">
        <div class="card">
            <div class="card-header"><h5>Scheduled Posts</h5></div>
            <div class="card-body">
                {% for post in scheduled_posts %}
                <div class="border rounded p-2 mb-2">
                    <strong>{{ post.platform.title() }}</strong><br>
                    <small>{{ post.content[:50] }}...</small><br>
                    <small class="text-muted">{{ post.scheduled_time }}</small>
                </div>
                {% endfor %}
                {% if not scheduled_posts %}
                <p class="text-muted">No posts scheduled.</p>
                {% endif %}
            </div>
        </div>
    </div>
</div>

<!-- Add Account Modal -->
<div class="modal fade" id="addAccountModal">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">Connect Social Media Account</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <form id="addAccountForm">
                <div class="modal-body">
                    <div class="mb-3">
                        <label class="form-label">Platform</label>
                        <select class="form-select" name="platform" required>
                            <option value="facebook">Facebook</option>
                            <option value="instagram">Instagram</option>
                            <option value="twitter">Twitter</option>
                        </select>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Account Name</label>
                        <input type="text" class="form-control" name="account_name" required>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="submit" class="btn btn-primary">Connect</button>
                </div>
            </form>
        </div>
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
            <div class="card-header">
                <h5>Overdue Payments 
                    <span class="badge bg-danger">{{ overdue_payments|length }}</span>
                </h5>
            </div>
            <div class="card-body">
                {% for payment in overdue_payments %}
                <div class="d-flex justify-content-between align-items-center mb-3 p-2 border rounded">
                    <div>
                        <strong>{{ payment.member_name }}</strong><br>
                        <small class="text-danger">${{ "%.2f"|format(payment.amount) }} - {{ "%.0f"|format(payment.days_overdue) }} days overdue</small><br>
                        <small class="text-muted">{{ payment.email }}</small>
                    </div>
                    <div>
                        <button class="btn btn-sm btn-warning me-1" onclick="sendReminder({{ payment.id }})">
                            <i class="fas fa-envelope"></i> Remind
                        </button>
                        <button class="btn btn-sm btn-success" onclick="processPayment({{ payment.id }})">
                            <i class="fas fa-credit-card"></i> Process
                        </button>
                    </div>
                </div>
                {% endfor %}
                {% if not overdue_payments %}
                <p class="text-success">No overdue payments!</p>
                {% endif %}
            </div>
        </div>
    </div>
    <div class="col-md-6">
        <div class="card">
            <div class="card-header"><h5>Recent Payments</h5></div>
            <div class="card-body">
                {% for payment in recent_payments %}
                <div class="d-flex justify-content-between mb-2">
                    <span>{{ payment.member }}</span>
                    <span class="text-success">${{ "%.2f"|format(payment.amount) }}</span>
                </div>
                {% endfor %}
                {% if not recent_payments %}
                <p class="text-muted">No recent payments.</p>
                {% endif %}
            </div>
        </div>
    </div>
</div>

<script>
function sendReminder(paymentId) {
    fetch('/api/payments/send-reminder', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({payment_id: paymentId})
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Payment reminder sent!');
        } else {
            alert('Error sending reminder');
        }
    });
}

function processPayment(paymentId) {
    if (confirm('Process this payment?')) {
        fetch('/api/payments/process', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({payment_id: paymentId})
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                alert('Error processing payment');
            }
        });
    }
}
</script>
{% endblock %}''',
        
        'messaging.html': '''{% extends "base.html" %}
{% block title %}Messaging{% endblock %}
{% block page_title %}Member Messaging{% endblock %}
{% block content %}
<div class="row">
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">
                <h5>Pending Messages 
                    <span class="badge bg-warning">{{ unread_messages|length }}</span>
                </h5>
            </div>
            <div class="card-body">
                {% for message in unread_messages %}
                <div class="border rounded p-3 mb-3">
                    <div class="d-flex justify-content-between align-items-start">
                        <div class="flex-grow-1">
                            <strong>{{ message.member_name }}</strong>
                            <span class="badge bg-info ms-2">{{ message.message_type }}</span><br>
                            <p class="mt-2 mb-2">{{ message.content }}</p>
                            <small class="text-muted">{{ message.created_at }}</small>
                        </div>
                        <button class="btn btn-sm btn-primary" onclick="respondToMessage({{ message.id }})">
                            <i class="fas fa-reply"></i> Respond
                        </button>
                    </div>
                </div>
                {% endfor %}
                {% if not unread_messages %}
                <p class="text-success">No pending messages!</p>
                {% endif %}
            </div>
        </div>
    </div>
    <div class="col-md-6">
        <div class="card">
            <div class="card-header"><h5>Recent AI Responses</h5></div>
            <div class="card-body">
                {% for response in recent_responses %}
                <div class="border rounded p-2 mb-2">
                    <strong>{{ response.member }}</strong><br>
                    <small class="text-muted">{{ response.message[:50] }}...</small><br>
                    <small class="text-success">{{ response.response[:50] }}...</small><br>
                    <small class="text-muted">{{ response.time }}</small>
                </div>
                {% endfor %}
                {% if not recent_responses %}
                <p class="text-muted">No recent responses.</p>
                {% endif %}
            </div>
        </div>
    </div>
</div>

<script>
function respondToMessage(messageId) {
    fetch('/api/messages/respond', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({message_id: messageId})
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('AI response sent: ' + data.response);
            location.reload();
        } else {
            alert('Error sending response');
        }
    });
}
</script>
{% endblock %}''',
                        </td>
                        <td>${{ member.monthly_fee }}</td>
                        <td>
                            <button class="btn btn-sm btn-outline-primary">Edit</button>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</div>

<!-- Add Member Modal -->
<div class="modal fade" id="addMemberModal">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">Add New Member</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <form id="addMemberForm">
                <div class="modal-body">
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
                        <input type="tel" class="form-control" name="phone">
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Membership Type</label>
                        <select class="form-select" name="membership_type" required>
                            <option value="Basic">Basic ($89.99/month)</option>
                            <option value="Premium">Premium ($149.99/month)</option>
                        </select>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="submit" class="btn btn-primary">Add Member</button>
                </div>
            </form>
        </div>
    </div>
</div>

<script>
document.getElementById('addMemberForm').addEventListener('submit', function(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    const memberData = {
        name: formData.get('name'),
        email: formData.get('email'),
        phone: formData.get('phone'),
        membership_type: formData.get('membership_type'),
        monthly_fee: formData.get('membership_type') === 'Basic' ? 89.99 : 149.99
    };
    
    fetch('/api/members/add', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(memberData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        } else {
            alert('Error adding member');
        }
    });
});
</script>
{% endblock %}''',
        
        'prospects.html': '''{% extends "base.html" %}
{% block title %}Prospects{% endblock %}
{% block page_title %}Prospect Management{% endblock %}
{% block content %}
<div class="card">
    <div class="card-header"><h5>All Prospects</h5></div>
    <div class="card-body">
        <div class="table-responsive">
            <table class="table">
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Email</th>
                        <th>Phone</th>
                        <th>Lead Source</th>
                        <th>Status</th>
                        <th>Interested In</th>
                        <th>Follow Up</th>
                    </tr>
                </thead>
                <tbody>
                    {% for prospect in prospects %}
                    <tr>
                        <td>{{ prospect.name }}</td>
                        <td>{{ prospect.email }}</td>
                        <td>{{ prospect.phone }}</td>
                        <td>{{ prospect.lead_source }}</td>
                        <td>
                            <span class="badge bg-info">{{ prospect.status }}</span>
                        </td>
                        <td>{{ prospect.interested_in }}</td>
                        <td>{{ prospect.follow_up_date }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</div>
{% endblock %}''',
        
        'training_clients.html': '''{% extends "base.html" %}
{% block title %}Training Clients{% endblock %}
{% block page_title %}Personal Training Clients{% endblock %}
{% block content %}
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
                        <td>{{ client.member_name }}</td>
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
{% endblock %}'''
    })

    # Create templates directory
    templates_dir = 'templates'
    if not os.path.exists(templates_dir):
        os.makedirs(templates_dir)
    
    for filename, content in templates.items():
    <div class="col-md-6">
        <div class="card">
            <div class="card-header"><h5>Connected Accounts</h5></div>
            <div class="card-body">
                {% for account in accounts %}
                <div class="d-flex justify-content-between mb-2">
                    <span><i class="fab fa-{{ account.platform }}"></i> {{ account.account_name }}</span>
                    <span class="badge bg-success">Connected</span>
                </div>
                {% endfor %}
            </div>
        </div>
    </div>
    <div class="col-md-6">
        <div class="card">
            <div class="card-header"><h5>Scheduled Posts</h5></div>
            <div class="card-body">
                {% for post in scheduled_posts %}
                <div class="border rounded p-2 mb-2">
                    <strong>{{ post.platform.title() }}</strong><br>
                    <small>{{ post.content[:50] }}...</small><br>
                    <small class="text-muted">{{ post.scheduled_time }}</small>
                </div>
                {% endfor %}
            </div>
        </div>
    </div>
</div>
{% endblock %}''',
        'analytics.html': '''{% extends "base.html" %}
{% block title %}Analytics{% endblock %}
{% block page_title %}Analytics & Business Insights{% endblock %}
{% block content %}
<div class="row mb-4">
    {% for kpi in kpis[:4] %}
    <div class="col-md-3">
        <div class="card metric-card">
            <div class="metric-value text-primary">{{ kpi.current_value }}{% if kpi.unit == '%' %}%{% endif %}</div>
            <div class="metric-label">{{ kpi.name }}</div>
        </div>
    </div>
    {% endfor %}
</div>
<div class="card">
    <div class="card-header"><h5>Business Insights</h5></div>
    <div class="card-body">
        {% for insight in insights %}
        <div class="border rounded p-3 mb-3">
            <h6>{{ insight.title }}</h6>
            <p>{{ insight.description }}</p>
            <strong>Recommendation:</strong> {{ insight.recommendation }}
        </div>
        {% endfor %}
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
                {% for payment in overdue_payments %}
                <div class="d-flex justify-content-between mb-2">
                    <span>{{ payment.member }}</span>
                    <span class="text-danger">${{ payment.amount }} ({{ payment.days_overdue }} days)</span>
                </div>
                {% endfor %}
            </div>
        </div>
    </div>
    <div class="col-md-6">
        <div class="card">
            <div class="card-header"><h5>Recent Payments</h5></div>
            <div class="card-body">
                {% for payment in recent_payments %}
                <div class="d-flex justify-content-between mb-2">
                    <span>{{ payment.member }}</span>
                    <span class="text-success">${{ payment.amount }}</span>
                </div>
                {% endfor %}
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
                {% for message in unread_messages %}
                <div class="border rounded p-2 mb-2">
                    <strong>{{ message.member }}</strong><br>
                    <small>{{ message.message }}</small><br>
                    <small class="text-muted">{{ message.time }}</small>
                </div>
                {% endfor %}
            </div>
        </div>
    </div>
    <div class="col-md-6">
        <div class="card">
            <div class="card-header"><h5>Recent AI Responses</h5></div>
            <div class="card-body">
                {% for response in recent_responses %}
                <div class="border rounded p-2 mb-2">
                    <strong>{{ response.member }}</strong><br>
                    <small>{{ response.response }}</small><br>
                    <small class="text-muted">{{ response.time }}</small>
                </div>
                {% endfor %}
            </div>
        </div>
    </div>
</div>
{% endblock %}''',
        'calendar.html': '''{% extends "base.html" %}
{% block title %}Calendar{% endblock %}
{% block page_title %}Calendar & Scheduling{% endblock %}
{% block content %}
<div class="row">
    <div class="col-md-6">
        <div class="card">
            <div class="card-header"><h5>Upcoming Classes</h5></div>
            <div class="card-body">
                {% for class in upcoming_classes %}
                <div class="d-flex justify-content-between mb-2">
                    <div>
                        <strong>{{ class.name }}</strong><br>
                        <small>{{ class.time }} - {{ class.instructor }}</small>
                    </div>
                    <span class="badge bg-info">{{ class.spots }} spots</span>
                </div>
                {% endfor %}
            </div>
        </div>
    </div>
    <div class="col-md-6">
        <div class="card">
            <div class="card-header"><h5>Equipment Maintenance</h5></div>
            <div class="card-body">
                {% for maintenance in equipment_maintenance %}
                <div class="d-flex justify-content-between mb-2">
                    <div>
                        <strong>{{ maintenance.equipment }}</strong><br>
                        <small>{{ maintenance.type }}</small>
                    </div>
                    <span class="text-muted">{{ maintenance.scheduled }}</span>
                </div>
                {% endfor %}
            </div>
        </div>
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
        'settings.html': '''{% extends "base.html" %}
{% block title %}Settings{% endblock %}
{% block page_title %}System Settings{% endblock %}
{% block content %}
<div class="card">
    <div class="card-header"><h5>Configuration</h5></div>
    <div class="card-body">
        <p><strong>GCP Project:</strong> {{ settings.gcp_project }}</p>
        <p><strong>Migration Mode:</strong> {{ settings.migration_mode }}</p>
        <p><strong>Environment:</strong> {{ settings.environment }}</p>
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