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

## 6. ADDITIONAL FEATURES - OSCILLATION PREDICTION (280 New Tables)

New feature types optimized for oscillating BQX prediction and game theory trading.

### Executive Summary - Additional Features

| Category | Required Tables | Current | Gap | Coverage | Architecture |
|----------|----------------|---------|-----|----------|--------------|
| REVERSAL (rev_) | 56 | 0 | 56 | 0% | INTERVAL-CENTRIC |
| DERIVATIVE (der_) | 56 | 0 | 56 | 0% | INTERVAL-CENTRIC |
| EXTREMITY (ext_) | 28 | 0 | 28 | 0% | INTERVAL-CENTRIC |
| CYCLE (cyc_) | 28 | 0 | 28 | 0% | INTERVAL-CENTRIC |
| DIVERGENCE (div_) | 56 | 0 | 56 | 0% | INTERVAL-CENTRIC |
| MEAN-REVERSION (mrt_) | 28 | 0 | 28 | 0% | INTERVAL-CENTRIC |
| TEMPORAL (tmp_) | 28 | 0 | 28 | 0% | **TIME-CENTRIC** |
| **TOTAL ADDITIONAL** | **280** | **0** | **280** | **0%** | |

### 6.1 REVERSAL DETECTION (rev_) - 56 Tables

Detect when BQX oscillation is about to change direction.

#### Structure
```
rev_{pair}           # IDX variant (28 tables)
rev_bqx_{pair}       # BQX variant (28 tables)
```

#### Game Theory Value
- Predicts WHEN momentum traders will exit
- Enables entry BEFORE reversal
- Highest ROI for contrarian strategy

#### Complete Table List - rev_
```
rev_eurusd, rev_gbpusd, rev_usdjpy, rev_usdchf, rev_audusd, rev_usdcad, rev_nzdusd,
rev_eurgbp, rev_eurjpy, rev_eurchf, rev_euraud, rev_eurcad, rev_eurnzd,
rev_gbpjpy, rev_gbpchf, rev_gbpaud, rev_gbpcad, rev_gbpnzd,
rev_audjpy, rev_audchf, rev_audcad, rev_audnzd,
rev_nzdjpy, rev_nzdchf, rev_nzdcad,
rev_cadjpy, rev_cadchf, rev_chfjpy

rev_bqx_eurusd, rev_bqx_gbpusd, rev_bqx_usdjpy, rev_bqx_usdchf, rev_bqx_audusd, rev_bqx_usdcad, rev_bqx_nzdusd,
rev_bqx_eurgbp, rev_bqx_eurjpy, rev_bqx_eurchf, rev_bqx_euraud, rev_bqx_eurcad, rev_bqx_eurnzd,
rev_bqx_gbpjpy, rev_bqx_gbpchf, rev_bqx_gbpaud, rev_bqx_gbpcad, rev_bqx_gbpnzd,
rev_bqx_audjpy, rev_bqx_audchf, rev_bqx_audcad, rev_bqx_audnzd,
rev_bqx_nzdjpy, rev_bqx_nzdchf, rev_bqx_nzdcad,
rev_bqx_cadjpy, rev_bqx_cadchf, rev_bqx_chfjpy
```

---

### 6.2 DERIVATIVE (der_) - 56 Tables

Velocity and acceleration of BQX changes.

#### Structure
```
der_{pair}           # IDX variant (28 tables)
der_bqx_{pair}       # BQX variant (28 tables)
```

#### Game Theory Value
- Velocity: HOW FAST momentum is building/fading
- Acceleration: Is momentum gaining or losing steam
- Jerk: Captures sudden changes before they manifest

#### Complete Table List - der_
```
der_eurusd, der_gbpusd, der_usdjpy, der_usdchf, der_audusd, der_usdcad, der_nzdusd,
der_eurgbp, der_eurjpy, der_eurchf, der_euraud, der_eurcad, der_eurnzd,
der_gbpjpy, der_gbpchf, der_gbpaud, der_gbpcad, der_gbpnzd,
der_audjpy, der_audchf, der_audcad, der_audnzd,
der_nzdjpy, der_nzdchf, der_nzdcad,
der_cadjpy, der_cadchf, der_chfjpy

der_bqx_eurusd, der_bqx_gbpusd, der_bqx_usdjpy, der_bqx_usdchf, der_bqx_audusd, der_bqx_usdcad, der_bqx_nzdusd,
der_bqx_eurgbp, der_bqx_eurjpy, der_bqx_eurchf, der_bqx_euraud, der_bqx_eurcad, der_bqx_eurnzd,
der_bqx_gbpjpy, der_bqx_gbpchf, der_bqx_gbpaud, der_bqx_gbpcad, der_bqx_gbpnzd,
der_bqx_audjpy, der_bqx_audchf, der_bqx_audcad, der_bqx_audnzd,
der_bqx_nzdjpy, der_bqx_nzdchf, der_bqx_nzdcad,
der_bqx_cadjpy, der_bqx_cadchf, der_bqx_chfjpy
```

---

### 6.3 EXTREMITY METRICS (ext_) - 28 Tables (BQX only)

Quantify how extreme current BQX is relative to history.

#### Structure
```
ext_bqx_{pair}       # BQX variant ONLY (28 tables)
```

**Note**: No IDX variant - extremity is specifically about BQX values.

#### Game Theory Value
- Extremes are where contrarian strategy acts (|BQX| > 1σ)
- "How extreme" directly informs position sizing
- Features that predict extremity = features that predict opportunity

#### Complete Table List - ext_
```
ext_bqx_eurusd, ext_bqx_gbpusd, ext_bqx_usdjpy, ext_bqx_usdchf, ext_bqx_audusd, ext_bqx_usdcad, ext_bqx_nzdusd,
ext_bqx_eurgbp, ext_bqx_eurjpy, ext_bqx_eurchf, ext_bqx_euraud, ext_bqx_eurcad, ext_bqx_eurnzd,
ext_bqx_gbpjpy, ext_bqx_gbpchf, ext_bqx_gbpaud, ext_bqx_gbpcad, ext_bqx_gbpnzd,
ext_bqx_audjpy, ext_bqx_audchf, ext_bqx_audcad, ext_bqx_audnzd,
ext_bqx_nzdjpy, ext_bqx_nzdchf, ext_bqx_nzdcad,
ext_bqx_cadjpy, ext_bqx_cadchf, ext_bqx_chfjpy
```

---

### 6.4 CYCLE POSITION (cyc_) - 28 Tables (BQX only)

Position in BQX oscillation cycle.

#### Structure
```
cyc_bqx_{pair}       # BQX variant ONLY (28 tables)
```

**Note**: No IDX variant - cycles are in BQX oscillation, not price.

#### Game Theory Value
- Oscillations have rhythm - knowing position is predictive
- "How long can this continue?" - cycle duration informs probability
- Mean-reversion probability increases with cycle duration

#### Complete Table List - cyc_
```
cyc_bqx_eurusd, cyc_bqx_gbpusd, cyc_bqx_usdjpy, cyc_bqx_usdchf, cyc_bqx_audusd, cyc_bqx_usdcad, cyc_bqx_nzdusd,
cyc_bqx_eurgbp, cyc_bqx_eurjpy, cyc_bqx_eurchf, cyc_bqx_euraud, cyc_bqx_eurcad, cyc_bqx_eurnzd,
cyc_bqx_gbpjpy, cyc_bqx_gbpchf, cyc_bqx_gbpaud, cyc_bqx_gbpcad, cyc_bqx_gbpnzd,
cyc_bqx_audjpy, cyc_bqx_audchf, cyc_bqx_audcad, cyc_bqx_audnzd,
cyc_bqx_nzdjpy, cyc_bqx_nzdchf, cyc_bqx_nzdcad,
cyc_bqx_cadjpy, cyc_bqx_cadchf, cyc_bqx_chfjpy
```

---

### 6.5 CROSS-WINDOW DIVERGENCE (div_) - 56 Tables

Disagreement between BQX windows - early reversal warning.

#### Structure
```
div_{pair}           # IDX variant (28 tables)
div_bqx_{pair}       # BQX variant (28 tables)
```

#### Game Theory Value
- Short-term window reversing while long-term extreme = leading indicator
- Alignment = trend strength; Divergence = transition coming
- Cross-window divergence often precedes direction changes

#### Complete Table List - div_
```
div_eurusd, div_gbpusd, div_usdjpy, div_usdchf, div_audusd, div_usdcad, div_nzdusd,
div_eurgbp, div_eurjpy, div_eurchf, div_euraud, div_eurcad, div_eurnzd,
div_gbpjpy, div_gbpchf, div_gbpaud, div_gbpcad, div_gbpnzd,
div_audjpy, div_audchf, div_audcad, div_audnzd,
div_nzdjpy, div_nzdchf, div_nzdcad,
div_cadjpy, div_cadchf, div_chfjpy

div_bqx_eurusd, div_bqx_gbpusd, div_bqx_usdjpy, div_bqx_usdchf, div_bqx_audusd, div_bqx_usdcad, div_bqx_nzdusd,
div_bqx_eurgbp, div_bqx_eurjpy, div_bqx_eurchf, div_bqx_euraud, div_bqx_eurcad, div_bqx_eurnzd,
div_bqx_gbpjpy, div_bqx_gbpchf, div_bqx_gbpaud, div_bqx_gbpcad, div_bqx_gbpnzd,
div_bqx_audjpy, div_bqx_audchf, div_bqx_audcad, div_bqx_audnzd,
div_bqx_nzdjpy, div_bqx_nzdchf, div_bqx_nzdcad,
div_bqx_cadjpy, div_bqx_cadchf, div_bqx_chfjpy
```

---

### 6.6 MEAN-REVERSION TENSION (mrt_) - 28 Tables (BQX only)

Quantify the "spring force" pulling BQX back to zero.

#### Structure
```
mrt_bqx_{pair}       # BQX variant ONLY (28 tables)
```

**Note**: No IDX variant - tension is about BQX mean-reversion, not price.

#### Game Theory Value
- Mean-reversion is the CORE of contrarian strategy
- "Tension" increases as BQX gets more extreme
- Quantifying tension = quantifying opportunity magnitude

#### Complete Table List - mrt_
```
mrt_bqx_eurusd, mrt_bqx_gbpusd, mrt_bqx_usdjpy, mrt_bqx_usdchf, mrt_bqx_audusd, mrt_bqx_usdcad, mrt_bqx_nzdusd,
mrt_bqx_eurgbp, mrt_bqx_eurjpy, mrt_bqx_eurchf, mrt_bqx_euraud, mrt_bqx_eurcad, mrt_bqx_eurnzd,
mrt_bqx_gbpjpy, mrt_bqx_gbpchf, mrt_bqx_gbpaud, mrt_bqx_gbpcad, mrt_bqx_gbpnzd,
mrt_bqx_audjpy, mrt_bqx_audchf, mrt_bqx_audcad, mrt_bqx_audnzd,
mrt_bqx_nzdjpy, mrt_bqx_nzdchf, mrt_bqx_nzdcad,
mrt_bqx_cadjpy, mrt_bqx_cadchf, mrt_bqx_chfjpy
```

---

### 6.7 TEMPORAL PATTERNS (tmp_) - 28 Tables (TIME-CENTRIC EXCEPTION)

Calendar and session effects in BQX behavior.

#### Structure
```
tmp_{pair}           # Per-pair (28 tables) - No IDX/BQX variant
```

#### Architecture Note
**This is the ONLY time-centric feature type.** All other features use interval-based calculations. tmp_ extracts time metadata from each row but does NOT use time-based window functions.

#### Game Theory Value
- BQX behavior varies by trading session (NY momentum > Asian)
- Certain hours produce more extremes
- Session transitions often trigger reversals

#### Complete Table List - tmp_
```
tmp_eurusd, tmp_gbpusd, tmp_usdjpy, tmp_usdchf, tmp_audusd, tmp_usdcad, tmp_nzdusd,
tmp_eurgbp, tmp_eurjpy, tmp_eurchf, tmp_euraud, tmp_eurcad, tmp_eurnzd,
tmp_gbpjpy, tmp_gbpchf, tmp_gbpaud, tmp_gbpcad, tmp_gbpnzd,
tmp_audjpy, tmp_audchf, tmp_audcad, tmp_audnzd,
tmp_nzdjpy, tmp_nzdchf, tmp_nzdcad,
tmp_cadjpy, tmp_cadchf, tmp_chfjpy
```

---

## 7. UPDATED TOTAL FEATURE TABLE REQUIREMENTS

### Combined Summary - All Features

| Category | Required | Current | Gap | Coverage | Priority |
|----------|----------|---------|-----|----------|----------|
| **EXISTING** | | | | | |
| PRIMARY | 392 | 504 | 0 | 128.6% | COMPLETE |
| CORRELATION | 448 | 448 | 0 | 100.0% | COMPLETE |
| COVARIANCE | 2,352 | 554 | 1,798 | 23.6% | IN_PROGRESS |
| **ADDITIONAL (NEW)** | | | | | |
| REVERSAL (rev_) | 56 | 0 | 56 | 0% | PHASE 1 |
| DERIVATIVE (der_) | 56 | 0 | 56 | 0% | PHASE 1 |
| EXTREMITY (ext_) | 28 | 0 | 28 | 0% | PHASE 2 |
| CYCLE (cyc_) | 28 | 0 | 28 | 0% | PHASE 2 |
| DIVERGENCE (div_) | 56 | 0 | 56 | 0% | PHASE 3 |
| MEAN-REVERSION (mrt_) | 28 | 0 | 28 | 0% | PHASE 3 |
| TEMPORAL (tmp_) | 28 | 0 | 28 | 0% | PHASE 4 |
| **GRAND TOTAL** | **3,472** | **1,506** | **2,078** | **43.4%** | |

### Implementation Priority

| Phase | Feature Types | Tables | Est. Duration | Rationale |
|-------|---------------|--------|---------------|-----------|
| **CURRENT** | cov_* remediation | 1,798 | ~8 hrs | In progress |
| **1** | rev_, der_ | 112 | ~4 hrs | Highest game theory value |
| **2** | ext_, cyc_ | 56 | ~3 hrs | Opportunity detection |
| **3** | div_, mrt_ | 84 | ~3 hrs | Early warning + magnitude |
| **4** | tmp_ | 28 | ~1 hr | Optimization layer |
| **TOTAL** | All additional | 280 | ~11 hrs | |

---

## 8. REFERENCE: DETAILED SPECIFICATION

For complete column definitions, SQL templates, and validation requirements, see:
- **[/mandate/ADDITIONAL_FEATURE_SPECIFICATION.md](ADDITIONAL_FEATURE_SPECIFICATION.md)**

---

*Document generated: 2025-11-29*
*Dataset: bqx-ml:bqx_ml_v3_features*
