#!/usr/bin/env python3
"""
Test script to verify deployment setup
"""

import os
import sys

def test_imports():
    """Test all imports work correctly"""
    print("🔍 Testing imports...")
    
    try:
        import streamlit as st
        print("✅ streamlit imported successfully")
    except ImportError as e:
        print(f"❌ streamlit import failed: {e}")
        return False
    
    try:
        import pandas as pd
        print("✅ pandas imported successfully")
    except ImportError as e:
        print(f"❌ pandas import failed: {e}")
        return False
    
    try:
        import plotly.express as px
        print("✅ plotly imported successfully")
    except ImportError as e:
        print(f"❌ plotly import failed: {e}")
        return False
    
    try:
        from github_client import GitHubClient
        print("✅ github_client imported successfully")
    except ImportError as e:
        print(f"❌ github_client import failed: {e}")
        return False
    
    try:
        from data_processor import GrantDataProcessor
        print("✅ data_processor imported successfully")
    except ImportError as e:
        print(f"❌ data_processor import failed: {e}")
        return False
    
    try:
        from database import GrantDatabase
        print("✅ database imported successfully")
    except ImportError as e:
        print(f"❌ database import failed: {e}")
        return False
    
    try:
        from ai_evaluator import AIEvaluator
        print("✅ ai_evaluator imported successfully")
    except ImportError as e:
        print(f"❌ ai_evaluator import failed: {e}")
        return False
    
    try:
        from config import GRANT_REPOSITORIES, STREAMLIT_CONFIG
        print("✅ config imported successfully")
    except ImportError as e:
        print(f"⚠️  config import failed (using fallbacks): {e}")
    
    return True

def test_environment():
    """Test environment variables"""
    print("\n🔍 Testing environment variables...")
    
    github_token = os.getenv('GITHUB_TOKEN')
    if github_token:
        print("✅ GITHUB_TOKEN is set")
    else:
        print("⚠️  GITHUB_TOKEN not set (some features may not work)")
    
    openai_key = os.getenv('OPENAI_API_KEY')
    if openai_key:
        print("✅ OPENAI_API_KEY is set")
    else:
        print("⚠️  OPENAI_API_KEY not set (AI features will be disabled)")
    
    return True

def test_database():
    """Test database functionality"""
    print("\n🔍 Testing database...")
    
    try:
        from database import GrantDatabase
        db = GrantDatabase()
        info = db.get_database_info()
        print(f"✅ Database initialized successfully")
        print(f"   Tables: {info.get('tables', [])}")
        print(f"   Proposals: {info.get('proposals_count', 0)}")
        print(f"   Metrics: {info.get('metrics_count', 0)}")
        print(f"   Size: {info.get('database_size_mb', 0):.2f} MB")
        return True
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_components():
    """Test component initialization"""
    print("\n🔍 Testing component initialization...")
    
    try:
        from github_client import GitHubClient
        from data_processor import GrantDataProcessor
        from database import GrantDatabase
        from ai_evaluator import AIEvaluator
        
        github_client = GitHubClient()
        data_processor = GrantDataProcessor()
        database = GrantDatabase()
        ai_evaluator = AIEvaluator()
        
        print("✅ All components initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Component initialization failed: {e}")
        return False

def test_streamlit_config():
    """Test Streamlit configuration"""
    print("\n🔍 Testing Streamlit configuration...")
    
    try:
        import streamlit as st
        from config import STREAMLIT_CONFIG
        
        print(f"✅ Streamlit config loaded:")
        print(f"   Page title: {STREAMLIT_CONFIG.get('page_title', 'N/A')}")
        print(f"   Page icon: {STREAMLIT_CONFIG.get('page_icon', 'N/A')}")
        print(f"   Layout: {STREAMLIT_CONFIG.get('layout', 'N/A')}")
        return True
    except Exception as e:
        print(f"❌ Streamlit config test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Polkadot Grant Analyzer - Deployment Test")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_environment,
        test_database,
        test_components,
        test_streamlit_config
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Deployment should work correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 