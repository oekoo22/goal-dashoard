#!/usr/bin/env python3
"""
Student Goal Dashboard - Main Entry Point

This is the main entry point for the Student Goal Dashboard application.
It provides a simple interface to run the Streamlit dashboard.

Usage:
    python main.py
    
Or run directly with streamlit:
    streamlit run gui.py
"""

import subprocess
import sys
import os
from pathlib import Path


def check_dependencies():
    """Check if required dependencies are installed."""
    required_packages = ['streamlit', 'plotly']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("Missing required packages:")
        for package in missing_packages:
            print(f"  - {package}")
        print("\nPlease install them using:")
        print(f"  pip install {' '.join(missing_packages)}")
        return False
    
    return True


def create_sample_data_if_needed():
    """Create sample data file if it doesn't exist."""
    if not os.path.exists('student_data.json'):
        print("Creating sample data...")
        try:
            from data import save_sample_data
            save_sample_data()
            print("Sample data created successfully!")
        except Exception as e:
            print(f"Error creating sample data: {e}")
            return False
    return True


def run_dashboard():
    """Run the Streamlit dashboard."""
    try:
        # Get the directory of this script
        script_dir = Path(__file__).parent
        gui_path = script_dir / "gui.py"
        
        # Run streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            str(gui_path),
            "--server.headless", "false",
            "--server.port", "8501",
            "--browser.gatherUsageStats", "false"
        ])
        
    except KeyboardInterrupt:
        print("\nDashboard stopped by user.")
    except Exception as e:
        print(f"Error running dashboard: {e}")
        return False
    
    return True


def main():
    """Main function to start the dashboard application."""
    print("🎓 Student Goal Dashboard")
    print("=" * 30)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Create sample data if needed
    if not create_sample_data_if_needed():
        sys.exit(1)
    
    print("Starting dashboard...")
    print("Dashboard will open in your browser automatically.")
    print("Press Ctrl+C to stop the dashboard.")
    print()
    
    # Run the dashboard
    if not run_dashboard():
        sys.exit(1)


if __name__ == "__main__":
    main()