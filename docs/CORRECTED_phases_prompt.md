# CORRECTED Phases Prompt - Uses Actual Fields

## Deploy lines 5-120 to Phases.record_audit

```
Evaluate this Phases record for strategic planning quality.

OUTPUT FIRST LINE MUST BE: Score: [number]

PHASES FOCUS: Budget, Timeline, Quantified Deliverables, Success Metrics

Step 1: Calculate Base Score
Start with: 30 points

Step 2: Check Critical Requirements
Notes length: {notes}
Estimated budget: {estimated_budget}
Deliverables: {deliverables}
Duration: {duration}

- Notes < 300 chars? PENALTY -60 points
- No estimated_budget? PENALTY -40 points
- No deliverables listed? PENALTY -30 points
- No duration specified? PENALTY -20 points

Step 3: Detect Generic Content
Look for these worthless phrases:
- "Complete phase" → PENALTY -50
- "Execute stages" → PENALTY -50
- "As per plan" → PENALTY -50
- "Implement functionality" → PENALTY -50

Step 4: Score Each Field
phase_id: {phase_id}
- Valid MP##.P## format? Add 5 points

name: {name}
- Specific phase with scope? Add 15 points
- Generic? Add 3 points

description: {description}
- Has objectives + deliverables + metrics? Add 25 points
- Some details? Add 10 points
- Vague? Add 0 points

notes: {notes}
- Resource allocation details? Add 10 points
- Technology specifications? Add 10 points
- Success criteria defined? Add 10 points
- Timeline breakdown? Add 5 points
Total possible for notes: 35 points

estimated_budget: {estimated_budget}
- Present and > 0? Add 10 points
- Missing or 0? Add 0 points

deliverables: {deliverables}
- 3+ specific items? Add 10 points
- 1-2 items? Add 5 points
- Empty? Add 0 points

milestones: {milestones}
- Clear timeline? Add 5 points
- Vague/missing? Add 0 points

status: {status}
- Valid status? Add 5 points

Step 5: Apply Major Penalties
- No quantified deliverables: -40
- No budget (estimated_budget = 0): -30
- No timeline/duration: -20
- Notes < 300 characters: -60

Step 6: Calculate Final Score
Total = Base (30) + Field Points - Penalties
Minimum: 1
Maximum: 100

Step 7: Generate Output
Score: [Total]
Planning Quality: [Poor/Fair/Good/Excellent]
Budget: ${estimated_budget}
Deliverables Count: [Number of items in deliverables]
Duration: {duration}

Remediation (if score < 60):
"PHASE LACKS PLANNING. Required:
1. Set estimated_budget > 0 (current: {estimated_budget})
2. List specific deliverables (current: {deliverables})
3. Define clear milestones with dates
4. Expand notes to >300 characters with resource details
5. Include measurable success criteria (R² > 0.30)"
```

## Key Changes Made

1. **Removed**: `{source}` field reference (doesn't exist)
2. **Added**: `{estimated_budget}` - actual budget field!
3. **Added**: `{deliverables}` - itemized outputs!
4. **Added**: `{milestones}` - timeline tracking!
5. **Added**: `{duration}` - phase duration!

## Important Note

The `record_score` field also doesn't exist. You may need to:
1. Create a `record_score` field in AirTable (Number type)
2. Or configure the AI to extract score from record_audit

## Deployment Instructions

1. Copy lines 5-120
2. Go to AirTable → Phases table → record_audit field
3. Click "Configure AI"
4. Paste the corrected prompt
5. Save and wait 10-30 minutes