#!/usr/bin/env python3
"""
Verify session names in Claude Code dropdown.
Shows the first user message text for all sessions in a project directory.

Usage:
    python3 verify_session_names.py [project_dir]

Example:
    python3 verify_session_names.py /home/micha/.claude/projects/-home-micha-bqx-ml-v3
"""

import json
import os
import sys
import glob

def get_session_title(session_file):
    """Extract the first user message text from session."""
    try:
        with open(session_file, 'r') as f:
            for line in f:
                try:
                    event = json.loads(line)
                    if event.get('type') == 'user':
                        content = event.get('message', {}).get('content', [])
                        for item in content:
                            if item.get('type') == 'text':
                                text = item.get('text', '')
                                if not text.startswith('<ide_opened_file>'):
                                    return text[:80]  # First 80 chars
                except:
                    continue
    except Exception as e:
        return f"Error: {e}"
    return "No user message found"

def verify_sessions(project_dir):
    """Check all session names in project directory."""

    if not os.path.exists(project_dir):
        print(f"✗ Directory not found: {project_dir}")
        return

    sessions = glob.glob(f"{project_dir}/*.jsonl")

    # Filter out agent sessions (usually small helper sessions)
    main_sessions = [s for s in sessions if not os.path.basename(s).startswith('agent-')]

    if not main_sessions:
        print(f"No main sessions found in {project_dir}")
        return

    print(f"Found {len(main_sessions)} main session(s) in {os.path.basename(project_dir)}:\n")
    print(f"{'Session ID':<40} {'Name':<50} {'Size':>10}")
    print("-" * 100)

    for session_file in sorted(main_sessions, key=os.path.getmtime, reverse=True):
        session_id = os.path.basename(session_file).replace('.jsonl', '')
        title = get_session_title(session_file)
        size_mb = os.path.getsize(session_file) / (1024 * 1024)

        # Truncate session ID for display
        display_id = session_id[:36] if len(session_id) > 36 else session_id

        print(f"{display_id:<40} {title:<50} {size_mb:>8.1f}M")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        project_dir = sys.argv[1]
    else:
        # Default to bqx_ml_v3 project
        project_dir = "/home/micha/.claude/projects/-home-micha-bqx-ml-v3"

    verify_sessions(project_dir)
