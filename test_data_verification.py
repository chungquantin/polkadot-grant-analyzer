#!/usr/bin/env python3
"""
Test script to verify test data was created correctly
"""

import pandas as pd
import json
import os

def test_data_verification():
    print("🔍 Verifying test data...")
    
    # Check if we have any data files
    data_files = [
        "grants_database.db",
        "2025-07-21T01-45_export.csv"
    ]
    
    for file in data_files:
        if os.path.exists(file):
            print(f"✅ Found data file: {file}")
        else:
            print(f"❌ Missing data file: {file}")
    
    # Try to load from CSV
    csv_file = "2025-07-21T01-45_export.csv"
    if os.path.exists(csv_file):
        print(f"\n📊 Loading data from {csv_file}...")
        df = pd.read_csv(csv_file)
        
        print(f"Total rows: {len(df)}")
        print(f"Columns: {list(df.columns)}")
        
        # Check for non-empty values
        print("\n=== Data Quality Check ===")
        for col in df.columns:
            non_empty = df[col].notna().sum()
            print(f"{col}: {non_empty}/{len(df)} non-empty values")
        
        # Check category distribution
        if 'category' in df.columns:
            print("\n=== Category Distribution ===")
            print(df['category'].value_counts())
        
        # Check author distribution
        if 'author' in df.columns:
            print("\n=== Author Distribution ===")
            print(df['author'].value_counts())
        
        # Check repository distribution
        if 'repository' in df.columns:
            print("\n=== Repository Distribution ===")
            print(df['repository'].value_counts())
    
    # Try to load from SQLite
    db_file = "grants_database.db"
    if os.path.exists(db_file):
        print(f"\n🗄️ Loading data from {db_file}...")
        try:
            import sqlite3
            with sqlite3.connect(db_file) as conn:
                # Check tables
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                print(f"Tables: {[table[0] for table in tables]}")
                
                # Check proposals table
                if ('proposals',) in tables:
                    cursor.execute("SELECT COUNT(*) FROM proposals")
                    count = cursor.fetchone()[0]
                    print(f"Proposals in database: {count}")
                    
                    if count > 0:
                        cursor.execute("SELECT * FROM proposals LIMIT 3")
                        rows = cursor.fetchall()
                        print("\n=== Sample Data ===")
                        for row in rows:
                            print(f"ID: {row[0]}, Title: {row[2]}, Author: {row[10]}")
                
        except Exception as e:
            print(f"❌ Error reading database: {e}")

if __name__ == "__main__":
    test_data_verification() 