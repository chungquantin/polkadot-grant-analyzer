#!/usr/bin/env python3
"""
Create sample data for testing the new features
"""

from database import GrantDatabase
from data_processor import GrantDataProcessor
import pandas as pd
from datetime import datetime, timedelta
import random

def create_sample_data():
    """Create sample grant proposal data"""
    
    # Sample proposals
    sample_proposals = {
        'w3f_grants': [
            {
                'id': 1,
                'number': 2600,
                'title': 'Polkadot Ecosystem Analytics Platform',
                'description': 'A comprehensive analytics platform for the Polkadot ecosystem with real-time data visualization and reporting capabilities.',
                'author': 'alice_dev',
                'repository': 'w3f_grants',
                'repository_info': {'owner': 'w3f', 'repo': 'Grants-Program'},
                'state': 'closed',
                'merged': True,
                'created_at': '2025-01-15T10:00:00Z',
                'updated_at': '2025-01-20T15:30:00Z',
                'closed_at': '2025-01-25T12:00:00Z',
                'merged_at': '2025-01-25T12:00:00Z',
                'milestones': 3,
                'curators': ['curator1', 'curator2'],
                'category': 'APPROVED',
                'approval_time_days': 10.0,
                'rejection_reason': None,
                'bounty_amount': 25000.0,
                'labels': ['approved', 'infrastructure'],
                'comments_count': 5,
                'reviews_count': 2,
                'additions': 150,
                'deletions': 10,
                'changed_files': 8
            },
            {
                'id': 2,
                'number': 2599,
                'title': 'Substrate Runtime Development Tools',
                'description': 'Development tools and utilities for Substrate runtime development with improved debugging and testing capabilities.',
                'author': 'bob_developer',
                'repository': 'w3f_grants',
                'repository_info': {'owner': 'w3f', 'repo': 'Grants-Program'},
                'state': 'closed',
                'merged': False,
                'created_at': '2025-01-10T09:00:00Z',
                'updated_at': '2025-01-15T14:20:00Z',
                'closed_at': '2025-01-18T11:00:00Z',
                'merged_at': None,
                'milestones': 2,
                'curators': ['curator3'],
                'category': 'REJECTED',
                'approval_time_days': 8.0,
                'rejection_reason': 'Insufficient technical details and unclear deliverables',
                'bounty_amount': 15000.0,
                'labels': ['rejected', 'development'],
                'comments_count': 3,
                'reviews_count': 1,
                'additions': 80,
                'deletions': 5,
                'changed_files': 4
            },
            {
                'id': 3,
                'number': 2598,
                'title': 'Polkadot Community Education Initiative',
                'description': 'Educational content and workshops for the Polkadot community with focus on developer onboarding.',
                'author': 'carol_educator',
                'repository': 'w3f_grants',
                'repository_info': {'owner': 'w3f', 'repo': 'Grants-Program'},
                'state': 'open',
                'merged': False,
                'created_at': '2025-01-05T08:00:00Z',
                'updated_at': '2025-01-20T16:45:00Z',
                'closed_at': None,
                'merged_at': None,
                'milestones': 4,
                'curators': ['curator1', 'curator4'],
                'category': 'PENDING',
                'approval_time_days': None,
                'rejection_reason': None,
                'bounty_amount': 30000.0,
                'labels': ['pending', 'education'],
                'comments_count': 7,
                'reviews_count': 3,
                'additions': 200,
                'deletions': 15,
                'changed_files': 12
            }
        ],
        'polkadot_fast_grants': [
            {
                'id': 4,
                'number': 100,
                'title': 'Quick Substrate Integration Tool',
                'description': 'A fast integration tool for Substrate-based projects with automated testing.',
                'author': 'dave_integrator',
                'repository': 'polkadot_fast_grants',
                'repository_info': {'owner': 'Polkadot-Fast-Grants', 'repo': 'apply'},
                'state': 'closed',
                'merged': True,
                'created_at': '2025-01-12T11:00:00Z',
                'updated_at': '2025-01-14T13:20:00Z',
                'closed_at': '2025-01-16T10:00:00Z',
                'merged_at': '2025-01-16T10:00:00Z',
                'milestones': 2,
                'curators': ['fast_curator1'],
                'category': 'APPROVED',
                'approval_time_days': 4.0,
                'rejection_reason': None,
                'bounty_amount': 8000.0,
                'labels': ['approved', 'fast-track'],
                'comments_count': 2,
                'reviews_count': 1,
                'additions': 60,
                'deletions': 3,
                'changed_files': 3
            }
        ]
    }
    
    # Create data processor
    processor = GrantDataProcessor()
    
    # Process the sample data
    print("Processing sample data...")
    df = processor.process_all_proposals(sample_proposals)
    
    # Save to database
    db = GrantDatabase()
    print("Saving to database...")
    db.save_proposals(df)
    
    # Calculate metrics
    print("Calculating metrics...")
    metrics = processor.calculate_performance_metrics(df)
    db.save_metrics(metrics)
    
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
    create_sample_data() 