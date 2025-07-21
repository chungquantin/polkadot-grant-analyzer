#!/usr/bin/env python3

from github_client import GitHubClient
from data_processor import GrantDataProcessor
from database import GrantDatabase
import logging

logging.basicConfig(level=logging.INFO)

def refresh_data():
    print("🔄 Starting data refresh...")
    
    # Initialize components
    github_client = GitHubClient()
    data_processor = GrantDataProcessor()
    database = GrantDatabase()
    
    try:
        # Step 1: Fetch data from GitHub
        print("📥 Fetching proposals from GitHub...")
        proposals = github_client.fetch_all_grant_proposals()
        
        # Process the data
        print("🔧 Processing proposals...")
        df = data_processor.process_proposals(proposals)
        
        # Save to database
        print("💾 Saving to database...")
        database.save_proposals(df)
        
        # Calculate and save metrics
        print("📊 Calculating metrics...")
        summary_stats = data_processor.get_summary_stats(df)
        program_stats = data_processor.get_program_stats(df)
        curator_stats = data_processor.get_curator_stats(df)
        
        metrics = {
            'summary_stats': summary_stats,
            'program_stats': program_stats,
            'curator_stats': curator_stats
        }
        database.save_metrics(metrics)
        
        print("✅ Data refresh completed!")
        print(f"📈 Total proposals: {len(df)}")
        
        # Check author and curator data
        if len(df) > 0:
            authors = df['author'].unique()
            print(f"👤 Unique authors: {len(authors)}")
            print(f"Sample authors: {list(authors[:5])}")
            
            all_curators = []
            for curators in df['curators']:
                if isinstance(curators, list):
                    all_curators.extend(curators)
            
            unique_curators = set(all_curators)
            print(f"👥 Unique curators: {len(unique_curators)}")
            print(f"Sample curators: {list(unique_curators)[:5]}")
        
    except Exception as e:
        print(f"❌ Error refreshing data: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    refresh_data() 