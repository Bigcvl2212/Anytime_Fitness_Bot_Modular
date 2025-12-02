import PyInstaller.__main__
import shutil
import os
import sys
import datetime

def _handle_remove_readonly(func, path, exc_info):
    """Allow shutil.rmtree to remove read-only files on Windows."""
    import stat
    exc_type, _, _ = exc_info
    if exc_type is PermissionError:
        os.chmod(path, stat.S_IWRITE)
        func(path)


def clean_build_artifacts():
    """Remove previous build artifacts to ensure a clean build."""
    dirs_to_remove = ['build', 'dist', '__pycache__']
    for d in dirs_to_remove:
        if os.path.exists(d):
            print(f"Removing {d}...")
            shutil.rmtree(d, onerror=_handle_remove_readonly)
    
    # Remove any .spec files
    for f in os.listdir('.'):
        if f.endswith('.spec'):
            print(f"Removing {f}...")
            os.remove(f)

def build():
    print("Starting clean build process...")
    clean_build_artifacts()

    # Define build timestamp
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"Build timestamp: {timestamp}")

    # Create a version file to be included
    with open("build_info.txt", "w") as f:
        f.write(f"Build Time: {timestamp}\n")
        f.write("Entry Point: gymbot_main.py\n")

    # PyInstaller arguments
    args = [
        'gymbot_main.py',  # Entry point
        '--name=GymBot',
        '--onedir',        # Directory based (easier to debug than onefile)
        '--console',       # Keep console for now for debugging
        '--clean',         # Clean PyInstaller cache
        '--noconfirm',
        
        # Data files
        '--add-data=templates;templates',
        '--add-data=static;static',
        '--add-data=VERSION;.',
        '--add-data=build_info.txt;.',
        
        # Hidden imports (explicitly list common Flask/SocketIO deps)
        '--hidden-import=flask',
        '--hidden-import=flask_socketio',
        '--hidden-import=engineio.async_drivers.threading',
        '--hidden-import=jinja2',
        '--hidden-import=engineio',
        '--hidden-import=socketio',
        
        # Excludes to save space
        '--exclude-module=matplotlib',
        '--exclude-module=scipy',
        '--exclude-module=numpy',
        '--exclude-module=pandas',
    ]

    # Add config folder if it exists
    if os.path.exists('config'):
        args.append('--add-data=config;config')
    
    # Add src folder if it exists
    if os.path.exists('src'):
        args.append('--add-data=src;src')

    print(f"Running PyInstaller with args: {args}")
    
    try:
        PyInstaller.__main__.run(args)
        print("PyInstaller finished successfully.")
    except Exception as e:
        print(f"PyInstaller failed: {e}")
        sys.exit(1)

    # Verify output
    exe_path = os.path.join('dist', 'GymBot', 'GymBot.exe')
    if os.path.exists(exe_path):
        print(f"SUCCESS: Executable found at {exe_path}")
    else:
        print(f"FAILURE: Executable not found at {exe_path}")
        sys.exit(1)

if __name__ == "__main__":
    build()
