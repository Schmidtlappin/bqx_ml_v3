# AirTable Notes Field Standardization Guide

**Date**: November 27, 2025
**Purpose**: Ensure consistent formatting of all AirTable task notes
**Scope**: All agents maintaining BQX ML V3 project in AirTable

---

## 📋 STANDARDIZED NOTES FORMAT

### Required Header Structure:
```
[STATUS_ICON] [STATUS_TEXT]: [ISO_TIMESTAMP]
================================================
[CONTENT]
================================================
```

---

## 🎯 STATUS ICONS AND USAGE

### Standard Status Icons:

| Icon | Status | Color | Usage |
|------|--------|-------|-------|
| ✅ | COMPLETED | Green | Task successfully finished |
| 🔄 | IN PROGRESS | Blue | Task actively being worked on |
| 📋 | PLANNED | Gray | Task scheduled but not started |
| 🚫 | BLOCKED | Red | Task blocked by dependency/issue |

---

## 📝 FORMATTING SPECIFICATIONS

### Timestamp Format:
- **ISO 8601**: `YYYY-MM-DDTHH:MM:SS.mmmmmm`
- **Example**: `2025-11-27T00:29:11.102885`
- **Generator**: Python `datetime.now().isoformat()`

### Content Structure:
```
[ICON] [STATUS]: [TIMESTAMP]
================================================
[SECTION 1 TITLE]
- Point 1
- Point 2
- Point 3

[SECTION 2 TITLE]
• Detail 1
• Detail 2
• Detail 3

[METRICS/RESULTS]
Key Metric: Value
Performance: Result
Impact: Description
================================================
```

---

## ✅ EXAMPLES

### Completed Task:
```
✅ COMPLETED: 2025-11-27T00:29:11.102885
================================================
SMART DUAL PROCESSING IMPLEMENTED
- 12 features selected and weighted
- IDX features: weight 2.0-1.2 (leading indicators)
- BQX features: weight 1.0-0.7 (momentum context)
- Derived features: weight 0.8-0.6 (relationships)

RESULTS ACHIEVED
• R² Score: 0.9362 (267% of target)
• Directional Accuracy: 94.89%
• Training Time: 25.1 minutes

All quality gates exceeded successfully.
================================================
```

### In Progress Task:
```
🔄 IN PROGRESS: 2025-11-27T03:15:00.000000
================================================
TRIANGULATION FEATURE TESTING
- Testing 378 currency triangles
- EUR-GBP-USD triangle complete (R² improvement: +0.023)
- USD-JPY-EUR triangle in testing
- 10 of 378 triangles evaluated

CURRENT STATUS
• Triangles Tested: 10/378 (2.6%)
• Average Improvement: +2.1% R²
• Expected Completion: 4 hours

Preliminary results promising.
================================================
```

### Planned Task:
```
📋 PLANNED: 2025-11-27T03:20:00.000000
================================================
CORRELATION NETWORK IMPLEMENTATION
Scheduled to begin after triangulation testing.

SCOPE
- 28×28 correlation matrix (784 pairs)
- Multiple rolling windows (10, 20, 50, 100, 200)
- Eigenvalue decomposition
- Network centrality measures

EXPECTED IMPACT
• Performance Gain: +4-6% R²
• Timeline: Week 2
• Priority: High

Awaiting triangulation results before starting.
================================================
```

### Blocked Task:
```
🚫 BLOCKED: 2025-11-27T03:25:00.000000
================================================
MARKET MICROSTRUCTURE FEATURES
Cannot proceed without institutional data access.

BLOCKING ISSUES
- Missing spread data
- No order flow information
- Market depth unavailable
- Premium data feed required ($1,000/month)

MITIGATION OPTIONS
• Use synthetic spread estimates
• Skip microstructure features
• Acquire data subscription

Decision required from project owner.
================================================
```

---

## 🔧 IMPLEMENTATION GUIDANCE

### For Python Scripts:
```python
from datetime import datetime

def format_airtable_note(status, content):
    """
    Format note according to standardization guide
    """
    icons = {
        'completed': '✅',
        'in_progress': '🔄',
        'planned': '📋',
        'blocked': '🚫'
    }

    icon = icons.get(status.lower(), '📋')
    timestamp = datetime.now().isoformat()

    note = f"""{icon} {status.upper()}: {timestamp}
================================================
{content}
================================================"""

    return note
```

### For Manual Updates:
1. Copy the appropriate icon from the guide
2. Add status text in CAPS
3. Generate timestamp: `datetime.now().isoformat()`
4. Use exactly 48 equals signs for separators
5. Structure content with clear sections

---

## 📊 VALIDATION CHECKLIST

Before saving any AirTable note, verify:

- [ ] Correct status icon used
- [ ] Status text in UPPERCASE
- [ ] Valid ISO timestamp
- [ ] Exactly 48 equals signs in separators
- [ ] Content organized in sections
- [ ] Key metrics/results included
- [ ] No formatting inconsistencies

---

## 🚀 MIGRATION REQUIREMENTS

### Existing Notes Update:
All existing task notes must be updated to follow this standard:

1. **Priority 1**: Active (In Progress) tasks
2. **Priority 2**: Recently completed tasks (last 7 days)
3. **Priority 3**: Blocked tasks
4. **Priority 4**: All remaining tasks

### Timeline:
- Immediate: New tasks must use this format
- Within 24 hours: All active tasks updated
- Within 48 hours: All tasks standardized

---

## ⚠️ COMPLIANCE

### Mandatory Requirements:
- All agents MUST follow this format
- No variations allowed without approval
- Automated validation will be implemented
- Non-compliant updates will be rejected

### Exceptions:
- Legacy tasks created before 2025-11-27 may retain original format until migration
- System-generated notes may use alternative format if clearly marked

---

## 📞 SUPPORT

For questions about this standardization:
- Reference: `/docs/AIRTABLE_NOTES_STANDARDIZATION_GUIDE.md`
- Update intelligence files: `/intelligence/airtable_standards.json`
- Contact: Chief Engineer (BQX ML V3)

---

**Document Status**: ACTIVE
**Version**: 1.0
**Effective Date**: 2025-11-27T03:30:00.000000