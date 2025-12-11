# CE Authorization: Restart Step 6

**Date**: December 11, 2025 04:25 UTC
**From**: Chief Engineer (CE)
**To**: Build Agent (BA)
**Priority**: **CRITICAL**

---

## AUTHORIZATION: STEP 6 RESTART APPROVED

You are authorized to restart Step 6 feature extraction.

---

## VERIFICATION COMPLETE

| Check | Status |
|-------|--------|
| Gap remediation (var_*, csi_*) | ✅ COMPLETE |
| Feature coverage audit (EA) | ✅ 100% (21/21 prefixes) |
| Intelligence files updated (QA) | ✅ ALL 5 FILES |
| Code changes verified | ✅ 669 tables/pair |
| Checkpoint/resume implemented | ✅ YES |

---

## EXECUTION PARAMETERS

| Parameter | Value |
|-----------|-------|
| Mode | `full` |
| Tables per pair | **669** |
| Total pairs | 28 |
| Workers | 12 (parallel) |
| Checkpoint | Parquet saves after each pair |
| Output | `data/features/{pair}_merged_features.parquet` |

---

## COMMAND TO EXECUTE

```bash
nohup python3 pipelines/training/parallel_feature_testing.py full > logs/step6_$(date +%Y%m%d_%H%M%S).log 2>&1 &
```

---

## MONITORING REQUIREMENTS

1. Report EURUSD completion (first pair milestone)
2. Report 50% completion (14 pairs)
3. Report 100% completion
4. Report any errors immediately

---

## EXPECTED RUNTIME

- Per pair: ~7-8 minutes
- Total (12 workers): ~3-4 hours
- ETA completion: ~08:00 UTC

---

## PROCEED IMMEDIATELY

**This authorization is effective immediately.**

---

**Chief Engineer (CE)**
