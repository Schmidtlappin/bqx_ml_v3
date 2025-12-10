# QA Report: F3b Source Cleanup Analysis

**Document Type**: P3.1 CLEANUP REPORT
**Date**: December 9, 2025 23:50
**From**: Quality Assurance Agent (QA)
**To**: Chief Engineer (CE)
**Status**: AWAITING CE APPROVAL

---

## Executive Summary

Found **101 misplaced feature tables** in `bqx_bq_uscen1_v2` (source dataset).
- **56 DUPLICATES**: Safe to delete (copies exist in features_v2)
- **45 ORPHANS**: Need CE decision (no copy in features_v2)
- **Storage**: 96.95 GB
- **Monthly savings**: ~$1.94

---

## Findings

### Dataset Analysis

| Dataset | Purpose | Misplaced Tables |
|---------|---------|------------------|
| bqx_bq_uscen1_v2 | Source data (raw OHLCV) | 101 feature tables |
| bqx_ml_v3_features_v2 | Feature tables | (correct location) |

### Misplaced Table Breakdown

| Category | Count | Status | Recommendation |
|----------|-------|--------|----------------|
| reg_* (pair) | 56 | DUPLICATE | DELETE |
| reg_bqx | 1 | ORPHAN | REVIEW |
| reg_corr_* | 8 | ORPHAN | REVIEW |
| regime_* | 36 | ORPHAN | REVIEW |
| **TOTAL** | **101** | - | - |

---

## DUPLICATE Tables (Safe to Delete)

These 56 tables exist in both `bqx_bq_uscen1_v2` AND `bqx_ml_v3_features_v2`:

```
reg_audcad, reg_audchf, reg_audjpy, reg_audnzd, reg_audusd,
reg_bqx_audcad, reg_bqx_audchf, reg_bqx_audjpy, reg_bqx_audnzd,
reg_bqx_audusd, reg_bqx_cadchf, reg_bqx_cadjpy, reg_bqx_chfjpy,
reg_bqx_euraud, reg_bqx_eurcad, reg_bqx_eurchf, reg_bqx_eurgbp,
reg_bqx_eurjpy, reg_bqx_eurnzd, reg_bqx_eurusd, reg_bqx_gbpaud,
reg_bqx_gbpcad, reg_bqx_gbpchf, reg_bqx_gbpjpy, reg_bqx_gbpnzd,
reg_bqx_gbpusd, reg_bqx_nzdcad, reg_bqx_nzdchf, reg_bqx_nzdjpy,
reg_bqx_nzdusd, reg_bqx_usdcad, reg_bqx_usdchf, reg_bqx_usdjpy,
reg_cadchf, reg_cadjpy, reg_chfjpy, reg_euraud, reg_eurcad,
reg_eurchf, reg_eurgbp, reg_eurjpy, reg_eurnzd, reg_eurusd,
reg_gbpaud, reg_gbpcad, reg_gbpchf, reg_gbpjpy, reg_gbpnzd,
reg_gbpusd, reg_nzdcad, reg_nzdchf, reg_nzdjpy, reg_nzdusd,
reg_usdcad, reg_usdchf, reg_usdjpy
```

**Recommendation**: APPROVE DELETE (verified duplicates)

---

## ORPHAN Tables (Need Decision)

These 45 tables exist ONLY in `bqx_bq_uscen1_v2`:

### reg_bqx (1 table)
- Combined BQX regression table
- **Question**: Is this needed or superseded by individual pair tables?

### reg_corr_* (8 tables)
```
reg_corr_ewa, reg_corr_ewg, reg_corr_ewj, reg_corr_ewu,
reg_corr_gld, reg_corr_spy, reg_corr_uup, reg_corr_vix
```
- Correlation tables for ETFs/indices
- **Question**: Migrate to features_v2 or delete?

### regime_* (36 tables)
```
regime_audcad, regime_audchf, regime_audjpy, ... (28 pairs)
regime_corr_ewa, regime_corr_ewg, ... (8 ETF correlations)
```
- Regime classification tables
- **Question**: Are these needed for regime-aware meta-learner?

---

## CE Decision Required

### Option A: Conservative Cleanup
- Delete 56 DUPLICATE tables only
- Keep 45 ORPHAN tables for review
- Savings: ~$1.00/month

### Option B: Full Cleanup
- Delete all 101 tables
- Orphans assumed superseded or unused
- Savings: ~$1.94/month

### Option C: Migrate + Cleanup
- Delete 56 DUPLICATE tables
- Migrate 45 ORPHAN tables to features_v2
- Savings: $0 (just reorganization)

---

## Cleanup Script

**Location**: `/scripts/cleanup_source_v2_misplaced.sh`

**Usage** (after approval):
```bash
chmod +x scripts/cleanup_source_v2_misplaced.sh
./scripts/cleanup_source_v2_misplaced.sh
```

Script currently deletes DUPLICATES only. ORPHAN deletion requires uncommenting.

---

## Risk Assessment

| Risk | Mitigation |
|------|------------|
| Data loss | DUPLICATES verified in features_v2 |
| Training impact | ORPHANS need CE review |
| Recovery | BQ trash retention (7 days) |

---

## QA Recommendation

**APPROVE Option A** (Conservative) as immediate action:
1. Delete 56 verified DUPLICATE tables
2. Mark ORPHAN tables for Phase 2.5 review
3. Document decision in semantics.json

---

## Verification Query

After cleanup, verify:
```sql
SELECT COUNT(*) as remaining_feature_tables
FROM `bqx-ml.bqx_bq_uscen1_v2.INFORMATION_SCHEMA.TABLES`
WHERE table_name LIKE 'reg_%' OR table_name LIKE 'regime_%'
-- Expected: 45 (if Option A) or 0 (if Option B)
```

---

**QA Agent Signature**: Claude (QA, BQX ML V3)
**Report Time**: December 9, 2025 23:50
**Status**: AWAITING CE APPROVAL FOR F3B CLEANUP
