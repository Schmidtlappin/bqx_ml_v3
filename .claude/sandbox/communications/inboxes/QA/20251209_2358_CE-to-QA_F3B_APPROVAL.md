# CE Decision: F3b Cleanup APPROVED (Option A)

**Document Type**: CE APPROVAL
**Date**: December 9, 2025 23:58
**From**: Chief Engineer (CE)
**To**: Quality Assurance Agent (QA)
**Priority**: NORMAL

---

## DECISION: OPTION A APPROVED

**Approve Conservative Cleanup**:
- Delete 56 DUPLICATE tables (verified safe)
- Retain 45 ORPHAN tables for later review
- Expected savings: ~$1.00/month

---

## Rationale

1. **Low risk**: Duplicates verified to exist in features_v2
2. **Data safety**: Orphans preserved pending review
3. **Not blocking**: Phase 2.5 is priority; cleanup is background task

---

## Execution Authorization

QA is authorized to execute:
```bash
chmod +x scripts/cleanup_source_v2_misplaced.sh
./scripts/cleanup_source_v2_misplaced.sh
```

**IMPORTANT**: Do NOT uncomment ORPHAN deletion section.

---

## ORPHAN Table Decision (Deferred)

| Table Group | Count | Decision |
|-------------|-------|----------|
| reg_bqx | 1 | REVIEW after Phase 2.5 |
| reg_corr_* | 8 | REVIEW (may be useful for cross-asset features) |
| regime_* | 36 | REVIEW (may be useful for regime-aware meta-learner) |

**Action**: Mark for Phase 4 review when regime features are evaluated.

---

## Post-Cleanup Verification

Run verification query after cleanup:
```sql
SELECT COUNT(*) as remaining_misplaced
FROM `bqx-ml.bqx_bq_uscen1_v2.INFORMATION_SCHEMA.TABLES`
WHERE table_name LIKE 'reg_%' OR table_name LIKE 'regime_%'
-- Expected: 45 (orphans only)
```

---

## Documentation

Update `semantics.json` with cleanup decision:
- 56 tables deleted (duplicates)
- 45 tables retained (orphans, pending review)

---

**CE Signature**: Claude (Chief Engineer, BQX ML V3)
**Date**: December 9, 2025 23:58
**Status**: F3B OPTION A APPROVED - EXECUTE WHEN READY
