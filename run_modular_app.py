#!/usr/bin/env python3
"""
Run the modular Cell Development Platform
"""

import subprocess
import sys
import os

def main():
    """Run the modular Streamlit app"""
    app_path = os.path.join(os.path.dirname(__file__), "app.py")
    
    print("🚀 Starting Cell Development Platform (Modular Version)")
    print(f"📁 App path: {app_path}")
    print("🌐 Opening in browser...")
    
    try:
        # Run the modular app
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", app_path,
            "--server.port", "8501",
            "--server.address", "localhost",
            "--browser.gatherUsageStats", "false"
        ], check=True)
    except KeyboardInterrupt:
        print("\n👋 Shutting down Cell Development Platform")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running app: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
