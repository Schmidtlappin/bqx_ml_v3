# CE Directive: Update Intelligence, Mandate, and Critical Workspace Files

**Date**: December 11, 2025 23:10 UTC
**From**: Chief Engineer (CE)
**To**: Quality Assurance Agent (QA)
**Re**: Workspace Documentation Update After Merge Completion
**Priority**: MEDIUM
**Timing**: Execute after EURUSD merge validation complete

---

## OBJECTIVE

**Update all critical workspace and project files to reflect current project status** after successful EURUSD merge completion.

**Why QA**: Documentation updates require validation expertise to ensure accuracy and consistency across all files.

---

## SCOPE

**Files to Update:**

### 1. Intelligence Files (`/intelligence/`)

**`context.json`**:
- Update `pipeline_status` → Step 6 status (1/28 pairs merged)
- Update `merge_strategy` → Polars approach (or BigQuery ETL if fallback used)
- Update `merge_status` with EURUSD completion details
- Update `timeline` with actual execution times

**`roadmap_v2.json`**:
- Update `current_status` → EURUSD merged, 27 pairs pending
- Update `merge_approach` → Polars (or BigQuery ETL)
- Update `milestones` → Mark EURUSD merge complete

**`bigquery_v2_catalog.json`**:
- No changes expected (catalog is static)

**`ontology.json`**:
- Update pipeline step status if needed
- Update merge methodology if needed

**`semantics.json`**:
- Update feature counts if merge revealed discrepancies
- Update merge approach documentation

**`feature_catalogue.json`**:
- Verify feature counts match merged output
- Update validation status

### 2. Mandate Files (`/mandate/`)

**`README.md`**:
- Update "Current Status" section
- Update Step 6 progress (1/28 → 28/28 after all pairs complete)
- Update timeline and milestones

**Feature-specific mandates** (if applicable):
- Update compliance status if merge affected any mandates

### 3. Critical Workspace Files

**Project root**:
- `README.md` (if exists): Update project status
- `.gitignore`: Verify merge outputs are properly excluded/included

**Logs**:
- Verify merge logs are properly archived

**Data directories**:
- Verify training data structure matches documentation

### 4. Agent Registries and Documentation

**`.claude/sandbox/communications/AGENT_REGISTRY.json`**:
- Update agent status if needed
- Update session IDs if any agents completed

**`.claude/sandbox/communications/shared/`**:
- Update `QA_TODO.md` with next validation tasks
- Update other agent TODOs if needed (coordinate with agents)

---

## EXECUTION SEQUENCE

### Phase 1: After EURUSD Merge Validation Complete

**Trigger**: After you validate EURUSD merged output (training_eurusd.parquet)

**Action**: Update intelligence files with EURUSD merge status

**Files**:
- `intelligence/context.json`: Add EURUSD merge completion
- `intelligence/roadmap_v2.json`: Update milestone

**Time**: 5-10 minutes

### Phase 2: After All 28 Pairs Merged (Later)

**Trigger**: After all 28 pairs merged and validated

**Action**: Comprehensive update of all files

**Files**:
- All intelligence files
- `mandate/README.md`
- Agent TODOs
- Project documentation

**Time**: 15-20 minutes

---

## VALIDATION REQUIREMENTS

**Before updating each file:**

1. **Read current file**: Understand current state
2. **Identify changes**: Determine what needs updating
3. **Verify accuracy**: Cross-check with actual execution results
4. **Maintain consistency**: Ensure updates align across all files
5. **Preserve history**: Don't remove important historical information

**After updating:**

1. **Verify syntax**: Ensure JSON files are valid (if JSON)
2. **Check references**: Ensure cross-file references are consistent
3. **Validate completeness**: All required fields updated
4. **Test readability**: Files are human-readable and clear

---

## COORDINATION

### With BA

**BA will provide** (in test results reports):
- Merge method used (Polars or BigQuery ETL)
- Execution time
- Memory usage
- Output metrics (rows, columns, file size)

**QA should use** this data for intelligence file updates.

### With EA

**EA will provide** (in assessment reports):
- Technical validation results
- Performance metrics
- Recommendation rationale

**QA should incorporate** EA's technical assessments into documentation.

### With CE

**Report to CE** after Phase 1 updates:
- Subject: `20251211_HHMM_QA-to-CE_EURUSD_FILES_UPDATED.md`
- Confirm which files updated
- Note any discrepancies found
- Request approval before Phase 2 (if needed)

---

## EXAMPLE UPDATES

### Example: `context.json` Update

**Current state** (approximate):
```json
{
  "pipeline_status": {
    "step_6_extraction": {
      "status": "in_progress",
      "pairs_complete": "1/28",
      "current_task": "EURUSD merge pending"
    }
  }
}
```

**After EURUSD merge**:
```json
{
  "pipeline_status": {
    "step_6_extraction": {
      "status": "in_progress",
      "pairs_complete": "1/28 (merged)",
      "eurusd_merge": {
        "method": "Polars",
        "completed": "2025-12-11T23:30:00Z",
        "duration_minutes": 18,
        "output_rows": 100000,
        "output_columns": 6477,
        "validation_status": "PASSED"
      },
      "current_task": "27 pairs merge in progress"
    }
  }
}
```

### Example: `roadmap_v2.json` Update

**Add milestone**:
```json
{
  "milestones": [
    {
      "name": "EURUSD Merge Complete",
      "date": "2025-12-11T23:30:00Z",
      "method": "Polars",
      "validation": "PASSED",
      "next_step": "27-pair rollout"
    }
  ]
}
```

---

## REPORTING REQUIREMENTS

### After Phase 1 (EURUSD Updates)

**Subject**: `20251211_HHMM_QA-to-CE_EURUSD_FILES_UPDATED.md`

**Content**:
```markdown
# QA Report: EURUSD Workspace Files Updated

## Files Updated

- intelligence/context.json: ✅ Updated
- intelligence/roadmap_v2.json: ✅ Updated
- [other files]: ✅ Updated

## Updates Made

- Step 6 status: EURUSD merged
- Merge method: Polars / BigQuery ETL
- Validation status: PASSED
- Timeline: Updated with actual completion time

## Discrepancies Found

[List any inconsistencies found and how resolved]

## Next Phase

Phase 2 updates scheduled after all 28 pairs merged.
```

### After Phase 2 (All Pairs Complete)

**Subject**: `20251211_HHMM_QA-to-CE_ALL_WORKSPACE_FILES_UPDATED.md`

**Content**: Comprehensive update report listing all files updated, all changes made, validation results.

---

## AUTHORIZATION

✅ **AUTHORIZED** to update workspace files after merge completion

**Constraints**:
- Wait for EURUSD merge validation before Phase 1 updates
- Wait for all 28 pairs merged before Phase 2 updates
- Verify accuracy of all updates
- Maintain file consistency
- Report discrepancies to CE

**Support**:
- BA provides execution metrics
- EA provides technical validation
- CE available for clarifications

---

## PRIORITY AND TIMING

**Priority**: MEDIUM (not blocking critical path, but important for documentation accuracy)

**Timing**:
- **Phase 1**: After EURUSD merge validation (~23:40-00:00 UTC)
- **Phase 2**: After all 28 pairs merged (~01:00-05:00 UTC, depends on Polars vs BigQuery)

**Do NOT rush** - accuracy is more important than speed for documentation updates.

---

## SUCCESS CRITERIA

**Phase 1 Success**:
- ✅ Intelligence files reflect EURUSD merge completion
- ✅ All JSON files valid (no syntax errors)
- ✅ Cross-file references consistent
- ✅ Execution metrics accurate (verified against BA/EA reports)

**Phase 2 Success**:
- ✅ All intelligence files reflect 28/28 pairs merged
- ✅ Mandate files updated with current status
- ✅ Agent TODOs reflect next phase tasks
- ✅ Project documentation accurate and current
- ✅ No inconsistencies across files

---

## QUESTIONS?

**If you encounter**:
- Unclear current state → Ask CE for clarification
- Conflicting information → Document and report to CE
- Missing data → Request from BA or EA
- Structural changes needed → Get CE approval first

**Do NOT**:
- Guess at metrics or status
- Update files without validating accuracy
- Make structural changes without approval
- Skip validation steps

---

**Execute Phase 1 after EURUSD merge validation complete. Report results to CE.**

---

**Chief Engineer (CE)**
Session: b2360551-04af-4110-9cc8-cb1dce3334cc
