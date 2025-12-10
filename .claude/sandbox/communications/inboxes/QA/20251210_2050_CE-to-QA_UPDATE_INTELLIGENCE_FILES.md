# CE Directive: Update and Make Current All Intelligence Files

**Document Type**: CE DIRECTIVE
**Date**: December 10, 2025 20:50 UTC
**From**: Chief Engineer (CE)
**To**: QA Agent
**Priority**: **HIGH**
**Subject**: Synchronize Intelligence Files with Current Project State

---

## DIRECTIVE: UPDATE INTELLIGENCE FILES

QA shall audit and update all intelligence files to reflect current project state.

---

## Scope: Intelligence Files to Update

| File | Key Updates Required |
|------|---------------------|
| `intelligence/context.json` | Current phase, pipeline status, feature counts |
| `intelligence/ontology.json` | Model definitions, feature schema |
| `intelligence/roadmap_v2.json` | Pipeline stages, corrected counts |
| `intelligence/semantics.json` | Feature definitions, naming conventions |
| `intelligence/feature_catalogue.json` | 11,337 columns, 1,064 unique features |

---

## Required Updates

### 1. Feature Counts (Corrected 2025-12-10)

| Metric | Old Value | New Value |
|--------|-----------|-----------|
| Total columns per pair | 6,477 | **11,337** |
| Unique features per pair | 399 | **1,064** |
| Tables per pair | - | **462** |

### 2. Pipeline Status

| Stage | Status |
|-------|--------|
| Step 6 (Feature Extraction) | IN PROGRESS |
| Stability Selection | PENDING (pipeline fix required) |
| Training | PENDING (hardcoded features being fixed) |
| SHAP | PENDING |

### 3. Model Status

| Model | Status |
|-------|--------|
| h15_ensemble_v2.joblib (59 features) | OBSOLETE - will be replaced |
| New h15 model (expanded features) | PENDING |

### 4. Pipeline Gaps (Per EA Audit)

Document in relevant intelligence files:
- Step 6 output persistence requirement
- Dynamic feature loading requirement
- Data handoff schema

---

## Validation Checklist

- [ ] All feature counts updated (6,477 → 11,337 / 1,064)
- [ ] Pipeline status current
- [ ] Model status reflects obsolete/pending states
- [ ] No stale references to "59 features" as current
- [ ] Timestamps updated
- [ ] Version numbers incremented

---

## Cross-Reference

Ensure consistency with:
- `mandate/BQX_ML_V3_FEATURE_INVENTORY.md`
- `.claude/sandbox/communications/shared/BA_TODO.md`
- `.claude/sandbox/communications/shared/EA_TODO.md`

---

## Expected Output

QA shall:
1. Audit each intelligence file
2. Apply updates
3. Report changes made to CE

---

**Chief Engineer (CE)**
**Date**: December 10, 2025 20:50 UTC
