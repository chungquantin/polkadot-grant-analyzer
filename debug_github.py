#!/usr/bin/env python3

from github_client import GitHubClient
import json

def debug_github_response():
    client = GitHubClient()
    
    # Get a sample PR from the first repository
    from config import GRANT_REPOSITORIES
    
    first_repo = list(GRANT_REPOSITORIES.keys())[0]
    repo_config = GRANT_REPOSITORIES[first_repo]
    
    print(f"Fetching from {repo_config['owner']}/{repo_config['repo']}")
    
    prs = client.get_pull_requests(
        owner=repo_config['owner'],
        repo=repo_config['repo'],
        per_page=1
    )
    
    if prs:
        sample_pr = prs[0]
        print("\n=== SAMPLE PR STRUCTURE ===")
        print("Keys:", list(sample_pr.keys()))
        
        print("\n=== USER INFO ===")
        user = sample_pr.get('user', {})
        print("User keys:", list(user.keys()) if user else "No user")
        print("User login:", user.get('login') if user else "No login")
        
        print("\n=== SAMPLE PR DATA ===")
        print("Title:", sample_pr.get('title'))
        print("Number:", sample_pr.get('number'))
        print("State:", sample_pr.get('state'))
        print("Merged:", sample_pr.get('merged'))
        
        # Check if we can get comments and reviews
        print("\n=== CHECKING COMMENTS/REVIEWS ===")
        enriched = client.enrich_proposal_data(sample_pr)
        print("Comments count:", len(enriched.get('comments', [])))
        print("Reviews count:", len(enriched.get('reviews', [])))
        
        if enriched.get('comments'):
            print("Sample comment user:", enriched['comments'][0].get('user', {}).get('login'))
        
        if enriched.get('reviews'):
            print("Sample review user:", enriched['reviews'][0].get('user', {}).get('login'))

if __name__ == "__main__":
    debug_github_response() 