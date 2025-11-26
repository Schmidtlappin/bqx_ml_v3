#!/usr/bin/env python3
"""
Fix all plan_link fields throughout AirTable.
Since there IS a Plans table, we need to properly link to it.
"""

import os
import json
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
plans_table = base.table('Plans')
phases_table = base.table('Phases')
tasks_table = base.table('Tasks')

def fix_plan_links():
    """Fix all plan_link fields."""
    print("=" * 80)
    print("FIXING PLAN_LINK FIELDS")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 80)

    # Get the Plans record for MP03
    print("\n📥 Loading Plans table...")
    plans = plans_table.all()
    print(f"  Found {len(plans)} plans")

    # Find MP03 plan record
    mp03_record = None
    for plan in plans:
        plan_id = plan['fields'].get('plan_id', '')
        plan_name = plan['fields'].get('name', '')
        print(f"  Plan: {plan_id} - {plan_name}")

        if plan_id == 'MP03' or 'MP03' in plan_name or 'BQX' in plan_name.upper():
            mp03_record = plan
            print(f"  ✅ Found BQX ML V3 plan record: {plan['id']}")
            break

    if not mp03_record:
        # Try to find any plan that looks like BQX ML
        for plan in plans:
            fields = plan['fields']
            if any(term in str(fields).upper() for term in ['BQX', 'ML', 'V3']):
                mp03_record = plan
                print(f"  ✅ Found likely BQX ML plan: {plan['id']}")
                break

    if not mp03_record:
        print("  ❌ Could not find BQX ML V3 plan record")
        print("  Will use first available plan record")
        if plans:
            mp03_record = plans[0]
            print(f"  Using plan: {mp03_record['id']}")
        else:
            print("  ❌ No plans found in Plans table")
            return False

    # Fix Phase plan_links
    print("\n📋 Fixing Phase plan_links...")
    phases = phases_table.all()
    phases_fixed = 0

    for phase in phases:
        phase_id = phase['fields'].get('phase_id')
        if not phase_id:
            continue

        # Check if phase belongs to MP03
        if not phase_id.startswith('MP03'):
            continue

        # Check if plan_link is missing or incorrect
        current_plan_link = phase['fields'].get('plan_link', [])

        if not current_plan_link or (isinstance(current_plan_link, list) and mp03_record['id'] not in current_plan_link):
            try:
                phases_table.update(phase['id'], {'plan_link': [mp03_record['id']]})
                phases_fixed += 1
                print(f"  ✅ Fixed {phase_id} plan_link")
            except Exception as e:
                print(f"  ❌ Failed to fix {phase_id}: {e}")

    # Fix Task plan_links
    print("\n📋 Fixing Task plan_links...")
    tasks = tasks_table.all()
    tasks_fixed = 0

    for task in tasks:
        task_id = task['fields'].get('task_id')
        if not task_id:
            continue

        # Check if task belongs to MP03
        if not task_id.startswith('MP03'):
            continue

        # Check if plan_link is missing or incorrect
        current_plan_link = task['fields'].get('plan_link', [])

        if not current_plan_link or (isinstance(current_plan_link, list) and mp03_record['id'] not in current_plan_link):
            try:
                tasks_table.update(task['id'], {'plan_link': [mp03_record['id']]})
                tasks_fixed += 1
                print(f"  ✅ Fixed {task_id} plan_link")
            except Exception as e:
                print(f"  ❌ Failed to fix {task_id}: {e}")

    # Summary
    print("\n" + "=" * 80)
    print("PLAN LINK FIX SUMMARY")
    print("=" * 80)

    print(f"\n📊 Results:")
    print(f"  Plan record used: {mp03_record['id']}")
    print(f"  Phases fixed: {phases_fixed}")
    print(f"  Tasks fixed: {tasks_fixed}")

    total_fixed = phases_fixed + tasks_fixed

    if total_fixed > 0:
        print(f"\n✅ SUCCESS! Fixed {total_fixed} plan_link fields")
    else:
        print(f"\n✅ All plan_link fields were already correct")

    # Final verification
    print("\n📋 Final Verification...")

    # Re-check
    phases = phases_table.all()
    tasks = tasks_table.all()

    issues = []

    for phase in phases:
        if phase['fields'].get('phase_id', '').startswith('MP03'):
            if not phase['fields'].get('plan_link'):
                issues.append(f"Phase {phase['fields'].get('phase_id')} still missing plan_link")

    for task in tasks:
        if task['fields'].get('task_id', '').startswith('MP03'):
            if not task['fields'].get('plan_link'):
                issues.append(f"Task {task['fields'].get('task_id')} still missing plan_link")

    if issues:
        print(f"  ⚠️  {len(issues)} issues remaining:")
        for issue in issues[:5]:
            print(f"    • {issue}")
    else:
        print("  ✅ All MP03 entities have plan_link!")

    print(f"\n🏁 Completed at: {datetime.now().isoformat()}")

    return len(issues) == 0

def main():
    """Main entry point."""
    success = fix_plan_links()

    if success:
        print("\n✅ SUCCESS! All plan_link fields are complete")
        return 0
    else:
        print("\n⚠️  Some plan_link issues remain")
        return 1

if __name__ == "__main__":
    exit(main())