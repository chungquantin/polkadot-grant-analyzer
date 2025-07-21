#!/usr/bin/env python3

from database import GrantDatabase
import pandas as pd

def test_data_loading():
    print("🔍 Testing data loading...")
    
    # Initialize database
    db = GrantDatabase()
    
    # Debug: Check which storage method is being used
    print(f"🔧 Cloud storage available: {db.cloud_storage is not None}")
    print(f"🔧 Database path: {db.db_path}")
    
    # Force SQLite usage for testing
    if db.cloud_storage:
        print("🔄 Temporarily disabling cloud storage to test SQLite...")
        db.cloud_storage = None
    
    # Try to load data
    try:
        df = db.load_proposals()
        print(f"✅ Data loaded successfully!")
        print(f"📊 DataFrame shape: {df.shape}")
        print(f"📋 Columns: {list(df.columns)}")
        
        if not df.empty:
            print(f"📈 Total proposals: {len(df)}")
            print(f"👤 Unique authors: {df['author'].nunique()}")
            print(f"🏢 Unique repositories: {df['repository'].nunique()}")
            print(f"📊 Categories: {df['category'].value_counts().to_dict()}")
            
            # Show first few rows
            print("\n📋 First 3 proposals:")
            print(df[['id', 'title', 'author', 'category', 'repository']].head(3))
            
            # Check for common columns that might be missing
            expected_columns = ['milestone', 'performance_score', 'approval_time_days', 'is_stale']
            print("\n🔍 Checking for expected columns:")
            for col in expected_columns:
                if col in df.columns:
                    print(f"✅ {col} column exists")
                else:
                    print(f"❌ {col} column missing")
            
            # Check for milestone column specifically
            if 'milestone' in df.columns:
                print(f"✅ Milestone column exists with {df['milestone'].notna().sum()} non-null values")
            elif 'milestones' in df.columns:
                print(f"✅ Milestones column exists with {df['milestones'].notna().sum()} non-null values")
            else:
                print("❌ Neither milestone nor milestones column exists")
                print("Available columns:", list(df.columns))
        else:
            print("❌ DataFrame is empty!")
            
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_data_loading() 