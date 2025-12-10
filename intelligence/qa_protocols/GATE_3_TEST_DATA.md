# GATE_3 Test Data Requirements

**Document Type**: QA Protocol
**Created**: December 10, 2025
**Purpose**: Define test data requirements for GATE_3 re-validation

---

## Sample Size Requirements (USER MANDATE)

| Metric | Requirement | Source |
|--------|-------------|--------|
| SHAP samples | **100,000+** | USER MANDATE |
| Validation rows | 100K+ recommended | Walk-forward splits |
| Pairs | Start EURUSD, then 27 others | Sequential validation |

---

## Data Sources

### Primary: BigQuery V2 Tables

| Dataset | Tables | Description |
|---------|--------|-------------|
| `bqx_ml_v3_features_v2` | 462 per pair | Engineered features |
| `bqx_ml_v3_analytics_v2` | 54 total | Target tables |

### Feature Universe

| Metric | Value |
|--------|-------|
| Total columns per pair | 11,337 |
| Unique features per pair | 1,064 |
| Expected after stability selection | 200-600 |

---

## Validation Data Split

Per walk-forward validation requirements:

```
Train:      T-365 to T-30 days
Validation: T-30 to T-7 days
Test:       T-7 to T days
```

### EURUSD Row Counts (Approximate)

| Split | Days | Rows (1-min bars) |
|-------|------|-------------------|
| Train | 335 | ~480,000 |
| Validation | 23 | ~33,000 |
| Test | 7 | ~10,000 |
| **Total** | 365 | ~523,000 |

---

## GATE_3 Validation Order

### Phase 1: EURUSD (Priority)

| Horizon | Status | Notes |
|---------|--------|-------|
| h15 | FIRST | Baseline model |
| h30 | After h15 | |
| h45 | After h30 | |
| h60-h105 | Sequential | |

### Phase 2: Major Pairs (5)

| Pair | Priority |
|------|----------|
| GBPUSD | HIGH |
| USDJPY | HIGH |
| AUDUSD | HIGH |
| USDCAD | MEDIUM |

### Phase 3: Cross/Minor Pairs (22)

After major pairs validated.

---

## Calibration Data Requirements

For each pair-horizon, need:

| File | Contents |
|------|----------|
| `calibrated_stack_{pair}_h{horizon}.json` | Gating results, thresholds |
| `shap_{pair}_h{horizon}.json` | SHAP values (100K+ samples) |

---

## Coverage Targets

| Metric | Target | Current (59-feature) |
|--------|--------|----------------------|
| Called Accuracy | ≥85% | 91.70% |
| Coverage | 30-50% | 17.33% |

**Note**: Coverage below 30% with 59-feature model. Expected to improve with expanded feature universe (200-600 selected features from 1,064 unique).

---

## Validation Scripts

| Script | Purpose |
|--------|---------|
| `scripts/validate_gate3.py` | Full GATE_3 validation |
| `scripts/validate_coverage.py` | Coverage-specific validation |

---

**QA Agent**
**Date**: December 10, 2025
