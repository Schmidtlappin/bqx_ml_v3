# EA Report: Pipeline Audit & Optimization Review

**Document Type**: EA TECHNICAL AUDIT
**Date**: December 10, 2025 20:30 UTC
**From**: Engineering Agent (EA)
**To**: Chief Engineer (CE)
**Reference**: CE-to-EA_PIPELINE_AUDIT

---

## EXECUTIVE SUMMARY

**CRITICAL GAPS IDENTIFIED**: Pipeline stages are NOT properly connected.

Current pipeline is **3 disconnected scripts** that each query BigQuery independently. Step 6 output is **transient** and not consumed by downstream stages.

---

## 1. PIPELINE INTEGRITY CHECK

| Question | Answer | Details |
|----------|--------|---------|
| Are all stages properly connected? | **NO** | See Gap Analysis below |
| Are inputs/outputs correctly specified? | **NO** | No intermediate persistence |
| Are there missing stages? | **YES** | No data handoff mechanism |
| Are there data format mismatches? | **YES** | Parquet → JSON → SQL (incompatible) |

---

## 2. GAP ANALYSIS

### Current Pipeline (AS-IS)

```
Step 6: parallel_feature_testing.py
    ├── Input: BigQuery (462 tables)
    ├── Output: /tmp/feature_chunks/{pair}/*.parquet (DELETED after use!)
    └── Returns: JSON summary only
         ↓
    ❌ NO CONNECTION ❌
         ↓
Stability Selection: feature_selection_robust.py
    ├── Input: RE-QUERIES BigQuery (ignores Step 6)
    ├── Output: /tmp/robust_feature_selection_{pair}_h{horizon}.json
    └── Stability scores for features
         ↓
    ⚠️ WEAK CONNECTION ⚠️
         ↓
Training: stack_calibrated.py
    ├── Input: HARDCODED 59 features (line 431-487)
    ├── load_selected_features() reads JSON but FALLBACK is hardcoded
    └── Output: JSON metrics, joblib model
```

### Gap Details

#### GAP 1: Step 6 Output is Transient (CRITICAL)

**Location**: `parallel_feature_testing.py:368`
```python
# Cleanup chunk files to save disk space (ENABLED - 56GB disk limit)
shutil.rmtree(pair_chunk_dir)
```

**Impact**: All feature data from Step 6 is **deleted immediately**. No downstream stage can consume it.

**Fix Required**: Persist merged feature data or pass directly to stability selection.

---

#### GAP 2: Stability Selection Re-Queries BigQuery (HIGH)

**Location**: `feature_selection_robust.py:109-147` and `parallel_stability_selection.py:52-91`

Both scripts query BigQuery independently instead of consuming Step 6 output.

**Impact**:
- Duplicate BigQuery costs (~$30 per run)
- Potential data inconsistency (different samples)
- Wasted Step 6 computation

---

#### GAP 3: Training Uses Hardcoded Features (CRITICAL)

**Location**: `stack_calibrated.py:431-487`

```python
query = f"""
    SELECT
        reg_idx.interval_time,
        -- Polynomial IDX (priority) - using V2 column names
        reg_idx.reg_quad_term_45, reg_idx.reg_lin_term_45, reg_idx.reg_total_var_45,
        ...
        -- 59 HARDCODED FEATURES
```

**Impact**: Even after stability selection identifies optimal features, training still uses hardcoded 59 features.

**Fix Required**: Training must dynamically load features from stability selection output.

---

#### GAP 4: No Feature Ledger Integration (MEDIUM)

**Missing**: No pipeline writes to feature ledger (`bqx_ml_v3_analytics_v2.feature_ledger_{pair}`)

**Impact**: Feature provenance not tracked. SHAP values not persisted to ledger.

---

## 3. VALIDATED PIPELINE DIAGRAM (TO-BE)

```
Step 6: Feature Extraction (parallel_feature_testing.py)
    Input: BigQuery (462 tables, 11,337 columns)
    Output: /data/features/{pair}_features.parquet (PERSISTENT)
         ↓
    [NEW: Data Handoff]
         ↓
Step 7: Stability Selection (feature_selection_robust.py)
    Input: /data/features/{pair}_features.parquet
    Output: /intelligence/stable_features_{pair}_h{horizon}.json
         ↓
    [NEW: Dynamic Feature Loading]
         ↓
Step 8: Training (stack_calibrated.py)
    Input: stable_features JSON → Dynamic BigQuery query
    Output: /models/{pair}/h{horizon}_ensemble_v2.joblib
         ↓
Step 9: SHAP Calculation
    Input: Trained model + feature data
    Output: /intelligence/shap_{pair}_h{horizon}.json
         ↓
    [NEW: Ledger Write]
         ↓
Step 10: Feature Ledger Update
    Output: BigQuery feature_ledger_{pair}
```

---

## 4. OPTIMIZATION RECOMMENDATIONS

### Short-Term (This Sprint)

| Area | Current | Recommended | Impact |
|------|---------|-------------|--------|
| **Step 6 Output** | Deleted after processing | Persist to `/data/features/` | CRITICAL - enables pipeline |
| **Stability Selection Input** | Re-queries BigQuery | Read from Step 6 parquet | -$30 cost, +consistency |
| **Training Feature Load** | Hardcoded 59 features | Dynamic from JSON | CRITICAL - enables full universe |
| **Memory Management** | 100K samples | Keep 100K (validated) | Stable |

### Long-Term (Future Sprints)

| Area | Current | Recommended | Impact |
|------|---------|-------------|--------|
| **Unified Pipeline** | 3 separate scripts | Single orchestrator with stages | Maintainability |
| **Feature Store** | Ad-hoc parquet files | BigQuery materialized views | Cost reduction |
| **Caching** | None | Redis/Memcached for feature embeddings | Speed |
| **Monitoring** | Manual | MLflow/Weights & Biases integration | Observability |
| **Parallelization** | Sequential pairs | Kubernetes Job parallelization | Speed |

---

## 5. RISK ASSESSMENT

| Risk | Severity | Likelihood | Mitigation |
|------|----------|------------|------------|
| Step 6 data loss | HIGH | CERTAIN | Persist output before delete |
| Feature mismatch train/inference | HIGH | HIGH | Use same feature source |
| BigQuery cost overrun | MEDIUM | LOW | Dry run validation (already done) |
| Memory OOM during merge | MEDIUM | MEDIUM | Batch processing (implemented) |
| Stability selection inconsistency | MEDIUM | MEDIUM | Seed control (implemented) |

---

## 6. IMMEDIATE ACTION ITEMS

### P0: CRITICAL (Before Step 7)

1. **Modify `parallel_feature_testing.py`**:
   - Comment out line 368 (`shutil.rmtree`)
   - Save merged features to persistent location
   - Return feature file path in results JSON

2. **Modify `stack_calibrated.py`**:
   - Remove hardcoded 59-feature query (lines 431-487)
   - Add function to load features from stability selection JSON
   - Build dynamic query from selected features

### P1: HIGH (This Session)

3. **Create data handoff**:
   - Define output schema for Step 6
   - Define input schema for Step 7
   - Validate schema compatibility

4. **Update `feature_selection_robust.py`**:
   - Add option to read from parquet instead of BigQuery
   - Reduce BigQuery dependency

---

## 7. FILES REQUIRING MODIFICATION

| File | Change | Priority |
|------|--------|----------|
| `parallel_feature_testing.py:368` | Remove/disable `shutil.rmtree` | P0 |
| `parallel_feature_testing.py` | Add persistent output path | P0 |
| `stack_calibrated.py:431-487` | Replace hardcoded query | P0 |
| `stack_calibrated.py:39-52` | Enhance `load_selected_features()` | P0 |
| `feature_selection_robust.py` | Add parquet input option | P1 |

---

## 8. SUMMARY

| Status | Count |
|--------|-------|
| Critical Gaps | 2 |
| High Gaps | 2 |
| Medium Gaps | 1 |
| Short-term Fixes | 4 |
| Long-term Improvements | 5 |

**Pipeline Status**: NOT PRODUCTION-READY until gaps resolved.

**Recommendation**: Fix P0 items before proceeding with Step 7 (Stability Selection).

---

**Enhancement Agent (EA)**
**Date**: December 10, 2025 20:30 UTC
**Status**: PIPELINE AUDIT COMPLETE - ACTION REQUIRED
