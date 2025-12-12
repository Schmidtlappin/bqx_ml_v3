# CE DIRECTIVE: Update Intelligence & Mandate Files - Current State

**Document Type**: CE DIRECTIVE
**Date**: December 12, 2025 18:40 UTC
**From**: Chief Engineer (CE)
**To**: Quality Assurance Agent (QA)
**Priority**: P1 - HIGH
**Directive ID**: CE-1840

---

## EXECUTIVE DIRECTIVE

**QA MUST update all intelligence and mandate files to reflect current project state** after charge ingestion complete.

---

## BACKGROUND

Multiple significant project changes occurred Dec 11-12:
1. **Agent charges updated to v2.0.0** with enhanced responsibilities
2. **Cloud Run Polars architecture deployed** (user-mandated, replaces BigQuery merge)
3. **Model count correction**: 784 → 588 (ElasticNet removed from ensemble)
4. **Table count correction**: 669 → 667 (excluded 2 summary tables from count)
5. **GBPUSD Cloud Run test running** (expected completion ~18:30 UTC)
6. **V2 migration complete**: All 4,888 tables in v2 datasets, V1 deleted

Intelligence and mandate files need comprehensive updates to reflect these changes.

---

## SCOPE OF WORK

### Phase 1: Intelligence Files (Priority Order)

**1. context.json** (HIGHEST PRIORITY)
- Update `current_phase`: Should reflect Cloud Run deployment phase
- Update `cloud_run_deployment` section with Polars architecture
- Update `model_architecture`: 784 → 588 models (remove ElasticNet references)
- Update `table_count_per_pair`: 669 → 667 (note exclusion of summary tables)
- Update `training_files_complete`: 2/28 (EURUSD, AUDUSD local), GBPUSD pending validation
- Update `cost_model`: Add Cloud Run costs ($30.82/year vs $3,324/year VM-only)
- Update `last_updated` timestamp
- Add `gbpusd_status` if completed during update

**2. roadmap_v2.json**
- Update Phase 1 status to reflect Cloud Run deployment
- Update model counts: 784 → 588
- Add Cloud Run deployment milestone
- Update completion percentages (2/28 pairs = 7%)
- Update cost estimates with Cloud Run actuals
- Add agent charge v2.0.0 milestone

**3. semantics.json**
- Update feature_count validations if needed
- Update model_configuration to reflect 3-algorithm ensemble (no ElasticNet)
- Add cloud_run_architecture section
- Update deployment_methodology

**4. ontology.json**
- Update Model entity: algorithms = [LightGBM, XGBoost, CatBoost] (3 only)
- Update Pipeline entity: Add cloud_run_deployment
- Update Feature entity: Ensure 6,477 total features reflected
- Update table_count: 667 per pair

**5. feature_catalogue.json**
- Validate version is current (v2.1.0 or later)
- Update ledger mandate references if needed
- Ensure feature counts align with 6,477 total

### Phase 2: Mandate Files (If Changes Needed)

**1. BQX_ML_V3_FEATURE_INVENTORY.md**
- Update if feature counts changed
- Ensure horizon count = 7 (h15-h105)
- Ensure model count = 588

**2. README.md** (Project root)
- Update project status
- Add Cloud Run deployment information
- Update cost estimates
- Update completion status (2/28 pairs)

**3. AGENT_ONBOARDING_PROTOCOL.md**
- Already current (no changes needed unless you identify gaps)

### Phase 3: Registries & Catalogues

**1. AGENT_REGISTRY.json**
- Already updated to v3.3 (CE completed)
- Verify accuracy during review

**2. feature_catalogue.json** (if not covered in Phase 1)
- Ensure consistency with other files

---

## DETAILED UPDATE REQUIREMENTS

### context.json Updates (Specific Changes)

**Section: cloud_run_deployment** (ADD if missing, UPDATE if exists):
```json
"cloud_run_deployment": {
  "status": "ACTIVE",
  "architecture": "Polars-based parallel merge",
  "user_mandate": "User mandated Polars over BigQuery (4.6× faster)",
  "cpu": 4,
  "memory_gb": 12,
  "timeout_hours": 2,
  "execution_time_per_pair_minutes": 13,
  "cost_per_pair_usd": 1.10,
  "annual_cost_total_usd": 30.82,
  "pairs_complete": 2,
  "pairs_pending": 26,
  "test_pair": "GBPUSD",
  "test_status": "RUNNING",
  "test_started": "2025-12-12T17:17:00Z",
  "test_expected_completion": "2025-12-12T18:30:00Z"
}
```

**Section: model_architecture** (UPDATE):
```json
"model_architecture": {
  "total_models": 588,
  "calculation": "28 pairs × 7 horizons × 3 algorithms",
  "base_algorithms": ["LightGBM", "XGBoost", "CatBoost"],
  "meta_learner": "LogisticRegression",
  "ensemble_count": 3,
  "note": "ElasticNet removed from ensemble per user directive"
}
```

**Section: training_files** (UPDATE):
```json
"training_files": {
  "total_required": 28,
  "completed": 2,
  "completion_percentage": 7.1,
  "completed_pairs": ["EURUSD", "AUDUSD"],
  "pending_validation": "GBPUSD",
  "pending_pairs": 25,
  "local_merge_complete": ["EURUSD", "AUDUSD"],
  "cloud_run_test_in_progress": "GBPUSD"
}
```

**Section: cost_model** (UPDATE):
```json
"cost_model": {
  "bigquery_storage_monthly": 2.16,
  "bigquery_queries_monthly": 0.50,
  "cloud_run_annual": 30.82,
  "cloud_run_monthly": 2.57,
  "total_monthly_usd": 5.23,
  "total_annual_usd": 62.82,
  "note": "Cloud Run replaces VM costs ($277/mo → $2.57/mo), 99% cost reduction"
}
```

---

## TIMELINE

**Phase 1 (Intelligence Files)**: 90-120 minutes
- context.json: 30 min
- roadmap_v2.json: 25 min
- semantics.json: 20 min
- ontology.json: 20 min
- feature_catalogue.json: 15 min

**Phase 2 (Mandate Files)**: 30-45 minutes
- Feature inventory: 15 min
- README: 15 min
- Other mandates: 15 min (if needed)

**Phase 3 (Validation)**: 15-20 minutes
- Cross-file consistency check
- Version alignment
- Count reconciliation

**Total Estimated Time**: 135-185 minutes (2.25-3 hours)

**Deadline**: Complete by **21:00 UTC Dec 12** (allows time for review before inventory deadline)

---

## DELIVERABLES

1. **Updated Intelligence Files** (5 files minimum):
   - `/intelligence/context.json`
   - `/intelligence/roadmap_v2.json`
   - `/intelligence/semantics.json`
   - `/intelligence/ontology.json`
   - `/intelligence/feature_catalogue.json`

2. **Updated Mandate Files** (as needed):
   - `/mandate/BQX_ML_V3_FEATURE_INVENTORY.md`
   - `/README.md`

3. **Completion Report** to CE:
   - Message format: `YYYYMMDD_HHMM_QA-to-CE_INTELLIGENCE_MANDATE_UPDATE_COMPLETE.md`
   - Include: Files updated, key changes, validation results, issues found

---

## VALIDATION CRITERIA

Before marking complete, validate:
- ✅ All counts consistent across files (588 models, 667 tables, 6,477 features)
- ✅ All version numbers updated
- ✅ All "last_updated" timestamps current
- ✅ Cloud Run architecture accurately documented
- ✅ Cost models reflect actual Cloud Run costs
- ✅ Agent charge v2.0.0 references added where relevant
- ✅ No stale information (>7 days old descriptions in active areas)

---

## COORDINATION WITH OTHER WORK

**Work Product Inventory** (due 21:45 UTC):
- QA can include these intelligence updates in the inventory
- Mark as "in progress" if not complete by inventory deadline
- Update inventory after completion if needed

**GBPUSD Validation** (expected ~18:30 UTC):
- If GBPUSD completes during intelligence updates, pause to validate
- Then update context.json with GBPUSD results before finalizing
- This ensures intelligence files reflect most current state

---

## SUCCESS CRITERIA

This directive is successfully fulfilled when:
- [ ] All Phase 1 intelligence files updated and validated
- [ ] All Phase 2 mandate files updated (if changes needed)
- [ ] Cross-file consistency verified (counts, versions, dates)
- [ ] Completion report sent to CE
- [ ] All updates reflect Cloud Run Polars architecture
- [ ] All updates reflect 588 models (not 784)
- [ ] All updates reflect 667 tables per pair (not 669)

---

## PRIORITY JUSTIFICATION

**Why P1-HIGH**:
1. Intelligence files are source of truth for all agents
2. Stale information causes agent coordination errors
3. Work product inventories depend on accurate intelligence
4. 25-pair production rollout needs current documentation
5. Cost projections and budgeting depend on accurate cost models

**Impact of Delay**:
- Agents operating with outdated information
- Inventory reports may contain inaccuracies
- Production rollout planning based on wrong assumptions
- Cost management decisions based on stale data

---

## QUESTIONS/CLARIFICATIONS

**Q: What if GBPUSD test fails during update?**
A: Update context.json with test status (failed), include error details, continue with other files. Don't block on test completion.

**Q: What if I find inconsistencies beyond the specified updates?**
A: Document them in completion report, fix if time permits, flag for follow-up if critical.

**Q: Should I update files if agents haven't ingested v2.0.0 charges yet?**
A: YES. Intelligence updates are independent of agent charge ingestion. Proceed immediately.

**Q: Can I use automated tools or scripts?**
A: YES, if you have them. Manual updates are acceptable. Prioritize accuracy over speed.

---

## CE SUPPORT

**CE is available for**:
- Clarifications on technical details
- Approvals for scope changes if needed
- Conflict resolution if priorities conflict
- Validation of major changes before commit

**Don't hesitate to ask CE if**:
- Unsure about Cloud Run architecture details
- Find contradictory information requiring decision
- Need approval to add/remove sections

---

## FINAL DIRECTIVE

✅ **QA: UPDATE ALL INTELLIGENCE AND MANDATE FILES TO REFLECT CURRENT STATE BY 21:00 UTC**

**Start Time**: After charge v2.0.0 ingestion (est. 19:30-19:45 UTC)
**Deadline**: 21:00 UTC Dec 12
**Priority**: P1-HIGH

---

**Chief Engineer (CE)**
Session: 05c73962-b9f1-4e06-9a5a-a5ae556cae5a

**Status**: Directive issued
**Next CE Check**: 21:00 UTC (review QA completion report)

---

**END OF DIRECTIVE**
