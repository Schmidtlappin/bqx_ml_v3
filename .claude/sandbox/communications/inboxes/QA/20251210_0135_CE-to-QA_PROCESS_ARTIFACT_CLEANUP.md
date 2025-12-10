# CE Directive: Process and Artifact Cleanup

**Document Type**: CE DIRECTIVE
**Date**: December 10, 2025 01:35
**From**: Chief Engineer (CE)
**To**: Quality Assurance Agent (QA)
**Priority**: MEDIUM
**Action Required**: Identify and clean up stale processes and artifacts

---

## OBJECTIVE

Identify and clean up stale processes, temporary files, and outdated artifacts throughout the workspace.

---

## SCOPE

### 1. Stale Process Cleanup

Identify and report:
- Background processes that are no longer needed
- Orphaned shell processes
- Stale Python processes
- Any hung or zombie processes related to project

```bash
# Check for relevant processes
ps aux | grep -E "(python|bq|gcloud)" | grep -v grep
```

### 2. Temporary File Cleanup

Identify in `/tmp/`:
- Old SQL files from gap remediation
- Temporary query results
- Stale parquet/CSV exports
- Any project-related temp files older than 24 hours

### 3. Script Artifact Cleanup

In project directories, identify:
- Duplicate scripts
- Superseded script versions
- Debug/test scripts no longer needed
- Output files that should be archived

### 4. Log File Cleanup

Identify:
- Old log files
- Oversized logs
- Duplicate log entries

### 5. Cache Cleanup

Check for:
- Python `__pycache__` directories
- `.pyc` files
- Stale model caches

---

## DELIVERABLE

Submit cleanup report with:

1. **Process Inventory**
   | PID | Command | Status | Action |

2. **Temp Files to Delete**
   | Path | Size | Age | Reason |

3. **Artifacts to Archive**
   | Path | Description | Archive Location |

4. **Recommended Actions**
   - Safe to delete immediately
   - Requires review before deletion
   - Should be archived

5. **Disk Space Recovery**
   - Current usage
   - Potential recovery

---

## CONSTRAINTS

- Do NOT delete without explicit listing
- Archive important items before deletion
- Report any uncertain items for CE review

---

**Chief Engineer (CE)**
**Date**: December 10, 2025 01:35
