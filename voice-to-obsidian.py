#!/usr/bin/env python3
"""
SuperWhisper to Obsidian Automation Script
Monitors clipboard for new transcriptions and saves formatted notes to Obsidian
"""

import os
import time
from datetime import datetime
from pathlib import Path
import subprocess
import anthropic
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration
OBSIDIAN_VAULT_PATH = Path(os.environ.get("OBSIDIAN_VAULT_PATH", "/Users/username/ObsidianVault/MyVault"))
CHECK_INTERVAL = 2  # Check clipboard every 2 seconds
MIN_WORDS = 5  # Minimum words to process (filters out accidental recordings)
MAX_CHARS = 5000  # Safety limit per note
DAILY_LIMIT = 100  # Maximum notes per day (safety measure)

# Track processed content to avoid duplicates
last_clipboard_content = ""
daily_count_file = OBSIDIAN_VAULT_PATH / ".automation_count.txt"

def get_api_key():
    """Get API key from environment variable"""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY environment variable not set!")
        print("Please set it in your .env file or environment")
        exit(1)
    return api_key

def get_clipboard():
    """Get current clipboard content on macOS"""
    try:
        result = subprocess.run(['pbpaste'], capture_output=True, text=True)
        return result.stdout.strip()
    except Exception as e:
        print(f"Error reading clipboard: {e}")
        return ""

def check_daily_limit():
    """Check if we've hit the daily limit"""
    today = datetime.now().strftime("%Y-%m-%d")
    
    if daily_count_file.exists():
        with open(daily_count_file, 'r') as f:
            data = f.read().strip().split(',')
            if len(data) == 2:
                date, count = data
                if date == today:
                    return int(count) < DAILY_LIMIT
    
    # Reset counter for new day
    with open(daily_count_file, 'w') as f:
        f.write(f"{today},0")
    return True

def increment_daily_count():
    """Increment the daily counter"""
    today = datetime.now().strftime("%Y-%m-%d")
    
    if daily_count_file.exists():
        with open(daily_count_file, 'r') as f:
            data = f.read().strip().split(',')
            if len(data) == 2:
                date, count = data
                if date == today:
                    count = int(count) + 1
                else:
                    count = 1
            else:
                count = 1
    else:
        count = 1
    
    with open(daily_count_file, 'w') as f:
        f.write(f"{today},{count}")

def format_with_claude(transcription):
    """Send transcription to Claude for formatting"""
    client = anthropic.Anthropic(api_key=get_api_key())
    
    prompt = f"""I just dictated the following text using voice-to-text. Please format it into a well-structured note with:

1. A clear, descriptive title/header based on the main topic
2. Proper grammar and sentence structure
3. Logical sections with headers where appropriate
4. Bullet points for lists or multiple items
5. Extract any action items into a dedicated "Action Items" section
6. Keep the tone and intent of my original words

At the very end, include a "---" divider followed by "### Original Transcription" and the exact original text word-for-word.

Here's what I said:

{transcription}"""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text
    except Exception as e:
        print(f"Error calling Claude API: {e}")
        return None

def save_to_obsidian(formatted_note):
    """Append formatted note to today's daily note"""
    today = datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.now().strftime("%I:%M %p")
    note_file = OBSIDIAN_VAULT_PATH / f"{today}.md"
    
    # Create or append to daily note
    if note_file.exists():
        with open(note_file, 'a') as f:
            f.write(f"\n\n## {current_time}\n\n{formatted_note}")
    else:
        with open(note_file, 'w') as f:
            f.write(f"# {datetime.now().strftime('%B %d, %Y')}\n\n## {current_time}\n\n{formatted_note}")
    
    print(f"✓ Note saved to {note_file.name}")

def is_valid_transcription(text):
    """Check if text is a valid transcription to process"""
    if not text or len(text) < 10:
        return False
    
    word_count = len(text.split())
    if word_count < MIN_WORDS:
        return False
    
    if len(text) > MAX_CHARS:
        print(f"Warning: Text too long ({len(text)} chars), truncating to {MAX_CHARS}")
        return True
    
    return True

def main():
    global last_clipboard_content
    
    print("🎙️  SuperWhisper to Obsidian Automation Started")
    print(f"📁 Vault: {OBSIDIAN_VAULT_PATH}")
    print(f"⏱️  Checking clipboard every {CHECK_INTERVAL} seconds")
    print("🛑 Press Ctrl+C to stop\n")
    
    # Verify vault exists
    if not OBSIDIAN_VAULT_PATH.exists():
        print(f"ERROR: Obsidian vault not found at {OBSIDIAN_VAULT_PATH}")
        print("Please update OBSIDIAN_VAULT_PATH in your .env file")
        exit(1)
    
    # Verify API key
    get_api_key()
    
    # Initialize last clipboard with current content
    last_clipboard_content = get_clipboard()
    
    try:
        while True:
            current_clipboard = get_clipboard()
            
            # Check if clipboard has new content
            if current_clipboard != last_clipboard_content:
                if is_valid_transcription(current_clipboard):
                    # Check daily limit
                    if not check_daily_limit():
                        print(f"⚠️  Daily limit of {DAILY_LIMIT} notes reached. Pausing until tomorrow.")
                        time.sleep(3600)  # Sleep for an hour
                        continue
                    
                    print(f"\n📝 New transcription detected ({len(current_clipboard)} chars)")
                    print("🤖 Processing with Claude...")
                    
                    # Truncate if needed
                    text_to_process = current_clipboard[:MAX_CHARS]
                    
                    # Format with Claude
                    formatted = format_with_claude(text_to_process)
                    
                    if formatted:
                        # Save to Obsidian
                        save_to_obsidian(formatted)
                        increment_daily_count()
                        print("✅ Done!\n")
                    else:
                        print("❌ Failed to format note\n")
                
                # Update last seen content
                last_clipboard_content = current_clipboard
            
            time.sleep(CHECK_INTERVAL)
            
    except KeyboardInterrupt:
        print("\n\n👋 Automation stopped")

if __name__ == "__main__":
    main()
