# SuperWhisper to Obsidian Automation

Automatically monitor your clipboard for voice transcriptions (from SuperWhisper or any voice-to-text tool) and save them as beautifully formatted notes in Obsidian using Claude AI.

## Features

- 🎙️ Monitors clipboard for new transcriptions
- 🤖 Formats notes with Claude AI for better structure
- 📝 Auto-saves to daily notes in Obsidian
- ✅ Extracts action items automatically
- 🛡️ Built-in safety limits (daily note limit, character limits)
- 📊 Preserves original transcription for reference

## Prerequisites

- macOS (uses `pbpaste` for clipboard access)
- Python 3.7 or higher
- [Anthropic API key](https://console.anthropic.com/)
- Obsidian vault

## Setup

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd <repo-name>
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

Or using a virtual environment (recommended):

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure Environment Variables

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your values:
   ```bash
   ANTHROPIC_API_KEY=your-actual-api-key-here
   OBSIDIAN_VAULT_PATH=/Users/yourusername/path/to/vault
   ```

   **To get your Anthropic API key:**
   - Go to https://console.anthropic.com/
   - Sign up or log in
   - Navigate to API Keys
   - Create a new key

### 4. Verify Your Obsidian Vault Path

Make sure the path in your `.env` file points to your actual Obsidian vault directory. For example:
- macOS: `/Users/yourusername/Documents/ObsidianVault`
- Windows: `C:\Users\yourusername\Documents\ObsidianVault`
- Linux: `/home/yourusername/Documents/ObsidianVault`

## Usage

### Running the Script

```bash
python voice_to_obsidian.py
```

The script will:
1. Start monitoring your clipboard every 2 seconds
2. Detect new transcriptions (text with 5+ words)
3. Format them using Claude AI
4. Save to your daily note in Obsidian

### How It Works

1. **Dictate** using SuperWhisper (or any voice-to-text tool)
2. Text is copied to your clipboard
3. Script detects the new content
4. Claude AI formats it with:
   - Clear title/header
   - Proper grammar and structure
   - Organized sections
   - Extracted action items
   - Original transcription preserved
5. Note is appended to today's daily note in Obsidian

### Stopping the Script

Press `Ctrl+C` to stop the automation.

## Configuration

You can customize these settings in `voice_to_obsidian.py`:

- `CHECK_INTERVAL`: How often to check clipboard (default: 2 seconds)
- `MIN_WORDS`: Minimum words to process (default: 5)
- `MAX_CHARS`: Maximum characters per note (default: 5000)
- `DAILY_LIMIT`: Maximum notes per day (default: 100)

## Safety Features

- **Daily Limit**: Prevents runaway API costs (default 100 notes/day)
- **Character Limit**: Truncates very long transcriptions
- **Duplicate Detection**: Ignores repeated clipboard content
- **Validation**: Filters out very short or invalid text

## Output Format

Notes are saved to daily files named `YYYY-MM-DD.md` in your vault with the format:

```markdown
# December 16, 2025

## 02:30 PM

[Formatted note content with headers, bullets, action items]

---
### Original Transcription
[Your exact dictated words]
```

## Troubleshooting

### "ERROR: ANTHROPIC_API_KEY environment variable not set"
- Make sure you've created the `.env` file
- Verify your API key is correct
- Try running: `source .env` (macOS/Linux)

### "ERROR: Obsidian vault not found"
- Check the path in your `.env` file
- Ensure the vault directory exists
- Use absolute paths, not relative paths

### Notes aren't being saved
- Verify Obsidian isn't blocking file access
- Check that the script has write permissions to your vault
- Look for error messages in the terminal

### Clipboard not being detected
- This script is macOS-specific (uses `pbpaste`)
- For Windows/Linux, you'll need to modify the `get_clipboard()` function

## Development

### Running Tests
(Tests to be added)

### Contributing
Pull requests are welcome! Please ensure:
- Code follows existing style
- Add tests for new features
- Update documentation as needed

## License

MIT License - feel free to use and modify as needed.

## Acknowledgments

- Built with [Anthropic's Claude API](https://www.anthropic.com/)
- Designed for use with [SuperWhisper](https://superwhisper.com/)
- Integrates with [Obsidian](https://obsidian.md/)