#!/usr/bin/env python3
"""
Check current scores across all tables to monitor remediation progress.
"""

import json
from pyairtable import Api
import statistics

def check_scores():
    """Check and report current scores across all tables."""

    # Load credentials
    with open('.secrets/github_secrets.json') as f:
        secrets = json.load(f)['secrets']

    api = Api(secrets['AIRTABLE_API_KEY']['value'])
    base_id = secrets['AIRTABLE_BASE_ID']['value']

    print("=" * 70)
    print("CURRENT SCORE STATUS CHECK")
    print("=" * 70)

    tables = ['Phases', 'Stages', 'Tasks']

    for table_name in tables:
        print(f"\n📊 {table_name.upper()} SCORES:")
        print("-" * 50)

        table = api.table(base_id, table_name)
        all_records = table.all()

        scores = []
        no_score_count = 0
        low_score_records = []
        high_score_count = 0

        for record in all_records:
            fields = record['fields']
            score = fields.get('record_score')

            # Get identifier
            if table_name == 'Phases':
                identifier = fields.get('phase_id', 'Unknown')
            elif table_name == 'Stages':
                identifier = fields.get('stage_id', 'Unknown')
            else:  # Tasks
                identifier = fields.get('task_id', 'Unknown')

            if score is None:
                no_score_count += 1
                low_score_records.append((identifier, None))
            else:
                scores.append(score)
                if score < 90:
                    low_score_records.append((identifier, score))
                else:
                    high_score_count += 1

        # Calculate statistics
        if scores:
            avg_score = statistics.mean(scores)
            min_score = min(scores)
            max_score = max(scores)
            median_score = statistics.median(scores)
        else:
            avg_score = min_score = max_score = median_score = 0

        # Print summary
        print(f"  Total records: {len(all_records)}")
        print(f"  Records with scores: {len(scores)}")
        print(f"  Records without scores: {no_score_count}")
        print(f"  Records scoring ≥90: {high_score_count}")
        print(f"  Records scoring <90: {len(low_score_records)}")

        if scores:
            print(f"\n  Score Statistics:")
            print(f"    Average: {avg_score:.1f}")
            print(f"    Median: {median_score:.1f}")
            print(f"    Min: {min_score}")
            print(f"    Max: {max_score}")

        # List low-scoring records
        if low_score_records:
            print(f"\n  Low-scoring records (<90):")
            for identifier, score in low_score_records[:10]:  # Show first 10
                score_str = str(score) if score is not None else "No score"
                print(f"    - {identifier}: {score_str}")
            if len(low_score_records) > 10:
                print(f"    ... and {len(low_score_records) - 10} more")

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    # Overall summary
    total_low = 0
    total_high = 0
    total_no_score = 0

    for table_name in tables:
        table = api.table(base_id, table_name)
        all_records = table.all()

        for record in all_records:
            score = record['fields'].get('record_score')
            if score is None:
                total_no_score += 1
            elif score < 90:
                total_low += 1
            else:
                total_high += 1

    total_records = total_low + total_high + total_no_score

    print(f"Total records across all tables: {total_records}")
    print(f"  ✅ Scoring ≥90: {total_high} ({100*total_high/total_records:.1f}%)")
    print(f"  ⚠️ Scoring <90: {total_low} ({100*total_low/total_records:.1f}%)")
    print(f"  ❓ No score: {total_no_score} ({100*total_no_score/total_records:.1f}%)")

    if total_low == 0 and total_no_score == 0:
        print("\n🎉 SUCCESS: All records are scoring ≥90!")
    else:
        print(f"\n📌 Still need to remediate: {total_low + total_no_score} records")

if __name__ == "__main__":
    check_scores()