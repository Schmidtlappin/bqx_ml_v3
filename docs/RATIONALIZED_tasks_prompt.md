# Rationalized TASKS Prompt - Implementation Code Quality

## Deploy lines 5-140 to Tasks.record_audit

```
Evaluate this Tasks record for implementation quality.

OUTPUT FIRST LINE MUST BE: Score: [number]

TASKS FOCUS: Executable Code, Specific Values, BQX Windows, Complete Formulas

Step 1: Calculate Base Score
Start with: 40 points

Step 2: Check Critical Requirements
Notes length: {notes}
- Less than 500 chars? PENALTY -60 points
- Contains ```python or ```sql code blocks?
- Code blocks have 5+ lines each?
- Need at least 2 code blocks for full points
- Contains specific values? (R²=0.35, not "good R²")
- References BQX windows? [45,90,180,360,720,1440,2880]

Step 3: Detect Generic Content
Look for these worthless phrases:
- "Complete implementation" → PENALTY -50
- "As per specifications" → PENALTY -50
- "TODO: implement" → PENALTY -50
- "Use appropriate values" → PENALTY -50

Step 4: Count Valid Code Blocks
Valid code must have:
- Proper syntax (def, class, SELECT, CREATE)
- 5+ lines of executable code
- Not just imports or comments
- BQX-specific implementation

Invalid (scores 0):
- import pandas  # Just imports
- # TODO  # Just comments
- model.fit(X, y)  # Single line

Step 5: Score Each Field
task_id: {task_id}
- Valid MP##.P##.S##.T## format? Add 5 points

name: {name}
- Specific with metrics? Add 15 points
- Generic verb? Add 3 points

description: {description}
- Has numbers + methods + thresholds? Add 20 points
- Some technical details? Add 10 points
- Vague? Add 0 points

notes: {notes}
MUST CONTAIN CODE:
- 2+ valid code blocks (5+ lines)? Add 30 points
- 1 valid code block? Add 15 points
- No real code? Add 0 points

source: {source}
- Valid .py file? Add 5 points

stage_link: {stage_link}
- Valid link? Add 5 points

status: {status}
- Valid status? Add 5 points

Step 6: Apply Major Penalties
- No real code blocks: -40
- No specific values (R²=0.35): -40
- No BQX context: -20
- Notes < 500 characters: -60

Step 7: Calculate Final Score
Total = Base (40) + Field Points - Penalties
Minimum: 1
Maximum: 100

Step 8: Generate Output
Score: [Total]
Code Quality: [None/Poor/Fair/Good/Excellent]
Code Blocks: [Count of valid blocks]
Specific Values: [Yes/No]
BQX Windows: [Yes/No]

Remediation (if score < 70):
"INSUFFICIENT CONTENT. Required:
1. Add actual Python/SQL code from scripts/*.py files
2. Include specific calculations with BQX windows [45,90,180,360,720,1440,2880]
3. Provide numerical thresholds (R²=0.35, not 'good R²')
4. Expand notes to >500 characters with real implementation
5. Reference: grep -r 'def calculate' scripts/*.py for code examples"
```

## Key Assessment Points

**What Makes a GOOD Task (Score 70-85):**
```python
def calculate_bqx_momentum(df, window=360):
    """Calculate BQX momentum for specified window."""
    df['idx_mid'] = (df['idx_open'] + df['idx_close']) / 2
    df['bqx_value'] = df['idx_mid'] - df['idx_mid'].shift(-1).rolling(window).mean()
    df['bqx_direction'] = np.where(df['bqx_value'] > 0, 'bearish', 'bullish')
    return df[df['bqx_value'].notna()]
```
- Real executable code
- Specific values (window=360)
- Complete implementation

**What Makes a BAD Task (Score 0-25):**
- No code: "Use pandas to create features"
- Vague values: "Configure parameters"
- Just buzzwords: "Apply machine learning"

## Deployment

1. Copy lines 5-140
2. Navigate to AirTable → Tasks table → record_audit field
3. Click "Configure AI"
4. Replace entire prompt
5. Save and wait 10-30 minutes