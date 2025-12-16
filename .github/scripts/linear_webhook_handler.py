#!/usr/bin/env python3
"""
Linear Webhook Handler
Receives webhooks from Linear and triggers GitHub Actions workflow
This script needs to be deployed on a server that can receive webhooks
"""

from flask import Flask, request, jsonify
import requests
import os
import hmac
import hashlib

app = Flask(__name__)

# Configuration
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")  # Personal Access Token with repo scope
GITHUB_REPO = "brennaman/voice-to-obsidian"
TARGET_LABEL = "ai-development"

def verify_linear_signature(payload, signature, secret):
    """Verify the webhook signature from Linear"""
    if not secret:
        return True  # Skip verification if no secret configured
    
    computed_signature = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, computed_signature)

@app.route('/webhook/linear', methods=['POST'])
def linear_webhook():
    """Handle incoming Linear webhooks"""
    
    # Verify signature (optional but recommended)
    signature = request.headers.get('Linear-Signature')
    webhook_secret = os.environ.get('LINEAR_WEBHOOK_SECRET')
    
    if webhook_secret and signature:
        if not verify_linear_signature(request.data, signature, webhook_secret):
            return jsonify({"error": "Invalid signature"}), 401
    
    data = request.json
    
    # Check if this is an issue labeled event
    if data.get('type') != 'Issue' or data.get('action') != 'update':
        return jsonify({"message": "Ignored - not an issue update"}), 200
    
    issue_data = data.get('data', {})
    labels = issue_data.get('labels', [])
    
    # Check if ai-development label was added
    has_target_label = any(label.get('name') == TARGET_LABEL for label in labels)
    
    if not has_target_label:
        return jsonify({"message": f"Ignored - no '{TARGET_LABEL}' label"}), 200
    
    # Extract issue details
    issue_id = issue_data.get('id')
    issue_title = issue_data.get('title')
    issue_description = issue_data.get('description', '')
    issue_identifier = issue_data.get('identifier')  # e.g., "PROJ-123"
    
    print(f"🎯 Triggering workflow for issue: {issue_identifier}")
    
    # Trigger GitHub Actions workflow via repository_dispatch
    github_url = f"https://api.github.com/repos/{GITHUB_REPO}/dispatches"
    
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
    
    response = requests.post(github_url, headers=headers, json=payload)
    
    if response.status_code == 204:
        print(f"✅ Successfully triggered GitHub Actions workflow")
        return jsonify({"message": "Workflow triggered successfully"}), 200
    else:
        print(f"❌ Failed to trigger workflow: {response.status_code}")
        return jsonify({"error": "Failed to trigger workflow", "details": response.text}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    if not GITHUB_TOKEN:
        print("ERROR: GITHUB_TOKEN environment variable not set!")
        exit(1)
    
    # Run on port 5000 by default
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)