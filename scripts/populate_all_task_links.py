#!/usr/bin/env python3
"""
Populate all plan_link, phase_link, and stage_link fields in Tasks table.
Ensures complete hierarchical linking for all tasks.
"""

import json
import os
import subprocess
from pyairtable import Api
from datetime import datetime
from collections import defaultdict

# Get credentials from GCP Secrets Manager
def get_secret(secret_name):
    try:
        result = subprocess.run(
            ["gcloud", "secrets", "versions", "access", "latest", f"--secret={secret_name}"],
            capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except:
        return None

# Try GitHub secrets as fallback
def get_github_secret():
    try:
        with open('/home/micha/bqx_ml_v3/.secrets/github_secrets.json', 'r') as f:
            secrets = json.load(f)
            api_key = secrets['secrets']['AIRTABLE_API_KEY']['value']
            base_id = secrets['secrets']['AIRTABLE_BASE_ID']['value']
            return api_key, base_id
    except:
        return None, None

# Get credentials
AIRTABLE_API_KEY = os.environ.get("AIRTABLE_API_KEY") or get_secret("bqx-ml-airtable-token")
BASE_ID = os.environ.get("AIRTABLE_BASE_ID") or get_secret("bqx-ml-airtable-base-id")

# Fallback to GitHub secrets
if not AIRTABLE_API_KEY or not BASE_ID:
    AIRTABLE_API_KEY, BASE_ID = get_github_secret()

if not AIRTABLE_API_KEY or not BASE_ID:
    raise ValueError("Could not load AirTable credentials from any source")

api = Api(AIRTABLE_API_KEY)
base = api.base(BASE_ID)

# Get all tables
tasks_table = base.table('Tasks')
stages_table = base.table('Stages')
phases_table = base.table('Phases')
plans_table = base.table('Plans')

def build_hierarchy_maps():
    """Build lookup maps for the entire hierarchy."""

    print("📊 Building hierarchy maps...")

    # Build plan lookup
    plan_lookup = {}
    all_plans = plans_table.all()
    for plan in all_plans:
        plan_id = plan['fields'].get('plan_id')
        if plan_id:
            plan_lookup[plan_id] = plan['id']
    print(f"  • Found {len(plan_lookup)} plans")

    # Build phase lookup with plan relationships
    phase_lookup = {}
    phase_to_plan = {}
    all_phases = phases_table.all()
    for phase in all_phases:
        phase_id = phase['fields'].get('phase_id')
        if phase_id:
            phase_lookup[phase_id] = phase['id']

            # Extract plan from phase_id (e.g., MP03.P01 -> MP03)
            parts = phase_id.split('.')
            if len(parts) >= 1:
                plan_id = parts[0]
                if plan_id in plan_lookup:
                    phase_to_plan[phase_id] = plan_lookup[plan_id]
    print(f"  • Found {len(phase_lookup)} phases")

    # Build stage lookup with phase and plan relationships
    stage_lookup = {}
    stage_to_phase = {}
    stage_to_plan = {}
    all_stages = stages_table.all()
    for stage in all_stages:
        stage_id = stage['fields'].get('stage_id')
        if stage_id:
            stage_lookup[stage_id] = stage['id']

            # Extract phase and plan from stage_id (e.g., MP03.P01.S01 -> MP03.P01, MP03)
            parts = stage_id.split('.')
            if len(parts) >= 2:
                phase_id = '.'.join(parts[:2])  # MP03.P01
                plan_id = parts[0]  # MP03

                if phase_id in phase_lookup:
                    stage_to_phase[stage_id] = phase_lookup[phase_id]
                if plan_id in plan_lookup:
                    stage_to_plan[stage_id] = plan_lookup[plan_id]
    print(f"  • Found {len(stage_lookup)} stages")

    return {
        'plan_lookup': plan_lookup,
        'phase_lookup': phase_lookup,
        'stage_lookup': stage_lookup,
        'phase_to_plan': phase_to_plan,
        'stage_to_phase': stage_to_phase,
        'stage_to_plan': stage_to_plan
    }

def populate_task_links(hierarchy):
    """Populate all link fields for tasks."""

    print("\n🔧 POPULATING ALL TASK LINK FIELDS")
    print("=" * 80)

    # Get all tasks
    all_tasks = tasks_table.all()
    print(f"Found {len(all_tasks)} tasks to process")

    # Track updates
    stats = {
        'plan_link_added': 0,
        'phase_link_added': 0,
        'stage_link_added': 0,
        'already_complete': 0,
        'updated': 0,
        'failed': 0
    }

    print("\n📝 Processing tasks...")
    print("-" * 60)

    for task in all_tasks:
        fields = task['fields']
        task_id = fields.get('task_id', 'Unknown')

        # Check existing links
        has_plan = bool(fields.get('plan_link'))
        has_phase = bool(fields.get('phase_link'))
        has_stage = bool(fields.get('stage_link'))

        # Skip if already complete
        if has_plan and has_phase and has_stage:
            stats['already_complete'] += 1
            continue

        # Extract IDs from task_id (e.g., MP03.P01.S01.T01)
        parts = task_id.split('.')
        if len(parts) < 3:
            print(f"  ⚠️  Cannot parse task ID: {task_id}")
            continue

        plan_id = parts[0]  # MP03
        phase_id = '.'.join(parts[:2])  # MP03.P01
        stage_id = '.'.join(parts[:3])  # MP03.P01.S01

        # Build update fields
        update_fields = {}

        # Add missing plan_link
        if not has_plan:
            if plan_id in hierarchy['plan_lookup']:
                update_fields['plan_link'] = [hierarchy['plan_lookup'][plan_id]]
                stats['plan_link_added'] += 1
            else:
                print(f"  ⚠️  Plan {plan_id} not found for task {task_id}")

        # Add missing phase_link
        if not has_phase:
            if phase_id in hierarchy['phase_lookup']:
                update_fields['phase_link'] = [hierarchy['phase_lookup'][phase_id]]
                stats['phase_link_added'] += 1
            else:
                print(f"  ⚠️  Phase {phase_id} not found for task {task_id}")

        # Add missing stage_link
        if not has_stage:
            if stage_id in hierarchy['stage_lookup']:
                update_fields['stage_link'] = [hierarchy['stage_lookup'][stage_id]]
                stats['stage_link_added'] += 1
            else:
                # Try default stage
                alt_stage_id = '.'.join(parts[:2]) + '.S01'
                if alt_stage_id in hierarchy['stage_lookup']:
                    update_fields['stage_link'] = [hierarchy['stage_lookup'][alt_stage_id]]
                    stats['stage_link_added'] += 1
                    print(f"  📍 Using default stage {alt_stage_id} for task {task_id}")
                else:
                    print(f"  ⚠️  Stage {stage_id} not found for task {task_id}")

        # Apply updates
        if update_fields:
            try:
                tasks_table.update(task['id'], update_fields)
                stats['updated'] += 1

                # Show what was updated
                links_added = []
                if 'plan_link' in update_fields:
                    links_added.append('plan')
                if 'phase_link' in update_fields:
                    links_added.append('phase')
                if 'stage_link' in update_fields:
                    links_added.append('stage')

                print(f"  ✅ {task_id}: Added {', '.join(links_added)} links")

            except Exception as e:
                stats['failed'] += 1
                print(f"  ❌ {task_id}: Failed to update - {e}")

    return stats

def verify_completeness():
    """Verify completeness of all link fields."""

    print("\n🔍 Verifying link field completeness...")

    all_tasks = tasks_table.all()

    missing = {
        'plan_link': [],
        'phase_link': [],
        'stage_link': []
    }

    for task in all_tasks:
        fields = task['fields']
        task_id = fields.get('task_id', 'Unknown')

        if not fields.get('plan_link'):
            missing['plan_link'].append(task_id)
        if not fields.get('phase_link'):
            missing['phase_link'].append(task_id)
        if not fields.get('stage_link'):
            missing['stage_link'].append(task_id)

    # Calculate completeness
    total_tasks = len(all_tasks)
    completeness = {
        'plan_link': ((total_tasks - len(missing['plan_link'])) / total_tasks * 100) if total_tasks > 0 else 100,
        'phase_link': ((total_tasks - len(missing['phase_link'])) / total_tasks * 100) if total_tasks > 0 else 100,
        'stage_link': ((total_tasks - len(missing['stage_link'])) / total_tasks * 100) if total_tasks > 0 else 100
    }

    return completeness, missing, total_tasks

def generate_report(stats, completeness, missing, total_tasks):
    """Generate final report."""

    print("\n" + "=" * 80)
    print("📊 TASK LINK POPULATION REPORT")
    print("=" * 80)

    # Update statistics
    print("\n📈 Update Statistics:")
    print(f"  • Tasks already complete: {stats['already_complete']}")
    print(f"  • Tasks updated: {stats['updated']}")
    print(f"  • Tasks failed: {stats['failed']}")
    print(f"  • Plan links added: {stats['plan_link_added']}")
    print(f"  • Phase links added: {stats['phase_link_added']}")
    print(f"  • Stage links added: {stats['stage_link_added']}")

    # Completeness report
    print("\n✅ Link Field Completeness:")
    for field, percentage in completeness.items():
        if percentage == 100:
            status = "✅"
        elif percentage >= 99:
            status = "🔄"
        else:
            status = "⚠️"

        missing_count = len(missing[field])
        complete_count = total_tasks - missing_count
        print(f"  {status} {field:12}: {complete_count}/{total_tasks} ({percentage:.1f}%)")

    # Overall assessment
    overall_complete = all(p == 100 for p in completeness.values())

    print("\n" + "=" * 80)
    print("🎯 OVERALL ASSESSMENT")
    print("=" * 80)

    if overall_complete:
        print("\n✅ PERFECT: All tasks have complete hierarchical linking!")
        print("   • Every task has plan_link")
        print("   • Every task has phase_link")
        print("   • Every task has stage_link")
        print("   • Full hierarchy is connected")
    else:
        print("\n📝 Some links are still missing:")
        for field, task_ids in missing.items():
            if task_ids:
                print(f"\n  {field} missing ({len(task_ids)} tasks):")
                for task_id in task_ids[:5]:
                    print(f"    • {task_id}")
                if len(task_ids) > 5:
                    print(f"    ... and {len(task_ids) - 5} more")

    print(f"\nCompleted: {datetime.now().isoformat()}")
    print("=" * 80)

    return overall_complete

def main():
    """Main execution function."""

    print("🚀 STARTING TASK LINK POPULATION")
    print("Target: 100% completion of plan_link, phase_link, and stage_link")
    print("-" * 80)

    try:
        # Build hierarchy
        hierarchy = build_hierarchy_maps()

        # Populate links
        stats = populate_task_links(hierarchy)

        # Verify completeness
        completeness, missing, total_tasks = verify_completeness()

        # Generate report
        overall_complete = generate_report(stats, completeness, missing, total_tasks)

        if overall_complete:
            print("\n🎉 SUCCESS! All task link fields are complete!")
        else:
            print("\n📝 Task link population completed with some gaps remaining.")

        return overall_complete

    except Exception as e:
        print(f"\n❌ Error during link population: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()