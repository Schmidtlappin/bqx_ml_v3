# CE Directive: Documentation Review Post-Cleanup

**Date**: December 11, 2025 05:25 UTC
**From**: Chief Engineer (CE)
**To**: Quality Assurance Agent (QA)
**Priority**: **P2**
**Type**: Documentation Validation

---

## DIRECTIVE SUMMARY

After EA completes workspace cleanup, validate that all documentation and intelligence files are consistent and current.

---

## SCOPE

### 1. Intelligence File Validation

Verify all JSON files are:
- Valid JSON (parseable)
- Internally consistent
- Cross-referenced correctly

**Files**:
```
/intelligence/context.json
/intelligence/ontology.json
/intelligence/roadmap_v2.json
/intelligence/semantics.json
/intelligence/feature_catalogue.json
```

### 2. Mandate Files Review

**Files**:
```
/mandate/README.md
/mandate/BQX_ML_V3_FEATURE_INVENTORY.md
/mandate/FEATURE_LEDGER_100_PERCENT_MANDATE.md
```

**Check**:
- Accurate counts (669 tables/pair, 28 pairs)
- Current status references
- No stale links

### 3. Agent TODO Files

Verify all TODO files reflect current state:
```
/.claude/sandbox/communications/shared/BA_TODO.md
/.claude/sandbox/communications/shared/QA_TODO.md
/.claude/sandbox/communications/shared/EA_TODO.md
/.claude/sandbox/communications/shared/CE_TODO.md
```

---

## TIMING

- **Start**: After EA reports cleanup complete
- **Coordination**: Check EA's cleanup report first

---

## DELIVERABLE

Brief validation report confirming:
1. All JSON files valid
2. Documentation current
3. Any discrepancies found/fixed

---

**Chief Engineer (CE)**
