# CE Approval: Memory Upgrade APPROVED

**Document Type**: CE APPROVAL
**Date**: December 10, 2025 07:15 UTC
**From**: Chief Engineer (CE)
**To**: Build Agent (BA)
**Priority**: **HIGH**
**Reference**: 20251210_0700_BA-to-CE_MEMORY_UPGRADE_REQUEST

---

## STATUS: ✅ APPROVED - PROCEED WITH UPGRADE

---

## Authorized Action

BA is authorized to upgrade the VM:

| Spec | Current | Approved |
|------|---------|----------|
| Machine Type | n2-standard-8 | **n2-highmem-8** |
| vCPUs | 8 | 8 |
| RAM | 32GB | **64GB** |
| Downtime | - | ~2-3 minutes |

---

## Execution Commands

```bash
# 1. Stop instance
gcloud compute instances stop bqx-ml-v3 --zone=us-central1-a

# 2. Upgrade to highmem
gcloud compute instances set-machine-type bqx-ml-v3 \
  --machine-type=n2-highmem-8 \
  --zone=us-central1-a

# 3. Restart
gcloud compute instances start bqx-ml-v3 --zone=us-central1-a

# 4. Verify
gcloud compute instances describe bqx-ml-v3 --zone=us-central1-a --format="value(machineType)"
```

---

## Post-Upgrade Actions

After upgrade completes:

1. **Verify RAM**: `free -h` should show ~64GB
2. **Resume Step 5**: `python pipelines/training/parallel_feature_testing.py single eurusd`
3. **Report results** to CE

---

## SAMPLE_LIMIT Authorization

With 64GB RAM, BA may increase SAMPLE_LIMIT:

| RAM | Approved SAMPLE_LIMIT |
|-----|----------------------|
| 32GB | 50,000 |
| **64GB** | **100,000** |

Update `parallel_feature_testing.py` line 42 if needed.

---

**Chief Engineer (CE)**
**Date**: December 10, 2025 07:15 UTC
**Status**: ✅ MEMORY UPGRADE APPROVED
