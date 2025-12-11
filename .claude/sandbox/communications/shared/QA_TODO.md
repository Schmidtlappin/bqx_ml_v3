# QA Task List

**Last Updated**: December 11, 2025 06:20
**Maintained By**: CE (refresh)
**Current Status**: **MONITORING** - Step 6 EXECUTING

---

## ✅ COMPLETE - ONBOARDING (CE Directive 06:20)

Onboarding completed at 06:25. Report: `20251211_0625_QA-to-CE_ONBOARDING_COMPLETE.md`

---

## P0: CRITICAL - STEP 6 VALIDATION (CE Directive 06:50)

**CE DIRECTIVE**: `inboxes/QA/20251211_0650_CE-to-QA_STEP6_VALIDATION_DIRECTIVE.md`

**GATE**: No pair proceeds to Step 7 without QA validation approval.

### Trigger
When EURUSD reaches 669/669 tables and merged parquet is created.

### Current Progress
| Pair | Tables | Status |
|------|--------|--------|
| EURUSD | 620/669 (93%) | EXTRACTING |

### Validation Checklist (Per Pair)
| Check | Expected | Status |
|-------|----------|--------|
| File integrity | Readable | [ ] |
| Row count | ~100K | [ ] |
| Column count | ~11,337 | [ ] |
| Feature categories | 5/5 (100%) | [ ] |
| NULL in key cols | 0% | [ ] |
| NULL in features | <1% | [ ] |
| Duplicates | 0 | [ ] |

### Deliverable
`inboxes/CE/[timestamp]_QA-to-CE_STEP6_EURUSD_AUDIT.md`

---

## 🟢 STEP 6 RESTART AUTHORIZED (04:25)

| Status | Result |
|--------|--------|
| Step 6 | **AUTHORIZED - EXECUTING** |
| Gap Remediation | ✅ **COMPLETE** |
| var_* (Variance) | 63 tables ✅ |
| csi_* (Currency Strength) | 144 tables ✅ |
| Total Tables per Pair | **669 (100%)** |

**Major Discovery**: CSI tables were FULLY IMPLEMENTED (catalogue was wrong, now corrected)

---

## CURRENT SPRINT

### ✅ COMPLETE - Update Intelligence Files (CE Directive 04:10)

| Task | Status | Report |
|------|--------|--------|
| **Update Intelligence Files** | ✅ **COMPLETE** | `20251211_0420_QA-to-CE_INTELLIGENCE_UPDATE_COMPLETE.md` |

**Files Updated (04:20)**:
1. ✅ `context.json` - Added feature_extraction section
2. ✅ `ontology.json` - Added extraction_categories, updated CSI status
3. ✅ `roadmap_v2.json` - Updated Step 6 status
4. ✅ `semantics.json` - Updated feature counts
5. ✅ `feature_catalogue.json` - (CE updated 03:40)

---

### P1: NEW - Claude Session File Inventory & Archive (CE Directive 05:30)

**CE DIRECTIVE**: `inboxes/QA/20251211_0530_CE-to-QA_SESSION_FILE_INVENTORY.md`

| Task | Status | Notes |
|------|--------|-------|
| Inventory all session files | PENDING | 249 files, 187 MB |
| Identify active vs deprecated | PENDING | Keep Dec 10-11, archive older |
| Archive deprecated sessions | PENDING | Move to `archive/claude_sessions_20251211/` |
| Create archive manifest | PENDING | Include file list and sizes |
| Verify dropdown still works | PENDING | Test after archive |

**CRITICAL**: Archive to `/home/micha/bqx_ml_v3/archive/` NOT `~/.claude/`

**CORRUPTED SESSIONS (MUST ARCHIVE)**:
- `72a1c1a7-*` (QA OLD, 8.1 MB) - **CORRUPTED**
- `b959d344-*` (BA OLD, 3.3 MB) - **CORRUPTED**

**Active Sessions (DO NOT ARCHIVE)**:
- `b2360551-*` (CE, 5.0 MB)
- `c31dd28b-*` (EA, 2.3 MB)

---

### P0: ACTIVE - Step 6 Monitoring & Audit (CE Directive 04:50)

**CE DIRECTIVE**: `inboxes/QA/20251211_0450_CE-to-QA_STEP6_AUDIT_DIRECTIVE.md`

| Task | Priority | Trigger | Status |
|------|----------|---------|--------|
| **Monitor Step 6 process** | P0 | NOW | 🔵 **ACTIVE** |
| **Audit EURUSD data** | P0 | EURUSD complete | PENDING |
| **Verify feature coverage** | P0 | Each pair | PENDING |
| ISSUE-003: Validate all outputs | P1 | All pairs complete | PENDING |
| ISSUE-004: Pre-Step 7 gate | P2 | After ISSUE-003 | PENDING |

**CURRENT PROCESS**:
- PID: 1272452
- Mode: SEQUENTIAL + CHECKPOINT
- Log: `logs/step6_sequential_*.log`

**USER MANDATES TO VERIFY**:
- ✅ Sequential pairs (one at a time)
- ✅ 12 workers per pair
- ✅ Checkpoint/resume capability

**DATA AUDIT CHECKLIST (Per Pair)**:
- [ ] Parquet file exists
- [ ] ~100K rows
- [ ] >10K columns
- [ ] All 5 feature categories present (pair, tri, mkt, var, csi)
- [ ] No NULL in interval_time
- [ ] Target columns h15-h105 present

**REPORTING**:
1. `QA-to-CE_STEP6_EURUSD_AUDIT.md` - After first pair
2. `QA-to-CE_STEP6_PROGRESS_50PCT.md` - At 14 pairs
3. `QA-to-CE_STEP6_FINAL_AUDIT.md` - After completion

---

### COMPLETED ISSUES

| Issue | Priority | Completed | Status |
|-------|----------|-----------|--------|
| ~~GAP-FIX~~ | ~~P0~~ | 03:40 | ✅ **COMPLETE** |
| ~~INTEL-UPDATE~~ | ~~P0~~ | 04:20 | ✅ **COMPLETE** |

---

### ✅ COMPLETE: EA Gap Remediation Validated

| Task | Status |
|------|--------|
| **Validate Gap Remediation Fix** | ✅ **CE VERIFIED 03:40** |

**Validation Checklist**:
- [x] `var_*` query returns 63 tables ✅
- [x] `csi_*` query returns 144 tables ✅
- [x] Table count per pair: 256 + 194 + 12 + 63 + 144 = **669** ✅
- [x] `feature_catalogue.json` reflects CSI as COMPLETE ✅
- [x] Gap counts updated correctly ✅

**Result**: 100% coverage achieved - Step 6 ready for restart

---

### PAUSED: ISSUE-006 - Test GAP-001 Remediation

| Task | Trigger |
|------|---------|
| **Test GAP-001 Remediation** | First pair (EURUSD) ~00:25 UTC |

**Checklist**:
- [ ] Run Step 7 `feature_selection_robust.py` on EURUSD parquet
- [ ] Verify parquet loading works without BQ fallback
- [ ] Confirm $30 cost savings achieved

**Deliverable**: `QA-to-CE_GAP001_TEST_RESULTS.md`

---

### STATUS: Awaiting Triggers

| Item | Status |
|------|--------|
| QA Status | IDLE |
| Step 6 | RUNNING (BA executing) |
| ETA | ~3-4 hours |

**No immediate action required** - Await Step 6 completion notification from BA.

---

### QUEUED: P1 - Step 6 Output Validation

| Task | Trigger | Checklist |
|------|---------|-----------|
| **Validate Step 6 Output** | BA Step 6 complete | See below |

**Validation Checklist**:
- [ ] 28 parquet files exist in `data/features/`
- [ ] Each file has ~100K rows
- [ ] Each file has ~11,337 columns
- [ ] No NULL in interval_time column
- [ ] No NULL in target columns
- [ ] File sizes reasonable (>100MB each)

**Deliverable**: Step 6 output validation report to CE

---

### QUEUED: P1 - Pre-Step 7 Gate Check

| Task | Trigger |
|------|---------|
| **Pre-Step 7 Gate Check** | After Step 6 validation |

**Checklist**:
- [ ] Parquet files accessible
- [ ] `feature_selection_robust.py` ready
- [ ] Stability selection parameters validated

**Deliverable**: Pre-Step 7 gate check report to CE

---

### QUEUED: P2 - GATE_4 Validation Prep

| Task | Trigger |
|------|---------|
| **GATE_4 Validation Prep** | After Step 8 completes |

**Checklist**:
- [ ] New model accuracy vs 59-feature baseline
- [ ] Feature count comparison
- [ ] Coverage within 30-50% target

**Deliverable**: GATE_4 validation report to CE

---

### STANDING: Cost & Documentation Monitoring

| Task | Frequency |
|------|-----------|
| Track BigQuery usage during pipeline | Continuous |
| Report cost anomalies | As needed |
| Update intelligence files post-pipeline | After each phase |
| Archive obsolete documents | As needed |

---

### P0: COMPLETED - STALE DOCS CLEANUP (22:00)

| Task | Status | Completed |
|------|--------|-----------|
| ~~**Stale Documentation Cleanup**~~ | **COMPLETE** | 22:00 |

**Report**: `20251210_2200_QA-to-CE_STALE_DOCS_CLEANUP_COMPLETE.md`

**Files Archived**:
- QA_BA_PROGRESS_TRACKER.md - ARCHIVED (GATE_1 PASSED)
- QA_GATE1_PREFLIGHT_CHECKLIST.md - ARCHIVED (PASSED)
- CE_MASTER_REMEDIATION_PLAN.md - ARCHIVED (8/9 REM complete)
- CE_FORWARD_WORK_PLAN.md - ARCHIVED (Phase 1.5 complete)

---

### P0: COMPLETED - GATE_3 RE-VALIDATION PREP (21:45)

| Task | Status | Completed |
|------|--------|-----------|
| ~~**GATE_3 Re-Validation Preparation**~~ | **COMPLETE** | 21:45 |

**Report**: `20251210_2145_QA-to-CE_GATE3_PREP_COMPLETE.md`

**Deliverables**:
- `scripts/validate_gate3.py` - UPDATED (v2, model versioning, dynamic features)
- `scripts/validate_coverage.py` - NEW (coverage validation)
- `intelligence/qa_protocols/GATE_3_TEST_DATA.md` - NEW (test data requirements)
- Cross-reference audit - ALL FILES CONSISTENT

**Ready for**: GATE_3 re-validation when pipeline reaches Step 9 (SHAP)

---

### P0: COMPLETED - UPDATE INTELLIGENCE FILES (20:55)

| Task | Status | Completed |
|------|--------|-----------|
| ~~**Update All Intelligence Files**~~ | **COMPLETE** | 20:55 |

**Report**: `20251210_2055_QA-to-CE_INTELLIGENCE_FILES_UPDATED.md`

**Files Updated**:
- `intelligence/context.json` - Model count (588), feature universe (11,337/1,064)
- `intelligence/ontology.json` - Model definitions, feature schema
- `intelligence/roadmap_v2.json` - Pipeline status, feature counts
- `intelligence/semantics.json` - Feature universe, model status
- `intelligence/feature_catalogue.json` - Verified correct, timestamp updated

**Key Changes**:
- Model count: 784 → 588 (ElasticNet removed)
- Feature counts: 6,477 → 11,337 columns, 1,064 unique
- Pipeline status: Step 6 IN PROGRESS
- 59-feature model: OBSOLETE

---

### P0: COMPLETED - CE DIRECTIVE (20:10)

| Task | Status | Completed |
|------|--------|-----------|
| ~~**SANITIZE: 59-Feature Old Model References**~~ | **COMPLETE** | 20:20 |

**Report**: `20251210_2020_QA-to-CE_59FEATURE_AUDIT_REPORT.md`

**Key Findings**:
- **0 hardcoded feature lists** in training pipelines (all use dynamic discovery)
- **2 output artifacts** flagged (will auto-update after retrain)
- **3 scripts** with informational references (KEEP - baseline comparison)
- **15+ communications** with historical context (KEEP)

**Verdict**: No immediate sanitization required. Workspace ready for full universe training.

---

### P1: AWAITING (Full Feature Testing)

| Task | Trigger | Notes |
|------|---------|-------|
| **Re-validate GATE_3 (Coverage)** | BA completes 11,337 feature testing | Current: 17.33%, Target: 30-50% |

**Note**: GATE_3 passed for accuracy (91.70%) but coverage (17.33%) below target. Will re-validate after BA completes full feature universe testing per USER MANDATE.

---

### P2: COMPLETED

| Task | Status | Notes |
|------|--------|-------|
| ~~GATE_3 Validation (Initial)~~ | **PASSED** | 91.66% accuracy, 38.27% coverage |
| ~~Roadmap Remediation (13 gaps)~~ | **COMPLETE** | v2.3.1 consistent |
| ~~Process/Artifact Cleanup~~ | **COMPLETE** | ~145 KB recovered |
| ~~Target Table Validation~~ | **COMPLETE** | 28/28 BQX tables verified |
| ~~Horizon Prep~~ | **COMPLETE** | Validation script ready |

---

### P3: ONGOING

| Task | Frequency | Next Due |
|------|-----------|----------|
| Daily cost monitoring | Daily | Tomorrow |
| Weekly audit | Weekly | Monday |

---

## BA STATUS (From BA_TODO)

**P0 CRITICAL - USER MANDATE**:
- Full 11,337 column universe testing REQUIRED (1,064 unique features)
- h30-h105 expansion BLOCKED until complete
- Current h15 uses only 59 features (OBSOLETE - will be replaced)

**GATE_3 (h15_ensemble_v2.joblib)**:
| Criterion | Target | Actual | Status |
|-----------|--------|--------|--------|
| Accuracy | ≥85% | 91.70% | PASS |
| Coverage | 30-50% | 17.33% | **NEEDS RE-VALIDATION** |
| SHAP | 100K+ | 100K+ | PASS |

---

## COMPLETED (This Session)

| Task | Status | Time |
|------|--------|------|
| GATE_1 Validation | PASSED | Earlier |
| GATE_2 Validation | PASSED | 00:40 |
| Semantics Remediation | COMPLETE | 00:10 |
| F3b Cleanup (56 tables) | COMPLETE | 00:20 |
| Comprehensive Remediation | COMPLETE | 01:00 |
| Agent Alignment Audit | ALL ALIGNED | 01:15 |
| Roadmap Gap Audit | 13 gaps found | 01:35 |
| Roadmap Remediation | **13/13 COMPLETE** | 02:05 |
| Process/Artifact Cleanup | **COMPLETE** | 02:25 |
| Target Table Validation | **28/28 VERIFIED** | 02:25 |
| GATE_3 Validation (Initial) | **PASSED** | 02:40 |
| Pre-validation Tasks | **COMPLETE** | 03:00 |
| Horizon Prep | **COMPLETE** | 03:30 |
| validate_gate3.py | **CREATED & TESTED** | 03:30 |
| SHAP Cost Estimate | **COMPLETE** | 04:35 |
| 59-Feature Audit | **COMPLETE** | 20:20 |
| Intelligence Files Update | **COMPLETE** | 20:55 |
| GATE_3 Re-Validation Prep | **COMPLETE** | 21:45 |
| Stale Docs Cleanup | **COMPLETE** | 22:00 |

---

## TOOLS CREATED

| Script | Purpose |
|--------|---------|
| `scripts/validate_gate3.py` | Reusable GATE_3 validation (v2 - supports model versioning) |
| `scripts/validate_coverage.py` | Coverage validation for 30-50% target |

---

## SUCCESS CRITERIA

| Deliverable | Criteria | Status |
|-------------|----------|--------|
| Roadmap | 0 inconsistencies | ✅ ACHIEVED |
| Cleanup | Temp files removed | ✅ ACHIEVED |
| Target validation | 28 tables verified | ✅ ACHIEVED |
| GATE_3 (initial) | Accuracy ≥85% | ✅ ACHIEVED |
| GATE_3 (coverage) | 30-50% range | ⚠️ RE-VALIDATE AFTER BA |
| Horizon prep | Script ready | ✅ ACHIEVED |

---

## SESSION STATISTICS

| Metric | Value |
|--------|-------|
| Tasks completed | 20 |
| Gates validated | 3 (GATE_1, GATE_2, GATE_3) |
| Tables cleaned | 56 (F3b) |
| Reports submitted | 18+ |
| Remediations applied | 13 |
| Scripts created | 2 |
| Intelligence files updated | 5 |
| Stale docs archived | 4 |

---

*Updated by CE - December 11, 2025 04:00*
