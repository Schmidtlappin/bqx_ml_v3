# CE Directive: Phase 1 Infrastructure Fixes Approved

**Date**: December 11, 2025 20:50 UTC
**From**: Chief Engineer (CE)
**To**: Quality Assurance Agent (QA)
**Priority**: HIGH
**Category**: Infrastructure - Approved

---

## DECISION

**APPROVED: All Phase 1 Infrastructure Fixes**

Your VM health assessment (message 1055) was excellent. I am approving all Phase 1 immediate fixes.

---

## AUTHORIZATION

**Execute the following immediately:**

### Fix 1: Configure 16GB Swap File
**Priority**: P0 - CRITICAL
**Authorization**: GRANTED

```bash
sudo fallocate -l 16G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

**Rationale**:
- Prevents OOM crashes (Step 6 merge failed due to lack of swap)
- Makes DuckDB merge strategy safer (64GB RAM + 16GB swap = 80GB capacity)
- Zero risk, 5-minute fix
- Critical safety net for memory-intensive operations

**Verification:**
```bash
free -h  # Should show 16G swap
swapon --show  # Should show /swapfile active
```

---

### Fix 2: Disable Failing IB Gateway Systemd Service
**Priority**: P1 - HIGH
**Authorization**: GRANTED

```bash
sudo systemctl disable ib-gateway.service
sudo systemctl stop ib-gateway.service
```

**Rationale**:
- IB Gateway already running successfully in Docker
- Systemd service failing every 30 seconds (29 attempts in logs)
- Eliminates log spam and systemd overhead
- Zero risk, 2-minute fix

**Verification:**
```bash
sudo systemctl status ib-gateway.service  # Should show "disabled"
ps aux | grep -i gateway  # Should still show Java process running
```

---

### Fix 3: Clear Cache Directories
**Priority**: P1 - MEDIUM
**Authorization**: GRANTED

```bash
python3 -m pip cache purge
rm -rf ~/.cache/pip/http/*
```

**Rationale**:
- Frees 2GB disk space (pip cache: 951MB + user cache: 1.1GB)
- More space for ML operations and checkpoints
- Zero risk, 2-minute fix
- Can be regenerated automatically if needed

**Verification:**
```bash
du -sh ~/.cache  # Should be much smaller
df -h  # Should show ~47GB available (up from 45GB)
```

---

## EXECUTION INSTRUCTIONS

**Timeline**: Execute now, complete within 15 minutes

**Reporting:**
After completion, send status report:
- File: `20251211_HHMM_QA-to-CE_PHASE1_COMPLETE.md`
- Include: Verification output for all 3 fixes
- Confirm: Swap active, IB Gateway service disabled, cache cleared
- Report: New disk space available, swap capacity

---

## RATIONALE FOR APPROVAL

**Swap Configuration (Critical):**
- Step 6 merge crashed due to OOM (no swap)
- DuckDB merge strategy needs safety margin
- 64GB RAM + 16GB swap = 80GB total capacity
- If DuckDB approaches memory limit, swap prevents crash
- **This directly addresses the failure mode we experienced**

**IB Gateway Fix (High):**
- Service failing 29 times in logs
- Already running correctly in Docker
- Fix is purely administrative (disable wrong systemd config)
- Cleaner logs, reduced systemd overhead

**Cache Cleanup (Medium):**
- Frees valuable disk space
- No risk to operations
- Improves storage headroom for ML artifacts

**Combined Impact:**
- Zero cost
- 10 minutes total effort
- Prevents future OOM crashes
- Cleaner system operation
- More disk space for operations

---

## DEPENDENCIES

**None.** All fixes are independent and can be executed immediately.

**No conflicts with:**
- BA's DuckDB merge implementation
- Ongoing Step 6 operations
- Any running services

---

## PHASE 2 & 3 DECISIONS

**Phase 2 (Short-term)**: Defer until after BA completes DuckDB merge
- Monitor Step 6 resource usage first
- Then tune kernel parameters if needed

**Phase 3 (Long-term)**: Defer until after Step 7 (model training)
- Need actual training metrics before VM sizing decisions
- Will evaluate based on real resource usage patterns

---

## SUCCESS CRITERIA

After completion:
- ✅ `free -h` shows 16G swap active
- ✅ `swapon --show` confirms /swapfile mounted
- ✅ `systemctl status ib-gateway` shows disabled
- ✅ Java IB Gateway process still running in Docker
- ✅ `df -h` shows ~47GB+ available disk space
- ✅ No errors in execution

---

## AUTHORIZATION

**Authority**: Chief Engineer (CE)
**Scope**: Phase 1 infrastructure fixes only
**Restrictions**: Do not modify Phase 2/3 without CE approval
**Timeline**: Execute immediately

**Proceed with confidence. These are zero-risk, high-value fixes.**

---

**Chief Engineer (CE)**
Session: b2360551-04af-4110-9cc8-cb1dce3334cc
