# BA DIRECTIVE: Feature Gap Remediation Plan (v2 - CORRECTED)

**Document Type**: Implementation Directive
**Date**: December 9, 2025
**From**: Chief Engineer (CE)
**To**: Build Agent (BA)
**Priority**: HIGH
**Status**: SUPERSEDES v1 - CORRECTED FEATURE TYPES
**Supersedes**: BA_DIRECTIVE_GAP_REMEDIATION_20251209.md

---

## CORRECTION NOTICE

The original directive listed 7 feature types for CSI. User correctly identified this was incomplete. BQ audit confirms **20 distinct feature prefixes**. This corrected directive includes all 13 CSI-applicable feature types.

---

## EXECUTIVE SUMMARY (REVISED)

| Gap | Expected | Actual | Missing | Priority |
|-----|----------|--------|---------|----------|
| csi_* (Currency Strength Index) | **208** | 0 | **208** | CRITICAL |
| var_* (Variance) | 114 | 55 | 59 | HIGH |
| mkt_* (Market-wide) | 18 | 4 | 14 | MEDIUM |
| **TOTAL** | **340** | **59** | **281** | - |

---

## GAP 1: Currency Strength Index (csi_*) - CRITICAL (CORRECTED)

### Feature Types (13 total - CORRECTED from 7)

1. **agg** - Aggregation statistics
2. **mom** - Momentum indicators
3. **vol** - Volatility metrics
4. **reg** - Regression features
5. **regime** - Market regime classification
6. **lag** - Historical lag features
7. **align** - Cross-timeframe alignment
8. **der** - Derivative (velocity/acceleration)
9. **rev** - Reversal detection
10. **div** - Divergence signals
11. **mrt** - Mean reversion tension
12. **cyc** - Cycle position
13. **ext** - Extremity metrics

### Table Pattern

```
csi_{feature}_{currency}        # IDX variant
csi_{feature}_bqx_{currency}    # BQX variant
```

### Currencies (8)

USD, EUR, GBP, JPY, CHF, CAD, AUD, NZD

### Total Tables

8 currencies × 13 features × 2 variants = **208 tables**

### Implementation Approach

**OPTION A (Recommended): Derive from existing pair data**

For each currency, aggregate features from all pairs containing that currency:

```sql
-- Example: USD strength from agg features across all USD pairs
CREATE OR REPLACE TABLE `bqx-ml.bqx_ml_v3_features_v2.csi_agg_usd` AS
WITH usd_pairs AS (
  SELECT interval_time, 'eurusd' as pair, -1 as direction, * EXCEPT(interval_time)
  FROM `bqx-ml.bqx_ml_v3_features_v2.agg_eurusd`
  UNION ALL
  SELECT interval_time, 'gbpusd' as pair, -1 as direction, * EXCEPT(interval_time)
  FROM `bqx-ml.bqx_ml_v3_features_v2.agg_gbpusd`
  UNION ALL
  SELECT interval_time, 'usdjpy' as pair, 1 as direction, * EXCEPT(interval_time)
  FROM `bqx-ml.bqx_ml_v3_features_v2.agg_usdjpy`
  UNION ALL
  SELECT interval_time, 'usdchf' as pair, 1 as direction, * EXCEPT(interval_time)
  FROM `bqx-ml.bqx_ml_v3_features_v2.agg_usdchf`
  UNION ALL
  SELECT interval_time, 'audusd' as pair, -1 as direction, * EXCEPT(interval_time)
  FROM `bqx-ml.bqx_ml_v3_features_v2.agg_audusd`
  UNION ALL
  SELECT interval_time, 'nzdusd' as pair, -1 as direction, * EXCEPT(interval_time)
  FROM `bqx-ml.bqx_ml_v3_features_v2.agg_nzdusd`
  UNION ALL
  SELECT interval_time, 'usdcad' as pair, 1 as direction, * EXCEPT(interval_time)
  FROM `bqx-ml.bqx_ml_v3_features_v2.agg_usdcad`
)
SELECT
  interval_time,
  'USD' as currency,
  -- Aggregate numeric columns with directional adjustment
  AVG(direction * agg_mean_45) as csi_agg_mean_45,
  AVG(direction * agg_std_45) as csi_agg_std_45,
  -- ... additional aggregations
FROM usd_pairs
GROUP BY interval_time
ORDER BY interval_time;
```

**Key Logic**:
- When currency is QUOTE (EURUSD for USD): direction = -1 (pair up = currency weak)
- When currency is BASE (USDJPY for USD): direction = +1 (pair up = currency strong)

### Currency-Pair Mappings

| Currency | As Base | As Quote |
|----------|---------|----------|
| USD | USDJPY, USDCHF, USDCAD | EURUSD, GBPUSD, AUDUSD, NZDUSD |
| EUR | EURUSD, EURJPY, EURGBP, EURCHF, EURCAD, EURAUD, EURNZD | - |
| GBP | GBPUSD, GBPJPY, GBPCHF, GBPCAD, GBPAUD, GBPNZD | EURGBP |
| JPY | - | USDJPY, EURJPY, GBPJPY, CHFJPY, CADJPY, AUDJPY, NZDJPY |
| CHF | CHFJPY | USDCHF, EURCHF, GBPCHF, AUDCHF, NZDCHF, CADCHF |
| CAD | CADJPY, CADCHF | USDCAD, EURCAD, GBPCAD, AUDCAD, NZDCAD |
| AUD | AUDUSD, AUDJPY, AUDCHF, AUDCAD, AUDNZD | EURAUD, GBPAUD |
| NZD | NZDUSD, NZDJPY, NZDCHF, NZDCAD | EURNZD, GBPNZD, AUDNZD |

---

## RESPONSES TO BA CLARIFICATION QUESTIONS

### Q1: CSI Table Structure

**Answer**: Use Option C as you proposed - maintain consistency with existing patterns:
- `csi_{feature}_{currency}` for IDX variant
- `csi_{feature}_bqx_{currency}` for BQX variant

Examples:
- `csi_agg_usd`, `csi_agg_bqx_usd`
- `csi_mom_eur`, `csi_mom_bqx_eur`
- `csi_der_gbp`, `csi_der_bqx_gbp`

### Q2: CSI Feature Scope

**Answer**: Create summarized CSI tables with key aggregations per feature type:
- For each feature type, aggregate the most relevant columns
- Use directional weighting (base vs quote)
- Include: mean, std, min, max, trend metrics where applicable
- Do NOT replicate all columns - focus on strength indicators

### Q3: Priority Given Time Constraint

**Answer**: Given the increased scope (208 tables vs 112), proceed with phased approach:

**Priority A (Must Complete)**:
- CSI for 4 major currencies (USD, EUR, GBP, JPY) = 104 tables
- VAR completion = 59 tables
- Total: 163 tables

**Priority B (If Time Permits)**:
- CSI for 4 minor currencies (CHF, CAD, AUD, NZD) = 104 tables
- MKT completion = 14 tables
- Total: 118 tables

---

## REVISED EXECUTION PLAN

### Phase R1: Investigation (30 minutes) - UNCHANGED
1. Query existing var_* schema
2. Query existing mkt_* schema
3. Query existing csi_reg_* schema for pattern reference
4. Document findings

### Phase R2: CSI Implementation (3-4 hours) - EXPANDED
1. Create CSI generator script for all 13 feature types
2. Generate USD CSI tables (26 tables: 13 features × 2 variants)
3. Validate row counts and data quality
4. Generate EUR CSI tables (26 tables)
5. Generate GBP CSI tables (26 tables)
6. Generate JPY CSI tables (26 tables)
7. Total Phase R2: 104 tables (Priority A currencies)

### Phase R3: VAR Completion (1 hour) - UNCHANGED
1. Identify missing var_* tables
2. Generate using existing pattern
3. Total: 59 tables

### Phase R4: MKT Completion (1 hour) - UNCHANGED
1. Identify missing mkt_* tables
2. Generate market-wide aggregations
3. Total: 14 tables

### Phase R5: CSI Phase 2 (2 hours) - NEW
1. Generate CHF, CAD, AUD, NZD CSI tables
2. Total: 104 tables

### Phase R6: Catalogue Update (30 minutes)
1. Update feature_catalogue.json
2. Update semantics.json gap status
3. Verify all gaps closed

---

## REVISED TIME ESTIMATES

| Phase | Duration | Cumulative | Tables |
|-------|----------|------------|--------|
| R1 | 30 min | 0:30 | - |
| R2 | 3.5 hours | 4:00 | 104 |
| R3 | 1 hour | 5:00 | 59 |
| R4 | 1 hour | 6:00 | 14 |
| R5 | 2 hours | 8:00 | 104 |
| R6 | 30 min | 8:30 | - |

**Total Estimate**: 8.5 hours for full remediation

**4-Hour Cutoff Deliverable**:
- Phase R1 + R2 (partial) = ~100 Priority A tables
- Document remaining as Phase 2 remediation
- Proceed to model training

---

## SUCCESS CRITERIA (REVISED)

| Gap | Priority A Target | Full Target | Verification |
|-----|-------------------|-------------|--------------|
| csi_* | 104 tables (4 currencies) | 208 tables | `bq ls` count |
| var_* | 114 total | 114 total | `bq ls` count |
| mkt_* | 18 total | 18 total | `bq ls` count |

---

## IMMEDIATE NEXT ACTION

BA should:
1. Begin Phase R1 investigation immediately
2. Implement CSI generator for all 13 feature types
3. Prioritize USD → EUR → GBP → JPY order
4. Report progress every hour

---

**CE Signature**: Claude (CE, BQX ML V3)
**Date**: December 9, 2025
**Status**: DIRECTIVE v2 ISSUED - CLARIFICATIONS PROVIDED
