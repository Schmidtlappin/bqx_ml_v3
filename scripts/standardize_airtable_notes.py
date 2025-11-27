#!/usr/bin/env python3
"""
Standardize all AirTable notes to follow the new format guide
Icons: ✅ COMPLETED, 🔄 IN PROGRESS, 📋 PLANNED, 🚫 BLOCKED
"""

import json
from pyairtable import Api
from datetime import datetime
import re

# Load credentials
with open('/home/micha/bqx_ml_v3/.secrets/github_secrets.json', 'r') as f:
    secrets = json.load(f)
    API_KEY = secrets['secrets']['AIRTABLE_API_KEY']['value']
    BASE_ID = secrets['secrets']['AIRTABLE_BASE_ID']['value']

print("✅ AirTable credentials loaded!")

api = Api(API_KEY)
base = api.base(BASE_ID)
tasks_table = base.table('Tasks')

def get_status_icon(status):
    """Map status to standardized icon"""
    status_icons = {
        'done': '✅',
        'completed': '✅',
        'in progress': '🔄',
        'in_progress': '🔄',
        'todo': '📋',
        'planned': '📋',
        'not started': '📋',
        'blocked': '🚫',
        'on hold': '🚫'
    }
    return status_icons.get(status.lower(), '📋')

def get_status_text(status):
    """Map status to standardized text"""
    status_text = {
        'done': 'COMPLETED',
        'completed': 'COMPLETED',
        'in progress': 'IN PROGRESS',
        'in_progress': 'IN PROGRESS',
        'todo': 'PLANNED',
        'planned': 'PLANNED',
        'not started': 'PLANNED',
        'blocked': 'BLOCKED',
        'on hold': 'BLOCKED'
    }
    return status_text.get(status.lower(), 'PLANNED')

def standardize_note(note, status, task_name=None):
    """
    Convert any note format to standardized format
    """
    if not note:
        note = "No details provided yet."

    # Check if already standardized (has icon and timestamp pattern)
    if re.match(r'^[✅🔄📋🚫] \w+: \d{4}-\d{2}-\d{2}T', note):
        return note  # Already standardized

    icon = get_status_icon(status)
    status_text = get_status_text(status)
    timestamp = datetime.now().isoformat()

    # Extract key information from existing note
    lines = note.split('\n')

    # Try to preserve existing structure
    content_sections = []
    current_section = []

    for line in lines:
        if line.strip().startswith('='):
            continue  # Skip existing separators
        elif line.strip() and (line.strip()[0].isupper() or line.strip().startswith('•') or line.strip().startswith('-')):
            if current_section and not current_section[-1].strip():
                content_sections.append('\n'.join(current_section))
                current_section = []
        current_section.append(line)

    if current_section:
        content_sections.append('\n'.join(current_section))

    # Build standardized content
    content = '\n\n'.join(content_sections) if content_sections else note

    # Add task context if available
    if task_name:
        header = f"{task_name.upper()}"
        if header not in content:
            content = f"{header}\n\n{content}"

    # Format final note
    standardized = f"""{icon} {status_text}: {timestamp}
================================================
{content.strip()}
================================================"""

    return standardized

print("\n📋 STANDARDIZING AIRTABLE NOTES...")

# Get all tasks
all_tasks = tasks_table.all()
print(f"Found {len(all_tasks)} tasks to process")

# Track updates
updated_count = 0
skipped_count = 0
error_count = 0

# Priority order for updates
priority_statuses = ['In Progress', 'Done', 'Blocked', 'Todo', 'Not Started']

# Sort tasks by priority
def get_priority(task):
    status = task['fields'].get('status', 'Todo')
    try:
        return priority_statuses.index(status)
    except ValueError:
        return 999

sorted_tasks = sorted(all_tasks, key=get_priority)

print("\n🔄 Processing tasks by priority...")

for record in sorted_tasks:
    task_id = record['fields'].get('task_id', 'Unknown')
    task_name = record['fields'].get('name', '')
    status = record['fields'].get('status', 'Todo')
    notes = record['fields'].get('notes', '')

    try:
        # Check if already standardized
        if notes and re.match(r'^[✅🔄📋🚫] \w+: \d{4}-\d{2}-\d{2}T', notes):
            skipped_count += 1
            print(f"⏭️  {task_id}: Already standardized")
            continue

        # Standardize the note
        standardized_note = standardize_note(notes, status, task_name)

        # Update AirTable
        tasks_table.update(
            record['id'],
            {'notes': standardized_note}
        )

        updated_count += 1
        icon = get_status_icon(status)
        print(f"{icon} {task_id}: Note standardized ({status})")

    except Exception as e:
        error_count += 1
        print(f"❌ {task_id}: Error updating - {e}")

# Create summary report
print("\n📊 STANDARDIZATION COMPLETE")
print(f"  ✅ Updated: {updated_count} tasks")
print(f"  ⏭️  Skipped: {skipped_count} tasks (already standardized)")
print(f"  ❌ Errors: {error_count} tasks")
print(f"  📋 Total: {len(all_tasks)} tasks")

# Update a few specific high-priority tasks with detailed notes
high_priority_updates = [
    {
        'task_id': 'MP03.P00.S00.T95',
        'notes': f"""📋 PLANNED: {datetime.now().isoformat()}
================================================
MASTER OBJECTIVE: ACHIEVE 95% PREDICTION ACCURACY

REQUIREMENTS
• Test all 6,000+ planned features
• Keep only performance-improving features
• Deploy ensemble of 10+ models
• Use 10+ years historical data

CURRENT STATUS
• Baseline: 70% R² with 12 features
• Gap to Target: 25% improvement needed
• Timeline: 6-8 weeks systematic testing

NEXT STEPS
1. Triangulation feature testing (Week 1)
2. Correlation network implementation (Week 2)
3. Algorithm diversification (Week 3)
4. Production optimization (Weeks 4-6)

Expected outcome: 85-88% accuracy with 200-500 features
================================================"""
    },
    {
        'task_id': 'MP03.P05.S05.T10',
        'notes': f"""📋 PLANNED: {datetime.now().isoformat()}
================================================
TRIANGULATION FEATURES IMPLEMENTATION

SCOPE
• 378 triangle combinations (28 choose 3)
• Real-time parity deviation calculation
• Z-score normalization
• Arbitrage signal generation

EXPECTED IMPACT
• Performance Gain: +3-5% R²
• Features to Keep: 20-30 of 378
• Priority: CRITICAL

IMPLEMENTATION PLAN
1. Start with EUR-GBP-USD triangle
2. Test on major pairs only
3. Evaluate incremental value
4. Keep only significant improvements

Decision threshold: >1% R² improvement
================================================"""
    }
]

print("\n🎯 Updating high-priority task notes...")
for update in high_priority_updates:
    try:
        # Find the task
        task = next((r for r in all_tasks if r['fields'].get('task_id') == update['task_id']), None)
        if task:
            tasks_table.update(task['id'], {'notes': update['notes']})
            print(f"✅ Updated {update['task_id']} with detailed standardized note")
    except Exception as e:
        print(f"⚠️ Could not update {update['task_id']}: {e}")

print(f"\n✅ STANDARDIZATION COMPLETE!")
print(f"  Timestamp: {datetime.now().isoformat()}")
print(f"  Guide: /docs/AIRTABLE_NOTES_STANDARDIZATION_GUIDE.md")