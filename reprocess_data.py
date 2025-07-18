#!/usr/bin/env python3
"""
Reprocess existing data with new categorization logic
"""

from database import GrantDatabase
from data_processor import GrantDataProcessor
import pandas as pd

def main():
    print("Reprocessing existing data with new categorization...")
    
    # Load existing data
    db = GrantDatabase()
    df = db.load_proposals()
    
    if df.empty:
        print("No data to reprocess")
        return
    
    print(f"Loaded {len(df)} proposals")
    
    # Create data processor
    processor = GrantDataProcessor()
    
    # Convert DataFrame back to list of dicts for reprocessing
    proposals_dict = {}
    for repo in df['repository'].unique():
        repo_data = df[df['repository'] == repo]
        proposals_dict[repo] = repo_data.to_dict('records')
    
    # Reprocess with new categorization
    print("Reprocessing proposals...")
    new_df = processor.process_all_proposals(proposals_dict)
    
    # Save reprocessed data
    print("Saving reprocessed data...")
    db.save_proposals(new_df)
    
    # Calculate new metrics
    print("Calculating new metrics...")
    metrics = processor.calculate_performance_metrics(new_df)
    db.save_metrics(metrics)
    
    print("✅ Data reprocessed successfully!")
    
    # Show new statistics
    print("\n=== New Statistics ===")
    print(f"Total proposals: {len(new_df)}")
    print(f"Approved: {len(new_df[new_df['category'] == 'APPROVED'])}")
    print(f"Rejected: {len(new_df[new_df['category'] == 'REJECTED'])}")
    print(f"Pending: {len(new_df[new_df['category'] == 'PENDING'])}")
    print(f"Stale: {len(new_df[new_df['category'] == 'STALE'])}")
    
    print("\n=== Category Breakdown ===")
    print(new_df['category'].value_counts())

if __name__ == "__main__":
    main() 