# AI Development Workflow Setup Guide

This guide will help you set up the complete AI development workflow using Linear, Claude, and GitHub.

## Overview

The workflow works like this:
1. You create an issue in Linear describing a feature
2. You add the `ai-development` label to the issue
3. Linear webhook notifies your webhook handler
4. Webhook handler triggers GitHub Actions
5. GitHub Actions calls Claude API to implement the feature
6. A draft Pull Request is automatically created
7. You review and merge the PR

## Files in This Setup

- `.github/workflows/ai-development.yml` - GitHub Actions workflow
- `.github/scripts/ai_developer.py` - Python script that calls Claude API
- `.github/scripts/linear_webhook_handler.py` - Webhook receiver (needs deployment)

## Setup Instructions

### Step 1: Add Files to Your Repository

1. Create the directory structure:
```bash
mkdir -p .github/workflows
mkdir -p .github/scripts
```

2. Add these files to your repository:
   - `.github/workflows/ai-development.yml`
   - `.github/scripts/ai_developer.py`
   - `.github/scripts/linear_webhook_handler.py`

3. Commit and push:
```bash
git add .github/
git commit -m "Add AI development workflow"
git push origin main
```

### Step 2: GitHub Secrets (Already Done ✅)

You've already added:
- `ANTHROPIC_API_KEY`
- `LINEAR_API_KEY`

The `GITHUB_TOKEN` is automatically provided by GitHub Actions.

### Step 3: Deploy Webhook Handler

The webhook handler needs to run on a publicly accessible server. Here are your options:

#### Option A: Use a Webhook Relay Service (Easiest)

For testing, you can skip deploying the webhook handler and **manually trigger** the workflow instead. See "Manual Trigger Method" below.

#### Option B: Deploy to a Server

Deploy `linear_webhook_handler.py` to:
- **Heroku** (free tier available)
- **Railway** (free tier available)
- **Google Cloud Run** (free tier available)
- **Your own server** with a public IP

Requirements:
```bash
pip install flask requests
```

Environment variables needed:
```
GITHUB_TOKEN=<your-github-personal-access-token>
LINEAR_WEBHOOK_SECRET=<optional-for-security>
```

To create a GitHub Personal Access Token:
1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token with `repo` scope
3. Save it as `GITHUB_TOKEN` environment variable on your webhook server

#### Option C: Manual Trigger Method (For Testing)

Instead of webhooks, you can manually trigger the workflow using GitHub CLI or API:

**Using GitHub CLI:**
```bash
gh api repos/brennaman/voice-to-obsidian/dispatches \
  --method POST \
  --field event_type='linear_issue_labeled' \
  --field client_payload[issue_id]='issue-id-here' \
  --field client_payload[issue_title]='Your issue title' \
  --field client_payload[issue_description]='Your issue description' \
  --field client_payload[issue_identifier]='PROJ-123'
```

**Using curl:**
```bash
curl -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer YOUR_GITHUB_TOKEN" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  https://api.github.com/repos/brennaman/voice-to-obsidian/dispatches \
  -d '{"event_type":"linear_issue_labeled","client_payload":{"issue_id":"abc123","issue_title":"Add .env support","issue_description":"Add environment variable support to the script","issue_identifier":"PROJ-1"}}'
```

### Step 4: Set Up Linear Webhook (If Using Webhook Handler)

1. In Linear: Settings → API → Webhooks
2. Click "Create webhook"
3. Configure:
   - **URL**: Your webhook handler URL (e.g., `https://your-server.com/webhook/linear`)
   - **Events**: Select "Issues" → "Issue updated"
   - **Secret**: (optional) Generate a secret for security
4. Save the webhook

### Step 5: Create Linear Label

1. In Linear: Settings → Labels
2. Create a new label:
   - **Name**: `ai-development`
   - **Color**: Choose any color
3. Save

## Testing the Workflow

### Test 1: Simple File Creation

Create a Linear issue:
- **Title**: "Add .env.example file"
- **Description**: 
  ```
  Create a .env.example file that contains template environment variables:
  - ANTHROPIC_API_KEY
  - OBSIDIAN_VAULT_PATH
  
  Include comments explaining what each variable is for.
  ```
- **Label**: Add `ai-development`

### Test 2: Code Modification

Create a Linear issue:
- **Title**: "Add configurable check interval"
- **Description**:
  ```
  Make the CHECK_INTERVAL configurable via environment variable.
  - Read from environment variable CHECK_INTERVAL_SECONDS
  - Default to 2 seconds if not set
  - Update the script to use this new configuration
  ```
- **Label**: Add `ai-development`

### Test 3: Multiple Files

Create a Linear issue:
- **Title**: "Add project documentation"
- **Description**:
  ```
  Create comprehensive project documentation:
  1. Create requirements.txt with all dependencies
  2. Create .gitignore for Python projects
  3. Create README.md with setup instructions
  ```
- **Label**: Add `ai-development`

## Expected Behavior

After adding the `ai-development` label:

1. ⏱️ Within 1-2 minutes, a GitHub Actions workflow should start
2. 🤖 The workflow calls Claude API to implement the feature
3. 📝 Files are created/modified in a new branch: `feature/ai-PROJ-123`
4. 🔄 A draft PR is created with:
   - Title: `[AI] Your Issue Title`
   - Description including the Linear issue details
   - Labels: `ai-generated`, `needs-review`
5. ✅ You review the PR and merge if satisfied

## Troubleshooting

### Workflow doesn't trigger
- Check GitHub Actions tab for any errors
- Verify webhook is configured correctly in Linear
- Check webhook handler logs
- Try manual trigger method to test

### Claude API errors
- Verify `ANTHROPIC_API_KEY` is set correctly in GitHub secrets
- Check API key has sufficient credits
- Look at workflow logs in GitHub Actions

### PR not created
- Check if branch already exists with same name
- Verify `GITHUB_TOKEN` has proper permissions
- Look for errors in GitHub Actions logs

### Files not modified correctly
- Check the Linear issue description is clear and detailed
- Claude works best with specific, detailed requirements
- Review the AI developer logs in GitHub Actions

## Tips for Writing Good Linear Issues

To get the best results from AI development:

1. **Be specific**: "Add .env support" is better than "improve config"
2. **List requirements**: Use numbered lists or bullet points
3. **Provide examples**: Show what the output should look like
4. **Mention files**: Specify which files to create/modify
5. **Include context**: Explain why the feature is needed

## Next Steps

Once this is working, you can:
- Add more sophisticated prompting to Claude
- Implement automated tests that run before PR creation
- Add code review comments from Claude
- Support multiple files/projects
- Add ChatGPT as an alternative AI backend

## Architecture Diagram

```
Linear Issue Created
    ↓
Add 'ai-development' label
    ↓
Linear Webhook → Webhook Handler
    ↓
GitHub Actions Triggered (repository_dispatch)
    ↓
Read Issue Details + Current Code
    ↓
Call Claude API
    ↓
Parse Response + Write Files
    ↓
Create Draft PR on feature/ai-* branch
    ↓
You Review & Merge
```

## Support

If you run into issues:
1. Check GitHub Actions logs
2. Check webhook handler logs (if deployed)
3. Verify all secrets are set correctly
4. Try manual trigger method to isolate webhook issues