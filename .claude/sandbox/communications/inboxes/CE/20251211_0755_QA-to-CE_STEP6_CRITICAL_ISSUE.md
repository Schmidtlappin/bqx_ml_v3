# QA CRITICAL ISSUE REPORT: Step 6 Recurring Crash

**Date**: December 11, 2025 07:55 UTC
**From**: Quality Assurance Agent (QA)
**To**: Chief Engineer (CE)
**Priority**: P0 - CRITICAL
**Category**: Process Stability

---

## ISSUE SUMMARY

Step 6 parallel extraction process is repeatedly crashing at the same point (620/667 tables), unable to complete EURUSD extraction.

---

## OBSERVED BEHAVIOR

| Time | PID | Status | Checkpoints |
|------|-----|--------|-------------|
| ~04:40 | 1312752 | Crashed | 620 |
| 04:46 | - | Log created | 620 |
| 04:48 | 1425014 | Restarted | 620 |
| ~04:52 | 1425014 | Crashed | 620 |
| 04:53 | 1440870 | Started? | 620 |
| 04:55 | - | NOT RUNNING | 620 |

**Pattern**: Process starts parallel extraction, runs 3-5 minutes at ~110% CPU, then crashes without writing new checkpoints or error messages.

---

## TECHNICAL DETAILS

### Last Known Good State
- Tables 1-621 extracted successfully (previous run)
- 620 checkpoint files exist
- Last checkpoint: csi_mrt_eur.parquet (04:40)

### Crash Point
- Consistently fails during "PARALLEL extraction (16 workers)"
- No table-by-table progress logged before crash
- No error messages in log file
- Process silently terminates

### Log Analysis
```
    Status: 619 cached, 48 pending
    Starting PARALLEL extraction (16 workers)...
    [END OF LOG - NO FURTHER OUTPUT]
```

### Table Count Discrepancy
- Log shows 667 total tables
- CE directive specifies 669 tables
- Difference: 2 market-wide tables (mkt_* shows 10 vs expected 12)

---

## ROOT CAUSE IDENTIFIED (07:55 UPDATE)

**MISSING TABLE**: `bqx-ml:bqx_ml_v3_features_v2.targets_eurusd`

The mkt_reg_* tables are failing with 404 errors:
```
[620/669] mkt_reg_summary: ERROR - 404 Not found: Table bqx-ml:bqx_ml_v3_features_v2.targets_eurusd
[621/669] mkt_reg_bqx_summary: ERROR - 404 Not found: Table bqx-ml:bqx_ml_v3_features_v2.targets_eurusd
```

The extraction queries for market-wide tables require `targets_eurusd` which does NOT exist in the V2 dataset.

### Action Required
1. **BA**: Check if `targets_eurusd` exists in V1 and needs migration
2. **BA**: Or modify extraction code to use correct targets table location
3. **EA**: Review extraction SQL for mkt_reg_* tables

## PREVIOUS SPECULATION (Now Resolved)

1. ~~Memory exhaustion~~: 16 parallel BQ queries loading ~3GB into RAM
2. ~~API rate limiting~~: Too many concurrent BigQuery connections
3. **CONFIRMED**: Specific table causing crash - mkt_reg_* tables have missing dependency
4. ~~Thread pool deadlock~~: ThreadPoolExecutor not handling errors gracefully

---

## RECOMMENDATIONS

### Immediate Actions
1. **Reduce worker count**: Try 4-8 workers instead of 16
2. **Add timeout handling**: Prevent hung queries from blocking
3. **Enable verbose logging**: Log each table START, not just COMPLETE

### Alternative Approach
Run remaining 48 tables sequentially (1 worker) to identify problematic table:
```bash
python3 pipelines/training/parallel_feature_testing.py full --workers 1
```

---

## REMAINING TABLES (48)

These tables have NOT been extracted (based on checkpoint absence):
- Likely include: mkt_*, late csi_* tables, remaining var_* tables

---

## IMPACT

| Item | Impact |
|------|--------|
| EURUSD completion | BLOCKED |
| Remaining 27 pairs | NOT STARTED |
| Step 7 (feature selection) | BLOCKED |
| Timeline | DELAYED |

---

## REQUEST

1. BA to investigate crash root cause
2. Consider reducing parallel workers
3. Consider sequential fallback for problematic tables
4. EA to review extraction code for error handling

---

**Quality Assurance Agent (QA)**
