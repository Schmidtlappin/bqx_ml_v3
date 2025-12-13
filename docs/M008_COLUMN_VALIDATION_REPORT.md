# M008 Column Naming Validation Report

**Date**: 2025-12-13 10:20:53 UTC
**Feature Catalogue**: v3.1.0
**Total Features**: 1604
**Compliant**: 1402 (87.4%)
**Non-Compliant**: 202 (12.6%)

---

## VIOLATION SUMMARY

| Violation Type | Count | Percentage |
|----------------|-------|------------|
| WINDOW_VIOLATION | 162 | 80.2% |
| PATTERN_VIOLATION | 40 | 19.8% |

---

## PATTERN_VIOLATION (40 features)

### 1. `bqx_1440`

**Feature Type**: bqx
**Violation**: Does not match M008 column pattern

### 2. `bqx_180`

**Feature Type**: bqx
**Violation**: Does not match M008 column pattern

### 3. `bqx_2880`

**Feature Type**: bqx
**Violation**: Does not match M008 column pattern

### 4. `bqx_360`

**Feature Type**: bqx
**Violation**: Does not match M008 column pattern

### 5. `bqx_45`

**Feature Type**: bqx
**Violation**: Does not match M008 column pattern

### 6. `bqx_720`

**Feature Type**: bqx
**Violation**: Does not match M008 column pattern

### 7. `bqx_90`

**Feature Type**: bqx
**Violation**: Does not match M008 column pattern

### 8. `dir_1440`

**Feature Type**: dir
**Violation**: Does not match M008 column pattern

### 9. `dir_180`

**Feature Type**: dir
**Violation**: Does not match M008 column pattern

### 10. `dir_360`

**Feature Type**: dir
**Violation**: Does not match M008 column pattern

### 11. `dir_45`

**Feature Type**: dir
**Violation**: Does not match M008 column pattern

### 12. `dir_720`

**Feature Type**: dir
**Violation**: Does not match M008 column pattern

### 13. `dir_90`

**Feature Type**: dir
**Violation**: Does not match M008 column pattern

### 14. `ema_45`

**Feature Type**: ema
**Violation**: Does not match M008 column pattern

### 15. `ema_90`

**Feature Type**: ema
**Violation**: Does not match M008 column pattern

### 16. `momentum_45`

**Feature Type**: momentum
**Violation**: Does not match M008 column pattern

### 17. `momentum_90`

**Feature Type**: momentum
**Violation**: Does not match M008 column pattern

### 18. `pos_1440`

**Feature Type**: pos
**Violation**: Does not match M008 column pattern

### 19. `pos_180`

**Feature Type**: pos
**Violation**: Does not match M008 column pattern

### 20. `pos_360`

**Feature Type**: pos
**Violation**: Does not match M008 column pattern

*...and 20 more features*

---

## WINDOW_VIOLATION (162 features)

### 1. `align_mean_score`

**Feature Type**: align
**Violation**: Missing or invalid window size (must end with 45, 90, 180, 360, 720, 1440, or 2880)

### 2. `align_trend_score`

**Feature Type**: align
**Violation**: Missing or invalid window size (must end with 45, 90, 180, 360, 720, 1440, or 2880)

### 3. `align_unanimous`

**Feature Type**: align
**Violation**: Missing or invalid window size (must end with 45, 90, 180, 360, 720, 1440, or 2880)

### 4. `arb_opportunity`

**Feature Type**: arb
**Violation**: Missing or invalid window size (must end with 45, 90, 180, 360, 720, 1440, or 2880)

### 5. `audusd`

**Feature Type**: unknown
**Violation**: Missing or invalid window size (must end with 45, 90, 180, 360, 720, 1440, or 2880)

### 6. `avg_market_corr`

**Feature Type**: avg
**Violation**: Missing or invalid window size (must end with 45, 90, 180, 360, 720, 1440, or 2880)

### 7. `base_curr`

**Feature Type**: base
**Violation**: Missing or invalid window size (must end with 45, 90, 180, 360, 720, 1440, or 2880)

### 8. `bqx_close`

**Feature Type**: bqx
**Violation**: Missing or invalid window size (must end with 45, 90, 180, 360, 720, 1440, or 2880)

### 9. `close_idx`

**Feature Type**: close
**Violation**: Missing or invalid window size (must end with 45, 90, 180, 360, 720, 1440, or 2880)

### 10. `corr_30min`

**Feature Type**: corr
**Violation**: Missing or invalid window size (must end with 45, 90, 180, 360, 720, 1440, or 2880)

### 11. `corr_60min`

**Feature Type**: corr
**Violation**: Missing or invalid window size (must end with 45, 90, 180, 360, 720, 1440, or 2880)

### 12. `corr_90min`

**Feature Type**: corr
**Violation**: Missing or invalid window size (must end with 45, 90, 180, 360, 720, 1440, or 2880)

### 13. `corr_change`

**Feature Type**: corr
**Violation**: Missing or invalid window size (must end with 45, 90, 180, 360, 720, 1440, or 2880)

### 14. `corr_regime`

**Feature Type**: corr
**Violation**: Missing or invalid window size (must end with 45, 90, 180, 360, 720, 1440, or 2880)

### 15. `covar_60min`

**Feature Type**: covar
**Violation**: Missing or invalid window size (must end with 45, 90, 180, 360, 720, 1440, or 2880)

### 16. `cross_curr`

**Feature Type**: cross
**Violation**: Missing or invalid window size (must end with 45, 90, 180, 360, 720, 1440, or 2880)

### 17. `csi_align_mean_score`

**Feature Type**: csi
**Violation**: Missing or invalid window size (must end with 45, 90, 180, 360, 720, 1440, or 2880)

### 18. `csi_align_trend_score`

**Feature Type**: csi
**Violation**: Missing or invalid window size (must end with 45, 90, 180, 360, 720, 1440, or 2880)

### 19. `csi_align_unanimous`

**Feature Type**: csi
**Violation**: Missing or invalid window size (must end with 45, 90, 180, 360, 720, 1440, or 2880)

### 20. `csi_cyc_avg_cycle_length`

**Feature Type**: csi
**Violation**: Missing or invalid window size (must end with 45, 90, 180, 360, 720, 1440, or 2880)

*...and 142 more features*

---
