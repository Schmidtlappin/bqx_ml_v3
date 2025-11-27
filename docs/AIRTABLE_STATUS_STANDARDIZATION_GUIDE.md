# AirTable Status Field Standardization Guide

**Date**: November 27, 2025
**Version**: 1.0
**Purpose**: Define and standardize status options across all AirTable tables
**Critical Addition**: CANCELLED and RESTATED statuses

---

## 📋 STANDARDIZED STATUS OPTIONS

### Complete Status Set (7 Options):

| Status | Icon | Color | Usage | When to Apply |
|--------|------|-------|-------|---------------|
| **Todo** | 📋 | Gray | Task planned but not started | Initial state, waiting to begin |
| **In Progress** | 🔄 | Blue | Actively being worked on | Work has started |
| **Done** | ✅ | Green | Successfully completed | All objectives achieved |
| **Blocked** | 🚫 | Red | Cannot proceed due to dependency | External blocker identified |
| **Cancelled** | ❌ | Dark Red | No longer needed/superseded | Task obsolete or approach changed |
| **Restated** | 🔀 | Orange | Reformulated with new scope | Requirements clarified/changed |
| **Not Started** | ⏸️ | Light Gray | Explicitly deferred | Consciously postponed |

---

## ❌ CANCELLED STATUS

### Definition:
Task that was planned but will NOT be executed because it's no longer relevant, needed, or has been superseded by a better approach.

### When to Use:
1. **Approach Changed**: Original task obsolete due to architectural pivot
2. **Superseded**: Another task/approach replaces this one
3. **No Longer Needed**: Requirements changed, making task unnecessary
4. **Duplicate**: Task redundant with another existing task
5. **Out of Scope**: Determined to be beyond project requirements

### Examples:
- Naive dual processing tasks (superseded by Smart Dual)
- TFT implementation (if XGBoost sufficient)
- 95% accuracy tasks (if 88% accepted as realistic)
- Duplicate feature engineering tasks

### Notes Format:
```
❌ CANCELLED: 2025-11-27T05:00:00.000000
================================================
REASON FOR CANCELLATION
Task superseded by Smart Dual Processing approach.
Original approach (naive dual) showed poor results.
New approach (Smart Dual) eliminates need for this task.

REPLACEMENT
See MP03.P01.S01.T05 for Smart Dual implementation.
================================================
```

---

## 🔀 RESTATED STATUS

### Definition:
Task that has been reformulated with different scope, approach, or requirements but represents the same fundamental work.

### When to Use:
1. **Scope Clarified**: Original vague, now specific
2. **Requirements Changed**: User clarified expectations
3. **Approach Refined**: Better method identified
4. **Target Adjusted**: Performance goals modified
5. **Context Updated**: New information changes task definition

### Examples:
- "Implement all 6000 features" → "Test 6000, keep best 300"
- "Achieve 95% accuracy" → "Achieve 85-88% realistic target"
- "Use all features" → "Test all, operationalize improvements"

### Notes Format:
```
🔀 RESTATED: 2025-11-27T05:00:00.000000
================================================
TASK REFORMULATION
Original: Implement all 6000 features for 95% accuracy
Restated: Test 6000 features, keep 200-300 that improve performance

REASON
User clarified that comprehensive testing with selective retention
is the goal, not blind implementation of all features.

NEW APPROACH
Systematic testing with >1% improvement threshold.
================================================
```

---

## 📊 STATUS TRANSITION RULES

### Valid Transitions:

```mermaid
graph LR
    Todo --> InProgress
    Todo --> Cancelled
    Todo --> Restated

    NotStarted --> InProgress
    NotStarted --> Cancelled
    NotStarted --> Restated

    InProgress --> Done
    InProgress --> Blocked
    InProgress --> Cancelled
    InProgress --> Restated

    Blocked --> InProgress
    Blocked --> Cancelled
    Blocked --> Restated

    Restated --> Todo
    Restated --> InProgress

    Done --> Restated[Only if scope changes]

    Cancelled --> [Terminal State]
```

### Invalid Transitions:
- Cancelled → Any (terminal state)
- Done → In Progress (create new task instead)
- Done → Blocked (completed tasks can't be blocked)

---

## 🔍 AUDIT CRITERIA

### Tasks That Should Be CANCELLED:

1. **Naive Dual Processing Tasks**
   - Superseded by Smart Dual approach
   - Poor performance (R² = 0.27 vs 0.94)

2. **Excessive Complexity Tasks**
   - "Implement all 6000 features"
   - "Use every possible algorithm"

3. **Unrealistic Targets**
   - "95% exact value prediction"
   - "Perfect accuracy requirements"

4. **Duplicate Tasks**
   - Multiple tasks for same outcome
   - Redundant implementations

### Tasks That Should Be RESTATED:

1. **Vague Original Scope**
   - "Improve model performance"
   - "Add advanced features"

2. **Changed Requirements**
   - Performance targets adjusted
   - Approach clarified by user

3. **Refined Understanding**
   - BQX lag insight changes approach
   - Feature selection strategy clarified

---

## 🎯 STANDARDIZATION REQUIREMENTS

### For All Tables:
1. Update status field to include all 7 options
2. Apply consistent icons in notes
3. Use standardized color coding
4. Follow transition rules

### For All Agents:
1. Check current status before updating
2. Use appropriate status for situation
3. Document reason when cancelling/restating
4. Preserve history in notes (append mode)

---

## 📝 IMPLEMENTATION CHECKLIST

### Immediate Actions:
- [ ] Update Tasks table status field options
- [ ] Update Stages table status field options
- [ ] Update Phases table status field options
- [ ] Audit existing records for cancellation candidates
- [ ] Audit existing records for restatement candidates
- [ ] Update intelligence files with new statuses

### Cancellation Candidates:
1. Naive dual processing tasks
2. Unrealistic 95% accuracy tasks
3. "Implement all features" tasks
4. Duplicate feature engineering tasks
5. Obsolete simulation tasks

### Restatement Candidates:
1. Master objective tasks (95% → 88%)
2. Feature implementation tasks (all → selective)
3. Algorithm selection tasks (must use → test if needed)
4. Data requirement tasks (synthetic → real when available)

---

## 🔧 AGENT GUIDANCE

### When Starting Work:
1. Check if task might be obsolete (consider cancelling)
2. Check if requirements changed (consider restating)
3. Update status appropriately
4. Document decision in notes

### Status Selection Logic:
```python
def select_status(task, context):
    if task.no_longer_needed():
        return "Cancelled"

    if task.requirements_changed():
        return "Restated"

    if task.has_blockers():
        return "Blocked"

    if task.work_started():
        return "In Progress"

    if task.completed():
        return "Done"

    return "Todo"
```

### Documentation Requirements:
- **Cancelled**: Must explain why and what replaces it
- **Restated**: Must explain what changed and why
- **All statuses**: Must use append mode with timestamps

---

## 📊 METRICS & COMPLIANCE

### Success Metrics:
- No ambiguous task states
- Clear project evolution tracking
- Reduced duplicate work
- Better requirement alignment

### Compliance Check:
- All status changes documented
- Reasons provided for cancellations
- Restatements include new scope
- History preserved in append mode

---

## ✅ BENEFITS

1. **Clarity**: True state of every task visible
2. **Efficiency**: No work on obsolete tasks
3. **Tracking**: Project evolution documented
4. **Alignment**: Tasks match current requirements
5. **Audit Trail**: Decisions and changes tracked

---

**Status**: ACTIVE
**Enforcement**: IMMEDIATE
**Applies To**: All AirTable tables and all agents