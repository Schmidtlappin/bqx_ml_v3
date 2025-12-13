# M008 PHASE 4C READINESS REPORT

**Audit Date**: December 13, 2025 21:45 UTC
**Auditor**: Build Agent (BA)
**Purpose**: Assess execution readiness for M008 Phase 4C (1,968-table remediation)
**Status**: GO/NO-GO Analysis - COMPLETE

---

## EXECUTIVE SUMMARY: ⚠️ **NO-GO FOR DEC 14 START**

### Readiness Assessment

**Can we execute M008 Phase 4C starting Dec 14 with ZERO delays?**

⚠️ **NO** - 3 critical scripts MISSING

**Missing Scripts** (P0-CRITICAL):
1. COV Rename Script (1,596 tables) - 4-6 hours to create
2. LAG Consolidation Script (224→56 tables) - 6-8 hours to create
3. Row Count Validation Tool (consolidation validation) - 1 hour to create

**Total Creation Time**: **11-15 hours**

---

### Recommended Timeline

✅ **REVISED START DATE**: **December 15, 2025**

**Dec 14 (Preparation Day)**:
- BA creates 3 missing scripts (8:00-20:00 UTC, 12 hours)
- EA delivers rename inventory CSV (old → new mappings)
- QA prepares validation protocols
- CE reviews all audit deliverables

**Dec 15 (Execution Start)**:
- Week 1 begins: COV renames + LAG consolidation
- All scripts tested and ready
- **ZERO DELAYS** from this point forward

**Impact**: +1 day to 2-week timeline (acceptable within 2-3 week approval)

---

### Alternative: Partial Start Dec 14

⚠️ **POSSIBLE** but **NOT RECOMMENDED**

**Dec 14 Tasks** (no script dependencies):
- EA investigates 364 primary violations
- BA samples COV tables to determine BQX vs IDX variant
- QA prepares validation checklist

**Blocked Dec 14 Tasks**:
- COV renames (missing script)
- LAG consolidation (missing script)
- Any bulk table operations

**Risk**: Creates execution fragmentation, increases complexity

**CE Decision**: Approve Dec 15 start OR proceed with partial Dec 14 start

---

## PART 1: SCRIPT READINESS FOR PHASE 4C

### Required Scripts for M008 Phase 4C

| Script | Status | Purpose | Tables | Blocker |
|--------|--------|---------|--------|---------|
| **COV Rename** | ❌ MISSING | Add variant ID to COV tables | 1,596 | P0-CRITICAL |
| **LAG Consolidation** | ❌ MISSING | Merge window tables | 224→56 | P0-CRITICAL |
| **Row Count Validator** | ❌ MISSING | Validate LAG consolidation | N/A | P0-CRITICAL |
| **VAR Rename** | ⚠️ ASSESS | Rename VAR tables | 7 | P1-HIGH |
| **execute_m008_table_remediation.py** | ✅ EXISTS | Generic bulk rename | 1,968 | None |
| **View Creation** | ❌ MISSING | Backward compatibility | 1,968 | P2-MEDIUM |
| **Primary Violation** | ⏳ PENDING EA | Address 364 violations | 364 | P1-HIGH |

---

### Script 1: COV Rename (P0-CRITICAL)

**Status**: ❌ **MISSING**

**Required For**: Week 1 - Rename 1,596 COV tables to add variant identifier

**Problem Statement**:
- Current: `cov_agg_eurusd_gbpusd` (MISSING variant)
- Mandated: `cov_agg_{variant}_eurusd_gbpusd` (BQX or IDX)
- **Cannot determine variant from table name alone**

**Script Requirements**:
1. Query INFORMATION_SCHEMA for all `cov_*` tables
2. For each table:
   - Sample 5-10 rows to inspect data
   - Determine variant (BQX if values oscillate around 0, IDX if values ~100)
   - OR: Join with source tables to determine data type
3. Generate rename mapping: `old_name` → `new_name`
4. Execute `ALTER TABLE RENAME` in batches (100-200 per batch)

**Complexity**: **MEDIUM**
- Variant detection logic needed (data sampling or JOIN analysis)
- Batch execution with rollback capability
- Progress tracking and logging

**Estimated Creation Time**: **4-6 hours**
- 2 hours: Script development (variant detection + rename logic)
- 1 hour: Testing on 5-10 sample COV tables
- 1 hour: Dry-run on all 1,596 tables (validation only)
- 2 hours: Full execution (actual renames)

**Dependencies**:
- `google-cloud-bigquery`
- BigQuery write permissions

**Recommended Creation Start**: **Dec 14, 08:00 UTC**

**Estimated Completion**: **Dec 14, 14:00 UTC** (ready for Week 1 execution Dec 15)

---

### Script 2: LAG Consolidation (P0-CRITICAL)

**Status**: ❌ **MISSING**

**Required For**: Week 1-2 - Consolidate 224 LAG tables → 56 tables

**Problem Statement**:
- Current: 4-8 separate tables per (pair, variant): `lag_idx_eurusd_45`, `lag_idx_eurusd_90`, etc.
- Mandated: 1 consolidated table: `lag_idx_eurusd` with all window columns

**Script Requirements**:
1. Query all `lag_*` tables, group by (pair, variant)
2. For each group:
   - Extract window number from table name
   - Read all tables in group
   - Merge on `interval_time` (FULL OUTER JOIN for complete row coverage)
   - Create consolidated table with columns: `interval_time`, `lag_1` through `lag_60`, `window_[w]_lag_[n]` patterns
3. **CRITICAL**: Validate row count preservation before dropping source tables
4. Drop source tables after validation passes
5. **GATE**: Pilot 5 pairs first, validate cost ≤$2/pair

**Complexity**: **HIGH**
- Multi-table merge logic (4-8 tables → 1 table)
- Row count validation CRITICAL (data loss prevention)
- Pilot gate implementation
- Cost tracking per pair

**Estimated Creation Time**: **6-8 hours**
- 3 hours: Script development (complex merge logic)
- 2 hours: Pilot testing (5 pairs: audcad, eurusd, gbpusd, usdjpy, usdchf)
- 1 hour: Validation protocol (row count, schema, null percentage)
- 2 hours: Full execution (56 consolidated tables)

**Dependencies**:
- `google-cloud-bigquery`
- Row count validation tool (see Script 3)

**Cost**: **$5-10** (approved by CE)

**Risk**: **MEDIUM**
- Complex merge logic increases error risk
- Row count validation is CRITICAL (must prevent data loss)
- Pilot gate mitigates risk (validate 5 pairs before full rollout)

**Recommended Creation Start**: **Dec 14, 08:00 UTC** (parallel with COV script)

**Estimated Completion**: **Dec 14, 16:00 UTC** (ready for pilot Dec 15)

---

### Script 3: Row Count Validation Tool (P0-CRITICAL)

**Status**: ❌ **MISSING**

**Required For**: LAG consolidation validation (prevent data loss)

**Problem Statement**:
- LAG consolidation merges 4-8 tables → 1 table
- **MUST** verify: `SUM(source_table_rows) = consolidated_table_rows`
- **Data loss is UNACCEPTABLE**

**Script Requirements**:
```python
def validate_row_counts(source_tables: List[str], dest_table: str):
    """
    Validate row count preservation during table consolidation.

    Args:
        source_tables: List of source table names
        dest_table: Consolidated destination table name

    Raises:
        AssertionError: If row counts don't match
    """
    source_total = 0
    for table in source_tables:
        count = bq_client.query(f"SELECT COUNT(*) as cnt FROM `{table}`").result()
        source_total += list(count)[0].cnt

    dest_count_result = bq_client.query(f"SELECT COUNT(*) as cnt FROM `{dest_table}`").result()
    dest_count = list(dest_count_result)[0].cnt

    assert source_total == dest_count, f"Row count mismatch: {source_total} != {dest_count}"

    return {"source_total": source_total, "dest_count": dest_count, "match": True}
```

**Complexity**: **LOW** (simple SQL COUNT queries)

**Estimated Creation Time**: **1 hour**
- 30 min: Script development
- 30 min: Testing on 3-5 sample tables

**Dependencies**:
- `google-cloud-bigquery`

**Cost**: **$0-1** (COUNT queries are cheap)

**Recommended Creation Start**: **Dec 14, 08:00 UTC**

**Estimated Completion**: **Dec 14, 09:00 UTC** (ready before LAG consolidation testing)

---

### Script 4: VAR Rename (P1-HIGH)

**Status**: ⚠️ **ASSESS** - May be covered by `execute_m008_table_remediation.py`

**Required For**: Week 1-2 - Rename 7 VAR tables (similar to COV issue)

**Problem Statement**:
- EA reported 7 VAR tables with violations
- Likely missing variant identifier (similar to COV)

**Assessment Needed**:
1. Does `execute_m008_table_remediation.py` handle VAR tables?
2. If yes: EA provides rename mapping, generic script executes
3. If no: Create VAR-specific rename script (similar to COV)

**Estimated Creation Time**: **1-2 hours** (if dedicated script needed)

**Alternative**: **Manual rename** (only 7 tables, can be done via BigQuery console if needed)

**Recommended Action**: **ASSESS** Dec 14 AM, decide whether dedicated script needed

---

### Script 5: Generic Bulk Rename (READY)

**Status**: ✅ **EXISTS**

**Script**: `scripts/execute_m008_table_remediation.py`

**Purpose**: Execute bulk table renames from EA's inventory

**Functionality**:
- Reads CSV: `old_name,new_name`
- Executes `ALTER TABLE old_name RENAME TO new_name`
- Batch processing (100-200 tables per batch)
- Rollback capability
- Progress logging

**Blocker**:
- ⚠️ **REQUIRES INPUT**: Rename inventory CSV from EA (not yet delivered)

**EA Deliverable**: Rename inventory for primary violations (364 tables)

**Estimated EA Delivery**: Dec 14-15 (after investigation complete)

**Recommendation**: ✅ **READY** pending EA input

---

### Script 6: View Creation (P2-MEDIUM)

**Status**: ❌ **MISSING**

**Required For**: Week 2 - Create 1,968 backward-compatible views (30-day grace period)

**CE Decision**: Option A (30-day grace) approved

**Problem Statement**:
- After renaming 1,968 tables, old names become invalid
- Downstream queries/notebooks may reference old names
- **30-day grace period** = create views as temporary aliases

**Script Requirements**:
1. Read rename inventory CSV (old_name → new_name)
2. For each renamed table:
   ```sql
   CREATE VIEW `old_name` AS SELECT * FROM `new_name`
   ```
3. Document grace period end date: **Jan 12, 2026**
4. Schedule view deletion (manual or automated)

**Complexity**: **LOW** (straightforward CREATE VIEW statements)

**Estimated Creation Time**: **2-3 hours**
- 1 hour: Script development
- 1 hour: Testing (validate views work correctly)
- 1 hour: Full execution (1,968 views)

**Dependencies**:
- `google-cloud-bigquery`
- Rename inventory CSV (from EA)

**Cost**: **$0** (view creation is metadata operation, no storage cost)

**Priority**: **P2-MEDIUM** (grace period, not critical path)

**Recommended Creation**: **Week 2** (after renames complete)

---

### Script 7: Primary Violation Remediation (PENDING EA)

**Status**: ⏳ **PENDING EA INVESTIGATION**

**Required For**: Week 1-2 (or later, depending on EA findings)

**Problem Statement**:
- EA reported 364 "primary violation" tables
- Root cause unknown (EA investigating Dec 14-15)
- Script requirements depend on investigation findings

**Estimated EA Investigation Completion**: **Dec 15, 2025**

**Script Complexity**: **UNKNOWN** (depends on violation types)

**Estimated Creation Time**: **UNKNOWN** (2-8 hours, depending on complexity)

**Recommendation**: **WAIT** for EA investigation, then assess script needs

---

## PART 2: EXECUTION SEQUENCE & DEPENDENCIES

### Week 1: COV Renames + LAG Consolidation Pilot

**Day 1 (Dec 15)**:
1. ✅ Execute COV rename script (1,596 tables, 4-6 hours)
2. ✅ Execute LAG consolidation pilot (5 pairs, 2 hours)
3. ✅ QA validates pilot results
4. ✅ CE GO/NO-GO decision on full LAG consolidation

**Day 2 (Dec 16)**:
5. ✅ If pilot GO: Execute full LAG consolidation (56 tables, 4-6 hours)
6. ✅ QA validates row counts (100% preservation required)
7. ✅ Drop source LAG tables after validation

**Day 3 (Dec 17)**:
8. ✅ Execute VAR renames (7 tables, 1-2 hours)
9. ✅ Checkpoint: 50% rename completion target
10. ✅ CE review and progress assessment

---

### Week 2: Primary Violations + View Creation

**Day 4-5 (Dec 18-19)**:
11. ✅ EA delivers primary violation investigation (364 tables)
12. ✅ BA assesses script needs (create if needed, 2-8 hours)
13. ✅ Execute primary violation remediation

**Day 6-7 (Dec 20-21)**:
14. ✅ Execute view creation (1,968 views, 2-3 hours)
15. ✅ QA validates backward compatibility (test sample queries)
16. ✅ Document grace period end date: Jan 12, 2026

**Day 8-10 (Dec 22-24)**:
17. ✅ Final QA validation (comprehensive)
18. ✅ EA M008 compliance audit (target: 100%)
19. ✅ CE reviews M008 Phase 4C certificate

**Day 11-14 (Dec 25-28)**: Buffer for unexpected issues

---

## PART 3: DEPENDENCY MATRIX

### Script Dependencies

| Script | Depends On | Delivers To |
|--------|------------|-------------|
| Row Count Validator | None | LAG Consolidation |
| COV Rename | None | Week 1 execution |
| LAG Consolidation | Row Count Validator | Week 1-2 execution |
| VAR Rename | None (or generic script) | Week 1-2 execution |
| Generic Bulk Rename | EA rename inventory | Week 1-2 execution |
| View Creation | Rename inventory | Week 2 execution |
| Primary Violation | EA investigation | Week 2 execution |

---

### Data Dependencies

1. **EA Rename Inventory CSV**: Required for generic bulk rename + view creation
   - Expected delivery: Dec 14-15
   - Format: `old_name,new_name`
   - Count: 364 rows (primary violations) + any additional

2. **COV Variant Detection**: Requires BigQuery data access
   - Sample 5-10 rows per table to determine BQX vs IDX
   - OR: Join with source tables

3. **LAG Source Tables**: Must exist before consolidation
   - 224 tables confirmed to exist
   - Row counts need validation before consolidation

---

## PART 4: COST & TIMELINE ESTIMATES

### Cost Breakdown

| Task | Tables | BigQuery Cost | Time |
|------|--------|---------------|------|
| COV Rename | 1,596 | $0 | 4-6 hours |
| LAG Consolidation Pilot | 10 (5 pairs × 2 variants) | $2-5 | 2 hours |
| LAG Consolidation Full | 56 | $5-10 | 4-6 hours |
| VAR Rename | 7 | $0 | 1-2 hours |
| Primary Violation | 364 | $0-5 | 2-8 hours |
| View Creation | 1,968 | $0 | 2-3 hours |
| **TOTAL** | **4,001** | **$7-20** | **15-27 hours** |

**CE Approved Budget**: $5-15

**Budget Status**: ⚠️ **POSSIBLE OVERRUN** ($7-20 vs $5-15)
- LAG consolidation is the cost driver ($5-10)
- All other operations are metadata ($0-5 total)
- **Mitigation**: Pilot gate validates cost before full rollout

**Recommendation**: CE approve $7-20 revised budget (LAG consolidation cost validated in pilot)

---

### Timeline Estimates

**Aggressive (2 weeks)**:
- Week 1: COV + LAG consolidation + VAR (Dec 15-21)
- Week 2: Primary violations + Views + QA (Dec 22-28)
- Total: **14 days**

**Conservative (3 weeks)**:
- Week 1: COV + LAG pilot + VAR (Dec 15-21)
- Week 2: LAG full + Primary violations (Dec 22-28)
- Week 3: Views + QA + Buffer (Dec 29-Jan 4)
- Total: **21 days**

**Recommended**: **Aggressive (2 weeks)** with 4-day buffer (Dec 25-28 for unexpected issues)

---

## PART 5: RISK ASSESSMENT

### P0-CRITICAL Risks (Prevent Execution)

#### Risk 1: Missing Scripts Not Created on Time

**Probability**: LOW (BA committed to Dec 14 creation)
**Impact**: HIGH (blocks Week 1 execution)
**Mitigation**:
- BA creates scripts Dec 14, 08:00-20:00 UTC (12-hour window)
- QA validates scripts before deployment
- CE approves Dec 15 start only after scripts tested

**Residual Risk**: LOW (12-hour creation window is sufficient)

---

#### Risk 2: LAG Consolidation Pilot Fails

**Probability**: MEDIUM (complex merge logic)
**Impact**: MEDIUM (pivot to Option B: rename LAG tables instead)
**Mitigation**:
- Pilot 5 pairs first (validate before full rollout)
- Row count validation MANDATORY (prevent data loss)
- Rollback capability (keep source tables until validation passes)

**Fallback**: Option B (rename LAG tables, lose architectural benefit but M008 compliant)

**Residual Risk**: LOW (pilot gate + fallback option)

---

### P1-HIGH Risks (Delay but not block)

#### Risk 3: EA Rename Inventory Delayed

**Probability**: MEDIUM (EA investigation in progress)
**Impact**: MEDIUM (delays primary violation remediation)
**Mitigation**:
- Execute COV/LAG/VAR in parallel (not dependent on EA inventory)
- Primary violations can be addressed in Week 2-3 if needed

**Residual Risk**: LOW (can proceed with most of Phase 4C without EA inventory)

---

#### Risk 4: Budget Overrun ($7-20 vs $5-15 approved)

**Probability**: MEDIUM (LAG consolidation cost uncertain)
**Impact**: LOW (budget difference is small, $5-7 overrun)
**Mitigation**:
- LAG pilot validates cost ≤$2/pair (5 pairs = $10 max)
- If pilot cost >$2/pair: Pivot to Option B (rename instead of consolidate)

**Residual Risk**: LOW (pilot gate prevents large overruns)

---

### P2-MEDIUM Risks (Minor delays)

#### Risk 5: View Creation Issues

**Probability**: LOW (straightforward CREATE VIEW)
**Impact**: LOW (grace period, not critical path)
**Mitigation**: Create views in Week 2 (after renames validated)

**Residual Risk**: VERY LOW

---

## PART 6: GO/NO-GO DECISION CRITERIA

### GO Criteria for Dec 15 Start

1. ✅ All 3 P0-CRITICAL scripts created and tested (Dec 14)
2. ✅ BigQuery access validated (write permissions)
3. ✅ QA validation protocols prepared
4. ✅ EA has started investigation of primary violations
5. ✅ BA, EA, QA all staffed and ready

### NO-GO Criteria (Force Delay)

1. ❌ Any P0-CRITICAL script not created by Dec 14 EOD
2. ❌ BigQuery access issues (permissions, quotas)
3. ❌ QA validation protocols not prepared
4. ❌ BA/EA/QA staffing issues

---

## RECOMMENDATIONS

### Recommendation 1: Approve Dec 15 Start Date

**Rationale**:
- Dec 14 is preparation day (create missing scripts)
- Dec 15 start ensures all scripts tested and ready
- +1 day delay is acceptable within 2-3 week approval

**Action**: CE approves revised timeline (Dec 15 start, Dec 28 completion)

---

### Recommendation 2: Approve $7-20 Revised Budget

**Rationale**:
- LAG consolidation cost is $5-10 (validated in pilot)
- All other operations are metadata ($0-5)
- $7-20 is still within reasonable range for 4,001 table operations

**Action**: CE approves $7-20 budget (contingent on pilot validation)

---

### Recommendation 3: Implement LAG Pilot Gate

**Rationale**:
- LAG consolidation is highest risk operation
- Pilot 5 pairs validates cost, complexity, and row count preservation
- GO/NO-GO decision based on pilot results

**Action**: BA executes pilot Dec 15, CE reviews results Dec 15 PM, decision by Dec 16 AM

---

### Recommendation 4: Parallel Script Creation Dec 14

**Rationale**:
- 3 scripts can be created in parallel (COV, LAG, Row Count)
- Total time: 12 hours (with 1-2 hour testing buffer)
- Allows Dec 15 start if all scripts complete

**Action**: BA creates all 3 scripts Dec 14, 08:00-20:00 UTC

---

## FINAL ASSESSMENT

### Readiness Status: ⚠️ **NO-GO FOR DEC 14**

**Blockers**:
- 3 P0-CRITICAL scripts missing (12-hour creation time)

**Revised Start Date**: ✅ **DEC 15, 2025** (after scripts created)

**Completion Date**: ✅ **DEC 28, 2025** (2 weeks from revised start)

**Budget**: ⚠️ **$7-20** (requires CE approval, exceeds $5-15 by $2-5)

**Risk Level**: ⚠️ **MEDIUM** (LAG consolidation complexity, EA dependency)

**Confidence**: ✅ **HIGH** (scripts can be created Dec 14, execution Dec 15-28)

---

## NEXT STEPS (IMMEDIATE)

**Dec 14, 08:00 UTC**: BA starts creating 3 P0-CRITICAL scripts
1. Row Count Validator (1 hour, 08:00-09:00)
2. COV Rename Script (4-6 hours, 08:00-14:00, parallel with #3)
3. LAG Consolidation Script (6-8 hours, 08:00-16:00, parallel with #2)

**Dec 14, 16:00 UTC**: All scripts created, testing begins

**Dec 14, 18:00 UTC**: Scripts tested and validated, ready for deployment

**Dec 14, 20:00 UTC**: CE review of audit deliverables, GO/NO-GO for Dec 15 start

**Dec 15, 08:00 UTC**: M008 Phase 4C execution begins (Week 1 Day 1)

---

**Audit Status**: M008 Phase 4C Readiness **COMPLETE**
**GO/NO-GO Decision**: **NO-GO for Dec 14, GO for Dec 15** (pending script creation)

**Document Updated**: December 13, 2025 21:45 UTC
**Auditor**: Build Agent (BA)
**Deliverable**: 2 of 6 required by CE

---

*End of M008 Phase 4C Readiness Report*
