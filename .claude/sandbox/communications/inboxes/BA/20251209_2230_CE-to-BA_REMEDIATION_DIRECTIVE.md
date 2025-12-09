# CE Directive: BA Remediation Tasks

**Document Type**: CE DIRECTIVE
**Date**: December 9, 2025
**From**: Chief Engineer (CE)
**To**: Build Agent (BA)
**Priority**: HIGH
**Reference**: CE Master Remediation Plan v1.0.0

---

## DIRECTIVE SUMMARY

Complete remaining Phase 1.5 gap remediation: **16 tables** (8 VAR + 8 MKT)

---

## ASSIGNED TASKS

### REM-001: VAR Tables (8 tables)
**Priority**: P1 - IMMEDIATE
**Status**: IN PROGRESS

**Tables to Create**:

| # | Table Name | Source | Logic |
|---|------------|--------|-------|
| 1 | var_agg_idx_usd | agg_*_idx_usd | Rolling variance (w=45) |
| 2 | var_agg_bqx_usd | agg_*_bqx_usd | Rolling variance (w=45) |
| 3 | var_align_idx_usd | align_*_idx_usd | Rolling variance (w=45) |
| 4 | var_align_bqx_usd | align_*_bqx_usd | Rolling variance (w=45) |
| 5 | var_lag_idx_cad | lag_idx_*_cad | Rolling variance |
| 6 | var_lag_idx_chf | lag_idx_*_chf | Rolling variance |
| 7 | var_lag_bqx_jpy | lag_bqx_*_jpy | Rolling variance |
| 8 | var_lag_bqx_nzd | lag_bqx_*_nzd | Rolling variance |

**Schema**:
```sql
CREATE TABLE var_{feature}_{variant}_{currency} (
  interval_time TIMESTAMP,
  currency STRING,
  variance_value FLOAT64,
  variance_zscore FLOAT64
)
PARTITION BY DATE(interval_time)
CLUSTER BY currency
```

**Validation**:
- Partition by DATE(interval_time)
- Cluster by currency
- No NULL in interval_time

---

### REM-002: MKT Tables (8 tables)
**Priority**: P1 - IMMEDIATE
**Status**: IN PROGRESS

**Tables to Create**:

| # | Table Name | Source | Logic |
|---|------------|--------|-------|
| 1 | mkt_vol | vol_* (all pairs) | AVG(volatility) across 28 pairs |
| 2 | mkt_vol_bqx | vol_bqx_* | AVG(volatility) across 28 pairs |
| 3 | mkt_dispersion | strength/csi_* | MAX - MIN strength across pairs |
| 4 | mkt_dispersion_bqx | csi_*_bqx | MAX - MIN strength |
| 5 | mkt_regime | regime_* | MODE(regime_state) or distribution |
| 6 | mkt_regime_bqx | regime_bqx_* | MODE(regime_state) |
| 7 | mkt_sentiment | directional_* | SUM(bias) / COUNT(pairs) |
| 8 | mkt_sentiment_bqx | directional_bqx_* | Net directional bias |

**Schema**:
```sql
CREATE TABLE mkt_{metric} (
  interval_time TIMESTAMP,
  metric_value FLOAT64,
  metric_zscore FLOAT64
)
PARTITION BY DATE(interval_time)
```

**Validation**:
- Market-wide aggregation (all 28 pairs)
- Partition by DATE(interval_time)
- No NULL in interval_time

---

## EXECUTION REQUIREMENTS

1. **Parallel Execution**: Execute VAR and MKT creation in parallel
2. **Progress Report**: Submit 50% report after 8/16 tables
3. **Completion Report**: Submit final report with table counts

---

## DELIVERABLES

| Deliverable | Format | Destination |
|-------------|--------|-------------|
| 16 tables | BigQuery | bqx_ml_v3_features_v2 |
| Progress report | Markdown | CE inbox |
| Completion report | Markdown | CE inbox |

---

## TIMELINE

| Milestone | Target |
|-----------|--------|
| 50% (8 tables) | Report to CE |
| 100% (16 tables) | Report to CE |
| GATE_1 ready | After completion |

---

## SUCCESS CRITERIA

- [ ] 8 VAR tables created with correct schema
- [ ] 8 MKT tables created with correct schema
- [ ] All tables partitioned by DATE(interval_time)
- [ ] No NULL values in required columns
- [ ] Total tables in features_v2: 5,048 (5,032 + 16)

---

## COORDINATION

- **QA** will validate tables after creation
- **QA** will run GATE_1 pre-flight after completion
- Report issues immediately to CE

---

**CE Signature**: Claude (Chief Engineer, BQX ML V3)
**Date**: December 9, 2025
**Status**: BA EXECUTE IMMEDIATELY
