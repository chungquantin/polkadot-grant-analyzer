import pandas as pd
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
from config import CATEGORIES

logger = logging.getLogger(__name__)

class GrantDataProcessor:
    def __init__(self):
        self.categories = CATEGORIES
    
    def parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string to datetime object"""
        if not date_str:
            return None
        try:
            # Handle ISO format with timezone
            if 'Z' in date_str:
                return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            else:
                return datetime.fromisoformat(date_str)
        except:
            try:
                # Handle format without timezone
                dt = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%SZ')
                # Make it timezone-aware
                return dt.replace(tzinfo=datetime.timezone.utc)
            except:
                try:
                    # Handle other formats
                    dt = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S')
                    return dt.replace(tzinfo=datetime.timezone.utc)
                except:
                    return None
    
    def extract_milestones(self, body: str) -> int:
        """Extract number of milestones from proposal body"""
        if not body:
            return 0
        
        # Common milestone patterns
        milestone_patterns = [
            r'milestone[s]?\s*[:\-]\s*(\d+)',
            r'phase[s]?\s*[:\-]\s*(\d+)',
            r'stage[s]?\s*[:\-]\s*(\d+)',
            r'(\d+)\s*milestone[s]?',
            r'(\d+)\s*phase[s]?',
            r'(\d+)\s*stage[s]?'
        ]
        
        for pattern in milestone_patterns:
            matches = re.findall(pattern, body.lower())
            if matches:
                try:
                    return max(int(match) for match in matches)
                except ValueError:
                    continue
        
        # Count milestone mentions
        milestone_mentions = len(re.findall(r'milestone', body.lower()))
        if milestone_mentions > 0:
            return milestone_mentions
        
        return 0
    
    def extract_curators(self, proposal: Dict) -> List[str]:
        """Extract curators from proposal comments and reviews"""
        curators = set()
        
        # Extract from comments
        comments = proposal.get('comments', [])
        for comment in comments:
            user = comment.get('user', {})
            if user and user.get('login'):
                curators.add(user['login'])
        
        # Extract from reviews
        reviews = proposal.get('reviews', [])
        for review in reviews:
            user = review.get('user', {})
            if user and user.get('login'):
                curators.add(user['login'])
        
        return list(curators)
    
    def determine_category(self, proposal: Dict) -> str:
        """Determine the category of a grant proposal"""
        state = proposal.get('state', '').upper()
        merged = proposal.get('merged', False)
        merged_at = proposal.get('merged_at')
        closed_at = proposal.get('closed_at')
        created_at = self.parse_date(proposal.get('created_at'))
        
        # Check if proposal is stale (over 60 days old and still open)
        if state == "OPEN" and created_at:
            days_since_creation = (datetime.now() - created_at).days
            if days_since_creation > 60:
                return "STALE"
        
        # Check if proposal was merged (either merged=True or has merged_at date)
        if merged or (merged_at is not None and pd.notna(merged_at)):
            return "APPROVED"
        elif state == "CLOSED":
            return "REJECTED"
        elif state == "OPEN":
            # Check labels for more specific categories
            labels = proposal.get('labels', [])
            for label in labels:
                label_name = label.get('name', '').upper()
                if label_name in self.categories:
                    return label_name
            return "PENDING"
        else:
            return "UNKNOWN"
    
    def calculate_approval_time(self, proposal: Dict) -> Optional[float]:
        """Calculate time from creation to approval/merge/rejection in days"""
        created_at = self.parse_date(proposal.get('created_at'))
        if not created_at:
            return None
        
        # Check for merge time
        merged_at = self.parse_date(proposal.get('merged_at'))
        if merged_at:
            # Ensure both dates are timezone-aware
            if created_at.tzinfo is None:
                created_at = created_at.replace(tzinfo=datetime.timezone.utc)
            if merged_at.tzinfo is None:
                merged_at = merged_at.replace(tzinfo=datetime.timezone.utc)
            return (merged_at - created_at).total_seconds() / 86400  # Convert to days
        
        # Check for close time (rejection)
        closed_at = self.parse_date(proposal.get('closed_at'))
        if closed_at:
            # Ensure both dates are timezone-aware
            if created_at.tzinfo is None:
                created_at = created_at.replace(tzinfo=datetime.timezone.utc)
            if closed_at.tzinfo is None:
                closed_at = closed_at.replace(tzinfo=datetime.timezone.utc)
            return (closed_at - created_at).total_seconds() / 86400
        
        return None
    
    def extract_rejection_reason(self, proposal: Dict) -> Optional[str]:
        """Extract rejection reason from comments"""
        if proposal.get('merged', False):
            return None
        
        comments = proposal.get('comments', [])
        rejection_keywords = [
            'reject', 'rejected', 'decline', 'declined', 'not approved',
            'does not meet', 'insufficient', 'incomplete', 'denied'
        ]
        
        for comment in comments:
            body = comment.get('body', '').lower()
            if any(keyword in body for keyword in rejection_keywords):
                return comment.get('body', '')
        
        return None
    
    def extract_bounty_amount(self, body: str) -> Optional[float]:
        """Extract bounty/grant amount from proposal body"""
        if not body:
            return None
        
        # Common patterns for amounts
        amount_patterns = [
            r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)',
            r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*USD',
            r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*DOT',
            r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*USDC',
            r'amount[:\s]*(\d+(?:,\d{3})*(?:\.\d{2})?)',
            r'budget[:\s]*(\d+(?:,\d{3})*(?:\.\d{2})?)',
            r'grant[:\s]*(\d+(?:,\d{3})*(?:\.\d{2})?)'
        ]
        
        for pattern in amount_patterns:
            matches = re.findall(pattern, body, re.IGNORECASE)
            if matches:
                try:
                    # Clean up the amount string and convert to float
                    amount_str = matches[0].replace(',', '')
                    return float(amount_str)
                except ValueError:
                    continue
        
        return None
    
    def process_proposal(self, proposal: Dict) -> Dict:
        """Process a single grant proposal and extract all metrics"""
        processed = {
            'id': proposal.get('id'),
            'number': proposal.get('number'),
            'title': proposal.get('title', ''),
            'description': proposal.get('body', ''),
            'author': proposal.get('user', {}).get('login', ''),
            'repository': proposal.get('repository', ''),
            'repository_info': proposal.get('repository_info', {}),
            'state': proposal.get('state', ''),
            'merged': proposal.get('merged', False),
            'created_at': proposal.get('created_at'),
            'updated_at': proposal.get('updated_at'),
            'closed_at': proposal.get('closed_at'),
            'merged_at': proposal.get('merged_at'),
            'milestones': self.extract_milestones(proposal.get('body', '')),
            'curators': self.extract_curators(proposal),
            'category': self.determine_category(proposal),
            'approval_time_days': self.calculate_approval_time(proposal),
            'rejection_reason': self.extract_rejection_reason(proposal),
            'bounty_amount': self.extract_bounty_amount(proposal.get('body', '')),
            'labels': [label.get('name', '') for label in proposal.get('labels', [])],
            'comments_count': len(proposal.get('comments', [])),
            'reviews_count': len(proposal.get('reviews', [])),
            'additions': proposal.get('additions', 0),
            'deletions': proposal.get('deletions', 0),
            'changed_files': proposal.get('changed_files', 0)
        }
        
        return processed
    
    def process_all_proposals(self, proposals: Dict[str, List[Dict]]) -> pd.DataFrame:
        """Process all grant proposals and return a DataFrame"""
        all_processed = []
        
        for repo_key, repo_proposals in proposals.items():
            logger.info(f"Processing {len(repo_proposals)} proposals from {repo_key}")
            
            for proposal in repo_proposals:
                try:
                    processed = self.process_proposal(proposal)
                    all_processed.append(processed)
                except Exception as e:
                    logger.error(f"Error processing proposal {proposal.get('number', 'unknown')}: {e}")
                    continue
        
        df = pd.DataFrame(all_processed)
        
        # Convert date columns
        date_columns = ['created_at', 'updated_at', 'closed_at', 'merged_at']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col])
        
        return df if not df.empty else pd.DataFrame(columns=[
            'id', 'number', 'title', 'description', 'author', 'repository', 
            'repository_info', 'state', 'merged', 'created_at', 'updated_at', 
            'closed_at', 'merged_at', 'milestones', 'curators', 'category', 
            'approval_time_days', 'rejection_reason', 'bounty_amount', 'labels', 
            'comments_count', 'reviews_count', 'additions', 'deletions', 'changed_files'
        ])
    
    def calculate_performance_metrics(self, df: pd.DataFrame) -> Dict:
        """Calculate performance metrics for grant programs"""
        metrics = {}
        
        # Overall statistics
        metrics['total_proposals'] = len(df)
        metrics['approved_proposals'] = len(df[df['category'] == 'APPROVED'])
        metrics['rejected_proposals'] = len(df[df['category'] == 'REJECTED'])
        metrics['pending_proposals'] = len(df[df['category'] == 'PENDING'])
        metrics['stale_proposals'] = len(df[df['category'] == 'STALE'])
        
        # Approval rate
        if metrics['total_proposals'] > 0:
            metrics['approval_rate'] = metrics['approved_proposals'] / metrics['total_proposals']
        else:
            metrics['approval_rate'] = 0
        
        # Time metrics
        approval_times = df[df['approval_time_days'].notna()]['approval_time_days']
        if len(approval_times) > 0:
            metrics['avg_approval_time_days'] = approval_times.mean()
            metrics['median_approval_time_days'] = approval_times.median()
            metrics['min_approval_time_days'] = approval_times.min()
            metrics['max_approval_time_days'] = approval_times.max()
        
        # Author statistics
        metrics['unique_authors'] = df['author'].nunique()
        metrics['top_authors'] = df['author'].value_counts().head(10).to_dict()
        
        # Curator statistics
        all_curators = []
        for curators in df['curators']:
            all_curators.extend(curators)
        metrics['unique_curators'] = len(set(all_curators))
        
        # Bounty statistics
        bounty_amounts = df[df['bounty_amount'].notna()]['bounty_amount']
        if len(bounty_amounts) > 0:
            metrics['total_bounty_amount'] = bounty_amounts.sum()
            metrics['avg_bounty_amount'] = bounty_amounts.mean()
            metrics['max_bounty_amount'] = bounty_amounts.max()
        
        # Repository breakdown
        metrics['repository_breakdown'] = df['repository'].value_counts().to_dict()
        
        # Category breakdown
        metrics['category_breakdown'] = df['category'].value_counts().to_dict()
        
        # Program-specific metrics
        metrics['program_metrics'] = {}
        for repo in df['repository'].unique():
            repo_data = df[df['repository'] == repo]
            repo_metrics = {
                'total': len(repo_data),
                'approved': len(repo_data[repo_data['category'] == 'APPROVED']),
                'rejected': len(repo_data[repo_data['category'] == 'REJECTED']),
                'pending': len(repo_data[repo_data['category'] == 'PENDING']),
                'stale': len(repo_data[repo_data['category'] == 'STALE']),
                'approval_rate': len(repo_data[repo_data['category'] == 'APPROVED']) / len(repo_data) if len(repo_data) > 0 else 0,
                'avg_approval_time': repo_data[repo_data['approval_time_days'].notna()]['approval_time_days'].mean() if len(repo_data[repo_data['approval_time_days'].notna()]) > 0 else 0,
                'unique_authors': repo_data['author'].nunique(),
                'unique_curators': len(set([curator for curators in repo_data['curators'] for curator in curators]))
            }
            metrics['program_metrics'][repo] = repo_metrics
        
        return metrics 