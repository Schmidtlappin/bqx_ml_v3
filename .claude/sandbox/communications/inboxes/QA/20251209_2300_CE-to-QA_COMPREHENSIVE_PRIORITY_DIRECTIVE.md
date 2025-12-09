# CE Directive: QA Comprehensive Priority Work Order

**Document Type**: CE PRIORITY DIRECTIVE
**Date**: December 9, 2025
**From**: Chief Engineer (CE)
**To**: Quality Assurance Agent (QA)
**Priority**: EXECUTE SEQUENTIALLY BY PRIORITY

---

## DIRECTIVE

Execute the following tasks in strict priority order. Complete each task before moving to the next. Report completion of each priority level before proceeding.

---

## PRIORITY 1: CRITICAL (Execute When Triggered)

### P1.1: GATE_1 Pre-Flight Validation
**Status**: BLOCKED - Awaiting BA 16/16 completion
**Trigger**: BA reports final 6 VAR tables complete (currently 213/219)

When triggered, execute full GATE_1 validation:

```sql
SELECT
  SUM(CASE WHEN table_name LIKE 'csi%' THEN 1 ELSE 0 END) as csi,
  SUM(CASE WHEN table_name LIKE 'var%' THEN 1 ELSE 0 END) as var,
  SUM(CASE WHEN table_name LIKE 'mkt%' THEN 1 ELSE 0 END) as mkt,
  COUNT(*) as total
FROM `bqx-ml.bqx_ml_v3_features_v2.INFORMATION_SCHEMA.TABLES`
```

**Validation Checklist**:
```
□ CSI tables: 144 ✓ (already complete)
□ VAR tables: 63 (currently 57, +6 pending)
□ MKT tables: 12 ✓ (already complete)
□ Total gap tables: 219
□ Schema compliance (10% sampling)
□ Row counts > 0 (10% sampling)
□ No NULL in interval_time
```

**Success Criteria**:
- All 219 gap tables present
- Schema compliance passes
- Row count validation passes

**Deliverable**: GATE_1 validation report to CE

---

### P1.2: REM-009 Accuracy Baseline Update
**Status**: BLOCKED - Awaiting EA validation confirmation
**Trigger**: EA reports pipeline validation complete

**Files to Update**:
- `/intelligence/roadmap_v2.json`

**Updates Required**:
```json
"current_performance": {
  "validation_date": "2025-12-09",
  "recommended_threshold": 0.80,
  "called_accuracy": [ACTUAL_FROM_EA],
  "coverage": [ACTUAL_FROM_EA],
  "ensemble_size": 3,
  "models": ["LightGBM", "XGBoost", "CatBoost"],
  "enhancements_applied": ["EA-002 (threshold)", "EA-001 (ElasticNet removal)"]
}
```

**Deliverable**: Updated roadmap_v2.json committed

---

## PRIORITY 2: HIGH (After P1 Complete)

### P2.1: Documentation Alignment Audit
**Files to Verify**:
| File | Key Fields |
|------|------------|
| roadmap_v2.json | phase, gap_counts, performance |
| semantics.json | feature counts, table counts |
| feature_catalogue.json | gap_total, feature_total |
| ontology.json | model counts, storage totals |

**Audit Criteria**:
- All counts consistent across files
- Dates current (2025-12-09)
- Status fields accurate
- No contradictions

**Deliverable**: Documentation alignment report

---

### P2.2: Cost Dashboard Validation
**Verify**:
```
□ Monthly storage cost: $35.46 (12.8% of $277 budget)
□ Query cost tracking active
□ Alert thresholds configured (80%/90%/100%)
□ No cost anomalies
```

**Query**:
```sql
SELECT
  table_schema,
  SUM(total_logical_bytes)/1024/1024/1024 as gb,
  SUM(total_logical_bytes)/1024/1024/1024 * 0.02 as monthly_cost
FROM `bqx-ml.region-us-central1.INFORMATION_SCHEMA.TABLE_STORAGE`
WHERE table_schema LIKE 'bqx_ml%'
GROUP BY 1
```

**Deliverable**: Cost verification report

---

### P2.3: QA-BA Progress Tracker Update
**File**: `QA_BA_PROGRESS_TRACKER.md`

**Updates**:
- Update VAR count when BA completes
- Update total percentage
- Update timestamps
- Mark GATE_1 status

**Deliverable**: Updated tracker

---

## PRIORITY 3: MEDIUM (After GATE_1 Passes)

### P3.1: F3b Source Cleanup Coordination
**Status**: After GATE_1 passes
**Scope**: 86 misplaced tables in `bqx_ml_v3_source_v2`

**Action**:
1. List all 86 tables
2. Verify they are duplicates/orphans
3. Create cleanup script (delete list)
4. Submit to CE for approval
5. Execute cleanup after approval

**Deliverable**: Cleanup verification report

---

### P3.2: Weekly Audit Protocol Setup
**Create**: `/intelligence/qa_protocols/weekly_audit.md`

**Protocol Contents**:
```markdown
## Weekly QA Audit Checklist

### Data Quality
□ Table counts match documentation
□ No orphaned tables
□ Schema compliance

### Documentation
□ Intelligence files current
□ No contradictions
□ Version control clean

### Cost
□ Weekly spend within budget
□ No cost anomalies
□ Storage optimized

### Performance
□ Accuracy tracking current
□ No degradation alerts
```

**Deliverable**: Audit protocol document

---

### P3.3: Pre-Phase Gate Template
**Create**: `/intelligence/qa_protocols/gate_template.md`

**Template for Future Gates**:
- GATE_2 (Feature Ledger)
- GATE_3 (Model Training)
- GATE_4 (Production)

**Deliverable**: Gate validation template

---

## PRIORITY 4: NORMAL (Ongoing)

### P4.1: Daily Cost Monitoring
**Frequency**: Daily check
**Action**: Monitor BigQuery costs
**Alert**: If daily spend > $10 or anomaly detected

**Report Format**:
```markdown
## Daily Cost Check - [DATE]
- Query cost: $X.XX
- Storage cost: $X.XX
- Anomalies: None/[Details]
```

---

### P4.2: Weekly Audit Execution
**Frequency**: Weekly (Mondays)
**Scope**: Run weekly audit checklist
**Deliverable**: Weekly audit report to CE

---

### P4.3: BA Progress Monitoring
**Frequency**: Per BA update
**Action**: Update progress tracker
**Alert**: If progress stalls >24 hours

---

### P4.4: Documentation Drift Detection
**Frequency**: Weekly
**Action**: Check for outdated documents
**Alert**: If documents >7 days stale in active phases

---

## PRIORITY 5: LOW (As Capacity Allows)

### P5.1: Historical Audit Archive
**Scope**: Archive completed audit reports
**Deliverable**: Organized audit history

### P5.2: Metrics Dashboard Enhancement
**Scope**: Improve cost/quality dashboards
**Deliverable**: Enhanced reporting

### P5.3: Cross-Agent Validation Protocol
**Scope**: Define QA validation for EA enhancements
**Deliverable**: Cross-validation protocol

---

## EXECUTION CHECKLIST

```
□ P1.1 - GATE_1 validation (when BA completes)
□ P1.2 - REM-009 accuracy baseline (when EA confirms)
□ P2.1 - Documentation alignment audit
□ P2.2 - Cost dashboard validation
□ P2.3 - Progress tracker update
□ P3.1 - F3b cleanup coordination
□ P3.2 - Weekly audit protocol setup
□ P3.3 - Gate template creation
□ P4.1 - Daily cost monitoring
□ P4.2 - Weekly audit execution
□ P4.3 - BA progress monitoring
□ P4.4 - Documentation drift detection
□ P5.1 - Historical audit archive
□ P5.2 - Metrics dashboard enhancement
□ P5.3 - Cross-agent validation protocol
```

---

## REPORTING REQUIREMENTS

| Priority | Report To | Timing |
|----------|-----------|--------|
| P1 | CE | Immediately on completion |
| P2 | CE | Within 1 hour |
| P3 | CE | On completion |
| P4 | CE | Weekly summary |
| P5 | CE | Monthly summary |

---

## SUCCESS METRICS

| Priority | Success Criteria |
|----------|--------------------|
| P1 | GATE_1 passes, baseline updated |
| P2 | All docs aligned, costs verified |
| P3 | F3b cleaned, protocols established |
| P4 | Ongoing monitoring active |
| P5 | Continuous improvement pipeline |

---

## DEPENDENCY MAP

```
BA (6 VAR tables) ──► P1.1 (GATE_1)
                            │
EA (validation)  ──► P1.2 (baseline) ──► P2.x
                            │
                     GATE_1 PASS
                            │
                            ▼
                     P3.x (post-gate)
```

---

**CE Signature**: Claude (Chief Engineer, BQX ML V3)
**Date**: December 9, 2025
**Status**: QA BEGIN P2.x IMMEDIATELY, AWAIT TRIGGERS FOR P1.x
