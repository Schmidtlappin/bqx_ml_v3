# Autonomous 27-Pair Pipeline - User Guide

## Overview

The autonomous pipeline handles the complete workflow for all 27 pairs without manual intervention:

1. **Extract** features from BigQuery to local parquet checkpoints
2. **Merge** checkpoints in BigQuery using cloud-based iterative JOIN
3. **Validate** merged training file
4. **Backup** to GCS (optional)
5. **Cleanup** checkpoints to free disk space
6. **Repeat** for next pair

## Quick Start

### Option 1: Start from Beginning (All 27 Pairs)

```bash
cd /home/micha/bqx_ml_v3
./scripts/autonomous_27pair_pipeline.sh
```

### Option 2: Resume from Specific Pair

```bash
cd /home/micha/bqx_ml_v3
./scripts/autonomous_27pair_pipeline.sh usdcad  # Resume from usdcad
```

### Option 3: Run in Background (Recommended for Long Jobs)

```bash
cd /home/micha/bqx_ml_v3
nohup ./scripts/autonomous_27pair_pipeline.sh > pipeline.out 2>&1 &
echo $! > pipeline.pid  # Save process ID
```

## Monitoring

### Real-Time Monitor (Live Dashboard)

```bash
# In a separate terminal
./scripts/monitor_pipeline.sh 30  # Update every 30 seconds
```

This shows:
- Current pair and stage
- System resources (memory, disk)
- Active processes
- Checkpoint directories
- Completed training files
- Latest log entries

### Manual Status Check

```bash
# Check current status
cat /home/micha/bqx_ml_v3/data/.pipeline_status.json

# Check latest log
tail -f logs/autonomous_pipeline_*.log

# Count completed pairs
ls -1 data/training/training_*.parquet | wc -l
```

## Pipeline Configuration

Edit `/home/micha/bqx_ml_v3/scripts/autonomous_27pair_pipeline.sh` to modify:

```bash
# Worker count (default: 40 for optimal BigQuery throughput)
WORKERS=40

# Date range
DATE_START="2020-01-01"
DATE_END="2020-12-31"

# Pair order (default: major USD pairs first)
PAIRS=(
    audusd usdcad usdchf nzdusd gbpusd usdjpy
    euraud eurcad eurchf eurgbp eurjpy eurnzd
    gbpjpy gbpchf gbpaud gbpcad gbpnzd
    audjpy audchf audcad audnzd
    nzdjpy nzdchf nzdcad
    cadjpy cadchf chfjpy
)
```

## Error Handling

### Pipeline Continues on Single Pair Failure

By default, if one pair fails, the pipeline logs the error and continues to the next pair.

To **stop on first failure**, edit the script and uncomment:

```bash
# Optional: Stop on first failure (uncomment if desired)
log "Stopping pipeline due to failure"
break
```

### Resume After Failure

The pipeline automatically skips pairs that are already complete (training file exists).

To resume:

```bash
# Resume from failed pair
./scripts/autonomous_27pair_pipeline.sh gbpusd
```

### Check for Failures

```bash
# Check final summary in log
tail -50 logs/autonomous_pipeline_*.log

# Check if any pairs are missing
ls -1 data/training/training_*.parquet | wc -l
# Should be 28 (including EURUSD)
```

## Resource Management

### Disk Space

- **Per pair checkpoints**: ~12 GB
- **After cleanup**: <1 GB (only training file remains)
- **Minimum free space**: 20 GB recommended

The pipeline automatically deletes checkpoints after each merge to maintain disk space.

### Memory

- **Extraction**: 2-4 GB (40 workers)
- **Merge**: <1 GB (cloud-based in BigQuery)
- **Total system**: 62 GB available

### CPU

- **Extraction**: ~100-110% (1-2 cores active)
- **Merge**: Minimal (cloud-based)

## Timeline Estimates

### Per Pair (Average)

- Extraction: 60-70 minutes (40 workers)
- Merge: 50-60 minutes (BigQuery cloud)
- Validation: 1-2 minutes
- Cleanup: <1 minute
- **Total**: 110-130 minutes per pair

### All 27 Pairs

- **Best case**: 27 × 90 min = 40.5 hours
- **Average case**: 27 × 120 min = 54 hours
- **Worst case**: 27 × 150 min = 67.5 hours

Expected completion: **2-3 days** for all 27 pairs

## Cost Estimate

### BigQuery Merge (Cloud)

- **Per pair**: $0.11 (iterative JOIN queries)
- **27 pairs**: $2.97 total

### Storage (Temporary)

- GCS staging: $0.01 per pair (deleted after merge)
- BigQuery temp tables: $0.01 per pair (deleted after merge)

### Total Cost: ~$3.50 for 27 pairs

## Output Files

### Training Files

Location: `/home/micha/bqx_ml_v3/data/training/`

```
training_audusd.parquet
training_usdcad.parquet
training_usdchf.parquet
...
training_chfjpy.parquet
```

### Logs

Location: `/home/micha/bqx_ml_v3/logs/`

```
autonomous_pipeline_20251212_002000.log  # Main pipeline log
```

### Status File

Location: `/home/micha/bqx_ml_v3/data/.pipeline_status.json`

Real-time status of current pair and stage.

## Stopping the Pipeline

### Graceful Stop

```bash
# Find process ID
cat pipeline.pid

# Send interrupt signal
kill -INT $(cat pipeline.pid)
```

The pipeline will finish the current stage and exit cleanly.

### Force Stop

```bash
# Find process ID
ps aux | grep autonomous_27pair_pipeline

# Force kill
kill -9 <PID>
```

Warning: May leave checkpoints or incomplete merges.

## Troubleshooting

### Pipeline Not Starting

```bash
# Check scripts exist and are executable
ls -l scripts/autonomous_27pair_pipeline.sh
ls -l scripts/merge_single_pair_optimized.py
ls -l pipelines/training/parallel_feature_testing.py

# Make executable if needed
chmod +x scripts/autonomous_27pair_pipeline.sh
```

### Extraction Slow

```bash
# Check worker count (increase if system has capacity)
# Edit WORKERS=40 to WORKERS=50 in pipeline script

# Check BigQuery quotas
gcloud compute quotas list --project=bqx-ml
```

### Merge Failures

```bash
# Check IAM permissions
gsutil iam get gs://bqx-ml-staging

# Check BigQuery datasets exist
bq ls -d bqx-ml

# Re-run merge manually for specific pair
python3 scripts/merge_single_pair_optimized.py gbpusd
```

### Disk Space Full

```bash
# Check disk usage
df -h /home/micha/bqx_ml_v3

# Manually delete old checkpoints
rm -rf data/features/checkpoints/*

# Resume pipeline
./scripts/autonomous_27pair_pipeline.sh <next_pair>
```

## Best Practices

1. **Run in background** using `nohup` for long jobs
2. **Monitor periodically** using the monitor script
3. **Check logs** if you see delays or errors
4. **Verify completeness** after pipeline finishes (28 training files)
5. **Keep disk space** above 20 GB during execution

## Integration with Agent Workflow

### Current Manual Process

1. BA extracts features manually
2. EA waits for extraction to complete
3. EA runs merge manually
4. QA validates manually
5. Repeat for each pair

### Autonomous Process (This Pipeline)

1. **Start pipeline once**
2. **Monitor periodically** (optional)
3. **All 27 pairs complete autonomously**
4. QA validates batch at end (optional)

### Coordination

The autonomous pipeline can run independently while agents:
- BA: Monitors extraction logs
- EA: Monitors merge logs
- QA: Validates final outputs
- CE: Receives completion reports

## Advanced Usage

### Parallel Pair Processing (NOT RECOMMENDED)

Current pipeline is **sequential** (one pair at a time) due to disk space constraints.

If you have **>100 GB disk space**, you could modify to process 2-3 pairs in parallel:

```bash
# Run multiple pipeline instances
./scripts/autonomous_27pair_pipeline.sh audusd &
./scripts/autonomous_27pair_pipeline.sh usdcad &
./scripts/autonomous_27pair_pipeline.sh usdchf &
```

Warning: Requires manual coordination and disk space management.

### Custom Pair Subset

```bash
# Edit PAIRS array in script to only process specific pairs
PAIRS=(gbpusd usdjpy eurjpy)

./scripts/autonomous_27pair_pipeline.sh
```

### Backup to GCS

Uncomment backup section in `stage_4_backup()`:

```bash
GCS_BACKUP="gs://bqx-ml-output/backups/training_${pair}.parquet"
log "Backing up to GCS: $GCS_BACKUP"
gsutil cp "$training_file" "$GCS_BACKUP"
```

---

**Questions?** Check logs first, then consult EA for pipeline optimization recommendations.
