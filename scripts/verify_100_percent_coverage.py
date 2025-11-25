#!/usr/bin/env python3
"""
Verify 100% coverage of all gaps in AirTable project plan
"""

import requests
import json
import time

# Load credentials
with open('/home/micha/bqx_ml_v3/.secrets/github_secrets.json') as f:
    secrets = json.load(f)

API_KEY = secrets['secrets']['AIRTABLE_API_KEY']['value']
BASE_ID = secrets['secrets']['AIRTABLE_BASE_ID']['value']

headers = {
    'Authorization': f'Bearer {API_KEY}',
    'Content-Type': 'application/json'
}

STAGES_TABLE = 'tblxnuvF8O7yH1dB4'

# Define all gaps that need coverage
REQUIRED_GAP_COVERAGE = {
    "Intelligence Architecture": [
        "Create 7 Intelligence JSON Files",
        "Implement IntelligenceManager Class"
    ],
    "GitHub Secrets": [
        "Deploy All GitHub Secrets"
    ],
    "GCP Infrastructure": [
        "Create BigQuery Datasets",
        "Deploy Vertex AI Infrastructure"
    ],
    "Data Pipelines": [
        "Build Real-Time Data Ingestion",
        "Implement Historical Data Backfill"
    ],
    "Feature Engineering": [
        "Implement BQX Paradigm Feature Generation",
        "Create Feature Store"
    ],
    "Model Implementation": [
        "Implement All 5 Model Algorithms",
        "Build Model Training and Evaluation"
    ],
    "Production APIs": [
        "Deploy REST APIs",
        "Implement WebSocket Streaming"
    ],
    "Testing": [
        "Write 2000+ Unit and Integration Tests",
        "Implement Continuous Testing"
    ],
    "Monitoring": [
        "Deploy Comprehensive Monitoring",
        "Implement Model Performance Monitoring"
    ],
    "Security": [
        "Implement End-to-End Encryption",
        "Build Comprehensive Security Controls"
    ]
}

def get_all_stages():
    """Fetch all stages from AirTable"""
    url = f'https://api.airtable.com/v0/{BASE_ID}/{STAGES_TABLE}'

    all_stages = []
    offset = None

    while True:
        params = {
            'filterByFormula': 'FIND("S03", {stage_id}) > 0',
            'pageSize': 100
        }

        if offset:
            params['offset'] = offset

        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            data = response.json()
            records = data.get('records', [])
            all_stages.extend(records)

            offset = data.get('offset')
            if not offset:
                break
        else:
            break

    return all_stages

def check_coverage(stages):
    """Check if all gaps are covered"""
    coverage_report = {}

    # Extract stage names and descriptions
    stage_content = []
    for stage in stages:
        fields = stage['fields']
        stage_id = fields.get('stage_id', '')
        name = fields.get('name', '')
        description = fields.get('description', '')
        score = fields.get('record_score', 0)

        stage_content.append({
            'id': stage_id,
            'name': name,
            'description': description,
            'score': score
        })

    # Check each required gap
    for gap_category, requirements in REQUIRED_GAP_COVERAGE.items():
        coverage_report[gap_category] = {}

        for requirement in requirements:
            found = False
            matching_stages = []

            for stage in stage_content:
                # Check if requirement is covered in stage name or description
                if (requirement.lower() in stage['name'].lower() or
                    requirement.lower() in stage['description'].lower()):
                    found = True
                    matching_stages.append({
                        'id': stage['id'],
                        'name': stage['name'][:60],
                        'score': stage['score']
                    })

            coverage_report[gap_category][requirement] = {
                'covered': found,
                'stages': matching_stages
            }

    return coverage_report

def calculate_metrics(stages):
    """Calculate project metrics"""
    total_stages = len(stages)

    # Score distribution
    score_distribution = {
        '95+': 0,
        '90-94': 0,
        '85-89': 0,
        '80-84': 0,
        '<80': 0
    }

    for stage in stages:
        score = stage['fields'].get('record_score', 0)
        if score >= 95:
            score_distribution['95+'] += 1
        elif score >= 90:
            score_distribution['90-94'] += 1
        elif score >= 85:
            score_distribution['85-89'] += 1
        elif score >= 80:
            score_distribution['80-84'] += 1
        else:
            score_distribution['<80'] += 1

    # Phase distribution
    phase_count = {}
    for stage in stages:
        stage_id = stage['fields'].get('stage_id', '')
        if '.' in stage_id:
            phase = '.'.join(stage_id.split('.')[:2])
            phase_count[phase] = phase_count.get(phase, 0) + 1

    return {
        'total_stages': total_stages,
        'score_distribution': score_distribution,
        'phase_count': phase_count
    }

def main():
    print("="*80)
    print("VERIFYING 100% GAP COVERAGE IN AIRTABLE")
    print("="*80)

    # Fetch all stages
    print("\n📊 Fetching all stages from AirTable...")
    stages = get_all_stages()
    print(f"✅ Found {len(stages)} total stages")

    # Calculate metrics
    metrics = calculate_metrics(stages)

    print("\n" + "-"*80)
    print("PROJECT METRICS")
    print("-"*80)

    print(f"\n📈 Total Stages: {metrics['total_stages']}")

    print("\n📊 Score Distribution:")
    for score_range, count in metrics['score_distribution'].items():
        percentage = (count / metrics['total_stages']) * 100
        bar = "█" * int(percentage / 2)
        print(f"  {score_range:6s}: {count:3d} ({percentage:5.1f}%) {bar}")

    print("\n📂 Stages per Phase:")
    for phase in sorted(metrics['phase_count'].keys()):
        print(f"  {phase}: {metrics['phase_count'][phase]} stages")

    # Check coverage
    print("\n" + "-"*80)
    print("GAP COVERAGE ANALYSIS")
    print("-"*80)

    coverage = check_coverage(stages)

    total_gaps = 0
    covered_gaps = 0

    for category, requirements in coverage.items():
        print(f"\n🔍 {category}:")
        for requirement, status in requirements.items():
            total_gaps += 1
            if status['covered']:
                covered_gaps += 1
                print(f"  ✅ {requirement}")
                for stage in status['stages']:
                    print(f"     • {stage['id']}: {stage['name']} (Score: {stage['score']})")
            else:
                print(f"  ❌ {requirement} - NOT COVERED")

    # Calculate coverage percentage
    coverage_percentage = (covered_gaps / total_gaps) * 100

    print("\n" + "="*80)
    print("COVERAGE SUMMARY")
    print("="*80)

    print(f"\n📊 Gap Coverage: {covered_gaps}/{total_gaps} ({coverage_percentage:.1f}%)")

    if coverage_percentage == 100:
        print("\n🎉 ACHIEVEMENT UNLOCKED: 100% GAP COVERAGE!")
        print("✅ All identified gaps have been addressed in the project plan")
        print("✅ Every implementation requirement has corresponding stages")
        print("✅ The project plan is now COMPLETE and COMPREHENSIVE")

        # Check if all stages are scoring 90+
        low_scoring = [s for s in stages if s['fields'].get('record_score', 0) < 90]
        if not low_scoring:
            print("\n🏆 BONUS ACHIEVEMENT: ALL STAGES SCORING 90+!")
            print("✅ Every single stage meets quality threshold")
            print("✅ Project plan is production-ready")
        else:
            print(f"\n⚠️ {len(low_scoring)} stages still scoring below 90")
            print("   Run remediation to fix these stages")
    else:
        uncovered = []
        for category, requirements in coverage.items():
            for requirement, status in requirements.items():
                if not status['covered']:
                    uncovered.append(f"{category}: {requirement}")

        print(f"\n⚠️ Coverage incomplete - {100 - coverage_percentage:.1f}% gaps remaining")
        print("\n🔴 Uncovered gaps:")
        for gap in uncovered:
            print(f"  • {gap}")
        print("\n💡 Action Required: Create stages to address uncovered gaps")

    print("\n" + "-"*80)
    print("PROJECT COMPLETENESS CHECKLIST")
    print("-"*80)

    checklist = {
        "Planning Phase": len(stages) > 50,
        "Gap Coverage": coverage_percentage == 100,
        "Quality Scores": all(s['fields'].get('record_score', 0) >= 90 for s in stages),
        "Intelligence Architecture": any("intelligence" in s['fields'].get('name', '').lower() for s in stages),
        "GCP Infrastructure": any("bigquery" in s['fields'].get('name', '').lower() for s in stages),
        "Data Pipelines": any("ingestion" in s['fields'].get('name', '').lower() for s in stages),
        "Feature Engineering": any("feature" in s['fields'].get('name', '').lower() for s in stages),
        "Model Training": any("model" in s['fields'].get('name', '').lower() for s in stages),
        "Production APIs": any("api" in s['fields'].get('name', '').lower() or "endpoint" in s['fields'].get('name', '').lower() for s in stages),
        "Testing Framework": any("test" in s['fields'].get('name', '').lower() for s in stages),
        "Monitoring System": any("monitoring" in s['fields'].get('name', '').lower() for s in stages),
        "Security Controls": any("security" in s['fields'].get('name', '').lower() or "encryption" in s['fields'].get('name', '').lower() for s in stages),
    }

    all_complete = all(checklist.values())

    for item, status in checklist.items():
        icon = "✅" if status else "❌"
        print(f"  {icon} {item}")

    if all_complete:
        print("\n🎊 PERFECT SCORE: PROJECT PLAN IS 100% COMPLETE!")
        print("✨ Ready to begin implementation phase")
    else:
        incomplete = [k for k, v in checklist.items() if not v]
        print(f"\n📋 {len(incomplete)} items need attention:")
        for item in incomplete:
            print(f"  • {item}")

    print("\n" + "="*80)

if __name__ == "__main__":
    main()