# BQX ML V3 Feature Table Directory

**Last Updated:** 2025-11-29
**Purpose:** Complete directory of all tables required for 100% feature matrix coverage

---

## Executive Summary

| Category | Required Tables | Current | Gap | Coverage |
|----------|----------------|---------|-----|----------|
| PRIMARY | 392 | 504 | 0 | 128.6% |
| CORRELATION | 448 | 448 | 0 | 100.0% |
| COVARIANCE | 2,352 | 554 | 1,798 | 23.6% |
| **TOTAL** | **3,192** | **1,506** | **1,798** | **47.2%** |

---

## 1. PRIMARY FEATURES (392 Required, 504 Actual)

Per-pair feature tables. Each pair gets one table per feature type.

### Structure
```
{feature_type}_{pair}        # IDX variant
{feature_type}_bqx_{pair}    # BQX variant
```

### Feature Types (7 types × 2 variants × 28 pairs = 392 tables)

| Type | Description | IDX Tables | BQX Tables | Status |
|------|-------------|------------|------------|--------|
| lag | Lagged BQX values | 28 | 28 | ✓ COMPLETE |
| regime | Market regime indicators | 28 | 28 | ✓ COMPLETE |
| reg | Regression features | 28 | 28 | ✓ COMPLETE |
| agg | Aggregation features | 28 | 28 | ✓ COMPLETE |
| mom | Momentum features | 28 | 28 | ✓ COMPLETE |
| vol | Volatility features | 28 | 28 | ✓ COMPLETE |
| align | Alignment features | 28 | 28 | ✓ COMPLETE |

### Complete Table List - PRIMARY

#### lag (56 tables)
```
lag_eurusd, lag_gbpusd, lag_usdjpy, lag_usdchf, lag_audusd, lag_usdcad, lag_nzdusd,
lag_eurgbp, lag_eurjpy, lag_eurchf, lag_euraud, lag_eurcad, lag_eurnzd,
lag_gbpjpy, lag_gbpchf, lag_gbpaud, lag_gbpcad, lag_gbpnzd,
lag_audjpy, lag_audchf, lag_audcad, lag_audnzd,
lag_nzdjpy, lag_nzdchf, lag_nzdcad,
lag_cadjpy, lag_cadchf, lag_chfjpy

lag_bqx_eurusd, lag_bqx_gbpusd, lag_bqx_usdjpy, lag_bqx_usdchf, lag_bqx_audusd, lag_bqx_usdcad, lag_bqx_nzdusd,
lag_bqx_eurgbp, lag_bqx_eurjpy, lag_bqx_eurchf, lag_bqx_euraud, lag_bqx_eurcad, lag_bqx_eurnzd,
lag_bqx_gbpjpy, lag_bqx_gbpchf, lag_bqx_gbpaud, lag_bqx_gbpcad, lag_bqx_gbpnzd,
lag_bqx_audjpy, lag_bqx_audchf, lag_bqx_audcad, lag_bqx_audnzd,
lag_bqx_nzdjpy, lag_bqx_nzdchf, lag_bqx_nzdcad,
lag_bqx_cadjpy, lag_bqx_cadchf, lag_bqx_chfjpy
```

#### regime (56 tables)
```
regime_eurusd, regime_gbpusd, regime_usdjpy, regime_usdchf, regime_audusd, regime_usdcad, regime_nzdusd,
regime_eurgbp, regime_eurjpy, regime_eurchf, regime_euraud, regime_eurcad, regime_eurnzd,
regime_gbpjpy, regime_gbpchf, regime_gbpaud, regime_gbpcad, regime_gbpnzd,
regime_audjpy, regime_audchf, regime_audcad, regime_audnzd,
regime_nzdjpy, regime_nzdchf, regime_nzdcad,
regime_cadjpy, regime_cadchf, regime_chfjpy

regime_bqx_eurusd, regime_bqx_gbpusd, regime_bqx_usdjpy, regime_bqx_usdchf, regime_bqx_audusd, regime_bqx_usdcad, regime_bqx_nzdusd,
regime_bqx_eurgbp, regime_bqx_eurjpy, regime_bqx_eurchf, regime_bqx_euraud, regime_bqx_eurcad, regime_bqx_eurnzd,
regime_bqx_gbpjpy, regime_bqx_gbpchf, regime_bqx_gbpaud, regime_bqx_gbpcad, regime_bqx_gbpnzd,
regime_bqx_audjpy, regime_bqx_audchf, regime_bqx_audcad, regime_bqx_audnzd,
regime_bqx_nzdjpy, regime_bqx_nzdchf, regime_bqx_nzdcad,
regime_bqx_cadjpy, regime_bqx_cadchf, regime_bqx_chfjpy
```

#### reg, agg, mom, vol, align (56 tables each)
Same pattern as above for each type.

---

## 2. CORRELATION FEATURES (448 Required, 448 Actual)

Correlation between currency pairs and external assets.

### Structure
```
corr_ibkr_{pair}_{asset}        # IDX variant (28 pairs × 8 assets = 224)
corr_bqx_ibkr_{pair}_{asset}    # BQX variant (28 pairs × 8 assets = 224)
```

### External Assets (8)
| Asset | Description |
|-------|-------------|
| EWA | Australia ETF |
| EWG | Germany ETF |
| EWJ | Japan ETF |
| EWU | UK ETF |
| GLD | Gold ETF |
| SPY | S&P 500 ETF |
| UUP | US Dollar ETF |
| VIX | Volatility Index |

### Status: ✓ COMPLETE (448/448)

---

## 3. COVARIANCE FEATURES (2,352 Required, 554 Actual)

Covariance between currency pairs that SHARE A COMMON CURRENCY.

### Structure
```
cov_{type}_{pair1}_{pair2}        # IDX variant
cov_{type}_bqx_{pair1}_{pair2}    # BQX variant
```

### Pair Combinations (168 unique)

Pairs sharing a currency get covariance tables:

| Currency | Pairs | Combinations (7C2) |
|----------|-------|-------------------|
| USD | eurusd, gbpusd, usdjpy, usdchf, audusd, usdcad, nzdusd | 21 |
| EUR | eurusd, eurgbp, eurjpy, eurchf, euraud, eurcad, eurnzd | 21 |
| GBP | gbpusd, eurgbp, gbpjpy, gbpchf, gbpaud, gbpcad, gbpnzd | 21 |
| JPY | usdjpy, eurjpy, gbpjpy, audjpy, nzdjpy, cadjpy, chfjpy | 21 |
| CHF | usdchf, eurchf, gbpchf, audchf, nzdchf, cadchf, chfjpy | 21 |
| AUD | audusd, euraud, gbpaud, audjpy, audchf, audcad, audnzd | 21 |
| CAD | usdcad, eurcad, gbpcad, audcad, nzdcad, cadjpy, cadchf | 21 |
| NZD | nzdusd, eurnzd, gbpnzd, audnzd, nzdjpy, nzdchf, nzdcad | 21 |

**Total unique combinations: 168** (deduplicated across currencies)

### Covariance Types (7 types × 2 variants = 14 prefixes)

| Type | Description | Required | Current | Gap |
|------|-------------|----------|---------|-----|
| cov_agg | Aggregation covariance | 168 | 51 | 117 |
| cov_agg_bqx | Aggregation covariance (BQX) | 168 | 51 | 117 |
| cov_align | Alignment covariance | 168 | 51 | 117 |
| cov_align_bqx | Alignment covariance (BQX) | 168 | 51 | 117 |
| cov_mom | Momentum covariance | 168 | 51 | 117 |
| cov_mom_bqx | Momentum covariance (BQX) | 168 | 51 | 117 |
| cov_reg | Regression covariance | 168 | 51 | 117 |
| cov_reg_bqx | Regression covariance (BQX) | 168 | 51 | 117 |
| cov_vol | Volatility covariance | 168 | 51 | 117 |
| cov_vol_bqx | Volatility covariance (BQX) | 168 | 51 | 117 |
| cov_lag | Lag covariance | 168 | 11 | 157 |
| cov_lag_bqx | Lag covariance (BQX) | 168 | 11 | 157 |
| cov_regime | Regime covariance | 168 | 11 | 157 |
| cov_regime_bqx | Regime covariance (BQX) | 168 | 11 | 157 |

### Complete Pair Combination List (168)

#### USD-based combinations (21)
```
eurusd_gbpusd, eurusd_usdjpy, eurusd_usdchf, eurusd_audusd, eurusd_usdcad, eurusd_nzdusd,
gbpusd_usdjpy, gbpusd_usdchf, gbpusd_audusd, gbpusd_usdcad, gbpusd_nzdusd,
usdjpy_usdchf, usdjpy_audusd, usdjpy_usdcad, usdjpy_nzdusd,
usdchf_audusd, usdchf_usdcad, usdchf_nzdusd,
audusd_usdcad, audusd_nzdusd,
usdcad_nzdusd
```

#### EUR-based combinations (21)
```
eurusd_eurgbp, eurusd_eurjpy, eurusd_eurchf, eurusd_euraud, eurusd_eurcad, eurusd_eurnzd,
eurgbp_eurjpy, eurgbp_eurchf, eurgbp_euraud, eurgbp_eurcad, eurgbp_eurnzd,
eurjpy_eurchf, eurjpy_euraud, eurjpy_eurcad, eurjpy_eurnzd,
eurchf_euraud, eurchf_eurcad, eurchf_eurnzd,
euraud_eurcad, euraud_eurnzd,
eurcad_eurnzd
```

#### GBP-based combinations (21)
```
gbpusd_eurgbp, gbpusd_gbpjpy, gbpusd_gbpchf, gbpusd_gbpaud, gbpusd_gbpcad, gbpusd_gbpnzd,
eurgbp_gbpjpy, eurgbp_gbpchf, eurgbp_gbpaud, eurgbp_gbpcad, eurgbp_gbpnzd,
gbpjpy_gbpchf, gbpjpy_gbpaud, gbpjpy_gbpcad, gbpjpy_gbpnzd,
gbpchf_gbpaud, gbpchf_gbpcad, gbpchf_gbpnzd,
gbpaud_gbpcad, gbpaud_gbpnzd,
gbpcad_gbpnzd
```

#### JPY-based combinations (21)
```
usdjpy_eurjpy, usdjpy_gbpjpy, usdjpy_audjpy, usdjpy_nzdjpy, usdjpy_cadjpy, usdjpy_chfjpy,
eurjpy_gbpjpy, eurjpy_audjpy, eurjpy_nzdjpy, eurjpy_cadjpy, eurjpy_chfjpy,
gbpjpy_audjpy, gbpjpy_nzdjpy, gbpjpy_cadjpy, gbpjpy_chfjpy,
audjpy_nzdjpy, audjpy_cadjpy, audjpy_chfjpy,
nzdjpy_cadjpy, nzdjpy_chfjpy,
cadjpy_chfjpy
```

#### CHF-based combinations (21)
```
usdchf_eurchf, usdchf_gbpchf, usdchf_audchf, usdchf_nzdchf, usdchf_cadchf, usdchf_chfjpy,
eurchf_gbpchf, eurchf_audchf, eurchf_nzdchf, eurchf_cadchf, eurchf_chfjpy,
gbpchf_audchf, gbpchf_nzdchf, gbpchf_cadchf, gbpchf_chfjpy,
audchf_nzdchf, audchf_cadchf, audchf_chfjpy,
nzdchf_cadchf, nzdchf_chfjpy,
cadchf_chfjpy
```

#### AUD-based combinations (21)
```
audusd_euraud, audusd_gbpaud, audusd_audjpy, audusd_audchf, audusd_audcad, audusd_audnzd,
euraud_gbpaud, euraud_audjpy, euraud_audchf, euraud_audcad, euraud_audnzd,
gbpaud_audjpy, gbpaud_audchf, gbpaud_audcad, gbpaud_audnzd,
audjpy_audchf, audjpy_audcad, audjpy_audnzd,
audchf_audcad, audchf_audnzd,
audcad_audnzd
```

#### CAD-based combinations (21)
```
usdcad_eurcad, usdcad_gbpcad, usdcad_audcad, usdcad_nzdcad, usdcad_cadjpy, usdcad_cadchf,
eurcad_gbpcad, eurcad_audcad, eurcad_nzdcad, eurcad_cadjpy, eurcad_cadchf,
gbpcad_audcad, gbpcad_nzdcad, gbpcad_cadjpy, gbpcad_cadchf,
audcad_nzdcad, audcad_cadjpy, audcad_cadchf,
nzdcad_cadjpy, nzdcad_cadchf,
cadjpy_cadchf
```

#### NZD-based combinations (21)
```
nzdusd_eurnzd, nzdusd_gbpnzd, nzdusd_audnzd, nzdusd_nzdjpy, nzdusd_nzdchf, nzdusd_nzdcad,
eurnzd_gbpnzd, eurnzd_audnzd, eurnzd_nzdjpy, eurnzd_nzdchf, eurnzd_nzdcad,
gbpnzd_audnzd, gbpnzd_nzdjpy, gbpnzd_nzdchf, gbpnzd_nzdcad,
audnzd_nzdjpy, audnzd_nzdchf, audnzd_nzdcad,
nzdjpy_nzdchf, nzdjpy_nzdcad,
nzdchf_nzdcad
```

---

## 4. REMEDIATION REQUIRED

### Tables to Create: 1,798

| Batch | Types | Tables | Time Est. |
|-------|-------|--------|-----------|
| 1 | cov_agg + cov_agg_bqx | 234 | 1 hr |
| 2 | cov_align + cov_align_bqx | 234 | 1 hr |
| 3 | cov_mom + cov_mom_bqx | 234 | 1 hr |
| 4 | cov_reg + cov_reg_bqx | 234 | 1 hr |
| 5 | cov_vol + cov_vol_bqx | 234 | 1 hr |
| 6 | cov_lag + cov_lag_bqx | 314 | 1.5 hr |
| 7 | cov_regime + cov_regime_bqx | 314 | 1.5 hr |
| **TOTAL** | | **1,798** | **~8 hrs** |

### BA Directive Status
- **OPTION A AUTHORIZED**: Full 1,798 table creation
- **Priority**: CRITICAL
- **Mandate Alignment**: PERFORMANCE_FIRST

---

## 5. POST-REMEDIATION STATE

| Category | Tables | Coverage |
|----------|--------|----------|
| PRIMARY | 504 | 100%+ |
| CORRELATION | 448 | 100% |
| COVARIANCE | 2,352 | 100% |
| **TOTAL** | **3,304** | **100%** |

---

## Appendix: 28 Currency Pairs Reference

| # | Pair | Base | Quote |
|---|------|------|-------|
| 1 | EURUSD | EUR | USD |
| 2 | GBPUSD | GBP | USD |
| 3 | USDJPY | USD | JPY |
| 4 | USDCHF | USD | CHF |
| 5 | AUDUSD | AUD | USD |
| 6 | USDCAD | USD | CAD |
| 7 | NZDUSD | NZD | USD |
| 8 | EURGBP | EUR | GBP |
| 9 | EURJPY | EUR | JPY |
| 10 | EURCHF | EUR | CHF |
| 11 | EURAUD | EUR | AUD |
| 12 | EURCAD | EUR | CAD |
| 13 | EURNZD | EUR | NZD |
| 14 | GBPJPY | GBP | JPY |
| 15 | GBPCHF | GBP | CHF |
| 16 | GBPAUD | GBP | AUD |
| 17 | GBPCAD | GBP | CAD |
| 18 | GBPNZD | GBP | NZD |
| 19 | AUDJPY | AUD | JPY |
| 20 | AUDCHF | AUD | CHF |
| 21 | AUDCAD | AUD | CAD |
| 22 | AUDNZD | AUD | NZD |
| 23 | NZDJPY | NZD | JPY |
| 24 | NZDCHF | NZD | CHF |
| 25 | NZDCAD | NZD | CAD |
| 26 | CADJPY | CAD | JPY |
| 27 | CADCHF | CAD | CHF |
| 28 | CHFJPY | CHF | JPY |

---

*Document generated: 2025-11-29*
*Dataset: bqx-ml:bqx_ml_v3_features*
