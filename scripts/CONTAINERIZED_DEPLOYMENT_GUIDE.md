# Containerized Autonomous Pipeline Deployment Guide

## Overview

Run the autonomous 27-pair pipeline in a Docker container to:
- ✅ Free up VM resources for other work
- ✅ Isolate pipeline from host system
- ✅ Set strict resource limits (prevent system overload)
- ✅ Enable parallel development while pipeline runs
- ✅ Easier monitoring and management

## Difficulty Assessment

**EASY-MEDIUM**: 30-60 minutes to deploy

- **Docker basics**: Easy (Docker already installed)
- **Build image**: Easy (5-10 min)
- **Configure limits**: Easy (pre-configured)
- **Deploy**: Easy (1 command)
- **Monitor**: Easy (docker logs, docker stats)

## Prerequisites

✅ **Already Available on Your VM**:
- Docker v29.0.2 installed
- GCP credentials configured
- Pipeline scripts ready

❌ **Not Required**:
- No new software installation
- No code changes
- No GCP configuration changes

---

## Quick Start (5 Minutes)

### 1. Build Container Image

```bash
cd /home/micha/bqx_ml_v3

# Build pipeline container (5-10 min first time, cached after)
docker build -f Dockerfile.pipeline -t bqx-pipeline:latest .
```

### 2. Deploy Pipeline Container

```bash
# Start pipeline in background with resource limits
docker-compose -f docker-compose.pipeline.yml up -d

# Verify started
docker ps | grep bqx-autonomous-pipeline
```

### 3. Monitor Progress

```bash
# View real-time logs
docker logs -f bqx-autonomous-pipeline

# Check resource usage
docker stats bqx-autonomous-pipeline

# Check status file
cat data/.pipeline_status.json
```

**That's it!** Pipeline runs autonomously in container for ~54 hours.

---

## Resource Isolation Benefits

### VM Resources After Containerization

**Container Limits** (configured in docker-compose.pipeline.yml):
- **CPU**: 4 cores max (out of 8 total)
- **Memory**: 20 GB max (out of 62 GB total)

**Freed for Other Work**:
- **CPU**: 4 cores available (50% of VM)
- **Memory**: 42 GB available (67% of VM)
- **Disk**: Shared (containers use same filesystem)

### What You Can Do While Pipeline Runs

With 4 cores and 42 GB free, you can:
- ✅ Run development environments (VSCode, Jupyter)
- ✅ Test new features in isolation
- ✅ Train small models (up to 30 GB)
- ✅ Run data analysis notebooks
- ✅ Build and test containers
- ✅ Run web applications

**Example: Run Jupyter Notebook Alongside**
```bash
# Pipeline uses 4 cores, 20 GB
# Jupyter can use 2-4 cores, 10-20 GB
docker run -d -p 8888:8888 jupyter/datascience-notebook
```

---

## Detailed Configuration

### Resource Limits (Customizable)

Edit `docker-compose.pipeline.yml`:

```yaml
deploy:
  resources:
    limits:
      cpus: '4.0'      # Max cores (increase if needed)
      memory: 20G      # Max memory (increase if VM has capacity)
    reservations:
      cpus: '2.0'      # Guaranteed minimum
      memory: 8G       # Guaranteed minimum
```

**Conservative** (more for other work):
```yaml
cpus: '3.0'
memory: 15G
```

**Aggressive** (faster pipeline):
```yaml
cpus: '6.0'
memory: 30G
```

### Volume Mounts (What's Shared)

**Read-Only** (container can't modify):
- GCP credentials: `${HOME}/.config/gcloud`
- Pipeline scripts: `./scripts`, `./pipelines`

**Read-Write** (container can modify):
- Checkpoints: `./data/features/checkpoints`
- Training files: `./data/training`
- Logs: `./logs`
- Status: `./data/.pipeline_status.json`

**Why This Works**: Output files written to container are immediately visible on host.

---

## Monitoring Containerized Pipeline

### Option 1: Docker Logs (Recommended)

```bash
# Real-time logs (like tail -f)
docker logs -f bqx-autonomous-pipeline

# Last 50 lines
docker logs --tail 50 bqx-autonomous-pipeline

# Since specific time
docker logs --since 10m bqx-autonomous-pipeline
```

### Option 2: Docker Stats (Resource Usage)

```bash
# Real-time resource usage
docker stats bqx-autonomous-pipeline

# Output:
# CONTAINER ID   CPU %   MEM USAGE / LIMIT   MEM %   NET I/O   BLOCK I/O
# abc123         110%    3.2GB / 20GB        16%     ...       ...
```

### Option 3: Monitor Dashboard (Optional)

```bash
# Start cAdvisor monitoring (optional)
docker-compose -f docker-compose.pipeline.yml --profile monitoring up -d

# Access dashboard: http://localhost:8080
```

### Option 4: Status File (Same as Before)

```bash
# Check current pair/stage
cat data/.pipeline_status.json

# Count completed pairs
ls -1 data/training/training_*.parquet | wc -l
```

---

## Container Management

### Start/Stop/Restart

```bash
# Stop pipeline (graceful)
docker-compose -f docker-compose.pipeline.yml stop

# Stop pipeline (force)
docker-compose -f docker-compose.pipeline.yml down

# Restart pipeline
docker-compose -f docker-compose.pipeline.yml restart

# Start pipeline
docker-compose -f docker-compose.pipeline.yml up -d
```

### Check Status

```bash
# Is container running?
docker ps | grep bqx-autonomous-pipeline

# Container details
docker inspect bqx-autonomous-pipeline

# Container health
docker inspect --format='{{.State.Health.Status}}' bqx-autonomous-pipeline
```

### Resume After Stop

```bash
# Pipeline automatically resumes from last completed pair
docker-compose -f docker-compose.pipeline.yml up -d
```

---

## Comparison: Host vs Container

### Performance

| Metric | Host (Direct) | Container | Difference |
|--------|--------------|-----------|------------|
| CPU overhead | 0% | ~2-5% | Minimal |
| Memory overhead | 0MB | ~200-500MB | Negligible |
| Disk I/O | Direct | Bind mount | ~5% slower |
| Network I/O | Direct | Host network | Same |
| **Total overhead** | 0% | **~5%** | Acceptable |

**Verdict**: Container adds ~5% overhead, but isolation benefits outweigh cost.

### Resource Isolation

| Feature | Host (Direct) | Container |
|---------|--------------|-----------|
| CPU limit | ❌ None | ✅ 4 cores max |
| Memory limit | ❌ None | ✅ 20 GB max |
| Crash isolation | ❌ Affects VM | ✅ Container only |
| Restart policy | ❌ Manual | ✅ Automatic |
| Monitoring | ⚠️ Manual | ✅ Docker stats |

**Verdict**: Container provides better isolation and management.

### Complexity

| Aspect | Host (Direct) | Container |
|--------|--------------|-----------|
| Setup | ✅ Simple (scripts) | ⚠️ Medium (build + deploy) |
| Deployment | ✅ 1 command | ⚠️ 2 commands (build + up) |
| Monitoring | ⚠️ Multiple tools | ✅ docker logs/stats |
| Troubleshooting | ⚠️ Host debugging | ⚠️ Container debugging |

**Verdict**: Container adds initial complexity, but simplifies operations.

---

## Benefits Analysis

### ✅ Pros of Containerization

1. **Resource Isolation**
   - Hard limits prevent pipeline from consuming entire VM
   - Guaranteed resources for other work (4 cores, 42 GB)

2. **Parallel Development**
   - Work on other projects while pipeline runs
   - No conflict with pipeline processes
   - Separate environments

3. **Crash Isolation**
   - If pipeline crashes, only container affected
   - Host VM remains stable
   - Auto-restart with `restart: unless-stopped`

4. **Easier Monitoring**
   - Single command: `docker stats`
   - Centralized logs: `docker logs`
   - Built-in health checks

5. **Reproducibility**
   - Same environment every time
   - No dependency conflicts
   - Easier to debug

6. **Portability**
   - Can move to different VM
   - Can run on Cloud Run (future)
   - Same configuration anywhere

### ❌ Cons of Containerization

1. **Initial Setup**
   - Build image: 5-10 min
   - Learn docker commands: 15-30 min

2. **Slight Performance Overhead**
   - ~5% slower disk I/O
   - ~2-5% CPU overhead
   - 200-500 MB memory overhead

3. **Debugging Complexity**
   - Need to exec into container
   - Separate filesystem namespace
   - Log access requires docker commands

4. **Disk Space**
   - Image size: ~1-2 GB
   - No significant impact (97 GB available)

### **Verdict**: ✅ Benefits Outweigh Costs

**For 54-hour autonomous run**: Container isolation worth the 5% overhead.

---

## Cost-Benefit Analysis

### Time Investment

**One-Time Setup**:
- Build Docker image: 10 min
- Test deployment: 10 min
- Learn commands: 20 min
- **Total**: 40 min

**Per Deployment**:
- Start container: 30 seconds
- Monitor setup: 2 min
- **Total**: 2.5 min

**ROI**: After 1-2 deployments, containerization saves time.

### Resource Freed

**With Container** (54-hour pipeline):
- Work capacity: 4 cores × 54h = 216 core-hours
- Memory capacity: 42 GB × 54h = 2,268 GB-hours
- **Value**: Can run multiple parallel projects

**Without Container**:
- Work capacity: Limited (risk of interfering with pipeline)
- Memory capacity: Limited (risk of OOM)
- **Value**: Must wait for pipeline to complete

**Verdict**: Container enables ~$100-500 worth of parallel work.

---

## Deployment Options

### Option A: Containerized (Recommended for Parallel Work)

```bash
cd /home/micha/bqx_ml_v3

# Build image (one-time, 5-10 min)
docker build -f Dockerfile.pipeline -t bqx-pipeline:latest .

# Deploy with resource limits
docker-compose -f docker-compose.pipeline.yml up -d

# Monitor
docker logs -f bqx-autonomous-pipeline
```

**When to Use**:
- ✅ Want to work on other projects simultaneously
- ✅ Need strict resource limits
- ✅ Want crash isolation
- ✅ Plan to run pipeline multiple times

### Option B: Direct Host Deployment (Simpler)

```bash
cd /home/micha/bqx_ml_v3

# Start pipeline directly
nohup ./scripts/autonomous_27pair_pipeline.sh > pipeline.out 2>&1 &
echo $! > pipeline.pid

# Monitor
tail -f logs/autonomous_pipeline_*.log
```

**When to Use**:
- ✅ One-time deployment
- ✅ Don't need parallel work
- ✅ Want simplest setup
- ✅ Maximum performance (no overhead)

---

## Troubleshooting

### Container Won't Start

```bash
# Check Docker daemon
sudo systemctl status docker

# Check image exists
docker images | grep bqx-pipeline

# Check logs
docker logs bqx-autonomous-pipeline

# Rebuild image
docker build --no-cache -f Dockerfile.pipeline -t bqx-pipeline:latest .
```

### Container Crashes/Restarts

```bash
# Check exit code
docker inspect bqx-autonomous-pipeline --format='{{.State.ExitCode}}'

# Check last logs
docker logs --tail 100 bqx-autonomous-pipeline

# Check resource limits
docker stats bqx-autonomous-pipeline
```

### GCP Credentials Not Working

```bash
# Verify credentials on host
gcloud auth application-default print-access-token

# Verify credentials in container
docker exec bqx-autonomous-pipeline gcloud auth application-default print-access-token

# Remount credentials
docker-compose -f docker-compose.pipeline.yml down
docker-compose -f docker-compose.pipeline.yml up -d
```

### Slow Performance

```bash
# Check resource usage
docker stats bqx-autonomous-pipeline

# Increase CPU limit (edit docker-compose.pipeline.yml)
cpus: '6.0'  # was 4.0

# Restart with new limits
docker-compose -f docker-compose.pipeline.yml up -d --force-recreate
```

---

## Advanced: Cloud Run Deployment (Future)

Container can also run on Google Cloud Run (serverless):

```bash
# Push image to GCR
docker tag bqx-pipeline:latest gcr.io/bqx-ml/pipeline:latest
docker push gcr.io/bqx-ml/pipeline:latest

# Deploy to Cloud Run
gcloud run deploy bqx-pipeline \
  --image gcr.io/bqx-ml/pipeline:latest \
  --region us-central1 \
  --memory 20Gi \
  --cpu 4 \
  --timeout 54h \
  --no-cpu-throttling
```

**Benefits**:
- No VM needed
- Pay per use (vs always-on VM)
- Auto-scaling
- Managed infrastructure

**When to Use**: For occasional pipeline runs, not continuous use.

---

## Recommendation

### For Current AUDUSD + 26 Pairs

**Scenario 1: Want to Work on Other Projects**
→ **Use Container** (40 min setup, frees 4 cores + 42 GB)

**Scenario 2: One-Time Run, No Parallel Work**
→ **Use Direct Host** (simpler, 0 setup time)

### For Future Deployments

**If pipeline will run regularly** (weekly, monthly):
→ **Containerize now** (40 min investment, saves time long-term)

**If pipeline is one-off**:
→ **Direct host** (simpler)

---

## Final Verdict

**Difficulty**: ⚠️ **EASY-MEDIUM** (40 min setup)

**Benefits**:
- ✅ Frees 4 cores + 42 GB for parallel work
- ✅ Crash isolation (pipeline can't take down VM)
- ✅ Easier monitoring (docker logs/stats)
- ✅ Auto-restart on failure

**Costs**:
- ⚠️ 40 min initial setup
- ⚠️ ~5% performance overhead
- ⚠️ Slightly more complex debugging

**Recommendation**:
- **Use Container IF**: You want to work on other projects while pipeline runs
- **Use Direct Host IF**: You prefer simplicity and don't need parallel work

**For 54-hour autonomous run**: Container is worth it if you value the freed resources.
