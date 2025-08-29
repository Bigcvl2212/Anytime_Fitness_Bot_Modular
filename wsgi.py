import os
import sys

# Ensure the 'src' directory is on sys.path so 'app.*' imports resolve
ROOT_DIR = os.path.dirname(__file__)
SRC_DIR = os.path.join(ROOT_DIR, 'src')
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

# Change to src directory to ensure proper imports
os.chdir(SRC_DIR)

# Import the Flask app directly from the top-level module to avoid circular imports
from clean_dashboard import app

if __name__ == "__main__":
    app.run()
