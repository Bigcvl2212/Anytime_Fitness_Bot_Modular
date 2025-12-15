#!/usr/bin/env python3
"""
Gym Bot Setup Wizard
First-time configuration GUI for new installations
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import requests
from pathlib import Path

try:
    from dotenv import dotenv_values
except ImportError:  # pragma: no cover - optional dependency
    dotenv_values = None


def resolve_config_dir() -> Path:
    """Determine persistent config directory for wizard data"""
    override = os.environ.get('GYMBOT_CONFIG_DIR')
    if override:
        target = Path(override).expanduser()
    elif getattr(sys, 'frozen', False):
        if sys.platform == 'win32':
            base = Path(os.environ.get('LOCALAPPDATA', Path.home()))
            target = base / 'GymBot'
        elif sys.platform == 'darwin':
            target = Path.home() / 'Library' / 'Application Support' / 'GymBot'
        else:
            base = Path(os.environ.get('XDG_CONFIG_HOME', Path.home() / '.config'))
            target = Path(base) / 'gymbot'
    else:
        target = Path(__file__).parent

    target.mkdir(parents=True, exist_ok=True)
    return target


class SetupWizard:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Gym Bot - First Time Setup")
        self.root.geometry("700x600")
        self.root.resizable(False, False)

        self.config_dir = resolve_config_dir()
        self.env_path = self.config_dir / '.env'
        self.setup_complete_path = self.config_dir / '.setup_complete'

        # Configuration values
        self.config = {
            'FLASK_SECRET_KEY': '',
            'CLUBOS_USERNAME': '',
            'CLUBOS_PASSWORD': '',
            'CLUBHUB_EMAIL': '',
            'CLUBHUB_PASSWORD': '',
            'SQUARE_ACCESS_TOKEN': '',
            'SQUARE_LOCATION_ID': '',
            'GROQ_API_KEY': ''
        }

        self._load_existing_config()

        self.current_page = 0
        self.pages = []

        # Create pages
        self.create_welcome_page()
        self.create_clubos_page()
        self.create_clubhub_page()
        self.create_square_page()
        self.create_ai_page()
        self.create_summary_page()

        # Show first page
        self.show_page(0)

    def _load_existing_config(self):
        """Populate config defaults from existing .env if available"""
        if not dotenv_values or not self.env_path.exists():
            return

        try:
            env_values = dotenv_values(self.env_path)
        except Exception:
            return

        for key in self.config:
            value = env_values.get(key)
            if value:
                self.config[key] = value

    def _prefill_entry(self, entry_widget: ttk.Entry, value: str):
        if value:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, value)

    def create_welcome_page(self):
        """Welcome and introduction page"""
        frame = ttk.Frame(self.root, padding="20")

        # Title
        title = ttk.Label(frame, text="Welcome to Gym Bot Setup",
                         font=('Arial', 18, 'bold'))
        title.pack(pady=20)

        # Description
        desc = ttk.Label(frame, text="""
This wizard will help you configure Gym Bot for your gym.

You'll need the following information:
• ClubOS credentials (username and password)
• ClubHub credentials (email and password)
• Square API credentials (optional - for invoicing)
• Groq API key (optional - for AI features, FREE)

The setup will take approximately 5-10 minutes.

Click 'Next' to begin setup.
        """, justify='left', wraplength=600)
        desc.pack(pady=20)

        # Navigation buttons
        nav_frame = ttk.Frame(frame)
        nav_frame.pack(side='bottom', fill='x', pady=20)

        ttk.Button(nav_frame, text="Exit", command=self.exit_wizard).pack(side='left')
        ttk.Button(nav_frame, text="Next", command=self.next_page).pack(side='right')

        self.pages.append(frame)

    def create_clubos_page(self):
        """ClubOS credentials page"""
        frame = ttk.Frame(self.root, padding="20")

        title = ttk.Label(frame, text="ClubOS Integration",
                         font=('Arial', 16, 'bold'))
        title.pack(pady=10)

        desc = ttk.Label(frame, text="""
ClubOS is required to access your member data, send messages,
and manage your gym operations. Enter your ClubOS login credentials below.
        """, justify='left', wraplength=600)
        desc.pack(pady=10)

        # Input fields
        input_frame = ttk.Frame(frame)
        input_frame.pack(pady=20, fill='x')

        ttk.Label(input_frame, text="ClubOS Username:").grid(row=0, column=0, sticky='w', pady=5)
        self.clubos_username = ttk.Entry(input_frame, width=40)
        self.clubos_username.grid(row=0, column=1, pady=5, padx=10)
        self._prefill_entry(self.clubos_username, self.config['CLUBOS_USERNAME'])

        ttk.Label(input_frame, text="ClubOS Password:").grid(row=1, column=0, sticky='w', pady=5)
        self.clubos_password = ttk.Entry(input_frame, width=40, show='*')
        self.clubos_password.grid(row=1, column=1, pady=5, padx=10)
        self._prefill_entry(self.clubos_password, self.config['CLUBOS_PASSWORD'])

        # Test connection button
        ttk.Button(input_frame, text="Test Connection",
                  command=self.test_clubos_connection).grid(row=2, column=1, pady=10)

        self.clubos_status = ttk.Label(input_frame, text="", foreground='gray')
        self.clubos_status.grid(row=3, column=1, pady=5)

        # Navigation
        nav_frame = ttk.Frame(frame)
        nav_frame.pack(side='bottom', fill='x', pady=20)

        ttk.Button(nav_frame, text="Back", command=self.prev_page).pack(side='left')
        ttk.Button(nav_frame, text="Next", command=self.next_page).pack(side='right')

        self.pages.append(frame)

    def create_clubhub_page(self):
        """ClubHub credentials page"""
        frame = ttk.Frame(self.root, padding="20")

        title = ttk.Label(frame, text="ClubHub Integration",
                         font=('Arial', 16, 'bold'))
        title.pack(pady=10)

        desc = ttk.Label(frame, text="""
    ClubHub is the new API system for accessing club data.
    Enter the SAME email and password you use to log into the ClubHub app/website.
        """, justify='left', wraplength=600)
        desc.pack(pady=10)

        # Input fields
        input_frame = ttk.Frame(frame)
        input_frame.pack(pady=20, fill='x')

        ttk.Label(input_frame, text="ClubHub Email (exact login email):").grid(row=0, column=0, sticky='w', pady=5)
        self.clubhub_email = ttk.Entry(input_frame, width=40)
        self.clubhub_email.grid(row=0, column=1, pady=5, padx=10)
        self._prefill_entry(self.clubhub_email, self.config['CLUBHUB_EMAIL'])

        ttk.Label(input_frame, text="ClubHub Password:").grid(row=1, column=0, sticky='w', pady=5)
        self.clubhub_password = ttk.Entry(input_frame, width=40, show='*')
        self.clubhub_password.grid(row=1, column=1, pady=5, padx=10)
        self._prefill_entry(self.clubhub_password, self.config['CLUBHUB_PASSWORD'])

        # Test connection button
        ttk.Button(input_frame, text="Test Connection",
                  command=self.test_clubhub_connection).grid(row=2, column=1, pady=10)

        self.clubhub_status = ttk.Label(input_frame, text="", foreground='gray')
        self.clubhub_status.grid(row=3, column=1, pady=5)

        # Navigation
        nav_frame = ttk.Frame(frame)
        nav_frame.pack(side='bottom', fill='x', pady=20)

        ttk.Button(nav_frame, text="Back", command=self.prev_page).pack(side='left')
        ttk.Button(nav_frame, text="Next", command=self.next_page).pack(side='right')

        self.pages.append(frame)

    def create_square_page(self):
        """Square API credentials page (optional)"""
        frame = ttk.Frame(self.root, padding="20")

        title = ttk.Label(frame, text="Square Integration (Optional)",
                         font=('Arial', 16, 'bold'))
        title.pack(pady=10)

        desc = ttk.Label(frame, text="""
Square integration allows you to send invoices and track payments.
This is optional - you can skip this step and add it later.

To get your Square credentials:
1. Go to https://developer.squareup.com/apps
2. Create a new application or select existing
3. Copy your Access Token and Location ID
        """, justify='left', wraplength=600)
        desc.pack(pady=10)

        # Input fields
        input_frame = ttk.Frame(frame)
        input_frame.pack(pady=20, fill='x')

        ttk.Label(input_frame, text="Square Access Token:").grid(row=0, column=0, sticky='w', pady=5)
        self.square_token = ttk.Entry(input_frame, width=40, show='*')
        self.square_token.grid(row=0, column=1, pady=5, padx=10)
        self._prefill_entry(self.square_token, self.config['SQUARE_ACCESS_TOKEN'])

        ttk.Label(input_frame, text="Square Location ID:").grid(row=1, column=0, sticky='w', pady=5)
        self.square_location = ttk.Entry(input_frame, width=40)
        self.square_location.grid(row=1, column=1, pady=5, padx=10)
        self._prefill_entry(self.square_location, self.config['SQUARE_LOCATION_ID'])

        # Navigation
        nav_frame = ttk.Frame(frame)
        nav_frame.pack(side='bottom', fill='x', pady=20)

        ttk.Button(nav_frame, text="Back", command=self.prev_page).pack(side='left')
        ttk.Button(nav_frame, text="Skip", command=self.next_page).pack(side='right', padx=5)
        ttk.Button(nav_frame, text="Next", command=self.next_page).pack(side='right')

        self.pages.append(frame)

    def create_ai_page(self):
        """Groq AI credentials page (optional)"""
        frame = ttk.Frame(self.root, padding="20")

        title = ttk.Label(frame, text="AI Features (Optional - FREE)",
                         font=('Arial', 16, 'bold'))
        title.pack(pady=10)

        desc = ttk.Label(frame, text="""
AI features provide intelligent insights, automated messaging,
and sales assistance. This uses Groq API which is FREE!

To get your Groq API key:
1. Go to https://console.groq.com/
2. Sign up or log in (free account)
3. Go to API Keys and create a new key
4. Copy and paste it below

This is optional - you can skip and add it later.
        """, justify='left', wraplength=600)
        desc.pack(pady=10)

        # Input fields
        input_frame = ttk.Frame(frame)
        input_frame.pack(pady=20, fill='x')

        ttk.Label(input_frame, text="Groq API Key:").grid(row=0, column=0, sticky='w', pady=5)
        self.groq_key = ttk.Entry(input_frame, width=40, show='*')
        self.groq_key.grid(row=0, column=1, pady=5, padx=10)
        self._prefill_entry(self.groq_key, self.config['GROQ_API_KEY'])

        # Navigation
        nav_frame = ttk.Frame(frame)
        nav_frame.pack(side='bottom', fill='x', pady=20)

        ttk.Button(nav_frame, text="Back", command=self.prev_page).pack(side='left')
        ttk.Button(nav_frame, text="Skip", command=self.next_page).pack(side='right', padx=5)
        ttk.Button(nav_frame, text="Next", command=self.next_page).pack(side='right')

        self.pages.append(frame)

    def create_summary_page(self):
        """Summary and final setup page"""
        frame = ttk.Frame(self.root, padding="20")

        title = ttk.Label(frame, text="Setup Complete!",
                         font=('Arial', 16, 'bold'))
        title.pack(pady=10)

        desc = ttk.Label(frame, text="Review your configuration below:",
                         justify='left')
        desc.pack(pady=10)

        # Summary text
        self.summary_text = scrolledtext.ScrolledText(frame, height=15, width=70)
        self.summary_text.pack(pady=10, fill='both', expand=True)
        self.summary_text.config(state='disabled')

        # Navigation
        nav_frame = ttk.Frame(frame)
        nav_frame.pack(side='bottom', fill='x', pady=20)

        ttk.Button(nav_frame, text="Back", command=self.prev_page).pack(side='left')
        ttk.Button(nav_frame, text="Save & Launch",
                  command=self.save_and_launch,
                  style='Accent.TButton').pack(side='right')

        self.pages.append(frame)

    def show_page(self, page_num):
        """Show specific page"""
        # Hide all pages
        for page in self.pages:
            page.pack_forget()

        # Show current page
        if page_num == len(self.pages) - 1:  # Summary page
            self.update_summary()

        self.pages[page_num].pack(fill='both', expand=True)
        self.current_page = page_num

    def next_page(self):
        """Go to next page"""
        # Save current page data
        if self.current_page == 1:  # ClubOS page
            self.config['CLUBOS_USERNAME'] = self.clubos_username.get()
            self.config['CLUBOS_PASSWORD'] = self.clubos_password.get()
        elif self.current_page == 2:  # ClubHub page
            self.config['CLUBHUB_EMAIL'] = self.clubhub_email.get()
            self.config['CLUBHUB_PASSWORD'] = self.clubhub_password.get()
        elif self.current_page == 3:  # Square page
            self.config['SQUARE_ACCESS_TOKEN'] = self.square_token.get()
            self.config['SQUARE_LOCATION_ID'] = self.square_location.get()
        elif self.current_page == 4:  # AI page
            self.config['GROQ_API_KEY'] = self.groq_key.get()

        if self.current_page < len(self.pages) - 1:
            self.show_page(self.current_page + 1)

    def prev_page(self):
        """Go to previous page"""
        if self.current_page > 0:
            self.show_page(self.current_page - 1)

    def test_clubos_connection(self):
        """Test ClubOS credentials using the real authentication flow"""
        username = self.clubos_username.get()
        password = self.clubos_password.get()

        if not username or not password:
            self.clubos_status.config(text="Please enter both username and password",
                                     foreground='red')
            return

        self.clubos_status.config(text="Testing ClubOS connection...", foreground='blue')
        self.root.update()

        def test_in_thread():
            try:
                from bs4 import BeautifulSoup

                # Use the REAL ClubOS authentication flow
                session = requests.Session()
                session.headers.update({
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
                })

                # Step 1: Get login page with CSRF tokens
                login_url = 'https://anytime.club-os.com/action/Login/view?__fsk=1221801756'
                login_response = session.get(login_url, verify=False, timeout=15)
                login_response.raise_for_status()

                soup = BeautifulSoup(login_response.text, 'html.parser')
                source_page = soup.find('input', {'name': '_sourcePage'})
                fp_token = soup.find('input', {'name': '__fp'})

                source_page_value = source_page.get('value') if source_page else ''
                fp_token_value = fp_token.get('value') if fp_token else ''

                # Step 2: Submit login form
                login_data = {
                    'login': 'Submit',
                    'username': username,
                    'password': password,
                    '_sourcePage': source_page_value,
                    '__fp': fp_token_value
                }

                auth_response = session.post(
                    'https://anytime.club-os.com/action/Login',
                    data=login_data,
                    headers={'Content-Type': 'application/x-www-form-urlencoded'},
                    allow_redirects=True,
                    verify=False,
                    timeout=15
                )

                # Check for successful login
                if session.cookies.get('JSESSIONID') and session.cookies.get('loggedInUserId'):
                    self.clubos_status.config(text="✓ ClubOS connection successful!",
                                             foreground='green')
                else:
                    self.clubos_status.config(text="✗ Invalid ClubOS credentials",
                                             foreground='red')

            except ImportError:
                self.clubos_status.config(text="✗ BeautifulSoup4 not installed - install with: pip install beautifulsoup4",
                                         foreground='red')
            except requests.exceptions.SSLError:
                self.clubos_status.config(text="✗ SSL error - check internet connection",
                                         foreground='red')
            except requests.exceptions.Timeout:
                self.clubos_status.config(text="✗ Connection timeout - check internet",
                                         foreground='red')
            except requests.exceptions.ConnectionError:
                self.clubos_status.config(text="✗ Cannot reach ClubOS server",
                                         foreground='red')
            except Exception as e:
                self.clubos_status.config(text=f"✗ Connection failed: {str(e)}",
                                         foreground='red')

        threading.Thread(target=test_in_thread, daemon=True).start()

    def test_clubhub_connection(self):
        """Test ClubHub credentials using the real ClubHub API"""
        email = self.clubhub_email.get().strip()
        password = self.clubhub_password.get()  # Don't strip password - may have intentional spaces
        
        # Debug log the credential lengths (not the values themselves)
        print(f"[DEBUG] ClubHub test - email length: {len(email)}, password length: {len(password)}")

        if not email or not password:
            self.clubhub_status.config(text="Please enter both email and password",
                                      foreground='red')
            return

        self.clubhub_status.config(text="Testing ClubHub connection...", foreground='blue')
        self.root.update()

        def update_status(text, color):
            """Thread-safe status update"""
            self.root.after(0, lambda: self.clubhub_status.config(text=text, foreground=color))

        def test_in_thread():
            try:
                print(f"[DEBUG] Starting ClubHub API test...")
                # Use the REAL ClubHub iOS API endpoint
                # IMPORTANT: The API expects 'username' not 'email' in the JSON body
                response = requests.post(
                    'https://clubhub-ios-api.anytimefitness.com/api/login',
                    json={
                        'username': email,  # ClubHub API uses 'username' field for email
                        'password': password
                    },
                    headers={
                        'Content-Type': 'application/json',
                        'API-version': '1',
                        'Accept': 'application/json',
                        'User-Agent': 'ClubHub Store/2.15.1 (com.anytimefitness.Club-Hub; build:1007; iOS 18.5.0) Alamofire/5.6.4'
                    },
                    timeout=15
                )
                
                print(f"[DEBUG] ClubHub API response status: {response.status_code}")
                print(f"[DEBUG] ClubHub API response body: {response.text[:200]}")

                if response.status_code == 200:
                    data = response.json()
                    # Check for accessToken (iOS API format) or token (alternate format)
                    if data.get('accessToken') or data.get('data', {}).get('token'):
                        update_status("✓ ClubHub connection successful!", 'green')
                    else:
                        print(f"[DEBUG] Response data keys: {list(data.keys())}")
                        update_status(f"✗ Invalid response (no token in response)", 'red')
                elif response.status_code == 401:
                    error_hint = ''
                    try:
                        error_json = response.json()
                        if isinstance(error_json, dict):
                            # Try to extract the detailed error message
                            exceptions = error_json.get('exceptions', [])
                            if exceptions and isinstance(exceptions, list):
                                for exc in exceptions:
                                    info = exc.get('info', {})
                                    if info.get('login'):
                                        error_hint = info.get('login')
                                        break
                            if not error_hint:
                                error_hint = error_json.get('message') or error_json.get('error') or ''
                    except ValueError:
                        error_hint = response.text[:80]

                    hint_suffix = f" ({error_hint})" if error_hint else ''
                    update_status("✗ Invalid ClubHub credentials" + hint_suffix, 'red')
                else:
                    update_status(f"✗ ClubHub error: {response.status_code}", 'red')

            except requests.exceptions.SSLError as e:
                update_status(f"✗ SSL error: {str(e)[:50]}", 'red')
            except requests.exceptions.Timeout:
                update_status("✗ Connection timeout - check internet", 'red')
            except requests.exceptions.ConnectionError as e:
                update_status(f"✗ Cannot reach server: {str(e)[:50]}", 'red')
            except Exception as e:
                update_status(f"✗ Error: {str(e)[:50]}", 'red')

        threading.Thread(target=test_in_thread, daemon=True).start()

    def update_summary(self):
        """Update summary page with configuration"""
        self.summary_text.config(state='normal')
        self.summary_text.delete(1.0, tk.END)

        summary = "Configuration Summary\n"
        summary += "=" * 50 + "\n\n"

        summary += "ClubOS Integration:\n"
        summary += f"  Username: {self.config['CLUBOS_USERNAME']}\n"
        summary += f"  Password: {'*' * len(self.config['CLUBOS_PASSWORD'])}\n"
        summary += f"  Status: {'Configured' if self.config['CLUBOS_USERNAME'] else 'Not configured'}\n\n"

        summary += "ClubHub Integration:\n"
        summary += f"  Email: {self.config['CLUBHUB_EMAIL']}\n"
        summary += f"  Password: {'*' * len(self.config['CLUBHUB_PASSWORD'])}\n"
        summary += f"  Status: {'Configured' if self.config['CLUBHUB_EMAIL'] else 'Not configured'}\n\n"

        summary += "Square Integration:\n"
        summary += f"  Access Token: {'*' * 20 if self.config['SQUARE_ACCESS_TOKEN'] else 'Not configured'}\n"
        summary += f"  Location ID: {self.config['SQUARE_LOCATION_ID'] or 'Not configured'}\n"
        summary += f"  Status: {'Configured' if self.config['SQUARE_ACCESS_TOKEN'] else 'Not configured'}\n\n"

        summary += "AI Features:\n"
        summary += f"  Groq API Key: {'*' * 20 if self.config['GROQ_API_KEY'] else 'Not configured'}\n"
        summary += f"  Status: {'Configured' if self.config['GROQ_API_KEY'] else 'Not configured'}\n\n"

        summary += "Configuration file path:\n"
        summary += f"  {self.env_path}\n\n"

        summary += "\n" + "=" * 50 + "\n"
        summary += "\nClick 'Save & Launch' to save this configuration and start Gym Bot."

        self.summary_text.insert(1.0, summary)
        self.summary_text.config(state='disabled')

    def save_and_launch(self):
        """Save configuration and close wizard"""
        # Generate secure Flask secret key
        import secrets
        if not self.config['FLASK_SECRET_KEY']:
            self.config['FLASK_SECRET_KEY'] = secrets.token_urlsafe(32)

        # Create .env file in persistent config directory
        env_path = self.env_path

        try:
            with open(env_path, 'w') as f:
                f.write("# Gym Bot Configuration\n")
                f.write("# Auto-generated by Setup Wizard\n\n")

                f.write("# Flask Configuration\n")
                f.write(f"FLASK_SECRET_KEY={self.config['FLASK_SECRET_KEY']}\n")
                f.write("FLASK_ENV=production\n\n")

                if self.config['CLUBOS_USERNAME']:
                    f.write("# ClubOS Integration\n")
                    f.write(f"CLUBOS_USERNAME={self.config['CLUBOS_USERNAME']}\n")
                    f.write(f"CLUBOS_PASSWORD={self.config['CLUBOS_PASSWORD']}\n\n")

                if self.config['CLUBHUB_EMAIL']:
                    f.write("# ClubHub Integration\n")
                    f.write(f"CLUBHUB_EMAIL={self.config['CLUBHUB_EMAIL']}\n")
                    f.write(f"CLUBHUB_PASSWORD={self.config['CLUBHUB_PASSWORD']}\n\n")

                if self.config['SQUARE_ACCESS_TOKEN']:
                    f.write("# Square Integration\n")
                    f.write(f"SQUARE_ACCESS_TOKEN={self.config['SQUARE_ACCESS_TOKEN']}\n")
                    f.write(f"SQUARE_LOCATION_ID={self.config['SQUARE_LOCATION_ID']}\n\n")

                if self.config['GROQ_API_KEY']:
                    f.write("# AI Features (Groq - FREE)\n")
                    f.write(f"GROQ_API_KEY={self.config['GROQ_API_KEY']}\n")
                    f.write("GROQ_MODEL=llama-3.3-70b-versatile\n\n")

            messagebox.showinfo("Success",
                              "Configuration saved successfully!\n\n"
                              "Gym Bot will now launch.")

            # Mark setup as complete
            self.setup_complete_path.touch()

            self.root.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save configuration:\n{str(e)}")

    def exit_wizard(self):
        """Exit wizard"""
        if messagebox.askyesno("Exit Setup",
                              "Are you sure you want to exit?\n\n"
                              "Gym Bot will not be configured."):
            sys.exit(0)

    def run(self):
        """Run the wizard"""
        self.root.mainloop()


def main():
    """Main entry point"""
    # Check if setup is already complete
    setup_complete = resolve_config_dir() / '.setup_complete'

    if setup_complete.exists():
        # Setup already done, skip wizard
        return True

    # Run setup wizard
    wizard = SetupWizard()
    wizard.run()

    return True


if __name__ == '__main__':
    main()
