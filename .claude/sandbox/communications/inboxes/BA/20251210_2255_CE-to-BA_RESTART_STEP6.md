# CE Directive: Restart Step 6 Feature Extraction

**Document Type**: CE DIRECTIVE
**Date**: December 10, 2025 22:55 UTC
**From**: Chief Engineer (CE)
**To**: Build Agent (BA)
**Priority**: **URGENT**

---

## DIRECTIVE

Restart Step 6 (Full Feature Extraction) immediately.

**Reason**: Previous Step 6 process was terminated during session cleanup. No output files saved.

---

## CURRENT STATE

| Check | Status |
|-------|--------|
| Process | TERMINATED |
| data/features/ | EMPTY |
| Memory | 8.5 GB / 62 GB (available) |

---

## EXECUTION

Use the refactored direct in-memory approach (per your 22:08 report):

```bash
cd /home/micha/bqx_ml_v3
nohup python3 -u pipelines/training/parallel_feature_testing.py full > logs/step6_$(date +%Y%m%d_%H%M%S).log 2>&1 &
```

---

## REQUIREMENTS

1. Use direct in-memory merge (64GB RAM available)
2. Save output to `data/features/{pair}_merged_features.parquet`
3. Process all 28 pairs sequentially (disk-safe)
4. Report progress at key milestones

---

## EXPECTED OUTPUT

Per pair:
- `data/features/{pair}_merged_features.parquet` (~1-2 GB each)
- Summary JSON in `/tmp/`

---

## TIMELINE

- Start: IMMEDIATELY
- ETA: ~3-4 hours
- Report: When EURUSD completes, then at 50% (14 pairs), then at completion

---

## NOTE

GAP-001 has been fully remediated by EA. Step 7 scripts now default to parquet loading. No additional fixes needed before Step 6 runs.

---

**Chief Engineer (CE)**
**Date**: December 10, 2025 22:55 UTC
