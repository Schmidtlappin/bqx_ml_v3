#!/usr/bin/env python3
"""
Audit AirTable project plan to determine number of idx and bqx features.
"""

import os
import json
import requests
import subprocess
from collections import defaultdict

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
BASE_ID = os.getenv('AIRTABLE_BASE_ID')
API_KEY = os.getenv('AIRTABLE_API_KEY')

# If not in env, try to load from GCP Secrets Manager
if not API_KEY or not BASE_ID:
    print("Loading credentials from GCP Secrets Manager...")
    API_KEY = API_KEY or get_secret('bqx-ml-airtable-token')
    BASE_ID = BASE_ID or get_secret('bqx-ml-airtable-base-id')

    if API_KEY and BASE_ID:
        print("✅ Successfully loaded AirTable credentials from GCP Secrets Manager")
    else:
        print("❌ Failed to load AirTable credentials from GCP Secrets Manager")

TABLE_NAME = 'Tasks'
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

def analyze_features(records):
    """Analyze records for idx and bqx feature mentions"""

    feature_stats = {
        'idx_features': set(),
        'bqx_features': set(),
        'idx_mentions': 0,
        'bqx_mentions': 0,
        'tasks_with_features': [],
        'feature_details': defaultdict(list)
    }

    # Keywords to search for
    idx_keywords = ['idx', 'technical indicator', 'rsi', 'macd', 'bollinger', 'stochastic',
                    'williams', 'atr', 'adx', 'cci', 'mfi', 'obv', 'vwap', 'ema', 'sma']
    bqx_keywords = ['bqx', 'momentum', 'bqx_45', 'bqx_90', 'bqx_180', 'bqx_360',
                    'bqx_720', 'bqx_1440', 'bqx_2880']

    for record in records:
        fields = record.get('fields', {})
        task_name = fields.get('Task Name', '')
        notes = fields.get('Notes', '')
        stage = fields.get('Stage', '')
        status = fields.get('Status', '')

        # Combine all text fields for searching
        all_text = f"{task_name} {notes} {stage}".lower()

        # Check for idx features
        idx_found = False
        for keyword in idx_keywords:
            if keyword in all_text:
                idx_found = True
                feature_stats['idx_mentions'] += 1
                feature_stats['idx_features'].add(keyword)
                feature_stats['feature_details']['idx'].append({
                    'task': task_name[:50],
                    'keyword': keyword,
                    'status': status
                })

        # Check for bqx features
        bqx_found = False
        for keyword in bqx_keywords:
            if keyword in all_text:
                bqx_found = True
                feature_stats['bqx_mentions'] += 1
                feature_stats['bqx_features'].add(keyword)
                feature_stats['feature_details']['bqx'].append({
                    'task': task_name[:50],
                    'keyword': keyword,
                    'status': status
                })

        if idx_found or bqx_found:
            feature_stats['tasks_with_features'].append({
                'name': task_name,
                'status': status,
                'has_idx': idx_found,
                'has_bqx': bqx_found
            })

    return feature_stats

def extract_feature_counts(records):
    """Try to extract specific feature counts from task descriptions"""

    feature_numbers = {
        'idx_count': None,
        'bqx_count': None,
        'total_features': None,
        'mentions': []
    }

    import re

    for record in records:
        fields = record.get('fields', {})
        task_name = fields.get('Task Name', '')
        notes = fields.get('Notes', '')

        all_text = f"{task_name} {notes}"

        # Look for patterns like "273 idx", "161 bqx", "12,000 features", etc.
        idx_pattern = r'(\d+)\s*(?:idx|IDX|technical indicator)'
        bqx_pattern = r'(\d+)\s*(?:bqx|BQX)'
        total_pattern = r'(\d+[,\d]*)\s*(?:total |)features'

        idx_match = re.search(idx_pattern, all_text)
        if idx_match:
            feature_numbers['idx_count'] = int(idx_match.group(1))
            feature_numbers['mentions'].append(f"IDX: {idx_match.group(0)} in '{task_name[:50]}'")

        bqx_match = re.search(bqx_pattern, all_text)
        if bqx_match:
            feature_numbers['bqx_count'] = int(bqx_match.group(1))
            feature_numbers['mentions'].append(f"BQX: {bqx_match.group(0)} in '{task_name[:50]}'")

        total_match = re.search(total_pattern, all_text)
        if total_match:
            total_str = total_match.group(1).replace(',', '')
            feature_numbers['total_features'] = int(total_str)
            feature_numbers['mentions'].append(f"Total: {total_match.group(0)} in '{task_name[:50]}'")

    return feature_numbers

def main():
    """Main audit function"""
    print("=" * 80)
    print("🔍 AIRTABLE PROJECT PLAN FEATURE AUDIT")
    print("=" * 80)

    if not API_KEY or not BASE_ID:
        print("❌ Error: AirTable credentials not found")
        return

    # Fetch all tasks
    print("\n📥 Fetching tasks from AirTable...")
    records = get_all_tasks()
    print(f"✅ Retrieved {len(records)} tasks")

    # Analyze features
    print("\n🔬 Analyzing feature mentions...")
    feature_stats = analyze_features(records)

    # Extract specific counts
    feature_numbers = extract_feature_counts(records)

    # Display results
    print("\n" + "=" * 80)
    print("📊 FEATURE AUDIT RESULTS")
    print("=" * 80)

    print("\n📈 FEATURE MENTIONS IN TASKS:")
    print(f"- Tasks mentioning IDX features: {len([t for t in feature_stats['tasks_with_features'] if t['has_idx']])}")
    print(f"- Tasks mentioning BQX features: {len([t for t in feature_stats['tasks_with_features'] if t['has_bqx']])}")
    print(f"- Total feature-related tasks: {len(feature_stats['tasks_with_features'])}")

    print("\n🔢 EXTRACTED FEATURE COUNTS:")
    if feature_numbers['idx_count']:
        print(f"✅ IDX Features: {feature_numbers['idx_count']}")
    else:
        print("❌ No specific IDX feature count found in tasks")

    if feature_numbers['bqx_count']:
        print(f"✅ BQX Features: {feature_numbers['bqx_count']}")
    else:
        print("❌ No specific BQX feature count found in tasks")

    if feature_numbers['total_features']:
        print(f"✅ Total Features Mentioned: {feature_numbers['total_features']:,}")

    print("\n📝 FEATURE KEYWORDS FOUND:")
    print(f"IDX Keywords: {', '.join(sorted(feature_stats['idx_features']))}")
    print(f"BQX Keywords: {', '.join(sorted(feature_stats['bqx_features']))}")

    if feature_numbers['mentions']:
        print("\n💡 SPECIFIC MENTIONS:")
        for mention in feature_numbers['mentions']:
            print(f"  - {mention}")

    print("\n🎯 TOP FEATURE-RELATED TASKS:")
    for i, task in enumerate(feature_stats['tasks_with_features'][:10], 1):
        features = []
        if task['has_idx']:
            features.append('IDX')
        if task['has_bqx']:
            features.append('BQX')
        print(f"{i}. {task['name'][:60]}")
        print(f"   Features: {', '.join(features)} | Status: {task['status']}")

    # Summary
    print("\n" + "=" * 80)
    print("📋 SUMMARY")
    print("=" * 80)
    print(f"Total AirTable Tasks: {len(records)}")
    print(f"Feature-Related Tasks: {len(feature_stats['tasks_with_features'])}")
    print(f"IDX Feature Count: {feature_numbers['idx_count'] or 'Not specified'}")
    print(f"BQX Feature Count: {feature_numbers['bqx_count'] or 'Not specified'}")
    print(f"Total Features: {feature_numbers['total_features'] or 'Not specified'}")

    return feature_numbers, feature_stats

if __name__ == "__main__":
    feature_numbers, feature_stats = main()