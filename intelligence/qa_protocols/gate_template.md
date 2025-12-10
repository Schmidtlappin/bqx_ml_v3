# QA Gate Validation Template

**Document Type**: QA GATE TEMPLATE
**Version**: 1.0
**Created**: December 9, 2025
**Author**: Quality Assurance Agent (QA)

---

## Gate Validation Framework

This template defines the standard validation process for all phase gates in BQX ML V3.

---

## Gate Overview

| Gate | Phase | Description | Status |
|------|-------|-------------|--------|
| GATE_1 | 1.5 | Gap Remediation Complete | **PASSED** (2025-12-09) |
| GATE_2 | 2.5 | Feature Ledger Complete | **PASSED** (2025-12-10) |
| GATE_3 | 4 | EURUSD Training Complete | PENDING (awaiting BA) |
| GATE_4 | 5 | Scale to 28 Pairs | PENDING |
| GATE_5 | 6 | Production Ready | PENDING |

---

## Generic Gate Template

### GATE_[N] Validation Checklist

```markdown
# GATE_[N] Validation Report

**Date**: [DATE]
**Phase**: [PHASE_NAME]
**Validator**: Quality Assurance Agent (QA)
**Status**: [PASS/FAIL]

---

## Pre-Gate Verification

| Requirement | Expected | Actual | Status |
|-------------|----------|--------|--------|
| [Req 1] | [Value] | [Value] | [PASS/FAIL] |
| [Req 2] | [Value] | [Value] | [PASS/FAIL] |
| [Req 3] | [Value] | [Value] | [PASS/FAIL] |

---

## Validation Queries

### Query 1: [Description]
```sql
-- Query here
```
Result: [X]
Expected: [Y]
Status: [PASS/FAIL]

### Query 2: [Description]
```sql
-- Query here
```
Result: [X]
Expected: [Y]
Status: [PASS/FAIL]

---

## Documentation Alignment

| File | Status |
|------|--------|
| roadmap_v2.json | [ALIGNED/MISALIGNED] |
| semantics.json | [ALIGNED/MISALIGNED] |
| feature_catalogue.json | [ALIGNED/MISALIGNED] |

---

## Cost Impact

| Metric | Value | Status |
|--------|-------|--------|
| Storage Added | [X] GB | [GREEN/YELLOW/RED] |
| Monthly Cost | $[X] | [GREEN/YELLOW/RED] |
| Budget Used | [X]% | [GREEN/YELLOW/RED] |

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| [Risk 1] | [L/M/H] | [L/M/H] | [Action] |

---

## QA Recommendation

**[APPROVE/REJECT] GATE_[N] PASSAGE**

Rationale: [Explanation]

---

## Next Steps (Upon Approval)

1. [Action 1]
2. [Action 2]
3. [Action 3]

---

**QA Signature**: Claude (QA, BQX ML V3)
**Validation Time**: [TIMESTAMP]
```

---

## GATE_2: Feature Ledger (Phase 2.5)

### Entry Criteria
- GATE_1 passed
- Phase 2.5 scripts created
- Feature selection complete (607 stable features)

### Validation Criteria
| Check | Criteria | Query |
|-------|----------|-------|
| Row Count | 1,269,492 | `SELECT COUNT(*) FROM feature_ledger` |
| NULL Status | 0 | `SELECT COUNT(*) WHERE final_status IS NULL` |
| SHAP Coverage | 100% | All RETAINED features have SHAP |
| SHAP Samples | 100,000+ | Per USER MANDATE |

### Exit Criteria
- Feature ledger generated
- 100% coverage validated
- SHAP values computed
- Documentation updated

### Detailed Spec
See: `/intelligence/qa_protocols/GATE_2_VALIDATION_CRITERIA.md`

---

## GATE_3: Model Training (Phase 3)

### Entry Criteria
- GATE_2 passed
- Training pipeline validated
- Compute resources provisioned

### Validation Criteria
| Check | Criteria | Query |
|-------|----------|-------|
| Model Count | 784 | 28 pairs × 7 horizons × 4 ensemble |
| Base Models | 3 | LightGBM, XGBoost, CatBoost |
| Meta-Learner | 1 | Logistic regression per pair-horizon |
| Accuracy | ≥85% | Called accuracy at recommended τ |
| Coverage | 30-50% | At recommended threshold |

### Exit Criteria
- All 784 models trained
- Accuracy targets met
- Model artifacts stored
- Versioning complete

### Validation Queries
```sql
-- Model count verification
SELECT
  pair,
  horizon,
  COUNT(DISTINCT model_type) as model_types
FROM `bqx-ml.bqx_ml_v3_models.model_registry`
GROUP BY 1, 2
HAVING COUNT(DISTINCT model_type) < 4
-- Expected: 0 rows (all pair-horizons have 4 models)
```

---

## GATE_4: Production Ready (Phase 4)

### Entry Criteria
- GATE_3 passed
- Production infrastructure ready
- Monitoring configured

### Validation Criteria
| Check | Criteria | Query |
|-------|----------|-------|
| Endpoint Health | All healthy | Health check all endpoints |
| Latency | <500ms P95 | 95th percentile response time |
| Error Rate | <0.1% | Errors / Total requests |
| Accuracy | ≥85% | Live accuracy matches training |

### Exit Criteria
- All endpoints deployed
- Monitoring active
- Alerting configured
- Runbook documented

### Validation Tests
```python
# Health check
for endpoint in endpoints:
    response = requests.get(f"{endpoint}/health")
    assert response.status_code == 200

# Latency check
latencies = measure_latencies(1000)
assert np.percentile(latencies, 95) < 500
```

---

## Gate Failure Protocol

### Immediate Actions
1. Document failure reason
2. Notify CE
3. Create remediation plan

### Remediation Process
1. Identify root cause
2. Create fix tasks
3. Implement fixes
4. Re-run validation
5. Submit for re-approval

### Escalation
| Failure Count | Action |
|---------------|--------|
| 1 | Remediate and retry |
| 2 | CE review required |
| 3+ | Project review meeting |

---

## Gate Approval Flow

```
+------------------+
| Pre-Gate Check   |
+--------+---------+
         |
         v
+------------------+
| Run Validation   |
| Queries          |
+--------+---------+
         |
    +----+----+
    |         |
  PASS      FAIL
    |         |
    v         v
+-------+  +--------+
| Draft |  | Create |
| Report|  | Remed. |
+---+---+  | Plan   |
    |      +----+---+
    v           |
+-------+       |
| Submit|       |
| to CE |<------+
+---+---+
    |
    v
+------------------+
| CE Approval      |
+--------+---------+
         |
    +----+----+
    |         |
APPROVE    REJECT
    |         |
    v         v
+-------+  +--------+
| Update|  | Revise |
| Docs  |  | Plan   |
+-------+  +--------+
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-12-09 | Initial template |

---

**QA Agent Signature**: Claude (QA, BQX ML V3)
**Template Version**: 1.0
**Effective Date**: December 9, 2025
