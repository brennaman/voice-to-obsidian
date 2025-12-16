#!/usr/bin/env python3
"""
AI Developer Script
Orchestrates Claude API to implement Linear issues and create PRs
"""

import os
import sys
from pathlib import Path
import anthropic

def get_env_var(name):
    """Get required environment variable"""
    value = os.environ.get(name)
    if not value:
        print(f"ERROR: {name} environment variable not set!")
        sys.exit(1)
    return value

def read_target_file():
    """Read the Python script that needs modification"""
    # For now, we're working with voice_to_obsidian.py
    # In the future, we could make this dynamic based on the issue
    target_file = Path("voice_to_obsidian.py")
    
    if not target_file.exists():
        print(f"ERROR: {target_file} not found in repository")
        sys.exit(1)
    
    with open(target_file, 'r') as f:
        return f.read()

def call_claude_api(issue_title, issue_description, current_code):
    """Call Claude API to implement the feature"""
    api_key = get_env_var("ANTHROPIC_API_KEY")
    client = anthropic.Anthropic(api_key=api_key)
    
    prompt = f"""You are an expert Python developer. You've been given a feature request to implement.

FEATURE REQUEST:
Title: {issue_title}
Description: {issue_description}

CURRENT CODE:
```python
{current_code}
```

YOUR TASK:
1. Analyze the feature request carefully
2. Implement the requested changes to the code
3. Ensure backward compatibility where possible
4. Follow Python best practices
5. Add comments for any complex logic

IMPORTANT INSTRUCTIONS:
- If the request asks to CREATE NEW FILES (like .env.example, .gitignore, requirements.txt, README.md), you should create those files
- Output each file separately with clear markers
- For modifying existing code, output the COMPLETE modified file, not just the changes
- Be thorough and professional in your implementation

OUTPUT FORMAT:
For each file you create or modify, use this format:

=== FILE: filename.ext ===
[complete file content here]
=== END FILE ===

Now implement the feature request."""

    try:
        print(f"🤖 Calling Claude API to implement: {issue_title}")
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        response_text = message.content[0].text
        print("✅ Claude API call successful")
        return response_text
        
    except Exception as e:
        print(f"❌ Error calling Claude API: {e}")
        sys.exit(1)

def parse_claude_response(response_text):
    """Parse Claude's response to extract files"""
    files = {}
    lines = response_text.split('\n')
    
    current_file = None
    current_content = []
    in_file = False
    
    for line in lines:
        if line.startswith('=== FILE:'):
            # Extract filename
            current_file = line.replace('=== FILE:', '').strip()
            current_content = []
            in_file = True
        elif line.startswith('=== END FILE'):
            # Save the file
            if current_file:
                files[current_file] = '\n'.join(current_content)
                current_file = None
                current_content = []
            in_file = False
        elif in_file:
            current_content.append(line)
    
    # If Claude didn't use the marker format, assume entire response is the modified file
    if not files and response_text.strip():
        # Default to modifying voice_to_obsidian.py
        files['voice_to_obsidian.py'] = response_text.strip()
    
    return files

def write_files(files):
    """Write the files to the repository"""
    for filename, content in files.items():
        filepath = Path(filename)
        
        # Create directories if needed
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w') as f:
            f.write(content)
        
        print(f"✅ Written: {filename}")

def main():
    print("🚀 AI Development Script Started")
    print("=" * 60)
    
    # Get issue details from environment
    issue_id = get_env_var("LINEAR_ISSUE_ID")
    issue_title = get_env_var("LINEAR_ISSUE_TITLE")
    issue_description = get_env_var("LINEAR_ISSUE_DESCRIPTION")
    issue_identifier = get_env_var("LINEAR_ISSUE_IDENTIFIER")
    
    print(f"📋 Issue: {issue_identifier}")
    print(f"📝 Title: {issue_title}")
    print(f"📄 Description: {issue_description[:100]}...")
    print("=" * 60)
    
    # Read current code
    print("\n📖 Reading current code...")
    current_code = read_target_file()
    print(f"✅ Read {len(current_code)} characters")
    
    # Call Claude API
    print("\n🤖 Calling Claude API...")
    response = call_claude_api(issue_title, issue_description, current_code)
    
    # Parse response
    print("\n🔍 Parsing Claude's response...")
    files = parse_claude_response(response)
    print(f"✅ Found {len(files)} file(s) to create/modify")
    
    # Write files
    print("\n💾 Writing files...")
    write_files(files)
    
    print("\n" + "=" * 60)
    print("✅ AI Development Complete!")
    print("📦 Files will be committed and PR will be created by GitHub Actions")
    print("=" * 60)

if __name__ == "__main__":
    main()