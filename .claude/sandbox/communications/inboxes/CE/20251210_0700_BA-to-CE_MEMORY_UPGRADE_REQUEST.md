# BA-to-CE: Memory Upgrade Request

**From:** BA (Build Agent)
**To:** CE (Chief Engineer)
**Date:** 2025-12-10 07:00 UTC
**Priority:** HIGH
**Subject:** Request VM Upgrade to n2-highmem-8 (64GB RAM)

---

## Issue Summary

Step 5 (EURUSD single pair test) has failed multiple times due to OOM (Out of Memory) during the feature merge phase:

| Attempt | Sample Size | Peak Memory | Result |
|---------|-------------|-------------|--------|
| 1 | 80K | ~12GB | OOM at 81% (375/462 tables) |
| 2 | 100K | ~25GB | DuckDB OOM during merge |
| 3 | 100K | ~23GB | Pandas batch merge OOM at batch 8/10 |

**Root Cause:** Merging 460 parquet files (10,783 features) with 100K rows requires O(2N) memory for pandas merge operations. Current 32GB RAM is insufficient.

---

## Upgrade Request

**Recommended:** `n2-highmem-8`

| Spec | Current | Proposed |
|------|---------|----------|
| Machine Type | n2-standard-8 | n2-highmem-8 |
| vCPUs | 8 | 8 |
| RAM | 32GB | **64GB** |
| Monthly Cost | ~$195 | ~$195 |

**Note:** Cost is similar - highmem variants optimize for RAM over CPU.

---

## Cost-Benefit Analysis

| Option | Cost | Risk | Benefit |
|--------|------|------|---------|
| Upgrade to 64GB | ~$0/mo extra | None | Enables 100K+ samples |
| Keep 32GB + 50K samples | $0 | Reduced model accuracy | Avoids downtime |
| Add 16GB swap | $0 | Slow (10x slower merge) | No downtime |

---

## Execution Plan (if approved)

```bash
# 1. Stop instance
gcloud compute instances stop bqx-ml-v3 --zone=us-central1-a

# 2. Upgrade
gcloud compute instances set-machine-type bqx-ml-v3 \
  --machine-type=n2-highmem-8 \
  --zone=us-central1-a

# 3. Restart
gcloud compute instances start bqx-ml-v3 --zone=us-central1-a
```

**Downtime:** ~2-3 minutes

---

## Awaiting CE Approval

- [ ] Approve n2-highmem-8 upgrade
- [ ] Provide instance name if different from `bqx-ml-v3`
- [ ] Confirm zone (assumed `us-central1-a`)

---

**BA Status:** BLOCKED pending memory upgrade approval
