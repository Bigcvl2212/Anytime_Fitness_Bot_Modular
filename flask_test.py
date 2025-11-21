#!/usr/bin/env python3
"""
Minimal Flask Test - Check Template Loading
"""
import os
import sys
from flask import Flask, render_template

# Add src directory to Python path for imports  
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
sys.path.insert(0, os.path.dirname(__file__))

# Initialize Flask app with absolute paths
base_dir = os.path.dirname(os.path.abspath(__file__))
templates_dir = os.path.join(base_dir, 'templates')
static_dir = os.path.join(base_dir, 'static')

app = Flask(__name__, template_folder=templates_dir, static_folder=static_dir)
app.secret_key = 'test-key'

print(f"📁 Flask app template folder: {app.template_folder}")
print(f"📁 Calculated templates dir: {templates_dir}")  
print(f"📁 Templates dir exists: {os.path.exists(templates_dir)}")
print(f"📁 members.html exists: {os.path.exists(os.path.join(templates_dir, 'members.html'))}")

@app.route('/')
def home():
    return "<h1>Flask Test - Template Loading</h1><a href='/members'>Test Members Template</a>"

@app.route('/members')
def test_members():
    """Test loading the members template"""
    return render_template('members.html',
                         members=[],
                         total_members=0,
                         statuses=[],
                         search='',
                         status_filter='',
                         page=1,
                         total_pages=1,
                         per_page=50,
                         red_list_count=0,
                         yellow_list_count=0,
                         past_due_count=0)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
