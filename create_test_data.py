#!/usr/bin/env python3
"""
Create test data with proper values for testing the dashboard
"""

from database import GrantDatabase
import pandas as pd
from datetime import datetime, timedelta
import random
import json

def create_test_data():
    print("🔧 Creating test data with proper values...")
    
    # Create test proposals with realistic data
    test_proposals = []
    
    # Sample repositories
    repositories = ['w3f_grants', 'polkadot_fast_grants', 'use_inkubator', 'polkadot_open_source']
    
    # Sample authors
    authors = ['alice', 'bob', 'charlie', 'diana', 'eve', 'frank', 'grace', 'henry']
    
    # Sample curators
    curators = ['curator1', 'curator2', 'curator3', 'curator4', 'curator5']
    
    # Categories with realistic distribution
    categories = ['APPROVED'] * 8 + ['REJECTED'] * 12 + ['PENDING'] * 5 + ['STALE'] * 2
    
    for i in range(27):  # 27 proposals total
        # Random repository
        repo = random.choice(repositories)
        
        # Random author
        author = random.choice(authors)
        
        # Random category
        category = random.choice(categories)
        
        # Random creation date (within last 200 days)
        days_ago = random.randint(1, 200)
        created_at = datetime.now() - timedelta(days=days_ago)
        
        # Calculate approval time based on category
        if category == 'APPROVED':
            approval_time = random.randint(1, 45)
            merged_at = created_at + timedelta(days=approval_time)
            closed_at = merged_at
            state = 'closed'
        elif category == 'REJECTED':
            approval_time = random.randint(1, 30)
            closed_at = created_at + timedelta(days=approval_time)
            merged_at = None
            state = 'closed'
        elif category == 'PENDING':
            approval_time = None
            merged_at = None
            closed_at = None
            state = 'open'
        else:  # STALE
            approval_time = None
            merged_at = None
            closed_at = None
            state = 'open'
        
        # Random curators (1-3 curators per proposal)
        num_curators = random.randint(1, 3)
        proposal_curators = random.sample(curators, num_curators)
        
        # Random metrics
        comments_count = random.randint(0, 20)
        review_comments_count = random.randint(0, 15)
        commits_count = random.randint(0, 10)
        additions_count = random.randint(0, 1000)
        deletions_count = random.randint(0, 500)
        changed_files_count = random.randint(1, 20)
        
        # Calculate performance score
        performance_score = 0
        if category == 'APPROVED':
            performance_score += 10
        if approval_time and approval_time < 30:
            performance_score += 5
        performance_score += min(comments_count / 10, 5)
        performance_score += min(review_comments_count / 5, 5)
        performance_score += min(commits_count / 5, 5)
        performance_score += min((additions_count + deletions_count) / 100, 5)
        
        # Create proposal
        proposal = {
            'id': 1000000 + i,
            'number': 1000 + i,
            'title': f'Test Proposal {i+1} - {category}',
            'body': f'This is a test proposal for {category} category. It has {comments_count} comments and {commits_count} commits.',
            'state': state,
            'created_at': created_at,
            'updated_at': created_at + timedelta(days=random.randint(0, 10)),
            'closed_at': closed_at,
            'merged_at': merged_at,
            'repository': repo,
            'author': author,
            'author_id': 1000 + i,
            'labels': ['test', category.lower()],
            'milestone': 'Test Milestone' if random.random() > 0.7 else '',
            'comments_count': comments_count,
            'review_comments_count': review_comments_count,
            'commits_count': commits_count,
            'additions_count': additions_count,
            'deletions_count': deletions_count,
            'changed_files_count': changed_files_count,
            'curators': proposal_curators,
            'comments': [],  # Empty for now
            'reviews': [],   # Empty for now
            'category': category,
            'approval_time_days': approval_time,
            'performance_score': performance_score,
            'is_stale': category == 'STALE'
        }
        
        test_proposals.append(proposal)
    
    # Create DataFrame
    df = pd.DataFrame(test_proposals)
    
    # Save to database
    db = GrantDatabase()
    print("💾 Saving test data to database...")
    
    # Convert DataFrame to the format expected by cloud storage
    proposals_dict = {}
    for _, row in df.iterrows():
        repo = row['repository']
        if repo not in proposals_dict:
            proposals_dict[repo] = []
        
        # Convert row to dict
        proposal_dict = row.to_dict()
        proposals_dict[repo].append(proposal_dict)
    
    db.save_proposals(proposals_dict)
    
    # Calculate and save metrics
    from data_processor import GrantDataProcessor
    processor = GrantDataProcessor()
    summary_stats = processor.get_summary_stats(df)
    program_stats = processor.get_program_stats(df)
    curator_stats = processor.get_curator_stats(df)
    
    metrics = {
        'summary_stats': summary_stats,
        'program_stats': program_stats,
        'curator_stats': curator_stats
    }
    db.save_metrics(metrics)
    
    print("✅ Test data created successfully!")
    
    # Show statistics
    print("\n=== Test Data Statistics ===")
    print(f"Total proposals: {len(df)}")
    print(f"Approved: {len(df[df['category'] == 'APPROVED'])}")
    print(f"Rejected: {len(df[df['category'] == 'REJECTED'])}")
    print(f"Pending: {len(df[df['category'] == 'PENDING'])}")
    print(f"Stale: {len(df[df['category'] == 'STALE'])}")
    
    print("\n=== Repository Breakdown ===")
    print(df['repository'].value_counts())
    
    print("\n=== Category Breakdown ===")
    print(df['category'].value_counts())
    
    print("\n=== Author Breakdown ===")
    print(df['author'].value_counts())
    
    print("\n=== Approval Rate ===")
    approval_rate = len(df[df['category'] == 'APPROVED']) / len(df) * 100
    print(f"Overall approval rate: {approval_rate:.1f}%")

if __name__ == "__main__":
    create_test_data() 