#!/usr/bin/env python3
"""
Test script to verify the Polkadot Grant Analyzer setup
"""

import sys
import importlib
from pathlib import Path

def test_imports():
    """Test if all required modules can be imported"""
    print("🔍 Testing imports...")
    
    required_modules = [
        'requests',
        'pandas',
        'streamlit',
        'plotly',
        'dateutil',
        'matplotlib',
        'seaborn',
        'numpy',
        'dotenv'
    ]
    
    failed_imports = []
    
    for module in required_modules:
        try:
            importlib.import_module(module)
            print(f"  ✅ {module}")
        except ImportError as e:
            print(f"  ❌ {module}: {e}")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"\n❌ Failed to import: {', '.join(failed_imports)}")
        print("Please install missing dependencies with: pip install -r requirements.txt")
        return False
    
    print("✅ All imports successful!")
    return True

def test_local_modules():
    """Test if local modules can be imported"""
    print("\n🔍 Testing local modules...")
    
    local_modules = [
        'config',
        'github_client',
        'data_processor',
        'database'
    ]
    
    failed_imports = []
    
    for module in local_modules:
        try:
            importlib.import_module(module)
            print(f"  ✅ {module}")
        except ImportError as e:
            print(f"  ❌ {module}: {e}")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"\n❌ Failed to import local modules: {', '.join(failed_imports)}")
        return False
    
    print("✅ All local modules imported successfully!")
    return True

def test_configuration():
    """Test configuration loading"""
    print("\n🔍 Testing configuration...")
    
    try:
        from config import GRANT_REPOSITORIES, DATABASE_PATH
        print(f"  ✅ Configuration loaded")
        print(f"  📊 Configured repositories: {len(GRANT_REPOSITORIES)}")
        print(f"  💾 Database path: {DATABASE_PATH}")
        return True
    except Exception as e:
        print(f"  ❌ Configuration error: {e}")
        return False

def test_database():
    """Test database initialization"""
    print("\n🔍 Testing database...")
    
    try:
        from database import GrantDatabase
        db = GrantDatabase()
        print("  ✅ Database initialized successfully")
        return True
    except Exception as e:
        print(f"  ❌ Database error: {e}")
        return False

def test_github_client():
    """Test GitHub client initialization"""
    print("\n🔍 Testing GitHub client...")
    
    try:
        from github_client import GitHubClient
        client = GitHubClient()
        print("  ✅ GitHub client initialized")
        return True
    except Exception as e:
        print(f"  ❌ GitHub client error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Polkadot Grant Analyzer - Setup Test")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_local_modules,
        test_configuration,
        test_database,
        test_github_client
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your setup is ready.")
        print("\n📖 Next steps:")
        print("1. Set up your GitHub token in .env file (optional)")
        print("2. Run: streamlit run streamlit_app.py")
        print("3. Or run: python main.py fetch")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 