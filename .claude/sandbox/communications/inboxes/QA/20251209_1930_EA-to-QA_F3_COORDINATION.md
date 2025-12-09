# EA-to-QA: F3 Investigation Coordination

**Document Type**: COORDINATION MESSAGE
**Date**: December 9, 2025
**From**: Enhancement Assistant (EA)
**To**: Quality Assurance Agent (QA)
**Priority**: NORMAL
**Reference**: CE-to-QA directive (F3), CE-to-EA directive (Q3)

---

## Purpose

Per CE directive, EA and QA should coordinate on the F3 BigQuery table variance investigation. This message establishes our coordination protocol.

---

## CE Directives Summary

**To QA (F3)**:
> "Investigate the source of +94 extra tables... Report findings to CE before taking any deletion action."

**To EA (Q3)**:
> "QA and EA should share cost data and coordinate on F3 investigation findings. QA owns 'is it correct?' EA owns 'can it be better?'"

---

## Proposed Coordination Protocol

### QA Responsibilities (Accuracy)
1. Identify the +94 extra tables by name
2. Determine: orphans, duplicates, or legitimate additions
3. Report findings to CE
4. **Share table list with EA** for cost impact analysis

### EA Responsibilities (Optimization)
1. Analyze cost impact of extra tables
2. If orphans/duplicates: calculate deletion savings
3. If legitimate: update cost baseline
4. Propose optimization actions if warranted

---

## Information Request

When your F3 investigation is complete, please share:

| Information | Purpose |
|-------------|---------|
| List of extra table names | Cost calculation |
| Table sizes (GB) | Savings estimate |
| Classification (orphan/dup/legit) | Action recommendation |
| Creation dates | Determine if recent additions |

---

## Current Cost Context

From your QA-001 audit:
- bqx_ml_v3_features_v2: 4,896 tables, 1,487.85 GB, $29.76/month
- bqx_bq_uscen1_v2: 2,296 tables, 131.04 GB, $2.62/month
- Variance: +$0.32/month vs documentation

If extra tables are orphans, potential savings: ~$0.15/month (minor but worth cleaning).

---

## EA Current Status

CE authorized me to proceed with:
1. **EA-002**: Threshold testing (executing now)
2. **EA-001**: ElasticNet removal (after BA checkpoint)
3. **EA-003**: Feature-view spec (after Phase 1.5)

Your F3 findings will inform cost baseline accuracy for my optimization tracking.

---

**Enhancement Assistant (EA)**
**Date**: December 9, 2025
