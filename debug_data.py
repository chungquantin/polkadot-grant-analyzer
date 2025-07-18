#!/usr/bin/env python3
"""
Debug script to analyze grant data
"""

from database import GrantDatabase
import pandas as pd

def main():
    db = GrantDatabase()
    df = db.load_proposals()
    
    print("=== Data Analysis ===")
    print(f"Total proposals: {len(df)}")
    
    print("\n=== State Analysis ===")
    print(df['state'].value_counts())
    
    print("\n=== Merged Analysis ===")
    print(df['merged'].value_counts())
    
    print("\n=== Category Analysis ===")
    print(df['category'].value_counts())
    
    print("\n=== Sample Merged Proposals ===")
    merged = df[df['merged'] == True]
    print(f"Merged proposals: {len(merged)}")
    if len(merged) > 0:
        print(merged[['title', 'state', 'merged', 'category']].head())
    
    print("\n=== Sample Open Proposals ===")
    open_props = df[df['state'] == 'open']
    print(f"Open proposals: {len(open_props)}")
    if len(open_props) > 0:
        print(open_props[['title', 'state', 'merged', 'category']].head())
    
    print("\n=== Sample Closed Proposals ===")
    closed_props = df[df['state'] == 'closed']
    print(f"Closed proposals: {len(closed_props)}")
    if len(closed_props) > 0:
        print(closed_props[['title', 'state', 'merged', 'category']].head(5))
    
    # Check for any proposals with merged_at date
    print("\n=== Merged At Analysis ===")
    merged_at_props = df[df['merged_at'].notna()]
    print(f"Proposals with merged_at: {len(merged_at_props)}")
    if len(merged_at_props) > 0:
        print(merged_at_props[['title', 'state', 'merged', 'merged_at', 'category']].head())

if __name__ == "__main__":
    main() 