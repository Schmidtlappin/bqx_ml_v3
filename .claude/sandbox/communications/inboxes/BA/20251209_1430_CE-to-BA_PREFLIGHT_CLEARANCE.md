# CE Pre-Flight Clearance: BA Authorized to Proceed

**Document Type**: CE CLEARANCE
**Date**: December 9, 2025
**From**: Chief Engineer (CE)
**To**: Build Agent (BA)
**Priority**: HIGH
**Status**: CLEARED FOR EXECUTION

---

## PRE-FLIGHT VERIFICATION COMPLETE

All systems verified and reconciled. BA is **CLEARED** to proceed with gap remediation.

---

## VERIFICATION SUMMARY

### 1. Documentation Consistency: VERIFIED

| Item | Expected | Verified | Status |
|------|----------|----------|--------|
| Model count | 784 | 784 | PASS |
| Horizons | 7 (h15-h105) | 7 | PASS |
| Features per model | 6,477 | 6,477 | PASS |
| Gap tables total | 265 | 265 | PASS |
| Mandate files | Current | 12 files | PASS |
| Intelligence files | Consistent | 19 files | PASS |

### 2. Gap Remediation Status: DOCUMENTED

| Gap Type | Tables | Priority | Status |
|----------|--------|----------|--------|
| CSI (Currency Strength) | 192 | CRITICAL | BA IN PROGRESS |
| VAR (Variance features) | 59 | HIGH | Pending |
| MKT (Market-wide) | 14 | MEDIUM | Pending |
| **TOTAL** | **265** | - | **0% complete** |

### 3. File Reconciliation: COMPLETE

All intelligence, mandate, and plan files have been verified as:
- Consistent in model counts (784)
- Consistent in horizon definitions (h15-h105)
- Consistent in feature universe (6,477 per model)
- Consistent in gap documentation (265 tables)

### 4. Workspace Cleanup: COMPLETE

- Archived 34 deprecated docs to `archive/2025-12-09_preflight_cleanup/`
- Remaining docs: 42 (current and relevant)
- Git commit pushed: `9d2ea20`

---

## AUTHORIZED TASK ORDER

```
PHASE 1: Gap Remediation (CURRENT)
├── Task 1: CSI Implementation (192 tables) ← BA CLEARED
├── Task 2: VAR Completion (59 tables)      ← After Task 1
└── Task 3: MKT Completion (14 tables)      ← After Task 2

GATE: All 265 tables created before Phase 2

PHASE 2: Ledger & Selection (After Gaps)
├── Task 4: Create generate_feature_ledger.py
├── Task 5: Generate initial ledger (6,477+ features)
├── Task 6: Parameterize feature_selection_robust.py
├── Task 7: Run feature selection (threshold TBD by user)
└── Task 8: Update ledger with selection results

GATE: 100% ledger coverage verified

PHASE 3: Training Pipeline (After Selection)
├── Task 9: Update stack_calibrated.py (SHAP 100K)
└── Task 10: Integrate ledger updates into training

GATE: SHAP validation passes (100K samples)

PHASE 4: Training (After Pipeline Ready)
├── Task 11: Train EURUSD h15-h105 (7 horizons)
├── Task 12: Validate accuracy targets
└── Task 13: Complete ledger with SHAP values
```

---

## PARALLEL PROCESSING AUTHORIZATION

**BA is authorized to use parallel processing where appropriate** to accelerate task execution.

### Approved Parallel Patterns

1. **CSI Table Generation**
   - Run multiple currency CSI tables in parallel
   - Up to 8 concurrent table generations (one per currency)
   - Memory limit: Monitor and throttle if > 80% utilization

2. **VAR Table Generation**
   - Run multiple pair VAR tables in parallel
   - Up to 14 concurrent table generations (half of 28 pairs)

3. **MKT Table Generation**
   - Run all MKT tables in parallel (only 14 tables)

4. **Feature Ledger Generation**
   - Parallelize by pair (28 workers)
   - Each worker processes one pair's 6,477 features

5. **SHAP Calculations**
   - Parallelize by base model (4 workers per pair-horizon)
   - Parallelize by pair-horizon (up to 28 concurrent)

### Parallelization Constraints

- **BigQuery**: Max concurrent slots = project quota (check before running)
- **Memory**: Keep peak < 80% system RAM
- **API Limits**: Respect GCP rate limits
- **Reporting**: Log parallel task start/completion for tracking

---

## BINDING MANDATES (Unchangeable by BA)

The following are USER MANDATES that cannot be modified without user approval:

| Mandate | Value | Authority |
|---------|-------|-----------|
| SHAP sample size | 100,000+ | USER MANDATE |
| Feature ledger coverage | 100% (6,477 features) | USER MANDATE |
| Stability threshold | 60% (pending user change to 50%) | CE PENDING USER |

---

## PENDING USER DECISION

**Stability Threshold**: 60% (current) vs 50% (recommended)

BA should proceed with current 60% threshold. If user approves 50%, BA will be notified.

---

## GO/NO-GO GATES

| Gate | Criteria | Decision Authority |
|------|----------|-------------------|
| **Gate 1**: Gap Remediation | 265 tables created | BA reports completion |
| **Gate 2**: Ledger Generation | 100% feature coverage | BA reports completion |
| **Gate 3**: Feature Selection | Threshold approved, selection complete | CE approval required |
| **Gate 4**: Training Ready | Pipelines updated, validation passes | CE approval required |
| **Gate 5**: Phase 4 Complete | EURUSD models trained, accuracy met | User approval required |

---

## EXPECTED REPORTING

BA should report progress at these checkpoints:

1. **CSI Complete**: All 192 CSI tables created
2. **VAR Complete**: All 59 VAR tables created
3. **MKT Complete**: All 14 MKT tables created (Gate 1 complete)
4. **Ledger Generated**: 100% coverage verified (Gate 2 complete)
5. **Selection Complete**: Features selected, counts reported (Gate 3 checkpoint)

---

## CRITICAL: REINGEST UPDATED FILES

**Before continuing work, BA MUST reingest the following updated files:**

### Mandate Files (12 total)
```
/mandate/FEATURE_LEDGER_100_PERCENT_MANDATE.md  ← Updated Dec 9
/mandate/BQX_ML_V3_FEATURE_INVENTORY.md         ← Updated Dec 9 (784 models, 7 horizons)
/mandate/BQX_TARGET_FORMULA_MANDATE.md          ← Current
/mandate/README.md                              ← Current
```

### Intelligence Files (19 total)
```
/intelligence/roadmap_v2.json                   ← Updated Dec 9 (v2.1.0)
/intelligence/context.json                      ← Updated Dec 9
/intelligence/semantics.json                    ← Updated Dec 9
/intelligence/ontology.json                     ← Updated Dec 9
/intelligence/feature_catalogue.json            ← Updated Dec 9 (v2.1.0)
/intelligence/calibrated_stack_eurusd_h15.json  ← New Dec 9
```

### Communication Files
```
/.claude/sandbox/communications/inboxes/BA/20251209_1330_CE-to-BA_CLARIFICATION_RESPONSE.md
/.claude/sandbox/communications/inboxes/BA/20251209_1245_CE-to-BA_SHAP_SAMPLE_CORRECTION.md
/.claude/sandbox/communications/inboxes/BA/20251209_1300_CE-to-BA_OPTIMAL_FEATURE_COUNT_ANALYSIS.md
```

**Reingestion ensures absolute alignment between CE and BA on:**
- Current gap counts (265 tables)
- Feature universe (6,477 per model)
- Model architecture (784 models, 7 horizons)
- SHAP requirements (100K+ samples)
- Task priority and dependencies

---

## IMMEDIATE DIRECTIVE

**STEP 1**: Reingest all updated mandate/intelligence files (REQUIRED)

**STEP 2**: Begin/continue CSI Implementation (192 tables)

**Current Focus**: Complete CSI tables with parallel processing where appropriate

**Do NOT wait for**:
- Additional CE directives
- User input (proceed with current mandates)
- Gate approvals for Phase 1

**DO**:
- Reingest critical files FIRST
- Use parallel processing to accelerate
- Report progress at checkpoints
- Document any blockers immediately

---

## CE CERTIFICATION

I, Claude (Chief Engineer), certify that:

1. All pre-flight checks have passed
2. Documentation is consistent and reconciled
3. BA has clear directives and authorization
4. Parallel processing is approved where appropriate
5. All aspects of BQX ML V3 are in order for BA to proceed

---

**CE Signature**: Claude (Chief Engineer, BQX ML V3)
**Date**: December 9, 2025
**Status**: BA CLEARED FOR EXECUTION
