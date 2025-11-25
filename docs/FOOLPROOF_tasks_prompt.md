# Foolproof Tasks Prompt - Step by Step

## Deploy lines 5-95 to Tasks.record_audit

```
Evaluate this Tasks record.

Step 1: Count description length
{description}
Length = [count characters]

Step 2: Determine max possible score
If length < 20: MAX_SCORE = 55
If length >= 20: MAX_SCORE = 100

Step 3: Calculate base score
Start with: 40 points

Step 4: Add quality points
task_id is valid MP##.P##.S##.T## format? Add 5
name is specific? Add up to 15
description length >= 100? Add 20
description length 20-99? Add 5
description length < 20? Add 0
notes has code blocks? Add up to 30
source is valid .py file? Add 5
stage_link exists? Add 5
status is valid? Add 5

Step 5: Calculate total
Total = base + quality points

Step 6: Apply cap
If description < 20 chars AND total > 55:
  Final = 55
Else:
  Final = total

Step 7: Ensure range
If Final < 1: Final = 1
If Final > 100: Final = 100

OUTPUT (first line MUST be Score):
Score: [Final]
Description length: [Length] chars
Capped: [Yes if description < 20, No otherwise]
```

## Deployment Instructions

1. Copy lines 5-95
2. Go to AirTable → Tasks table → record_audit field
3. Click "Configure AI"
4. Replace entire prompt
5. Save

## Why This Should Work

1. **Step-by-step**: AI follows numbered steps
2. **Explicit math**: Shows calculation process
3. **Clear cap logic**: Step 6 explicitly handles the 55 cap
4. **Simple output**: Just Score, length, and cap status

## Test Verification

After deployment, test with:
- Task with empty description
- Expected: Score ≤55, "Capped: Yes"

## Summary of ALL Prompts Created

| File | Lines | Complexity | Issue |
|------|-------|------------|-------|
| bulletproof_record_audit_prompt.md | 340 | Too complex | AI ignored critical parts |
| FINAL_tasks_prompt.md | 298 | Too complex | Didn't output "Score:" first |
| ULTRA_STRICT_tasks_prompt.md | 220 | Still complex | Too many warnings |
| SIMPLE_tasks_prompt.md | 150 | Moderate | Drifted from core issue |
| MINIMAL_tasks_prompt.md | 75 | Minimal | Good but needs more explicit steps |
| **FOOLPROOF_tasks_prompt.md** | **95** | **Step-by-step** | **Explicit numbered steps** |

This FOOLPROOF version is the most explicit about the cap logic.