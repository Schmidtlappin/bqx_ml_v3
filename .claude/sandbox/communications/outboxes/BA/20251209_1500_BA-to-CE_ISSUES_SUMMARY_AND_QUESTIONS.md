# BA Report: Issues Summary and Clarifying Questions

**Document Type**: Issues Summary + Clarification Request
**Date**: December 9, 2025
**From**: Build Agent (BA)
**To**: Chief Engineer (CE)
**Priority**: HIGH
**Status**: PRE-EXECUTION AUDIT

---

## ISSUES INVENTORY COMPLETE

BA has completed a comprehensive audit of all known issues, errors, and gaps. Summary below.

---

## CATEGORY SUMMARY

| Category | Count | Priority | Status |
|----------|-------|----------|--------|
| Feature Table Gaps | 281 tables | CRITICAL | BA Task (Phase 1) |
| Feature Selection Gaps | 3 issues | HIGH | Pending Phase 2 |
| Model Training Gaps | 3 items | PENDING | Blocked by Phase 1 |
| Infrastructure Issues | 4 items | RESOLVED | Complete |
| Governance Artifacts | 5 artifacts | PENDING | Phase 4.5 |
| Configuration Decisions | 3 items | PENDING | 1 requires USER |

---

## CLARIFYING QUESTIONS

### Q1: CSI Table Schema Verification

Before implementing 192 CSI tables, should BA first verify the source table schemas for each of the 12 feature types?

**Concern**: Different feature types have different column structures. A schema audit would ensure correct aggregation.

**Options**:
- A) Proceed with implementation, fix schema issues as encountered
- B) Run schema audit first (30-60 minutes), then implement
- C) Create one CSI table per feature type as proof of concept, validate, then scale

**BA Recommendation**: Option C - proof of concept first for each feature type

### Q2: Parallel Processing Limits

CE authorized up to 8 concurrent CSI table generations. Should BA:
- A) Start with 8 parallel immediately
- B) Start with 2-4 parallel, scale up if stable
- C) Sequential for first currency (USD), then parallel for rest

**BA Recommendation**: Option C - sequential for USD proof of concept, then parallel

### Q3: Error Handling Strategy

If a CSI table creation fails:
- A) Stop all parallel jobs, investigate, then resume
- B) Log error, continue with others, report failures at end
- C) Retry failed table 3 times, then log and continue

**BA Recommendation**: Option C - retry with logging

### Q4: VAR/MKT Gap Investigation

VAR has 55 existing tables out of 114 expected. MKT has 4 out of 18.

**Question**: Should BA investigate what tables exist vs what's missing BEFORE starting CSI, or proceed with CSI first?

**Options**:
- A) CSI first (as directed), VAR/MKT investigation later
- B) Quick VAR/MKT audit now (15 minutes), then CSI
- C) Parallel: Start CSI, investigate VAR/MKT in background

**BA Recommendation**: Option A - follow authorized task order

### Q5: Regime Feature Type for CSI

CE approved excluding "regime" from CSI (12 types, not 13). Confirm this is still the directive?

- Original: 13 feature types × 8 currencies × 2 variants = 208 tables
- After regime exclusion: 12 feature types × 8 currencies × 2 variants = 192 tables

**Confirm**: 192 tables is correct target?

### Q6: Progress Reporting Frequency

CE requested progress reports at checkpoints. During CSI implementation, should BA:
- A) Report after each currency complete (8 reports)
- B) Report after each feature type complete (12 reports)
- C) Report at 25%, 50%, 75%, 100% milestones
- D) Report only at 100% completion

**BA Recommendation**: Option C - milestone-based reporting

---

## BLOCKED ITEMS (None Currently)

All issues are either:
- Resolved (infrastructure)
- Pending future phases (governance artifacts)
- Under BA's current task scope (gap remediation)

**BA is NOT BLOCKED**. Questions above are for optimization, not blocking.

---

## AWAITING CE RESPONSE

If CE prefers BA to proceed with defaults, BA will use:
- Q1: Option C (proof of concept first)
- Q2: Option C (sequential for USD, then parallel)
- Q3: Option C (retry with logging)
- Q4: Option A (CSI first)
- Q5: Confirm 192 tables
- Q6: Option C (milestone reports)

---

**Build Agent Signature**: Claude (BA, BQX ML V3)
**Date**: December 9, 2025
**Status**: READY TO EXECUTE - Questions are non-blocking
