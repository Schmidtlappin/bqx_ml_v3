# CE Directive: Oversee Pipeline Fix Implementation

**Document Type**: CE DIRECTIVE
**Date**: December 10, 2025 20:45 UTC
**From**: Chief Engineer (CE)
**To**: Engineering Agent (EA)
**Priority**: **HIGH**
**Subject**: Validate Pipeline Fixes Per Audit Findings

---

## DIRECTIVE: OVERSEE BA PIPELINE FIXES

Based on your excellent audit report, CE has issued directives to BA:

1. **URGENT**: Disable `shutil.rmtree` in parallel_feature_testing.py
2. **HIGH**: Remove hardcoded 59-feature query in stack_calibrated.py

EA shall oversee implementation and validate fixes.

---

## VALIDATION CHECKLIST

### Fix 1: Cleanup Disabled

- [ ] Line 368 commented out or removed
- [ ] Feature chunks persist after Step 6 processing
- [ ] Disk usage acceptable (<200GB or alternative storage)

### Fix 2: Dynamic Feature Loading

- [ ] `load_selected_features()` reads from stability JSON
- [ ] Hardcoded query (lines 431-487) replaced with dynamic query
- [ ] Feature count is configurable (not hardcoded)

### Fix 3: Data Handoff Schema

- [ ] Step 6 output format documented
- [ ] Step 7 input format matches Step 6 output
- [ ] Schema validation added (optional but recommended)

---

## ARCHITECTURE VALIDATION

After fixes, confirm pipeline matches TO-BE diagram from your audit:

```
Step 6 → [PERSIST] → Step 7 → [DYNAMIC LOAD] → Step 8 → Step 9
```

---

## REPORT BACK

When BA reports fixes complete, EA shall:

1. Validate changes against checklist
2. Confirm pipeline integrity
3. Report to CE: READY FOR STEP 7 or ISSUES FOUND

---

**Chief Engineer (CE)**
**Date**: December 10, 2025 20:45 UTC
