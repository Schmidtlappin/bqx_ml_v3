# CE Directive: Workspace Archive and Cleanup

**Document Type**: CE DIRECTIVE
**Date**: December 10, 2025 01:35
**From**: Chief Engineer (CE)
**To**: Enhancement Assistant (EA)
**Priority**: MEDIUM
**Action Required**: Organize workspace and archive outdated files

---

## OBJECTIVE

Audit workspace structure and recommend files/directories for archival or cleanup to improve organization and reduce clutter.

---

## SCOPE

### 1. Documentation Cleanup

Review `/docs/` directory:
- Identify outdated documentation
- Find superseded status reports
- Locate duplicate or redundant docs
- Recommend archive candidates

### 2. Script Organization

Review `/scripts/` directory:
- Identify one-time scripts that completed their purpose
- Find deprecated or superseded scripts
- Locate scripts with duplicate functionality
- Recommend consolidation or archival

### 3. Intelligence File Cleanup

Review `/intelligence/` directory:
- Identify outdated analysis files
- Find superseded reports
- Check for stale intermediate files
- Recommend archive candidates

### 4. Communication Archive

Review `/.claude/sandbox/communications/`:
- Old messages that can be archived
- Completed directive chains
- Historical reports for archival

### 5. Data Directory Organization

Review `/data/` directory:
- Intermediate files no longer needed
- Temporary exports
- Debug outputs
- Archive candidates

### 6. Archive Structure

Recommend archive organization:
```
/archive/
├── YYYY-MM-DD_<category>/
│   ├── docs/
│   ├── scripts/
│   ├── data/
│   └── communications/
```

---

## DELIVERABLE

Submit workspace cleanup report with:

1. **Files to Archive** (move to /archive/)
   | Current Path | Description | Archive Path |

2. **Files to Delete** (no archive needed)
   | Path | Reason | Size |

3. **Directories to Consolidate**
   | Source | Target | Reason |

4. **Naming Convention Fixes**
   | Current Name | Recommended Name | Reason |

5. **Recommended Archive Policy**
   - What to archive vs delete
   - Retention periods
   - Naming conventions

6. **Disk Space Impact**
   - Current workspace size
   - Post-cleanup estimate
   - Archive size

---

## EXISTING ARCHIVE

Note: Archive directory exists at `/home/micha/bqx_ml_v3/archive/`

Check existing archives:
- `2025-12-09_preflight_cleanup/`
- Any other archive folders

Ensure new archival follows established patterns.

---

## CONSTRAINTS

- Do NOT delete or move files without explicit approval
- Provide complete file lists for review
- Preserve git history (use git mv for tracked files)
- Do NOT archive active/current files

---

**Chief Engineer (CE)**
**Date**: December 10, 2025 01:35
