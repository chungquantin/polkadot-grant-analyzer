#!/usr/bin/env python3
"""
Create simple sample data for testing
"""

from database import GrantDatabase
import pandas as pd
from datetime import datetime, timezone

def create_simple_sample():
    """Create simple sample data"""
    
    # Create sample DataFrame
    sample_data = [
        {
            'id': 1,
            'number': 2600,
            'title': 'Polkadot Ecosystem Analytics Platform',
            'description': 'A comprehensive analytics platform for the Polkadot ecosystem with real-time data visualization and reporting capabilities.',
            'author': 'alice_dev',
            'repository': 'w3f_grants',
            'repository_info': '{"owner": "w3f", "repo": "Grants-Program"}',
            'state': 'closed',
            'merged': True,
            'created_at': datetime(2025, 1, 15, 10, 0, 0, tzinfo=timezone.utc),
            'updated_at': datetime(2025, 1, 20, 15, 30, 0, tzinfo=timezone.utc),
            'closed_at': datetime(2025, 1, 25, 12, 0, 0, tzinfo=timezone.utc),
            'merged_at': datetime(2025, 1, 25, 12, 0, 0, tzinfo=timezone.utc),
            'milestones': 3,
            'curators': '["curator1", "curator2"]',
            'category': 'APPROVED',
            'approval_time_days': 10.0,
            'rejection_reason': None,
            'bounty_amount': 25000.0,
            'labels': '["approved", "infrastructure"]',
            'comments_count': 5,
            'reviews_count': 2,
            'additions': 150,
            'deletions': 10,
            'changed_files': 8,
            'created_date': datetime(2025, 1, 15).date(),
            'updated_date': datetime(2025, 1, 20).date()
        },
        {
            'id': 2,
            'number': 2599,
            'title': 'Substrate Runtime Development Tools',
            'description': 'Development tools and utilities for Substrate runtime development with improved debugging and testing capabilities.',
            'author': 'bob_developer',
            'repository': 'w3f_grants',
            'repository_info': '{"owner": "w3f", "repo": "Grants-Program"}',
            'state': 'closed',
            'merged': False,
            'created_at': datetime(2025, 1, 10, 9, 0, 0, tzinfo=timezone.utc),
            'updated_at': datetime(2025, 1, 15, 14, 20, 0, tzinfo=timezone.utc),
            'closed_at': datetime(2025, 1, 18, 11, 0, 0, tzinfo=timezone.utc),
            'merged_at': None,
            'milestones': 2,
            'curators': '["curator3"]',
            'category': 'REJECTED',
            'approval_time_days': 8.0,
            'rejection_reason': 'Insufficient technical details and unclear deliverables',
            'bounty_amount': 15000.0,
            'labels': '["rejected", "development"]',
            'comments_count': 3,
            'reviews_count': 1,
            'additions': 80,
            'deletions': 5,
            'changed_files': 4,
            'created_date': datetime(2025, 1, 10).date(),
            'updated_date': datetime(2025, 1, 15).date()
        },
        {
            'id': 3,
            'number': 2598,
            'title': 'Polkadot Community Education Initiative',
            'description': 'Educational content and workshops for the Polkadot community with focus on developer onboarding.',
            'author': 'carol_educator',
            'repository': 'w3f_grants',
            'repository_info': '{"owner": "w3f", "repo": "Grants-Program"}',
            'state': 'open',
            'merged': False,
            'created_at': datetime(2025, 1, 5, 8, 0, 0, tzinfo=timezone.utc),
            'updated_at': datetime(2025, 1, 20, 16, 45, 0, tzinfo=timezone.utc),
            'closed_at': None,
            'merged_at': None,
            'milestones': 4,
            'curators': '["curator1", "curator4"]',
            'category': 'PENDING',
            'approval_time_days': None,
            'rejection_reason': None,
            'bounty_amount': 30000.0,
            'labels': '["pending", "education"]',
            'comments_count': 7,
            'reviews_count': 3,
            'additions': 200,
            'deletions': 15,
            'changed_files': 12,
            'created_date': datetime(2025, 1, 5).date(),
            'updated_date': datetime(2025, 1, 20).date()
        },
        {
            'id': 4,
            'number': 100,
            'title': 'Quick Substrate Integration Tool',
            'description': 'A fast integration tool for Substrate-based projects with automated testing.',
            'author': 'dave_integrator',
            'repository': 'polkadot_fast_grants',
            'repository_info': '{"owner": "Polkadot-Fast-Grants", "repo": "apply"}',
            'state': 'closed',
            'merged': True,
            'created_at': datetime(2025, 1, 12, 11, 0, 0, tzinfo=timezone.utc),
            'updated_at': datetime(2025, 1, 14, 13, 20, 0, tzinfo=timezone.utc),
            'closed_at': datetime(2025, 1, 16, 10, 0, 0, tzinfo=timezone.utc),
            'merged_at': datetime(2025, 1, 16, 10, 0, 0, tzinfo=timezone.utc),
            'milestones': 2,
            'curators': '["fast_curator1"]',
            'category': 'APPROVED',
            'approval_time_days': 4.0,
            'rejection_reason': None,
            'bounty_amount': 8000.0,
            'labels': '["approved", "fast-track"]',
            'comments_count': 2,
            'reviews_count': 1,
            'additions': 60,
            'deletions': 3,
            'changed_files': 3,
            'created_date': datetime(2025, 1, 12).date(),
            'updated_date': datetime(2025, 1, 14).date()
        }
    ]
    
    # Create DataFrame
    df = pd.DataFrame(sample_data)
    
    # Save to database
    db = GrantDatabase()
    print("Saving sample data to database...")
    db.save_proposals(df)
    
    print("✅ Sample data created successfully!")
    
    # Show statistics
    print("\n=== Sample Data Statistics ===")
    print(f"Total proposals: {len(df)}")
    print(f"Approved: {len(df[df['category'] == 'APPROVED'])}")
    print(f"Rejected: {len(df[df['category'] == 'REJECTED'])}")
    print(f"Pending: {len(df[df['category'] == 'PENDING'])}")
    print(f"Stale: {len(df[df['category'] == 'STALE'])}")
    
    print("\n=== Repository Breakdown ===")
    print(df['repository'].value_counts())
    
    print("\n=== Category Breakdown ===")
    print(df['category'].value_counts())

if __name__ == "__main__":
    create_simple_sample() 