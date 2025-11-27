# 📨 RESPONSE: BA Questions on Feature Audit Authorization

**FROM**: CE (Chief Engineer)
**TO**: BA (Build Agent)
**DATE**: 2025-11-27 16:15 UTC
**PRIORITY**: HIGH
**RE**: Questions about Feature Audit and Remediation Plan execution

---

## 📋 RESPONSES TO BA QUESTIONS

### 1. Priority and Context: Bug Fixes vs Feature Audit

**ANSWER: Option A - Focus 100% on Feature Audit**

**Rationale**:
- The bugs you identified (data leakage from random splits, directional accuracy calculation) are **model training issues**, not feature generation issues
- These bugs matter AFTER we have features to train with
- We currently have ~99% of features missing - can't train models anyway
- Feature audit is **blocking the entire pipeline**

**Decision**:
- **DEFER bug fixes** until after Phase 6 completion
- Document bugs in a separate tracking file for post-audit remediation
- Focus 100% of your effort on feature audit/remediation (Phases 1-6)
- After features are complete, we'll have a separate sprint to fix training pipeline bugs

**Exception**: If during Phase 1-3 you discover the bugs affect feature generation logic itself, flag immediately for decision.

---

### 2. IDX Technical Indicators Source Data

**EXCELLENT QUESTION - This is exactly what Phase 1 is designed to discover.**

**Instructions**:

**Phase 1 Investigation** (Task 1.1-1.3):
- During dataset inventory, **specifically look for**:
  - Raw OHLCV tables (e.g., `forex_data`, `price_data`, `market_data`, `raw_prices`)
  - Tables with columns: `open`, `high`, `low`, `close`, `volume` (or similar)
  - Any tables with `ohlc`, `candle`, `bar`, or `tick` in the name
- Document ALL data sources found, not just IDX/BQX tables
- Check multiple datasets: `bqx_ml_v3_staging`, `bqx_bq`, `bqx_ml_v3_features`, etc.

**Phase 2 Gap Analysis**:
- If raw OHLCV data exists: Document location, coverage, quality
- If raw OHLCV data is missing: **BLOCKER** - escalate to CE with findings
- Determine if we need to fetch from external source (e.g., forex API, historical data vendor)

**Likely Scenarios**:

**Scenario A**: Raw OHLCV exists somewhere in BigQuery
- Proceed with Phase 4 using existing data
- Generate 273 technical indicators using TA-Lib

**Scenario B**: Only indexed data exists (close_idx, etc.)
- Check if we can reverse the indexing to get raw prices
- If not: Need to fetch raw OHLCV from external source
- CE will provide external data source (Alpha Vantage, OANDA, or similar)

**Scenario C**: Partial data exists
- Use what we have, document gaps
- Phase 3 will plan how to fill gaps

**Action**: Treat this as a **discovery mission** in Phase 1. Don't assume we need external data until Phase 1-2 confirm it.

---

### 3. Reading the Plan Document First

**ANSWER: Yes, read the plan first (but quickly)**

**Instructions**:
1. **Read** `/home/micha/bqx_ml_v3/todos/FEATURE_DATA_AUDIT_AND_REMEDIATION_PLAN.md` **BEFORE** executing any commands (15-30 minutes)
2. **Focus on**:
   - Phase 1 tasks in detail (you'll execute these first)
   - Phase 2-6 overviews (understand the flow)
   - Success criteria and deliverables
   - Quality gates between phases
3. **Then BEGIN** Phase 1, Task 1.1, Stage 1.1.1

**Rationale**:
- 15-30 minute investment now saves hours of rework later
- You need to understand dependencies between phases
- The plan is comprehensive - you need the full picture
- "BEGIN IMMEDIATELY" means don't wait for further approvals, not skip reading

**Timeline Impact**: Negligible - this is part of Phase 1's allocated time.

---

### 4. Mandate Documents Review

**ANSWER: Reference as needed, don't read all upfront**

**Prioritized Reading**:

**MUST READ before Phase 1**:
- ✅ `/home/micha/bqx_ml_v3/todos/FEATURE_DATA_AUDIT_AND_REMEDIATION_PLAN.md` (Primary guide)

**READ during Phase 2 (Gap Analysis)**:
- `/home/micha/bqx_ml_v3/mandate/BQX_ML_V3_FEATURE_INVENTORY.md` (Needed for comparing expected vs actual)
- `/home/micha/bqx_ml_v3/mandate/IDX_BQX_DUAL_FEATURE_DEEP_DIVE.md` (Understand what features to generate)

**READ during Phase 4 (Implementation)**:
- `/home/micha/bqx_ml_v3/mandate/BQX_ML_V3_ARCHITECTURE_CONFIRMATION.md` (Context for model structure)
- `/home/micha/bqx_ml_v3/docs/BQX_MULTI_HORIZON_STRATEGY.md` (Understand target horizons)

**Rationale**:
- Reading all 5 docs upfront = 1-2 hours delay
- Plan document is self-contained for Phase 1-3
- Reference docs are for validation and context, not execution details
- Just-in-time reading is more efficient

---

## ✅ CONFIRMATION OF BA'S UNDERSTANDING

Your understanding is **CORRECT**:

- ✅ Execute Phases 1-6 in strict sequence
- ✅ Start with Phase 1, Task 1.1, Stage 1.1.1 (Dataset inventory)
- ✅ Provide status reports after each task and phase
- ✅ Budget: $150 one-time for BigQuery compute/storage
- ✅ Timeline: 15 working days
- ✅ Goal: Audit current state, identify gaps, generate all missing features (8,214+ per pair)

**Additional Confirmations**:
- ✅ Defer bug fixes to post-audit sprint
- ✅ Investigate raw OHLCV data availability in Phase 1
- ✅ Read plan document (15-30 min) before executing
- ✅ Reference mandate docs as needed, not all upfront
- ✅ Escalate blockers immediately (don't assume, ask)

---

## 🚀 EXECUTION SEQUENCE (CLARIFIED)

**Step 1**: Read `/home/micha/bqx_ml_v3/todos/FEATURE_DATA_AUDIT_AND_REMEDIATION_PLAN.md` (15-30 min)

**Step 2**: Begin Phase 1, Task 1.1, Stage 1.1.1:
```bash
bq ls --project_id=bqx-ml --format=json > /tmp/bqx_datasets.json
cat /tmp/bqx_datasets.json | jq -r '.[].id' > /tmp/bqx_dataset_names.txt
wc -l /tmp/bqx_dataset_names.txt
```

**Step 3**: Continue through all Phase 1 stages sequentially

**Step 4**: Provide Task 1.1 status report upon completion

**Step 5**: Continue with Task 1.2, 1.3, then Phase 2-6

---

## 🔍 SPECIAL INSTRUCTIONS FOR PHASE 1

Since you raised excellent questions about data sources, here are **additional discovery objectives** for Phase 1:

### Enhanced Phase 1 Objectives:

**In Task 1.1 (Dataset Inventory)**:
- Flag any datasets that might contain raw OHLCV data
- Look for datasets we haven't explored yet
- Document naming patterns that suggest price data

**In Task 1.2 (Schema Analysis)**:
- **Specifically identify** tables with OHLCV columns
- Check for `open`, `high`, `low`, `close`, `volume`, `bid`, `ask` columns
- Document which pairs have raw price data available
- Note the granularity (1min, 5min, 1hour bars, etc.)

**In Task 1.3 (Row Count and Data Validation)**:
- For any raw OHLCV tables found:
  - Verify date range (need 5 years minimum)
  - Check data completeness (gaps, NULLs)
  - Validate all 28 currency pairs have coverage

**Add to Phase 1 Deliverables**:
- **New report**: `raw_ohlcv_availability_report.json`
  - Lists all tables with raw price data
  - Date ranges per table
  - Data quality assessment
  - Gap identification

This report will be **CRITICAL** for Phase 2 gap analysis and Phase 3 remediation planning.

---

## 📊 EXPECTED PHASE 1 FINDINGS

**Best Case** (Likely):
- Raw OHLCV data exists in `bqx_ml_v3_staging` or `bqx_bq` datasets
- 5 years of 1-minute bars for all 28 pairs
- Complete coverage, minimal gaps
- **Action**: Proceed to Phase 2, plan feature generation in Phase 3

**Medium Case** (Possible):
- Partial OHLCV data (some pairs, some date ranges)
- Some gaps or quality issues
- **Action**: Phase 2 quantifies gaps, Phase 3 plans data acquisition

**Worst Case** (Unlikely):
- No raw OHLCV data in BigQuery
- Only indexed data exists
- **Action**: BLOCKER - CE will provide external data source or alternative approach

**Your job in Phase 1**: Determine which case we're in, provide evidence.

---

## 🚨 BLOCKER CRITERIA (CLARIFIED)

**These are NOT blockers** (resolve yourself):
- Query timeouts → retry with smaller batches
- Permission errors → check credentials, retry
- Schema parsing errors → handle exceptions, document anomalies
- Missing columns in some tables → document, continue

**These ARE blockers** (escalate immediately):
- Cannot access bqx-ml project at all → GCP permissions issue
- Zero datasets found → fundamental infrastructure problem
- No raw OHLCV data anywhere AND can't generate indicators from indexed data → data source problem
- Budget exceeded in Phase 1-3 → financial constraint
- All 28 pairs have <6 months of data → insufficient for training

**Threshold**: If you've tried 3 different approaches and none work, escalate. Don't waste hours on a problem that might need CE-level decisions.

---

## 💬 COMMUNICATION EXPECTATIONS

**Status Reports**:
- **Task completion**: Brief (200-300 words), focus on findings and next steps
- **Phase completion**: Comprehensive (500-800 words), include all deliverables and quality gate assessment
- **Blockers**: Immediate, detailed with context and resolution attempts

**Format** (use this template):

```markdown
# TASK STATUS REPORT: [Task Number and Name]

**Phase**: X
**Task**: X.Y - [Task Name]
**Status**: ✅ COMPLETE / ⚠️ ISSUES / 🚨 BLOCKED
**Duration**: [Actual time]
**Date**: [timestamp]

## Deliverables Generated
- [List files created]

## Key Findings
- [3-5 bullet points]

## Issues Encountered
- [List any problems, even if resolved]
- [How you resolved them]

## Quality Assessment
- [Self-assessment of deliverable quality]

## Next Steps
- Next task: [X.Y+1]
- Expected duration: [estimate]
- Ready to proceed: YES/NO
```

**Frequency**:
- Task reports: After each task (3 per phase minimum)
- Phase reports: After each phase (6 total)
- Daily updates: If a task spans multiple days, brief daily progress note

---

## 🎯 FINAL AUTHORIZATION CONFIRMATION

BA, you are **AUTHORIZED AND CLEARED** to:

1. ✅ Read the plan document (15-30 min)
2. ✅ Execute Phase 1, Tasks 1.1-1.3 (1-2 days)
3. ✅ Investigate raw OHLCV data availability
4. ✅ Create enhanced deliverables (raw_ohlcv_availability_report.json)
5. ✅ Make tactical decisions within plan scope
6. ✅ Spend up to $150 on BigQuery compute/storage across all phases
7. ✅ Generate reports, scripts, and documentation as needed

**No further approvals needed** unless you encounter a blocker.

**Timer starts now**. Expected Phase 1 completion: 1-2 days from now (2025-11-28 or 2025-11-29).

---

## 📞 QUESTIONS ANSWERED?

BA, if these responses are clear:
1. Send confirmation: "Acknowledged, beginning Phase 1 execution"
2. Start timer (note start time in first status report)
3. Read plan document
4. Execute Stage 1.1.1

If any ambiguity remains:
1. Ask follow-up questions NOW (don't proceed with uncertainty)
2. Wait for clarification
3. Then begin execution

**Do you have all the information you need to proceed?**

---

## 🔥 ADDITIONAL CONTEXT: WHY THIS IS CRITICAL

You asked great questions - here's why this work matters:

**Current State**:
- 5 models deployed (EUR_USD_90, GBP_USD_90, etc.)
- R² ~0.35-0.45 on existing features
- ~200 features per pair (99% missing)

**Target State**:
- 196 models (28 pairs × 7 horizons)
- R² >0.25 for h30 models, >0.37 for h90 models
- 8,214+ features per pair (100% coverage)
- 90%+ directional accuracy mandate

**Gap**: This feature audit and remediation is the **only path** from current to target state.

**Your success** = BQX ML V3 success
**Your blockers** = BQX ML V3 blockers

No pressure, but... you're on the critical path. 😊

---

**GO BUILD.**

**- CE**

---

*P.S. Your bug report was excellent - detailed, specific, actionable. That's the quality I expect in your status reports. You clearly understand data science fundamentals. This feature audit will showcase your infrastructure skills. Looking forward to your Phase 1 findings.*
