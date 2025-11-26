#!/usr/bin/env python3
"""
Update AirTable model objectives to reflect INTERVAL-CENTRIC precision.
Changes "predict future BQX values" to "predict BQX values at specific future intervals".
"""

import os
import json
import time
from datetime import datetime
from pyairtable import Api

# AirTable configuration
BASE_ID = os.getenv('AIRTABLE_BASE_ID')
API_KEY = os.getenv('AIRTABLE_API_KEY')

# Load from secrets if not in environment
if not API_KEY or not BASE_ID:
    try:
        with open('/home/micha/bqx_ml_v3/.secrets/github_secrets.json', 'r') as f:
            secrets = json.load(f)
            API_KEY = API_KEY or secrets['secrets']['AIRTABLE_API_KEY']['value']
            BASE_ID = BASE_ID or secrets['secrets']['AIRTABLE_BASE_ID']['value']
    except:
        print("Warning: Could not load AirTable credentials")

# Initialize API
api = Api(API_KEY)
base = api.base(BASE_ID)
phases_table = base.table('Phases')
stages_table = base.table('Stages')
tasks_table = base.table('Tasks')

def update_model_objectives():
    """Update all references to model objectives with interval-centric precision."""
    print("=" * 80)
    print("UPDATING MODEL OBJECTIVES TO INTERVAL-CENTRIC PRECISION")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 80)

    updates_made = {
        'phases': 0,
        'stages': 0,
        'tasks': 0
    }

    # Key phrases to replace
    replacements = {
        'predict future bqx values': 'predict BQX values at specific future intervals',
        'predicting future bqx': 'predicting BQX at future intervals',
        'future bqx predictions': 'BQX predictions at future intervals',
        'forecast bqx values': 'predict BQX values at specific intervals',
        'bqx value predictions': 'BQX predictions at specific interval horizons',
        'predict bqx ahead': 'predict BQX at future intervals',
        '45 minutes ahead': 'at interval N+45',
        '90 minutes ahead': 'at interval N+90',
        '180 minutes ahead': 'at interval N+180',
        '24 hours ahead': 'at interval N+1440',
        'time-based predictions': 'interval-based predictions',
        'temporal predictions': 'interval-based predictions',
        'future time periods': 'future intervals',
        'prediction horizons': 'prediction intervals (45i, 90i, 180i, 360i, 720i, 1440i, 2880i)'
    }

    # Update Phases
    print("\n📊 Updating Phases...")
    phases = phases_table.all()

    for phase in phases:
        phase_id = phase['fields'].get('phase_id', '')
        description = phase['fields'].get('description', '')
        notes = phase['fields'].get('notes', '')

        updated_desc = description
        updated_notes = notes
        changed = False

        # Apply replacements
        for old, new in replacements.items():
            if old in description.lower():
                updated_desc = updated_desc.replace(old, new)
                updated_desc = updated_desc.replace(old.title(), new)
                updated_desc = updated_desc.replace(old.upper(), new.upper())
                changed = True

            if notes and old in notes.lower():
                updated_notes = updated_notes.replace(old, new)
                updated_notes = updated_notes.replace(old.title(), new)
                updated_notes = updated_notes.replace(old.upper(), new.upper())
                changed = True

        if changed:
            try:
                update_fields = {}
                if updated_desc != description:
                    update_fields['description'] = updated_desc
                if updated_notes != notes:
                    update_fields['notes'] = updated_notes

                if update_fields:
                    phases_table.update(phase['id'], update_fields)
                    print(f"  ✅ Updated {phase_id}")
                    updates_made['phases'] += 1
                    time.sleep(0.1)
            except Exception as e:
                print(f"  ❌ Failed to update {phase_id}: {e}")

    # Update key model-related stages
    print("\n📊 Updating Model-Related Stages...")
    stages = stages_table.all()

    model_stages = [
        'MP03.P01',  # Model Training phase
        'MP03.P08',  # Model Evaluation phase
        'MP03.P09',  # Production Deployment phase
    ]

    for stage in stages:
        stage_id = stage['fields'].get('stage_id', '')

        # Check if this is a model-related stage
        if any(ms in stage_id for ms in model_stages):
            description = stage['fields'].get('description', '')
            notes = stage['fields'].get('notes', '')

            updated_desc = description
            updated_notes = notes
            changed = False

            # Apply replacements
            for old, new in replacements.items():
                if old in description.lower():
                    updated_desc = updated_desc.replace(old, new)
                    updated_desc = updated_desc.replace(old.title(), new)
                    changed = True

                if notes and old in notes.lower():
                    updated_notes = updated_notes.replace(old, new)
                    updated_notes = updated_notes.replace(old.title(), new)
                    changed = True

            # Add interval clarification if discussing predictions
            if 'predict' in updated_desc.lower() and 'interval' not in updated_desc.lower():
                updated_desc += "\n\n**INTERVAL-CENTRIC**: All predictions target specific future intervals (N+45, N+90, etc.), not time-based periods."
                changed = True

            if changed:
                try:
                    update_fields = {}
                    if updated_desc != description:
                        update_fields['description'] = updated_desc
                    if updated_notes != notes and updated_notes:
                        update_fields['notes'] = updated_notes

                    if update_fields:
                        stages_table.update(stage['id'], update_fields)
                        print(f"  ✅ Updated {stage_id}")
                        updates_made['stages'] += 1
                        time.sleep(0.1)
                except Exception as e:
                    print(f"  ❌ Failed to update {stage_id}: {e}")

    # Update specific high-priority tasks
    print("\n📊 Updating Model Training and Prediction Tasks...")
    tasks = tasks_table.all()

    priority_task_keywords = [
        'model training',
        'prediction',
        'forecast',
        'target variable',
        'model objective',
        'batch prediction'
    ]

    for task in tasks:
        task_id = task['fields'].get('task_id', '')
        description = task['fields'].get('description', '')

        # Check if this is a priority task
        if any(keyword in description.lower() for keyword in priority_task_keywords):
            notes = task['fields'].get('notes', '')

            updated_desc = description
            updated_notes = notes
            changed = False

            # Apply replacements
            for old, new in replacements.items():
                if old in description.lower():
                    updated_desc = updated_desc.replace(old, new)
                    updated_desc = updated_desc.replace(old.title(), new)
                    changed = True

                if notes and old in notes.lower():
                    updated_notes = updated_notes.replace(old, new)
                    updated_notes = updated_notes.replace(old.title(), new)
                    changed = True

            if changed:
                try:
                    update_fields = {}
                    if updated_desc != description:
                        update_fields['description'] = updated_desc
                    if updated_notes != notes and updated_notes:
                        update_fields['notes'] = updated_notes

                    if update_fields:
                        tasks_table.update(task['id'], update_fields)
                        print(f"  ✅ Updated {task_id}")
                        updates_made['tasks'] += 1
                        time.sleep(0.1)
                except Exception as e:
                    print(f"  ❌ Failed to update {task_id}: {e}")

        # Limit updates to avoid timeout
        if updates_made['tasks'] >= 20:
            print("\n⚠️ Reached update limit for tasks (20). Run again if more updates needed.")
            break

    return updates_made

def add_interval_glossary():
    """Add a glossary task explaining interval notation."""
    print("\n" + "=" * 80)
    print("ADDING INTERVAL NOTATION GLOSSARY")
    print("=" * 80)

    # Find documentation stage
    stages = stages_table.all()
    doc_stage = None

    for stage in stages:
        stage_id = stage['fields'].get('stage_id', '')
        name = stage['fields'].get('name', '').lower()

        if 'MP03.P11' in stage_id or 'document' in name:
            doc_stage = stage
            break

    if not doc_stage:
        print("⚠️ Could not find documentation stage")
        return False

    glossary_task = {
        'task_id': f"{doc_stage['fields']['stage_id']}.T98",
        'description': """**Create INTERVAL-CENTRIC Glossary and Notation Guide**

Define and document the precise interval-based terminology used throughout BQX ML V3.""",

        'notes': """### Interval Notation Reference

**Core Principle**: All BQX ML V3 calculations are INTERVAL-CENTRIC, not time-based.

**Notation Convention**:
• `N` = Current interval index
• `i` suffix = intervals (e.g., 45i = 45 intervals)
• `N+H` = Interval N plus H intervals ahead
• `N-L` = Interval N minus L intervals back

**Standard Horizons**:
• N+45 = 45 intervals ahead (short-term)
• N+90 = 90 intervals ahead (medium-term)
• N+180 = 180 intervals ahead
• N+360 = 360 intervals ahead
• N+720 = 720 intervals ahead
• N+1440 = 1440 intervals ahead (long-term)
• N+2880 = 2880 intervals ahead (very long-term)

**Feature Windows**:
• bqx_45w = BQX calculated over 45-interval window
• lag_90i = Value from 90 intervals ago
• mean_180i = Mean over 180 intervals

**Key Clarifications**:
• "Predict at N+90" NOT "predict 90 minutes ahead"
• "45-interval window" NOT "45-minute window"
• "Interval-based predictions" NOT "time-based predictions"

**SQL Implementation**:
```sql
-- CORRECT: Interval-based
ROWS BETWEEN 44 PRECEDING AND CURRENT ROW  -- 45 intervals

-- INCORRECT: Time-based
RANGE BETWEEN INTERVAL 45 MINUTE PRECEDING AND CURRENT ROW
```

**Model Objective (Restated)**:
"Predict BQX values at specific future intervals for 28 currency pairs"

This glossary ensures consistent terminology across all documentation and implementation.""",

        'status': 'Todo',
        'priority': 'High',
        'stage_link': [doc_stage['id']]
    }

    try:
        new_task = tasks_table.create(glossary_task)
        print(f"✅ Created glossary task: {new_task['fields']['task_id']}")
        return True
    except Exception as e:
        print(f"❌ Failed to create glossary task: {e}")
        return False

def main():
    """Main execution."""
    print("=" * 80)
    print("MODEL OBJECTIVES INTERVAL-CENTRIC UPDATE")
    print("=" * 80)

    # Update existing records
    updates = update_model_objectives()

    # Add glossary task
    glossary_added = add_interval_glossary()

    # Summary
    print("\n" + "=" * 80)
    print("UPDATE SUMMARY")
    print("=" * 80)

    print(f"\n📊 Records Updated:")
    print(f"  Phases: {updates['phases']}")
    print(f"  Stages: {updates['stages']}")
    print(f"  Tasks: {updates['tasks']}")
    print(f"  Total: {sum(updates.values())}")

    if glossary_added:
        print(f"\n✅ Interval notation glossary task added")

    print(f"\n🎯 Model Objective Restated:")
    print(f"  'Predict BQX values at specific future intervals'")
    print(f"  NOT 'Predict future BQX values'")

    print(f"\n📋 Key Changes:")
    print(f"  • Time-based → Interval-based terminology")
    print(f"  • Added interval notation (N+45, N+90, etc.)")
    print(f"  • Clarified prediction horizons as intervals")
    print(f"  • Emphasized INTERVAL-CENTRIC architecture")

    print(f"\n🏁 Completed at: {datetime.now().isoformat()}")

    return 0 if sum(updates.values()) > 0 else 1

if __name__ == "__main__":
    exit(main())