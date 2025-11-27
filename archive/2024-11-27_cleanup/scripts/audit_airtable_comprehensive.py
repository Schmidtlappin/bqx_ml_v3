#!/usr/bin/env python3
"""
Comprehensive AirTable audit to find all mentions of features and technical specifications.
"""

import os
import json
import requests
import subprocess
from collections import defaultdict
import re

# Function to get secret from GCP
def get_secret(secret_name):
    """Fetch secret from GCP Secrets Manager"""
    try:
        result = subprocess.run(
            f'gcloud secrets versions access latest --secret="{secret_name}" --project=bqx-ml',
            shell=True,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None

# AirTable Configuration
BASE_ID = os.getenv('AIRTABLE_BASE_ID') or get_secret('bqx-ml-airtable-base-id')
API_KEY = os.getenv('AIRTABLE_API_KEY') or get_secret('bqx-ml-airtable-token')

TABLE_NAME = 'tblQ9VXdTgZiIR6H2'  # Tasks table ID
headers = {
    'Authorization': f'Bearer {API_KEY}',
    'Content-Type': 'application/json'
}

def get_all_tasks():
    """Fetch all tasks from AirTable"""
    url = f'https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}'
    records = []
    offset = None

    while True:
        params = {}
        if offset:
            params['offset'] = offset

        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            print(f"Error fetching records: {response.status_code}")
            print(response.text)
            break

        data = response.json()
        records.extend(data.get('records', []))

        offset = data.get('offset')
        if not offset:
            break

    return records

def comprehensive_analysis(records):
    """Deep analysis of all records for any feature mentions"""

    stats = {
        'total_records': len(records),
        'fields_found': set(),
        'feature_mentions': [],
        'numeric_mentions': [],
        'technical_terms': [],
        'model_mentions': [],
        'stage_analysis': defaultdict(list)
    }

    # Expanded search patterns
    feature_patterns = {
        'idx': r'idx|IDX|technical\s+indicator|indicator|rsi|RSI|macd|MACD|bollinger|stochastic|williams|atr|ATR|adx|ADX|cci|CCI|mfi|MFI|obv|OBV|vwap|VWAP|ema|EMA|sma|SMA',
        'bqx': r'bqx|BQX|momentum|window|interval',
        'features': r'feature|Feature|FEATURE|variable|predictor|input',
        'numbers': r'\b\d{2,5}\b(?:\s*(?:features?|variables?|indicators?|predictors?))?',
        'technical': r'model|Model|MODEL|algorithm|prediction|forecast|accuracy|metric|performance|training|testing|validation',
        'ml_terms': r'random\s*forest|xgboost|neural|deep\s*learning|machine\s*learning|ML|AI|sklearn|tensorflow|pytorch',
        'data': r'data|dataset|table|column|field|schema|BigQuery|BQ|SQL'
    }

    print("\n📋 ANALYZING ALL FIELDS IN AIRTABLE...")
    print("=" * 80)

    for i, record in enumerate(records, 1):
        fields = record.get('fields', {})
        record_id = record.get('id', '')

        # Collect all field names
        for field_name in fields.keys():
            stats['fields_found'].add(field_name)

        # Combine all text content
        all_text = ' '.join(str(v) for v in fields.values() if v)

        # Search for patterns
        for pattern_name, pattern in feature_patterns.items():
            matches = re.findall(pattern, all_text, re.IGNORECASE)
            if matches:
                stage_val = fields.get('stage_link', fields.get('Stage', 'Unknown'))
                if isinstance(stage_val, list):
                    stage_val = stage_val[0] if stage_val else 'Unknown'

                task_info = {
                    'id': record_id,
                    'task_name': fields.get('name', fields.get('Task Name', 'Unnamed')),
                    'stage': stage_val,
                    'pattern': pattern_name,
                    'matches': list(set(matches))[:5],  # First 5 unique matches
                    'status': fields.get('status', fields.get('Status', 'Unknown'))
                }

                if pattern_name in ['idx', 'bqx', 'features']:
                    stats['feature_mentions'].append(task_info)
                elif pattern_name == 'numbers':
                    stats['numeric_mentions'].append(task_info)
                elif pattern_name in ['technical', 'ml_terms', 'data']:
                    stats['technical_terms'].append(task_info)

        # Stage analysis
        stage = fields.get('stage_link', fields.get('Stage', 'Unknown'))
        # Handle if stage_link is a list
        if isinstance(stage, list):
            stage = stage[0] if stage else 'Unknown'
        if stage and stage != 'Unknown':
            task_name = fields.get('name', fields.get('Task Name', 'Unnamed'))
            stats['stage_analysis'][stage].append(task_name)

        # Show progress
        if i % 50 == 0:
            print(f"Processed {i}/{len(records)} records...")

    return stats

def display_comprehensive_results(stats):
    """Display comprehensive analysis results"""

    print("\n" + "=" * 80)
    print("🔍 COMPREHENSIVE AIRTABLE ANALYSIS RESULTS")
    print("=" * 80)

    print(f"\n📊 OVERVIEW:")
    print(f"- Total Records: {stats['total_records']}")
    print(f"- Unique Fields Found: {len(stats['fields_found'])}")

    print("\n📝 FIELDS IN AIRTABLE:")
    for field in sorted(stats['fields_found']):
        print(f"  • {field}")

    print("\n🎯 FEATURE-RELATED MENTIONS:")
    if stats['feature_mentions']:
        print(f"Found {len(stats['feature_mentions'])} tasks with feature keywords:")
        for mention in stats['feature_mentions'][:10]:
            print(f"\n  Task: {mention['task_name'][:60]}")
            print(f"  Stage: {mention['stage']}")
            print(f"  Status: {mention['status']}")
            print(f"  Matches: {', '.join(mention['matches'])}")
    else:
        print("❌ No direct feature mentions found")

    print("\n🔢 NUMERIC REFERENCES:")
    if stats['numeric_mentions']:
        print(f"Found {len(stats['numeric_mentions'])} tasks with numbers that might be feature counts:")
        for mention in stats['numeric_mentions'][:10]:
            print(f"\n  Task: {mention['task_name'][:60]}")
            print(f"  Numbers found: {', '.join(mention['matches'][:3])}")
    else:
        print("❌ No numeric references found")

    print("\n🔬 TECHNICAL/ML TERMS:")
    if stats['technical_terms']:
        print(f"Found {len(stats['technical_terms'])} tasks with technical terms:")
        unique_terms = set()
        for mention in stats['technical_terms']:
            unique_terms.update(mention['matches'])
        print(f"  Unique terms: {', '.join(list(unique_terms)[:20])}")
    else:
        print("❌ No technical terms found")

    print("\n📈 STAGE DISTRIBUTION:")
    for stage, tasks in stats['stage_analysis'].items():
        print(f"  {stage}: {len(tasks)} tasks")
        if 'feature' in stage.lower() or 'data' in stage.lower() or 'model' in stage.lower():
            print(f"    → First 3 tasks: {', '.join(tasks[:3])}")

    # Search for specific numbers mentioned in documentation
    print("\n🔍 SEARCHING FOR DOCUMENTED NUMBERS:")
    documented_numbers = ['273', '161', '12000', '12,000', '6000', '6,000', '9000', '9,000', '434']
    found_docs = False
    for num in documented_numbers:
        for mention in stats['numeric_mentions']:
            if num in mention['matches']:
                print(f"  ✅ Found '{num}' in task: {mention['task_name'][:60]}")
                print(f"     Status: {mention['status']}, Stage: {mention['stage']}")
                found_docs = True
    if not found_docs:
        print("  ❌ None of the documented feature counts (273, 161, 12000, etc.) found in AirTable")

    print("\n" + "=" * 80)
    print("💡 ANALYSIS SUMMARY")
    print("=" * 80)

    if not stats['feature_mentions'] and not any(num in str(stats['numeric_mentions']) for num in ['273', '161', '12000']):
        print("""
The AirTable project plan appears to be HIGH-LEVEL and does not contain specific
technical details about feature counts. The documented numbers (273 IDX features,
161 BQX features, 12,000+ total features) are likely from:
1. Technical documentation files (not in AirTable)
2. Code comments or implementation details
3. Strategic planning documents outside of task management

The AirTable is being used for PROJECT MANAGEMENT, not technical specification.
""")
    else:
        print("""
Found some feature-related mentions in AirTable. See details above.
""")

    return stats

def main():
    """Main audit function"""
    print("=" * 80)
    print("🔍 COMPREHENSIVE AIRTABLE AUDIT")
    print("=" * 80)

    if not API_KEY or not BASE_ID:
        print("❌ Error: AirTable credentials not found")
        return None

    # Fetch all tasks
    print("\n📥 Fetching all records from AirTable...")
    records = get_all_tasks()
    print(f"✅ Retrieved {len(records)} records")

    # Comprehensive analysis
    stats = comprehensive_analysis(records)

    # Display results
    display_comprehensive_results(stats)

    # Export detailed findings
    print("\n💾 Exporting detailed findings...")
    with open('/home/micha/bqx_ml_v3/airtable_audit_results.json', 'w') as f:
        export_data = {
            'total_records': stats['total_records'],
            'fields_found': list(stats['fields_found']),
            'feature_mentions_count': len(stats['feature_mentions']),
            'numeric_mentions_count': len(stats['numeric_mentions']),
            'technical_terms_count': len(stats['technical_terms']),
            'stages': {k: len(v) for k, v in stats['stage_analysis'].items()}
        }
        json.dump(export_data, f, indent=2)
    print("✅ Results exported to airtable_audit_results.json")

    return stats

if __name__ == "__main__":
    stats = main()