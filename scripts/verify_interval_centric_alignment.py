#!/usr/bin/env python3
"""
Verify that BQX ML V3 project plan in AirTable is aligned with INTERVAL-CENTRIC precision.
Confirms that terminology correctly references future interval predictions of BQX values.
"""

import os
import json
from datetime import datetime
from pyairtable import Api
from collections import defaultdict

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

def verify_interval_centric_alignment():
    """Verify comprehensive alignment with interval-centric precision."""
    print("=" * 80)
    print("VERIFYING INTERVAL-CENTRIC ALIGNMENT IN AIRTABLE")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 80)

    # Tracking metrics
    metrics = {
        'total_records': 0,
        'interval_references': 0,
        'rows_between_references': 0,
        'incorrect_time_references': 0,
        'correct_predictions': 0,
        'vague_predictions': 0,
        'interval_notation': 0
    }

    issues = []

    # Key interval-centric patterns
    interval_patterns = [
        'interval', 'rows between', 'n+45', 'n+90', 'n+180',
        'n+360', 'n+720', 'n+1440', 'n+2880', '45i', '90i',
        '180i', '360i', 'interval-centric', 'interval-based',
        'specific future intervals', 'interval horizons'
    ]

    # Time-based patterns (should be avoided)
    time_patterns = [
        'minutes ahead', 'hours ahead', 'minutes later',
        'hours later', 'time-based', 'temporal window',
        'range between', 'time period', 'future time'
    ]

    # Correct prediction terminology
    correct_prediction_terms = [
        'predict bqx values at specific future intervals',
        'predict bqx at future intervals',
        'predictions at specific interval horizons',
        'predict at interval n+',
        'bqx at interval'
    ]

    # Vague prediction terminology
    vague_prediction_terms = [
        'predict future bqx values',
        'forecast bqx',
        'future predictions',
        'predict ahead'
    ]

    print("\n📊 Analyzing All Records...")
    print("=" * 40)

    # Analyze Phases
    print("\n🔍 Checking Phases...")
    phases = phases_table.all()

    for phase in phases:
        metrics['total_records'] += 1
        phase_id = phase['fields'].get('phase_id', '')
        desc = phase['fields'].get('description', '').lower()
        notes = (phase['fields'].get('notes', '') or '').lower()
        content = f"{desc} {notes}"

        # Check for interval references
        for pattern in interval_patterns:
            if pattern in content:
                metrics['interval_references'] += 1
                break

        # Check for time-based references (issues)
        for pattern in time_patterns:
            if pattern in content:
                metrics['incorrect_time_references'] += 1
                issues.append(f"Phase {phase_id}: Contains time-based reference '{pattern}'")
                break

    # Analyze Stages
    print("🔍 Checking Stages...")
    stages = stages_table.all()

    model_related_stages = []
    for stage in stages:
        metrics['total_records'] += 1
        stage_id = stage['fields'].get('stage_id', '')
        name = stage['fields'].get('name', '').lower()
        desc = stage['fields'].get('description', '').lower()
        notes = (stage['fields'].get('notes', '') or '').lower()
        content = f"{name} {desc} {notes}"

        # Track model-related stages
        if any(term in content for term in ['model', 'predict', 'train', 'evaluation']):
            model_related_stages.append(stage_id)

        # Check for ROWS BETWEEN
        if 'rows between' in content:
            metrics['rows_between_references'] += 1

        # Check for interval notation
        if any(notation in content for notation in ['n+45', 'n+90', '45i', '90i']):
            metrics['interval_notation'] += 1

        # Check prediction terminology
        for term in correct_prediction_terms:
            if term in content:
                metrics['correct_predictions'] += 1
                break

        for term in vague_prediction_terms:
            if term in content and not any(ct in content for ct in correct_prediction_terms):
                metrics['vague_predictions'] += 1
                issues.append(f"Stage {stage_id}: Uses vague prediction terminology")
                break

        # Check for time-based issues
        for pattern in time_patterns:
            if pattern in content:
                metrics['incorrect_time_references'] += 1
                issues.append(f"Stage {stage_id}: Contains time-based reference '{pattern}'")
                break

    # Analyze Tasks (focus on critical ones)
    print("🔍 Checking Tasks...")
    tasks = tasks_table.all()

    critical_task_count = 0
    for task in tasks:
        task_id = task['fields'].get('task_id', '')

        # Focus on model and prediction tasks
        if any(ms in task_id for ms in model_related_stages):
            metrics['total_records'] += 1
            critical_task_count += 1

            desc = task['fields'].get('description', '').lower()
            notes = (task['fields'].get('notes', '') or '').lower()
            content = f"{desc} {notes}"

            # Check for interval references
            for pattern in interval_patterns:
                if pattern in content:
                    metrics['interval_references'] += 1
                    break

            # Check for time-based issues
            for pattern in time_patterns:
                if pattern in content:
                    metrics['incorrect_time_references'] += 1
                    issues.append(f"Task {task_id}: Contains time-based reference '{pattern}'")
                    break

    # Generate Report
    print("\n" + "=" * 80)
    print("ALIGNMENT VERIFICATION REPORT")
    print("=" * 80)

    print(f"\n📊 Metrics Summary:")
    print(f"  Total records analyzed: {metrics['total_records']}")
    print(f"  Records with interval references: {metrics['interval_references']}")
    print(f"  ROWS BETWEEN references: {metrics['rows_between_references']}")
    print(f"  Interval notation usage (N+45, 90i, etc.): {metrics['interval_notation']}")
    print(f"  Correct prediction terminology: {metrics['correct_predictions']}")
    print(f"  Vague prediction terminology: {metrics['vague_predictions']}")
    print(f"  Incorrect time references: {metrics['incorrect_time_references']}")

    # Calculate alignment score
    positive_score = (
        metrics['interval_references'] * 2 +
        metrics['rows_between_references'] * 3 +
        metrics['interval_notation'] * 3 +
        metrics['correct_predictions'] * 5
    )

    negative_score = (
        metrics['incorrect_time_references'] * 5 +
        metrics['vague_predictions'] * 2
    )

    max_score = metrics['total_records'] * 10
    alignment_score = max(0, min(100, (positive_score - negative_score) / max_score * 100))

    print(f"\n🎯 Alignment Score: {alignment_score:.1f}%")

    if alignment_score >= 90:
        status = "✅ EXCELLENT"
        status_desc = "Project plan is well-aligned with interval-centric precision"
    elif alignment_score >= 75:
        status = "✅ GOOD"
        status_desc = "Project plan shows strong interval-centric alignment"
    elif alignment_score >= 60:
        status = "⚠️ MODERATE"
        status_desc = "Some improvements needed for full interval-centric alignment"
    else:
        status = "❌ NEEDS IMPROVEMENT"
        status_desc = "Significant updates required for interval-centric alignment"

    print(f"\n📈 Status: {status}")
    print(f"   {status_desc}")

    # Show issues if any
    if issues:
        print(f"\n⚠️ Issues Found ({len(issues)}):")
        for i, issue in enumerate(issues[:10], 1):
            print(f"  {i}. {issue}")
        if len(issues) > 10:
            print(f"  ... and {len(issues) - 10} more issues")
    else:
        print("\n✅ No terminology issues found!")

    # Key confirmations
    print("\n" + "=" * 80)
    print("KEY CONFIRMATIONS")
    print("=" * 80)

    confirmations = []

    # Check for specific critical elements
    print("\n✅ Checking Critical Elements:")

    # 1. Model objectives restated
    model_stages_correct = metrics['correct_predictions'] > 0
    if model_stages_correct:
        confirmations.append("Model objectives correctly state 'predict BQX at specific future intervals'")

    # 2. ROWS BETWEEN usage
    if metrics['rows_between_references'] > 10:
        confirmations.append("ROWS BETWEEN is widely used for interval-based windows")

    # 3. Interval notation
    if metrics['interval_notation'] > 5:
        confirmations.append("Interval notation (N+45, 90i, etc.) is properly adopted")

    # 4. No time-based calculations
    if metrics['incorrect_time_references'] == 0:
        confirmations.append("No incorrect time-based references found")
    elif metrics['incorrect_time_references'] < 5:
        confirmations.append("Minimal time-based references (mostly corrected)")

    for conf in confirmations:
        print(f"  ✓ {conf}")

    # Recommendations
    print("\n📋 Recommendations:")
    if metrics['vague_predictions'] > 0:
        print("  1. Update remaining vague prediction terminology")
        print("     Change: 'predict future BQX' → 'predict BQX at specific future intervals'")

    if metrics['incorrect_time_references'] > 0:
        print("  2. Replace time-based references with interval-based")
        print("     Change: '90 minutes ahead' → 'at interval N+90'")

    if metrics['interval_notation'] < 10:
        print("  3. Increase use of standard interval notation")
        print("     Use: N+45, N+90, 45i, 90i, etc.")

    # Final verdict
    print("\n" + "=" * 80)
    print("FINAL VERDICT")
    print("=" * 80)

    if alignment_score >= 75 and metrics['incorrect_time_references'] < 5:
        print("\n✅ **CONFIRMED**: BQX ML V3 project plan in AirTable is")
        print("   properly aligned with INTERVAL-CENTRIC precision")
        print("   • Models correctly target specific future intervals")
        print("   • Terminology emphasizes interval-based predictions")
        print("   • ROWS BETWEEN paradigm is well-established")
        return True
    else:
        print("\n⚠️ **PARTIAL ALIGNMENT**: BQX ML V3 project plan needs")
        print("   additional updates for full interval-centric precision")
        print("   • Run update scripts to fix remaining issues")
        print("   • Review and update vague terminology")
        return False

def main():
    """Main execution."""
    print("=" * 80)
    print("INTERVAL-CENTRIC ALIGNMENT VERIFICATION")
    print("=" * 80)

    # Run verification
    aligned = verify_interval_centric_alignment()

    print("\n" + "=" * 80)
    print("VERIFICATION COMPLETE")
    print("=" * 80)

    if aligned:
        print("\n🎉 SUCCESS! The BQX ML V3 project plan is properly aligned")
        print("   with interval-centric precision for predicting BQX values")
        print("   at specific future intervals.")
    else:
        print("\n📋 Action Required: Run update scripts to achieve full alignment")
        print("   Scripts available:")
        print("   • update_model_objectives_interval_centric.py")
        print("   • update_airtable_interval_centric_v2.py")

    print(f"\n🏁 Verification completed at: {datetime.now().isoformat()}")

    return 0 if aligned else 1

if __name__ == "__main__":
    exit(main())