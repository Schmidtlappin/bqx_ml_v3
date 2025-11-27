# AirTable Status Icon Reference Guide

**Version**: 2.0
**Date**: November 27, 2025
**Purpose**: Complete reference for all status icons and their usage in AirTable notes headers
**Compliance**: MANDATORY for all agents and updates

---

## 🎯 COMPLETE STATUS ICON SET

### Standard Status Icons (7 Total)

| Icon | Status | Header Format | Color | Usage | Transition |
|------|--------|---------------|-------|-------|------------|
| 📋 | **TODO** | `📋 PLANNED: [timestamp]` | Gray | Task planned but not started | → In Progress, Cancelled, Restated |
| 🔄 | **IN PROGRESS** | `🔄 IN PROGRESS: [timestamp]` | Blue | Actively being worked on | → Done, Blocked, Cancelled, Restated |
| ✅ | **DONE** | `✅ COMPLETED: [timestamp]` | Green | Successfully completed | → Restated (only if scope changes) |
| 🚫 | **BLOCKED** | `🚫 BLOCKED: [timestamp]` | Red | Cannot proceed due to dependency | → In Progress, Cancelled, Restated |
| ❌ | **CANCELLED** | `❌ CANCELLED: [timestamp]` | Dark Red | No longer needed/superseded | Terminal state (no transitions) |
| 🔀 | **RESTATED** | `🔀 RESTATED: [timestamp]` | Orange | Reformulated with new scope | → Todo, In Progress |
| ⏸️ | **NOT STARTED** | `⏸️ NOT STARTED: [timestamp]` | Light Gray | Explicitly deferred | → In Progress, Cancelled, Restated |

---

## 📝 NOTES HEADER FORMAT

### Required Structure
```
[ICON] [STATUS_TEXT]: [ISO_TIMESTAMP]
================================================
[CONTENT]
================================================
```

### Real Examples
```
✅ COMPLETED: 2025-11-27T00:29:11.102885
================================================
Task successfully finished with all objectives met.
Results validated against quality gates.
================================================

❌ CANCELLED: 2025-11-27T01:45:32.456789
================================================
REASON FOR CANCELLATION
• Superseded by Smart Dual Processing approach
• Original approach showed poor performance (R² = 0.27)
================================================

🔀 RESTATED: 2025-11-27T02:15:45.789012
================================================
TASK REFORMULATION
Original: Implement all 6000 features
Restated: Test all 6000 features, keep those with >1% improvement
================================================
```

---

## 🔄 RATIONALIZATION FOR EXPANDED ICONS

### Why Cancelled Status (❌)
**Problem Solved**: Without explicit cancellation tracking, obsolete tasks could be accidentally worked on, wasting valuable development time.

**Benefits**:
1. **Clear Obsolescence**: Immediately visible when tasks are no longer needed
2. **Prevent Wasted Work**: No agent will accidentally implement cancelled tasks
3. **Audit Trail**: Documents why approaches were abandoned
4. **Project Evolution**: Shows learning and optimization over time

**Common Scenarios**:
- Naive approaches superseded by optimized versions
- Unrealistic targets adjusted after user feedback
- Duplicate tasks identified and consolidated
- Technology choices changed (e.g., TFT not needed when XGBoost sufficient)

### Why Restated Status (🔀)
**Problem Solved**: Requirements often evolve, but without tracking reformulation, the original intent gets lost and confusion arises.

**Benefits**:
1. **Requirements Clarity**: Shows exact evolution of task scope
2. **Expectation Management**: Documents changing targets
3. **Learning Documentation**: Captures project refinement
4. **Prevents Confusion**: Clear distinction between original and current scope

**Common Scenarios**:
- Accuracy targets adjusted (95% → 85-88%)
- Scope refined (implement all → test all, keep beneficial)
- Approach clarified (must use → test if needed)
- Understanding improved (BQX lag insight changes approach)

---

## 🚀 IMPLEMENTATION GUIDELINES

### For All Agents

1. **Reading Tasks**: Check icon first to understand current state
2. **Updating Tasks**: Always use correct icon for new status
3. **Append Mode**: New updates on top, preserve all history
4. **Terminal States**: Never transition from Cancelled
5. **Reformulation**: Use Restated when scope changes, not for minor edits

### Status Selection Logic
```python
def get_status_icon(task_state):
    """Return appropriate icon and header text"""
    status_map = {
        'todo': ('📋', 'PLANNED'),
        'in_progress': ('🔄', 'IN PROGRESS'),
        'done': ('✅', 'COMPLETED'),
        'blocked': ('🚫', 'BLOCKED'),
        'cancelled': ('❌', 'CANCELLED'),
        'restated': ('🔀', 'RESTATED'),
        'not_started': ('⏸️', 'NOT STARTED')
    }

    icon, text = status_map.get(task_state.lower(), ('📋', 'PLANNED'))
    timestamp = datetime.now().isoformat()

    return f"{icon} {text}: {timestamp}"
```

---

## ⚠️ CRITICAL RULES

### ALWAYS:
✅ Use exact icon from this reference
✅ Include timestamp in ISO format
✅ Keep status text in UPPERCASE
✅ Use 48 equals signs for separators
✅ Append new updates on top

### NEVER:
❌ Mix icons (e.g., using 🛑 instead of 🚫)
❌ Skip timestamps
❌ Delete previous updates
❌ Transition from Cancelled status
❌ Use lowercase status text

---

## 📊 QUICK REFERENCE TABLE

```
Status         Icon  Color      Next States
─────────────────────────────────────────────
Todo           📋    Gray       → Progress/Cancel/Restate
In Progress    🔄    Blue       → Done/Block/Cancel/Restate
Done           ✅    Green      → Restate (rare)
Blocked        🚫    Red        → Progress/Cancel/Restate
Cancelled      ❌    Dark Red   → [Terminal]
Restated       🔀    Orange     → Todo/Progress
Not Started    ⏸️    Lt Gray    → Progress/Cancel/Restate
```

---

## 🔧 TOOLS & SCRIPTS

- **Append Tool**: `/scripts/append_airtable_note.py`
- **Audit Tool**: `/scripts/audit_airtable_status_candidates.py`
- **Apply Changes**: `/scripts/apply_status_changes.py`
- **Standards File**: `/intelligence/airtable_standards.json`

---

## 📚 RELATED DOCUMENTATION

- [AIRTABLE_STATUS_STANDARDIZATION_GUIDE.md](./AIRTABLE_STATUS_STANDARDIZATION_GUIDE.md)
- [AIRTABLE_NOTES_STANDARDIZATION_GUIDE_V2.md](./AIRTABLE_NOTES_STANDARDIZATION_GUIDE_V2.md)
- [airtable_standards.json](/intelligence/airtable_standards.json)
- [mandates.json](/intelligence/mandates.json)

---

## ✅ COMPLIANCE

**Effective**: Immediately
**Enforcement**: All AirTable updates must use these exact icons
**Validation**: Automated checks will reject non-compliant updates
**Questions**: Refer to this guide or check intelligence files

---

**Last Updated**: 2025-11-27T01:45:00.000000
**Status**: ACTIVE
**Compliance**: MANDATORY