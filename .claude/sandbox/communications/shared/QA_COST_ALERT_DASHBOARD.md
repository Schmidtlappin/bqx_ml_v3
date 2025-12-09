# Cost Alert Dashboard - BQX ML V3

**Document Type**: QA MONITORING DASHBOARD
**Created**: December 9, 2025
**Maintained By**: Quality Assurance Agent (QA)
**Last Updated**: 2025-12-09 22:15

---

## Budget Overview

| Metric | Value |
|--------|-------|
| Monthly Budget | **$277.00** |
| Current Spend | **$35.46** |
| Budget Used | **12.8%** |
| Status | **GREEN** |

---

## Alert Thresholds

| Level | Threshold | Cost | Action |
|-------|-----------|------|--------|
| GREEN | 0-79% | $0 - $221.59 | Normal operations |
| YELLOW | 80-89% | $221.60 - $249.29 | Inform CE |
| ORANGE | 90-99% | $249.30 - $276.99 | Recommend action |
| RED | 100%+ | $277.00+ | Escalate immediately |

---

## Current Cost Breakdown (2025-12-09)

| Dataset | Tables | Size (GB) | Monthly Cost | % of Budget |
|---------|--------|-----------|--------------|-------------|
| bqx_ml_v3_features_v2 | 5,032 | 1,567.22 | $31.34 | 11.3% |
| bqx_bq_uscen1_v2 | 2,300 | 131.04 | $2.62 | 0.9% |
| bqx_ml_v3_analytics_v2 | 56 | 75.13 | $1.50 | 0.5% |
| **TOTAL** | **7,388** | **1,773.39** | **$35.46** | **12.8%** |

---

## Cost Trend

| Date | Total Cost | Change | Status |
|------|------------|--------|--------|
| 2025-12-09 | $35.46 | - | GREEN |

*Trend tracking started 2025-12-09*

---

## Projected Costs

### Phase 1.5 Completion (16 more tables)

| Addition | Tables | Est. Size (GB) | Est. Cost |
|----------|--------|----------------|-----------|
| VAR tables | 8 | ~10 | +$0.20 |
| MKT tables | 8 | ~5 | +$0.10 |
| **Post-Phase 1.5** | +16 | ~15 | **$35.76** |

**Post-Phase 1.5 Projection**: $35.76/month (12.9% of budget) - GREEN

### Full Model Training (784 models)

| Component | Est. Size (GB) | Est. Cost |
|-----------|----------------|-----------|
| Model artifacts (GCS) | 200 | N/A (GCS) |
| Predictions tables | 500 | +$10.00 |
| Analytics expansion | 200 | +$4.00 |
| **Full Production** | ~700 new | **~$50** total |

**Full Production Projection**: ~$50/month (18% of budget) - GREEN

---

## Alert History

| Date | Level | Message | Resolution |
|------|-------|---------|------------|
| - | - | No alerts recorded | - |

---

## Monitoring Queries

### Check Current Costs
```sql
SELECT
  table_schema as dataset,
  COUNT(*) as tables,
  ROUND(SUM(total_logical_bytes)/1024/1024/1024, 2) as size_gb,
  ROUND(SUM(total_logical_bytes)/1024/1024/1024 * 0.02, 2) as cost_usd
FROM `bqx-ml.region-us-central1.INFORMATION_SCHEMA.TABLE_STORAGE`
WHERE table_schema LIKE 'bqx%_v2'
GROUP BY table_schema
ORDER BY cost_usd DESC
```

### Check Budget Status
```sql
WITH costs AS (
  SELECT
    ROUND(SUM(total_logical_bytes)/1024/1024/1024 * 0.02, 2) as total_cost
  FROM `bqx-ml.region-us-central1.INFORMATION_SCHEMA.TABLE_STORAGE`
  WHERE table_schema LIKE 'bqx%_v2'
)
SELECT
  total_cost,
  277.00 as budget,
  ROUND(total_cost / 277.00 * 100, 1) as pct_used,
  CASE
    WHEN total_cost / 277.00 < 0.80 THEN 'GREEN'
    WHEN total_cost / 277.00 < 0.90 THEN 'YELLOW'
    WHEN total_cost / 277.00 < 1.00 THEN 'ORANGE'
    ELSE 'RED'
  END as status
FROM costs
```

---

## Escalation Procedures

### YELLOW Alert (80%)
1. QA notifies CE via inbox message
2. CE reviews cost drivers
3. No immediate action required

### ORANGE Alert (90%)
1. QA notifies CE with recommended actions
2. Recommended actions:
   - Identify redundant tables for deletion
   - Review partition retention policies
   - Defer non-critical table creation

### RED Alert (100%)
1. QA escalates to CE immediately
2. CE authorizes emergency measures:
   - Pause BA table creation
   - Delete non-essential tables
   - Review project scope

---

## Cost Optimization Opportunities

| Opportunity | Est. Savings | Priority | Status |
|-------------|--------------|----------|--------|
| F3b cleanup (86 misplaced tables) | ~$0.30 | LOW | PENDING |
| Partition retention (90 days) | ~$5.00 | MEDIUM | FUTURE |
| Archive old analytics | ~$1.00 | LOW | FUTURE |

---

## Weekly Check Schedule

| Day | Task | Owner |
|-----|------|-------|
| Monday | Run cost query, update dashboard | QA |
| Friday | Weekly cost report to CE | QA |

---

## Notes

- Storage pricing: $0.02/GB/month (BigQuery active storage)
- Budget includes 50% buffer for unexpected growth
- GCS costs tracked separately (not included here)
- Compute costs (queries) minimal due to slot pricing

---

*QA Agent - Cost Monitoring Active*
