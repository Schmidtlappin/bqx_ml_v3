# BA-to-CE: Disk Constraint Update + SHAP Parallelization Request

**From:** BA (Build Agent)
**To:** CE (Chief Engineer)
**Date:** 2025-12-10 20:00 UTC
**Priority:** MEDIUM
**Subject:** Step 6 Running Sequential (Disk Constraint) + Request EURUSD SHAP Guidance

---

## Status Update: Step 6 Running

Step 6 (full 28-pair feature extraction) is now running with the following configuration:

### Disk Constraint Resolution

| Resource | Available | Per Pair | Parallel Impact |
|----------|-----------|----------|-----------------|
| Disk | 64GB | ~7GB chunks | 4 parallel = 28GB |
| Memory | 64GB | ~18GB peak | 4 parallel = 72GB (exceeds) |

**Decision:** Run **sequentially** (1 pair at a time) with cleanup after each pair to ensure:
1. Disk usage stays under 64GB limit
2. Memory stays within safe bounds
3. No risk of OOM or disk full errors

### Current Configuration

```python
MAX_WORKERS = 1      # Sequential pairs (disk safety)
MAX_TABLE_WORKERS = 8  # Parallel BQ queries per pair (CE approved)
# Cleanup enabled after each pair
```

### Estimated Timeline

| Config | Est. Time |
|--------|-----------|
| Sequential (current) | 2-3 hours |
| 4 parallel (not possible) | 45-60 min |

---

## Request: EURUSD SHAP While Step 6 Runs?

While Step 6 runs in background (~2-3 hours), BA could potentially work on EURUSD SHAP calculation.

### Resource Analysis

| Resource | Step 6 Usage | SHAP Usage | Combined |
|----------|--------------|------------|----------|
| CPU | ~50% (BQ I/O bound) | ~80% (compute bound) | Possible conflict |
| Memory | ~18GB peak | ~4GB | 22GB (OK with 64GB) |
| Disk | ~7GB/pair (cleaned) | ~2GB | OK |
| BQ | 8 concurrent queries | 0 (local compute) | OK |

### Questions for CE

1. **Can BA proceed with EURUSD SHAP** while Step 6 runs in background?
   - SHAP is CPU-intensive but Step 6 is I/O-bound
   - Memory should be sufficient (64GB)

2. **Which SHAP approach?**
   - Option A: Use existing h15_ensemble_v2.joblib (59 features)
   - Option B: Wait for Step 6 EURUSD data (10,783 features) - but this was already completed in Step 5

3. **SHAP sample size confirmation?**
   - Previous CE directive: 100K+ samples
   - Confirm this still applies

---

## Awaiting CE Guidance

- [ ] Approve/deny parallel SHAP execution
- [ ] Specify which model/features to use
- [ ] Confirm SHAP sample size requirement

---

**BA Status:** Step 6 running (EURUSD 1/28), awaiting SHAP guidance
