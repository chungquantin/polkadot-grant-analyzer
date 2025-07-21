#!/usr/bin/env python3
"""
Test script to check GitHub data fetching
"""

from github_client import GitHubClient
import json

def test_github_data():
    print("🔍 Testing GitHub data fetching...")
    
    # Initialize GitHub client
    github_client = GitHubClient()
    
    # Test fetching from one repository
    repo_config = {
        "owner": "w3f",
        "repo": "Grants-Program",
        "type": "pull_request",
        "description": "Web3 Foundation Grants Program"
    }
    
    print(f"📥 Fetching from {repo_config['owner']}/{repo_config['repo']}...")
    
    try:
        # Fetch pull requests
        prs = github_client.get_pull_requests(
            owner=repo_config['owner'],
            repo=repo_config['repo'],
            per_page=5  # Just get 5 for testing
        )
        
        print(f"✅ Fetched {len(prs)} pull requests")
        
        if prs:
            # Show first PR structure
            first_pr = prs[0]
            print("\n=== First PR Structure ===")
            print(f"ID: {first_pr.get('id')}")
            print(f"Number: {first_pr.get('number')}")
            print(f"Title: {first_pr.get('title')}")
            print(f"State: {first_pr.get('state')}")
            print(f"Author: {first_pr.get('user', {}).get('login')}")
            print(f"Merged: {first_pr.get('merged')}")
            print(f"Merged At: {first_pr.get('merged_at')}")
            print(f"Closed At: {first_pr.get('closed_at')}")
            print(f"Created At: {first_pr.get('created_at')}")
            print(f"Comments: {first_pr.get('comments')}")
            print(f"Review Comments: {first_pr.get('review_comments')}")
            print(f"Commits: {first_pr.get('commits')}")
            print(f"Additions: {first_pr.get('additions')}")
            print(f"Deletions: {first_pr.get('deletions')}")
            print(f"Changed Files: {first_pr.get('changed_files')}")
            
            # Check if it's actually a PR or an issue
            print(f"\n=== PR vs Issue Check ===")
            if 'pull_request' in first_pr:
                print("✅ This is a Pull Request")
                print(f"PR URL: {first_pr['pull_request'].get('url')}")
            else:
                print("❌ This appears to be an Issue, not a PR")
            
            # Show labels
            labels = first_pr.get('labels', [])
            print(f"\n=== Labels ===")
            for label in labels:
                print(f"  - {label.get('name')}")
            
        else:
            print("❌ No pull requests found")
            
    except Exception as e:
        print(f"❌ Error fetching data: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_github_data() 