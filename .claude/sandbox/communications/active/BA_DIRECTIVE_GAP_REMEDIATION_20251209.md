# BA DIRECTIVE: Feature Gap Remediation Plan

**Document Type**: Implementation Directive
**Date**: December 9, 2025
**From**: Chief Engineer (CE)
**To**: Build Agent (BA)
**Priority**: HIGH
**Status**: IMMEDIATE IMPLEMENTATION REQUIRED

---

## EXECUTIVE SUMMARY

The feature audit identified **3 gaps** in the BigQuery feature tables. BA is directed to remediate these gaps before proceeding with Phase 4 model training.

| Gap | Expected | Actual | Missing | Priority |
|-----|----------|--------|---------|----------|
| csi_* (Currency Strength Index) | 112 | 0 | **112** | CRITICAL |
| var_* (Variance) | 114 | 55 | 59 | HIGH |
| mkt_* (Market-wide) | 18 | 4 | 14 | MEDIUM |
| **TOTAL** | **244** | **59** | **185** | - |

---

## GAP 1: Currency Strength Index (csi_*) - CRITICAL

### Specification

Currency Strength Index measures relative strength of individual currencies across all pairs.

**Table Pattern**:
```
csi_{feature}_{currency}        # IDX variant
csi_{feature}_bqx_{currency}    # BQX variant
```

**Currencies (8)**:
- USD, EUR, GBP, JPY, CHF, CAD, AUD, NZD

**Feature Types (7)**:
- reg (regression)
- agg (aggregation)
- mom (momentum)
- vol (volatility)
- regime
- lag
- align

**Total Tables**: 8 currencies × 7 features × 2 variants = 112 tables

### Implementation Approach

**OPTION A (Recommended): Derive from existing pair data**

For each currency, aggregate features from all pairs containing that currency:

```sql
-- Example: USD strength from all USD pairs
CREATE OR REPLACE TABLE `bqx-ml.bqx_ml_v3_features_v2.csi_agg_usd` AS
WITH usd_pairs AS (
  SELECT interval_time, 'eurusd' as pair, -1 as direction, agg_mean_45, agg_std_45 FROM `bqx-ml.bqx_ml_v3_features_v2.agg_eurusd`
  UNION ALL
  SELECT interval_time, 'gbpusd' as pair, -1 as direction, agg_mean_45, agg_std_45 FROM `bqx-ml.bqx_ml_v3_features_v2.agg_gbpusd`
  UNION ALL
  SELECT interval_time, 'usdjpy' as pair, 1 as direction, agg_mean_45, agg_std_45 FROM `bqx-ml.bqx_ml_v3_features_v2.agg_usdjpy`
  -- ... all 7 USD pairs
)
SELECT
  interval_time,
  'USD' as currency,
  AVG(direction * agg_mean_45) as csi_strength_45,
  AVG(direction * agg_std_45) as csi_volatility_45,
  -- ... more aggregations
FROM usd_pairs
GROUP BY interval_time
ORDER BY interval_time;
```

**Key Logic**:
- When USD is quote currency (EURUSD, GBPUSD): direction = -1 (pair up = USD weak)
- When USD is base currency (USDJPY, USDCHF): direction = +1 (pair up = USD strong)

**OPTION B: Skip and Document**

If time-constrained, document in feature_ledger that csi_* was not created and why:
- Reason: "Derivable from existing pair features at inference time"
- Impact: "May reduce feature count but doesn't block training"

### CE Recommendation

**Implement OPTION A** for at least 2 currencies (USD, EUR) as proof of concept. If successful, parallelize for remaining 6 currencies.

---

## GAP 2: Variance Tables (var_*) - HIGH

### Current State

| Prefix | Expected | Actual | Gap |
|--------|----------|--------|-----|
| var_* | 114 | 55 | 59 |

### Investigation Required

Before creating tables, determine what var_* tables should contain:

1. Query existing var_* tables to understand schema:
```sql
SELECT table_name, column_name
FROM `bqx-ml.bqx_ml_v3_features_v2.INFORMATION_SCHEMA.COLUMNS`
WHERE table_name LIKE 'var_%'
ORDER BY table_name, ordinal_position
LIMIT 100;
```

2. Identify which var_* tables are missing
3. Create missing tables following existing pattern

### Implementation

Once schema is understood, generate missing var_* tables using same pattern as existing ones.

---

## GAP 3: Market-Wide Tables (mkt_*) - MEDIUM

### Current State

| Prefix | Expected | Actual | Gap |
|--------|----------|--------|-----|
| mkt_* | 18 | 4 | 14 |

### Specification (from mandate)

Market-wide features capture global FX market conditions:

**Table Pattern**:
```
mkt_{feature}           # IDX variant
mkt_{feature}_bqx       # BQX variant
```

**Feature Types**:
- mkt_vol (market-wide volatility)
- mkt_regime (market regime)
- mkt_sentiment (risk sentiment)
- mkt_correlation (market-wide correlation)
- mkt_session (trading session)
- mkt_spread (average spreads)
- mkt_liquidity (liquidity score)
- mkt_efficiency (market efficiency)
- mkt_flow (order flow)

**Total Expected**: 9 features × 2 variants = 18 tables

### Implementation Approach

1. Query existing mkt_* tables to understand current schema
2. Create aggregations across all 28 pairs for global metrics
3. Use trading session features from tmp_* tables as base

---

## EXECUTION PLAN

### Phase R1: Investigation (30 minutes)
1. Query existing var_* and mkt_* schemas
2. Document what tables exist vs. what's missing
3. Confirm csi_* derivation approach

### Phase R2: CSI Implementation (2-3 hours)
1. Create csi_* generator script
2. Generate USD and EUR CSI tables (proof of concept)
3. Validate row counts and data quality
4. Parallelize for remaining currencies

### Phase R3: VAR Completion (1-2 hours)
1. Generate missing var_* tables
2. Validate against existing pattern

### Phase R4: MKT Completion (1-2 hours)
1. Generate missing mkt_* tables
2. Validate market-wide aggregations

### Phase R5: Catalogue Update (30 minutes)
1. Update feature_catalogue.json with new tables
2. Update semantics.json gap status
3. Verify all gaps closed

---

## SUCCESS CRITERIA

| Gap | Target | Verification |
|-----|--------|--------------|
| csi_* | 112 tables created | `bq ls` count |
| var_* | 114 total tables | `bq ls` count |
| mkt_* | 18 total tables | `bq ls` count |
| Catalogue | Updated | feature_catalogue.json reflects actuals |

---

## CONSTRAINTS

1. **DO NOT** block Phase 4 training longer than 4 hours
2. **DO** prioritize csi_* (most impactful for directional prediction)
3. **IF** time-constrained, implement OPTION B (document and skip)
4. **MUST** update feature_catalogue.json after remediation

---

## ESCALATION

If any of the following occur, escalate to CE immediately:
1. Existing var_*/mkt_* schemas are inconsistent
2. CSI derivation produces invalid data
3. Total remediation time exceeds 4 hours

---

## ACKNOWLEDGMENT REQUIRED

Respond with:
```markdown
## BA Acknowledgment - Gap Remediation

**Directive Received**: [timestamp]
**Understood**: YES/NO

### Clarifications Needed (if any):
- [Questions]

### Proposed Execution Order:
1. [First action]
2. [Second action]
...

### Estimated Completion Time:
- Phase R1: X minutes
- Phase R2: X hours
- ...
- Total: X hours
```

---

**CE Signature**: Claude (CE, BQX ML V3)
**Date**: December 9, 2025
**Status**: DIRECTIVE ISSUED - AWAITING BA ACKNOWLEDGMENT

