# CE Directive: Polars Test Artifact Cleanup

**Date**: December 11, 2025 23:42 UTC
**From**: Chief Engineer (CE)
**To**: Build Agent (BA)
**Re**: Cleanup Polars Test Artifacts and Processes
**Priority**: MEDIUM
**Timing**: Execute during Phase 1 (EURUSD BigQuery ETL upload/merge time)
**Session**: 05c73962-b9f1-4e06-9a5a-a5ae556cae5a

---

## DIRECTIVE

**Task**: Clean up all Polars test artifacts, processes, and temporary files from the EURUSD Polars merge test.

**Rationale**: We've pivoted to BigQuery ETL, so Polars test artifacts are no longer needed for production use. Clean up to free disk space (20GB available, need to maximize for 28 BigQuery downloads).

---

## SCOPE

### **1. Polars Test Output File**

**File**: `/home/micha/bqx_ml_v3/data/training/merged/eurusd_merged_training.parquet` (or similar)

**Action**:
- **DO NOT DELETE** - Keep for comparison purposes
- Move to archive location: `/home/micha/bqx_ml_v3/archive/polars_test_20251211/`
- Rename with clear labeling: `eurusd_merged_training_POLARS_TEST_20251211.parquet`
- Document file size and location in cleanup report

**Purpose**: QA will compare Polars vs BigQuery ETL outputs to validate equivalence.

---

### **2. Temporary Polars Files**

**Location**: `/tmp/` or `/home/micha/bqx_ml_v3/temp/`

**Action**:
- Identify any temporary files created during Polars test
  - Look for: `*.tmp`, `*.parquet.tmp`, `polars_*`, etc.
- List all files found (with sizes)
- Delete all temporary files
- Report disk space recovered

**Command**:
```bash
find /tmp /home/micha/bqx_ml_v3/temp -name "*polars*" -o -name "*.tmp" 2>/dev/null
```

---

### **3. Polars Python Processes**

**Action**:
- Check for any lingering Polars processes
- Verify no processes from PID 232011 (the Polars test process) still running
- Kill any orphaned Polars processes (if found)

**Commands**:
```bash
# Check for Polars processes
ps aux | grep -i polars | grep -v grep

# Check for Python processes running merge scripts
ps aux | grep "merge_with_polars" | grep -v grep

# If found, kill gracefully
kill -15 <PID>
```

---

### **4. Polars Installation**

**Action**:
- **DO NOT UNINSTALL** - Keep Polars installed for potential future use
- Document installed version: `pip3 show polars`
- No action needed

---

### **5. Test Scripts and Logs**

**Files**:
- `/home/micha/bqx_ml_v3/scripts/merge_with_polars.py` (test script)
- `/home/micha/bqx_ml_v3/scripts/test_polars_merge.py` (if exists)
- Any test logs in `/home/micha/bqx_ml_v3/logs/polars_*`

**Action**:
- **DO NOT DELETE SCRIPTS** - These are valuable for future reference
- Move scripts to archive: `/home/micha/bqx_ml_v3/archive/polars_test_20251211/scripts/`
- Move logs to archive: `/home/micha/bqx_ml_v3/archive/polars_test_20251211/logs/`
- Keep originals in place (git-tracked files should stay for version control)

---

### **6. Disk Space Audit**

**Before Cleanup**:
```bash
df -h /home/micha/bqx_ml_v3
du -sh /home/micha/bqx_ml_v3/data/training/merged/
```

**After Cleanup**:
```bash
df -h /home/micha/bqx_ml_v3
du -sh /home/micha/bqx_ml_v3/archive/polars_test_20251211/
```

**Report**: Disk space freed (GB)

---

## EXECUTION TIMING

**When**: During Phase 1 EURUSD BigQuery ETL execution (23:45-23:57 UTC)

**Why**: You'll have ~12 minutes of idle time while BigQuery processes the merge query. Use this time productively for cleanup.

**Workflow**:
1. Start EURUSD BigQuery upload (23:45)
2. While upload/merge runs in background → Execute cleanup tasks (23:45-23:57)
3. Download merged output when ready (23:57)
4. Report cleanup results along with Phase 1 completion report

---

## DELIVERABLES

**Cleanup Report** (include in Phase 1 completion report to CE):

**Section**: Polars Test Artifact Cleanup

**Required Info**:
1. ✅ Polars output file archived (location, size)
2. ✅ Temporary files deleted (count, total size freed)
3. ✅ Lingering processes killed (count, PIDs)
4. ✅ Disk space before/after cleanup
5. ✅ Total disk space freed (GB)

**Format**:
```markdown
### Polars Test Artifact Cleanup (Completed 23:55 UTC)

**Polars Output**:
- File: `eurusd_merged_training_POLARS_TEST_20251211.parquet` (9.27 GB)
- Archived to: `/home/micha/bqx_ml_v3/archive/polars_test_20251211/`

**Temporary Files Cleaned**:
- Count: 3 files
- Size: 1.2 GB freed

**Processes**:
- No lingering processes found

**Disk Space**:
- Before: 20.0 GB available
- After: 21.2 GB available
- Freed: 1.2 GB
```

---

## SUCCESS CRITERIA

**Cleanup Complete**:
1. ✅ Polars output archived (not deleted)
2. ✅ All temporary files removed
3. ✅ No lingering processes
4. ✅ Disk space audit complete
5. ✅ Cleanup report included in Phase 1 report

**No Failures**: Cleanup is low-risk, should complete without errors.

---

## COORDINATION

**With EA**: EA is documenting the Polars failure analysis (separate task). BA's cleanup report will provide EA with artifact disposition info.

**With QA**: QA will need the archived Polars output location for comparison validation.

---

**Chief Engineer (CE)**
Session: 05c73962-b9f1-4e06-9a5a-a5ae556cae5a
Priority: MEDIUM (execute during Phase 1 idle time)
Expected Completion: 23:57 UTC (along with Phase 1)
