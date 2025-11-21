#!/usr/bin/env python3
"""
Simple Anytime Fitness Dashboard - Minimal Working Version
"""

import os
import sys
import sqlite3
from flask import Flask, render_template, jsonify, request
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app with absolute paths
base_dir = os.path.dirname(os.path.abspath(__file__))
templates_dir = os.path.join(base_dir, 'templates')
static_dir = os.path.join(base_dir, 'static')

app = Flask(__name__, template_folder=templates_dir, static_folder=static_dir)
app.secret_key = 'anytime-fitness-dashboard-secret-key-2025'

# Debug template configuration
logger.info(f"📁 Flask app template folder: {app.template_folder}")
logger.info(f"📁 Calculated templates dir: {templates_dir}")
logger.info(f"📁 Templates dir exists: {os.path.exists(templates_dir)}")
logger.info(f"📁 members.html exists: {os.path.exists(os.path.join(templates_dir, 'members.html'))}")

# Simple database setup
def init_simple_database():
    """Initialize a simple database for testing"""
    conn = sqlite3.connect('gym_bot.db')
    cursor = conn.cursor()
    
    # Create simple members table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            email TEXT,
            status TEXT DEFAULT 'Active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert some test data if empty
    cursor.execute("SELECT COUNT(*) FROM members")
    if cursor.fetchone()[0] == 0:
        test_members = [
            ('John', 'Doe', 'john.doe@example.com', 'Active'),
            ('Jane', 'Smith', 'jane.smith@example.com', 'Active'),
            ('Mike', 'Johnson', 'mike.johnson@example.com', 'Past Due'),
        ]
        cursor.executemany(
            "INSERT INTO members (first_name, last_name, email, status) VALUES (?, ?, ?, ?)", 
            test_members
        )
    
    conn.commit()
    conn.close()

# Initialize database
init_simple_database()

@app.route('/')
def dashboard():
    """Main dashboard with overview."""
    logger.info("=== DASHBOARD ROUTE TRIGGERED ===")
    
    # Get data from database
    conn = sqlite3.connect('gym_bot.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM members")
    total_members = cursor.fetchone()[0]
    
    cursor.execute("SELECT first_name, last_name, email, status FROM members ORDER BY created_at DESC LIMIT 5")
    recent_members_data = cursor.fetchall()
    recent_members = [
        {'first_name': row[0], 'last_name': row[1], 'email': row[2], 'status': row[3]} 
        for row in recent_members_data
    ]
    
    conn.close()
    
    logger.info(f"📊 Database Stats: {total_members} members")
    
    return render_template('dashboard.html', 
                         total_members=total_members,
                         total_prospects=0,
                         total_training_clients=0,
                         total_live_events=0,
                         today_events_count=0,
                         training_sessions_count=0,
                         appointments_count=0,
                         bot_messages_today=0,
                         active_conversations=0,
                         bot_activities=[],
                         bot_conversations=[],
                         bot_stats={'messages_sent': 0, 'last_activity': 'None'},
                         stats={'todays_events': 0, 'next_session_time': 'None', 'revenue': '$0'},
                         recent_members=recent_members,
                         recent_prospects=[],
                         recent_events=[],
                         clubos_status="Disconnected",
                         clubos_connected=False,
                         sync_time=datetime.now())

@app.route('/members')
def members_page():
    """Display members page."""
    logger.info("🔄 Members page loaded")
    
    # Get members from database
    conn = sqlite3.connect('gym_bot.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM members")
    total_members = cursor.fetchone()[0]
    
    cursor.execute("SELECT id, first_name, last_name, email, status FROM members")
    members_data = cursor.fetchall()
    members = [
        {
            'id': row[0],
            'first_name': row[1], 
            'last_name': row[2], 
            'full_name': f"{row[1]} {row[2]}",
            'email': row[3], 
            'status': row[4],
            'amount_past_due': 0 if row[4] != 'Past Due' else 150.00
        } 
        for row in members_data
    ]
    
    conn.close()
    
    return render_template('members.html',
                         members=members,
                         total_members=total_members,
                         statuses=['Active', 'Past Due'],
                         search='',
                         status_filter='',
                         page=1,
                         total_pages=1,
                         per_page=50,
                         red_list_count=1,
                         yellow_list_count=0,
                         past_due_count=1)

@app.route('/api/members/all')
def get_all_members():
    """API endpoint to get all members."""
    try:
        conn = sqlite3.connect('gym_bot.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, first_name, last_name, email, status FROM members")
        members_data = cursor.fetchall()
        members = [
            {
                'id': row[0],
                'first_name': row[1], 
                'last_name': row[2], 
                'full_name': f"{row[1]} {row[2]}",
                'email': row[3], 
                'status': row[4],
                'amount_past_due': 0 if row[4] != 'Past Due' else 150.00
            } 
            for row in members_data
        ]
        
        conn.close()
        
        return jsonify({
            'success': True,
            'members': members,
            'total': len(members)
        })
        
    except Exception as e:
        logger.error(f"❌ Error getting members: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/prospects')
def prospects_page():
    """Display prospects page."""
    return render_template('prospects.html',
                         prospects=[],
                         total_prospects=0,
                         statuses=[],
                         search='',
                         page=1,
                         total_pages=1,
                         per_page=50)

@app.route('/training-clients')
def training_clients_page():
    """Display training clients page."""
    return render_template('training_clients.html',
                         training_clients=[],
                         total_training_clients=0,
                         search='',
                         page=1,
                         total_pages=1,
                         per_page=50)

@app.route('/calendar')
def calendar_page():
    """Display calendar page."""
    return render_template('calendar.html')

if __name__ == '__main__':
    logger.info("🚀 Starting Simple Anytime Fitness Dashboard...")
    app.run(debug=True, use_reloader=False, host='0.0.0.0', port=5000)
