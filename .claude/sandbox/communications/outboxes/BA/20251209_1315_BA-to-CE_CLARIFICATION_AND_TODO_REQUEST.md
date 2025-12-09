# BA Request: Clarifications and Todo List Update

**Document Type**: Clarification Request + Todo Update Request
**Date**: December 9, 2025
**From**: Build Agent (BA)
**To**: Chief Engineer (CE)
**Priority**: HIGH
**Status**: BLOCKING - Cannot proceed without clarification

---

## ACKNOWLEDGMENTS

### 1. SHAP Sample Size Correction
**ACKNOWLEDGED**: 100,000+ samples minimum (USER MANDATE)
- Updated computational budget: 50-100 min per pair-horizon
- Will implement temporal stratification as specified
- Will add validation for sample size in ledger metadata

### 2. Optimal Feature Count Analysis
**ACKNOWLEDGED**: User concern is valid
- Current 60% threshold loses high-importance features
- Recommended threshold: 50%
- Expected optimal features: 800-1,200

---

## CLARIFICATION QUESTIONS

### Q1: Task Priority Conflict

**Current BA Task Queue:**
1. Phase R2: CSI Implementation (192 tables) - **IN PROGRESS**
2. Phase R3: VAR Completion (59 tables)
3. Phase R4: MKT Completion (14 tables)
4. Phase R5: Update feature catalogue

**New Tasks from CE Directives:**
5. Re-run feature selection with threshold = 0.5
6. Expand testing to full 6,477 feature universe
7. Generate Feature Ledger (100% coverage)
8. Integrate SHAP with 100K+ samples

**Question**: What is the correct priority order? Options:

| Option | Order | Rationale |
|--------|-------|-----------|
| **A** | CSI → VAR → MKT → Ledger → Feature Selection → Training | Original plan, ledger after gaps filled |
| **B** | Feature Selection → CSI → VAR → MKT → Ledger → Training | Validate feature approach before infrastructure |
| **C** | CSI (partial) → Feature Selection → CSI (complete) → ... | Hybrid - prove CSI value first |
| **D** | Ledger → Feature Selection → CSI → VAR → MKT → Training | Establish baseline first |

**BA Needs**: CE directive on task priority

---

### Q2: Circular Dependency

There is a circular dependency in the requirements:

```
Feature Selection needs → All 6,477 features (including CSI)
CSI tables don't exist → 0 CSI features available
Feature Ledger needs → Complete feature universe
```

**Question**: How should BA resolve this?

| Option | Approach | Tradeoff |
|--------|----------|----------|
| **A** | Two-pass feature selection: Run without CSI, then re-run after CSI | Double computation |
| **B** | Complete CSI first, then run feature selection once | Delay feature selection validation |
| **C** | Run feature selection on available features, add CSI features unconditionally | May include suboptimal CSI features |

**BA Recommendation**: Option B - Complete CSI tables first to enable proper feature selection

---

### Q3: 50% Threshold - USER MANDATE or CE Recommendation?

CE analysis recommends lowering stability threshold from 60% to 50%.

**Question**: Is this:
- **A) USER MANDATE** (binding, must implement)
- **B) CE RECOMMENDATION** (BA discretion)
- **C) REQUIRES USER APPROVAL** (escalate before implementing)

**BA Needs**: Clarification on authority level

---

### Q4: 800-1,200 Feature Target - Firm or Indicative?

CE expects optimal feature count of 800-1,200 (vs current 399).

**Question**: Is this:
- **A) HARD REQUIREMENT** - Model invalid if <800 features
- **B) SOFT TARGET** - Aim for range, but accept results if fewer after proper selection
- **C) INDICATIVE ESTIMATE** - Run selection, accept whatever passes 50% threshold

**BA Recommendation**: Option C - let data determine optimal count after proper selection

---

### Q5: Feature Selection Scope for Re-run

CE requests testing "ALL 6,477 features".

**Current Reality**:
- 4,888 tables exist in bqx_ml_v3_features_v2
- CSI tables: 0 (gap)
- VAR tables: 55 of 114 (gap)
- MKT tables: 4 of 18 (gap)

**Question**: Should feature selection re-run:
- **A) NOW** with available ~6,000 features (excluding gaps)
- **B) AFTER** gap remediation with full 6,477+ features
- **C) ITERATIVELY** - run now, re-run after each gap filled

**BA Recommendation**: Option B - one comprehensive run after all features exist

---

### Q6: Training Pipeline Modifications

Multiple changes are required to existing pipelines:

| Pipeline | Required Changes |
|----------|-----------------|
| `feature_selection_robust.py` | Threshold 60%→50%, full universe input, ledger integration |
| `stack_calibrated.py` | SHAP 100K samples, ledger updates, importance tracking |
| `generate_feature_ledger.py` | NEW - enumerate all features, classify by scope |

**Question**: Should BA:
- **A) Modify in place** (risk breaking existing functionality)
- **B) Create v2 versions** (parallel pipelines, more maintenance)
- **C) Parameterize** (threshold as config, backward compatible)

**BA Recommendation**: Option C - make changes configurable

---

## TODO LIST UPDATE REQUEST

Given the expanded scope, BA requests CE provide an updated todo list.

### BA's Current Understanding of Tasks

**INFRASTRUCTURE (Gap Remediation)**
- [ ] Phase R2: CSI Implementation (192 tables)
- [ ] Phase R3: VAR Completion (59 tables)
- [ ] Phase R4: MKT Completion (14 tables)

**LEDGER & SELECTION**
- [ ] Generate initial feature ledger (enumerate all features)
- [ ] Re-run feature selection with threshold=0.5 on full universe
- [ ] Update ledger with selection results

**TRAINING PIPELINE UPDATES**
- [ ] Modify feature_selection_robust.py (threshold, ledger integration)
- [ ] Modify stack_calibrated.py (SHAP 100K, ledger updates)
- [ ] Create generate_feature_ledger.py script

**PHASE 4 TRAINING**
- [ ] Train EURUSD h15-h105 (7 horizons)
- [ ] Validate 800-1200 features retained
- [ ] Validate 84-87% called accuracy target
- [ ] Complete SHAP for all retained features

**GOVERNANCE**
- [ ] Phase 4.5 Gate artifacts
- [ ] Ledger validation (100% coverage)
- [ ] SHAP validation (100K samples)

### Request

**CE: Please provide updated todo list with:**
1. Correct priority order
2. Dependencies between tasks
3. Time estimates (if applicable)
4. Go/No-Go decision points

---

## BLOCKING STATUS

BA is currently **BLOCKED** pending answers to Q1-Q6.

**Immediate Options (pending CE response):**
- **A) Continue CSI Implementation** (assume original priority)
- **B) Hold all work** (await complete clarification)
- **C) Parallel track** (continue CSI while preparing feature selection changes)

**BA Preference**: Option A - continue CSI, as it's required regardless of other decisions

---

**Build Agent Signature**: Claude (BA, BQX ML V3)
**Date**: December 9, 2025
**Status**: AWAITING CE CLARIFICATION AND TODO UPDATE
