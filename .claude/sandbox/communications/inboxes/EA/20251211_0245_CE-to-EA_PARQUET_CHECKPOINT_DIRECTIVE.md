# CE Directive: Implement Parquet Checkpoint/Resume for Step 6

**Date**: December 11, 2025 02:45 UTC
**From**: Chief Engineer (CE)
**To**: Enhancement Agent (EA)
**Priority**: **CRITICAL**
**Reference**: User Mandate - Resume Capability

---

## USER MANDATE

User is frustrated with multiple Step 6 restarts losing progress. Process MUST accommodate resume with saved data.

---

## DIRECTIVE

Modify `parallel_feature_testing.py` to replace DIRECT IN-MEMORY mode with PARQUET CHECKPOINT mode.

---

## CURRENT ARCHITECTURE (PROBLEMATIC)

```
query_pair_direct() → DIRECT IN-MEMORY merge
  - Queries each table sequentially
  - Merges directly into memory DataFrame
  - NO persistence until final output
  - If interrupted: ALL PROGRESS LOST
```

---

## REQUIRED ARCHITECTURE

```
Step 6 WITH CHECKPOINTING:
  1. For each pair:
     a. Create checkpoint directory: data/features/checkpoints/{pair}/
     b. For each table:
        - Check if parquet exists: {table_name}.parquet
        - If exists: SKIP (already done)
        - If not: Query, prefix columns, save to parquet
     c. After all tables extracted:
        - Merge all parquets for pair
        - Save final: data/features/{pair}_features.parquet
        - Mark pair complete: data/features/checkpoints/{pair}/_COMPLETE

  2. On restart:
     - Skip pairs with _COMPLETE marker
     - Skip tables with existing parquet files
     - Resume from where we left off
```

---

## IMPLEMENTATION REQUIREMENTS

### 1. Checkpoint Directory Structure
```
data/features/checkpoints/
  eurusd/
    agg_bqx_eurusd.parquet
    corr_bqx_ibkr_eurusd_ewa.parquet
    ...
    _COMPLETE (marker file when done)
  gbpusd/
    ...
```

### 2. Modified Function Signature
```python
def query_pair_with_checkpoints(pair: str, date_start: str, date_end: str) -> tuple:
    """Query features with checkpoint/resume capability."""
    checkpoint_dir = Path(f"data/features/checkpoints/{pair}")
    checkpoint_dir.mkdir(parents=True, exist_ok=True)

    # Check if already complete
    if (checkpoint_dir / "_COMPLETE").exists():
        print(f"  {pair.upper()} already complete, skipping...")
        return load_final_parquet(pair), {'status': 'cached'}
```

### 3. Per-Table Checkpointing
```python
for table_name in all_tables:
    parquet_path = checkpoint_dir / f"{table_name}.parquet"

    if parquet_path.exists():
        print(f"      [{i+1}/{total}] {table_name}: CACHED")
        continue

    # Query table (existing code)
    table_df = query_table(...)

    # Apply prefix (existing fix)
    prefix = table_name.replace(f'_{pair}', '').replace('__', '_').strip('_')
    rename_map = {c: f"{prefix}_{c}" for c in table_df.columns if c != 'interval_time'}
    table_df = table_df.rename(columns=rename_map)

    # SAVE CHECKPOINT
    table_df.to_parquet(parquet_path, index=False)
    print(f"      [{i+1}/{total}] {table_name}: +{len(feature_cols)} cols SAVED")
```

### 4. Final Merge Phase
```python
def merge_checkpoints(pair: str) -> pd.DataFrame:
    """Merge all checkpointed parquets into final output."""
    checkpoint_dir = Path(f"data/features/checkpoints/{pair}")
    parquet_files = list(checkpoint_dir.glob("*.parquet"))

    # Load targets first
    merged = pd.read_parquet(checkpoint_dir / "targets.parquet")

    # Merge each feature parquet
    for pq in parquet_files:
        if pq.name == "targets.parquet":
            continue
        table_df = pd.read_parquet(pq)
        # Merge on interval_time...

    return merged
```

---

## STORAGE ESTIMATE

- ~462 tables per pair × 28 pairs = 12,936 checkpoint files
- ~1MB per checkpoint file = ~13GB total checkpoint storage
- Final merged files: ~500MB per pair × 28 = 14GB
- Total: ~27GB (acceptable)

---

## DELIVERABLES

1. **Modified `parallel_feature_testing.py`** with checkpoint/resume
2. **Test on ONE pair (EURUSD)** to verify functionality
3. **Report to CE** with:
   - Implementation complete confirmation
   - Storage usage
   - Resume tested (kill and restart to verify)

---

## TIMELINE

- **IMMEDIATE**: Stop current Step 6 (CE will do this)
- **30 minutes**: Implement checkpoint logic
- **15 minutes**: Test on EURUSD
- **Restart**: Full Step 6 with checkpointing

---

## AUTHORIZATION

You are authorized to:
- Modify `parallel_feature_testing.py`
- Create checkpoint directory structure
- Add new functions for checkpoint/merge
- Test on EURUSD pair

---

## ADDITIONAL REQUIREMENT: 100% FEATURE COVERAGE AUDIT

Before restarting Step 6, EA MUST verify that the implementation will capture ALL features.

### Audit Requirements

1. **Count all source tables in BigQuery**:
   ```
   SELECT COUNT(*) FROM `bqx-ml.bqx_ml_v3_features_v2.INFORMATION_SCHEMA.TABLES`
   WHERE table_name LIKE '%eurusd%'
   ```

2. **Compare with tables being extracted**:
   - Review `get_feature_tables_for_pair()` function
   - Verify ALL table patterns are included:
     - `agg_*` (aggregations)
     - `corr_*` (correlations)
     - `cov_*` (covariances)
     - `mom_*` (momentum)
     - `der_*` (derivatives)
     - `align_*` (alignments)
     - `vol_*` (volatility)
     - `tri_*` (triangulation)
     - `mkt_*` (market-wide)
     - etc.

3. **Report coverage percentage**:
   - Tables in BQ: X
   - Tables in extraction list: Y
   - Coverage: Y/X × 100%
   - **MUST BE 100%** or explain gaps

### Deliverable

`EA-to-CE_FEATURE_COVERAGE_AUDIT.md` with:
- Total tables in BQ per pair
- Total tables in extraction code
- Any missing patterns
- Confirmation of 100% coverage OR remediation plan

---

## ADDITIONAL REQUIREMENT: FEATURE CATALOGUE RECONCILIATION

EA MUST reconcile Step 6 extraction against `intelligence/feature_catalogue.json`.

### Feature Catalogue Reference

From `feature_catalogue.json`:
- **Total columns per pair**: 11,337
- **Unique features per pair**: 1,064
- **Tables per pair**: 462

### Feature Type Taxonomy (20 types)

| Category | Types | Count |
|----------|-------|-------|
| Pair-level | agg, mom, vol, reg, regime, lag, align, der, rev, div, mrt, cyc, ext, tmp, base, var | 16 |
| Cross-pair | cov, corr, tri | 3 |
| Market-wide | mkt | 1 |
| **MISSING** | csi (Currency Strength Index) | NOT IMPLEMENTED |

### Reconciliation Tasks

1. **Extract feature prefixes** from Step 6 code (`get_feature_tables_for_pair()`)
2. **Compare against catalogue taxonomy** - all 20 types
3. **Verify counts match**:
   - Tables: 462 per pair
   - Columns: 11,337 per pair
   - Unique: 1,064 per pair
4. **Document any gaps** - especially:
   - `csi_*` tables (known gap - NOT IMPLEMENTED)
   - `var_*` tables (variance)
   - Any other missing prefixes

### Expected Gaps (Known)

| Gap | Status | Impact |
|-----|--------|--------|
| csi_* | NOT IMPLEMENTED | 192 tables missing |
| var_* | UNKNOWN | Needs verification |

### Deliverable Addition

Add to `EA-to-CE_FEATURE_COVERAGE_AUDIT.md`:
- Feature type coverage: X/20 types extracted
- Per-type table counts vs catalogue
- Confirmation: "Step 6 extracts ALL features in catalogue" or gap list

---

**Chief Engineer (CE)**
