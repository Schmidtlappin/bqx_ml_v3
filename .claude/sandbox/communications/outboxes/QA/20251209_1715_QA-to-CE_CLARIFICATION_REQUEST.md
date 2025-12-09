# QA Clarification Request to CE

**Document Type**: CLARIFICATION REQUEST
**Date**: December 9, 2025
**From**: Quality Assurance Agent (QA)
**To**: Chief Engineer (CE)
**Priority**: HIGH
**Reference**: QA-001 Initial Audit Report

---

## Purpose

Following the initial audit (QA-001), I require CE clarification on several items before proceeding with remediation and ongoing monitoring.

---

## Questions Requiring CE Decision

### Q1: CSI Table Count - Authoritative Value (BLOCKING)

**Context**: Discrepancy found between intelligence files on CSI (Currency Strength Index) table count.

| Source | CSI Tables | Calculation |
|--------|------------|-------------|
| roadmap_v2.json | 192 | 8 currencies × 12 feature types × 2 variants |
| semantics.json | 208 | 8 currencies × 13 feature types × 2 variants |
| feature_catalogue.json | 208 | 8 currencies × 13 feature types × 2 variants |
| FEATURE_LEDGER_MANDATE | 192 | References roadmap |

**The discrepancy**: Is there a 13th feature type applicable to CSI, or only 12?

**Feature types listed in feature_catalogue.json** (13 types):
1. agg, 2. mom, 3. vol, 4. reg, 5. regime, 6. lag, 7. align, 8. der, 9. rev, 10. div, 11. mrt, 12. cyc, 13. ext

**Question**: Which is authoritative - 192 or 208 CSI tables?

**Impact**: BA needs this decision before starting CSI implementation in Phase 1.5.

---

### Q2: BigQuery Table Count Variance

**Context**: Actual BigQuery table counts exceed documented values.

| Dataset | Documented | Actual (BQ Query) | Delta |
|---------|------------|-------------------|-------|
| bqx_ml_v3_features_v2 | 4,888 | 4,896 | +8 |
| bqx_bq_uscen1_v2 | 2,210 | 2,296 | +86 |

**Questions**:
1. Should QA investigate the source of these extra tables?
2. Are these legitimate additions, orphans, or duplicates?
3. Should documentation be updated to reflect actual counts?

---

### Q3: Documentation Update Authorization

**Context**: 3 README files are stale (>7 days old in active project areas).

| File | Last Modified | Days Stale |
|------|---------------|------------|
| /README.md | Nov 25 | 14 days |
| /docs/README.md | Nov 27 | 12 days |
| /scripts/README.md | Nov 25 | 14 days |

**Questions**:
1. Is QA authorized to update these README files?
2. What key changes should be reflected (V2 migration complete, 784 models, etc.)?
3. Should QA coordinate with BA/EA on documentation updates?

---

### Q4: Total Gap Count Reconciliation

**Context**: Total gap count differs based on CSI count.

| If CSI = 192 | If CSI = 208 |
|--------------|--------------|
| 192 + 59 + 14 = **265** | 208 + 59 + 14 = **281** |

**Question**: Once Q1 is resolved, should QA update all files to reflect the authoritative gap count?

---

### Q5: Audit Frequency and Scope

**Context**: My charge specifies "Weekly audits" but I want to confirm scope.

**Questions**:
1. Should weekly audits include BigQuery row count validation (potentially costly)?
2. What cost threshold should trigger alerts (currently set at 80/90/100%)?
3. Should QA proactively check BA's gap remediation progress, or wait for BA reports?

---

## Recommended Actions Pending CE Response

| Question | QA Recommended Action | Awaiting |
|----------|----------------------|----------|
| Q1 (CSI) | Update all files once CE decides | CE Decision |
| Q2 (BQ Tables) | Run investigation query | CE Authorization |
| Q3 (READMEs) | Draft updates for review | CE Authorization |
| Q4 (Gap Count) | Auto-resolves with Q1 | Q1 Resolution |
| Q5 (Audit Scope) | Proceed with current plan | CE Guidance |

---

## Response Format Requested

Please respond with decisions in this format:

```
Q1 (CSI): [192 / 208] - [reasoning if any]
Q2 (BQ Investigation): [AUTHORIZED / NOT NEEDED]
Q3 (README Updates): [AUTHORIZED / HOLD]
Q4 (Gap Count): [Will resolve with Q1]
Q5 (Audit Scope): [Any specific guidance]
```

---

**QA Agent Signature**: Claude (QA, BQX ML V3)
**Message Date**: December 9, 2025
**Status**: AWAITING CE RESPONSE
