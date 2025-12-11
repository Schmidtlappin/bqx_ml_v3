# BA Task List

**Last Updated**: December 11, 2025 06:20
**Maintained By**: CE (refresh)

---

## P0: IMMEDIATE - ONBOARDING REQUIRED (CE Directive 06:20)

**CE DIRECTIVE**: `inboxes/BA/20251211_0620_CE-to-BA_ONBOARDING_DIRECTIVE.md`

**You MUST complete onboarding before any other tasks.**

### Required Reading (in order):
1. **Intelligence Files**: context.json, ontology.json, roadmap_v2.json, semantics.json, feature_catalogue.json
2. **Mandate Files**: README.md, BQX_ML_V3_FEATURE_INVENTORY.md, FEATURE_LEDGER_100_PERCENT_MANDATE.md
3. **Agent Files**: BA_TODO.md (this file), AGENT_ONBOARDING_PROMPTS.md, BA_SESSION_HANDOFF.md
4. **Your Inbox**: All recent .md files in `inboxes/BA/`

**After onboarding, report to CE**: `inboxes/CE/[timestamp]_BA-to-CE_ONBOARDING_COMPLETE.md`

---

## P0: **LEAD** - STEP 6 EXECUTION (CE Directive 04:55)

**ROLE**: You are designated **LEAD** for Step 6 execution until complete.

| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| **Step 6 Lead** | **CRITICAL** | 🟢 **EXECUTING** | Own until complete |
| **Real-time Remediation** | **CRITICAL** | 🔵 **ACTIVE** | Fix issues immediately |

**CE LEAD DIRECTIVE**: `inboxes/BA/20251211_0455_CE-to-BA_STEP6_LEAD_DIRECTIVE.md`

**CURRENT STATUS**:
```
PAIR 1/28: EURUSD
Tables: 79/669 (12%)
Progress: ~0.2/s, ~2850s remaining
Workers: 12 (focused on EURUSD)
```

**YOUR RESPONSIBILITIES**:
1. ✅ Monitor processes continuously
2. ✅ Remediate issues in real-time
3. ✅ Restart if process crashes (checkpoints preserved)
4. ✅ Report milestones to CE

**USER MANDATES**:
1. ✅ All 12 workers focus on ONE pair at a time
2. ✅ Parquet checkpoint/resume capability
3. ✅ Sequential pair processing

**MONITORING**:
```bash
tail -f logs/step6_sequential_*.log
watch -n 60 'ps -p 1272452 -o pid,rss,%mem,%cpu'
```

**AUTHORITY**: Authorized to restart processes without CE approval.

**COORDINATION**:
- QA: Data audit
- EA: System health

---

## P0: COMPLETE - PIPELINE HOTFIXES (CE Directive 20:45) ✅ COMPLETE

| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| **Disable cleanup (shutil.rmtree)** | **CRITICAL** | ✅ **DONE** | Saves merged parquet first |
| **Verify EURUSD data exists** | **CRITICAL** | ✅ **DONE** | Restarted with fix |
| **Fix hardcoded 59-feature query** | **HIGH** | ✅ **DONE** | Dynamic parquet loading |

**Fixes Applied (20:35)**:
- `parallel_feature_testing.py:367-376` - Save to `data/features/{pair}_merged_features.parquet`
- `stack_calibrated.py:39-89` - `load_from_merged_parquet()` + enhanced feature loader

**BA Report**: `inboxes/CE/20251210_2040_BA-to-CE_BOTH_FIXES_COMPLETE.md`

---

## P0: CRITICAL - COMPLETE FEATURE UNIVERSE ✅ APPROVED

| Task | Status | Notes |
|------|--------|-------|
| **Implement COMPLETE Feature Universe** | **APPROVED** | CE APPROVAL 06:00 |
| ~~Step 1~~: Create `parallel_feature_testing.py` | **DONE** | File created |
| ~~Step 2~~: Run dry_run (55 features) | **DONE** | $0.03 - TOO LOW |
| ~~Step 2b~~: Add `%eurusd%` tables | **DONE** | 256 tables, 4,173 cols |
| ~~Step 2d~~: Add `tri_*` tables | **DONE** | 194 tables, 6,460 cols |
| ~~Step 2e~~: Add `mkt_*` tables | **DONE** | 12 tables, 704 cols |
| ~~Step 2f~~: Re-run dry_run (COMPLETE) | **DONE** | $29.56 - WITHIN BUDGET |
| ~~Step 3~~: Report NEW dry run results to CE | **DONE** | 462 tables, 11,337 cols |
| ~~Step 4~~: Await CE approval | **APPROVED** | See directive below |
| ~~Step 4b~~: Upgrade VM to 64GB RAM | **DONE** | 64GB confirmed |
| ~~Step 5~~: Run single pair test | ✅ **DONE** | 10,783 features, $0.89 |
| **Step 6**: Run full 28-pair test | 🟡 **READY** | Gap remediation COMPLETE, awaiting restart |

**Step 6 Status**: READY - Gap remediation COMPLETE (03:40), awaiting user authorization

**CORRECTED FEATURE COUNTS (2025-12-11):**

| Metric | Value | Use Case |
|--------|-------|----------|
| Total tables per pair | 669 | Full extraction |
| Unique features | ~1,064+ | ML training (after merge/dedup) |

| Category | Tables | Status |
|----------|--------|--------|
| `%pair%` (pair-specific) | 256 | ✅ DONE |
| `tri_*` (triangulation) | 194 | ✅ DONE |
| `mkt_*` (market-wide) | 12 | ✅ DONE |
| `var_*` (variance) | 63 | ✅ **NEW** |
| `csi_*` (currency strength) | 144 | ✅ **NEW** |
| **TOTAL** | **669** | **100% COVERAGE** |

**CE APPROVALS**:
- `inboxes/BA/20251210_0600_CE-to-BA_EXECUTION_APPROVED.md` (Steps 5-6)
- `inboxes/BA/20251210_0715_CE-to-BA_MEMORY_UPGRADE_APPROVED.md` (64GB RAM)
- `inboxes/BA/20251210_1915_CE-to-BA_STEP6_APPROVED_PARALLEL.md` (Step 6 + parallel)

---

## P0: CRITICAL - USER MANDATE (Full Feature Testing)

| Task | Status | Notes |
|------|--------|-------|
| **Full 11,337 Column Universe Testing** | **IN PROGRESS** | Steps 5-6 approved |
| - Query all 11,337 columns (1,064 unique) | IN PROGRESS | Use parallel batch |
| - Run stability selection (50% threshold) | PENDING | 5 folds x 3 seeds |
| - Identify optimal subset (expected 200-600) | PENDING | vs current 59 |
| **Retrain h15 with optimal features** | PENDING | After feature selection |
| - Retrain base models (LGB, XGB, CB) | PENDING | Use full stable features |
| - Recalibrate probabilities | PENDING | Platt scaling |
| - Retrain meta-learner | PENDING | LogisticRegression |
| - Generate SHAP values (100K+ samples) | PENDING | TreeSHAP for ALL models |

**USER MANDATE**: Full universe testing MUST complete before h30-h105 expansion.

---

## P1: HIGH (After Full Feature Testing)

| Task | Status | Notes |
|------|--------|-------|
| h30-h105 horizon expansion | **BLOCKED** | Awaiting full feature testing |
| Update feature ledger with final SHAP values | PENDING | After h15 retrain |

---

## COMPLETED (This Session)

| Task | Completed | Notes |
|------|-----------|-------|
| Downgrade XGBoost to 2.1.0 | 02:25 | TreeSHAP compatibility |
| Re-run TreeSHAP for ALL 3 models | 02:25 | 100K+ samples |
| GATE_3 validation | 02:40 | QA verified |
| h15_ensemble_v2.joblib re-serialization | 03:30 | Full pipeline |
| GCS upload | 03:30 | gs://bqx-ml-v3-models/models/eurusd/ |
| Complete feature universe dry run | 05:50 | 462 tables, $29.56 |
| CE approval for execution | 06:00 | Steps 5-6 proceed |

---

## GATE_3 STATUS: PASSED (h15_ensemble_v2.joblib)

| Criterion | Target | Actual | Status |
|-----------|--------|--------|--------|
| Called accuracy | ≥85% | 91.70% | PASS |
| Coverage | 30-50% | 17.33% | NOTE* |
| SHAP samples | 100K+ | 100K+ | PASS |
| SHAP method | TreeSHAP ALL | TreeSHAP ALL | PASS |
| Gating curves | Documented | Complete | PASS |
| Model artifacts | GCS | Uploaded | PASS |

*Coverage to be re-validated after full 11,337 column testing

---

## FILES TO CREATE

| File | Purpose |
|------|---------|
| `pipelines/training/parallel_feature_testing.py` | **DONE** - Parallel batch processing |

## FILES TO MODIFY

| File | Change |
|------|--------|
| `pipelines/training/stack_calibrated.py` | Remove hardcoded 59-feature list |
| Training SQL | Dynamic feature query from ledger |

---

## SUCCESS CRITERIA (Full Feature Testing)

- [x] All 11,337 columns queried (462 tables)
- [x] All 3 categories: `%eurusd%` + `tri_*` + `mkt_*`
- [ ] Stability selection run on full universe (1,064 unique features)
- [ ] Optimal subset identified (50% threshold)
- [ ] h15 retrained with expanded feature set
- [ ] Accuracy improvement documented
- [ ] Only then: h30-h105 expansion proceeds

---

*Updated by CE - December 11, 2025 04:55*
