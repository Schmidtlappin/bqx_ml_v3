#!/usr/bin/env python3
"""
Create tmp_ temporal pattern tables (28 tables - one per pair).
These extract time-based features from interval_time for session analysis.

Features include:
- Hour of day (0-23)
- Day of week (0-6, Monday=0)
- Trading session indicators (Asian, European, American)
- Session overlap indicators
- Week of year, month, quarter
- Is weekend, is month start/end
"""

from google.cloud import bigquery
import time

PROJECT = 'bqx-ml'
DATASET = 'bqx_ml_v3_features_v2'
SOURCE_DATASET = 'bqx_ml_v3_features'

PAIRS = [
    'audcad', 'audchf', 'audjpy', 'audnzd', 'audusd',
    'cadchf', 'cadjpy', 'chfjpy',
    'euraud', 'eurcad', 'eurchf', 'eurgbp', 'eurjpy', 'eurnzd', 'eurusd',
    'gbpaud', 'gbpcad', 'gbpchf', 'gbpjpy', 'gbpnzd', 'gbpusd',
    'nzdcad', 'nzdchf', 'nzdjpy', 'nzdusd',
    'usdcad', 'usdchf', 'usdjpy'
]


def create_temporal_table(client, pair):
    """Create temporal features table for a pair."""

    # Use reg_ table as source for interval_time and pair columns
    source_table = f"reg_{pair}"
    new_table = f"tmp_{pair}"

    sql = f"""
    CREATE TABLE `{PROJECT}.{DATASET}.{new_table}`
    PARTITION BY DATE(interval_time)
    CLUSTER BY pair
    AS
    SELECT
        interval_time,
        '{pair}' as pair,

        -- Hour features
        EXTRACT(HOUR FROM interval_time) as hour_of_day,
        CASE
            WHEN EXTRACT(HOUR FROM interval_time) BETWEEN 0 AND 7 THEN 'asian'
            WHEN EXTRACT(HOUR FROM interval_time) BETWEEN 8 AND 15 THEN 'european'
            ELSE 'american'
        END as trading_session,

        -- Session binary indicators (UTC times)
        CASE WHEN EXTRACT(HOUR FROM interval_time) BETWEEN 0 AND 8 THEN 1 ELSE 0 END as is_asian_session,
        CASE WHEN EXTRACT(HOUR FROM interval_time) BETWEEN 7 AND 16 THEN 1 ELSE 0 END as is_european_session,
        CASE WHEN EXTRACT(HOUR FROM interval_time) BETWEEN 13 AND 22 THEN 1 ELSE 0 END as is_american_session,

        -- Session overlaps (high liquidity periods)
        CASE WHEN EXTRACT(HOUR FROM interval_time) BETWEEN 7 AND 8 THEN 1 ELSE 0 END as is_asian_european_overlap,
        CASE WHEN EXTRACT(HOUR FROM interval_time) BETWEEN 13 AND 16 THEN 1 ELSE 0 END as is_european_american_overlap,

        -- Day features
        EXTRACT(DAYOFWEEK FROM interval_time) as day_of_week,  -- 1=Sunday, 7=Saturday
        CASE WHEN EXTRACT(DAYOFWEEK FROM interval_time) IN (1, 7) THEN 1 ELSE 0 END as is_weekend,
        CASE WHEN EXTRACT(DAYOFWEEK FROM interval_time) = 2 THEN 1 ELSE 0 END as is_monday,
        CASE WHEN EXTRACT(DAYOFWEEK FROM interval_time) = 6 THEN 1 ELSE 0 END as is_friday,

        -- Week/Month/Quarter features
        EXTRACT(WEEK FROM interval_time) as week_of_year,
        EXTRACT(MONTH FROM interval_time) as month,
        EXTRACT(QUARTER FROM interval_time) as quarter,

        -- Month position features
        EXTRACT(DAY FROM interval_time) as day_of_month,
        CASE WHEN EXTRACT(DAY FROM interval_time) <= 5 THEN 1 ELSE 0 END as is_month_start,
        CASE WHEN EXTRACT(DAY FROM interval_time) >= 25 THEN 1 ELSE 0 END as is_month_end,

        -- Time-based cyclical encoding (for ML models)
        SIN(2 * ACOS(-1) * EXTRACT(HOUR FROM interval_time) / 24) as hour_sin,
        COS(2 * ACOS(-1) * EXTRACT(HOUR FROM interval_time) / 24) as hour_cos,
        SIN(2 * ACOS(-1) * EXTRACT(DAYOFWEEK FROM interval_time) / 7) as day_sin,
        COS(2 * ACOS(-1) * EXTRACT(DAYOFWEEK FROM interval_time) / 7) as day_cos,
        SIN(2 * ACOS(-1) * EXTRACT(MONTH FROM interval_time) / 12) as month_sin,
        COS(2 * ACOS(-1) * EXTRACT(MONTH FROM interval_time) / 12) as month_cos

    FROM `{PROJECT}.{SOURCE_DATASET}.{source_table}`
    """

    try:
        job = client.query(sql)
        job.result()

        # Get row count
        count_result = client.query(f"SELECT COUNT(*) as cnt FROM `{PROJECT}.{DATASET}.{new_table}`")
        row_count = list(count_result.result())[0].cnt

        return True, row_count
    except Exception as e:
        return False, str(e)


def main():
    client = bigquery.Client(project=PROJECT)

    print("=" * 70)
    print("CREATING TEMPORAL PATTERN TABLES (tmp_)")
    print("=" * 70)
    print(f"Target dataset: {PROJECT}.{DATASET}")
    print(f"Tables to create: {len(PAIRS)}")
    print()

    success = 0
    failed = 0
    skipped = 0

    for i, pair in enumerate(PAIRS, 1):
        table_name = f"tmp_{pair}"

        # Check if already exists
        try:
            client.get_table(f"{PROJECT}.{DATASET}.{table_name}")
            print(f"[{i}/{len(PAIRS)}] SKIP {table_name} (already exists)")
            skipped += 1
            continue
        except:
            pass

        print(f"[{i}/{len(PAIRS)}] Creating {table_name}...", end=" ", flush=True)

        ok, result = create_temporal_table(client, pair)

        if ok:
            print(f"OK ({result:,} rows)")
            success += 1
        else:
            print(f"FAILED: {result}")
            failed += 1

        time.sleep(0.5)

    print()
    print("=" * 70)
    print(f"COMPLETE: {success} created, {failed} failed, {skipped} skipped")
    print("=" * 70)


if __name__ == "__main__":
    main()
