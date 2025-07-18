#!/usr/bin/env python3
"""
Polkadot Grant Analyzer - Main Script

This script provides a command-line interface for running the grant analysis pipeline.
It can fetch data, process proposals, and generate reports without the Streamlit interface.
"""

import argparse
import logging
import sys
from datetime import datetime
import json

from github_client import GitHubClient
from data_processor import GrantDataProcessor
from database import GrantDatabase
from config import GRANT_REPOSITORIES

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def fetch_data(force_refresh=False):
    """Fetch grant proposals from all repositories"""
    logger.info("Starting data fetch...")
    
    github_client = GitHubClient()
    data_processor = GrantDataProcessor()
    database = GrantDatabase()
    
    try:
        # Fetch proposals
        proposals = github_client.fetch_all_grant_proposals()
        
        # Process data
        df = data_processor.process_all_proposals(proposals)
        
        # Save to database
        database.save_proposals(df)
        
        # Calculate metrics
        metrics = data_processor.calculate_performance_metrics(df)
        database.save_metrics(metrics)
        
        logger.info(f"Successfully processed {len(df)} proposals")
        return df, metrics
        
    except Exception as e:
        logger.error(f"Error fetching data: {e}")
        raise

def generate_report(df, metrics, output_file=None):
    """Generate a comprehensive report"""
    logger.info("Generating report...")
    
    report = {
        "generated_at": datetime.now().isoformat(),
        "summary": {
            "total_proposals": len(df),
            "approved_proposals": len(df[df['merged'] == True]),
            "rejected_proposals": len(df[df['category'] == 'REJECTED']),
            "pending_proposals": len(df[df['category'] == 'PENDING']),
            "unique_authors": df['author'].nunique(),
            "unique_curators": metrics.get('unique_curators', 0)
        },
        "performance_metrics": metrics,
        "repository_breakdown": df['repository'].value_counts().to_dict(),
        "category_breakdown": df['category'].value_counts().to_dict(),
        "top_authors": df['author'].value_counts().head(10).to_dict(),
        "approval_time_stats": {
            "mean": df['approval_time_days'].mean(),
            "median": df['approval_time_days'].median(),
            "min": df['approval_time_days'].min(),
            "max": df['approval_time_days'].max()
        } if df['approval_time_days'].notna().any() else {}
    }
    
    if output_file:
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        logger.info(f"Report saved to {output_file}")
    else:
        print(json.dumps(report, indent=2, default=str))
    
    return report

def show_statistics():
    """Show basic statistics from the database"""
    database = GrantDatabase()
    
    try:
        df = database.load_proposals()
        metrics = database.load_metrics()
        
        if df.empty:
            print("No data available. Run 'fetch' command first.")
            return
        
        print(f"\n📊 Polkadot Grant Statistics")
        print(f"{'='*50}")
        print(f"Total Proposals: {len(df)}")
        print(f"Approved: {len(df[df['category'] == 'APPROVED'])}")
        print(f"Rejected: {len(df[df['category'] == 'REJECTED'])}")
        print(f"Pending: {len(df[df['category'] == 'PENDING'])}")
        print(f"Stale: {len(df[df['category'] == 'STALE'])}")
        print(f"Unique Authors: {df['author'].nunique()}")
        print(f"Unique Curators: {metrics.get('unique_curators', 0)}")
        
        if 'approval_rate' in metrics:
            print(f"Approval Rate: {metrics['approval_rate']:.1%}")
        
        if 'avg_approval_time_days' in metrics:
            print(f"Avg Approval Time: {metrics['avg_approval_time_days']:.1f} days")
        
        print(f"\nRepository Breakdown:")
        for repo, count in df['repository'].value_counts().items():
            print(f"  {repo}: {count}")
        
        print(f"\nCategory Breakdown:")
        for category, count in df['category'].value_counts().items():
            print(f"  {category}: {count}")
            
    except Exception as e:
        logger.error(f"Error showing statistics: {e}")

def main():
    parser = argparse.ArgumentParser(description="Polkadot Grant Analyzer")
    parser.add_argument('command', choices=['fetch', 'report', 'stats', 'clear'],
                       help='Command to execute')
    parser.add_argument('--output', '-o', help='Output file for report')
    parser.add_argument('--force', '-f', action='store_true', 
                       help='Force refresh data even if recent data exists')
    
    args = parser.parse_args()
    
    try:
        if args.command == 'fetch':
            df, metrics = fetch_data(force_refresh=args.force)
            print(f"✅ Successfully fetched and processed {len(df)} proposals")
            
        elif args.command == 'report':
            database = GrantDatabase()
            df = database.load_proposals()
            metrics = database.load_metrics()
            
            if df.empty:
                print("No data available. Run 'fetch' command first.")
                return
            
            generate_report(df, metrics, args.output)
            
        elif args.command == 'stats':
            show_statistics()
            
        elif args.command == 'clear':
            database = GrantDatabase()
            database.clear_database()
            print("✅ Database cleared")
            
    except Exception as e:
        logger.error(f"Error executing command: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 