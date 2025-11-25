# Rationalized PHASES Prompt - Strategic Planning Quality

## Deploy lines 5-120 to Phases.record_audit

```
Evaluate this Phases record for strategic planning quality.

OUTPUT FIRST LINE MUST BE: Score: [number]

PHASES FOCUS: Budget, Timeline, Quantified Deliverables, Success Metrics

Step 1: Calculate Base Score
Start with: 30 points

Step 2: Check Critical Requirements
Notes length: {notes}
- Less than 300 chars? PENALTY -60 points
- Contains dollar amounts? (e.g., $5,000)
- Contains hour estimates? (e.g., 80 hours)
- Contains countable deliverables? (e.g., 28 models, 112 tables)
- Contains success metrics? (e.g., R² > 0.30, Sharpe > 1.5)

Step 3: Detect Generic Content
Look for these worthless phrases:
- "Complete phase" → PENALTY -50
- "Execute stages" → PENALTY -50
- "As per plan" → PENALTY -50
- "Implement functionality" → PENALTY -50

Step 4: Score Each Field
phase_id: {phase_id}
- Valid P## format? Add 5 points

name: {name}
- Specific phase with scope? Add 15 points
- Generic? Add 3 points

description: {description}
- Has objectives + deliverables + metrics? Add 25 points
- Some details? Add 10 points
- Vague? Add 0 points

notes: {notes}
MUST CONTAIN:
- Resource estimates ($X,XXX, XX hours)? Add 10 points
- Quantified deliverables (28 models)? Add 10 points
- Timeline specifics? Add 10 points
- Success criteria (R² > 0.30)? Add 5 points
Total possible for notes: 35 points

source: {source}
- Valid file path? Add 5 points

status: {status}
- Valid status? Add 10 points

Step 5: Apply Major Penalties
- No quantified deliverables (missing numbers): -40
- No resource estimates (missing $ or hours): -30
- No success metrics: -20
- Notes < 300 characters: -60

Step 6: Calculate Final Score
Total = Base (30) + Field Points - Penalties
Minimum: 1
Maximum: 100

Step 7: Generate Output
Score: [Total]
Planning Quality: [Poor/Fair/Good/Excellent]
Budget Found: [Yes/No]
Timeline Found: [Yes/No]
Deliverables Quantified: [Yes/No]
Success Metrics: [Yes/No]

Remediation (if score < 60):
"PHASE LACKS PLANNING. Required:
1. Quantify ALL deliverables (e.g., '28 models', not 'models')
2. Provide resource estimates (hours and $ costs)
3. Specify exact technologies (Vertex AI, BigQuery, XGBoost)
4. Include measurable success criteria (R² > 0.30)
5. Expand notes to >300 characters with concrete details"
```

## Key Assessment Points

**What Makes a GOOD Phase (Score 65-80):**
- Budget explicitly stated: "$5,000 compute + $2,000/month"
- Hours quantified: "80 hours development, 40 hours validation"
- Deliverables countable: "28 production models, 112 BigQuery tables"
- Success measurable: "R² > 0.30, Sharpe > 1.5, latency < 100ms"

**What Makes a BAD Phase (Score 0-40):**
- Vague: "Train models for the project"
- No numbers: "Requires cloud resources"
- No timeline: "Complete when ready"
- No success criteria: "Good performance"

## Deployment

1. Copy lines 5-120
2. Navigate to AirTable → Phases table → record_audit field
3. Click "Configure AI"
4. Replace entire prompt
5. Save and wait 10-30 minutes