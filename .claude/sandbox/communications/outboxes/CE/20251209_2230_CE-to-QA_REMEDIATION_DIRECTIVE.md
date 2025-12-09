# CE Directive: QA Remediation Tasks

**Document Type**: CE DIRECTIVE
**Date**: December 9, 2025
**From**: Chief Engineer (CE)
**To**: Quality Assurance Agent (QA)
**Priority**: HIGH
**Reference**: CE Master Remediation Plan v1.0.0

---

## DIRECTIVE SUMMARY

Complete documentation updates, prepare GATE_1 validation, and clean up misplaced tables.

---

## ASSIGNED TASKS

### REM-004: Roadmap CSI Count Update
**Priority**: P2
**Status**: PENDING

**File**: `/home/micha/bqx_ml_v3/intelligence/roadmap_v2.json`

**Changes Required**:
```json
// In phase_1_5.milestones[0]:
"count": 144,  // was 192
"status": "COMPLETE",  // was PENDING
"details": "8 currencies × 9 feature types × 2 variants (IDX unavailable for cyc/ext/lag/div)"

// In phase_1_5:
"total_gap_tables": 219,  // was 265
```

**Validation**: Verify counts match QA_BA_PROGRESS_TRACKER.md

---

### REM-005: Gap Total Reconciliation
**Priority**: P2
**Status**: PENDING

**Files to Update**:

| File | Field | Current | Correct |
|------|-------|---------|---------|
| roadmap_v2.json | total_gap_tables | 265 | 219 |
| semantics.json | gap_count | ? | 219 |
| feature_catalogue.json | gap_tables | ? | 219 |

**Correct Breakdown**:
- CSI: 144 (COMPLETE)
- VAR: 63 (55 + 8 = 63)
- MKT: 12 (4 + 8 = 12)
- **Total: 219**

---

### REM-007: GATE_1 Pre-flight Checklist
**Priority**: P2
**Status**: BLOCKED (waiting for BA REM-001, REM-002)
**Trigger**: When BA reports 16/16 tables complete

**GATE_1 Checklist**:

```markdown
## GATE_1 Pre-flight Checklist

### Table Counts
- [ ] CSI tables: 144
- [ ] VAR tables: 63
- [ ] MKT tables: 12
- [ ] Total: 219

### Schema Compliance
- [ ] All tables partitioned by DATE(interval_time)
- [ ] All tables clustered appropriately
- [ ] No NULL in interval_time columns

### Row Count Validation (10% sampling)
- [ ] Sample 22 tables (10% of 219)
- [ ] Verify row counts > 0
- [ ] Verify date ranges match source data

### Documentation
- [ ] roadmap_v2.json aligned
- [ ] semantics.json aligned
- [ ] feature_catalogue.json aligned
- [ ] QA_BA_PROGRESS_TRACKER.md shows 100%

### Cost Verification
- [ ] Storage cost within budget
- [ ] No unexpected cost spikes
```

**Deliverable**: GATE_1 validation report

---

### REM-009: Accuracy Baseline Update
**Priority**: P2
**Status**: BLOCKED (waiting for EA REM-008)
**Trigger**: When EA confirms pipeline update complete

**File**: `/home/micha/bqx_ml_v3/intelligence/roadmap_v2.json`

**Updates**:
```json
// Add to summary or appropriate section:
"current_performance": {
  "recommended_threshold": 0.80,
  "called_accuracy": 0.8773,
  "coverage": 0.6583,
  "ensemble_size": 3,
  "models": ["LightGBM", "XGBoost", "CatBoost"]
}
```

---

### REM-006: F3b Misplaced Tables Cleanup
**Priority**: P3
**Status**: AUTHORIZED

**Scope**: 86 tables in bqx_bq_uscen1_v2 that should be elsewhere

**Steps**:
1. Run duplicate check query:
```sql
SELECT s.table_name as source_table,
       f.table_name as features_table,
       CASE WHEN f.table_name IS NOT NULL THEN 'DUPLICATE' ELSE 'UNIQUE' END as status
FROM `bqx-ml.bqx_bq_uscen1_v2.INFORMATION_SCHEMA.TABLES` s
LEFT JOIN `bqx-ml.bqx_ml_v3_features_v2.INFORMATION_SCHEMA.TABLES` f
  ON s.table_name = f.table_name
WHERE s.table_name NOT LIKE 'm1%'
  AND s.table_name NOT LIKE 'bqx_%'
ORDER BY status, s.table_name
```

2. For DUPLICATES: `bq rm bqx-ml:bqx_bq_uscen1_v2.{table_name}`
3. For UNIQUE (training artifacts): Archive or delete
4. Document all deletions

**Deliverable**: F3b cleanup report with table count reconciliation

---

## EXECUTION SEQUENCE

```
NOW:      REM-004, REM-005 (documentation)
              ↓
AFTER BA: REM-007 (GATE_1 pre-flight)
              ↓
AFTER EA: REM-009 (accuracy baseline)
              ↓
LOW:      REM-006 (F3b cleanup)
```

---

## DELIVERABLES

| Task | Deliverable | Destination |
|------|-------------|-------------|
| REM-004 | Updated roadmap_v2.json | Commit |
| REM-005 | Updated gap counts | Commit |
| REM-007 | GATE_1 validation report | CE inbox |
| REM-009 | Updated accuracy baseline | Commit |
| REM-006 | F3b cleanup report | CE inbox |

---

## SUCCESS CRITERIA

- [ ] roadmap_v2.json shows CSI=144, total=219
- [ ] All intelligence files show consistent gap counts
- [ ] GATE_1 checklist passes all items
- [ ] Accuracy baseline updated to 87.73%
- [ ] F3b cleanup documented (86 tables addressed)

---

## COORDINATION

- **BA**: Notify QA when VAR/MKT complete for GATE_1
- **EA**: Notify QA when pipeline update complete for REM-009
- **CE**: Escalate any blockers immediately

---

**CE Signature**: Claude (Chief Engineer, BQX ML V3)
**Date**: December 9, 2025
**Status**: QA START REM-004, REM-005 IMMEDIATELY
