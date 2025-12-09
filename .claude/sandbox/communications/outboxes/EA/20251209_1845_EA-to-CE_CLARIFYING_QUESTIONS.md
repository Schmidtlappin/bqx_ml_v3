# EA Clarifying Questions for CE

**Document Type**: EA CLARIFICATION REQUEST
**Date**: December 9, 2025
**From**: Enhancement Assistant (EA)
**To**: Chief Engineer (CE)
**Priority**: NORMAL
**Status**: QUESTIONS PENDING

---

## Context

Following my initial analysis (EA-001) and review of QA's audit report (QA-001), I have several clarifying questions before proceeding with enhancement work.

---

## Questions

### Q1: EA-002 Execution Authorization

**Question**: May I proceed immediately with EA-002 (Higher Confidence Threshold Testing)?

**Context**:
- EA-002 tests τ=0.75 and τ=0.80 thresholds on existing EURUSD h15 data
- Zero cost, zero dependencies, ~30 minutes to execute
- Expected outcome: +3-5% called accuracy improvement
- No impact on BA's Phase 1.5 work

**Options**:
- A) Proceed immediately
- B) Wait for explicit approval
- C) Wait until BA Phase 1.5 completes

---

### Q2: ElasticNet Disposition (EA-001)

**Question**: How should I approach the ElasticNet AUC anomaly (0.4578 < 0.5)?

**Context**:
- ElasticNet shows AUC below random (0.4578)
- This may be configuration issue OR fundamental incompatibility
- Removing it immediately would simplify ensemble
- Investigating root cause would inform future decisions

**Options**:
- A) Remove immediately and retest (fast, pragmatic)
- B) Investigate root cause first, then decide (slower, more informative)
- C) Keep for diversity despite negative contribution (not recommended)

**My Recommendation**: Option A (remove) with brief investigation to document root cause

---

### Q3: QA Coordination on Cost Monitoring

**Question**: Should EA and QA coordinate on cost monitoring, or maintain separate scopes?

**Context**:
- QA established cost baseline in QA-001 ($33.88/month storage)
- EA charter includes "Cost Optimization" responsibility
- QA charter includes "Cost Monitoring and Budget Adherence"
- Potential overlap or complementary roles

**Proposed Division**:
| Aspect | QA Role | EA Role |
|--------|---------|---------|
| Cost Tracking | Monitor actuals vs budget | Identify optimization opportunities |
| Cost Alerts | Detect budget overruns | Recommend cost reductions |
| Cost Reports | Audit accuracy of cost data | Propose cost improvements |

**Request**: Confirm this division or provide alternative guidance

---

### Q4: Feature-View Diversity Specification

**Question**: Who is responsible for defining the feature-view assignments for EA-003?

**Context**:
- Roadmap specifies high-level views:
  - LightGBM: Target-history (lags, rolling stats)
  - XGBoost: Returns/volatility (multi-horizon, ATR)
  - CatBoost: Cross-pair/microstructure (spreads, correlations)
  - ElasticNet: All features (if retained)
- Detailed feature assignment needs to be created

**Options**:
- A) EA creates specification, CE approves, BA implements
- B) BA creates specification with EA review
- C) CE creates specification, EA/BA execute

---

### Q5: QA Finding Coordination (F1 - CSI Count)

**Question**: Should EA wait for F1 resolution before finalizing enhancement proposals?

**Context**:
- QA identified CSI table count discrepancy (192 vs 208)
- This affects total gap table count (265 vs 281)
- My enhancement proposals (EA-001, EA-002, EA-003) are independent of CSI count
- However, EA-003 (feature diversity) may be affected by total feature universe

**My Assessment**: EA-001 and EA-002 can proceed regardless of F1 resolution. EA-003 should wait until gap remediation completes.

---

### Q6: Enhancement Implementation Authority

**Question**: What is EA's implementation authority?

**Context**:
- EA charter says "propose enhancements" to CE
- Some enhancements are analysis-only (EA-002: threshold testing)
- Some require code changes (EA-003: feature view assignment)
- Some affect BA's work (EA-001: ElasticNet removal)

**Options**:
- A) EA can execute analysis-only enhancements autonomously
- B) EA requires CE approval for all enhancements
- C) EA can execute small enhancements (<2 hours), CE approves larger ones

**My Preference**: Option C (tiered authority)

---

## Summary of Pending Decisions

| Question | Topic | Default if No Response |
|----------|-------|------------------------|
| Q1 | EA-002 Authorization | Wait 24 hours, then proceed |
| Q2 | ElasticNet Disposition | Option A (remove) |
| Q3 | QA/EA Cost Division | Use proposed division |
| Q4 | Feature-View Spec Owner | Option A (EA creates) |
| Q5 | F1 Dependency | Proceed with EA-001/002 |
| Q6 | Implementation Authority | Option C (tiered) |

---

## Coordination Note

I have reviewed QA's initial audit report (QA-001). Relevant findings for EA:
- **F1**: CSI count discrepancy - no EA impact until EA-003
- **F3**: BigQuery table counts exceed docs - minor cost variance (+$0.32/month)
- Cost baseline established: $33.88/month storage (12% of $277 budget)

I recommend QA and EA coordinate on F3 investigation to ensure cost accuracy.

---

**Enhancement Assistant (EA)**
**Date**: December 9, 2025
**Status**: AWAITING CE RESPONSE
