# Containerized Pipeline: Data Flow & Cost Analysis

## Current Configuration Data Flow

### Option 1: Local Disk (Current docker-compose.yml)

**Data Flow**:
```
BigQuery Tables
    ↓ (extraction via container)
Local VM Disk: /home/micha/bqx_ml_v3/data/features/checkpoints/{pair}/
    ↓ (668 parquet files per pair, ~12 GB)
    ↓ (container uploads to GCS)
GCS Staging: gs://bqx-ml-staging/{pair}/
    ↓ (BigQuery loads from GCS)
BigQuery Temp Tables: bqx_ml_v3_staging.{pair}_*
    ↓ (iterative JOIN merge in BigQuery)
BigQuery Final: bqx_ml_v3_models.training_{pair}
    ↓ (export to GCS)
GCS Output: gs://bqx-ml-output/training_{pair}.parquet
    ↓ (container downloads)
Local VM Disk: /home/micha/bqx_ml_v3/data/training/training_{pair}.parquet
    ↓ (cleanup)
Delete: checkpoints, GCS staging, BigQuery temp tables
```

**Volume Mounts** (docker-compose.yml):
```yaml
volumes:
  # Container writes to host filesystem via bind mounts
  - ./data/features/checkpoints:/workspace/data/features/checkpoints:rw
  - ./data/training:/workspace/data/training:rw
```

**Storage Locations**:
- ✅ **Checkpoints**: Local VM disk (12 GB per pair, deleted after merge)
- ✅ **Training files**: Local VM disk (0.6-1 GB per pair, permanent)
- ⚠️ **GCS**: Temporary staging only (deleted after merge)
- ⚠️ **BigQuery**: Temporary tables only (deleted after merge)

**Disk Space Requirements**:
- Active checkpoints: 12 GB (1 pair at a time)
- Completed training files: 27 × 0.6 GB = 16.2 GB (permanent)
- Peak usage: 12 + 16.2 = **28.2 GB**
- Available: 31 GB
- **Margin**: 2.8 GB (TIGHT but safe with sequential processing)

---

## Alternative: Direct GCS Storage

### Option 2: GCS-First (Modified Approach)

**Data Flow**:
```
BigQuery Tables
    ↓ (extraction via container, writes directly to GCS)
GCS Staging: gs://bqx-ml-staging/{pair}/
    ↓ (668 parquet files per pair, ~12 GB)
    ↓ (BigQuery loads from GCS)
BigQuery Temp Tables: bqx_ml_v3_staging.{pair}_*
    ↓ (iterative JOIN merge in BigQuery)
BigQuery Final: bqx_ml_v3_models.training_{pair}
    ↓ (export to GCS)
GCS Output: gs://bqx-ml-output/training_{pair}.parquet
    ↓ (container downloads to local, optional)
Local VM Disk: /home/micha/bqx_ml_v3/data/training/training_{pair}.parquet (optional)
    ↓ (cleanup)
Delete: GCS staging, BigQuery temp tables (keep GCS output)
```

**Required Modification**:
```python
# In pipelines/training/parallel_feature_testing.py
# Change from:
output_path = f"/workspace/data/features/checkpoints/{pair}/{table_name}.parquet"

# To:
output_path = f"gs://bqx-ml-staging/{pair}/{table_name}.parquet"
```

**Storage Locations**:
- ✅ **Checkpoints**: GCS (12 GB per pair, deleted after merge)
- ✅ **Training files**: GCS permanent + Local VM optional
- ✅ **Local disk**: Minimal (only final training files if downloaded)

**Disk Space Requirements**:
- Active checkpoints: 0 GB (on GCS)
- Completed training files: 0-16.2 GB (optional download)
- Peak usage: **0-16.2 GB** (vs 28.2 GB current)
- **Margin**: 14.8-31 GB (EXCELLENT)

**Benefits**:
- ✅ No local disk constraint (enables parallel pair processing)
- ✅ Data already in GCS (no upload step needed)
- ✅ Faster merge (BigQuery loads from GCS directly)
- ✅ Persistent checkpoints (can re-merge without re-extracting)

---

## Cost Analysis: Local Disk vs GCS

### Option 1: Local Disk (Current)

#### Per Pair Costs

**Extraction** (BigQuery query):
- Bytes scanned: ~50 GB
- Cost: $0.00 (batch load queries are free)

**GCS Staging Upload**:
- Data uploaded: 12 GB
- Cost: $0.00 (free ingress)

**GCS Staging Storage**:
- Size: 12 GB
- Duration: ~1 hour
- Cost: $0.026/GB/month × 12 GB × (1h/730h) = **$0.0004**

**BigQuery Load**:
- Load jobs: 668 files
- Cost: $0.00 (batch load is free)

**BigQuery Merge**:
- Query cost: ~14 queries (iterative JOIN batches)
- Bytes processed: ~50 GB
- Cost: $5/TB × 0.05 TB = $0.25
- With free tier (1 TB/month): **$0.00-0.25**

**BigQuery Temp Storage**:
- Size: ~12 GB
- Duration: ~1 hour
- Cost: $0.02/GB/month × 12 GB × (1h/730h) = **$0.0003**

**GCS Output**:
- Export: $0.00 (free)
- Storage: 0.6 GB × $0.026/GB/month × (permanent) = $0.016/month
- Download: $0.00 (free egress within same region)

**Total Per Pair**: **$0.00-0.27** (depends on BigQuery free tier)

#### 27 Pairs Total

**Extraction**: $0.00
**GCS Staging**: 27 × $0.0004 = $0.01
**BigQuery Merge**: 27 × $0.11 = $2.97 (assuming free tier used)
**BigQuery Temp Storage**: 27 × $0.0003 = $0.01
**GCS Output Storage**: 27 × $0.016 = $0.43/month (permanent)

**Total One-Time**: **$2.99**
**Total Recurring**: **$0.43/month** (GCS output storage)

---

### Option 2: GCS-First (Direct Write)

#### Per Pair Costs

**Extraction** (BigQuery query to GCS):
- Bytes scanned: ~50 GB
- Cost: $0.00 (batch queries free)

**GCS Staging Write**:
- Data written: 12 GB
- Cost: $0.00 (free ingress)

**GCS Staging Storage**:
- Size: 12 GB
- Duration: ~1 hour (if deleted after merge)
- Cost: $0.026/GB/month × 12 GB × (1h/730h) = **$0.0004**
- OR: Permanent (if kept for re-merge): $0.026/GB/month × 12 GB = **$0.31/month**

**BigQuery Load**:
- Load jobs: 668 files from GCS
- Cost: $0.00 (batch load free)

**BigQuery Merge**:
- Same as Option 1: **$0.00-0.25**

**BigQuery Temp Storage**:
- Same as Option 1: **$0.0003**

**GCS Output**:
- Export: $0.00
- Storage: 0.6 GB × $0.026/GB/month = **$0.016/month**

**Total Per Pair** (delete checkpoints): **$0.00-0.27**
**Total Per Pair** (keep checkpoints): **$0.31-0.56/month**

#### 27 Pairs Total

**One-Time Costs** (delete checkpoints after merge):
- Extraction: $0.00
- GCS Staging: 27 × $0.0004 = $0.01
- BigQuery Merge: 27 × $0.11 = $2.97
- BigQuery Temp: 27 × $0.0003 = $0.01
- **Total**: **$2.99**

**Recurring Costs** (keep checkpoints for re-merge):
- GCS Checkpoints: 27 × 12 GB × $0.026/GB/month = **$8.42/month**
- GCS Training Files: 27 × 0.6 GB × $0.026/GB/month = **$0.43/month**
- **Total**: **$8.85/month**

**Recurring Costs** (delete checkpoints, keep training files only):
- GCS Training Files: **$0.43/month**

---

## Container Compute Costs

### Running on Local VM (Current)

**VM Cost**: Already paying for VM, no additional cost
**Container Overhead**: ~5% CPU, 200-500 MB memory
**Additional Cost**: **$0.00**

**Rationale**: Container runs on existing VM, no new infrastructure

---

### Running on Cloud Run (Alternative)

**Cloud Run Pricing**:
- CPU: $0.00002400/vCPU-second
- Memory: $0.00000250/GiB-second
- Requests: $0.40/million

**Per Pair** (120 min execution):
- vCPU: 2 cores × 7200 sec × $0.000024 = **$0.35**
- Memory: 8 GB × 7200 sec × $0.0000025 = **$0.14**
- Request: 1 × $0.0000004 = **$0.0000004**
- **Total**: **$0.49 per pair**

**27 Pairs Total**:
- vCPU: 27 × $0.35 = **$9.45**
- Memory: 27 × $0.14 = **$3.78**
- **Total**: **$13.23**

**Not Recommended**: Cloud Run costs 4× more than BigQuery ($13.23 vs $2.99)

---

## Complete Cost Comparison

### Option 1: Local Disk + Local Container (CURRENT)

**One-Time Costs**:
- BigQuery Merge: $2.97
- GCS Staging (temp): $0.01
- BigQuery Temp Storage: $0.01
- Container Compute: $0.00 (runs on existing VM)
- **Total**: **$2.99**

**Recurring Costs**:
- GCS Training Files: $0.43/month
- **Total**: **$0.43/month**

**Pros**:
- ✅ Lowest cost
- ✅ Uses existing VM
- ✅ No new infrastructure

**Cons**:
- ❌ Local disk constraint (28 GB peak)
- ❌ Sequential processing only
- ❌ No persistent checkpoints (must re-extract if merge fails)

---

### Option 2: GCS-First + Local Container (DELETE Checkpoints)

**One-Time Costs**:
- BigQuery Merge: $2.97
- GCS Staging (temp): $0.01
- BigQuery Temp Storage: $0.01
- Container Compute: $0.00
- **Total**: **$2.99**

**Recurring Costs**:
- GCS Training Files: $0.43/month
- **Total**: **$0.43/month**

**Pros**:
- ✅ Same cost as Option 1
- ✅ No local disk constraint
- ✅ Enables parallel processing (2-4 pairs at once)
- ✅ Faster execution (potential 50-75% time savings)

**Cons**:
- ❌ No persistent checkpoints (must re-extract if merge fails)
- ⚠️ Requires script modification (30 min)

---

### Option 3: GCS-First + Local Container (KEEP Checkpoints)

**One-Time Costs**:
- Same as Option 2: **$2.99**

**Recurring Costs**:
- GCS Checkpoints: $8.42/month (27 pairs × 12 GB)
- GCS Training Files: $0.43/month
- **Total**: **$8.85/month**

**Pros**:
- ✅ No local disk constraint
- ✅ Enables parallel processing
- ✅ Persistent checkpoints (can re-merge without re-extracting)
- ✅ Faster recovery from failures

**Cons**:
- ❌ Higher recurring cost ($8.85/month vs $0.43/month)
- ⚠️ Requires script modification

---

### Option 4: GCS-First + Cloud Run (NOT RECOMMENDED)

**One-Time Costs**:
- BigQuery Merge: $2.97
- Cloud Run Compute: $13.23
- GCS Staging: $0.01
- **Total**: **$16.21**

**Recurring Costs**:
- GCS Training Files: $0.43/month (or $8.85 with checkpoints)

**Pros**:
- ✅ No VM needed
- ✅ Serverless (auto-scaling)

**Cons**:
- ❌ 5× more expensive ($16.21 vs $2.99)
- ❌ Not cost-effective for continuous 54h run

---

## Network Costs (All Options)

**BigQuery to GCS**: $0.00 (same region)
**GCS to BigQuery**: $0.00 (same region)
**GCS to Container**: $0.00 (same region, free egress to Compute Engine)
**Container to GCS**: $0.00 (free ingress)

**Total Network Costs**: **$0.00**

**Note**: All resources in same region (us-central1), no egress charges

---

## Recommended Configuration

### Best Overall: Option 2 (GCS-First, Delete Checkpoints)

**Why**:
1. ✅ **Same cost as current** ($2.99 one-time, $0.43/month recurring)
2. ✅ **No local disk constraint** (enables parallel processing)
3. ✅ **Faster execution** (can process 2-4 pairs at once)
4. ✅ **Cleaner architecture** (all data in cloud)

**Modification Required** (30 minutes):
```python
# File: pipelines/training/parallel_feature_testing.py
# Line ~50-60: Change output path from local to GCS

# Before:
checkpoint_file = f"{checkpoint_dir}/{table_name}.parquet"

# After:
checkpoint_file = f"gs://bqx-ml-staging/{pair}/{table_name}.parquet"
```

**Docker Compose Update** (remove local checkpoint mount):
```yaml
volumes:
  # Remove this line:
  # - ./data/features/checkpoints:/workspace/data/features/checkpoints:rw

  # Keep training files local (or make optional):
  - ./data/training:/workspace/data/training:rw
```

---

## Cost Summary Table

| Option | One-Time | Monthly | Total (1 Year) | Disk Usage | Speed |
|--------|----------|---------|----------------|------------|-------|
| **1. Local Disk** | $2.99 | $0.43 | $8.15 | 28 GB | 54h (baseline) |
| **2. GCS Delete** | $2.99 | $0.43 | $8.15 | 16 GB | **36h (33% faster)** |
| **3. GCS Keep** | $2.99 | $8.85 | $109.19 | 0 GB | **36h (33% faster)** |
| **4. Cloud Run** | $16.21 | $0.43 | $21.37 | 0 GB | 54h |

**Recommended**: **Option 2** (GCS-First, Delete Checkpoints)
- Same cost as current
- 33% faster (parallel processing)
- No local disk constraint
- Minimal modification (30 min)

---

## Implementation Checklist

### To Switch to GCS-First (Option 2)

**1. Modify Extraction Script** (30 min):
```bash
# Edit pipelines/training/parallel_feature_testing.py
# Change checkpoint output from local to GCS
# Lines to modify: ~50-60, ~200-220
```

**2. Test with Single Pair** (60 min):
```bash
# Test AUDUSD extraction to GCS
python3 pipelines/training/parallel_feature_testing.py single audusd --workers 25

# Verify files in GCS
gsutil ls gs://bqx-ml-staging/audusd/
```

**3. Update Docker Compose** (5 min):
```yaml
# Remove checkpoint volume mount (data now in GCS)
# Keep training files mount (final outputs)
```

**4. Rebuild Container** (10 min):
```bash
docker build -f Dockerfile.pipeline -t bqx-pipeline:latest .
```

**5. Deploy** (1 min):
```bash
docker-compose -f docker-compose.pipeline.yml up -d
```

**Total Time**: ~2 hours (includes testing)

---

## Final Recommendation

**Current AUDUSD Run**: Keep as-is (54% complete, ~30 min remaining)

**For 27 Remaining Pairs**:

**If you value speed** (54h → 36h):
→ **Implement GCS-First** (2h setup, 33% faster, same cost)

**If you prefer simplicity** (no changes):
→ **Keep Local Disk** (0h setup, slower, same cost)

**Cost Impact**: **Identical** ($2.99 one-time, $0.43/month)

**Speed Impact**: **33% faster** (54h → 36h) with parallel processing

**Disk Impact**: **50% less** (28 GB → 16 GB)

**My Recommendation**: **GCS-First** - Worth the 2-hour setup for 18-hour time savings
