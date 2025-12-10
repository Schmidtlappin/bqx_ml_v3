# Correlation Strategy Expansion for Polynomial Features

**Date**: 2025-11-29
**Status**: PENDING (Awaiting polynomial feature implementation)
**Impact**: Expand from 817 features to 1,069+ features
**Priority**: HIGH

---

## Executive Summary

The current extreme correlation analysis covers 817 features across 49 target combinations. Once polynomial regression features are implemented, the feature set will expand significantly, requiring re-execution of the correlation matrix and top-100 rankings.

---

## 1. CURRENT STATE

### Features Analyzed
- **Total Features**: 817
- **Source Tables**: 24 EURUSD tables
- **Targets**: 49 (7 windows × 7 horizons)

### Current Feature Categories
| Category | Features | Status |
|----------|----------|--------|
| BQX Base | ~70 | ✓ Analyzed |
| AGG (Aggregation) | ~70 | ✓ Analyzed |
| MOM (Momentum) | ~70 | ✓ Analyzed |
| REG (Regression - simple) | ~70 | ✓ Analyzed |
| VOL (Volatility) | ~70 | ✓ Analyzed |
| ALIGN (Alignment) | ~70 | ✓ Analyzed |
| DER (Derivative) | ~70 | ✓ Analyzed |
| EXT (Extremity) | ~70 | ✓ Analyzed |
| MRT (Mean-Reversion) | ~70 | ✓ Analyzed |
| Others | ~187 | ✓ Analyzed |
| **Total** | **817** | **Complete** |

### Current Top Performers
| Rank | Feature | Max Correlation |
|------|---------|-----------------|
| 1 | reg_slope_720 | 0.9709 |
| 2 | mom_diff_720 | 0.9702 |
| 3 | der_v1_720 | 0.9702 |
| 4 | bqx_720 | 0.9689 |
| 5 | mom_roc_720 | 0.9689 |

---

## 2. EXPANDED STATE (Post-Polynomial Implementation)

### New Features to Add
Once polynomial features are implemented, add:

#### Per reg_ Table (IDX + BQX)
| Feature | Per Window | × Windows | Total |
|---------|------------|-----------|-------|
| reg_quad_term_{W} | 1 | 7 | 7 |
| reg_lin_term_{W} | 1 | 7 | 7 |
| reg_const_term_{W} | 1 | 7 | 7 |
| reg_quad_norm_{W} | 1 | 7 | 7 |
| reg_lin_norm_{W} | 1 | 7 | 7 |
| reg_r2_{W} | 1 | 7 | 7 |
| reg_rmse_{W} | 1 | 7 | 7 |
| reg_resid_std_{W} | 1 | 7 | 7 |
| reg_resid_last_{W} | 1 | 7 | 7 |
| reg_resid_skew_{W} | 1 | 7 | 7 |
| reg_resid_kurt_{W} | 1 | 7 | 7 |
| reg_acceleration_{W} | 1 | 7 | 7 |
| reg_trend_str_{W} | 1 | 7 | 7 |
| reg_forecast_5_{W} | 1 | 7 | 7 |
| reg_curv_sign_{W} | 1 | 7 | 7 |
| **Per Table** | **15** | **7** | **105** |
| **IDX + BQX** | | | **210** |

### Expected Feature Count
| Category | Current | After Expansion |
|----------|---------|-----------------|
| Existing features | 817 | 817 |
| New polynomial (IDX) | 0 | 105 |
| New polynomial (BQX) | 0 | 105 |
| **Total** | **817** | **1,027** |

With additional derived features:
| Category | Features |
|----------|----------|
| Base + polynomial | 1,027 |
| Cross-feature interactions | ~42 |
| **Grand Total** | **1,069+** |

---

## 3. CORRELATION CALCULATION STRATEGY

### Methodology (Unchanged)
1. **Extreme Selection**: 5,000 points (|BQX_45| > 2σ)
2. **Window Extraction**: 301 intervals per extreme
3. **Pooled Correlation**: Pearson across all windows
4. **49 Targets**: 7 windows × 7 horizons

### New Feature Integration
For each new polynomial feature `reg_{metric}_{W}`:

```sql
-- Add to correlation calculation
CORR(CAST(f.reg_quad_term_{W} AS FLOAT64), t.delta_w{TW}_h{H}) as corr_quad_{W}_w{TW}_h{H},
CORR(CAST(f.reg_lin_term_{W} AS FLOAT64), t.delta_w{TW}_h{H}) as corr_lin_{W}_w{TW}_h{H},
CORR(CAST(f.reg_r2_{W} AS FLOAT64), t.delta_w{TW}_h{H}) as corr_r2_{W}_w{TW}_h{H},
...
```

### Cross-Feature Analysis (New)
Analyze correlation between polynomial features and existing features:

```sql
-- Example: How does quad_term relate to existing momentum?
CORR(f.reg_quad_term_720, f.mom_diff_720) as poly_mom_correlation,
CORR(f.reg_lin_term_720, f.der_v1_720) as poly_der_correlation
```

---

## 4. HYPOTHESIS: Expected High Performers

Based on mathematical relationships, these polynomial features should rank highly:

### Tier 1: Expected Ultra-High Correlation (>0.90)
| Feature | Hypothesis |
|---------|------------|
| reg_lin_term_720 | Should correlate highly with existing reg_slope_720 |
| reg_acceleration_720 | Second derivative of trend, predictive of reversals |
| reg_forecast_5_720 | Direct prediction feature |
| reg_trend_str_720 | Normalized trend strength |

### Tier 2: Expected High Correlation (0.80-0.90)
| Feature | Hypothesis |
|---------|------------|
| reg_quad_term_* | Curvature indicates acceleration/deceleration |
| reg_r2_* | Fit quality indicates trend reliability |
| reg_resid_last_* | Prediction error at current point |

### Tier 3: Expected Moderate Correlation (0.70-0.80)
| Feature | Hypothesis |
|---------|------------|
| reg_resid_std_* | Volatility around trend |
| reg_curv_sign_* | Direction of curvature change |
| reg_quad_norm_* | Normalized curvature for cross-window comparison |

---

## 5. IMPLEMENTATION PLAN

### Phase 1: Wait for BA Implementation
- **Dependency**: Polynomial features must be implemented in reg_ tables
- **Status**: Directive sent to BA
- **ETA**: ~8 hours

### Phase 2: Update Correlation Scripts
After polynomial features exist:

```python
# Update batch_full_correlation.py to include new columns
NEW_POLYNOMIAL_COLUMNS = [
    'reg_quad_term_{W}',
    'reg_lin_term_{W}',
    'reg_const_term_{W}',
    'reg_quad_norm_{W}',
    'reg_lin_norm_{W}',
    'reg_r2_{W}',
    'reg_rmse_{W}',
    'reg_resid_std_{W}',
    'reg_resid_last_{W}',
    'reg_resid_skew_{W}',
    'reg_resid_kurt_{W}',
    'reg_acceleration_{W}',
    'reg_trend_str_{W}',
    'reg_forecast_5_{W}',
    'reg_curv_sign_{W}'
]

# Expand across all windows
WINDOWS = [45, 90, 180, 360, 720, 1440, 2880]
ALL_NEW_COLUMNS = [col.format(W=w) for col in NEW_POLYNOMIAL_COLUMNS for w in WINDOWS]
```

### Phase 3: Re-run Full Correlation Matrix
```bash
python3 scripts/batch_full_correlation.py --include-polynomial
```

Expected output:
- `full_correlation_matrix` table updated (1,069+ rows × 54 columns)
- `top100_per_target` table updated (4,900 rows)

### Phase 4: Regenerate Reports
```bash
# Export updated CSV files
bq extract --destination_format=CSV \
  'bqx-ml:bqx_ml_v3_analytics_v2.full_correlation_matrix' \
  gs://bqx-ml-exports/correlation_matrix_expanded.csv

bq extract --destination_format=CSV \
  'bqx-ml:bqx_ml_v3_analytics_v2.top100_per_target' \
  gs://bqx-ml-exports/top100_expanded.csv
```

### Phase 5: Update Documentation
- Update [EXTREME_CORRELATION_ANALYSIS_RESULTS.md](../docs/EXTREME_CORRELATION_ANALYSIS_RESULTS.md)
- Add polynomial features to Top 50 rankings
- Document any surprising findings

---

## 6. EXPECTED OUTCOMES

### Ranking Changes
The top performers are likely to shift:

| Current Top 5 | Expected New Top 5 |
|---------------|-------------------|
| reg_slope_720 | reg_lin_term_720 (same as slope?) |
| mom_diff_720 | reg_forecast_5_720 |
| der_v1_720 | reg_acceleration_720 |
| bqx_720 | bqx_720 |
| mom_roc_720 | reg_trend_str_720 |

### Feature Redundancy Analysis
Need to identify if polynomial features are redundant with existing:
- `reg_lin_term` vs `reg_slope` (likely highly correlated)
- `reg_acceleration` vs `der_v1` (related but different)
- `reg_resid_std` vs `vol_*` (complementary)

### Model Selection Impact
Top polynomial features should be added to model training:
- If `reg_quad_term` correlates >0.85, include in feature set
- If `reg_forecast_5` performs well, use as ensemble input

---

## 7. SUCCESS CRITERIA

- [ ] All polynomial features added to correlation matrix
- [ ] Full correlation matrix has 1,069+ rows
- [ ] Top 100 rankings regenerated for all 49 targets
- [ ] CSV exports updated with expanded features
- [ ] Documentation updated with new findings
- [ ] Feature redundancy analysis complete
- [ ] Model training feature set updated

---

## 8. TIMELINE

| Phase | Task | Duration | Dependency |
|-------|------|----------|------------|
| 1 | BA polynomial implementation | ~8 hours | None |
| 2 | Update correlation scripts | ~1 hour | Phase 1 |
| 3 | Re-run correlation matrix | ~2 hours | Phase 2 |
| 4 | Regenerate reports | ~30 min | Phase 3 |
| 5 | Update documentation | ~1 hour | Phase 4 |
| **Total** | | **~12.5 hours** | |

---

*Document created: 2025-11-29*
*Chief Engineer, BQX ML V3*
