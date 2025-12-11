# CE DIRECTIVE: BigQuery ETL Strategy (Replaces Local Merge)

**Date**: December 11, 2025 10:15 UTC
**From**: Chief Engineer (CE)
**To**: Build Agent (BA)
**Priority**: P0 - CRITICAL
**Supersedes**: All previous merge directives

---

## STRATEGIC DECISION

**LOCAL MERGE ABANDONED** - OOM crashes make local pandas merge unviable.

**NEW APPROACH**: ETL parquet checkpoints back to BigQuery, merge with SQL.

---

## RATIONALE

| Factor | Local Merge | BigQuery ETL |
|--------|-------------|--------------|
| Memory | OOM at 27GB | **Unlimited** |
| Speed | 40+ min/pair | **2-3 min/pair** |
| Reliability | Crashed | **Production-grade** |
| Cost | $0 | **~$0.70/pair** |

**Total cost for 28 pairs**: ~$20 (acceptable)

---

## IMPLEMENTATION PLAN

### Phase 1: Upload Checkpoints to BigQuery Staging

For each pair's 667 checkpoint files:

```python
from google.cloud import bigquery
import pandas as pd
from pathlib import Path

client = bigquery.Client(project="bqx-ml")
STAGING_DATASET = "bqx_ml_v3_staging"

def upload_checkpoints(pair: str):
    """Upload all parquet checkpoints to BigQuery staging tables."""
    checkpoint_dir = Path(f"data/features/checkpoints/{pair}")

    for pq_file in checkpoint_dir.glob("*.parquet"):
        table_name = pq_file.stem  # e.g., "base_bqx_eurusd"
        table_id = f"bqx-ml.{STAGING_DATASET}.{table_name}"

        df = pd.read_parquet(pq_file)

        job_config = bigquery.LoadJobConfig(
            write_disposition="WRITE_TRUNCATE",
        )

        job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
        job.result()  # Wait for completion

        print(f"  Uploaded {table_name}: {len(df):,} rows")
```

### Phase 2: Merge in BigQuery with SQL

```sql
-- Create merged training table for EURUSD
CREATE OR REPLACE TABLE `bqx-ml.bqx_ml_v3_models.training_eurusd` AS
SELECT
    t.interval_time,
    t.target_bqx45_h15, t.target_bqx45_h30, /* ... all 49 targets */
    f1.*, f2.*, f3.*, /* ... all feature tables */
FROM `bqx-ml.bqx_ml_v3_staging.targets` t
LEFT JOIN `bqx-ml.bqx_ml_v3_staging.base_bqx_eurusd` f1 USING (interval_time)
LEFT JOIN `bqx-ml.bqx_ml_v3_staging.base_idx_eurusd` f2 USING (interval_time)
/* ... 665 more JOINs ... */
```

### Phase 3: Dynamic SQL Generation

```python
def generate_merge_sql(pair: str, table_names: list) -> str:
    """Generate BigQuery SQL to merge all checkpoint tables."""

    # Start with targets
    sql = f"""
CREATE OR REPLACE TABLE `bqx-ml.bqx_ml_v3_models.training_{pair}` AS
SELECT *
FROM `bqx-ml.bqx_ml_v3_staging.targets` t
"""

    # Add LEFT JOINs for each feature table
    for i, table in enumerate(table_names):
        if table != "targets":
            sql += f"LEFT JOIN `bqx-ml.bqx_ml_v3_staging.{table}` USING (interval_time)\n"

    return sql
```

---

## EXECUTION STEPS

### Step 1: Upload EURUSD Checkpoints (Pilot)
```bash
python3 scripts/upload_checkpoints_to_bq.py --pair eurusd
```
- Expected: 668 tables uploaded to staging
- Time: ~10-15 minutes

### Step 2: Generate and Execute Merge SQL
```bash
python3 scripts/merge_in_bigquery.py --pair eurusd
```
- Expected: `training_eurusd` table created in `bqx_ml_v3_models`
- Time: ~2-5 minutes

### Step 3: Validate Merged Table
```sql
SELECT
    COUNT(*) as rows,
    COUNT(DISTINCT interval_time) as unique_intervals,
    SUM(CASE WHEN target_bqx45_h15 IS NOT NULL THEN 1 ELSE 0 END) as targets_present
FROM `bqx-ml.bqx_ml_v3_models.training_eurusd`
```

### Step 4: Scale to All 28 Pairs
```bash
for pair in eurusd gbpusd usdjpy ...; do
    python3 scripts/upload_checkpoints_to_bq.py --pair $pair
    python3 scripts/merge_in_bigquery.py --pair $pair
done
```

---

## COST ESTIMATE

| Operation | Cost/Pair | Total (28 pairs) |
|-----------|-----------|------------------|
| Upload to staging | $0.05 | $1.40 |
| Merge query | $0.05 | $1.40 |
| Storage (staging) | $0.50/mo | $14/mo |
| Storage (training) | $0.50/mo | $14/mo |
| **Total** | **~$0.60** | **~$17** |

---

## DELIVERABLES

1. `scripts/upload_checkpoints_to_bq.py` - Upload checkpoints to staging
2. `scripts/merge_in_bigquery.py` - Execute BigQuery merge
3. `training_{pair}` tables in `bqx_ml_v3_models` dataset

---

## SUCCESS CRITERIA

- [ ] EURUSD checkpoints uploaded to staging (668 tables)
- [ ] `training_eurusd` table created with ~100K rows, ~6,500 columns
- [ ] All 49 target columns present
- [ ] Query time < 5 minutes
- [ ] No OOM errors

---

## MANDATE COMPLIANCE

This approach:
- Preserves 100% feature coverage (667 tables + targets)
- Uses BigQuery native operations (already in ecosystem)
- Creates persistent training tables (reusable)
- Enables direct training from BigQuery

---

**Chief Engineer (CE)**
