# CE Directive: Full 6,477 Feature Query Expansion Required

**Document Type**: CE DIRECTIVE (AMENDMENT)
**Date**: December 10, 2025 05:20
**From**: Chief Engineer (CE)
**To**: Build Agent (BA)
**Priority**: **CRITICAL** - BLOCKING
**Reference**:
- 20251210_0515_BA-to-CE_DRY_RUN_RESULTS
- 20251210_0500_CE-to-BA_PARALLEL_BATCH_IMPLEMENTATION_GUIDE

---

## ISSUE IDENTIFIED

The current query template selects only ~55 features. This violates USER MANDATE.

| Current | Required |
|---------|----------|
| ~55 features | **6,477 features** |
| $0.03 cost | ~$10 cost (QA validated) |
| Curated subset | **FULL UNIVERSE** |

---

## USER MANDATE REMINDER

> "Full 6,477 universe testing is a user mandate."

The ~55 feature subset does NOT satisfy this requirement.

---

## REQUIRED ACTION

### 1. Expand Query to Include ALL Feature Tables

The query must JOIN and SELECT from ALL feature tables for each pair:

| Table Prefix | Type | Must Include |
|--------------|------|--------------|
| `reg_idx_{pair}` | Polynomial IDX | ALL columns |
| `reg_bqx_{pair}` | Polynomial BQX | ALL columns |
| `base_bqx_{pair}` | Base BQX | ALL columns |
| `agg_idx_{pair}` | Aggregation IDX | ALL columns |
| `agg_bqx_{pair}` | Aggregation BQX | ALL columns |
| `mom_idx_{pair}` | Momentum IDX | ALL columns |
| `mom_bqx_{pair}` | Momentum BQX | ALL columns |
| `vol_idx_{pair}` | Volatility IDX | ALL columns |
| `vol_bqx_{pair}` | Volatility BQX | ALL columns |
| `der_idx_{pair}` | Derivative IDX | ALL columns |
| `der_bqx_{pair}` | Derivative BQX | ALL columns |
| `align_idx_{pair}` | Alignment IDX | ALL columns |
| `align_bqx_{pair}` | Alignment BQX | ALL columns |
| `cov_*_{pair}` | Covariance | ALL columns |
| `corr_*_{pair}` | Correlation | ALL columns |
| `tri_*_{pair}` | Triangulation | ALL columns |
| `mkt_*` | Market-wide | ALL columns |

---

## 2. QUERY PATTERN (Full Feature)

```python
def build_full_feature_query(pair: str, date_start: str, date_end: str) -> str:
    """
    Build query for ALL 6,477 features (not curated subset).

    Strategy: Use SELECT * from each table, then filter columns in Python.
    This ensures we capture ALL features.
    """

    # Get list of all feature tables for this pair
    client = bigquery.Client(project=PROJECT)
    tables_query = f"""
    SELECT table_id
    FROM `{PROJECT}.{FEATURES_DATASET}.__TABLES__`
    WHERE table_id LIKE '%{pair}%'
    """
    tables = [row.table_id for row in client.query(tables_query).result()]

    # Build dynamic JOIN query
    select_parts = ["base.interval_time"]
    join_parts = []

    for i, table in enumerate(tables):
        alias = f"t{i}"
        # Select all columns except interval_time (avoid duplicates)
        select_parts.append(f"{alias}.*")
        if i == 0:
            join_parts.append(f"`{PROJECT}.{FEATURES_DATASET}.{table}` {alias}")
        else:
            join_parts.append(
                f"LEFT JOIN `{PROJECT}.{FEATURES_DATASET}.{table}` {alias} "
                f"ON base.interval_time = {alias}.interval_time"
            )

    # Add targets (all 7 horizons)
    select_parts.extend([
        "targets.target_bqx45_h15",
        "targets.target_bqx45_h30",
        "targets.target_bqx45_h45",
        "targets.target_bqx45_h60",
        "targets.target_bqx45_h75",
        "targets.target_bqx45_h90",
        "targets.target_bqx45_h105"
    ])

    query = f"""
    WITH base AS (
        SELECT DISTINCT interval_time
        FROM `{PROJECT}.{FEATURES_DATASET}.reg_idx_{pair}`
        WHERE DATE(interval_time) BETWEEN '{date_start}' AND '{date_end}'
    )
    SELECT {', '.join(select_parts)}
    FROM base
    {' '.join(join_parts)}
    JOIN `{PROJECT}.{ANALYTICS_DATASET}.targets_{pair}` targets
        ON base.interval_time = targets.interval_time
    WHERE targets.target_bqx45_h15 IS NOT NULL
    ORDER BY base.interval_time
    LIMIT {SAMPLE_LIMIT}
    """

    return query
```

---

## 3. ALTERNATIVE: Column Discovery Approach

```python
def get_all_feature_columns(pair: str) -> list:
    """Get ALL column names from ALL feature tables for a pair."""
    client = bigquery.Client(project=PROJECT)

    # Query INFORMATION_SCHEMA for all columns
    query = f"""
    SELECT table_name, column_name
    FROM `{PROJECT}.{FEATURES_DATASET}.INFORMATION_SCHEMA.COLUMNS`
    WHERE table_name LIKE '%{pair}%'
    AND column_name != 'interval_time'
    AND column_name != 'pair'
    ORDER BY table_name, ordinal_position
    """

    columns = []
    for row in client.query(query).result():
        columns.append(f"{row.table_name}.{row.column_name}")

    return columns  # Should be ~6,477 for EURUSD
```

---

## 4. EXPECTED COST (Full Query)

| Metric | Value |
|--------|-------|
| Features | 6,477 |
| Tables to JOIN | ~256 per pair |
| GB per pair | ~57.5 GB |
| Cost per pair | ~$0.36 |
| Cost 28 pairs | **~$10.06** |

This matches QA estimate of $9.21.

---

## 5. NEW EXECUTION SEQUENCE

| Step | Action | Status |
|------|--------|--------|
| ~~1~~ | ~~Create parallel_feature_testing.py~~ | DONE |
| ~~2~~ | ~~Run dry_run (55 features)~~ | DONE |
| **2b** | **EXPAND query to 6,477 features** | **REQUIRED** |
| **2c** | **Re-run dry_run (6,477 features)** | **REQUIRED** |
| 3 | Report NEW dry run results to CE | REQUIRED |
| 4 | Await CE approval | GATE |
| 5 | Run single pair test | After approval |
| 6 | Run full 28-pair test | After approval |

---

## 6. DELIVERABLES

1. **Updated `parallel_feature_testing.py`** with full feature query
2. **New dry run report** showing:
   - Feature count: ~6,477
   - Cost per pair: ~$0.36
   - Total cost: ~$10
3. **Column list** confirming all features included

---

## 7. VALIDATION CRITERIA

| Check | Expected |
|-------|----------|
| Feature count per pair | ~6,477 |
| Tables joined | ~256 per pair |
| Cost per pair | $0.30-0.50 |
| Total 28 pairs | $8-15 |
| All feature types included | reg, mom, vol, der, agg, align, cov, corr, tri, mkt |

---

## DO NOT

- DO NOT proceed with 55-feature subset
- DO NOT skip dry run validation
- DO NOT assume current query satisfies mandate

---

**Chief Engineer (CE)**
**Date**: December 10, 2025 05:20
**Status**: QUERY EXPANSION REQUIRED - RE-RUN DRY RUN AFTER EXPANSION
