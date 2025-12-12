#!/usr/bin/env python3
"""
Update the first user message text in a Claude Code session file.
This determines the name shown in the VS Code dropdown menu.

Usage:
    python3 update_first_message.py <session_file> <new_title>

Example:
    python3 update_first_message.py \
        /home/micha/.claude/projects/-home-micha-bqx-ml-v3/session.jsonl \
        "QA - Quality Assurance"
"""

import json
import sys

def update_first_user_message(session_file, new_title):
    """Update the first user message text in session file."""

    lines = []
    fixed = False

    with open(session_file, 'r') as f:
        for line in f:
            try:
                event = json.loads(line)
                if not fixed and event.get('type') == 'user':
                    content = event.get('message', {}).get('content', [])
                    for item in content:
                        if item.get('type') == 'text':
                            text = item.get('text', '')
                            # Skip ide_opened_file notifications
                            if not text.startswith('<ide_opened_file>'):
                                # Found first actual user text - replace it
                                item['text'] = new_title
                                fixed = True
                                break
                    if fixed:
                        line = json.dumps(event) + '\n'
            except Exception as e:
                # Keep malformed lines as-is
                pass
            lines.append(line)

    if fixed:
        with open(session_file, 'w') as f:
            f.writelines(lines)
        print(f"✓ Updated first user message to: {new_title}")
        return True
    else:
        print("✗ No user message found to update")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 update_first_message.py <session_file> <new_title>")
        print("\nExample:")
        print("  python3 update_first_message.py \\")
        print("    /home/micha/.claude/projects/-home-micha-bqx-ml-v3/session.jsonl \\")
        print("    'QA - Quality Assurance'")
        sys.exit(1)

    success = update_first_user_message(sys.argv[1], sys.argv[2])
    sys.exit(0 if success else 1)
