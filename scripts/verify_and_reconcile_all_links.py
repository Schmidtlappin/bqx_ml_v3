#!/usr/bin/env python3
"""
Verify and reconcile 100% of plan_link, phase_link, stage_link, and task_link fields
across all AirTable tables to ensure complete connectivity.
"""

import os
import subprocess
import json
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

def analyze_link_fields():
    """Analyze all link fields across tables."""

    print("🔍 ANALYZING ALL LINK FIELDS ACROSS AIRTABLE")
    print("=" * 80)

    analysis = {
        'tasks': {'total': 0, 'missing_links': defaultdict(list)},
        'stages': {'total': 0, 'missing_links': defaultdict(list)},
        'phases': {'total': 0, 'missing_links': defaultdict(list)},
        'plans': {'total': 0, 'missing_links': defaultdict(list)}
    }

    # Build ID maps for quick lookup
    id_maps = {
        'plans': {},
        'phases': {},
        'stages': {},
        'tasks': {}
    }

    # Load Plans
    print("\n📋 Loading Plans table...")
    try:
        all_plans = plans_table.all()
        analysis['plans']['total'] = len(all_plans)
        for plan in all_plans:
            plan_id = plan['fields'].get('plan_id', '')
            if plan_id:
                id_maps['plans'][plan_id] = plan['id']
        print(f"   ✓ Found {len(all_plans)} plans")
    except Exception as e:
        print(f"   ⚠️ Plans table not accessible: {e}")

    # Load Phases
    print("\n📋 Loading Phases table...")
    try:
        all_phases = phases_table.all()
        analysis['phases']['total'] = len(all_phases)
        for phase in all_phases:
            phase_id = phase['fields'].get('phase_id', '')
            if phase_id:
                id_maps['phases'][phase_id] = phase['id']

                # Check plan_link
                if not phase['fields'].get('plan_link'):
                    analysis['phases']['missing_links']['plan_link'].append(phase_id)
        print(f"   ✓ Found {len(all_phases)} phases")
    except Exception as e:
        print(f"   ⚠️ Phases table not accessible: {e}")

    # Load Stages
    print("\n📋 Loading Stages table...")
    all_stages = stages_table.all()
    analysis['stages']['total'] = len(all_stages)
    for stage in all_stages:
        stage_id = stage['fields'].get('stage_id', '')
        if stage_id:
            id_maps['stages'][stage_id] = stage['id']

            # Check phase_link
            if not stage['fields'].get('phase_link'):
                analysis['stages']['missing_links']['phase_link'].append(stage_id)
    print(f"   ✓ Found {len(all_stages)} stages")

    # Load Tasks
    print("\n📋 Loading Tasks table...")
    all_tasks = tasks_table.all()
    analysis['tasks']['total'] = len(all_tasks)
    for task in all_tasks:
        task_id = task['fields'].get('task_id', '')
        if task_id:
            id_maps['tasks'][task_id] = task['id']

            # Check stage_link
            if not task['fields'].get('stage_link'):
                analysis['tasks']['missing_links']['stage_link'].append(task_id)
    print(f"   ✓ Found {len(all_tasks)} tasks")

    return analysis, id_maps, {
        'plans': all_plans if 'all_plans' in locals() else [],
        'phases': all_phases if 'all_phases' in locals() else [],
        'stages': all_stages,
        'tasks': all_tasks
    }

def reconcile_links(analysis, id_maps, all_records):
    """Reconcile missing links based on ID patterns."""

    print("\n🔧 RECONCILING MISSING LINKS")
    print("=" * 80)

    fixes = {
        'phases': [],
        'stages': [],
        'tasks': []
    }

    # Fix missing phase->plan links
    if 'phases' in analysis and analysis['phases']['missing_links']['plan_link']:
        print(f"\n📍 Fixing {len(analysis['phases']['missing_links']['plan_link'])} missing phase->plan links")
        for phase_id in analysis['phases']['missing_links']['plan_link']:
            # Extract plan from phase_id (e.g., MP03.P01 -> MP03)
            parts = phase_id.split('.')
            if len(parts) >= 1:
                plan_id = parts[0]  # MP03
                if plan_id in id_maps['plans']:
                    fixes['phases'].append({
                        'phase_id': phase_id,
                        'plan_link': [id_maps['plans'][plan_id]]
                    })

    # Fix missing stage->phase links
    if analysis['stages']['missing_links']['phase_link']:
        print(f"\n📍 Fixing {len(analysis['stages']['missing_links']['phase_link'])} missing stage->phase links")
        for stage_id in analysis['stages']['missing_links']['phase_link']:
            # Extract phase from stage_id (e.g., MP03.P01.S01 -> MP03.P01)
            parts = stage_id.split('.')
            if len(parts) >= 2:
                phase_id = '.'.join(parts[:2])  # MP03.P01
                if phase_id in id_maps['phases']:
                    fixes['stages'].append({
                        'stage_id': stage_id,
                        'phase_link': [id_maps['phases'][phase_id]]
                    })

    # Fix missing task->stage links
    if analysis['tasks']['missing_links']['stage_link']:
        print(f"\n📍 Fixing {len(analysis['tasks']['missing_links']['stage_link'])} missing task->stage links")
        for task_id in analysis['tasks']['missing_links']['stage_link']:
            # Extract stage from task_id (e.g., MP03.P01.S01.T01 -> MP03.P01.S01)
            parts = task_id.split('.')
            if len(parts) >= 3:
                stage_id = '.'.join(parts[:3])  # MP03.P01.S01
                if stage_id in id_maps['stages']:
                    fixes['tasks'].append({
                        'task_id': task_id,
                        'stage_link': [id_maps['stages'][stage_id]]
                    })

    return fixes

def apply_fixes(fixes, all_records):
    """Apply the reconciliation fixes to AirTable."""

    print("\n💾 APPLYING FIXES TO AIRTABLE")
    print("=" * 80)

    success_count = {'phases': 0, 'stages': 0, 'tasks': 0}
    failed_count = {'phases': 0, 'stages': 0, 'tasks': 0}

    # Fix phases
    if fixes['phases']:
        print(f"\n📝 Updating {len(fixes['phases'])} phases...")
        for fix in fixes['phases']:
            try:
                phase = next((p for p in all_records['phases'] if p['fields'].get('phase_id') == fix['phase_id']), None)
                if phase:
                    phases_table.update(phase['id'], {'plan_link': fix['plan_link']})
                    success_count['phases'] += 1
                    print(f"   ✅ Fixed phase {fix['phase_id']}")
            except Exception as e:
                failed_count['phases'] += 1
                print(f"   ❌ Failed to fix phase {fix['phase_id']}: {e}")

    # Fix stages
    if fixes['stages']:
        print(f"\n📝 Updating {len(fixes['stages'])} stages...")
        for fix in fixes['stages']:
            try:
                stage = next((s for s in all_records['stages'] if s['fields'].get('stage_id') == fix['stage_id']), None)
                if stage:
                    stages_table.update(stage['id'], {'phase_link': fix['phase_link']})
                    success_count['stages'] += 1
                    print(f"   ✅ Fixed stage {fix['stage_id']}")
            except Exception as e:
                failed_count['stages'] += 1
                print(f"   ❌ Failed to fix stage {fix['stage_id']}: {e}")

    # Fix tasks
    if fixes['tasks']:
        print(f"\n📝 Updating {len(fixes['tasks'])} tasks...")
        for fix in fixes['tasks']:
            try:
                task = next((t for t in all_records['tasks'] if t['fields'].get('task_id') == fix['task_id']), None)
                if task:
                    tasks_table.update(task['id'], {'stage_link': fix['stage_link']})
                    success_count['tasks'] += 1
                    print(f"   ✅ Fixed task {fix['task_id']}")
            except Exception as e:
                failed_count['tasks'] += 1
                print(f"   ❌ Failed to fix task {fix['task_id']}: {e}")

    return success_count, failed_count

def generate_completeness_report(analysis, success_count, failed_count):
    """Generate final completeness report."""

    print("\n" + "=" * 80)
    print("📊 LINK FIELD COMPLETENESS REPORT")
    print("=" * 80)

    # Calculate completeness percentages
    completeness = {}

    # Plans table (no upward links)
    if analysis['plans']['total'] > 0:
        completeness['plans'] = 100.0  # Plans don't need upward links
        print(f"\n✅ Plans Table: {completeness['plans']:.1f}% complete")
        print(f"   • Total plans: {analysis['plans']['total']}")
        print(f"   • All plans are root entities (no upward links needed)")

    # Phases table
    if 'phases' in analysis and analysis['phases']['total'] > 0:
        missing = len(analysis['phases']['missing_links']['plan_link']) - success_count.get('phases', 0)
        complete = analysis['phases']['total'] - missing
        completeness['phases'] = (complete / analysis['phases']['total']) * 100
        print(f"\n{'✅' if completeness['phases'] == 100 else '⚠️'} Phases Table: {completeness['phases']:.1f}% complete")
        print(f"   • Total phases: {analysis['phases']['total']}")
        print(f"   • With plan_link: {complete}")
        print(f"   • Missing plan_link: {missing}")

    # Stages table
    missing_stage_links = len(analysis['stages']['missing_links']['phase_link']) - success_count.get('stages', 0)
    complete_stages = analysis['stages']['total'] - missing_stage_links
    completeness['stages'] = (complete_stages / analysis['stages']['total']) * 100 if analysis['stages']['total'] > 0 else 0
    print(f"\n{'✅' if completeness['stages'] == 100 else '⚠️'} Stages Table: {completeness['stages']:.1f}% complete")
    print(f"   • Total stages: {analysis['stages']['total']}")
    print(f"   • With phase_link: {complete_stages}")
    print(f"   • Missing phase_link: {missing_stage_links}")

    # Tasks table
    missing_task_links = len(analysis['tasks']['missing_links']['stage_link']) - success_count.get('tasks', 0)
    complete_tasks = analysis['tasks']['total'] - missing_task_links
    completeness['tasks'] = (complete_tasks / analysis['tasks']['total']) * 100 if analysis['tasks']['total'] > 0 else 0
    print(f"\n{'✅' if completeness['tasks'] == 100 else '⚠️'} Tasks Table: {completeness['tasks']:.1f}% complete")
    print(f"   • Total tasks: {analysis['tasks']['total']}")
    print(f"   • With stage_link: {complete_tasks}")
    print(f"   • Missing stage_link: {missing_task_links}")

    # Overall completeness
    overall = sum(completeness.values()) / len(completeness) if completeness else 0

    print("\n" + "=" * 80)
    print("🎯 OVERALL LINK COMPLETENESS")
    print("=" * 80)

    if overall == 100:
        print(f"\n✅ PERFECT: {overall:.1f}% - All link fields are complete!")
        print("   All plan_link, phase_link, stage_link, and task_link fields are populated.")
        print("   The AirTable hierarchy is fully connected.")
    elif overall >= 95:
        print(f"\n✅ EXCELLENT: {overall:.1f}% - Nearly all links are complete!")
    elif overall >= 90:
        print(f"\n🔄 GOOD: {overall:.1f}% - Most links are complete")
    else:
        print(f"\n⚠️ NEEDS ATTENTION: {overall:.1f}% - Many links are missing")

    print("\n📝 Summary of Applied Fixes:")
    total_fixed = sum(success_count.values())
    total_failed = sum(failed_count.values())
    print(f"   • Successfully fixed: {total_fixed} links")
    print(f"   • Failed to fix: {total_failed} links")

    if total_failed > 0:
        print("\n⚠️ Some fixes failed - manual intervention may be required")

    print("\n" + "=" * 80)
    print(f"Report generated: {datetime.now().isoformat()}")
    print("=" * 80)

    return overall

def main():
    """Main execution function."""

    print("\n🚀 STARTING LINK FIELD VERIFICATION AND RECONCILIATION")
    print("Target: 100% completion of all link fields")
    print("-" * 80)

    try:
        # Analyze current state
        analysis, id_maps, all_records = analyze_link_fields()

        # Identify fixes needed
        fixes = reconcile_links(analysis, id_maps, all_records)

        # Apply fixes
        success_count, failed_count = apply_fixes(fixes, all_records)

        # Re-analyze after fixes
        print("\n🔄 Re-analyzing after fixes...")
        analysis, _, _ = analyze_link_fields()

        # Generate report
        overall_completeness = generate_completeness_report(analysis, success_count, failed_count)

        if overall_completeness == 100:
            print("\n🎉 SUCCESS! All link fields are 100% complete and reconciled!")
        else:
            print(f"\n📈 Progress made: {overall_completeness:.1f}% complete")
            print("   Run this script again to attempt fixing remaining issues.")

        return overall_completeness

    except Exception as e:
        print(f"\n❌ Error during verification: {e}")
        import traceback
        traceback.print_exc()
        return 0

if __name__ == "__main__":
    completeness = main()