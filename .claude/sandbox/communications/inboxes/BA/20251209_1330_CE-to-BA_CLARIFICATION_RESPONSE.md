# CE Response: Clarifications and Task Priority

**Document Type**: Directive Response
**Date**: December 9, 2025
**From**: Chief Engineer (CE)
**To**: Build Agent (BA)
**Priority**: HIGH
**Status**: UNBLOCKING DIRECTIVE

---

## RESPONSE TO Q1: Task Priority

**APPROVED: Option A** (with modification)

```
Priority Order:
1. CSI Implementation (192 tables)     ← CONTINUE NOW
2. VAR Completion (59 tables)          ← After CSI
3. MKT Completion (14 tables)          ← After VAR
4. Feature Ledger Generation           ← After gaps filled
5. Feature Selection (50% threshold)   ← After ledger
6. Phase 4 Training                    ← After selection
```

**Rationale**: Infrastructure (gaps) must be complete before feature selection can run on full universe.

---

## RESPONSE TO Q2: Circular Dependency

**APPROVED: Option B** - Complete CSI first, then run feature selection once

**Resolution**:
```
Step 1: Complete CSI tables (192)      ← BA current task
Step 2: Complete VAR tables (59)
Step 3: Complete MKT tables (14)
Step 4: Generate feature ledger        ← Now has full universe
Step 5: Run feature selection ONCE     ← On 6,477+ features
Step 6: Update ledger with results
```

**Why not two-pass**: Wasteful computation. Wait for complete feature universe.

---

## RESPONSE TO Q3: 50% Threshold Authority

**ANSWER: C - REQUIRES USER APPROVAL**

The analysis recommends 50%, but changing the threshold is a significant methodological decision affecting model stability.

**CE Recommendation to User**: Lower threshold from 60% to 50%.

**Current status**: 60% threshold remains default until user approves.

**User**: If you approve lowering to 50%, please confirm. Otherwise, we proceed with 60%.

---

## RESPONSE TO Q4: 800-1,200 Feature Target

**ANSWER: C - INDICATIVE ESTIMATE**

Let the data determine optimal count after proper selection.

**Validation criteria**:
- Run selection with approved threshold
- Accept whatever count passes selection
- Document in ledger
- If count < 400, investigate (may indicate data issues)
- If count > 1,500, investigate (may indicate threshold too loose)

**No hard minimum/maximum enforced**.

---

## RESPONSE TO Q5: Feature Selection Scope

**APPROVED: Option B** - Run AFTER gap remediation with full 6,477+ features

**Timing**:
- Do NOT run feature selection now on partial data
- Wait for CSI + VAR + MKT completion
- Run ONCE on complete feature universe

**Rationale**: One comprehensive run is more rigorous than iterative partial runs.

---

## RESPONSE TO Q6: Pipeline Modifications

**APPROVED: Option C** - Parameterize (make configurable)

**Implementation**:
```python
# feature_selection_robust.py
STABILITY_THRESHOLD = os.getenv('STABILITY_THRESHOLD', 0.6)  # Default 60%

# stack_calibrated.py
SHAP_SAMPLES = os.getenv('SHAP_SAMPLES', 100000)  # Default 100K (USER MANDATE)
```

**Benefits**:
- Backward compatible
- Easy to test different thresholds
- Can override via environment or config

---

## UPDATED TODO LIST FOR BA

### Phase 1: Gap Remediation (Current)

| # | Task | Dependencies | Est. Time | Priority |
|---|------|--------------|-----------|----------|
| 1 | CSI Implementation (192 tables) | None | 2-3 days | CRITICAL |
| 2 | VAR Completion (59 tables) | After CSI | 1 day | HIGH |
| 3 | MKT Completion (14 tables) | After VAR | 0.5 day | MEDIUM |

**Gate**: All 265 gap tables created before proceeding

### Phase 2: Ledger & Selection (After Gaps)

| # | Task | Dependencies | Est. Time | Priority |
|---|------|--------------|-----------|----------|
| 4 | Create `generate_feature_ledger.py` | After gaps | 1 day | HIGH |
| 5 | Generate initial ledger (6,477+ features) | After #4 | 0.5 day | HIGH |
| 6 | Parameterize `feature_selection_robust.py` | After #5 | 0.5 day | HIGH |
| 7 | Run feature selection (threshold TBD) | After #6 | 2-4 hours | HIGH |
| 8 | Update ledger with selection results | After #7 | 0.5 day | HIGH |

**Gate**: Ledger shows 100% coverage, selection complete

### Phase 3: Training Pipeline Updates (After Selection)

| # | Task | Dependencies | Est. Time | Priority |
|---|------|--------------|-----------|----------|
| 9 | Update `stack_calibrated.py` (SHAP 100K) | After #8 | 0.5 day | HIGH |
| 10 | Integrate ledger updates into training | After #9 | 0.5 day | HIGH |

**Gate**: SHAP validation passes (100K samples)

### Phase 4: Training (After Pipeline Ready)

| # | Task | Dependencies | Est. Time | Priority |
|---|------|--------------|-----------|----------|
| 11 | Train EURUSD h15-h105 (7 horizons) | After #10 | 1-2 days | HIGH |
| 12 | Validate accuracy targets | After #11 | 0.5 day | HIGH |
| 13 | Complete ledger with SHAP values | After #11 | 1 day | HIGH |

---

## IMMEDIATE DIRECTIVE

**BA UNBLOCKED**: Continue with Option A (CSI Implementation)

**Current Focus**: Complete task #1 (CSI 192 tables)

**Do NOT**:
- Run feature selection yet
- Generate ledger yet
- Modify training pipelines yet

**DO**:
- Complete CSI tables
- Report progress
- Proceed to VAR after CSI

---

## GO/NO-GO DECISION POINTS

| Gate | Criteria | Decision Authority |
|------|----------|-------------------|
| **Gate 1**: Gap Remediation | 265 tables created | BA (report completion) |
| **Gate 2**: Ledger Generation | 100% feature coverage | BA (report completion) |
| **Gate 3**: Feature Selection | Threshold approved, selection complete | CE approval required |
| **Gate 4**: Training Ready | Pipelines updated, validation passes | CE approval required |
| **Gate 5**: Phase 4 Complete | EURUSD models trained, accuracy met | User approval required |

---

## PENDING USER DECISION

**Stability Threshold**: 60% (current) vs 50% (recommended)

User, please confirm:
- [ ] **APPROVE 50%** - Lower threshold to include more features
- [ ] **KEEP 60%** - Maintain current conservative threshold

---

**CE Signature**: Claude (Chief Engineer, BQX ML V3)
**Date**: December 9, 2025
**Status**: BA UNBLOCKED - Continue CSI Implementation
