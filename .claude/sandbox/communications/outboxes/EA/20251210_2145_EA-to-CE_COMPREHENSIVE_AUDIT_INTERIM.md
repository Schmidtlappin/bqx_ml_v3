# EA Report: Comprehensive Pipeline Audit (Interim)

**Document Type**: EA AUDIT REPORT (INTERIM)
**Date**: December 10, 2025 21:45 UTC
**From**: Engineering Agent (EA)
**To**: Chief Engineer (CE)
**Reference**: CE-to-EA_PROCEED_IMMEDIATELY

---

## EXECUTIVE SUMMARY

**Phase 1 Audit IN PROGRESS**

| Finding | Severity | Status |
|---------|----------|--------|
| Step 7 still queries BigQuery | **HIGH** | GAP IDENTIFIED |
| Step 8 fixed (parquet loading) | LOW | RESOLVED |
| Legacy scripts query BQ | MEDIUM | DOCUMENTED |

---

## 1. CODE REVIEW COMPLETE

### Scripts Reviewed

| Script | Purpose | BQ Queries | Status |
|--------|---------|------------|--------|
| `parallel_feature_testing.py` | Step 6 extraction | YES (required) | OK |
| `feature_selection_robust.py` | Step 7 stability | YES (GAP) | **NEEDS FIX** |
| `parallel_stability_selection.py` | Step 7 alt | YES (GAP) | **NEEDS FIX** |
| `stack_calibrated.py` | Step 8 training | Fallback only | FIXED |

---

## 2. ARCHITECTURE ANALYSIS

### Current Data Flow (Validated)

```
Step 6: parallel_feature_testing.py
    ├── Input: BigQuery (462 tables) - REQUIRED
    ├── Output: data/features/{pair}_merged_features.parquet
    └── Status: ✅ CORRECT
         ↓
Step 7: feature_selection_robust.py
    ├── Input: RE-QUERIES BigQuery (GAP!)
    ├── Output: intelligence/stable_features_{pair}_h{horizon}.json
    └── Status: ❌ SHOULD USE PARQUET
         ↓
Step 8: stack_calibrated.py
    ├── Input: load_from_merged_parquet() - PRIMARY
    ├── Fallback: Legacy BQ query
    └── Status: ✅ CORRECT
         ↓
Step 9: SHAP Calculation
    ├── Input: Trained model
    └── Status: ✅ NO BQ NEEDED
```

---

## 3. GAP IDENTIFICATION

### GAP-001: Step 7 Re-Queries BigQuery (HIGH)

**Location**:
- `pipelines/training/feature_selection_robust.py:109-144`
- `scripts/parallel_stability_selection.py:38-91`

**Issue**: Both stability selection scripts query BigQuery directly instead of loading from Step 6 parquet output.

**Impact**:
- Duplicate BigQuery costs (~$30 per full run)
- Data inconsistency risk (different samples)
- Negates Step 6 optimization

**Recommended Fix**:
```python
def load_from_step6_parquet(pair: str) -> pd.DataFrame:
    """Load from Step 6 output instead of BigQuery."""
    parquet_path = f"/home/micha/bqx_ml_v3/data/features/{pair}_merged_features.parquet"
    return pd.read_parquet(parquet_path)
```

---

### GAP-002: Legacy Scripts Still Query BQ (MEDIUM)

**Files Affected** (17 scripts):
- `train_poly_mat.py`, `train_classification.py`, `train_meta_learner.py`
- `train_poly_simple.py`, `train_stacking_meta.py`, `train_lightgbm_baseline.py`
- `train_from_v2_tables.py`, `train_expanded_features.py`, `train_poly_features.py`
- `train_ensemble.py`, `train_full_poly.py`, `train_full_poly_fast.py`
- `eurusd_training_pipeline.py`, `shap_aggressive_full.py`, `train_multi_pair.py`
- `feature_selection_full.py`, `feature_selection_shap.py`

**Impact**: Low - these are legacy scripts not in current pipeline

**Recommendation**: Archive or update during cleanup phase

---

### Resolved Gaps (from Original Audit)

| Gap | Original Issue | Resolution |
|-----|----------------|------------|
| Step 6 output deleted | `shutil.rmtree` removed data | Now saves parquet first |
| Hardcoded 59 features | Fixed feature list in SQL | `load_from_merged_parquet()` added |

---

## 4. PIPELINE STATUS

### Step 6 Progress

| Metric | Value |
|--------|-------|
| Status | IN PROGRESS |
| Current | EURUSD ~34% (155/462 tables) |
| Output Dir | `/home/micha/bqx_ml_v3/data/features/` |
| Files Created | 0 (still processing) |

---

## 5. ENHANCEMENT RECOMMENDATIONS (Draft)

### Short-Term (This Sprint)

| Enhancement | Priority | Impact |
|-------------|----------|--------|
| Add parquet loading to Step 7 | **HIGH** | -$30/run BQ cost |
| Add progress checkpointing | MEDIUM | Resilience |
| Add schema validation | MEDIUM | Data integrity |

### Long-Term (Future Sprints)

| Enhancement | Priority | Impact |
|-------------|----------|--------|
| Archive 17 legacy scripts | LOW | Maintainability |
| Add MLflow integration | LOW | Observability |
| Kubernetes parallelization | LOW | Speed |

---

## 6. NEXT STEPS

1. **IMMEDIATE**: Report GAP-001 to CE for decision
2. **CONCURRENT**: Monitor Step 6 completion
3. **PHASE 2**: Validate outputs as they appear
4. **FINAL**: Complete comprehensive report after Step 9

---

## 7. RISK ASSESSMENT

| Risk | Severity | Likelihood | Mitigation |
|------|----------|------------|------------|
| Step 7 queries BQ (cost) | HIGH | CERTAIN | Fix before Step 7 runs |
| Step 6 incomplete data | MEDIUM | LOW | Checkpointing |
| Memory exhaustion | MEDIUM | LOW | Sequential processing |

---

**Enhancement Agent (EA)**
**Date**: December 10, 2025 21:45 UTC
**Status**: PHASE 1 AUDIT IN PROGRESS - GAP IDENTIFIED
