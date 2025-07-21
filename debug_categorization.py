#!/usr/bin/env python3
"""
Debug script to check data categorization issues
"""

from database import GrantDatabase
import pandas as pd

def debug_categorization():
    print("🔍 Debugging categorization issues...")
    
    # Load data
    db = GrantDatabase()
    df = db.load_proposals()
    
    if df.empty:
        print("❌ No data available")
        return
    
    print(f"📊 Loaded {len(df)} proposals")
    
    # Check data structure
    print("\n=== Data Structure ===")
    print("Columns:", list(df.columns))
    print("\nData types:")
    print(df.dtypes)
    
    # Check state distribution
    print("\n=== State Distribution ===")
    if 'state' in df.columns:
        print(df['state'].value_counts())
    else:
        print("❌ No 'state' column found")
    
    # Check merged_at distribution
    print("\n=== Merged At Distribution ===")
    if 'merged_at' in df.columns:
        merged_counts = df['merged_at'].notna().value_counts()
        print(f"Has merged_at: {merged_counts.get(True, 0)}")
        print(f"No merged_at: {merged_counts.get(False, 0)}")
        
        # Show some examples
        print("\nExamples with merged_at:")
        merged_examples = df[df['merged_at'].notna()].head(3)
        for _, row in merged_examples.iterrows():
            print(f"  - {row['title'][:50]}... (state: {row.get('state', 'N/A')})")
    else:
        print("❌ No 'merged_at' column found")
    
    # Check closed_at distribution
    print("\n=== Closed At Distribution ===")
    if 'closed_at' in df.columns:
        closed_counts = df['closed_at'].notna().value_counts()
        print(f"Has closed_at: {closed_counts.get(True, 0)}")
        print(f"No closed_at: {closed_counts.get(False, 0)}")
    else:
        print("❌ No 'closed_at' column found")
    
    # Check current category distribution
    print("\n=== Current Category Distribution ===")
    if 'category' in df.columns:
        print(df['category'].value_counts())
    else:
        print("❌ No 'category' column found")
    
    # Check for merged field
    print("\n=== Merged Field Check ===")
    if 'merged' in df.columns:
        merged_field_counts = df['merged'].value_counts()
        print(merged_field_counts)
        
        # Show examples of merged=True
        merged_true = df[df['merged'] == True]
        print(f"\nProposals with merged=True: {len(merged_true)}")
        for _, row in merged_true.head(3).iterrows():
            print(f"  - {row['title'][:50]}... (state: {row.get('state', 'N/A')})")
    else:
        print("❌ No 'merged' column found")
    
    # Check repository distribution
    print("\n=== Repository Distribution ===")
    if 'repository' in df.columns:
        print(df['repository'].value_counts())
    else:
        print("❌ No 'repository' column found")
    
    # Sample data for inspection
    print("\n=== Sample Data ===")
    sample = df.head(3)
    for _, row in sample.iterrows():
        print(f"\nTitle: {row.get('title', 'N/A')}")
        print(f"State: {row.get('state', 'N/A')}")
        print(f"Merged: {row.get('merged', 'N/A')}")
        print(f"Merged At: {row.get('merged_at', 'N/A')}")
        print(f"Closed At: {row.get('closed_at', 'N/A')}")
        print(f"Category: {row.get('category', 'N/A')}")
        print(f"Repository: {row.get('repository', 'N/A')}")

if __name__ == "__main__":
    debug_categorization() 