#!/usr/bin/env python3
"""
Example usage of the Polkadot Grant Analyzer API

This script demonstrates how to use the analyzer programmatically
for custom analysis and reporting.
"""

import pandas as pd
from datetime import datetime, timedelta
import json

from github_client import GitHubClient
from data_processor import GrantDataProcessor
from database import GrantDatabase

def example_basic_usage():
    """Example of basic usage - fetch and analyze data"""
    print("🔍 Example: Basic Usage")
    print("=" * 40)
    
    # Initialize components
    github_client = GitHubClient()
    data_processor = GrantDataProcessor()
    database = GrantDatabase()
    
    # Fetch data
    print("📥 Fetching grant proposals...")
    proposals = github_client.fetch_all_grant_proposals()
    
    # Process data
    print("⚙️ Processing proposals...")
    df = data_processor.process_all_proposals(proposals)
    
    # Save to database
    print("💾 Saving to database...")
    database.save_proposals(df)
    
    # Calculate metrics
    print("📊 Calculating metrics...")
    metrics = data_processor.calculate_performance_metrics(df)
    database.save_metrics(metrics)
    
    print(f"✅ Processed {len(df)} proposals")
    return df, metrics

def example_analysis_queries(df):
    """Example of various analysis queries"""
    print("\n🔍 Example: Analysis Queries")
    print("=" * 40)
    
    # 1. Top authors by number of proposals
    print("\n1. Top 5 authors by number of proposals:")
    top_authors = df['author'].value_counts().head(5)
    for author, count in top_authors.items():
        print(f"   {author}: {count} proposals")
    
    # 2. Approval rates by repository
    print("\n2. Approval rates by repository:")
    for repo in df['repository'].unique():
        repo_data = df[df['repository'] == repo]
        approved = len(repo_data[repo_data['merged'] == True])
        total = len(repo_data)
        rate = (approved / total) * 100 if total > 0 else 0
        print(f"   {repo}: {rate:.1f}% ({approved}/{total})")
    
    # 3. Average approval time
    approval_times = df[df['approval_time_days'].notna()]['approval_time_days']
    if len(approval_times) > 0:
        avg_time = approval_times.mean()
        print(f"\n3. Average approval time: {avg_time:.1f} days")
    
    # 4. Proposals with milestones
    milestone_proposals = df[df['milestones'] > 0]
    print(f"\n4. Proposals with milestones: {len(milestone_proposals)}")
    
    # 5. Recent proposals (last 30 days)
    recent_date = datetime.now() - timedelta(days=30)
    recent_proposals = df[df['created_at'] >= recent_date]
    print(f"\n5. Recent proposals (last 30 days): {len(recent_proposals)}")

def example_custom_analysis(df):
    """Example of custom analysis"""
    print("\n🔍 Example: Custom Analysis")
    print("=" * 40)
    
    # Find proposals with high bounty amounts
    high_bounty = df[df['bounty_amount'] > 10000]  # > $10k
    if len(high_bounty) > 0:
        print(f"\nHigh-value proposals (>$10k): {len(high_bounty)}")
        for _, proposal in high_bounty.head(3).iterrows():
            print(f"   {proposal['title']}: ${proposal['bounty_amount']:,.0f}")
    
    # Find proposals that took long to approve
    long_approval = df[df['approval_time_days'] > 30]  # > 30 days
    if len(long_approval) > 0:
        print(f"\nProposals with long approval times (>30 days): {len(long_approval)}")
        for _, proposal in long_approval.head(3).iterrows():
            print(f"   {proposal['title']}: {proposal['approval_time_days']:.1f} days")
    
    # Find rejected proposals with reasons
    rejected = df[df['category'] == 'REJECTED']
    rejected_with_reasons = rejected[rejected['rejection_reason'].notna()]
    print(f"\nRejected proposals with reasons: {len(rejected_with_reasons)}")
    for _, proposal in rejected_with_reasons.head(2).iterrows():
        reason = proposal['rejection_reason'][:100] + "..." if len(proposal['rejection_reason']) > 100 else proposal['rejection_reason']
        print(f"   {proposal['title']}: {reason}")

def example_export_data(df):
    """Example of exporting data in different formats"""
    print("\n🔍 Example: Data Export")
    print("=" * 40)
    
    # Export to CSV
    csv_file = "grants_export.csv"
    df.to_csv(csv_file, index=False)
    print(f"✅ Exported to CSV: {csv_file}")
    
    # Export summary to JSON
    summary = {
        "total_proposals": len(df),
        "approved": len(df[df['merged'] == True]),
        "rejected": len(df[df['category'] == 'REJECTED']),
        "unique_authors": df['author'].nunique(),
        "date_range": {
            "earliest": df['created_at'].min().isoformat(),
            "latest": df['created_at'].max().isoformat()
        }
    }
    
    json_file = "grants_summary.json"
    with open(json_file, 'w') as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"✅ Exported summary to JSON: {json_file}")
    
    # Export specific data
    approved_proposals = df[df['merged'] == True][['title', 'author', 'repository', 'bounty_amount']]
    approved_file = "approved_grants.csv"
    approved_proposals.to_csv(approved_file, index=False)
    print(f"✅ Exported approved proposals to: {approved_file}")

def example_database_queries():
    """Example of database queries"""
    print("\n🔍 Example: Database Queries")
    print("=" * 40)
    
    database = GrantDatabase()
    
    # Load data from database
    df = database.load_proposals()
    
    if df.empty:
        print("No data in database. Run example_basic_usage() first.")
        return
    
    # Query by repository
    w3f_proposals = database.get_proposals_by_repository("w3f_grants")
    print(f"W3F proposals: {len(w3f_proposals)}")
    
    # Query by category
    rejected_proposals = database.get_proposals_by_category("REJECTED")
    print(f"Rejected proposals: {len(rejected_proposals)}")
    
    # Get statistics
    stats = database.get_statistics()
    print(f"Database statistics: {stats}")

def main():
    """Run all examples"""
    print("🚀 Polkadot Grant Analyzer - Example Usage")
    print("=" * 60)
    
    try:
        # Basic usage
        df, metrics = example_basic_usage()
        
        # Analysis queries
        example_analysis_queries(df)
        
        # Custom analysis
        example_custom_analysis(df)
        
        # Export data
        example_export_data(df)
        
        # Database queries
        example_database_queries()
        
        print("\n🎉 All examples completed successfully!")
        print("\n📁 Generated files:")
        print("- grants_export.csv")
        print("- grants_summary.json")
        print("- approved_grants.csv")
        
    except Exception as e:
        print(f"❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 