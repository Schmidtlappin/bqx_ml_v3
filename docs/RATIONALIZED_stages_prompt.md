# Rationalized STAGES Prompt - Tactical Deliverables Quality

## Deploy lines 5-125 to Stages.record_audit

```
Evaluate this Stages record for tactical planning quality.

OUTPUT FIRST LINE MUST BE: Score: [number]

STAGES FOCUS: Named Deliverables, Technical Approach, Dependencies, Task Count

Step 1: Calculate Base Score
Start with: 35 points

Step 2: Check Critical Requirements
Notes length: {notes}
- Less than 400 chars? PENALTY -60 points
- Contains named outputs? (e.g., lag_bqx_eurusd table)
- Contains technical method? (e.g., PurgedTimeSeriesSplit)
- Contains dependencies? (e.g., Requires S02.14 complete)
- Contains task count? (e.g., 12 tasks, 24 hours)

Step 3: Detect Generic Content
Look for these worthless phrases:
- "Implement functionality" → PENALTY -50
- "Execute tasks" → PENALTY -50
- "As specified" → PENALTY -50
- "Complete stage" → PENALTY -50

Step 4: Score Each Field
stage_id: {stage_id}
- Valid MP##.P##.S## format? Add 5 points

name: {name}
- Specific objective with deliverable named? Add 15 points
- Generic action? Add 3 points

description: {description}
- Has scope + approach + deliverables? Add 20 points
- Some specifics? Add 10 points
- Vague? Add 0 points

notes: {notes}
MUST CONTAIN:
- 3+ named deliverables (table/model names)? Add 15 points
- Technical approach specified? Add 10 points
- Dependencies listed? Add 5 points
- Task count and hours? Add 5 points
Total possible for notes: 35 points

source: {source}
- Valid .py or .md file? Add 5 points

phase_link: {phase_link}
- Valid link? Add 5 points

status: {status}
- Valid status? Add 5 points

Step 5: Apply Major Penalties
- No concrete deliverables (missing names): -40
- No technical approach: -30
- No dependencies listed: -20
- Notes < 400 characters: -60

Step 6: Calculate Final Score
Total = Base (35) + Field Points - Penalties
Minimum: 1
Maximum: 100

Step 7: Generate Output
Score: [Total]
Deliverable Quality: [Poor/Fair/Good/Excellent]
Named Outputs: [Count found]
Technical Method: [Yes/No]
Dependencies: [Yes/No]
Task Count: [Number or "Not specified"]

Remediation (if score < 60):
"STAGE LACKS SPECIFICATIONS. Required:
1. List exact deliverables (e.g., '28 train_* tables, 196 models')
2. Specify technical approach with methods
3. Provide task count and hour estimates
4. Include dependencies on other stages
5. Expand notes to >400 characters with concrete details"
```

## Key Assessment Points

**What Makes a GOOD Stage (Score 60-75):**
- Deliverables named: "28 lag_bqx_* tables, 28 regime_bqx_* tables"
- Technical clear: "SQL window functions with ROWS BETWEEN"
- Dependencies explicit: "Requires S02.14 regression_bqx_* tables"
- Tasks quantified: "12 tasks, estimated 24 hours"

**What Makes a BAD Stage (Score 0-25):**
- Vague: "Create feature tables"
- No names: "Generate features"
- No method: "Process data"
- No dependencies: "After previous work"

## Deployment

1. Copy lines 5-125
2. Navigate to AirTable → Stages table → record_audit field
3. Click "Configure AI"
4. Replace entire prompt
5. Save and wait 10-30 minutes