#!/usr/bin/env python3
"""
Quick Start Script for Polkadot Grant Analyzer

This script guides users through the initial setup and helps them get started quickly.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def check_dependencies():
    """Check if required dependencies are installed"""
    print("\n🔍 Checking dependencies...")
    
    try:
        import requests
        import pandas
        import streamlit
        import plotly
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def setup_environment():
    """Set up environment file if it doesn't exist"""
    env_file = Path(".env")
    
    if not env_file.exists():
        print("\n🔧 Setting up environment file...")
        
        env_content = """# GitHub API Configuration
# Get your token from: https://github.com/settings/tokens
# Required permissions: repo, public_repo
GITHUB_TOKEN=your_github_token_here

# Database Configuration (optional)
# DATABASE_PATH=grants_database.db

# Logging Configuration (optional)
# LOG_LEVEL=INFO
"""
        
        with open(env_file, 'w') as f:
            f.write(env_content)
        
        print("✅ Created .env file")
        print("📝 Please edit .env file and add your GitHub token (optional)")
    else:
        print("✅ .env file already exists")

def run_test_setup():
    """Run the test setup script"""
    print("\n🧪 Running setup tests...")
    
    try:
        result = subprocess.run([sys.executable, "test_setup.py"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Setup tests passed")
            return True
        else:
            print("❌ Setup tests failed")
            print(result.stdout)
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False

def fetch_initial_data():
    """Fetch initial data from GitHub"""
    print("\n📥 Fetching initial data...")
    
    try:
        result = subprocess.run([sys.executable, "main.py", "fetch"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Data fetched successfully")
            print(result.stdout)
            return True
        else:
            print("❌ Error fetching data")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def show_next_steps():
    """Show next steps to the user"""
    print("\n🎉 Setup complete!")
    print("\n📖 Next steps:")
    print("1. 🖥️  Start the dashboard:")
    print("   streamlit run streamlit_app.py")
    print("\n2. 📊 View statistics:")
    print("   python main.py stats")
    print("\n3. 📄 Generate a report:")
    print("   python main.py report --output report.json")
    print("\n4. 🔄 Refresh data:")
    print("   python main.py fetch")
    print("\n5. 🧹 Clear database:")
    print("   python main.py clear")
    
    print("\n💡 Tips:")
    print("- Add your GitHub token to .env file for better rate limits")
    print("- The dashboard will open automatically in your browser")
    print("- Data is stored in grants_database.db")

def main():
    """Main quick start function"""
    print("🚀 Polkadot Grant Analyzer - Quick Start")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        print("\n📦 Installing dependencies...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                         check=True)
            print("✅ Dependencies installed")
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies")
            sys.exit(1)
    
    # Setup environment
    setup_environment()
    
    # Run tests
    if not run_test_setup():
        print("❌ Setup tests failed. Please check the errors above.")
        sys.exit(1)
    
    # Ask user if they want to fetch data
    print("\n🤔 Would you like to fetch initial data now? (y/n)")
    response = input().lower().strip()
    
    if response in ['y', 'yes']:
        fetch_initial_data()
    
    # Show next steps
    show_next_steps()

if __name__ == "__main__":
    main() 