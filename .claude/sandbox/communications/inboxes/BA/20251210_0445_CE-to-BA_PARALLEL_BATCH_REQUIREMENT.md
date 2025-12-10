# CE Directive: MANDATORY Parallel Batch Processing Implementation

**Document Type**: CE DIRECTIVE (BLOCKING)
**Date**: December 10, 2025 04:45
**From**: Chief Engineer (CE)
**To**: Build Agent (BA)
**Priority**: **CRITICAL** - BLOCKING
**Reference**:
- 20251210_0430_CE-to-QA_SHAP_COST_ESTIMATE
- 20251210_0345_CE-to-BA_FULL_FEATURE_UNIVERSE_TESTING

---

## BLOCKING REQUIREMENT

**DO NOT proceed with full 6,477 feature testing until parallel batch processing is implemented.**

---

## PROBLEM IDENTIFIED

Current BA pipelines use **SEQUENTIAL processing**:

| File | Issue |
|------|-------|
| `stack_calibrated.py` | Single pair, single horizon per run |
| `train_multi_pair.py` | Sequential `for pair in pairs:` loop |
| No multiprocessing | No `Pool`, no `concurrent.futures` |

### Cost Impact

| Strategy | Estimated Cost | Time |
|----------|----------------|------|
| Sequential (current) | **~$1,287** | ~200 hours |
| Parallel batch (required) | **~$12** | ~6 hours |

**Risk**: 100× cost overrun if BA runs without batch optimization.

---

## REQUIRED IMPLEMENTATION

### 1. Batch Query Strategy (MANDATORY)

Query features ONCE per pair, retrieve ALL 7 horizons:

```python
# BEFORE (wrong - 7 queries per pair)
for horizon in [15, 30, 45, 60, 75, 90, 105]:
    query = f"SELECT ... WHERE horizon = {horizon}"

# AFTER (correct - 1 query per pair)
query = """
SELECT
    features.*,
    targets.target_bqx45_h15,
    targets.target_bqx45_h30,
    targets.target_bqx45_h45,
    targets.target_bqx45_h60,
    targets.target_bqx45_h75,
    targets.target_bqx45_h90,
    targets.target_bqx45_h105
FROM feature_tables features
JOIN targets ON features.interval_time = targets.interval_time
"""
# Then process all 7 horizons locally from single DataFrame
```

### 2. Parallel Worker Implementation (MANDATORY)

```python
from concurrent.futures import ProcessPoolExecutor
import multiprocessing

def process_pair(pair: str) -> dict:
    """Process all 7 horizons for one pair."""
    # 1. Query all features + all targets (single query)
    df = query_pair_data(pair)

    # 2. Run stability selection locally
    # 3. Train models locally
    # 4. Compute SHAP locally
    return results

def main():
    pairs = ALL_28_PAIRS
    max_workers = min(8, multiprocessing.cpu_count())

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(process_pair, pairs))
```

### 3. Memory Management (REQUIRED)

| Constraint | Limit |
|------------|-------|
| Workers | 8 max (64 GB total) |
| Per-worker memory | 8 GB |
| DataFrame size | ~70 GB per pair (sample to 80K rows) |

---

## FILE TO CREATE

Create new file: `pipelines/training/parallel_feature_testing.py`

### Required Functions

```python
def query_pair_all_horizons(pair: str) -> pd.DataFrame:
    """Single query for all features + all 7 target columns."""
    pass

def run_stability_selection_local(df: pd.DataFrame, horizon: int) -> list:
    """Run stability selection on local DataFrame."""
    pass

def process_pair_all_horizons(pair: str) -> dict:
    """Process one pair: query once, test all horizons."""
    pass

def run_parallel_testing(pairs: list, max_workers: int = 8) -> dict:
    """Run parallel processing across pairs."""
    pass
```

---

## ACCEPTANCE CRITERIA

- [ ] Single BigQuery query per pair (not per horizon)
- [ ] All 7 horizons processed from single DataFrame
- [ ] `ProcessPoolExecutor` or `multiprocessing.Pool` implemented
- [ ] Max 8 workers (configurable)
- [ ] Memory usage monitored and bounded
- [ ] Total BigQuery cost < $50 for full 28-pair run

---

## VALIDATION BEFORE EXECUTION

Before running full 6,477 feature test, BA must:

1. **Dry run cost estimate**: Query 1 pair, verify bytes scanned
2. **Confirm batch query**: Show single query returns all horizons
3. **Confirm parallel execution**: Show worker count in logs
4. **CE approval**: Report estimated total cost for approval

---

## TIMELINE

| Step | Action |
|------|--------|
| 1 | Implement `parallel_feature_testing.py` |
| 2 | Test on EURUSD only (single pair) |
| 3 | Report cost and time to CE |
| 4 | Await CE approval for full 28-pair run |

---

## DO NOT

- DO NOT run sequential queries (196+ queries)
- DO NOT skip batch optimization
- DO NOT exceed $50 budget without CE approval
- DO NOT proceed without implementing parallel workers

---

**Chief Engineer (CE)**
**Date**: December 10, 2025 04:45
**Status**: BLOCKING - IMPLEMENT BEFORE PROCEEDING
