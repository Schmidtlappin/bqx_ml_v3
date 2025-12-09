# Weekly Audit Protocol - BQX ML V3

**Document Type**: QA OPERATIONAL PROTOCOL
**Created**: December 9, 2025
**Maintained By**: Quality Assurance Agent (QA)
**Version**: 1.0

---

## Purpose

This protocol defines QA's recurring audit schedule for the BQX ML V3 project. Regular audits ensure data quality, cost control, and documentation currency.

---

## Weekly Audit Schedule

### Monday - Cost Audit

| Task | Description | Output |
|------|-------------|--------|
| Run cost query | Check current storage costs | Update Cost Dashboard |
| Compare to budget | Calculate % utilization | Alert if threshold crossed |
| Trend analysis | Compare to previous week | Note anomalies |

**Query**: See [QA_COST_ALERT_DASHBOARD.md](./QA_COST_ALERT_DASHBOARD.md)

### Tuesday - BA Progress Check

| Task | Description | Output |
|------|-------------|--------|
| Count new tables | Check gap remediation progress | Update Progress Tracker |
| Validate schema | Spot-check new tables | Note violations |
| Review BA reports | Check outbox for updates | Respond if needed |

**Query**:
```sql
SELECT
  CASE
    WHEN table_name LIKE 'csi%' THEN 'CSI'
    WHEN table_name LIKE 'var%' THEN 'VAR'
    WHEN table_name LIKE 'mkt%' THEN 'MKT'
  END as category,
  COUNT(*) as count
FROM `bqx-ml.bqx_ml_v3_features_v2.INFORMATION_SCHEMA.TABLES`
WHERE table_name LIKE 'csi%'
   OR table_name LIKE 'var%'
   OR table_name LIKE 'mkt%'
GROUP BY 1
```

### Wednesday - Documentation Sync

| Task | Description | Output |
|------|-------------|--------|
| Review intelligence files | Check for staleness | Flag if >7 days stale |
| Cross-reference counts | Verify alignment | Update if needed |
| README currency | Check root/docs/scripts | Update if stale |

**Files to Check**:
- intelligence/semantics.json
- intelligence/feature_catalogue.json
- intelligence/roadmap_v2.json
- mandate/BQX_ML_V3_FEATURE_INVENTORY.md

### Thursday - EA Coordination

| Task | Description | Output |
|------|-------------|--------|
| Check EA inbox | Review any requests | Respond within 4h |
| Share cost data | If requested | Send via shared folder |
| Optimization review | Review EA proposals | Provide QA assessment |

### Friday - Weekly Summary

| Task | Description | Output |
|------|-------------|--------|
| Compile metrics | Costs, progress, issues | Weekly Report |
| Send to CE | Summary of week | CE inbox |
| Plan next week | Note upcoming gates | Update protocols |

---

## Audit Checklists

### Cost Audit Checklist
- [ ] Run storage cost query
- [ ] Update Cost Dashboard total
- [ ] Check threshold (GREEN/YELLOW/ORANGE/RED)
- [ ] Update cost trend table
- [ ] Alert CE if non-GREEN

### BA Progress Checklist
- [ ] Count CSI/VAR/MKT tables
- [ ] Calculate progress percentages
- [ ] Update Progress Tracker
- [ ] Spot-check schema compliance (3 random tables)
- [ ] Note any naming violations

### Documentation Sync Checklist
- [ ] Check semantics.json last_updated
- [ ] Verify feature counts match BQ
- [ ] Check roadmap phase status
- [ ] Verify README dates
- [ ] Update any stale fields

---

## Reporting Templates

### Weekly Cost Report (Friday)
```markdown
# QA Weekly Cost Report - Week of [DATE]

## Summary
- Current spend: $X.XX
- Budget: $277.00
- Utilization: X%
- Status: [GREEN/YELLOW/ORANGE/RED]

## Week-over-Week Change
- Last week: $X.XX
- This week: $X.XX
- Change: +/-$X.XX (X%)

## Notable Events
- [List any cost changes or alerts]

## Projection
- Next week estimate: $X.XX
```

### Weekly Status Report (Friday)
```markdown
# QA Weekly Status Report - Week of [DATE]

## BA Progress
- CSI: X/144 (X%)
- VAR: X/63 (X%)
- MKT: X/12 (X%)
- Total Gap: X remaining

## Documentation
- Files checked: X
- Issues found: X
- Issues resolved: X

## EA Coordination
- Requests: X
- Completed: X

## Next Week Focus
- [Priority items]
```

---

## Escalation Matrix

| Issue Type | Threshold | Escalate To |
|------------|-----------|-------------|
| Cost alert | YELLOW+ | CE |
| Schema violation | Any | BA, CE |
| Documentation conflict | 3+ files | CE |
| BA stalled | >48h no progress | CE |
| Data quality issue | >5% affected | CE, BA |

---

## Audit Log

| Week | Cost | BA Progress | Docs | Issues |
|------|------|-------------|------|--------|
| 2025-12-09 | GREEN ($35.46) | CSI 100% | Synced | None |

---

## Notes

- All times in UTC
- Audits should complete within 30 minutes each
- Store all reports in QA outbox
- Reference this protocol in all audit outputs

---

*QA Agent - Weekly Protocol v1.0*
