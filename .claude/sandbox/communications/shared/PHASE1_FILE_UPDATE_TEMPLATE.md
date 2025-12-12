# Phase 1 File Update Template - EURUSD Merge Completion

**Purpose**: Quick reference for updating intelligence files after EURUSD merge validation

**Data Sources**:
- BA test results report: `20251211_HHMM_BA-to-CE_POLARS_TEST_RESULTS.md` (or equivalent)
- QA validation results: `validate_merged_output.py` execution output
- EA technical assessment: `20251211_HHMM_EA-to-CE_POLARS_TEST_ASSESSMENT.md` (or equivalent)

---

## 1. intelligence/context.json Updates

### Section: `current_phase.pipeline_status.step_6_feature_extraction`

**Current** (line 224):
```json
"step_6_feature_extraction": "IN PROGRESS - EURUSD complete (667/667 tables, 668 checkpoints)"
```

**After EURUSD Merge**:
```json
"step_6_feature_extraction": "IN PROGRESS - EURUSD merged (1/28 pairs), 27 pairs pending"
```

### Section: `current_phase.merge_strategy` (lines 230-250)

**Updates Needed**:

1. **Line 231** - Update `approach`:
```json
"approach": "{{MERGE_METHOD}}"
```
- Replace {{MERGE_METHOD}} with: "Polars" or "BigQuery ETL" (from BA report)

2. **Line 233** - Update `directive`:
```json
"directive": "CE-to-BA 20251211_2255 POLARS_APPROVED"
```
(or equivalent if BigQuery ETL used)

3. **Line 235** - Update `rationale`:
```json
"rationale": "{{RATIONALE}}"
```
- If Polars: "3-5x faster than pandas (8-20 min/pair), zero BigQuery cost, lazy evaluation"
- If BigQuery ETL: "Reliable fallback, $2.52/28 pairs = $0.09/pair, 6 min/pair"

4. **Line 236-242** - Update `implementation`:
```json
"implementation": {
  "tool": "{{TOOL}}",
  "method": "{{METHOD}}",
  "memory_peak": "{{MEMORY_PEAK_GB}}GB",
  "threads": {{THREADS}},
  "execution_time": "{{EXECUTION_TIME_MIN}} minutes"
}
```
Placeholders:
- {{TOOL}}: "Polars" or "BigQuery"
- {{METHOD}}: "Lazy evaluation with streaming" or "BigQuery ETL with deduplication"
- {{MEMORY_PEAK_GB}}: from BA report (e.g., "38")
- {{THREADS}}: from BA report (e.g., 8)
- {{EXECUTION_TIME_MIN}}: from BA report (e.g., 18)

5. **Line 243-249** - Update `performance_targets` to `performance_actual`:
```json
"performance_actual": {
  "time_eurusd": "{{TIME_EURUSD}} minutes",
  "memory_peak": "{{MEMORY_PEAK}}GB",
  "cost_eurusd": "${{COST}}",
  "estimated_total_time_28_pairs": "{{TOTAL_TIME_HOURS}} hours",
  "estimated_total_cost_28_pairs": "${{TOTAL_COST}}"
}
```

6. **Line 250** - Update `status`:
```json
"status": "EURUSD COMPLETE - 27 pairs pending ({{MERGE_METHOD}})"
```

### NEW Section: Add `eurusd_merge_completion` after line 250

```json
"eurusd_merge_completion": {
  "completed_date": "{{COMPLETION_DATE}}",
  "merge_method": "{{MERGE_METHOD}}",
  "execution_time_minutes": {{EXECUTION_TIME_MIN}},
  "memory_peak_gb": {{MEMORY_PEAK_GB}},
  "cost_dollars": {{COST}},
  "validation_status": "{{VALIDATION_STATUS}}",
  "output_file": "/home/micha/bqx_ml_v3/data/features/training_eurusd.parquet",
  "output_metrics": {
    "rows": {{OUTPUT_ROWS}},
    "columns": {{OUTPUT_COLS}},
    "file_size_mb": {{FILE_SIZE_MB}},
    "target_columns": {{TARGET_COLS}}
  },
  "validation_report": "20251211_HHMM_QA-to-CE_EURUSD_VALIDATION_COMPLETE.md"
}
```

Placeholders:
- {{COMPLETION_DATE}}: ISO 8601 format (e.g., "2025-12-11T23:30:00Z")
- {{MERGE_METHOD}}: "Polars" or "BigQuery ETL"
- {{EXECUTION_TIME_MIN}}: Integer (e.g., 18)
- {{MEMORY_PEAK_GB}}: Integer (e.g., 38)
- {{COST}}: Float (e.g., 0.00 or 0.09)
- {{VALIDATION_STATUS}}: "PASSED" or "PASSED_WITH_WARNINGS"
- {{OUTPUT_ROWS}}: Integer (e.g., 100000)
- {{OUTPUT_COLS}}: Integer (e.g., 6477)
- {{FILE_SIZE_MB}}: Float (e.g., 5234.56)
- {{TARGET_COLS}}: Integer (should be 49)

---

## 2. intelligence/roadmap_v2.json Updates

### Section: `phases.phase_4.pipeline_status` (lines 239-248)

**Update line 240**:
```json
"step_6_feature_extraction": "IN PROGRESS - EURUSD merged (1/28 pairs), 27 pairs pending"
```

**Update line 241**:
```json
"step_6_merge_strategy": "{{MERGE_METHOD}} - EURUSD complete"
```

**Update line 244**:
```json
"merge_approach": "{{MERGE_METHOD}} ({{TIME_PER_PAIR}} min/pair, ${{COST_PER_PAIR}} cost) - {{STATUS}}"
```

Examples:
- Polars: "Polars (8-20 min/pair, $0 cost) - EURUSD COMPLETE, 27 pairs pending"
- BigQuery ETL: "BigQuery ETL (6 min/pair, $0.09 cost) - EURUSD COMPLETE, 27 pairs pending"

### NEW Section: Add to `phases.phase_4.milestones` array (after line 211)

```json
{
  "item": "EURUSD Merge Complete",
  "status": "COMPLETE",
  "details": "{{MERGE_METHOD}}: {{EXECUTION_TIME_MIN}} min, {{MEMORY_PEAK_GB}}GB peak, {{OUTPUT_ROWS}} rows × {{OUTPUT_COLS}} cols",
  "completion_date": "{{COMPLETION_DATE}}",
  "validation": "{{VALIDATION_STATUS}}"
}
```

### NEW Section: Add `eurusd_merge_milestone` to roadmap root (after line 677)

```json
"eurusd_merge_milestone": {
  "date": "{{COMPLETION_DATE}}",
  "method": "{{MERGE_METHOD}}",
  "execution_time_minutes": {{EXECUTION_TIME_MIN}},
  "memory_peak_gb": {{MEMORY_PEAK_GB}},
  "cost_dollars": {{COST}},
  "validation_status": "{{VALIDATION_STATUS}}",
  "output_metrics": {
    "rows": {{OUTPUT_ROWS}},
    "columns": {{OUTPUT_COLS}},
    "target_columns": {{TARGET_COLS}},
    "file_size_mb": {{FILE_SIZE_MB}}
  },
  "next_step": "27-pair rollout using {{MERGE_METHOD}}",
  "estimated_completion": "{{ESTIMATED_28_PAIRS_COMPLETE}}"
}
```

---

## 3. Placeholder Value Sources

### From BA Test Results Report

Expected file: `20251211_HHMM_BA-to-CE_POLARS_TEST_RESULTS.md` (or `_BIGQUERY_TEST_RESULTS.md`)

Extract:
- {{MERGE_METHOD}}: "Polars" or "BigQuery ETL"
- {{EXECUTION_TIME_MIN}}: Integer (execution time in minutes)
- {{MEMORY_PEAK_GB}}: Integer (peak memory usage in GB)
- {{COST}}: Float (cost in dollars, $0.00 for Polars, ~$0.09 for BigQuery ETL)
- {{THREADS}}: Integer (number of parallel workers)
- {{TOOL}}: Same as merge method
- {{METHOD}}: Description of approach

### From QA Validation (validate_merged_output.py)

Extract:
- {{OUTPUT_ROWS}}: Integer (df row count)
- {{OUTPUT_COLS}}: Integer (df column count)
- {{TARGET_COLS}}: Integer (should be 49)
- {{FILE_SIZE_MB}}: Float (file size in MB)
- {{VALIDATION_STATUS}}: "PASSED" or "PASSED_WITH_WARNINGS"

### From EA Technical Assessment

Expected file: `20251211_HHMM_EA-to-CE_POLARS_TEST_ASSESSMENT.md`

Extract:
- {{RATIONALE}}: Why this method succeeded/was chosen
- Validation of BA's metrics
- Technical recommendations for 27-pair rollout

### Computed Values

- {{COMPLETION_DATE}}: ISO 8601 timestamp when BA reported completion
- {{TOTAL_TIME_HOURS}}: {{EXECUTION_TIME_MIN}} × 28 pairs ÷ 60
- {{TOTAL_COST}}: {{COST}} × 28 pairs
- {{TIME_PER_PAIR}}: {{EXECUTION_TIME_MIN}} (for EURUSD)
- {{COST_PER_PAIR}}: {{COST}}
- {{ESTIMATED_28_PAIRS_COMPLETE}}: Add {{TOTAL_TIME_HOURS}} to current time
- {{STATUS}}: "EURUSD COMPLETE, 27 pairs pending"

---

## 4. Update Execution Checklist

### Pre-Update
- [ ] Read BA test results report (has {{MERGE_METHOD}}, {{EXECUTION_TIME_MIN}}, {{MEMORY_PEAK_GB}}, {{COST}})
- [ ] Read QA validation output (has {{OUTPUT_ROWS}}, {{OUTPUT_COLS}}, {{FILE_SIZE_MB}}, {{VALIDATION_STATUS}})
- [ ] Read EA technical assessment (has validation and rationale)
- [ ] Compute derived values ({{TOTAL_TIME_HOURS}}, {{TOTAL_COST}}, {{COMPLETION_DATE}})

### Update context.json
- [ ] Update line 224: step_6_feature_extraction status
- [ ] Update line 231: merge_strategy.approach
- [ ] Update line 233: merge_strategy.directive
- [ ] Update line 235: merge_strategy.rationale
- [ ] Update lines 236-242: merge_strategy.implementation
- [ ] Update lines 243-249: performance_targets → performance_actual
- [ ] Update line 250: merge_strategy.status
- [ ] Add eurusd_merge_completion section after line 250
- [ ] Validate JSON syntax: `python3 -m json.tool intelligence/context.json > /dev/null`

### Update roadmap_v2.json
- [ ] Update line 240: pipeline_status.step_6_feature_extraction
- [ ] Update line 241: pipeline_status.step_6_merge_strategy
- [ ] Update line 244: pipeline_status.merge_approach
- [ ] Add EURUSD merge milestone to phase_4.milestones array
- [ ] Add eurusd_merge_milestone to roadmap root
- [ ] Validate JSON syntax: `python3 -m json.tool intelligence/roadmap_v2.json > /dev/null`

### Post-Update
- [ ] Verify cross-file consistency (merge method same in both files)
- [ ] Verify all placeholders replaced with actual values
- [ ] Verify JSON syntax valid for both files
- [ ] Verify metrics accurate (compare with BA/EA/QA reports)

### Report to CE
- [ ] Create 20251211_HHMM_QA-to-CE_EURUSD_FILES_UPDATED.md
- [ ] List all files updated
- [ ] Summarize changes made
- [ ] Report any discrepancies found
- [ ] Confirm Phase 1 complete

---

## 5. Example Values (Polars Scenario)

If BA reports:
- Method: Polars
- Time: 18 minutes
- Memory: 38GB peak
- Cost: $0.00
- Output: 100,000 rows, 6,477 columns
- QA validation: PASSED

Then:
- {{MERGE_METHOD}} = "Polars"
- {{EXECUTION_TIME_MIN}} = 18
- {{MEMORY_PEAK_GB}} = 38
- {{COST}} = 0.00
- {{OUTPUT_ROWS}} = 100000
- {{OUTPUT_COLS}} = 6477
- {{TOTAL_TIME_HOURS}} = 18 × 28 ÷ 60 = 8.4 hours
- {{TOTAL_COST}} = $0.00
- {{VALIDATION_STATUS}} = "PASSED"
- {{COMPLETION_DATE}} = "2025-12-11T23:30:00Z" (when BA reported)

---

## 6. Example Values (BigQuery ETL Scenario)

If BA reports:
- Method: BigQuery ETL
- Time: 6 minutes
- Memory: N/A (BigQuery serverless)
- Cost: $0.09
- Output: 100,000 rows, 6,477 columns
- QA validation: PASSED

Then:
- {{MERGE_METHOD}} = "BigQuery ETL"
- {{EXECUTION_TIME_MIN}} = 6
- {{MEMORY_PEAK_GB}} = "N/A"
- {{COST}} = 0.09
- {{OUTPUT_ROWS}} = 100000
- {{OUTPUT_COLS}} = 6477
- {{TOTAL_TIME_HOURS}} = 6 × 28 ÷ 60 = 2.8 hours
- {{TOTAL_COST}} = $2.52
- {{VALIDATION_STATUS}} = "PASSED"
- {{COMPLETION_DATE}} = "2025-12-11T23:30:00Z"

---

**This template ensures fast, accurate file updates when BA reports completion.**
