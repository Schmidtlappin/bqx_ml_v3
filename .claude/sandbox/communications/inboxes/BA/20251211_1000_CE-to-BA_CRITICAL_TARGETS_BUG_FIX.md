# CE DIRECTIVE: CRITICAL - Fix query_targets() Bug

**Date**: December 11, 2025 10:00 UTC
**From**: Chief Engineer (CE)
**To**: Build Agent (BA)
**Priority**: P0 - CRITICAL
**Supersedes**: All previous Step 6 directives

---

## EXECUTIVE SUMMARY

**CRITICAL BUG CONFIRMED** by EA audit: `query_targets()` extracts only 7 columns instead of 49.

| Source | Columns | Status |
|--------|---------|--------|
| BigQuery targets_eurusd | **49** | COMPLIANT |
| Checkpoint targets.parquet | **7** | **BUG** |

---

## ROOT CAUSE

**File**: `pipelines/training/parallel_feature_testing.py`
**Function**: `query_targets()` (lines 301-326)
**Bug**: Hardcoded to query only `bqx_45` window

```python
# CURRENT (BROKEN):
SELECT interval_time,
    target_bqx45_h15, target_bqx45_h30, target_bqx45_h45,
    target_bqx45_h60, target_bqx45_h75, target_bqx45_h90, target_bqx45_h105
```

**Missing**: 6 windows × 7 horizons = 42 columns
- bqx_90, bqx_180, bqx_360, bqx_720, bqx_1440, bqx_2880

---

## REQUIRED FIX

Replace `query_targets()` function (lines 301-326) with:

```python
def query_targets(pair: str, date_start: str, date_end: str) -> tuple:
    """Query targets table with all 7 windows × 7 horizons = 49 columns."""
    client = bigquery.Client(project=PROJECT)

    # All 7 BQX windows and 7 horizons per mandate
    windows = [45, 90, 180, 360, 720, 1440, 2880]
    horizons = [15, 30, 45, 60, 75, 90, 105]

    # Generate all 49 target column names
    target_cols = ',\n        '.join([
        f'target_bqx{w}_h{h}'
        for w in windows
        for h in horizons
    ])

    query = f"""
    SELECT
        interval_time,
        {target_cols}
    FROM `{PROJECT}.{ANALYTICS_DATASET}.targets_{pair}`
    WHERE DATE(interval_time) BETWEEN '{date_start}' AND '{date_end}'
    AND target_bqx45_h15 IS NOT NULL
    ORDER BY interval_time
    LIMIT {SAMPLE_LIMIT}
    """

    job = client.query(query)
    df = job.to_dataframe()
    bytes_scanned = job.total_bytes_processed or 0

    return df, bytes_scanned
```

---

## ACTION SEQUENCE

### Step 1: HALT Current Process
```bash
kill 1493048  # Current merge process
```

### Step 2: Apply Fix
Edit `pipelines/training/parallel_feature_testing.py` lines 301-326

### Step 3: Delete Bad Checkpoint
```bash
rm -f /home/micha/bqx_ml_v3/data/features/eurusd/checkpoints/targets.parquet
```

### Step 4: Verify Fix
```bash
python3 -c "
from pipelines.training.parallel_feature_testing import query_targets
df, _ = query_targets('eurusd', '2023-01-01', '2023-01-02')
print(f'Columns: {len(df.columns)}')
print(df.columns.tolist())
"
```
Expected: 50 columns (interval_time + 49 targets)

### Step 5: Restart Step 6
```bash
timeout 3600 python3 pipelines/training/parallel_feature_testing.py full > logs/step6_fixed_targets.log 2>&1 &
```

---

## VERIFICATION CHECKLIST

- [ ] Process 1493048 killed
- [ ] query_targets() updated with all 49 columns
- [ ] targets.parquet checkpoint deleted
- [ ] Test query returns 50 columns
- [ ] Step 6 restarted
- [ ] Report status to CE

---

## MANDATE COMPLIANCE

This fix is **REQUIRED** for mandate compliance:

| Requirement | Before | After |
|-------------|--------|-------|
| Target columns | 7 | **49** |
| Windows covered | 1 | **7** |
| Horizons per window | 7 | 7 |

Without this fix, models can only train on bqx_45 window, violating the multi-window architecture mandate.

---

**Chief Engineer (CE)**
