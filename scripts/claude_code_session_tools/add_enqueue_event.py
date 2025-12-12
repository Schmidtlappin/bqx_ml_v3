#!/usr/bin/env python3
"""
Add enqueue event with title to beginning of Claude Code session file.

Usage:
    python3 add_enqueue_event.py <session_file> <title> <session_id>

Example:
    python3 add_enqueue_event.py \
        /home/micha/.claude/projects/-home-micha-bqx-ml-v3/b2360551.jsonl \
        "CE - Chief Engineer" \
        "b2360551-04af-4110-9cc8-cb1dce3334cc"
"""

import json
import sys
from datetime import datetime

def add_enqueue_event(session_file, title, session_id):
    """Add enqueue event with title to beginning of session file."""

    # Create the enqueue event
    enqueue_event = {
        "type": "queue-operation",
        "operation": "enqueue",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "content": [{"type": "text", "text": title}],
        "sessionId": session_id
    }

    # Read existing content
    with open(session_file, 'r') as f:
        lines = f.readlines()

    # Write enqueue first, then existing content
    with open(session_file, 'w') as f:
        f.write(json.dumps(enqueue_event) + '\n')
        f.writelines(lines)

    print(f"✓ Added enqueue event '{title}' to {session_file}")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python3 add_enqueue_event.py <session_file> <title> <session_id>")
        print("\nExample:")
        print("  python3 add_enqueue_event.py \\")
        print("    /home/micha/.claude/projects/-home-micha-bqx-ml-v3/session.jsonl \\")
        print("    'CE - Chief Engineer' \\")
        print("    'b2360551-04af-4110-9cc8-cb1dce3334cc'")
        sys.exit(1)

    add_enqueue_event(sys.argv[1], sys.argv[2], sys.argv[3])
