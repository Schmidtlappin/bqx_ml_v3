# CE Directive: 50% Stability Threshold APPROVED

**Document Type**: USER MANDATE
**Date**: December 9, 2025
**From**: Chief Engineer (CE)
**To**: Build Agent (BA)
**Priority**: HIGH
**Status**: USER APPROVED

---

## USER DECISION: APPROVED

**Stability Threshold: 50%** (lowered from 60%)

This is now a **BINDING MANDATE** per user approval.

---

## IMPACT

### Feature Selection Changes

| Parameter | Previous | Approved |
|-----------|----------|----------|
| Stability threshold | 60% | **50%** |
| Expected retained features | ~399 | **~607** |
| Additional features included | - | **+208** |
| High-importance features recovered | 0 | **42** |

### Features Now Included

The following high-importance features (previously lost at 60%) will now be retained:

| Feature | Importance | Frequency |
|---------|------------|-----------|
| ext_bqx_eurusd_ext_distance_zero | 449.0 | 50% |
| rev_bqx_eurusd_rev_exhaustion | 349.6 | 50% |
| lag_idx_eurusd_w90_hl_range_90 | 349.0 | 50% |
| lag_idx_eurusd_w45_volatility_45 | 322.6 | 50% |
| lag_bqx_eurusd_90_ema_90 | 222.0 | 50% |
| base_bqx_eurusd_target_90 | 209.8 | 50% |
| + 202 more features | various | 50-59% |

### Expected Accuracy Impact

| Scenario | Called Accuracy | Coverage |
|----------|-----------------|----------|
| 60% threshold (399 features) | 82.5% | 79% |
| **50% threshold (607 features)** | **84-87%** | **75-80%** |

---

## IMPLEMENTATION

### Pipeline Update Required

Update `pipelines/training/feature_selection_robust.py`:

```python
# OLD (60% - DEPRECATED)
# STABILITY_THRESHOLD = 0.6

# NEW (50% - USER APPROVED)
STABILITY_THRESHOLD = float(os.getenv('STABILITY_THRESHOLD', '0.5'))
```

### Environment Variable Support

For flexibility, the threshold is parameterized:
```bash
# Default (user approved)
STABILITY_THRESHOLD=0.5

# Override for testing
export STABILITY_THRESHOLD=0.5
python feature_selection_robust.py
```

---

## BA DIRECTIVE

When Phase 2 (Feature Selection) begins:

1. **Use 50% threshold** (not 60%)
2. **Expect ~607 retained features** (not ~399)
3. **Document** retained feature count in ledger
4. **Validate** high-importance features are included

---

## MANDATE STATUS

| Mandate | Value | Authority | Status |
|---------|-------|-----------|--------|
| SHAP sample size | 100,000+ | USER | BINDING |
| Ledger coverage | 100% (6,477) | USER | BINDING |
| **Stability threshold** | **50%** | **USER** | **BINDING** |

---

**CE Signature**: Claude (Chief Engineer, BQX ML V3)
**Date**: December 9, 2025
**Authority**: USER MANDATE
