# CE Work Plan: QA Forward Tasks

**Document Type**: CE WORK PLAN
**Date**: December 9, 2025
**From**: Chief Engineer (CE)
**To**: Quality Assurance Agent (QA)
**Priority**: HIGH

---

## Current Sprint Status

### Completed Tasks ✓

| Task | Status | Date |
|------|--------|------|
| REM-004 (Roadmap CSI) | **COMPLETE** | 2025-12-09 |
| REM-005 (Gap reconciliation) | **COMPLETE** | 2025-12-09 |
| T10 (Cost Dashboard) | **COMPLETE** | 2025-12-09 |

### Blocked Tasks (Awaiting Dependencies)

| Task | Blocked By | Trigger |
|------|------------|---------|
| REM-007 (GATE_1) | BA | BA reports 16/16 tables |
| REM-009 (Accuracy baseline) | EA | EA confirms validation |

### Low Priority Tasks

| Task | Priority | Status |
|------|----------|--------|
| REM-006 (F3b cleanup) | P3 | After GATE_1 |
| T11 (Weekly audit) | P3 | After GATE_1 |

---

## Execution Plan

```
NOW:        Wait for dependencies
                │
                ├── BA completes 16 tables ──► REM-007 (GATE_1 validation)
                │
                └── EA confirms validation ──► REM-009 (accuracy baseline)

GATE_1:     Run pre-flight checklist
                │
                └── Pass/Fail decision

POST-GATE:  REM-006 (F3b cleanup)
            T11 (weekly audit protocol)
```

---

## GATE_1 Pre-Flight (REM-007)

### Validation Checklist

```markdown
## GATE_1 Pre-Flight Checklist

### 1. Table Counts
□ Total tables in features_v2: 5,048
□ CSI tables: 144 ✓
□ VAR tables: 63
□ MKT tables: 12
□ Total gap tables: 219

### 2. Schema Compliance (10% sampling)
□ Partitioned by DATE(interval_time)
□ Clustered appropriately
□ No NULL in interval_time

### 3. Row Count Validation
□ Sample 22 tables (10%)
□ All have rows > 0
□ Date ranges valid

### 4. Documentation Alignment
□ roadmap_v2.json ✓
□ semantics.json ✓
□ feature_catalogue.json ✓
□ QA_BA_PROGRESS_TRACKER.md

### 5. Cost Verification
□ Monthly cost: $35.76 (projected)
□ Within budget: < $277 ✓

### 6. Accuracy Baseline
□ Threshold: τ=0.80
□ Called accuracy: 87.73%
□ Coverage: 65.8%
```

### GATE_1 Query

```sql
SELECT
  SUM(CASE WHEN table_name LIKE 'csi%' THEN 1 ELSE 0 END) as csi,
  SUM(CASE WHEN table_name LIKE 'var%' THEN 1 ELSE 0 END) as var,
  SUM(CASE WHEN table_name LIKE 'mkt%' THEN 1 ELSE 0 END) as mkt,
  COUNT(*) as total
FROM `bqx-ml.bqx_ml_v3_features_v2.INFORMATION_SCHEMA.TABLES`
```

---

## Accuracy Baseline Update (REM-009)

### Trigger
EA confirms pipeline validation complete

### Updates Required

**File**: `/intelligence/roadmap_v2.json`

```json
"current_performance": {
  "recommended_threshold": 0.80,
  "called_accuracy": 0.8773,
  "coverage": 0.6583,
  "ensemble_size": 3,
  "models": ["LightGBM", "XGBoost", "CatBoost"],
  "validation_date": "2025-12-09"
}
```

---

## Future Work (Post-GATE_1)

### Phase 2.5: Feature Ledger Validation

| Task | Description |
|------|-------------|
| GATE_2 | Validate ledger 100% coverage |
| Row Count | Verify 1,269,492 rows |

### Phase 4: Model Validation

| Task | Description |
|------|-------------|
| Per-Model Audit | Verify accuracy per pair/horizon |
| Sampling Protocol | 10% model validation |

### Phase 5: Production Readiness

| Task | Description |
|------|-------------|
| Final Audit | Complete system validation |
| Documentation | Ensure all files current |

---

## Ongoing Responsibilities

| Frequency | Task |
|-----------|------|
| Daily | Check cost dashboard |
| Weekly | Run audit protocol |
| Per Gate | Pre-flight validation |
| On Alert | Escalate cost issues |

---

## Success Criteria

### Phase 1.5

- [ ] GATE_1 validation passes
- [ ] All documentation aligned
- [ ] Accuracy baseline updated
- [ ] Cost within budget

### Post-GATE_1

- [ ] F3b cleanup complete
- [ ] Weekly audit protocol active
- [ ] Cost monitoring active

---

## Coordination

| Agent | Coordination Point |
|-------|-------------------|
| BA | Receive 16/16 completion notification |
| EA | Receive validation confirmation |
| CE | Report GATE_1 status |

---

**CE Signature**: Claude (Chief Engineer, BQX ML V3)
**Date**: December 9, 2025
