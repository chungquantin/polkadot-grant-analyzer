import requests
import time
from datetime import datetime
from typing import Dict, List, Optional
import logging
import os

# Try to import config, with fallbacks
try:
    from config import GITHUB_TOKEN, GITHUB_API_BASE_URL, GRANT_REPOSITORIES
except ImportError:
    # Fallback values if config module is not available
    GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', '')
    GITHUB_API_BASE_URL = "https://api.github.com"
    GRANT_REPOSITORIES = {
        "w3f_grants": {
            "owner": "w3f",
            "repo": "Grants-Program",
            "type": "pull_request",
            "description": "Web3 Foundation Grants Program"
        },
        "polkadot_fast_grants": {
            "owner": "Polkadot-Fast-Grants",
            "repo": "apply",
            "type": "pull_request",
            "description": "Polkadot Fast Grants"
        },
        "use_inkubator": {
            "owner": "use-inkubator",
            "repo": "Ecosystem-Grants",
            "type": "pull_request",
            "description": "Use Inkubator Ecosystem Grants"
        },
        "polkadot_open_source": {
            "owner": "PolkadotOpenSourceGrants",
            "repo": "apply",
            "type": "pull_request",
            "description": "Polkadot Open Source Grants"
        }
    }

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GitHubClient:
    def __init__(self, token: str = None):
        self.token = token or GITHUB_TOKEN
        self.headers = {
            'Accept': 'application/vnd.github.v3+json'
        }
        if self.token:
            self.headers['Authorization'] = f'token {self.token}'
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def _make_request(self, url: str, params: Dict = None) -> Dict:
        """Make a GitHub API request with rate limiting"""
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            # Check rate limit
            remaining = int(response.headers.get('X-RateLimit-Remaining', 0))
            if remaining < 10:
                logger.warning(f"Rate limit low: {remaining} requests remaining")
                time.sleep(60)  # Wait 1 minute if rate limit is low
                
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"GitHub API request failed: {e}")
            return {}
    
    def get_pull_requests(self, owner: str, repo: str, state: str = "all", per_page: int = 100) -> List[Dict]:
        """Fetch pull requests from a repository"""
        url = f"{GITHUB_API_BASE_URL}/repos/{owner}/{repo}/pulls"
        params = {
            'state': state,
            'per_page': per_page,
            'sort': 'created',
            'direction': 'desc'
        }
        
        all_prs = []
        page = 1
        
        while True:
            params['page'] = page
            data = self._make_request(url, params)
            
            if not data:
                break
                
            all_prs.extend(data)
            
            # Check if we have more pages
            if len(data) < per_page:
                break
                
            page += 1
            time.sleep(1)  # Rate limiting
        
        logger.info(f"Fetched {len(all_prs)} pull requests from {owner}/{repo}")
        return all_prs
    
    def get_pull_request_details(self, owner: str, repo: str, pr_number: int) -> Dict:
        """Get detailed information about a specific pull request"""
        url = f"{GITHUB_API_BASE_URL}/repos/{owner}/{repo}/pulls/{pr_number}"
        return self._make_request(url)
    
    def get_pull_request_comments(self, owner: str, repo: str, pr_number: int) -> List[Dict]:
        """Get comments for a pull request"""
        url = f"{GITHUB_API_BASE_URL}/repos/{owner}/{repo}/pulls/{pr_number}/comments"
        return self._make_request(url) or []
    
    def get_pull_request_reviews(self, owner: str, repo: str, pr_number: int) -> List[Dict]:
        """Get reviews for a pull request"""
        url = f"{GITHUB_API_BASE_URL}/repos/{owner}/{repo}/pulls/{pr_number}/reviews"
        return self._make_request(url) or []
    
    def get_issues(self, owner: str, repo: str, state: str = "all") -> List[Dict]:
        """Fetch issues from a repository (for labels and categories)"""
        url = f"{GITHUB_API_BASE_URL}/repos/{owner}/{repo}/issues"
        params = {
            'state': state,
            'per_page': 100,
            'sort': 'created',
            'direction': 'desc'
        }
        
        all_issues = []
        page = 1
        
        while True:
            params['page'] = page
            data = self._make_request(url, params)
            
            if not data:
                break
                
            all_issues.extend(data)
            
            if len(data) < 100:
                break
                
            page += 1
            time.sleep(1)
        
        return all_issues
    
    def fetch_all_grant_proposals(self) -> Dict[str, List[Dict]]:
        """Fetch grant proposals from all configured repositories"""
        all_proposals = {}
        
        for repo_key, repo_config in GRANT_REPOSITORIES.items():
            logger.info(f"Fetching proposals from {repo_config['owner']}/{repo_config['repo']}")
            
            try:
                prs = self.get_pull_requests(
                    owner=repo_config['owner'],
                    repo=repo_config['repo']
                )
                
                # Add repository metadata to each PR
                for pr in prs:
                    pr['repository'] = repo_key
                    pr['repository_info'] = repo_config
                
                # Enrich with comments and reviews for curator extraction
                logger.info(f"Enriching {len(prs)} proposals with comments and reviews...")
                enriched_prs = []
                for i, pr in enumerate(prs):
                    if i % 10 == 0:  # Log progress every 10 proposals
                        logger.info(f"Enriching proposal {i+1}/{len(prs)}")
                    enriched_pr = self.enrich_proposal_data(pr)
                    enriched_prs.append(enriched_pr)
                    time.sleep(0.5)  # Rate limiting for API calls
                
                all_proposals[repo_key] = enriched_prs
                
            except Exception as e:
                logger.error(f"Error fetching from {repo_key}: {e}")
                all_proposals[repo_key] = []
        
        return all_proposals
    
    def enrich_proposal_data(self, proposal: Dict) -> Dict:
        """Enrich proposal data with additional details"""
        repo_info = proposal.get('repository_info', {})
        owner = repo_info.get('owner')
        repo = repo_info.get('repo')
        pr_number = proposal.get('number')
        
        if not all([owner, repo, pr_number]):
            return proposal
        
        # Get detailed PR information
        details = self.get_pull_request_details(owner, repo, pr_number)
        if details:
            proposal.update(details)
        
        # Get comments
        comments = self.get_pull_request_comments(owner, repo, pr_number)
        proposal['comments'] = comments
        
        # Get reviews
        reviews = self.get_pull_request_reviews(owner, repo, pr_number)
        proposal['reviews'] = reviews
        
        return proposal 