# QA Validation Quick Reference

**Purpose**: Fast reference for validating merged training files

---

## Single Pair Validation

### Command
```bash
python3 /home/micha/bqx_ml_v3/scripts/validate_merged_output.py eurusd
```

### With Custom Expectations
```bash
python3 /home/micha/bqx_ml_v3/scripts/validate_merged_output.py eurusd \
  --expected-rows 100000 \
  --expected-cols 6500
```

### Validation Checks (10 total)
1. ✅ File exists
2. ✅ File readable
3. ✅ Row count (~100K, ±5% tolerance)
4. ✅ Column count (~6,500, ±10% tolerance)
5. ✅ interval_time column present and datetime type
6. ✅ Target columns (49 expected)
7. ✅ No all-null columns
8. ✅ No duplicate column names
9. ✅ Memory usage reasonable (<10GB)
10. ✅ Data types (>95% numeric)

### Exit Codes
- `0`: PASSED or PASSED_WITH_WARNINGS
- `1`: FAILED

---

## Batch Validation (All 28 Pairs)

### Validate All Pairs
```bash
./scripts/validate_all_merged_outputs.sh
```

### Validate Specific Pairs
```bash
./scripts/validate_all_merged_outputs.sh --pairs "eurusd gbpusd usdjpy"
```

### Parallel Validation
```bash
./scripts/validate_all_merged_outputs.sh --parallel 8
```

### Custom Report Directory
```bash
./scripts/validate_all_merged_outputs.sh --report-dir logs/custom_validation
```

### Output
- Summary report: `logs/validation_reports/validation_summary_YYYYMMDD_HHMMSS.md`
- Individual logs: `logs/validation_reports/validation_<pair>_YYYYMMDD_HHMMSS.log`

---

## Common Validation Scenarios

### Scenario 1: EURUSD Merge Just Completed

```bash
# Validate EURUSD immediately
python3 scripts/validate_merged_output.py eurusd

# Check output
echo $?  # 0 = passed, 1 = failed
```

### Scenario 2: 5 Pairs Completed, Batch Validate

```bash
./scripts/validate_all_merged_outputs.sh \
  --pairs "eurusd gbpusd usdjpy audusd usdcad" \
  --parallel 5
```

### Scenario 3: All 28 Pairs Complete, Final Validation

```bash
# Validate all in parallel (4 workers by default)
./scripts/validate_all_merged_outputs.sh

# Or use more workers for speed
./scripts/validate_all_merged_outputs.sh --parallel 8
```

---

## Interpreting Results

### PASSED ✅
- All 10 checks passed
- No errors
- Warnings (if any) are cosmetic
- File ready for training

**Action**: Approve for merge

### PASSED_WITH_WARNINGS ⚠️
- All critical checks passed
- Minor warnings (e.g., column count slightly outside range, some null columns)
- File likely usable for training

**Action**: Review warnings, approve if acceptable

### FAILED ❌
- One or more critical checks failed
- Examples: Missing target columns, duplicate columns, file not readable
- File NOT ready for training

**Action**: Report to CE, investigate root cause

---

## Validation Metrics to Report

After validation, extract these metrics for CE report:

1. **Validation Status**: PASSED / PASSED_WITH_WARNINGS / FAILED
2. **Row Count**: From validation output
3. **Column Count**: From validation output
4. **Target Columns**: Should be 49
5. **File Size (MB)**: From validation output
6. **Validation Time**: From script execution time
7. **Errors**: If any
8. **Warnings**: If any

---

## Example Validation Report to CE

```markdown
# QA Report: EURUSD Merged Output Validation

**Date**: 2025-12-11 23:45 UTC
**Pair**: EURUSD
**Validation Script**: validate_merged_output.py v1.0

## Results

✅ **Overall Status**: PASSED

**Metrics**:
- Rows: 100,000
- Columns: 6,477
- Target columns: 49
- File size: 5,234.56 MB
- Memory usage: 8,756.23 MB

**Validation Checks**: 10/10 PASSED
- ✅ File exists and readable
- ✅ Row count: 100,000 (matches expected)
- ✅ Column count: 6,477 (within range)
- ✅ interval_time column present (datetime64)
- ✅ Target columns: 49 (matches expected)
- ✅ No all-null columns
- ✅ No duplicate column names
- ✅ Memory usage: 8.5 GB (reasonable)
- ✅ Data types: 99.8% numeric
- ✅ No errors detected

**Warnings**: None

**Recommendation**: ✅ APPROVED FOR TRAINING
```

---

## Troubleshooting

### File Not Found
```
Error: File not found: /home/micha/bqx_ml_v3/data/features/training_eurusd.parquet
```
**Cause**: BA merge hasn't completed yet or output path is wrong
**Action**: Wait for BA to report completion

### Memory Error
```
MemoryError: Unable to allocate array
```
**Cause**: Insufficient RAM to load file
**Action**: Close other applications, or use memory_usage check only

### Import Error
```
ModuleNotFoundError: No module named 'pandas'
```
**Cause**: pandas not installed
**Action**: `pip3 install pandas pyarrow`

---

## When to Run Validations

### Immediate (After Each Merge)
- ✅ Validate immediately after BA reports merge completion
- ✅ Report results to CE within 10 minutes

### Batch (After Multiple Merges)
- ✅ Validate in batches of 5-10 pairs for efficiency
- ✅ Use parallel validation (--parallel 4-8)

### Final (After All 28 Pairs)
- ✅ Run comprehensive batch validation
- ✅ Generate summary report for CE
- ✅ Verify 100% pass rate before proceeding to training

---

## Integration with Phase 1 File Updates

**Workflow**:
1. BA reports merge completion → Read metrics
2. QA validates merged output → Extract validation metrics
3. QA updates intelligence files → Use template with actual values
4. QA reports to CE → Confirm Phase 1 complete

**Files**:
- Template: `.claude/sandbox/communications/shared/PHASE1_FILE_UPDATE_TEMPLATE.md`
- Validation script: `scripts/validate_merged_output.py`
- Batch script: `scripts/validate_all_merged_outputs.sh`

---

**Keep this reference handy for fast validation execution.**
