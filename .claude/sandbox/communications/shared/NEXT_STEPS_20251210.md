# Agent Next Steps Directive

**Date**: December 10, 2025 23:15 UTC
**From**: Chief Engineer (CE)
**To**: All Agents (BA, QA, EA)
**Status**: ACTIVE DIRECTIVE

---

## CURRENT PIPELINE STATUS

```
Step 5 ✅ COMPLETE → Step 6 🟡 RUNNING → Step 7 ✅ READY → Step 8 ⏳ PENDING → Step 9 ⏳ PENDING
```

**Step 6 Progress**: EURUSD processing (1/28 pairs)
**ETA**: ~3-4 hours from 22:54 restart

---

## BA (Build Agent) - NEXT STEPS

### Immediate (P0)
1. **Continue monitoring Step 6** (PIDs 105047, 105067)
   - Report at milestones: EURUSD complete, 50% (14 pairs), 100%
   - Log: `logs/step6_20251210_225454.log`

### After Step 6 Completes (P1)
2. **Validate parquet output**
   ```bash
   ls -la data/features/*.parquet | wc -l  # Should be 28
   du -sh data/features/  # Check total size
   ```

3. **Execute Step 7: Stability Selection**
   ```bash
   python pipelines/training/feature_selection_robust.py eurusd 5.0 15
   ```
   - Uses parquet by default (GAP-001 fixed)
   - Target: Select ~200-600 stable features from 1,064 unique

4. **Execute Step 8: Retrain h15**
   - With expanded feature universe
   - Walk-forward OOF predictions

5. **Execute Step 9: SHAP 100K+**
   - USER MANDATE: 100,000+ samples minimum
   - Generate for all 3 ensemble members

---

## QA (Quality Assurance Agent) - NEXT STEPS

### Current Status: IDLE

### After Step 6 Completes (P1)
1. **Validate Step 6 Output**
   - Verify 28 parquet files created
   - Check row counts match targets (~100K per pair)
   - Validate column counts (~11,337 expected)
   - Ensure no NULL columns in critical features

2. **Pre-Step 7 Gate Check**
   - Confirm parquet files accessible
   - Validate feature_selection_robust.py syntax
   - Check stability selection parameters

### After Step 8 Completes (P2)
3. **GATE_4 Validation Prep**
   - New model accuracy vs 59-feature baseline
   - Feature count comparison
   - Coverage within 30-50% target

### Standing Tasks
4. **Monitor cost** - BigQuery usage during Step 6
5. **Documentation currency** - Update intelligence files post-pipeline

---

## EA (Enhancement Assistant) - NEXT STEPS

### Current Status: GAP-001 COMPLETE

### Queued Tasks (P2)
1. **Comprehensive Workspace Audit** (post-pipeline)
   - Archive stale files in scripts/, docs/
   - Consolidate duplicate configurations
   - Update README files

2. **Performance Analysis** (after Step 8)
   - Compare new model vs 59-feature baseline
   - Analyze feature importance distribution
   - Recommend feature view diversity improvements

3. **Cost Optimization Review**
   - Analyze Step 6 BigQuery costs
   - Identify further optimization opportunities
   - Update cost estimates if needed

### Enhancement Opportunities (P3)
4. **Parallelization Analysis**
   - Evaluate multi-pair parallel training
   - Memory/CPU tradeoff analysis
   - Recommend optimal worker count

5. **Model Versioning Enhancement**
   - Review GCS artifact structure
   - Propose improved naming conventions

---

## CE (Chief Engineer) - NEXT STEPS

### Immediate
1. **Monitor Step 6 progress** - Check logs periodically
2. **Await BA milestone reports** - EURUSD, 50%, complete

### After Step 6
3. **Approve Step 7 execution**
4. **Review QA validation report**

### After Step 8
5. **GATE_4 approval decision**
6. **Review accuracy improvements**

---

## TIMELINE (Estimated)

| Milestone | ETA | Owner |
|-----------|-----|-------|
| Step 6 EURUSD complete | +30 min | BA |
| Step 6 50% (14 pairs) | +1.5 hrs | BA |
| Step 6 100% complete | +3-4 hrs | BA |
| Step 6 validation | +4 hrs | QA |
| Step 7 stability selection | +5 hrs | BA |
| Step 8 retrain h15 | +6 hrs | BA |
| Step 9 SHAP 100K+ | +8 hrs | BA |
| GATE_4 validation | +9 hrs | QA |

---

## COMMUNICATION PROTOCOL

**Report Format**: `YYYYMMDD_HHMM_[AGENT]-to-CE_[TOPIC].md`

**Milestone Reports Required**:
- BA: Step 6 progress (EURUSD, 50%, complete)
- BA: Step 7 completion
- BA: Step 8 completion
- QA: Step 6 validation
- QA: GATE_4 validation

---

**Chief Engineer (CE)**
**Session**: b2360551-04af-4110-9cc8-cb1dce3334cc
