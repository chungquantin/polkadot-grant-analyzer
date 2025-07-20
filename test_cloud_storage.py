#!/usr/bin/env python3
"""
Test script to verify cloud storage functionality
"""

import streamlit as st
import pandas as pd
import json
from datetime import datetime

def test_cloud_storage():
    """Test cloud storage functionality"""
    print("🧪 Testing Cloud Storage System")
    print("=" * 40)
    
    try:
        from cloud_storage import CloudStorage
        
        # Initialize cloud storage
        storage = CloudStorage()
        print("✅ Cloud storage initialized successfully")
        
        # Test data
        test_proposals = {
            "test_repo": [
                {
                    "id": 1,
                    "number": 1,
                    "title": "Test Proposal",
                    "body": "This is a test proposal",
                    "state": "open",
                    "created_at": "2024-01-01T00:00:00Z",
                    "updated_at": "2024-01-01T00:00:00Z",
                    "closed_at": None,
                    "merged_at": None,
                    "user": {"login": "testuser", "id": 123},
                    "labels": [],
                    "milestone": None,
                    "comments": [],
                    "reviews": [],
                    "comments_count": 0,
                    "review_comments_count": 0,
                    "commits_count": 0,
                    "additions_count": 0,
                    "deletions_count": 0,
                    "changed_files_count": 0,
                    "curators": [],
                    "category": "PENDING",
                    "approval_time_days": None,
                    "performance_score": 0.0,
                    "is_stale": False
                }
            ]
        }
        
        # Test saving
        print("📝 Testing save functionality...")
        success = storage.save_proposals(test_proposals)
        if success:
            print("✅ Save test passed")
        else:
            print("❌ Save test failed")
            return False
        
        # Test loading
        print("📖 Testing load functionality...")
        df = storage.load_proposals()
        if not df.empty and len(df) == 1:
            print("✅ Load test passed")
            print(f"   Loaded {len(df)} proposals")
        else:
            print("❌ Load test failed")
            return False
        
        # Test metrics
        print("📊 Testing metrics functionality...")
        test_metrics = {
            "total_proposals": 1,
            "approved_proposals": 0,
            "test_metric": "test_value"
        }
        
        success = storage.save_metrics(test_metrics)
        if success:
            print("✅ Metrics save test passed")
        else:
            print("❌ Metrics save test failed")
            return False
        
        loaded_metrics = storage.load_metrics()
        if loaded_metrics and "total_proposals" in loaded_metrics:
            print("✅ Metrics load test passed")
        else:
            print("❌ Metrics load test failed")
            return False
        
        # Test storage info
        print("ℹ️  Testing storage info...")
        info = storage.get_storage_info()
        if info and "proposals_count" in info:
            print("✅ Storage info test passed")
            print(f"   Proposals: {info.get('proposals_count', 0)}")
            print(f"   Metrics: {info.get('metrics_count', 0)}")
        else:
            print("❌ Storage info test failed")
            return False
        
        # Test data presence
        print("🔍 Testing data presence...")
        if storage.has_data():
            print("✅ Data presence test passed")
        else:
            print("❌ Data presence test failed")
            return False
        
        # Test clearing
        print("🗑️  Testing clear functionality...")
        success = storage.clear_storage()
        if success:
            print("✅ Clear test passed")
        else:
            print("❌ Clear test failed")
            return False
        
        # Verify cleared
        if not storage.has_data():
            print("✅ Clear verification passed")
        else:
            print("❌ Clear verification failed")
            return False
        
        print("\n🎉 All cloud storage tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Cloud storage test failed with error: {e}")
        return False

def test_database_integration():
    """Test database integration with cloud storage"""
    print("\n🧪 Testing Database Integration")
    print("=" * 40)
    
    try:
        from database import GrantDatabase
        
        # Initialize database (should use cloud storage if available)
        db = GrantDatabase()
        print("✅ Database initialized successfully")
        
        # Test storage info
        info = db.get_database_info()
        print(f"✅ Storage info retrieved: {info.get('storage_type', 'Unknown')}")
        
        # Test data presence
        has_data = db.has_data()
        print(f"✅ Data presence check: {has_data}")
        
        print("🎉 Database integration test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Database integration test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Cloud Storage Test Suite")
    print("=" * 50)
    
    tests = [
        test_cloud_storage,
        test_database_integration
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
        print("🎉 All tests passed! Cloud storage is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 