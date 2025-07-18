#!/usr/bin/env python3
"""
Add stale proposals to test the stale detection feature
"""

from database import GrantDatabase
import pandas as pd
from datetime import datetime, timezone, timedelta

def add_stale_proposals():
    """Add stale proposals to the database"""
    
    # Load existing data
    db = GrantDatabase()
    existing_df = db.load_proposals()
    
    # Create stale proposals (over 60 days old and still open)
    stale_date = datetime.now() - timedelta(days=70)  # 70 days ago
    
    stale_proposals = [
        {
            'id': 5,
            'number': 2597,
            'title': 'Old Stale Proposal - Substrate Integration',
            'description': 'This is a proposal that has been sitting for over 60 days without any updates.',
            'author': 'stale_developer',
            'repository': 'w3f_grants',
            'repository_info': '{"owner": "w3f", "repo": "Grants-Program"}',
            'state': 'open',
            'merged': False,
            'created_at': stale_date.replace(tzinfo=timezone.utc),
            'updated_at': stale_date.replace(tzinfo=timezone.utc),
            'closed_at': None,
            'merged_at': None,
            'milestones': 2,
            'curators': '["curator1"]',
            'category': 'STALE',
            'approval_time_days': None,
            'rejection_reason': None,
            'bounty_amount': 12000.0,
            'labels': '["stale", "development"]',
            'comments_count': 1,
            'reviews_count': 0,
            'additions': 30,
            'deletions': 2,
            'changed_files': 2,
            'created_date': stale_date.date(),
            'updated_date': stale_date.date()
        },
        {
            'id': 6,
            'number': 2596,
            'title': 'Another Stale Proposal - Documentation',
            'description': 'Another proposal that has been pending for too long without curator attention.',
            'author': 'another_stale_dev',
            'repository': 'polkadot_fast_grants',
            'repository_info': '{"owner": "Polkadot-Fast-Grants", "repo": "apply"}',
            'state': 'open',
            'merged': False,
            'created_at': (stale_date - timedelta(days=10)).replace(tzinfo=timezone.utc),
            'updated_at': (stale_date - timedelta(days=10)).replace(tzinfo=timezone.utc),
            'closed_at': None,
            'merged_at': None,
            'milestones': 1,
            'curators': '["fast_curator1"]',
            'category': 'STALE',
            'approval_time_days': None,
            'rejection_reason': None,
            'bounty_amount': 5000.0,
            'labels': '["stale", "documentation"]',
            'comments_count': 0,
            'reviews_count': 0,
            'additions': 15,
            'deletions': 1,
            'changed_files': 1,
            'created_date': (stale_date - timedelta(days=10)).date(),
            'updated_date': (stale_date - timedelta(days=10)).date()
        }
    ]
    
    # Create DataFrame for stale proposals
    stale_df = pd.DataFrame(stale_proposals)
    
    # Combine with existing data
    combined_df = pd.concat([existing_df, stale_df], ignore_index=True)
    
    # Save to database
    print("Adding stale proposals to database...")
    db.save_proposals(combined_df)
    
    # Recalculate metrics
    from data_processor import GrantDataProcessor
    processor = GrantDataProcessor()
    metrics = processor.calculate_performance_metrics(combined_df)
    db.save_metrics(metrics)
    
    print("✅ Stale proposals added successfully!")
    
    # Show updated statistics
    print("\n=== Updated Statistics ===")
    print(f"Total proposals: {len(combined_df)}")
    print(f"Approved: {len(combined_df[combined_df['category'] == 'APPROVED'])}")
    print(f"Rejected: {len(combined_df[combined_df['category'] == 'REJECTED'])}")
    print(f"Pending: {len(combined_df[combined_df['category'] == 'PENDING'])}")
    print(f"Stale: {len(combined_df[combined_df['category'] == 'STALE'])}")
    
    print("\n=== Category Breakdown ===")
    print(combined_df['category'].value_counts())

if __name__ == "__main__":
    add_stale_proposals() 