#!/usr/bin/env python3
"""
Manual Workflow Trigger
Use this script to manually trigger the AI development workflow for testing
without needing to set up webhooks
"""

import requests
import sys
import os

# Configuration
GITHUB_REPO = "brennaman/voice-to-obsidian"
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")

def trigger_workflow(issue_id, issue_title, issue_description, issue_identifier):
    """Manually trigger the GitHub Actions workflow"""
    
    if not GITHUB_TOKEN:
        print("ERROR: GITHUB_TOKEN environment variable not set!")
        print("\nTo create a GitHub token:")
        print("1. Go to: https://github.com/settings/tokens")
        print("2. Generate new token (classic)")
        print("3. Select 'repo' scope")
        print("4. Export it: export GITHUB_TOKEN='your-token'")
        sys.exit(1)
    
    url = f"https://api.github.com/repos/{GITHUB_REPO}/dispatches"
    
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    
    payload = {
        "event_type": "linear_issue_labeled",
        "client_payload": {
            "issue_id": issue_id,
            "issue_title": issue_title,
            "issue_description": issue_description,
            "issue_identifier": issue_identifier
        }
    }
    
    print(f"🚀 Triggering workflow for: {issue_identifier} - {issue_title}")
    print(f"📝 Description: {issue_description[:100]}...")
    
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 204:
        print("✅ Workflow triggered successfully!")
        print(f"\n🔗 Check progress at: https://github.com/{GITHUB_REPO}/actions")
    else:
        print(f"❌ Failed to trigger workflow: {response.status_code}")
        print(f"Response: {response.text}")
        sys.exit(1)

def main():
    if len(sys.argv) < 4:
        print("Usage: python trigger_workflow.py <issue_id> <title> <description> [identifier]")
        print("\nExample:")
        print('  python trigger_workflow.py "issue-123" "Add .env support" "Create .env.example file with environment variables" "PROJ-1"')
        sys.exit(1)
    
    issue_id = sys.argv[1]
    issue_title = sys.argv[2]
    issue_description = sys.argv[3]
    issue_identifier = sys.argv[4] if len(sys.argv) > 4 else f"MANUAL-{issue_id}"
    
    trigger_workflow(issue_id, issue_title, issue_description, issue_identifier)

if __name__ == "__main__":
    main()