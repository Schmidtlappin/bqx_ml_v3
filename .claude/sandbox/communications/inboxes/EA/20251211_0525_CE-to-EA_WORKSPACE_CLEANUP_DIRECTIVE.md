# CE Directive: Workspace Cleanup & Archive

**Date**: December 11, 2025 05:25 UTC
**From**: Chief Engineer (CE)
**To**: Enhancement Agent (EA)
**Priority**: **P1**
**Type**: Cleanup & Maintenance

---

## DIRECTIVE SUMMARY

Perform comprehensive workspace cleanup while Step 6 runs. Archive stale files, clean artifacts, and update intelligence/documentation.

---

## SCOPE

### 1. PROCESS CLEANUP (Do NOT kill Step 6)

**Active Process** (DO NOT TOUCH):
```
PID 1312752 - parallel_feature_testing.py (Step 6 - RUNNING)
```

**Stale Processes to Kill** (if any):
```bash
# Check for orphaned python processes (NOT PID 1312752)
ps aux | grep python | grep -v grep | grep -v 1312752
```

### 2. LOG FILE CLEANUP

**Location**: `/logs/`
**Current**: 12 files, 412K

**Action**:
| Pattern | Action |
|---------|--------|
| `step6_sequential_*.log` (current) | KEEP |
| `step6_*.log` (old runs) | Archive to `archive/logs_20251211/` |
| `sync_*.log` | Archive |

### 3. COMMUNICATIONS CLEANUP

**Location**: `/.claude/sandbox/communications/`
**Current**: 258 inbox messages

**Action**:
| Folder | Criteria | Action |
|--------|----------|--------|
| `inboxes/*/` | Messages before Dec 10 | Archive to `archive/communications_20251211/` |
| `outboxes/*/` | Messages before Dec 10 | Archive |
| Keep | Today's messages (Dec 11) | RETAIN |
| Keep | All `shared/*.md` | RETAIN |

### 4. CACHE/TEMP CLEANUP

```bash
# Remove Python cache
find /home/micha/bqx_ml_v3 -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find /home/micha/bqx_ml_v3 -name "*.pyc" -delete 2>/dev/null

# Remove any .tmp files
find /home/micha/bqx_ml_v3 -name "*.tmp" -delete 2>/dev/null
```

### 5. DATA ARTIFACTS (CAREFUL)

**DO NOT DELETE**:
- `data/features/checkpoints/` (Step 6 checkpoints)
- `data/features/*.parquet` (production data)

**May Archive** (if >30 days old):
- `data/features/backup_*/`
- `data/raw/*/` (if processed)

---

## INTELLIGENCE FILES UPDATE

### Files to Update

**`/intelligence/context.json`**:
- Update `current_phase` if needed
- Update `last_cleanup_date`: "2025-12-11"
- Add cleanup summary to `recent_activities`

**`/intelligence/roadmap_v2.json`**:
- Verify milestone statuses are current
- Update any stale dates

### Verification Checklist
- [ ] All intelligence files parseable (valid JSON)
- [ ] No stale references to deleted files
- [ ] Dates are current

---

## README UPDATE

**File**: `/mandate/README.md`

Update if needed:
- Current pipeline status
- Recent milestones achieved
- Link to current roadmap

---

## ARCHIVE STRUCTURE

Create dated archive folder:
```
/archive/2025-12-11_session_cleanup/
├── logs/
├── communications/
│   ├── inboxes/
│   └── outboxes/
└── manifest.md  (list of archived items)
```

---

## DELIVERABLES

1. **Archive manifest** - List of all archived files
2. **Cleanup report** to CE - Summary of actions taken
3. **Updated intelligence files** (if changes made)
4. **Disk space recovered** - Before/after comparison

---

## CONSTRAINTS

| DO | DO NOT |
|----|--------|
| Archive old logs | Delete any logs |
| Archive old comms | Delete checkpoints |
| Update JSON files | Modify running process |
| Clean __pycache__ | Touch data/features/ |

---

## REPORT FORMAT

```markdown
## EA Cleanup Report

**Date**: [timestamp]
**Duration**: [X minutes]

### Actions Taken
- Archived X log files
- Archived X communication files
- Cleaned X cache directories
- Updated X intelligence files

### Disk Space
- Before: X GB used
- After: Y GB used
- Recovered: Z MB

### Files Archived
[list or link to manifest]

### Intelligence Updates
[list changes made]
```

---

**Chief Engineer (CE)**
