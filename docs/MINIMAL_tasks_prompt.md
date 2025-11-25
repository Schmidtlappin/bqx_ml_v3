# Minimal Tasks Prompt - Description-Focused

## Deploy lines 5-75 to Tasks.record_audit

```
Output format: Score: [number]

Check description field first:
{description}

If description is empty (less than 20 characters):
  Maximum score is 55

Scoring:
1. Base: 40 points
2. Add points:
   - task_id valid: +5
   - name good: +15
   - description good: +20 (BUT 0 if empty)
   - notes with code: +30
   - source valid: +5
   - links valid: +10

3. Final score: 1-100
   If description empty: cap at 55

Output:
Score: [calculated score]
Description: [character count] chars
Issues: [if description empty: "Empty description caps score at 55"]
Remediation: [what to fix]
```

## Critical Logic Flow

```
1. FIRST: Check description length
2. IF < 20 chars: Set max_possible = 55
3. Calculate normal score
4. IF score > max_possible: score = max_possible
5. Output Score: [number] as FIRST line
```

## Why This Works

1. **Ultra-simple**: 75 lines instead of 300+
2. **Description check FIRST**: Can't miss it
3. **Clear cap logic**: If empty, max is 55
4. **Minimal complexity**: AI agent can follow this

## Expected Behavior

- Empty descriptions → Score ≤55
- Good content → Score up to 100
- ALWAYS outputs "Score: [number]" first

## Test Cases

**Empty Description:**
- Input: description = ""
- Expected: Score: 55 or less
- Output includes: "Empty description caps score at 55"

**Good Description:**
- Input: description = "Calculate BQX momentum using 360-bar window with R²>0.35 threshold"
- Expected: Score: 70-100
- No cap applied