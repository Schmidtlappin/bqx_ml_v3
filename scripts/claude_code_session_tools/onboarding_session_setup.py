#!/usr/bin/env python3
"""
Agent Onboarding Session Setup Script

Handles session naming during agent onboarding:
1. Deprecates predecessor session by adding "(deprecated)" to its name
2. Verifies current session has correct agent name

Usage:
    python3 onboarding_session_setup.py <agent_id> <predecessor_session_id>

Example:
    python3 onboarding_session_setup.py BA df480dab-e189-46d8-be49-b60b436c2a3e

Agent IDs:
    CE - Chief Engineer
    BA - Build Agent
    QA - Quality Assurance
    EA - Enhancement Assistant
"""

import json
import sys
import os
from pathlib import Path

# Agent name mappings
AGENT_NAMES = {
    "CE": "Chief Engineer",
    "BA": "Build Agent",
    "QA": "Quality Assurance",
    "EA": "Enhancement Assistant"
}

PROJECT_DIR = "/home/micha/.claude/projects/-home-micha-bqx-ml-v3"


def update_first_message(session_file, new_title):
    """Update the first user message text in session file."""

    if not os.path.exists(session_file):
        print(f"✗ Session file not found: {session_file}")
        return False

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
            except:
                pass
            lines.append(line)

    if fixed:
        with open(session_file, 'w') as f:
            f.writelines(lines)
        return True
    else:
        print(f"✗ No user message found in {session_file}")
        return False


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
    except:
        pass
    return None


def find_current_session_id():
    """Find the most recently modified session file (likely current session)."""
    import glob

    sessions = glob.glob(f"{PROJECT_DIR}/*.jsonl")
    # Filter out agent helper sessions and archived
    main_sessions = [s for s in sessions if not os.path.basename(s).startswith('agent-')]

    if not main_sessions:
        return None

    # Sort by modification time, newest first
    main_sessions.sort(key=os.path.getmtime, reverse=True)

    # Return the most recent session ID
    return os.path.basename(main_sessions[0]).replace('.jsonl', '')


def onboarding_setup(agent_id, predecessor_id):
    """Setup session naming for agent onboarding."""

    # Validate agent ID
    if agent_id not in AGENT_NAMES:
        print(f"✗ Invalid agent ID: {agent_id}")
        print(f"   Valid options: {', '.join(AGENT_NAMES.keys())}")
        return False

    agent_name = AGENT_NAMES[agent_id]

    print(f"=== Agent Onboarding Session Setup ===")
    print(f"Agent: {agent_id} - {agent_name}")
    print()

    # Step 1: Deprecate predecessor session
    print(f"Step 1: Deprecating predecessor session...")
    predecessor_file = f"{PROJECT_DIR}/{predecessor_id}.jsonl"
    deprecated_name = f"{agent_id} - {agent_name} (deprecated)"

    if update_first_message(predecessor_file, deprecated_name):
        print(f"✓ Predecessor renamed to: {deprecated_name}")
    else:
        print(f"⚠ Could not deprecate predecessor (may not exist or have no user messages)")

    print()

    # Step 2: Verify current session name
    print(f"Step 2: Verifying current session name...")
    current_id = find_current_session_id()

    if not current_id:
        print(f"✗ Could not find current session")
        return False

    current_file = f"{PROJECT_DIR}/{current_id}.jsonl"
    current_title = get_session_title(current_file)
    expected_name = f"{agent_id} - {agent_name}"

    print(f"Current session ID: {current_id}")
    print(f"Current name: {current_title}")
    print(f"Expected name: {expected_name}")
    print()

    if current_title and current_title.startswith(expected_name):
        print(f"✓ Current session name is correct")
        print()
        print("=== Setup Complete ===")
        print()
        print("Next steps:")
        print(f"1. Update AGENT_REGISTRY.json with session ID: {current_id}")
        print(f"2. Read charge document and TODO file")
        print(f"3. Check inbox for directives")
        print(f"4. Report ready status to CE")
        print()
        print("Reload VS Code window to see updated names:")
        print("  Cmd/Ctrl + Shift + P → 'Developer: Reload Window'")
        return True
    else:
        print(f"⚠ Current session name doesn't match expected")
        print()
        print(f"To fix, run:")
        print(f"  python3 update_first_message.py {current_file} '{expected_name}'")
        return False


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 onboarding_session_setup.py <agent_id> <predecessor_session_id>")
        print()
        print("Example:")
        print("  python3 onboarding_session_setup.py BA df480dab-e189-46d8-be49-b60b436c2a3e")
        print()
        print("Agent IDs: CE, BA, QA, EA")
        sys.exit(1)

    agent_id = sys.argv[1].upper()
    predecessor_id = sys.argv[2]

    success = onboarding_setup(agent_id, predecessor_id)
    sys.exit(0 if success else 1)
