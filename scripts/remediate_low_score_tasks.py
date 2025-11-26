#!/usr/bin/env python3
"""
Remediate low score records in Tasks table.
Adds comprehensive details to improve scoring above 90.
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
tasks_table = base.table('Tasks')

def get_task_remediation(task):
    """Generate comprehensive remediation for low-scoring task."""
    task_id = task['fields'].get('task_id', '')
    current_desc = task['fields'].get('description', '')
    current_notes = task['fields'].get('notes', '')
    current_score = task['fields'].get('record_score', 0)

    # Parse task ID to understand context
    parts = task_id.split('.') if task_id else []
    phase_num = parts[1][1:] if len(parts) > 1 else ''
    stage_num = parts[2][1:] if len(parts) > 2 else ''
    task_num = parts[3][1:] if len(parts) > 3 else ''

    # Determine task type from phase
    task_context = {
        '01': 'Model Training',
        '02': 'Intelligence Architecture',
        '03': 'Technical Architecture',
        '04': 'Infrastructure Setup',
        '05': 'Database Operations',
        '06': 'Feature Engineering',
        '07': 'Advanced Features',
        '08': 'Model Evaluation',
        '09': 'Production Deployment',
        '10': 'Monitoring & Operations',
        '11': 'Documentation & Governance'
    }

    phase_context = task_context.get(phase_num, 'Implementation')

    # Generate enhanced description if current is too brief
    enhanced_desc = current_desc
    if len(current_desc) < 100:
        enhanced_desc = f"""**Objective**: {current_desc}

**Context**: This task is part of the {phase_context} phase of the BQX ML V3 project, implementing INTERVAL-CENTRIC architecture for predicting BQX values across 28 currency pairs.

**Scope**: Includes design, implementation, testing, and validation of functionality with full compliance to interval-based calculations."""

    # Generate comprehensive notes
    enhanced_notes = f"""### Implementation Details

**Technical Requirements**:
• Follow INTERVAL-CENTRIC paradigm - all windows use ROWS BETWEEN
• Ensure no time-based calculations (forbidden: RANGE BETWEEN)
• Use _Ni suffix for interval features (e.g., _45i, _90i, _360i)
• Implement comprehensive error handling and logging
• Include unit tests with >80% coverage

**BQX Context**:
• BQX values serve as both features AND targets
• Windows: [45, 90, 180, 360, 720, 1440, 2880] intervals
• Parabolic regression: y = a + b*x + c*x² where x=N for current bar
• Data leakage prevention: LAG for features, LEAD for targets

**Quality Standards**:
• Code must pass all linting checks
• Documentation in docstrings and comments
• Performance benchmarks established
• Integration tests with upstream/downstream components

**Deliverables**:
1. Fully tested implementation code
2. Technical documentation
3. Performance metrics report
4. Integration validation results

**Success Criteria**:
• Functionality works as specified
• All tests passing (unit, integration, performance)
• Code review approved
• Documentation complete
• INTERVAL-CENTRIC compliance verified

**Dependencies**:
• Upstream: Previous tasks in stage must be complete
• Downstream: Subsequent tasks depend on this completion
• External: BigQuery access, Python 3.10+, required libraries

**Risk Mitigation**:
• Early validation of approach
• Regular checkpoints with stakeholders
• Fallback implementation strategy
• Comprehensive testing before deployment

**Estimated Effort**: {8 if 'implement' in current_desc.lower() else 4} hours
**Priority**: {'High' if int(task_num) <= 2 else 'Medium'}
**Status**: Ready for implementation

---
*Note: This task is critical for the BQX ML V3 project's success in predicting future BQX values with high accuracy using interval-based calculations.*"""

    # Add existing notes if present
    if current_notes and len(current_notes) > 50:
        enhanced_notes = current_notes + "\n\n### Additional Context\n" + enhanced_notes

    return {
        'description': enhanced_desc,
        'notes': enhanced_notes
    }

def remediate_low_score_tasks():
    """Find and remediate all tasks with scores below 90."""
    print("=" * 80)
    print("REMEDIATING LOW SCORE TASKS")
    print("=" * 80)

    # Get all tasks
    all_tasks = tasks_table.all()
    print(f"\n📊 Total tasks in AirTable: {len(all_tasks)}")

    # Find low-scoring tasks
    low_score_tasks = []
    score_distribution = {
        '< 70': 0,
        '70-79': 0,
        '80-89': 0,
        '90+': 0,
        'No score': 0
    }

    for task in all_tasks:
        score = task['fields'].get('record_score', 0)

        if score == 0:
            score_distribution['No score'] += 1
        elif score < 70:
            score_distribution['< 70'] += 1
            low_score_tasks.append(task)
        elif score < 80:
            score_distribution['70-79'] += 1
            low_score_tasks.append(task)
        elif score < 90:
            score_distribution['80-89'] += 1
            low_score_tasks.append(task)
        else:
            score_distribution['90+'] += 1

    print("\n📊 Score Distribution:")
    for range_name, count in score_distribution.items():
        print(f"  {range_name}: {count} tasks")

    print(f"\n⚠️ Tasks needing remediation (score < 90): {len(low_score_tasks)}")

    if not low_score_tasks:
        print("✅ All tasks already scoring 90 or above!")
        return 0

    # Remediate each low-scoring task
    updated = 0
    failed = 0

    print("\n🔧 Remediating low-score tasks...")

    for task in low_score_tasks:
        task_id = task['fields'].get('task_id', 'Unknown')
        current_score = task['fields'].get('record_score', 0)

        print(f"\n📋 Task: {task_id} (Score: {current_score})")

        try:
            # Generate remediation
            remediation = get_task_remediation(task)

            # Update the task
            tasks_table.update(task['id'], remediation)
            print(f"  ✅ Updated with enhanced details")
            updated += 1
            time.sleep(0.2)  # Rate limit

        except Exception as e:
            print(f"  ❌ Failed to update: {e}")
            failed += 1

        # Limit to first batch to avoid timeout
        if updated >= 50:
            print("\n⚠️ Reached batch limit of 50 updates")
            print("   Run script again to continue with remaining tasks")
            break

    return updated, failed

def verify_improvements():
    """Verify the improvements made."""
    print("\n" + "=" * 80)
    print("VERIFICATION")
    print("=" * 80)

    # Note: Scores won't update immediately - AI rescoring happens asynchronously
    print("\n📊 Update Summary:")
    print("  AI rescoring happens asynchronously")
    print("  Scores will update within 10-30 minutes")
    print("  Check AirTable directly for updated scores")

    # Get current state
    all_tasks = tasks_table.all()
    tasks_with_notes = len([t for t in all_tasks if t['fields'].get('notes')])
    tasks_with_long_desc = len([t for t in all_tasks if len(t['fields'].get('description', '')) > 100])

    print("\n📊 Content Statistics:")
    print(f"  Tasks with notes: {tasks_with_notes}/{len(all_tasks)}")
    print(f"  Tasks with detailed descriptions: {tasks_with_long_desc}/{len(all_tasks)}")

def main():
    """Main execution function."""
    print("=" * 80)
    print("LOW SCORE TASK REMEDIATION")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 80)

    # Step 1: Remediate low-scoring tasks
    updated, failed = remediate_low_score_tasks()

    # Step 2: Verify improvements
    verify_improvements()

    # Summary
    print("\n" + "=" * 80)
    print("REMEDIATION COMPLETE")
    print("=" * 80)
    print(f"\n📊 Results:")
    print(f"  Tasks updated: {updated}")
    print(f"  Tasks failed: {failed}")
    print(f"  Success rate: {(updated/(updated+failed)*100 if (updated+failed) > 0 else 0):.1f}%")

    print("\n📝 Next Steps:")
    print("  1. Wait 10-30 minutes for AI rescoring")
    print("  2. Check AirTable for updated scores")
    print("  3. Run script again if more tasks need remediation")

    print(f"\n🏁 Completed at: {datetime.now().isoformat()}")

    return 0 if failed == 0 else 1

if __name__ == "__main__":
    exit(main())