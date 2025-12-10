# QA Weekly Audit Protocol

**Document Type**: QA OPERATIONAL PROTOCOL
**Version**: 1.0
**Created**: December 9, 2025
**Author**: Quality Assurance Agent (QA)
**Frequency**: Weekly (Mondays)

---

## Purpose

Ensure ongoing data quality, documentation alignment, and cost management for BQX ML V3 project.

---

## Weekly Audit Checklist

### 1. Data Quality Audit

#### 1.1 Table Count Verification
```sql
SELECT
  table_schema as dataset,
  COUNT(*) as table_count
FROM `bqx-ml.region-us-central1.INFORMATION_SCHEMA.TABLES`
WHERE table_schema LIKE 'bqx_ml%' OR table_schema LIKE 'bqx_bq%'
GROUP BY 1
ORDER BY 1
```

**Expected Counts** (as of 2025-12-09):
| Dataset | Tables |
|---------|--------|
| bqx_bq_uscen1_v2 | ~2,200 |
| bqx_ml_v3_features_v2 | ~5,100 |
| bqx_ml_v3_analytics_v2 | ~60 |
| bqx_ml_v3_models | TBD |
| bqx_ml_v3_predictions | TBD |

**Action**: Flag if count changes >5% without documented reason

#### 1.2 Schema Compliance (Sampling)
```sql
-- Sample 10 tables from features_v2
SELECT table_name, partition_column
FROM `bqx-ml.bqx_ml_v3_features_v2.INFORMATION_SCHEMA.PARTITIONS`
WHERE partition_column IS NOT NULL
LIMIT 10
```

**Criteria**: All feature tables must be partitioned by DATE(interval_time)

#### 1.3 Empty Table Check
```sql
SELECT
  table_name,
  row_count
FROM `bqx-ml.bqx_ml_v3_features_v2.INFORMATION_SCHEMA.TABLE_STORAGE`
WHERE row_count = 0
```

**Action**: Report any empty tables to CE

#### 1.4 NULL Check (Critical Columns)
```sql
-- Sample check for interval_time NULLs
SELECT table_name
FROM `bqx-ml.bqx_ml_v3_features_v2.INFORMATION_SCHEMA.TABLES`
WHERE table_name IN (
  SELECT DISTINCT table_name
  FROM (
    -- Run for each sampled table
    SELECT 'agg_eurusd' as table_name WHERE EXISTS (
      SELECT 1 FROM `bqx-ml.bqx_ml_v3_features_v2.agg_eurusd`
      WHERE interval_time IS NULL LIMIT 1
    )
  )
)
```

**Criteria**: No NULL values in interval_time

---

### 2. Documentation Alignment

#### 2.1 Intelligence File Consistency

Check for contradictions between:
- `roadmap_v2.json`
- `semantics.json`
- `feature_catalogue.json`
- `ontology.json`

**Key Fields to Verify**:
| File | Field | Expected |
|------|-------|----------|
| roadmap_v2.json | model_count | 784 |
| semantics.json | features_per_model | 6,477 |
| feature_catalogue.json | stable_features | 607 |
| ontology.json | horizons | 7 (h15-h105) |

#### 2.2 Version Control
```bash
git log --oneline -10 intelligence/
```

**Action**: Flag if files >7 days stale during active phases

#### 2.3 Communication Archive
- Archive completed CE/QA/BA/EA communications weekly
- Verify no orphaned action items

---

### 3. Cost Monitoring

#### 3.1 Storage Cost Query
```sql
SELECT
  table_schema as dataset,
  ROUND(SUM(total_logical_bytes)/1024/1024/1024, 2) as gb,
  ROUND(SUM(total_logical_bytes)/1024/1024/1024 * 0.02, 2) as monthly_cost
FROM `bqx-ml.region-us-central1.INFORMATION_SCHEMA.TABLE_STORAGE`
WHERE table_schema LIKE 'bqx_ml%' OR table_schema LIKE 'bqx_bq%'
GROUP BY 1
ORDER BY 3 DESC
```

**Budget**: $277/month
**Alert Thresholds**:
- 80% ($221.60) - Yellow
- 90% ($249.30) - Orange
- 100% ($277.00) - Red

#### 3.2 Query Cost Check
- Review BigQuery job history for the week
- Flag any queries >$1

#### 3.3 Cost Trend Analysis
| Week | Storage GB | Monthly Cost | Trend |
|------|------------|--------------|-------|
| Current | [X] | $[X] | [UP/DOWN/STABLE] |
| Previous | [X] | $[X] | - |

---

### 4. Performance Monitoring

#### 4.1 Accuracy Baseline Check
- Compare current accuracy to baseline (91.66% at τ=0.85)
- Flag if degradation >2%

#### 4.2 Pipeline Health
- Check for failed training jobs
- Check for stale predictions (>24h old)

---

### 5. Security & Access

#### 5.1 IAM Review (Monthly)
- Verify service account permissions
- Check for unused credentials

#### 5.2 Audit Log Review
- Check for unauthorized access attempts
- Review data export logs

---

## Report Template

```markdown
# QA Weekly Audit Report - Week of [DATE]

## Summary
| Category | Status |
|----------|--------|
| Data Quality | [PASS/WARN/FAIL] |
| Documentation | [PASS/WARN/FAIL] |
| Cost | [GREEN/YELLOW/ORANGE/RED] |
| Performance | [PASS/WARN/FAIL] |

## Key Metrics
- Tables: [X]
- Storage: [X] GB
- Monthly Cost: $[X] ([X]% of budget)
- Accuracy: [X]%

## Findings
1. [Finding 1]
2. [Finding 2]

## Actions Required
- [ ] [Action 1]
- [ ] [Action 2]

## Next Week Focus
- [Priority 1]
- [Priority 2]
```

---

## Escalation Matrix

| Issue | Severity | Escalate To | Timeline |
|-------|----------|-------------|----------|
| Data loss | CRITICAL | CE | Immediately |
| Cost >90% | HIGH | CE | Same day |
| Empty tables | MEDIUM | CE | 24 hours |
| Doc drift | LOW | CE | Weekly report |

---

## Execution Schedule

| Task | Day | Time |
|------|-----|------|
| Data quality audit | Monday | AM |
| Documentation check | Monday | AM |
| Cost monitoring | Monday | PM |
| Report submission | Monday | EOD |

---

**QA Agent Signature**: Claude (QA, BQX ML V3)
**Protocol Version**: 1.0
**Effective Date**: December 9, 2025
