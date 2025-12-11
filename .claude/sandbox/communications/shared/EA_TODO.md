# EA Task List

**Last Updated**: December 11, 2025 05:00
**Maintained By**: CE (refresh)

---

## CURRENT STATUS

| Item | Status |
|------|--------|
| GAP-001 | ✅ **COMPLETE** |
| Gap Remediation | ✅ **COMPLETE** (var_*, csi_*) |
| Feature Coverage Audit | ✅ **COMPLETE** (21/21 prefixes) |
| Step 6 | 🟢 **EXECUTING** - SEQUENTIAL MODE |
| EA Role | 🔵 **SYSTEM MONITORING** |

**ACTIVE DIRECTIVES**:
- `inboxes/EA/20251211_0545_CE-to-EA_SESSION_ARCHIVE_DIRECTIVE.md` **(P0 - IMMEDIATE)**
- `inboxes/EA/20251211_0525_CE-to-EA_WORKSPACE_CLEANUP_DIRECTIVE.md` (P1 - COMPLETE)
- `inboxes/EA/20251211_0510_CE-to-EA_OPTIMIZATION_RESPONSE.md`
- `inboxes/EA/20251211_0450_CE-to-EA_SYSTEM_MONITORING_DIRECTIVE.md`

---

## P0: IMMEDIATE - SESSION FILE ARCHIVE (NEW)

**CE DIRECTIVE**: `inboxes/EA/20251211_0545_CE-to-EA_SESSION_ARCHIVE_DIRECTIVE.md`

**PROBLEM**: Dropdown shows 249 sessions, only 4 are active.

| Task | Status |
|------|--------|
| Archive corrupted sessions (72a1c1a7-*, b959d344-*) | PENDING |
| Archive ALL agent-*.jsonl (232 files) | PENDING |
| Archive 0-byte sessions | PENDING |
| Archive old main sessions | PENDING |
| Verify dropdown shows only CE & EA | PENDING |

**KEEP ONLY**:
- `b2360551-04af-4110-9cc8-cb1dce3334cc.jsonl` (CE)
- `c31dd28b-2f5b-4f93-a3ad-1a9f0fe74dbc.jsonl` (EA)

**ARCHIVE TO**: `/home/micha/bqx_ml_v3/archive/claude_sessions_20251211/`

---

## P1: COMPLETE - WORKSPACE CLEANUP

**CE DIRECTIVE**: `inboxes/EA/20251211_0525_CE-to-EA_WORKSPACE_CLEANUP_DIRECTIVE.md`

| Task | Status | Notes |
|------|--------|-------|
| Archive old logs | PENDING | `logs/step6_*.log` (except current) |
| Archive old comms | PENDING | Messages before Dec 10 |
| Clean __pycache__ | PENDING | All Python cache |
| Update intelligence files | PENDING | context.json, roadmap_v2.json |
| Create archive manifest | PENDING | `archive/2025-12-11_session_cleanup/` |
| Report to CE | PENDING | Cleanup summary |

**DO NOT TOUCH**:
- PID 1312752 (Step 6 running)
- `data/features/checkpoints/`

---

## P0: ACTIVE - SYSTEM MONITORING (Step 6)

| Metric | Threshold | Alert Level |
|--------|-----------|-------------|
| Memory (RSS) | >40GB | WARNING |
| Memory (RSS) | >50GB | CRITICAL |
| CPU | >1100% | WARNING |
| Disk /home | >80% | WARNING |
| Disk /home | >90% | CRITICAL |
| Process dead | N/A | CRITICAL |
| Log stale >5min | N/A | CRITICAL |

**Commands**:
```bash
# Process memory/CPU
ps -p 1312752 -o pid,rss,vsz,%mem,%cpu --no-headers

# System memory
free -h

# Disk usage
df -h /home

# Process state
ps -p 1312752 -o state --no-headers
```

**Schedule**:
| Interval | Actions |
|----------|---------|
| Every 5 min | Process alive, memory |
| Every 15 min | Disk, progress |
| Every 30 min | Report to CE |
| On anomaly | Immediate alert |

**Current Values (05:25)**:
- PID 1312752: RUNNING (16 workers)
- Memory: ~2.5 GB (OK)
- CPU: 106% (OK)
- Progress: EURUSD in progress

---

## P0: COMPLETE - GAP-001 REMEDIATION

| Task | Status | Notes |
|------|--------|-------|
| ~~Fix feature_selection_robust.py~~ | **COMPLETE** | Parquet now default (--bq flag for BQ) |
| ~~Fix parallel_stability_selection.py~~ | **COMPLETE** | Added parquet loading + --bq flag |
| ~~Report to CE~~ | **COMPLETE** | Cost savings: $30/run |

**CE Acknowledgment**: `inboxes/EA/20251210_2320_CE-to-EA_NEXT_STEPS_DIRECTIVE.md`

---

## P0: CRITICAL - PARQUET CHECKPOINT IMPLEMENTATION

**CE DIRECTIVE**: `inboxes/EA/20251211_0245_CE-to-EA_PARQUET_CHECKPOINT_DIRECTIVE.md`

| Task | Status | Notes |
|------|--------|-------|
| ~~Audit 100% Feature Coverage~~ | ✅ **COMPLETE** | CE audit found 207 missing tables |
| ~~Reconcile vs feature_catalogue.json~~ | ✅ **COMPLETE** | CSI IS IMPLEMENTED (catalogue updated) |
| ~~Implement checkpoint/resume~~ | ✅ **COMPLETE** | Per EA report 02:55 |
| ~~FIX var_* gap (63 tables)~~ | ✅ **COMPLETE** | Added var_* query |
| ~~FIX csi_* gap (144 tables)~~ | ✅ **COMPLETE** | Added csi_* query |
| ~~Test dry_run after fix~~ | ✅ **COMPLETE** | Verified 669 tables |
| ~~Report to CE~~ | ✅ **COMPLETE** | EA-to-CE_GAP_REMEDIATION_COMPLETE.md |
| ~~Feature Coverage Audit~~ | ✅ **COMPLETE** | EA-to-CE_FEATURE_COVERAGE_AUDIT.md |

### Feature Coverage Audit COMPLETE (04:15)

| Metric | Result |
|--------|--------|
| Feature prefixes | 21/21 (100%) |
| Tables per pair | 669 |
| Total BQ tables | 5,048 |
| CE Acknowledgment | `20251211_0420_CE-to-EA_AUDIT_ACKNOWLEDGED.md` |

### Gap Remediation COMPLETE (03:40)

| Category | Tables | Status |
|----------|--------|--------|
| pair_specific | 256 | ✅ |
| triangulation | 194 | ✅ |
| market_wide | 12 | ✅ |
| variance | 63 | ✅ **FIXED** |
| currency_strength | 144 | ✅ **FIXED** |
| **TOTAL** | **669** | **100%** |

### User Context
User frustrated with multiple restarts losing progress. MUST save intermediate parquets to enable resume.

---

## P1: PAUSED - STEP 6 MONITORING (Pending Checkpoint Implementation)

| Task | Status | Notes |
|------|--------|-------|
| Monitor Step 6 progress | **PAUSED** | Step 6 STOPPED for checkpoint implementation |
| Validate parquet outputs | PENDING | After completion |

---

## P2: QUEUED - POST-PIPELINE TASKS (After Step 8)

| Task | Status | Deliverable |
|------|--------|-------------|
| **Comprehensive Workspace Audit** | QUEUED | Audit report |
| - Archive stale files in scripts/, docs/ | | |
| - Consolidate duplicate configurations | | |
| - Update README files | | |
| - Remove deprecated scripts | | |
| **Performance Analysis** | QUEUED | Analysis report |
| - Compare new model vs 59-feature baseline | | |
| - Analyze feature importance distribution | | |
| - Identify underperforming feature groups | | |
| - Recommend feature view diversity | | |
| **Cost Optimization Review** | QUEUED | Cost report |
| - Analyze Step 6 BigQuery costs | | |
| - Calculate actual vs estimated | | |
| - Identify further optimizations | | |
| - Update documentation | | |

---

## P3: QUEUED - ENHANCEMENT OPPORTUNITIES

| Task | Status | Notes |
|------|--------|-------|
| **Parallelization Analysis** | QUEUED | Multi-pair feasibility |
| - Memory/CPU tradeoff analysis | | |
| - Recommend optimal worker count | | |
| **Model Versioning Enhancement** | QUEUED | GCS improvements |
| - Review artifact structure | | |
| - Propose naming conventions | | |
| - Recommend retention policies | | |
| **EA-003 Implementation** | DEFERRED | Phase 4.5 (A/B comparison) |

---

## ACHIEVEMENTS

| Enhancement | Impact | Date |
|-------------|--------|------|
| EA-001 ElasticNet removal | +1.5% accuracy | 2025-12-09 |
| EA-002 Higher threshold | +3.71% accuracy | 2025-12-09 |
| EA-003 Feature-view diversity | +1-2% (projected) | Approved for Phase 4.5 |
| Workspace Cleanup | 31% disk reduction | 2025-12-10 |
| **GAP-001 Remediation** | **-$30/run** | **2025-12-10** |

**Total Accuracy Improvement**: 82.52% → 91.66% (+9.14%)

---

## DELIVERABLES (Per CE Directive)

1. [ ] Workspace audit report
2. [ ] Performance analysis report (after Step 8)
3. [ ] Cost optimization report
4. [ ] Enhancement recommendations

---

*Updated by CE - December 11, 2025 04:00*
