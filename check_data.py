#!/usr/bin/env python3

from database import GrantDatabase
import pandas as pd
import json

def check_database():
    db = GrantDatabase()
    df = db.load_proposals()
    
    print("=== DATABASE CHECK ===")
    print(f"Total rows: {len(df)}")
    print(f"Columns: {df.columns.tolist()}")
    
    if len(df) > 0:
        print("\n=== SAMPLE DATA ===")
        if 'author' in df.columns:
            print("Authors found:", df['author'].unique()[:5])
            print("Author value counts:", df['author'].value_counts().head())
        else:
            print("❌ NO AUTHOR COLUMN")
            
        if 'curators' in df.columns:
            print("Curators sample:", df['curators'].head(3))
            # Check if curators are lists or strings
            print("Curators type:", type(df['curators'].iloc[0]))
            print("Curators sample raw:", df['curators'].iloc[0])
        else:
            print("❌ NO CURATORS COLUMN")
        
        # Check a specific row in detail
        print("\n=== DETAILED SAMPLE ROW ===")
        sample_row = df.iloc[0]
        print("Title:", sample_row['title'])
        print("Author:", sample_row.get('author', 'N/A'))
        print("Curators:", sample_row.get('curators', 'N/A'))
        print("Repository:", sample_row.get('repository', 'N/A'))
        print("State:", sample_row.get('state', 'N/A'))
        
        # Check if we have user information
        if 'user' in df.columns:
            print("User column found:", df['user'].head(3))
        else:
            print("No 'user' column found")
            
    else:
        print("❌ NO DATA IN DATABASE")

if __name__ == "__main__":
    check_database() 