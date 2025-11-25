# Simple Tasks Prompt - Minimal Version with Remediation

## Deploy lines 5-150 to Tasks.record_audit

```
Score the quality of this Tasks table record.

FIRST LINE MUST BE: Score: [number]

## Scoring Rules

1. If description is empty or < 20 characters:
   - Maximum score is 55
   - Empty means: "", null, whitespace only, or < 20 chars

2. Base scoring:
   - Start at 40 points
   - Add points for good content:
     * Valid task_id format: +5
     * Good name: +15
     * Good description: +20
     * Good notes with code: +30
     * Valid source: +5
     * Valid links: +10
   - Maximum: 100 points

3. Check description FIRST:
   {description}

   If length < 20: MAX SCORE = 55

## Field Evaluation

task_id: {task_id}
- MP##.P##.S##.T## format? +5 points

name: {name}
- Specific with metrics? +15 points
- Generic? +3 points

description: {description}
- Empty or < 20 chars? 0 points (cap score at 55)
- 20-99 chars? +5 points
- 100+ chars with details? +20 points

notes: {notes}
- Has Python/SQL code blocks? +30 points
- Just text? +10 points
- Empty? 0 points

source: {source}
- Valid .py file? +5 points

stage_link: {stage_link}
- Valid? +5 points

status: {status}
- Valid? +5 points

## Calculate Final Score

1. Start: 40 points
2. Add field points (max +85)
3. If description < 20 chars: Cap at 55
4. Range: 1-100 (never 0)

## Output Format

Score: [1-100]
Description: [length] chars
Issues: [list any problems]
Remediation: [specific fixes needed]

## Remediation Guidance

If score < 70, provide specific fixes:

For empty description (score ≤55):
"CRITICAL: Add description (100+ chars). Include what this task does, methods used, and expected outcomes. This caps score at 55."

For missing code (score < 80):
"Add Python/SQL code blocks to notes. Include actual implementation from scripts/*.py files with BQX calculations."

For thin content (score < 90):
"Expand notes with:
- Code blocks showing implementation
- BQX window calculations [45,90,180,360,720,1440,2880]
- Specific thresholds (R²=0.35, PSI=0.22)
- Table schemas if applicable"

For good content (score ≥90):
"Good quality. Minor improvements: [specific suggestions]"
```

## Key Features

1. **Simple scoring logic** - Easy for AI to follow
2. **Clear output format** - Always starts with "Score:"
3. **Specific remediation** - Actionable guidance based on score
4. **Empty description handling** - Explicit cap at 55
5. **150 lines total** - Half the size of complex version

## Deployment

1. Copy lines 5-150
2. Paste into Tasks table → record_audit field → Configure AI
3. Save and wait 10-30 minutes

## Expected Behavior

- Empty descriptions will score ≤55
- All outputs start with "Score: [number]"
- Clear remediation guidance for improvements
- Scores range 1-100 (never 0)