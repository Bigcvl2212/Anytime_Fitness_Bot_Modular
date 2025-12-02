#!/usr/bin/env python3
"""
Gym Bot Desktop Launcher
Simple GUI to start/stop the Gym Bot server and open the dashboard
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import threading
import webbrowser
import socket
import time
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GymBotLauncher:
    def __init__(self):
        # Load version
        self.version = self.get_version()
        
        self.root = tk.Tk()
        self.root.title(f"Gym Bot Launcher v{self.version}")
        self.root.geometry("500x400")
        self.root.resizable(False, False)

        # Server process
        self.server_process = None
        self.log_handle = None  # Add log handle tracking
        self.is_running = False
        self.server_url = "http://localhost:5000"

        # Setup UI
        self.setup_ui()

        # Check for first-time setup
        self.check_first_time_setup()

        # Check if server is already running
        self.check_server_status()

    def get_version(self):
        """Get version from VERSION file"""
        try:
            version_file = Path(__file__).parent / 'VERSION'
            if version_file.exists():
                return version_file.read_text().strip()
        except:
            pass
        return "2.1.6"

    def setup_ui(self):
        """Setup the user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill='both', expand=True)

        # Title
        title = ttk.Label(main_frame, text="Gym Bot Dashboard",
                         font=('Arial', 20, 'bold'))
        title.pack(pady=20)

        # Logo/Image placeholder
        logo_frame = ttk.Frame(main_frame, width=100, height=100,
                              relief='solid', borderwidth=2)
        logo_frame.pack(pady=10)
        logo_label = ttk.Label(logo_frame, text="🏋️", font=('Arial', 48))
        logo_label.pack(expand=True)

        # Status frame
        status_frame = ttk.LabelFrame(main_frame, text="Server Status", padding="10")
        status_frame.pack(fill='x', pady=20)

        self.status_label = ttk.Label(status_frame, text="Server is stopped",
                                      font=('Arial', 12))
        self.status_label.pack()

        self.status_indicator = tk.Canvas(status_frame, width=20, height=20)
        self.status_indicator.pack(pady=5)
        self.status_circle = self.status_indicator.create_oval(2, 2, 18, 18,
                                                               fill='red')

        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=10)

        # Start button
        self.start_btn = ttk.Button(button_frame, text="Start Server",
                                    command=self.start_server,
                                    style='Success.TButton')
        self.start_btn.pack(side='left', padx=5, fill='x', expand=True)

        # Stop button
        self.stop_btn = ttk.Button(button_frame, text="Stop Server",
                                   command=self.stop_server,
                                   state='disabled')
        self.stop_btn.pack(side='left', padx=5, fill='x', expand=True)

        # Open browser button
        self.open_btn = ttk.Button(button_frame, text="Open Dashboard",
                                   command=self.open_browser,
                                   state='disabled')
        self.open_btn.pack(side='left', padx=5, fill='x', expand=True)

        # Additional options frame
        options_frame = ttk.Frame(main_frame)
        options_frame.pack(fill='x', pady=10)

        ttk.Button(options_frame, text="Settings",
                  command=self.open_settings).pack(side='left', padx=5)
        ttk.Button(options_frame, text="View Logs",
                  command=self.view_logs).pack(side='left', padx=5)
        ttk.Button(options_frame, text="Check Updates",
                  command=self.check_updates).pack(side='left', padx=5)
        ttk.Button(options_frame, text="Help",
                  command=self.show_help).pack(side='left', padx=5)

        # Exit button
        ttk.Button(main_frame, text="Exit",
                  command=self.exit_app).pack(side='bottom', pady=10)

        # Setup window close handler
        self.root.protocol("WM_DELETE_WINDOW", self.exit_app)

    def check_first_time_setup(self):
        """Check if first-time setup is needed"""
        setup_complete = Path(__file__).parent / '.setup_complete'
        env_file = Path(__file__).parent / '.env'

        if not setup_complete.exists() and not env_file.exists():
            # Run setup wizard
            if messagebox.askyesno("First Time Setup",
                                  "It looks like this is your first time running Gym Bot.\n\n"
                                  "Would you like to run the setup wizard?"):
                self.run_setup_wizard()

    def run_setup_wizard(self):
        """Run the setup wizard"""
        try:
            import setup_wizard
            setup_wizard.main()
        except Exception as e:
            messagebox.showerror("Setup Error",
                               f"Failed to run setup wizard:\n{str(e)}")

    def check_server_status(self):
        """Check if server is already running"""
        if self.is_port_in_use(5000):
            self.is_running = True
            self.update_ui_state(True)

    def is_port_in_use(self, port):
        """Check if a port is in use"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) == 0

    def start_server(self):
        """Start the Gym Bot server"""
        if self.is_running:
            messagebox.showinfo("Already Running",
                              "Server is already running!")
            return

        try:
            # Update status
            self.status_label.config(text="Starting server...")
            self.root.update()

            # Get the path to run_dashboard.py
            if getattr(sys, 'frozen', False):
                # Running as compiled executable
                # CRITICAL: run_dashboard.py is bundled in _MEIPASS
                app_dir = sys._MEIPASS
                run_script = Path(app_dir) / 'run_dashboard.py'
                
                # CRITICAL: When frozen, we CANNOT use subprocess to run Python scripts
                # PyInstaller doesn't expose python.exe - we must use the bundled exe with -m flag
                # OR import the module directly. We'll use direct import approach.
                python_exe = None  # Will use import instead
            else:
                # Running as script
                app_dir = Path(__file__).parent
                run_script = Path(app_dir) / 'run_dashboard.py'
                python_exe = sys.executable  # Normal Python interpreter

            # Create log file for server output in USER's writable directory
            # CRITICAL: C:\Program Files is read-only, must use user directory
            if getattr(sys, 'frozen', False):
                # Running as compiled executable - use user's AppData
                log_dir = Path.home() / 'AppData' / 'Local' / 'GymBot' / 'logs'
            else:
                # Running as script - use project directory
                log_dir = Path(app_dir) / 'logs'
            
            log_dir.mkdir(parents=True, exist_ok=True)
            log_file = log_dir / 'launcher_flask.log'
            
            # Open log file for writing with UTF-8 encoding (fixes Windows charmap issues)
            log_handle = open(log_file, 'w', encoding='utf-8', buffering=1)  # Line buffered

            # Start server
            if getattr(sys, 'frozen', False):
                # FROZEN MODE: Import and run Flask directly in background thread
                # CANNOT use subprocess because PyInstaller doesn't bundle python.exe
                logger.info(f"Starting Flask server in-process (frozen mode)... Logs at: {log_file}")
                
                # Store log handle
                self.log_handle = log_handle
                
                # Import and run Flask in background thread
                def run_flask():
                    try:
                        # Redirect stdout/stderr to log file
                        import io
                        old_stdout = sys.stdout
                        old_stderr = sys.stderr
                        
                        sys.stdout = log_handle
                        sys.stderr = log_handle
                        
                        # Change to app directory
                        original_cwd = os.getcwd()
                        
                        # CRITICAL: Add both sys._MEIPASS and project root to path
                        if app_dir not in sys.path:
                            sys.path.insert(0, str(app_dir))
                        
                        project_root = Path(app_dir).parent if not getattr(sys, 'frozen', False) else app_dir
                        if str(project_root) not in sys.path:
                            sys.path.insert(0, str(project_root))
                        
                        os.chdir(app_dir)
                        
                        try:
                            # Import Flask app directly
                            print("Importing Flask app from src.main_app...", flush=True)
                            from src.main_app import create_app
                            
                            print("Creating Flask app instance...", flush=True)
                            app = create_app()
                            
                            print("Starting Flask server on http://localhost:5000...", flush=True)
                            
                            # Run Flask with socketio if available
                            if hasattr(app, 'socketio') and app.socketio:
                                print("Starting Flask with SocketIO support...", flush=True)
                                app.socketio.run(app, host='0.0.0.0', port=5000, debug=False, use_reloader=False)
                            else:
                                print("Starting Flask without SocketIO...", flush=True)
                                app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
                            
                        except Exception as e:
                            print(f"❌ FATAL: Flask app failed to start: {e}", file=sys.stderr, flush=True)
                            import traceback
                            traceback.print_exc(file=sys.stderr)
                        finally:
                            # Restore stdout/stderr
                            sys.stdout = old_stdout
                            sys.stderr = old_stderr
                            os.chdir(original_cwd)
                            
                    except Exception as e:
                        print(f"❌ FATAL: Flask thread crashed: {e}", flush=True)
                        import traceback
                        traceback.print_exc()
                
                # Start Flask in daemon thread
                flask_thread = threading.Thread(target=run_flask, daemon=True)
                flask_thread.start()
                self.server_process = flask_thread  # Store thread reference
                
            else:
                # SCRIPT MODE: Use subprocess with python.exe
                if sys.platform == 'win32':
                    # Windows: hide console window but write to log file
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

                    self.server_process = subprocess.Popen(
                        [python_exe, str(run_script)],
                        stdout=log_handle,
                        stderr=subprocess.STDOUT,
                        startupinfo=startupinfo,
                        cwd=str(app_dir),
                        creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
                    )
                else:
                    # Unix/Mac
                    self.server_process = subprocess.Popen(
                        [python_exe, str(run_script)],
                        stdout=log_handle,
                        stderr=subprocess.STDOUT,
                        cwd=str(app_dir)
                    )
                
                # Store log handle
                self.log_handle = log_handle
                logger.info(f"Flask server starting via subprocess... Logs at: {log_file}")

            # Wait for server to start
            self.wait_for_server()

        except Exception as e:
            messagebox.showerror("Error",
                               f"Failed to start server:\n{str(e)}")
            self.status_label.config(text="Server failed to start")

    def wait_for_server(self):
        """Wait for server to be ready"""
        def check_server():
            max_attempts = 30
            for i in range(max_attempts):
                if self.is_port_in_use(5000):
                    self.is_running = True
                    self.update_ui_state(True)

                    # Auto-open browser
                    time.sleep(1)
                    self.open_browser()
                    return

                time.sleep(1)

            # Server didn't start
            self.status_label.config(text="Server failed to start")
            messagebox.showerror("Error",
                               "Server failed to start within 30 seconds.\n"
                               "Check the logs for more information.")

        threading.Thread(target=check_server, daemon=True).start()

    def stop_server(self):
        """Stop the Gym Bot server"""
        if not self.is_running:
            messagebox.showinfo("Not Running",
                              "Server is not running!")
            return

        if messagebox.askyesno("Stop Server",
                              "Are you sure you want to stop the server?"):
            try:
                if self.server_process:
                    # Check if it's a thread (frozen mode) or process (script mode)
                    if isinstance(self.server_process, threading.Thread):
                        # Frozen mode: Cannot gracefully stop daemon thread
                        # Best we can do is close the log and mark as stopped
                        # The thread will exit when the launcher exits
                        logger.warning("⚠️ Cannot stop Flask thread - will terminate when launcher exits")
                        logger.info("💡 To fully stop the server, close the launcher application")
                    else:
                        # Script mode: Terminate subprocess
                        self.server_process.terminate()
                        self.server_process.wait(timeout=5)
                
                # Close log file handle if it exists
                if hasattr(self, 'log_handle') and self.log_handle:
                    try:
                        self.log_handle.close()
                        self.log_handle = None
                    except:
                        pass

                self.is_running = False
                self.update_ui_state(False)

                if isinstance(self.server_process, threading.Thread):
                    messagebox.showinfo("Info", 
                                      "Server marked as stopped.\n\n"
                                      "Note: In frozen mode, the server thread will\n"
                                      "continue running until you close the launcher.")
                else:
                    messagebox.showinfo("Success", "Server stopped successfully")

            except Exception as e:
                messagebox.showerror("Error",
                                   f"Failed to stop server:\n{str(e)}")

    def update_ui_state(self, running):
        """Update UI based on server state"""
        if running:
            self.status_label.config(text="Server is running")
            self.status_indicator.itemconfig(self.status_circle, fill='green')
            self.start_btn.config(state='disabled')
            self.stop_btn.config(state='normal')
            self.open_btn.config(state='normal')
        else:
            self.status_label.config(text="Server is stopped")
            self.status_indicator.itemconfig(self.status_circle, fill='red')
            self.start_btn.config(state='normal')
            self.stop_btn.config(state='disabled')
            self.open_btn.config(state='disabled')

    def open_browser(self):
        """Open the dashboard in the default browser"""
        try:
            webbrowser.open(self.server_url)
        except Exception as e:
            messagebox.showerror("Error",
                               f"Failed to open browser:\n{str(e)}\n\n"
                               f"Please manually open: {self.server_url}")

    def open_settings(self):
        """Open settings (re-run setup wizard)"""
        if messagebox.askyesno("Settings",
                              "This will open the setup wizard to modify your settings.\n\n"
                              "Do you want to continue?"):
            # Delete setup complete marker
            setup_complete = Path(__file__).parent / '.setup_complete'
            if setup_complete.exists():
                setup_complete.unlink()

            self.run_setup_wizard()

    def view_logs(self):
        """Open log file"""
        # CRITICAL: Check user's AppData for compiled exe, project dir for script
        if getattr(sys, 'frozen', False):
            # Running as compiled executable - logs in user's AppData
            launcher_log = Path.home() / 'AppData' / 'Local' / 'GymBot' / 'logs' / 'launcher_flask.log'
            dashboard_log = Path.home() / 'AppData' / 'Local' / 'GymBot' / 'logs' / 'dashboard.log'
        else:
            # Running as script - logs in project directory
            launcher_log = Path(__file__).parent / 'logs' / 'launcher_flask.log'
            dashboard_log = Path(__file__).parent / 'logs' / 'dashboard.log'
        
        log_file = launcher_log if launcher_log.exists() else dashboard_log

        if not log_file.exists():
            messagebox.showinfo("No Logs",
                              "No log file found yet.\n"
                              "Logs will appear after the server has been started.")
            return

        try:
            if sys.platform == 'win32':
                os.startfile(str(log_file))
            elif sys.platform == 'darwin':
                subprocess.run(['open', str(log_file)])
            else:
                subprocess.run(['xdg-open', str(log_file)])
        except Exception as e:
            messagebox.showerror("Error",
                               f"Failed to open log file:\n{str(e)}")

    def show_help(self):
        """Show help information"""
        help_text = """
Gym Bot Dashboard - Quick Help

Starting the Server:
1. Click 'Start Server' to launch the dashboard
2. The browser will open automatically
3. Login with your admin credentials

Stopping the Server:
1. Click 'Stop Server' when you're done
2. Confirm the action

Settings:
- Click 'Settings' to modify your configuration
- You can update ClubOS, Square, and AI credentials

Logs:
- Click 'View Logs' to see server activity
- Useful for troubleshooting issues

For more help, visit the documentation or contact support.
        """

        messagebox.showinfo("Help", help_text)

    def check_updates(self):
        """Check for and apply updates from GitHub"""
        try:
            from src.utils.auto_updater import AutoUpdater
            
            # Show checking message
            self.status_label.config(text="Checking for updates...")
            self.root.update()
            
            updater = AutoUpdater()
            update_available, local_ver, remote_ver = updater.check_for_updates()
            
            if not update_available:
                messagebox.showinfo("Up to Date", 
                                   f"You have the latest version (v{local_ver})")
                self.status_label.config(text="Server is stopped" if not self.is_running else "Server is running")
                return
            
            # Ask user if they want to update
            if messagebox.askyesno("Update Available",
                                   f"A new version is available!\n\n"
                                   f"Current: v{local_ver}\n"
                                   f"Latest: v{remote_ver}\n\n"
                                   f"Do you want to update now?\n\n"
                                   f"Note: The server will be restarted if running."):
                
                # Stop server if running
                was_running = self.is_running
                if was_running:
                    self.stop_server()
                    time.sleep(2)
                
                # Show progress
                self.status_label.config(text="Downloading update...")
                self.root.update()
                
                # Perform update
                success, message = updater.perform_update()
                
                if success:
                    messagebox.showinfo("Update Complete", 
                                       f"{message}\n\nPlease restart the application.")
                    # Update version display
                    self.version = updater.get_local_version()
                    self.root.title(f"Gym Bot Launcher v{self.version}")
                else:
                    messagebox.showerror("Update Failed", message)
                
                # Restart server if it was running
                if was_running:
                    self.start_server()
                else:
                    self.status_label.config(text="Server is stopped")
            else:
                self.status_label.config(text="Server is stopped" if not self.is_running else "Server is running")
                
        except ImportError:
            messagebox.showerror("Error", 
                               "Auto-updater not available.\n"
                               "Please download the latest installer from GitHub.")
        except Exception as e:
            messagebox.showerror("Update Error", f"Failed to check for updates:\n{str(e)}")
            self.status_label.config(text="Server is stopped" if not self.is_running else "Server is running")

    def exit_app(self):
        """Exit the application"""
        if self.is_running:
            if messagebox.askyesno("Exit",
                                  "Server is still running.\n\n"
                                  "Do you want to stop the server and exit?"):
                try:
                    if self.server_process:
                        self.server_process.terminate()
                    # Close log file handle
                    if self.log_handle:
                        try:
                            self.log_handle.close()
                        except:
                            pass
                except:
                    pass
                self.root.destroy()
        else:
            self.root.destroy()

    def run(self):
        """Run the launcher"""
        self.root.mainloop()


def main():
    """Main entry point"""
    launcher = GymBotLauncher()
    launcher.run()


if __name__ == '__main__':
    main()
