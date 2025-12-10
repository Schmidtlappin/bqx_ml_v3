# EA Report: Workspace Archive and Cleanup

**Document Type**: EA CLEANUP REPORT
**Date**: December 10, 2025 01:55
**From**: Enhancement Assistant (EA)
**To**: Chief Engineer (CE)
**Reference**: CE-to-EA_WORKSPACE_ARCHIVE_CLEANUP

---

## Executive Summary

| Directory | Size | Files | Archive Candidates |
|-----------|------|-------|-------------------|
| /docs | 572K | 43 | 30+ |
| /scripts | 2.7M | 80+ | 40+ |
| /intelligence | 636K | 27 | 5 |
| /data | 18M | 1 | 0 (ACTIVE) |
| /archive | 9.9M | - | Already archived |
| /.claude/comms | 2.4M | 163 | 100+ |

**Total Workspace**: ~34MB
**Estimated Post-Cleanup**: ~20MB (40% reduction)

---

## 1. Files to Archive

### /docs/ Directory (Archive 30+ files)

| Current Path | Description | Archive Path |
|--------------|-------------|--------------|
| docs/ARCHITECTURAL_DECISION_LAG_INSIGHT.md | Nov 27 analysis | archive/2025-12-10_docs_cleanup/ |
| docs/BA_IMPLEMENTATION_TRACKING.md | Old BA tracking | archive/2025-12-10_docs_cleanup/ |
| docs/BQX_ML_MIGRATION_EXECUTION_MASTERPLAN.md | V1 migration plan | archive/2025-12-10_docs_cleanup/ |
| docs/BQX_ML_V3_BUILDER_BRIEFING.md | Old briefing | archive/2025-12-10_docs_cleanup/ |
| docs/BQX_ML_V3_BUILDER_CHARGE.md | Superseded by charge docs | archive/2025-12-10_docs_cleanup/ |
| docs/COMPREHENSIVE_CORRELATION_PLAN.md | Old correlation plan | archive/2025-12-10_docs_cleanup/ |
| docs/COMPREHENSIVE_FEATURE_ANALYSIS.md | Old analysis | archive/2025-12-10_docs_cleanup/ |
| docs/CRITICAL_GAPS_EXECUTIVE_SUMMARY.md | Gaps resolved | archive/2025-12-10_docs_cleanup/ |
| docs/DUAL_PROCESSING_VERIFICATION.md | Old verification | archive/2025-12-10_docs_cleanup/ |
| docs/EXTREME_CORRELATION_ANALYSIS_RESULTS.md | Old results | archive/2025-12-10_docs_cleanup/ |
| docs/FEATURE_SELECTION_REQUIREMENTS_ANALYSIS.md | Superseded | archive/2025-12-10_docs_cleanup/ |
| docs/FEATURE_TESTING_AND_OPTIMIZATION_STRATEGY.md | Old strategy | archive/2025-12-10_docs_cleanup/ |
| docs/GAP_REMEDIATION_PLAN.md | Gaps complete | archive/2025-12-10_docs_cleanup/ |
| docs/MODEL_OBJECTIVE_CLARIFICATION.md | Old clarification | archive/2025-12-10_docs_cleanup/ |
| docs/NEXT_STEPS_POST_BREAKTHROUGH.md | Steps taken | archive/2025-12-10_docs_cleanup/ |
| docs/PARADIGM_SHIFT_UPDATE_20241124.md | Old update | archive/2025-12-10_docs_cleanup/ |
| docs/PHASE_25B_REDO_TARGET_CORRELATION.md | Phase complete | archive/2025-12-10_docs_cleanup/ |
| docs/POLYNOMIAL_CORRELATION_ANALYSIS.md | Old analysis | archive/2025-12-10_docs_cleanup/ |
| docs/REAL_DATA_BREAKTHROUGH_CONFIRMATION.md | Old confirmation | archive/2025-12-10_docs_cleanup/ |
| docs/RECOMMENDATION_RATIONALE.md | Old rationale | archive/2025-12-10_docs_cleanup/ |
| docs/REMEDIATION_PLAN.md | Superseded | archive/2025-12-10_docs_cleanup/ |
| docs/SHORT_WINDOW_PREDICTION_STRATEGY.md | Old strategy | archive/2025-12-10_docs_cleanup/ |
| docs/TESTING_METHODOLOGY_AND_RESULTS.md | Old results | archive/2025-12-10_docs_cleanup/ |
| docs/status_reports/*.md | All 5 old reports | archive/2025-12-10_docs_cleanup/status_reports/ |
| docs/incidents/*.md | Old incidents | archive/2025-12-10_docs_cleanup/incidents/ |

**KEEP ACTIVE**:
- docs/README.md
- docs/GCP_COST_ESTIMATE_784_MODELS.md
- docs/roadmap_update_recommendations.md
- docs/BQX_ML_V3_INTELLIGENCE_ARCHITECTURE_GUIDE.md
- docs/BIGQUERY_RESTRUCTURE_PLAN.md
- docs/CATALOG_MANDATE_GAP_ANALYSIS.md

### /scripts/ Directory (Archive 40+ files)

| Current Path | Description | Archive Path |
|--------------|-------------|--------------|
| scripts/complete_task_fields*.py (6 files) | Duplicates | archive/2025-12-10_scripts_cleanup/ |
| scripts/airtable_*.py (8 files) | Airtable scripts | archive/2025-12-10_scripts_cleanup/airtable/ |
| scripts/comprehensive_*_testing.py (6 files) | Old tests | archive/2025-12-10_scripts_cleanup/testing/ |
| scripts/calculate_extreme_correlations.py | One-time | archive/2025-12-10_scripts_cleanup/ |
| scripts/batch_correlation_calculator.py | One-time | archive/2025-12-10_scripts_cleanup/ |
| scripts/archived/* | Already marked | archive/2025-12-10_scripts_cleanup/ |

**KEEP ACTIVE**:
- scripts/README.md
- scripts/bigquery_restructure/*
- scripts/create_all_targets_tables.py
- scripts/cleanup_source_v2_misplaced.sh

### /intelligence/ Directory (Archive 5 files)

| Current Path | Description | Archive Path |
|--------------|-------------|--------------|
| intelligence/airtable_audit_results.json | Old audit | archive/2025-12-10_intel_cleanup/ |
| intelligence/airtable_completeness.json | Old completeness | archive/2025-12-10_intel_cleanup/ |
| intelligence/airtable_standards.json | Old standards | archive/2025-12-10_intel_cleanup/ |
| intelligence/status_mismatches.json | Old mismatches | archive/2025-12-10_intel_cleanup/ |
| intelligence/backup_mandate.json | Old backup | archive/2025-12-10_intel_cleanup/ |

**KEEP ACTIVE**: All other intelligence files (roadmap, semantics, ontology, EA files, etc.)

### Communications (Archive 100+ messages)

| Category | Count | Archive Path |
|----------|-------|--------------|
| Dec 9 messages (pre-2300) | ~80 | archive/2025-12-10_comms_cleanup/20251209/ |
| Active directives | Keep | - |

---

## 2. Files to Delete (No Archive)

| Path | Reason | Size |
|------|--------|------|
| scripts/__pycache__/* | Python cache | ~50KB |
| *.pyc files | Compiled Python | Variable |

**Note**: All other files should be archived, not deleted, to preserve history.

---

## 3. Directories to Consolidate

| Source | Target | Reason |
|--------|--------|--------|
| scripts/archived/ | archive/2025-12-10_scripts_cleanup/ | Consolidate |
| scripts/airtable_loaders/ | archive/2025-12-10_scripts_cleanup/airtable/ | Unused |

---

## 4. Naming Convention Fixes

| Current Name | Recommended Name | Reason |
|--------------|------------------|--------|
| docs/task_description_field_state.txt | Archive | Wrong format, old |
| scripts/comprehensive_triangulation_results.json | Move to data/ or archive | Misplaced |

---

## 5. Recommended Archive Policy

### What to Archive (Not Delete)
- Completed phase artifacts
- Superseded documentation
- One-time scripts after completion
- Old analysis results
- Historical communications (>24 hours old)

### Retention Periods
| Category | Retention | Location |
|----------|-----------|----------|
| Phase artifacts | 90 days | archive/ |
| Communications | 30 days active, then archive | archive/comms/ |
| Scripts | Archive after phase complete | archive/scripts/ |
| Analysis results | 90 days | archive/data/ |

### Naming Conventions
```
archive/YYYY-MM-DD_<category>/
  ├── docs/
  ├── scripts/
  ├── data/
  └── communications/
```

---

## 6. Disk Space Impact

| Metric | Current | Post-Cleanup |
|--------|---------|--------------|
| /docs | 572KB | ~150KB |
| /scripts | 2.7MB | ~500KB |
| /intelligence | 636KB | ~550KB |
| /data | 18MB | 18MB (unchanged) |
| /.claude/comms | 2.4MB | ~500KB |
| **TOTAL** | ~34MB | ~20MB |

**Archive Size Increase**: ~14MB
**Active Workspace Reduction**: ~40%

---

## Implementation Script (Draft)

```bash
# Create archive directory
mkdir -p /home/micha/bqx_ml_v3/archive/2025-12-10_workspace_cleanup/{docs,scripts,intel,comms}

# Archive docs (use git mv for tracked files)
# Archive scripts
# Archive intel
# Archive old communications

# Clean pycache
find /home/micha/bqx_ml_v3 -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
```

---

## Recommendations

### Immediate Actions
1. **Approve archive list** - Review candidates above
2. **Execute cleanup** - EA can run with CE approval
3. **Update .gitignore** - Add archive/ if not present

### Process Improvements
1. **Weekly cleanup** - Archive completed artifacts every Monday
2. **Communication rotation** - Auto-archive messages >7 days
3. **Script retirement** - Archive after phase completion

---

**Enhancement Assistant (EA)**
**Date**: December 10, 2025 01:55
**Status**: CLEANUP AUDIT COMPLETE - AWAITING APPROVAL
