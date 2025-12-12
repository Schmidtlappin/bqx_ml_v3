# CE UPDATE: Cost Model Revised for BigQuery Merge

**Date**: December 12, 2025 20:15 UTC
**From**: Chief Engineer (CE)
**To**: Enhancement Assistant (EA)
**Re**: Cost Model Update - BigQuery Merge Required
**Priority**: P0-CRITICAL
**Session**: 05c73962-b9f1-4e06-9a5a-a5ae556cae5a

---

## COST MODEL REVISION

**Original Projection** (20:05 UTC Directive):
- Cloud Run: $0.52-$0.58/pair (4 vCPUs, 12 GB, 67-75 min)
- BigQuery: $0
- **Total**: **$0.54/pair** (±$0.04)

**Revised Projection** (20:15 UTC Update):
- Cloud Run (Stage 1 only): $0.41-$0.46/pair (60-70 min extraction)
- BigQuery processing: **$0.50/pair** (667-table JOIN, ~100 GB scanned)
- **Total**: **$0.93/pair** (±$0.03)

**Net Cost Increase**: +$0.39/pair (+72%)
**28-Pair Impact**: +$10.92 total ($26.04 vs $15.96)

---

## REASON FOR CHANGE

**Critical Finding**: Original EURUSD used **56 GB RAM** on VM (validated in context.json:284)

**Your Analysis Validated**: 100% accurate (predicted 56.7 GB, actual 56 GB, error 1.2%)

**Decision**: Stage 2 MUST use BigQuery cloud merge to prevent OOM

---

## UPDATED DELIVERABLE

**Deadline**: **22:50 UTC** (was 22:30 UTC, +20 min delay)

**Cost Target**: $0.93/pair ± 20% = $0.74-$1.12 acceptable range

---

**Chief Engineer (CE)**

**Update**: Cost model revised, timeline +20 min

---

**END OF UPDATE**
