import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os

# Try to import config, with fallbacks
try:
    from config import CATEGORIES
except ImportError:
    # Fallback values if config module is not available
    CATEGORIES = {
        "ADMIN-REVIEW": "Under administrative review",
        "PENDING": "Pending approval",
        "REJECTED": "Rejected proposals",
        "APPROVED": "Approved proposals",
        "STALE": "Stale proposals (over 60 days old)",
        "CLOSED": "Closed without merging"
    }

class GrantDataProcessor:
    def __init__(self):
        self.categories = CATEGORIES
    
    def process_proposals(self, proposals_data: dict) -> pd.DataFrame:
        """Process raw proposals data into a structured DataFrame"""
        processed_data = []
        
        for repo_key, proposals in proposals_data.items():
            for proposal in proposals:
                processed_proposal = self._process_single_proposal(proposal, repo_key)
                if processed_proposal:
                    processed_data.append(processed_proposal)
        
        df = pd.DataFrame(processed_data)
        
        if not df.empty:
            # Convert date columns
            date_columns = ['created_at', 'updated_at', 'closed_at', 'merged_at']
            for col in date_columns:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
            
            # Calculate additional metrics
            df = self._calculate_metrics(df)
        
        return df
    
    def _process_single_proposal(self, proposal: dict, repo_key: str) -> dict:
        """Process a single proposal"""
        try:
            # Basic proposal info
            processed = {
                'id': proposal.get('id'),
                'number': proposal.get('number'),
                'title': proposal.get('title', ''),
                'body': proposal.get('body', ''),
                'state': proposal.get('state', ''),
                'created_at': proposal.get('created_at'),
                'updated_at': proposal.get('updated_at'),
                'closed_at': proposal.get('closed_at'),
                'merged_at': proposal.get('merged_at'),
                'repository': repo_key,
                'author': proposal.get('user', {}).get('login', 'Unknown'),
                'author_id': proposal.get('user', {}).get('id'),
                'labels': self._extract_labels(proposal),
                'milestone': proposal.get('milestone', {}).get('title', ''),
                'comments_count': proposal.get('comments', 0),
                'review_comments_count': proposal.get('review_comments', 0),
                'commits_count': proposal.get('commits', 0),
                'additions_count': proposal.get('additions', 0),
                'deletions_count': proposal.get('deletions', 0),
                'changed_files_count': proposal.get('changed_files', 0),
                'curators': self._extract_curators(proposal),
                'comments': proposal.get('comments', []),
                'reviews': proposal.get('reviews', [])
            }
            
            return processed
        except Exception as e:
            print(f"Error processing proposal {proposal.get('id', 'unknown')}: {e}")
            return None
    
    def _extract_labels(self, proposal: dict) -> list:
        """Extract labels from proposal"""
        labels = proposal.get('labels', [])
        return [label.get('name', '') for label in labels if label.get('name')]
    
    def _extract_curators(self, proposal: dict) -> list:
        """Extract curators from comments and reviews"""
        curators = set()
        
        # Extract from comments
        comments = proposal.get('comments', [])
        for comment in comments:
            user = comment.get('user', {})
            if user and user.get('login'):
                curators.add(user.get('login'))
        
        # Extract from reviews
        reviews = proposal.get('reviews', [])
        for review in reviews:
            user = review.get('user', {})
            if user and user.get('login'):
                curators.add(user.get('login'))
        
        return list(curators)
    
    def _calculate_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate additional metrics for the DataFrame"""
        if df.empty:
            return df
        
        # Calculate approval time
        df['approval_time_days'] = self._calculate_approval_time(df)
        
        # Determine category
        df['category'] = df.apply(self._categorize_proposal, axis=1)
        
        # Calculate performance metrics
        df['performance_score'] = self._calculate_performance_score(df)
        
        # Add stale detection
        df['is_stale'] = self._detect_stale_proposals(df)
        
        return df
    
    def _calculate_approval_time(self, df: pd.DataFrame) -> pd.Series:
        """Calculate approval time in days"""
        def calculate_time(row):
            if pd.notna(row.get('merged_at')):
                created = pd.to_datetime(row.get('created_at'))
                merged = pd.to_datetime(row.get('merged_at'))
                return (merged - created).days
            return None
        
        return df.apply(calculate_time, axis=1)
    
    def _categorize_proposal(self, row) -> str:
        """Categorize a proposal based on its state and characteristics"""
        state = row.get('state', '').lower()
        merged_at = row.get('merged_at')
        closed_at = row.get('closed_at')
        
        if pd.notna(merged_at):
            return 'APPROVED'
        elif state == 'closed' and pd.notna(closed_at):
            return 'REJECTED'
        elif state == 'open':
            # Check if stale
            created_at = pd.to_datetime(row.get('created_at'))
            if pd.notna(created_at):
                days_open = (datetime.now() - created_at).days
                if days_open > 60:
                    return 'STALE'
            return 'PENDING'
        else:
            return 'CLOSED'
    
    def _calculate_performance_score(self, df: pd.DataFrame) -> pd.Series:
        """Calculate a performance score based on various metrics"""
        score = pd.Series(0.0, index=df.index)
        
        # Base score for approved proposals
        score += (df['category'] == 'APPROVED').astype(int) * 10
        
        # Bonus for quick approval
        approval_time = df['approval_time_days']
        score += ((approval_time < 30) & (approval_time > 0)).astype(int) * 5
        
        # Bonus for engagement (comments, reviews)
        score += np.minimum(df['comments_count'] / 10, 5)
        score += np.minimum(df['review_comments_count'] / 5, 5)
        
        # Bonus for activity (commits, changes)
        score += np.minimum(df['commits_count'] / 5, 5)
        score += np.minimum((df['additions_count'] + df['deletions_count']) / 100, 5)
        
        return score
    
    def _detect_stale_proposals(self, df: pd.DataFrame) -> pd.Series:
        """Detect stale proposals (over 60 days old)"""
        def is_stale(row):
            if row.get('state', '').lower() != 'open':
                return False
            
            created_at = pd.to_datetime(row.get('created_at'))
            if pd.notna(created_at):
                days_open = (datetime.now() - created_at).days
                return days_open > 60
            return False
        
        return df.apply(is_stale, axis=1)
    
    def get_summary_stats(self, df: pd.DataFrame) -> dict:
        """Get summary statistics for the dataset"""
        if df.empty:
            return {}
        
        stats = {
            'total_proposals': len(df),
            'approved_proposals': len(df[df['category'] == 'APPROVED']),
            'pending_proposals': len(df[df['category'] == 'PENDING']),
            'rejected_proposals': len(df[df['category'] == 'REJECTED']),
            'stale_proposals': len(df[df['category'] == 'STALE']),
            'avg_approval_time': df[df['approval_time_days'].notna()]['approval_time_days'].mean(),
            'total_repositories': df['repository'].nunique(),
            'total_authors': df['author'].nunique(),
            'total_curators': len(set([curator for curators in df['curators'] for curator in curators if curator]))
        }
        
        return stats
    
    def get_program_stats(self, df: pd.DataFrame) -> dict:
        """Get statistics by grant program"""
        if df.empty:
            return {}
        
        program_stats = {}
        
        for repo in df['repository'].unique():
            repo_df = df[df['repository'] == repo]
            
            program_stats[repo] = {
                'total_proposals': len(repo_df),
                'approved_proposals': len(repo_df[repo_df['category'] == 'APPROVED']),
                'pending_proposals': len(repo_df[repo_df['category'] == 'PENDING']),
                'rejected_proposals': len(repo_df[repo_df['category'] == 'REJECTED']),
                'stale_proposals': len(repo_df[repo_df['category'] == 'STALE']),
                'avg_approval_time': repo_df[repo_df['approval_time_days'].notna()]['approval_time_days'].mean(),
                'total_authors': repo_df['author'].nunique(),
                'total_curators': len(set([curator for curators in repo_df['curators'] for curator in curators if curator]))
            }
        
        return program_stats
    
    def get_curator_stats(self, df: pd.DataFrame) -> dict:
        """Get statistics by curator"""
        if df.empty:
            return {}
        
        # Flatten curators list
        curator_data = []
        for _, row in df.iterrows():
            for curator in row.get('curators', []):
                if curator:
                    curator_data.append({
                        'curator': curator,
                        'proposal_id': row.get('id'),
                        'category': row.get('category'),
                        'repository': row.get('repository'),
                        'approval_time_days': row.get('approval_time_days')
                    })
        
        if not curator_data:
            return {}
        
        curator_df = pd.DataFrame(curator_data)
        
        curator_stats = {}
        for curator in curator_df['curator'].unique():
            curator_proposals = curator_df[curator_df['curator'] == curator]
            
            curator_stats[curator] = {
                'total_proposals': len(curator_proposals),
                'approved_proposals': len(curator_proposals[curator_proposals['category'] == 'APPROVED']),
                'rejected_proposals': len(curator_proposals[curator_proposals['category'] == 'REJECTED']),
                'pending_proposals': len(curator_proposals[curator_proposals['category'] == 'PENDING']),
                'avg_approval_time': curator_proposals[curator_proposals['approval_time_days'].notna()]['approval_time_days'].mean(),
                'programs_worked_on': curator_proposals['repository'].nunique()
            }
        
        return curator_stats 