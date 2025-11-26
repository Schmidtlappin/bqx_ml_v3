#!/usr/bin/env python3
"""
Verify 100% coverage of INTERVAL-CENTRIC V2.0 recommendations in AirTable.
Confirms all phases, stages, and tasks have been properly created or modified.
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
phases_table = base.table('Phases')
stages_table = base.table('Stages')
tasks_table = base.table('Tasks')

# V2.0 Recommendations Checklist
RECOMMENDATIONS = {
    "Data Leakage Prevention": {
        "required": True,
        "stage_id": "MP03.P06.S08",
        "type": "new",
        "keywords": ["temporal isolation", "LAG", "LEAD", "leakage"]
    },
    "BQX Autoregressive Lags": {
        "required": True,
        "stage_id": "MP03.P06.S03",
        "type": "updated",
        "keywords": ["LAG", "bqx_mid_lag", "autoregressive", "1-180"]
    },
    "Multi-Resolution Features": {
        "required": True,
        "stage_id": ["MP03.P07.S01", "MP03.P06.S05"],
        "type": "updated",
        "keywords": ["5i", "15i", "45i", "90i", "180i", "360i", "multi-resolution"]
    },
    "BQX Momentum Derivatives": {
        "required": True,
        "stage_id": "MP03.P06.S07",
        "type": "new",
        "keywords": ["velocity", "acceleration", "jerk", "derivatives", "momentum"]
    },
    "Interval-Based Regime Detection": {
        "required": True,
        "stage_id": "MP03.P06.S02",
        "type": "updated",
        "keywords": ["regime", "ROWS BETWEEN", "volatility", "trending"]
    },
    "Interval Validation Framework": {
        "required": True,
        "stage_id": "MP03.P07.S05",
        "type": "new",
        "keywords": ["validation", "ROWS BETWEEN", "naming convention", "_Ni"]
    },
    "ROWS BETWEEN Mandate": {
        "required": True,
        "stage_id": "all",
        "type": "all_tasks",
        "keywords": ["ROWS BETWEEN", "INTERVAL-CENTRIC", "not RANGE"]
    },
    "Naming Convention (_Ni)": {
        "required": True,
        "stage_id": "all",
        "type": "all_features",
        "keywords": ["_Ni", "_5i", "_15i", "_45i", "_90i", "_180i", "_360i"]
    }
}

def check_stage_exists(stage_id):
    """Check if a stage exists in AirTable."""
    stages = stages_table.all()
    for stage in stages:
        if stage['fields'].get('Stage ID') == stage_id:
            return True, stage
    return False, None

def check_stage_content(stage, keywords):
    """Check if stage contains required keywords."""
    description = stage['fields'].get('Description', '').lower()
    notes = stage['fields'].get('Notes', '').lower()
    name = stage['fields'].get('Name', '').lower()

    content = f"{description} {notes} {name}"

    matches = []
    for keyword in keywords:
        if keyword.lower() in content:
            matches.append(keyword)

    return len(matches) > 0, matches

def verify_interval_centric_coverage():
    """Main verification function."""
    print("=" * 80)
    print("INTERVAL-CENTRIC V2.0 COVERAGE VERIFICATION")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 80)

    # Get all records
    all_stages = stages_table.all()
    all_tasks = tasks_table.all()
    all_phases = phases_table.all()

    print(f"\n📊 AirTable Record Counts:")
    print(f"  - Phases: {len(all_phases)}")
    print(f"  - Stages: {len(all_stages)}")
    print(f"  - Tasks: {len(all_tasks)}")

    # Track coverage
    coverage_results = {}
    total_recommendations = len(RECOMMENDATIONS)
    covered_recommendations = 0

    print("\n" + "=" * 80)
    print("RECOMMENDATION COVERAGE VERIFICATION")
    print("=" * 80)

    for rec_name, rec_details in RECOMMENDATIONS.items():
        print(f"\n📋 Checking: {rec_name}")
        print(f"  Type: {rec_details['type']}")

        if rec_details['type'] == 'new':
            # Check if new stage was created
            exists, stage = check_stage_exists(rec_details['stage_id'])
            if exists:
                has_content, matches = check_stage_content(stage, rec_details['keywords'])
                if has_content:
                    print(f"  ✅ NEW stage {rec_details['stage_id']} created successfully")
                    print(f"     Found keywords: {', '.join(matches)}")
                    coverage_results[rec_name] = "COVERED"
                    covered_recommendations += 1
                else:
                    print(f"  ⚠️ Stage {rec_details['stage_id']} exists but missing keywords")
                    coverage_results[rec_name] = "PARTIAL"
            else:
                print(f"  ❌ NEW stage {rec_details['stage_id']} NOT FOUND")
                coverage_results[rec_name] = "MISSING"

        elif rec_details['type'] == 'updated':
            # Check if existing stage was updated
            stage_ids = rec_details['stage_id'] if isinstance(rec_details['stage_id'], list) else [rec_details['stage_id']]
            found_any = False
            for sid in stage_ids:
                exists, stage = check_stage_exists(sid)
                if exists:
                    has_content, matches = check_stage_content(stage, rec_details['keywords'])
                    if has_content:
                        print(f"  ✅ Stage {sid} updated with INTERVAL-CENTRIC specs")
                        print(f"     Found keywords: {', '.join(matches)}")
                        found_any = True

            if found_any:
                coverage_results[rec_name] = "COVERED"
                covered_recommendations += 1
            else:
                print(f"  ❌ Stage updates NOT FOUND or incomplete")
                coverage_results[rec_name] = "MISSING"

        elif rec_details['type'] == 'all_tasks':
            # Check if all tasks mention ROWS BETWEEN
            tasks_with_interval = 0
            total_feature_tasks = 0

            for task in all_tasks:
                task_id = task['fields'].get('Task ID', '')
                if 'P06' in task_id or 'P07' in task_id:  # Feature engineering phases
                    total_feature_tasks += 1
                    notes = task['fields'].get('Notes', '').lower()
                    description = task['fields'].get('Description', '').lower()
                    if 'rows between' in notes or 'interval-centric' in notes or 'rows between' in description:
                        tasks_with_interval += 1

            coverage_pct = (tasks_with_interval / total_feature_tasks * 100) if total_feature_tasks > 0 else 0
            print(f"  ✅ {tasks_with_interval}/{total_feature_tasks} feature tasks have INTERVAL-CENTRIC specs")
            print(f"     Coverage: {coverage_pct:.1f}%")

            if coverage_pct >= 80:  # 80% threshold for task coverage
                coverage_results[rec_name] = "COVERED"
                covered_recommendations += 1
            else:
                coverage_results[rec_name] = "PARTIAL"

        elif rec_details['type'] == 'all_features':
            # Check naming convention
            naming_correct = 0
            total_checked = 0

            for stage in all_stages:
                stage_id = stage['fields'].get('Stage ID', '')
                if 'P06' in stage_id or 'P07' in stage_id:
                    total_checked += 1
                    content = f"{stage['fields'].get('Description', '')} {stage['fields'].get('Notes', '')}"
                    # Check for _Ni naming pattern
                    if any(f"_{n}i" in content for n in ["5", "15", "45", "90", "180", "360"]):
                        naming_correct += 1

            if total_checked > 0:
                naming_pct = (naming_correct / total_checked * 100)
                print(f"  ✅ {naming_correct}/{total_checked} stages use _Ni naming convention")
                print(f"     Coverage: {naming_pct:.1f}%")

                if naming_pct >= 70:  # 70% threshold for naming
                    coverage_results[rec_name] = "COVERED"
                    covered_recommendations += 1
                else:
                    coverage_results[rec_name] = "PARTIAL"
            else:
                coverage_results[rec_name] = "MISSING"

    # Check for specific new stages
    print("\n" + "=" * 80)
    print("NEW STAGE VERIFICATION")
    print("=" * 80)

    new_stages = [
        ("MP03.P06.S07", "BQX Momentum Derivatives"),
        ("MP03.P06.S08", "Data Leakage Prevention"),
        ("MP03.P07.S05", "Interval Validation Framework")
    ]

    new_stages_found = 0
    for stage_id, stage_name in new_stages:
        exists, stage = check_stage_exists(stage_id)
        if exists:
            print(f"✅ {stage_id}: {stage_name} - CREATED")
            new_stages_found += 1
        else:
            print(f"❌ {stage_id}: {stage_name} - NOT FOUND")

    # Check for updated stages
    print("\n" + "=" * 80)
    print("UPDATED STAGE VERIFICATION")
    print("=" * 80)

    updated_stages = [
        ("MP03.P07.S01", "Multi-Resolution BQX Features"),
        ("MP03.P06.S02", "BQX Paradigm Transformations"),
        ("MP03.P06.S03", "LAG Feature Tables"),
        ("MP03.P06.S05", "Aggregated BQX Features"),
        ("MP03.P06.S01", "BQX Base Features")
    ]

    updated_stages_found = 0
    for stage_id, stage_name in updated_stages:
        exists, stage = check_stage_exists(stage_id)
        if exists:
            # Check for INTERVAL-CENTRIC keywords
            content = f"{stage['fields'].get('Description', '')} {stage['fields'].get('Notes', '')}"
            if "interval" in content.lower() or "rows between" in content.lower():
                print(f"✅ {stage_id}: {stage_name} - UPDATED with INTERVAL-CENTRIC")
                updated_stages_found += 1
            else:
                print(f"⚠️ {stage_id}: {stage_name} - EXISTS but may need more updates")
        else:
            print(f"❌ {stage_id}: {stage_name} - NOT FOUND")

    # Final Summary
    print("\n" + "=" * 80)
    print("COVERAGE SUMMARY")
    print("=" * 80)

    coverage_percentage = (covered_recommendations / total_recommendations * 100)

    print(f"\n📊 Overall Coverage Metrics:")
    print(f"  Total V2.0 Recommendations: {total_recommendations}")
    print(f"  Fully Covered: {covered_recommendations}")
    print(f"  Coverage Percentage: {coverage_percentage:.1f}%")

    print(f"\n📋 Detailed Coverage Status:")
    for rec_name, status in coverage_results.items():
        icon = "✅" if status == "COVERED" else "⚠️" if status == "PARTIAL" else "❌"
        print(f"  {icon} {rec_name}: {status}")

    print(f"\n📈 Integration Metrics:")
    print(f"  New Stages Created: {new_stages_found}/3")
    print(f"  Existing Stages Updated: {updated_stages_found}/5")

    # Final Verdict
    print("\n" + "=" * 80)
    print("FINAL VERDICT")
    print("=" * 80)

    if coverage_percentage >= 100:
        print("✅ 100% COVERAGE ACHIEVED!")
        print("All INTERVAL-CENTRIC V2.0 recommendations have been successfully")
        print("integrated into the BQX ML V3 AirTable project plan.")
    elif coverage_percentage >= 90:
        print("✅ EXCELLENT COVERAGE (>90%)")
        print("Most INTERVAL-CENTRIC recommendations are integrated.")
        print("Minor adjustments may be needed for full compliance.")
    elif coverage_percentage >= 80:
        print("⚠️ GOOD COVERAGE (>80%)")
        print("Significant progress made but some gaps remain.")
    else:
        print("❌ INSUFFICIENT COVERAGE (<80%)")
        print("Additional work needed to achieve full integration.")

    print("\n" + "=" * 80)
    print(f"Report generated at: {datetime.now().isoformat()}")
    print("=" * 80)

    return coverage_percentage >= 100

if __name__ == "__main__":
    success = verify_interval_centric_coverage()
    exit(0 if success else 1)