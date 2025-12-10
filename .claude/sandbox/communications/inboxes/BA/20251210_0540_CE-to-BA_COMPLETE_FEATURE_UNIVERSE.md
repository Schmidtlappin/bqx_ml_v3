# CE Directive: COMPLETE Feature Universe - Include tri_* and mkt_* Tables

**Document Type**: CE DIRECTIVE (AMENDMENT)
**Date**: December 10, 2025 05:40
**From**: Chief Engineer (CE)
**To**: Build Agent (BA)
**Priority**: **CRITICAL** - BLOCKING
**Reference**:
- 20251210_0530_BA-to-CE_FULL_FEATURE_DRY_RUN
- 20251210_0520_CE-to-BA_FULL_FEATURE_QUERY_EXPANSION

---

## ISSUE IDENTIFIED

BA dry run only queried tables with `eurusd` in the name, missing 63% of features.

| Source | Tables | Columns | BA Included? |
|--------|--------|---------|--------------|
| `%eurusd%` tables | 256 | 4,173 | **YES** |
| `tri_*` tables | 194 | 6,460 | **NO - MISSING** |
| `mkt_*` tables | 12 | 704 | **NO - MISSING** |
| **TOTAL** | **462** | **11,337** | **37% only** |

---

## REQUIRED ACTION

### Query Must Include THREE Table Categories

```python
def get_all_feature_tables(pair: str) -> list:
    """
    Get ALL feature tables for a pair - THREE categories.
    """
    client = bigquery.Client(project=PROJECT)

    # Category 1: Pair-specific tables (e.g., reg_idx_eurusd, agg_bqx_eurusd)
    pair_tables_query = f"""
    SELECT table_id FROM `{PROJECT}.{FEATURES_DATASET}.__TABLES__`
    WHERE table_id LIKE '%{pair}%'
    """

    # Category 2: Triangulation tables (cross-pair, apply to all pairs)
    tri_tables_query = f"""
    SELECT table_id FROM `{PROJECT}.{FEATURES_DATASET}.__TABLES__`
    WHERE table_id LIKE 'tri_%'
    """

    # Category 3: Market-wide tables (apply to all pairs)
    mkt_tables_query = f"""
    SELECT table_id FROM `{PROJECT}.{FEATURES_DATASET}.__TABLES__`
    WHERE table_id LIKE 'mkt_%'
    """

    all_tables = []

    # Execute all three queries
    for query in [pair_tables_query, tri_tables_query, mkt_tables_query]:
        result = client.query(query).result()
        for row in result:
            all_tables.append(row.table_id)

    return all_tables  # Should be ~462 tables for EURUSD
```

---

## TABLE CATEGORIES EXPLAINED

### Category 1: Pair-Specific (`%eurusd%`)

| Pattern | Example | Description |
|---------|---------|-------------|
| `reg_idx_{pair}` | reg_idx_eurusd | Polynomial regression on IDX |
| `reg_bqx_{pair}` | reg_bqx_eurusd | Polynomial regression on BQX |
| `agg_idx_{pair}` | agg_idx_eurusd | Aggregation features IDX |
| `mom_bqx_{pair}` | mom_bqx_eurusd | Momentum features BQX |
| `vol_idx_{pair}` | vol_idx_eurusd | Volatility features IDX |
| `cov_*_{pair}` | cov_agg_gbpusd_eurusd | Covariance with other pairs |
| ... | ... | ~256 tables total |

### Category 2: Triangulation (`tri_*`)

| Pattern | Example | Description |
|---------|---------|-------------|
| `tri_{pair1}_{pair2}_{pair3}` | tri_eurusd_gbpusd_eurgbp | 3-pair triangulation |
| `tri_bqx_{...}` | tri_bqx_eurusd_usdjpy_eurjpy | BQX triangulation |

**Note**: Triangulation tables are CROSS-PAIR. They apply to EURUSD training even if "eurusd" is not in the table name.

**Tables**: 194
**Columns**: 6,460

### Category 3: Market-Wide (`mkt_*`)

| Pattern | Example | Description |
|---------|---------|-------------|
| `mkt_agg_*` | mkt_agg_mean | Market-wide aggregates |
| `mkt_vol_*` | mkt_vol_std | Market-wide volatility |
| `mkt_regime_*` | mkt_regime_cluster | Market regime indicators |

**Note**: Market-wide tables contain features aggregated across ALL pairs. They apply to EURUSD training.

**Tables**: 12
**Columns**: 704

---

## UPDATED QUERY STRUCTURE

```python
def build_complete_feature_query(pair: str) -> dict:
    """
    Build queries for COMPLETE feature universe.

    Returns dict with three query lists for batched execution.
    """

    queries = {
        'pair_specific': [],    # ~256 tables, 4,173 columns
        'triangulation': [],    # ~194 tables, 6,460 columns
        'market_wide': []       # ~12 tables, 704 columns
    }

    # Get all tables
    client = bigquery.Client(project=PROJECT)

    # Category 1: Pair-specific
    pair_tables = client.query(f"""
        SELECT table_id FROM `{PROJECT}.{FEATURES_DATASET}.__TABLES__`
        WHERE table_id LIKE '%{pair}%'
    """).result()
    queries['pair_specific'] = [row.table_id for row in pair_tables]

    # Category 2: Triangulation (ALL tri_* tables)
    tri_tables = client.query(f"""
        SELECT table_id FROM `{PROJECT}.{FEATURES_DATASET}.__TABLES__`
        WHERE table_id LIKE 'tri_%'
    """).result()
    queries['triangulation'] = [row.table_id for row in tri_tables]

    # Category 3: Market-wide (ALL mkt_* tables)
    mkt_tables = client.query(f"""
        SELECT table_id FROM `{PROJECT}.{FEATURES_DATASET}.__TABLES__`
        WHERE table_id LIKE 'mkt_%'
    """).result()
    queries['market_wide'] = [row.table_id for row in mkt_tables]

    return queries


def query_all_features_batched(pair: str, date_start: str, date_end: str) -> pd.DataFrame:
    """
    Query ALL features using batched approach.

    1. Query pair-specific tables (256 tables)
    2. Query triangulation tables (194 tables)
    3. Query market-wide tables (12 tables)
    4. Merge all DataFrames by interval_time
    """

    table_groups = build_complete_feature_query(pair)
    all_dfs = []

    # Process each category
    for category, tables in table_groups.items():
        print(f"  Querying {category}: {len(tables)} tables")

        for table in tables:
            query = f"""
            SELECT * FROM `{PROJECT}.{FEATURES_DATASET}.{table}`
            WHERE DATE(interval_time) BETWEEN '{date_start}' AND '{date_end}'
            """
            df = client.query(query).to_dataframe()
            all_dfs.append(df)

    # Merge all DataFrames
    result = all_dfs[0]
    for df in all_dfs[1:]:
        # Merge on interval_time, handling duplicate columns
        result = result.merge(df, on='interval_time', how='outer', suffixes=('', '_dup'))
        # Drop duplicate columns
        result = result.loc[:, ~result.columns.str.endswith('_dup')]

    return result
```

---

## EXPECTED RESULTS (COMPLETE UNIVERSE)

| Metric | Previous (partial) | Expected (complete) |
|--------|-------------------|---------------------|
| Tables | 256 | **462** |
| Columns | 4,173 | **~11,337** |
| GB per pair | 68.81 | ~180 GB (estimate) |
| Cost per pair | $0.43 | ~$1.12 |
| Cost 28 pairs | $12.04 | **~$31.50** |

**Still within $50 budget.**

---

## VALIDATION CRITERIA

Before reporting completion, verify:

| Check | Expected |
|-------|----------|
| `%eurusd%` tables included | 256 tables |
| `tri_*` tables included | 194 tables |
| `mkt_*` tables included | 12 tables |
| **Total tables** | **~462** |
| **Total columns** | **~11,337** |
| Cost per pair | $1.00-1.50 |
| Total 28 pairs | $28-42 |

---

## EXECUTION SEQUENCE

| Step | Status | Action |
|------|--------|--------|
| ~~2b~~ | DONE | Expanded to 4,173 features (partial) |
| **2d** | **REQUIRED** | Add tri_* tables (6,460 columns) |
| **2e** | **REQUIRED** | Add mkt_* tables (704 columns) |
| **2f** | **REQUIRED** | Re-run dry_run with COMPLETE universe |
| 3 | PENDING | Report NEW dry run results |
| 4 | GATE | Await CE approval |

---

## DO NOT

- DO NOT proceed with 4,173 features (37% coverage)
- DO NOT skip tri_* tables (largest category)
- DO NOT skip mkt_* tables (market context)
- DO NOT report completion until all 462 tables included

---

## SUMMARY

| Requirement | Value |
|-------------|-------|
| Tables to query | **462** (not 256) |
| Columns to capture | **~11,337** (not 4,173) |
| Cost estimate | ~$31.50 (within budget) |
| Categories | pair-specific + tri_* + mkt_* |

---

**Chief Engineer (CE)**
**Date**: December 10, 2025 05:40
**Status**: COMPLETE FEATURE UNIVERSE REQUIRED - ADD tri_* AND mkt_* TABLES
