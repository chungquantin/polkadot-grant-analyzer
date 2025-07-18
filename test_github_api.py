#!/usr/bin/env python3

import requests
from config import GITHUB_TOKEN, GITHUB_API_BASE_URL

def test_github_api():
    headers = {
        'Accept': 'application/vnd.github.v3+json'
    }
    if GITHUB_TOKEN:
        headers['Authorization'] = f'token {GITHUB_TOKEN}'
    
    # Test with a known repository
    url = f"{GITHUB_API_BASE_URL}/repos/w3f/Grants-Program/pulls"
    params = {'per_page': 1, 'state': 'all'}
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        prs = response.json()
        if prs:
            pr = prs[0]
            print("=== GITHUB API RESPONSE STRUCTURE ===")
            print("Keys:", list(pr.keys()))
            
            print("\n=== USER INFO ===")
            user = pr.get('user', {})
            print("User keys:", list(user.keys()) if user else "No user")
            print("User login:", user.get('login') if user else "No login")
            print("User type:", user.get('type') if user else "No type")
            
            print("\n=== SAMPLE PR DATA ===")
            print("Title:", pr.get('title'))
            print("Number:", pr.get('number'))
            print("State:", pr.get('state'))
            print("Merged:", pr.get('merged'))
            print("Author (user.login):", pr.get('user', {}).get('login'))
            
            # Test comments endpoint
            comments_url = f"{GITHUB_API_BASE_URL}/repos/w3f/Grants-Program/pulls/{pr['number']}/comments"
            comments_response = requests.get(comments_url, headers=headers)
            
            if comments_response.status_code == 200:
                comments = comments_response.json()
                print(f"\n=== COMMENTS ({len(comments)} found) ===")
                if comments:
                    comment = comments[0]
                    print("Comment user:", comment.get('user', {}).get('login'))
                    print("Comment body preview:", comment.get('body', '')[:100])
                else:
                    print("No comments found")
            else:
                print(f"Failed to get comments: {comments_response.status_code}")
                
    else:
        print(f"Failed to fetch PRs: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    test_github_api() 