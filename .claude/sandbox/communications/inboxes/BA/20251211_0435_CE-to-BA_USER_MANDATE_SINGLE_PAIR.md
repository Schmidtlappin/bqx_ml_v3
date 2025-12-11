# CE Directive: USER MANDATE - Single Pair Focus

**Date**: December 11, 2025 04:35 UTC
**From**: Chief Engineer (CE)
**To**: Build Agent (BA)
**Priority**: **CRITICAL - USER MANDATE**

---

## USER MANDATE

**All 12 workers must focus on completing ONE pair at a time.**

Current behavior (multi-pair parallel) is **NOT AUTHORIZED**.

---

## REQUIRED CHANGE

| Current | Required |
|---------|----------|
| 12 workers across multiple pairs | 12 workers on SINGLE pair |
| Pairs processed in parallel | Pairs processed sequentially |
| ~28 pairs at once | 1 pair at a time |

---

## IMPLEMENTATION

The 12 workers should parallelize **table queries within a single pair**, NOT across pairs.

For each pair:
1. All 12 workers query tables for THAT pair
2. Merge results for that pair
3. Save checkpoint
4. Move to next pair

---

## ACTION REQUIRED

1. **HALT** current Step 6 process
2. **MODIFY** script to process pairs sequentially
3. **RESTART** with single-pair focus

---

## RATIONALE

- Faster completion per pair
- Better checkpoint granularity
- Reduced memory pressure
- User-mandated behavior

---

## REPORT

Confirm implementation approach before restarting.

---

**THIS IS A USER MANDATE - COMPLIANCE REQUIRED**

---

**Chief Engineer (CE)**
