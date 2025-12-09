#!/usr/bin/env python3
"""
Walk-Forward Data Splits for BQX ML V3

Creates time-series aware train/validation/test splits following the plan:
- Train window: T-365 to T-30 days
- Validation window: T-30 to T-7 days
- Test window: T-7 to T days

Critical: Standard cross-validation causes look-ahead bias in time series!
"""

import sys
import json
from datetime import datetime, timedelta
from google.cloud import bigquery

PROJECT = "bqx-ml"
ANALYTICS_DATASET = "bqx_ml_v3_analytics_v2"


def get_date_range(pair: str) -> tuple:
    """Get min/max dates from targets table."""
    client = bigquery.Client(project=PROJECT)

    query = f"""
    SELECT
        MIN(DATE(interval_time)) as min_date,
        MAX(DATE(interval_time)) as max_date,
        COUNT(*) as total_rows
    FROM `{PROJECT}.{ANALYTICS_DATASET}.targets_{pair}`
    WHERE target_bqx45_h15 IS NOT NULL
    """

    result = list(client.query(query).result())[0]
    return result['min_date'], result['max_date'], result['total_rows']


def create_walk_forward_splits(
    pair: str,
    train_days: int = 365,
    val_days: int = 23,
    test_days: int = 7,
    step_days: int = 30
) -> list:
    """
    Create walk-forward splits.

    For each split:
    - train: T-train_days to T-val_days-test_days
    - val: T-val_days-test_days to T-test_days
    - test: T-test_days to T

    Then roll forward by step_days and repeat.
    """
    min_date, max_date, total_rows = get_date_range(pair)

    print(f"Date range: {min_date} to {max_date}")
    print(f"Total rows: {total_rows:,}")
    print(f"Train/Val/Test: {train_days}/{val_days}/{test_days} days")
    print(f"Step forward: {step_days} days")

    splits = []
    total_window = train_days + val_days + test_days

    # Convert to datetime for arithmetic
    current_end = max_date

    split_num = 0
    while True:
        test_end = current_end
        test_start = test_end - timedelta(days=test_days - 1)
        val_end = test_start - timedelta(days=1)
        val_start = val_end - timedelta(days=val_days - 1)
        train_end = val_start - timedelta(days=1)
        train_start = train_end - timedelta(days=train_days - 1)

        # Check if we have enough data
        if train_start < min_date:
            print(f"\nNot enough data for split {split_num + 1}")
            break

        split = {
            "split_id": split_num,
            "train": {
                "start": str(train_start),
                "end": str(train_end),
                "days": train_days
            },
            "validation": {
                "start": str(val_start),
                "end": str(val_end),
                "days": val_days
            },
            "test": {
                "start": str(test_start),
                "end": str(test_end),
                "days": test_days
            }
        }

        splits.append(split)
        split_num += 1

        # Roll back for next split
        current_end = current_end - timedelta(days=step_days)

        # Stop after reasonable number of splits
        if split_num >= 24:  # 2 years of monthly splits
            break

    print(f"\nCreated {len(splits)} walk-forward splits")
    return splits


def generate_split_queries(pair: str, splits: list) -> dict:
    """Generate BigQuery queries for each split."""
    queries = {}

    for split in splits:
        split_id = split['split_id']

        # Training query
        queries[f"train_{split_id}"] = f"""
        SELECT *
        FROM `{PROJECT}.{ANALYTICS_DATASET}.targets_{pair}` t
        WHERE DATE(interval_time) BETWEEN '{split['train']['start']}' AND '{split['train']['end']}'
          AND target_bqx45_h15 IS NOT NULL
        """

        # Validation query
        queries[f"val_{split_id}"] = f"""
        SELECT *
        FROM `{PROJECT}.{ANALYTICS_DATASET}.targets_{pair}` t
        WHERE DATE(interval_time) BETWEEN '{split['validation']['start']}' AND '{split['validation']['end']}'
          AND target_bqx45_h15 IS NOT NULL
        """

        # Test query
        queries[f"test_{split_id}"] = f"""
        SELECT *
        FROM `{PROJECT}.{ANALYTICS_DATASET}.targets_{pair}` t
        WHERE DATE(interval_time) BETWEEN '{split['test']['start']}' AND '{split['test']['end']}'
          AND target_bqx45_h15 IS NOT NULL
        """

    return queries


def main():
    pair = sys.argv[1] if len(sys.argv) > 1 else "eurusd"

    print("=" * 60)
    print(f"Walk-Forward Data Splits for {pair.upper()}")
    print("=" * 60)

    # Create splits
    splits = create_walk_forward_splits(
        pair,
        train_days=365,  # 1 year training
        val_days=23,     # ~3 weeks validation
        test_days=7,     # 1 week test
        step_days=30     # Monthly roll-forward
    )

    # Generate queries
    queries = generate_split_queries(pair, splits)

    # Save results
    output = {
        "pair": pair,
        "created_at": datetime.now().isoformat(),
        "splits": splits,
        "split_count": len(splits)
    }

    output_file = f"/tmp/walk_forward_splits_{pair}.json"
    with open(output_file, "w") as f:
        json.dump(output, f, indent=2)

    # Print summary
    print("\n" + "=" * 60)
    print("SPLIT SUMMARY")
    print("=" * 60)

    for i, split in enumerate(splits[:5]):  # Show first 5
        print(f"\nSplit {i}:")
        print(f"  Train: {split['train']['start']} to {split['train']['end']} ({split['train']['days']} days)")
        print(f"  Val:   {split['validation']['start']} to {split['validation']['end']} ({split['validation']['days']} days)")
        print(f"  Test:  {split['test']['start']} to {split['test']['end']} ({split['test']['days']} days)")

    if len(splits) > 5:
        print(f"\n... and {len(splits) - 5} more splits")

    print(f"\nResults saved to: {output_file}")

    # Count expected rows for first split
    client = bigquery.Client(project=PROJECT)
    split0 = splits[0]

    count_query = f"""
    SELECT
        'train' as split,
        COUNT(*) as rows
    FROM `{PROJECT}.{ANALYTICS_DATASET}.targets_{pair}`
    WHERE DATE(interval_time) BETWEEN '{split0['train']['start']}' AND '{split0['train']['end']}'
      AND target_bqx45_h15 IS NOT NULL
    UNION ALL
    SELECT
        'val' as split,
        COUNT(*) as rows
    FROM `{PROJECT}.{ANALYTICS_DATASET}.targets_{pair}`
    WHERE DATE(interval_time) BETWEEN '{split0['validation']['start']}' AND '{split0['validation']['end']}'
      AND target_bqx45_h15 IS NOT NULL
    UNION ALL
    SELECT
        'test' as split,
        COUNT(*) as rows
    FROM `{PROJECT}.{ANALYTICS_DATASET}.targets_{pair}`
    WHERE DATE(interval_time) BETWEEN '{split0['test']['start']}' AND '{split0['test']['end']}'
      AND target_bqx45_h15 IS NOT NULL
    """

    print("\nSplit 0 Row Counts:")
    for row in client.query(count_query).result():
        print(f"  {row['split']}: {row['rows']:,} rows")


if __name__ == "__main__":
    main()
