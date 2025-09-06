#!/usr/bin/env python3
"""
Cell Development App Launcher
Run this script to start the Streamlit application
"""

import subprocess
import sys
import os

def main():
    """Launch the Cell Development App"""
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    app_file = os.path.join(script_dir, "cell_development_app.py")
    
    # Check if the app file exists
    if not os.path.exists(app_file):
        print(f"Error: {app_file} not found!")
        sys.exit(1)
    
    # Launch Streamlit
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            app_file, "--server.port", "8501", "--server.address", "0.0.0.0"
        ])
    except KeyboardInterrupt:
        print("\nApp stopped by user")
    except Exception as e:
        print(f"Error launching app: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
